#!/usr/bin/env python3
"""
扫描 FDE 洞察站目录，提取每个文档的元数据，生成 manifest.json。

被 serve.py 在 /_manifest.json 端点调用。也可独立运行：
    python3 _assets/build_manifest.py            # 写到 _assets/manifest.json
    python3 _assets/build_manifest.py --stdout   # 打印到 stdout

元数据来源（优先级）：
  1. HTML 的 .doc-meta 区块解析
  2. 文件名前缀（YYYY-MM-DD_*.md / YYYY-MM_*.html）
  3. 文件 mtime（最后兜底）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {"_drafts", "_source", "_media", "node_modules", ".git"}
SKIP_FILES = {"index.html", "README.md", "README.zh-CN.md"}

STAMPS_PATH = ROOT / "_assets" / "stamps.json"


def load_stamps() -> dict:
    """读取印章数据源（时机 / 信心），以文档 path 为键。缺失或损坏时返回空表。"""
    if not STAMPS_PATH.exists():
        return {}
    try:
        data = json.loads(STAMPS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data.get("stamps", {}) if isinstance(data, dict) else {}


# ──────────────────────────────────────────────────────────────────────────
# HTML 解析
# ──────────────────────────────────────────────────────────────────────────


class DocMetaParser(HTMLParser):
    """提取 HTML 文件中的 <title>、第一篇文章的 <h1>、.doc-meta 块的 <span> 文本。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str = ""
        self.h1: str = ""
        self.meta_spans: list[str] = []
        # state
        self._in_title = False
        self._in_h1 = False
        self._h1_done = False
        self._meta_depth = 0  # 是否在 .doc-meta 内
        self._in_meta_span = False
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "") or ""

        if tag == "title":
            self._in_title = True
            self._current_text = []
        elif tag == "h1" and not self._h1_done:
            self._in_h1 = True
            self._current_text = []
        elif tag == "div" and "doc-meta" in cls.split():
            self._meta_depth = 1
        elif self._meta_depth > 0:
            if tag == "div":
                self._meta_depth += 1
            elif tag == "span":
                self._in_meta_span = True
                self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = "".join(self._current_text).strip()
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            self._h1_done = True
            self.h1 = "".join(self._current_text).strip()
        elif self._meta_depth > 0 and tag == "div":
            self._meta_depth -= 1
        elif self._in_meta_span and tag == "span":
            self._in_meta_span = False
            text = "".join(self._current_text).strip()
            if text:
                self.meta_spans.append(text)

    def handle_data(self, data: str) -> None:
        if self._in_title or self._in_h1 or self._in_meta_span:
            self._current_text.append(data)


# ──────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────


@dataclass
class DocEntry:
    path: str  # 相对站点根的路径
    title: str
    date: str  # YYYY-MM-DD 或 YYYY-MM 或 YYYY-Q?
    audience: Optional[str] = None  # tob / toc / cross
    status: Optional[str] = None  # 草案 / 对内 / 可对外
    tags: list[str] = field(default_factory=list)
    category: str = ""  # insight / frontier-deep / frontier-digest / readings / oss / legacy
    extra: dict = field(default_factory=dict)  # 比如 vendor 名


# ──────────────────────────────────────────────────────────────────────────
# 工具：日期 / 受众 / 状态识别
# ──────────────────────────────────────────────────────────────────────────


_AUDIENCE_MAP = {
    "tob": "tob", "ToB": "tob", "TOB": "tob", "B端": "tob", "企业": "tob",
    "toc": "toc", "ToC": "toc", "TOC": "toc", "C端": "toc", "消费者": "toc",
    "cross": "cross", "跨市场": "cross", "跨": "cross",
}

_STATUS_KEYWORDS = {"草案", "对内", "可对外", "已产出", "记录中", "已验证", "已归档", "待验证"}

_NOISE_PATTERNS = [
    re.compile(r"^[~约≈]?[\d,]+\s*字$"),  # ~6,000 字 / 4500 字
    re.compile(r"^\d+\s*words?$", re.IGNORECASE),
]

_DATE_PATTERNS = [
    re.compile(r"(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(\d{4}-Q[1-4])", re.IGNORECASE),
    re.compile(r"(\d{4}-\d{2})"),
    re.compile(r"(\d{4}年\d{1,2}月)"),
]


def _classify_audience(spans: list[str]) -> Optional[str]:
    for s in spans:
        for key, val in _AUDIENCE_MAP.items():
            if key in s:
                return val
    return None


def _classify_status(spans: list[str]) -> Optional[str]:
    for s in spans:
        for kw in _STATUS_KEYWORDS:
            if kw in s:
                return kw
    return None


