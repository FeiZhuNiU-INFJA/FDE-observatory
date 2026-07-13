#!/usr/bin/env python3
"""
视频字幕拉取 + HTML 落盘辅助工具（供 Cursor Agent 调用）。

工作流（无需 API Key）：
  1. Agent 运行 fetch，获取元数据与字幕全文
  2. Agent 阅读 transcript，撰写解读内容
  3. Agent 运行 render（或直接写 HTML），落盘到合适目录

示例：
  python3 skill/video-digest/video_digest.py fetch "https://www.youtube.com/watch?v=xxx"
  python3 skill/video-digest/video_digest.py fetch "URL" --save
  python3 skill/video-digest/video_digest.py render -o insights/cross/2026-06_foo.html -s draft.json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "_assets" / "_template_video_digest.html"
DRAFTS_DIR = ROOT / "insights" / "_drafts"

# 字幕语言优先级（越靠前越优先）
LANG_PREF = [
    "zh-hans", "zh-hant", "zh-cn", "zh-tw", "zh",
    "en", "en-us", "en-gb",
]

SKIP_SUB_LANGS = {"danmaku", "live_chat", "comments"}


def _die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def find_yt_dlp() -> str:
    path = shutil.which("yt-dlp")
    if path:
        return path
    # 兼容：pip user install 装到 ~/Library/Python/3.x/bin/yt-dlp 但未加 PATH
    for cand in Path.home().glob("Library/Python/3.*/bin/yt-dlp"):
        if cand.exists():
            return str(cand)
    _die("未找到 yt-dlp。请先安装：brew install yt-dlp  或  pip install yt-dlp")
    return ""  # unreachable


def _yt_dlp_supports_flag(yt_dlp: str, flag: str) -> bool:
    try:
        proc = subprocess.run([yt_dlp, "--help"], capture_output=True, text=True, check=False)
    except OSError:
        return False
    return flag in (proc.stdout or "")


def _yt_dlp_js_runtime_args(yt_dlp: str) -> list[str]:
    """YouTube 提取需要 JS runtime；优先 node，其次 deno。仅当 yt-dlp 支持 --js-runtimes 时下发。"""
    if not _yt_dlp_supports_flag(yt_dlp, "--js-runtimes"):
        return []
    for runtime in ("node", "deno"):
        if shutil.which(runtime):
            return ["--js-runtimes", runtime]
    return []


def _norm_lang(lang: str) -> str:
    return lang.lower().replace("_", "-")


def _lang_score(lang: str) -> int:
    n = _norm_lang(lang)
    for i, pref in enumerate(LANG_PREF):
        if n == pref or n.startswith(pref + "-"):
            return i
    return 100 + len(n)


def _pick_subtitle_file(work_dir: Path, video_id: str) -> Optional[tuple[Path, str]]:
    """从工作目录中选出最佳字幕文件。返回 (path, lang)。"""
    candidates: list[tuple[int, Path, str]] = []
    for pattern in (f"{video_id}*.srt", f"{video_id}*.vtt"):
        for p in work_dir.glob(pattern):
            stem = p.name[: -len(p.suffix)]
            parts = stem.split(".", 1)
            lang = parts[1] if len(parts) > 1 else "unknown"
            if _norm_lang(lang) in SKIP_SUB_LANGS:
                continue
            # 跳过 xx-zh-Hans 这类翻译轨，优先原生语言轨
            if re.match(r"^[a-z]{2,3}-zh-", lang, re.I):
                continue
            candidates.append((_lang_score(lang), p, lang))
    if not candidates:
        # 回退：接受翻译轨（如仅有 en-zh-Hans）
        for pattern in (f"{video_id}*.srt", f"{video_id}*.vtt"):
            for p in work_dir.glob(pattern):
                stem = p.name[: -len(p.suffix)]
                parts = stem.split(".", 1)
                lang = parts[1] if len(parts) > 1 else "unknown"
                if _norm_lang(lang) in SKIP_SUB_LANGS:
                    continue
                candidates.append((_lang_score(lang), p, lang))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], len(x[2])))
    _, path, lang = candidates[0]
    return path, lang


def parse_subtitle_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    ext = path.suffix.lower()
    if ext == ".srt":
        return _srt_to_text(raw)
    if ext == ".vtt":
        return _vtt_to_text(raw)
    return raw.strip()


def _srt_to_text(raw: str) -> str:
    lines: list[str] = []
    prev = ""
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.isdigit():
            continue
        if re.match(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->", s):
            continue
        if s == prev:
            continue
        lines.append(s)
        prev = s
    return "\n".join(lines)


def _vtt_to_text(raw: str) -> str:
    lines: list[str] = []
    prev = ""
    skip_prefixes = ("WEBVTT", "NOTE", "Kind:", "Language:")
    for line in raw.splitlines():
        s = line.strip()
        if not s or any(s.startswith(p) for p in skip_prefixes):
            continue
        if re.match(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->", s):
            continue
        if s.isdigit():
            continue
        # 去掉 VTT 内联标签 <c> 等
        s = re.sub(r"<[^>]+>", "", s)
        if not s or s == prev:
            continue
        lines.append(s)
        prev = s
    return "\n".join(lines)


def _detect_platform(info: dict[str, Any]) -> str:
    extractor = (info.get("extractor") or info.get("extractor_key") or "").lower()
    webpage = (info.get("webpage_url") or info.get("original_url") or "").lower()
    if "bilibili" in extractor or "bilibili" in webpage:
        return "bilibili"
    if "youtube" in extractor or "youtu" in webpage:
        return "youtube"
    return extractor or "unknown"


def _format_duration(seconds: Optional[float]) -> str:
    if not seconds:
        return ""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def _format_upload_date(raw: Optional[str]) -> str:
    if not raw or len(raw) != 8:
        return ""
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


def fetch_video(
    url: str,
    *,
    save_draft: bool = False,
    cookies: Optional[str] = None,
    audio_only: bool = False,
) -> dict[str, Any]:
    yt_dlp = find_yt_dlp()
    work_dir = Path(tempfile.mkdtemp(prefix="video_digest_"))

    sub_langs = "zh-Hans,zh-Hant,zh,en,en-orig"
    out_tpl = str(work_dir / "%(id)s.%(ext)s") if audio_only else str(work_dir / "%(id)s")

    if audio_only:
        # Plan B 第 1 步：只拉音频，不写字幕
        cmd = [
            yt_dlp,
            *_yt_dlp_js_runtime_args(yt_dlp),
            "-f", "bestaudio[ext=m4a]/bestaudio/best",
            "--extract-audio", "--audio-format", "m4a",
            "--write-info-json",
            "--no-write-playlist-metafiles",
            "-o", out_tpl,
        ]
    else:
        # Plan A：拉字幕 + 元数据（不下音视频）
        cmd = [
            yt_dlp,
            *_yt_dlp_js_runtime_args(yt_dlp),
            "-t", "sleep",
            "--sleep-interval", "3",
            "--max-sleep-interval", "8",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--write-info-json",
            "--no-write-playlist-metafiles",
            "--sub-langs", sub_langs,
            "-o", out_tpl,
        ]
    # B 站风控/YouTube 保底 headers
    cmd.extend([
        "--user-agent",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
        "--add-header", "Accept-Language:zh-CN,zh;q=0.9",
    ])
    if "bilibili" in url.lower():
        cmd.extend(["--referer", "https://www.bilibili.com/"])
    if cookies:
        cookies_path = Path(cookies).expanduser().resolve()
        if not cookies_path.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
            _die(f"cookies 文件不存在: {cookies_path}")
        cmd.extend(["--cookies", str(cookies_path)])
    cmd.append(url)

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        _die(f"运行 yt-dlp 失败: {exc}")

    if proc.returncode != 0:
        shutil.rmtree(work_dir, ignore_errors=True)
        err = (proc.stderr or proc.stdout or "").strip()
        hint = ""
        if "Sign in to confirm you're not a bot" in err or "confirm you" in err.lower():
            hint = (
                "\n\n提示：YouTube 触发了 bot 检查。请让用户按下面步骤导出 cookies 后重试：\n"
                "  1) 在已登录 YouTube 的浏览器安装 cookies.txt 导出扩展（如 'Get cookies.txt LOCALLY'）\n"
                "  2) 打开 youtube.com 导出 Netscape 格式 cookies.txt\n"
                "  3) 重跑：video_digest.py fetch <URL> --cookies /path/to/cookies.txt\n"
                "  4) 抓取成功后立即删除 cookies 文件（含登录态，勿提交到 git）"
            )
        elif "412" in err and "bilibili" in url.lower():
            hint = (
                "\n\n提示：B 站 /x/player/wbi/v2 被风控拦（412）。请参考 skill/video-digest/SKILL.md 的「B 站 412 应急」节，\n"
                "  用 curl 直接调 /x/player/playurl 拿 DASH 音频 URL 下载 m4s，再 ffmpeg 转 m4a。\n"
                "  拿到 m4a 后：Plan A 走飞书妙记 ASR（drive +upload → minutes +upload → minutes +detail --transcript）；\n"
                "  Plan A 不可行才走 Plan B：python3 skill/video-digest/video_digest.py transcribe <path.m4a> --language zh"
            )
        _die(f"yt-dlp 失败 (exit {proc.returncode}):\n{err[-2000:]}{hint}")

    info_files = list(work_dir.glob("*.info.json"))
    if not info_files:
        shutil.rmtree(work_dir, ignore_errors=True)
        _die("yt-dlp 未生成 info.json")

    try:
        info = json.loads(info_files[0].read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        _die(f"解析 info.json 失败: {exc}")

    video_id = info.get("id") or "unknown"
    picked = None if audio_only else _pick_subtitle_file(work_dir, video_id)

    transcript = ""
    sub_lang = None
    sub_file = None
    if picked:
        sub_path, sub_lang = picked
        transcript = parse_subtitle_text(sub_path)
        sub_file = sub_path.name

    available_subs: list[str] = []
    for key in ("subtitles", "automatic_captions"):
        block = info.get(key) or {}
        if isinstance(block, dict):
            available_subs.extend(block.keys())
    available_subs = sorted({s for s in available_subs if _norm_lang(s) not in SKIP_SUB_LANGS})

    platform = _detect_platform(info)
    duration = info.get("duration")
    upload_date = _format_upload_date(info.get("upload_date"))

    result: dict[str, Any] = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "url": info.get("webpage_url") or url,
        "video_id": video_id,
        "platform": platform,
        "title": info.get("title") or "",
        "channel": info.get("channel") or info.get("uploader") or "",
        "duration_seconds": duration,
        "duration_label": _format_duration(duration),
        "upload_date": upload_date,
        "description": (info.get("description") or "")[:4000],
        "thumbnail": info.get("thumbnail") or "",
        "available_sub_langs": available_subs,
        "subtitle_lang": sub_lang,
        "subtitle_file": sub_file,
        "transcript": transcript,
        "transcript_chars": len(transcript),
        "has_transcript": bool(transcript.strip()),
        "transcript_source": ("subtitle:" + sub_lang) if picked else None,
    }

    audio_path: Optional[Path] = None
    if audio_only:
        cand = list(work_dir.glob(f"{video_id}.m4a")) or list(work_dir.glob(f"{video_id}.*"))
        # 过滤掉 info.json
        cand = [p for p in cand if p.suffix.lower() not in {".json"}]
        if cand:
            audio_path = cand[0]

    if save_draft:
        draft_dir = DRAFTS_DIR / f"video_{video_id}"
        draft_dir.mkdir(parents=True, exist_ok=True)
        if audio_path:
            dest = draft_dir / audio_path.name
            shutil.move(str(audio_path), str(dest))
            result["audio_file"] = str(dest.relative_to(ROOT))
        (draft_dir / "meta.json").write_text(
            json.dumps({k: v for k, v in result.items() if k != "transcript"},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (draft_dir / "transcript.txt").write_text(transcript, encoding="utf-8")
        (draft_dir / "GENERATE.md").write_text(_generate_prompt(result), encoding="utf-8")
        result["draft_dir"] = str(draft_dir.relative_to(ROOT))
    elif audio_path:
        # 不 save_draft 时也把音频挪到临时可发现位置，避免连同 work_dir 一起被删
        keep = DRAFTS_DIR / f"video_{video_id}"
        keep.mkdir(parents=True, exist_ok=True)
        dest = keep / audio_path.name
        shutil.move(str(audio_path), str(dest))
        result["audio_file"] = str(dest.relative_to(ROOT))

    shutil.rmtree(work_dir, ignore_errors=True)
    return result


def _generate_prompt(meta: dict[str, Any]) -> str:
    return f"""# 视频解读生成指引

