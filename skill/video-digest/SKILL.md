---
name: video-digest
description: >-
  Extracts subtitles + metadata from YouTube/Bilibili via yt-dlp for later
  digest writing. This skill only handles the video-specific extraction step;
  the actual deep-dive writing/publishing flow lives in
  skill/insight-write/SKILL.md. Use when the user asks 拉字幕 / 想解读视频 /
  video subtitles fetch.
---

# 视频字幕提取（写作前置工具）

**定位**：本 skill 只做一件事 —— **把视频 URL 变成可读的字幕文本 + 元数据 JSON**。

**之后的深度解读、SVG、HTML 落盘、manifest 收录**全部走 [`skill/insight-write/SKILL.md`](../insight-write/SKILL.md)。视频只是众多源类型里的一种，写作路径与厂商博客 / 论文 / 开源拆解**完全一致**，没必要分岔。

## 前置条件

- 本机已安装 `yt-dlp`（`brew install yt-dlp` 或 `pip install yt-dlp`）

## 一步走完提取

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL"
```

可选保存草稿到 `insights/_drafts/video_<id>/`（把 transcript.txt / meta.json 落盘，避免占对话上下文）：

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL" --save
```

**输出 JSON** 关键字段：`title`、`channel`、`platform`、`duration_label`、`upload_date`、`transcript`、`has_transcript`、`available_sub_langs`、`thumbnail`。

**常见问题**：

- `has_transcript: false` → 该视频无字幕轨；告知用户或考虑放弃。
- URL 不要转义反斜杠：`"https://youtube.com/watch?v=xxx"` ✓，`watch\?v\=` ✗。
- **YouTube 触发 bot check** → 见下一节。

### YouTube 触发 bot 检查怎么办

自 2024 下半年起 YouTube 对无 cookie 请求会返回 `Sign in to confirm you're not a bot`，`fetch` 会直接失败并给出提示。**不要**盲目重试或换代理。

**依次尝试三条路（成本从低到高）**：

1. `--cookies-from-browser` **在 macOS 上通常不可用** —— Chrome 走 Keychain 加密（`could not be decrypted`），Safari 找不到 cookie DB。别浪费时间。
2. **让用户手动导出 cookies.txt**（推荐主路径）——
   1. 在<u>已登录 YouTube 的浏览器</u>装扩展 `Get cookies.txt LOCALLY`（Chrome/Edge）或 `cookies.txt`（Firefox）——必须能导出 **Netscape 格式**，JSON 不吃。
   2. 打开 `youtube.com`，点扩展 → Export → 保存文件（提示用户放到 draft 目录，如 `insights/_drafts/video_<id>/cookies.txt`）。
   3. 重跑 `fetch --cookies <path>`。
3. **抓完立即删** —— cookies.txt 含完整登录态，抓成功后必须马上 `rm`，并<u>绝不 commit</u>（推荐把文件放在 gitignore 覆盖的 `_drafts/` 或 `/tmp/`）。

```bash
# 完整应急流程
python3 skill/video-digest/video_digest.py fetch \
  "https://www.youtube.com/watch?v=<id>" \
  --cookies /Users/xxx/cookies.txt --save
rm /Users/xxx/cookies.txt   # 立即删！
```

**给用户的话术模板**（agent 遇到 bot-check 时应直接抛出）：

> YouTube 拦截了服务器端抓取（bot check）。请你在<u>已登录 YouTube 的浏览器</u>里用 `Get cookies.txt LOCALLY` 扩展导出 `cookies.txt`（Netscape 格式），保存到任意路径后告诉我路径。抓成功后我会立即删除该文件。

**次要备选**（都试过、都不稳，仅记录）：

- `--extractor-args "player_client=web,android,ios,mweb,tv"` 切换客户端指纹：对 bot check 无效，已属过时对策。
- `youtubetranscript.com` / `youtubetotranscript.com` 等第三方 API：同样被 YouTube 限流拦截。
- 借他人机器 / 换 IP：偶尔一次能过，不可复现，不推荐。

## 拿到 transcript 之后

**回到 [`skill/insight-write`](../insight-write/SKILL.md) 的 Step 2 开始走**：

1. Step 2 提图（视频用 `ffmpeg -ss` 截关键帧，命令在 insight-write 里）
2. Step 3 选 accent
3. Step 4 起页面骨架（doc-header + hero-stats + lede + 一页要点）
4. Step 5 ≥3 个 bespoke SVG + 章节
5. Step 6 印章 + 修订记录
6. Step 7 `build_manifest` + `serve.py` 亮/暗验收

**板块判定**（视频照样按核心价值归类，不因为「是视频」就强制归某处）：
- 厂商 PM 访谈讲他们内部做法 → **厂商动态** `frontier/vendors/<v>/deep_dives/`
- 第三方演讲 / 播客解读 → **阅读材料** `readings/`
- 视频只是启发我写自己论点 → **前沿洞察** `insights/<audience>/`

## 工具速查

| 命令 | 作用 |
|------|------|
| `fetch URL` | 拉字幕，JSON 输出 stdout |
| `fetch URL --save` | 额外存草稿（meta.json + transcript.txt + GENERATE.md） |
| `fetch URL --cookies PATH` | YouTube bot check 时携带手动导出的 cookies.txt；抓完立即删 |

工具源码：[`video_digest.py`](./video_digest.py)（内含 `render` 子命令，历史遗留；新流程一律走 `insight-write`，不要再用 `render`）。