def _extract_date(spans: list[str], filename: str, mtime: float) -> str:
    # 优先 doc-meta 第一个 span 里像日期的部分
    for s in spans[:2]:
        for pat in _DATE_PATTERNS:
            m = pat.search(s)
            if m:
                return m.group(1)
    # 再尝试文件名
    for pat in _DATE_PATTERNS:
        m = pat.search(filename)
        if m:
            return m.group(1)
    # 最后用 mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m")


# 两枚判断印章：doc-meta 里写 <span>时机：进行中</span><span>信心：高</span>
_STAMP_KEYS = {"时机": "timing", "信心": "confidence"}
_STAMP_SPAN_RE = re.compile(r"^\s*(时机|信心)\s*[:：]\s*(.+?)\s*$")


def _classify_stamps(spans: list[str]) -> dict:
    """从 doc-meta 里识别「时机：X」「信心：Y」两枚判断印章，返回 {timing, confidence}。"""
    out: dict = {}
    for s in spans:
        m = _STAMP_SPAN_RE.match(s)
        if m:
            val = m.group(2).strip()
            if val:
                out[_STAMP_KEYS[m.group(1)]] = val
    return out


def _classify_tags(spans: list[str], audience: Optional[str], status: Optional[str], date: str) -> list[str]:
    """剩余 span（去掉日期/受众/状态/印章后）作为主题标签。"""
    result = []
    skip_set = {audience, status, date} if audience else {status, date}
    for s in spans:
        s_clean = s.strip()
        if not s_clean or s_clean in skip_set:
            continue
        # 跳过含日期的
        if any(p.search(s_clean) for p in _DATE_PATTERNS):
            continue
        # 跳过印章 span（时机：… / 信心：…）
        if _STAMP_SPAN_RE.match(s_clean):
            continue
        # 跳过受众词
        if any(key in s_clean for key in _AUDIENCE_MAP):
            continue
        # 跳过状态词
        if any(kw in s_clean for kw in _STATUS_KEYWORDS):
            continue
        # 长度过滤
        if len(s_clean) > 25:
            continue
        # 字数 / wordcount 噪声
        if any(p.match(s_clean) for p in _NOISE_PATTERNS):
            continue
        result.append(s_clean)
    return result


def _date_sort_key(date_str: str) -> str:
    """把混杂格式的日期转成可比较字符串。
       YYYY-QN → 用季度首月  (Q1→01, Q2→04, Q3→07, Q4→10)
       YYYY-MM → 补 -00
       其余原样
    """
    if not date_str:
        return ""
    m = re.match(r"^(\d{4})-Q([1-4])$", date_str, re.IGNORECASE)
    if m:
        q_month = {"1": "01", "2": "04", "3": "07", "4": "10"}[m.group(2)]
        return f"{m.group(1)}-{q_month}-00"
    m = re.match(r"^(\d{4})-(\d{2})$", date_str)
    if m:
        return f"{date_str}-00"
    return date_str


# ──────────────────────────────────────────────────────────────────────────
# 文件 → DocEntry
# ──────────────────────────────────────────────────────────────────────────


def parse_html_doc(path: Path, rel_path: str, category: str, extra: dict | None = None) -> DocEntry:
    text = path.read_text(encoding="utf-8", errors="ignore")
    parser = DocMetaParser()
    try:
        parser.feed(text)
    except Exception:
        pass
    spans = parser.meta_spans
    title = parser.h1 or parser.title or path.stem
    # 清理 title 中的 <span class="brand-sub"> 之类的尾巴
    title = re.sub(r"\s+", " ", title).strip()

    audience = _classify_audience(spans)
    status = _classify_status(spans)
    date = _extract_date(spans, path.name, path.stat().st_mtime)
    tags = _classify_tags(spans, audience, status, date)
    stamps = _classify_stamps(spans)

    merged_extra = dict(extra or {})
    merged_extra.update(stamps)

    return DocEntry(
        path=rel_path,
        title=title,
        date=date,
        audience=audience,
        status=status,
        tags=tags,
        category=category,
        extra=merged_extra,
    )


_MD_TITLE_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def parse_md_doc(path: Path, rel_path: str, category: str, extra: dict | None = None) -> DocEntry:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = _MD_TITLE_RE.search(text[:4096])
    title = (m.group(1) if m else path.stem).strip()
    date = _extract_date([], path.name, path.stat().st_mtime)
    return DocEntry(
        path=rel_path,
        title=title,
        date=date,
        category=category,
        extra=extra or {},
    )


# ──────────────────────────────────────────────────────────────────────────
# 目录扫描
# ──────────────────────────────────────────────────────────────────────────


def _iter_files(base: Path, exts: tuple[str, ...]) -> list[Path]:
    if not base.exists():
        return []
    out = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            continue
        if p.name in SKIP_FILES:
            # 特例：子目录 index.html 若是该目录下唯一的 HTML，则收录
            if p.name == "index.html" and p.parent != base:
                siblings = [s for s in p.parent.iterdir()
                            if s.is_file() and s.suffix.lower() in exts and s.name not in SKIP_FILES]
                if siblings:
                    continue  # 有其他 HTML 文件，跳过 index.html
                # 无其他 HTML → 收录此 index.html
            else:
                continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace(os.sep, "/")