## 源视频
- 标题：{meta.get('title', '')}
- 频道：{meta.get('channel', '')}
- 平台：{meta.get('platform', '')}
- 时长：{meta.get('duration_label', '')}
- 链接：{meta.get('url', '')}

## Agent 任务
1. 阅读同目录 `transcript.txt`
2. 撰写深度解读（非简单摘要），对齐站点已有风格（参考 `frontier/vendors/anthropic/deep_dives/`）
3. 根据内容选择落盘目录：
   - 外部厂商/访谈信号 → `frontier/vendors/<vendor>/deep_dives/`
   - 自己的前沿洞察 → `insights/<tob|toc|cross>/`
4. 生成 HTML（可用 `python3 skill/video-digest/video_digest.py render --spec ...`）
5. 确保 `doc-meta` 含：日期、受众、标签、状态

## 输出文件名
`YYYY-MM-DD_<slug>.html` 或 `YYYY-MM_<slug>.html`
"""


def assets_relpath(output: Path) -> str:
    """从输出 HTML 路径计算到 _assets/ 的相对路径。"""
    depth = len(output.parent.relative_to(ROOT).parts)
    return "/".join([".."] * depth) + "/_assets"


def index_relpath(output: Path) -> str:
    depth = len(output.parent.relative_to(ROOT).parts)
    return "/".join([".."] * depth) + "/index.html"


def category_index_relpath(output: Path) -> tuple[str, str]:
    """返回 (href, label) 用于 doc-footer。"""
    rel = output.relative_to(ROOT)
    parts = rel.parts
    if parts[0] == "frontier":
        depth = len(parts) - 1
        prefix = "/".join([".."] * depth)
        return f"{prefix}/frontier/index.html", "← Frontier 索引"
    if parts[0] == "insights":
        depth = len(parts) - 1
        prefix = "/".join([".."] * depth)
        return f"{prefix}/insights/index.html", "← 洞察总索引"
    return index_relpath(output), "← 首页"


def render_html(spec: dict[str, Any], output: Path) -> None:
    if not TEMPLATE.exists():
        _die(f"模板不存在: {TEMPLATE}")

    output = output if output.is_absolute() else ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)

    assets = assets_relpath(output)
    index_href = index_relpath(output)
    cat_href, cat_label = category_index_relpath(output)

    tags = spec.get("tags") or []
    meta_spans = [
        spec.get("date", datetime.now().strftime("%Y-%m-%d")),
        spec.get("audience", "跨市场"),
        *tags,
        spec.get("status", "草案"),
    ]
    meta_html = "\n        ".join(f"<span>{t}</span>" for t in meta_spans if t)

    video_url = spec.get("video_url", "")
    video_label = spec.get("video_label") or video_url
    video_link_html = ""
    if video_url:
        video_link_html = (
            f'<p style="color: var(--text-soft); font-size: .95rem;">\n'
            f'        视频：<a href="{video_url}" target="_blank" rel="noopener">{video_label}</a>\n'
            f"      </p>"
        )

    accent_style = ""
    accent = spec.get("accent")
    if accent:
        accent_style = f"""<style>
  :root {{ --accent: {accent}; --accent-soft: color-mix(in srgb, {accent} 12%, white); }}
  [data-theme="dark"] {{ --accent-soft: color-mix(in srgb, {accent} 20%, #1a1a22); }}
</style>"""

    footer_extra = spec.get("footer_extra", "")
    footer_html = f'<a href="{cat_href}">{cat_label}</a>'
    if footer_extra:
        footer_html += f"\n      ·\n      {footer_extra}"

    tpl = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{ASSETS_REL}}": assets,
        "{{INDEX_REL}}": index_href,
        "{{TITLE}}": spec.get("title", "视频解读"),
        "{{SUBTITLE}}": spec.get("subtitle", ""),
        "{{BRAND_SUB}}": spec.get("brand_sub", spec.get("audience", "跨市场")),
        "{{META_SPANS}}": meta_html,
        "{{VIDEO_LINK}}": video_link_html,
        "{{LEDE}}": spec.get("lede", ""),
        "{{BODY}}": spec.get("body", ""),
        "{{FOOTER}}": footer_html,
        "{{ACCENT_STYLE}}": accent_style,
        "{{REVISION}}": spec.get(
            "revision",
            f"{spec.get('date', datetime.now().strftime('%Y-%m-%d'))} 初稿",
        ),
    }
    html = tpl
    for k, v in replacements.items():
        html = html.replace(k, v)

    output.write_text(html, encoding="utf-8")
    print(f"✓ HTML written to {output.relative_to(ROOT)}")


def cmd_fetch(args: argparse.Namespace) -> int:
    result = fetch_video(
        args.url,
        save_draft=args.save,
        cookies=args.cookies,
        audio_only=args.audio_only,
    )
    if args.json or not args.save:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✓ Draft saved to {result.get('draft_dir')}")
        print(f"  transcript: {result['transcript_chars']} chars")
        if result.get("audio_file"):
            print(f"  audio: {result['audio_file']}")
    if not args.audio_only and not result["has_transcript"]:
        print("warning: 未获取到字幕。建议路径：Plan A → 音频送妙记 ASR；不可行时再走 --audio-only + transcribe（Plan B）", file=sys.stderr)
    return 0


def _find_whisper_backend() -> tuple[str, Any]:
    """按优先级挑选可用后端：mlx-whisper > faster-whisper > openai-whisper。返回 (backend_name, module)。"""
    try:
        import mlx_whisper  # type: ignore
        return "mlx-whisper", mlx_whisper
    except Exception:
        pass
    try:
        from faster_whisper import WhisperModel  # type: ignore
        return "faster-whisper", WhisperModel
    except Exception:
        pass
    try:
        import whisper  # type: ignore
        return "openai-whisper", whisper
    except Exception:
        pass
    return "", None


def _transcribe_with_backend(
    backend: str, mod: Any, audio_path: Path, *, model: str, language: Optional[str]
) -> str:
    if backend == "mlx-whisper":
        result = mod.transcribe(
            str(audio_path),
            path_or_hf_repo=f"mlx-community/whisper-{model}-mlx",
            language=language,
        )
        return (result.get("text") or "").strip()
    if backend == "faster-whisper":
        WhisperModel = mod  # 类
        m = WhisperModel(model, device="auto", compute_type="int8")
        segments, _ = m.transcribe(str(audio_path), language=language, vad_filter=True)
        return "\n".join(seg.text.strip() for seg in segments if seg.text.strip())
    if backend == "openai-whisper":
        m = mod.load_model(model)
        result = m.transcribe(str(audio_path), language=language, fp16=False)
        return (result.get("text") or "").strip()
    _die(f"未知 whisper 后端: {backend}")
    return ""


def cmd_transcribe(args: argparse.Namespace) -> int:
    audio_path = Path(args.audio_path)
    if not audio_path.is_absolute():
        audio_path = ROOT / audio_path
    if not audio_path.exists():
        _die(f"音频文件不存在: {audio_path}")

    backend, mod = _find_whisper_backend()
    if not backend:
        _die(
            "本机没有 whisper 后端。任选其一安装：\n"
            "  - Apple Silicon 首选：pip install mlx-whisper\n"
            "  - 通用较快：       pip install faster-whisper\n"
            "  - 官方：           pip install -U openai-whisper"
        )

    print(f"[transcribe] backend={backend} model={args.model} language={args.language or 'auto'}", file=sys.stderr)
    print(f"[transcribe] audio={audio_path}", file=sys.stderr)
    text = _transcribe_with_backend(backend, mod, audio_path, model=args.model, language=args.language)
    if not text:
        _die("whisper 返回空文本，可能是音频无声或后端异常")

    # 若 audio 位于 insights/_drafts/video_<id>/ 里，同步更新 transcript.txt + meta.json
    draft_dir = audio_path.parent
    is_draft = draft_dir.parent.name == "_drafts" and draft_dir.name.startswith("video_")
    if is_draft:
        transcript_path = draft_dir / "transcript.txt"
        transcript_path.write_text(text, encoding="utf-8")
        meta_path = draft_dir / "meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
            meta["has_transcript"] = True
            meta["transcript_chars"] = len(text)
            meta["transcript_source"] = f"whisper:{backend}:{args.model}"
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        print(f"✓ transcript → {transcript_path.relative_to(ROOT)} ({len(text)} chars)")
        print(f"  meta updated: transcript_source=whisper:{backend}:{args.model}")
    else:
        # 独立音频文件：结果打印到 stdout
        print(text)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = ROOT / spec_path
    if not spec_path.exists():
        _die(f"spec 文件不存在: {spec_path}")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if args.body_file:
        body_path = Path(args.body_file)
        if not body_path.is_absolute():
            body_path = ROOT / body_path
        spec["body"] = body_path.read_text(encoding="utf-8")
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    render_html(spec, output)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="视频字幕拉取 + HTML 落盘（供 Agent 调用）")
    sub = ap.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="拉取视频元数据与字幕（Plan A）")
    p_fetch.add_argument("url", help="视频 URL（YouTube / Bilibili 等）")
    p_fetch.add_argument("--save", action="store_true", help="同时保存草稿到 insights/_drafts/")
    p_fetch.add_argument("--json", action="store_true", help="输出 JSON（默认 fetch 时输出）")
    p_fetch.add_argument(
        "--cookies",
        metavar="PATH",
        help="Netscape 格式 cookies.txt 路径（YouTube 触发 bot 检查时使用；抓完请立即删除）",
    )
    p_fetch.add_argument(
        "--audio-only",
        action="store_true",
        help="Plan B 第 1 步：跳过字幕、只下最低码率 m4a 到 insights/_drafts/video_<id>/",
    )
    p_fetch.set_defaults(func=cmd_fetch)

    p_tx = sub.add_parser(
        "transcribe",
        help="Plan B 第 2 步：本地 whisper 转写音频（仅在 Plan A 不可行时使用）",
    )
    p_tx.add_argument("audio_path", help="音频文件路径（相对站点根或绝对）")
    p_tx.add_argument(
        "--model", default="medium",
        help="whisper 模型：tiny/base/small/medium/large-v3（默认 medium）",
    )
    p_tx.add_argument(
        "--language", default=None,
        help="强制指定语言（zh/en/ja/...），默认自动检测；中文口播建议显式传 zh",
    )
    p_tx.set_defaults(func=cmd_transcribe)

    p_render = sub.add_parser("render", help="根据 spec JSON 渲染 HTML")
    p_render.add_argument("--output", "-o", required=True, help="输出 HTML 路径（相对站点根）")
    p_render.add_argument("--spec", "-s", required=True, help="spec JSON 路径")
    p_render.add_argument("--body-file", help="文章正文 HTML（覆盖 spec.body）")
    p_render.set_defaults(func=cmd_render)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