def scan() -> dict:
    insights: list[DocEntry] = []
    for sub, audience in [("tob", "tob"), ("toc", "toc"), ("cross", "cross")]:
        for p in _iter_files(ROOT / "insights" / sub, (".html",)):
            entry = parse_html_doc(p, _rel(p), "insight")
            # 子目录推断的受众覆盖 doc-meta 的（避免分类错位）
            entry.audience = entry.audience or audience
            if not entry.audience:
                entry.audience = audience
            insights.append(entry)

    frontier_deep: list[DocEntry] = []
    frontier_digest: list[DocEntry] = []
    vendors_dir = ROOT / "frontier" / "vendors"
    if vendors_dir.exists():
        for vendor_dir in vendors_dir.iterdir():
            if not vendor_dir.is_dir():
                continue
            vendor = vendor_dir.name
            # 同 stem 优先 .html（阅读版）；.md 保留为工作稿索引
            deep_dir = vendor_dir / "deep_dives"
            by_stem: dict[str, Path] = {}
            for p in _iter_files(deep_dir, (".md", ".html")):
                stem = p.stem
                if stem not in by_stem or p.suffix.lower() == ".html":
                    by_stem[stem] = p
            for p in by_stem.values():
                rel = _rel(p)
                extra = {"vendor": vendor}
                if p.suffix.lower() == ".html":
                    frontier_deep.append(
                        parse_html_doc(p, rel, "frontier-deep", extra)
                    )
                else:
                    frontier_deep.append(parse_md_doc(p, rel, "frontier-deep", extra))
            digest_dir = vendor_dir / "digests"
            by_stem = {}
            for p in _iter_files(digest_dir, (".md", ".html")):
                stem = p.stem
                if stem not in by_stem or p.suffix.lower() == ".html":
                    by_stem[stem] = p
            for p in by_stem.values():
                rel = _rel(p)
                extra = {"vendor": vendor}
                if p.suffix.lower() == ".html":
                    frontier_digest.append(parse_html_doc(p, rel, "frontier-digest", extra))
                else:
                    frontier_digest.append(parse_md_doc(p, rel, "frontier-digest", extra))

    oss: list[DocEntry] = []
    oss_dir = ROOT / "opensource-analysis"
    if oss_dir.exists():
        for p in _iter_files(oss_dir, (".html",)):
            oss.append(parse_html_doc(p, _rel(p), "oss"))

    readings: list[DocEntry] = []
    for p in _iter_files(ROOT / "readings", (".html",)):
        readings.append(parse_html_doc(p, _rel(p), "readings"))

    legacy: list[DocEntry] = []
    legacy_dir = ROOT / "legacy"
    if legacy_dir.exists():
        for p in _iter_files(legacy_dir, (".html", ".md")):
            ext = p.suffix.lower()
            parser_fn = parse_html_doc if ext == ".html" else parse_md_doc
            entry = parser_fn(p, _rel(p), "legacy")
            if ext == ".md":
                entry.tags.append("MD 草稿")
            legacy.append(entry)

    for lst in [insights, frontier_deep, frontier_digest, oss, legacy, readings]:
        lst.sort(key=lambda e: _date_sort_key(e.date), reverse=True)

    # 印章兜底：文章 .doc-meta 里写的「时机/信心」优先；stamps.json 只补文章没写的。
    stamps = load_stamps()
    if stamps:
        for lst in [insights, frontier_deep, frontier_digest, oss, legacy, readings]:
            for e in lst:
                s = stamps.get(e.path)
                if not s:
                    continue
                if s.get("timing") and not e.extra.get("timing"):
                    e.extra["timing"] = s["timing"]
                if s.get("confidence") and not e.extra.get("confidence"):
                    e.extra["confidence"] = s["confidence"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "insights": [asdict(e) for e in insights],
        "frontier_deep": [asdict(e) for e in frontier_deep],
        "frontier_digest": [asdict(e) for e in frontier_digest],
        "oss": [asdict(e) for e in oss],
        "legacy": [asdict(e) for e in legacy],
        "readings": [asdict(e) for e in readings],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build site manifest.json")
    ap.add_argument("--stdout", action="store_true", help="打印到 stdout 而非写文件")
    ap.add_argument("-o", "--output", default=str(ROOT / "_assets" / "manifest.json"),
                    help="输出路径（默认 _assets/manifest.json）")
    args = ap.parse_args()

    data = scan()
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if args.stdout:
        sys.stdout.write(payload)
    else:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        total = sum(len(data[k]) for k in data if isinstance(data[k], list))
        print(f"✓ Manifest written to {out.relative_to(ROOT)} ({total} docs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
