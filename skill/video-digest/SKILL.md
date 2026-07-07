---
name: video-digest
description: >-
  Fetches subtitles from YouTube/Bilibili via skill/video-digest/video_digest.py, writes a
  deep-dive interpretation, and publishes HTML to the FDE insight site (no API
  key). Use when the user asks to summarize, interpret, or digest a video, or
  mentions video subtitles and site publishing. 触发词：总结视频、解读视频、看视频写洞察。
---

# 视频解读 → 站点发布

本仓库专用工作流：**工具拉字幕，Agent 写解读，落盘 HTML，首页自动收录**。

## 前置条件

- 本机已安装 `yt-dlp`（`brew install yt-dlp` 或 `pip install yt-dlp`）

## 工作流

```
Task Progress:
- [ ] 1. fetch 拉字幕与元数据
- [ ] 2. 阅读 transcript，撰写深度解读
- [ ] 3. 判断落盘目录
- [ ] 4. render 生成 HTML
- [ ] 5. 验证 manifest 收录
```

### Step 1 — 拉取字幕（必须执行）

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL"
```

可选保存草稿到 `insights/_drafts/video_<id>/`：

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL" --save
```

输出 JSON 含 `title`、`channel`、`transcript`、`platform`、`has_transcript` 等。

- `has_transcript: false` → 告知用户可能无字幕或需 cookie（B 站高清/登录场景）
- URL 不要转义反斜杠：`"https://youtube.com/watch?v=xxx"` ✓，`watch\?v\=` ✗

#### YouTube 触发 bot 检查怎么办

自 2024 下半年起 YouTube 对无 cookie 请求会返回 `Sign in to confirm you're not a bot`，此时 `fetch` 会直接失败并给出提示。**不要**盲目重试或换代理，按下面流程走：

**依次尝试三条路（成本从低到高）**：

1. `--cookies-from-browser` **在 macOS 上通常不可用** —— Chrome 走 Keychain 加密（`could not be decrypted`），Safari 找不到 cookie DB。别浪费时间。
2. **让用户手动导出 cookies.txt**（推荐主路径）——
   1. 在<u>已登录 YouTube 的浏览器</u>装扩展 `Get cookies.txt LOCALLY`（Chrome/Edge）或 `cookies.txt`（Firefox）——必须能导出 **Netscape 格式**，JSON 不吃。
   2. 打开 `youtube.com`，点扩展 → Export → 保存文件（提示用户放到 draft 目录，如 `insights/_drafts/video_<id>/cookies.txt`）。
   3. 重跑 `fetch --cookies <path>`。
3. **抓完立即删** —— cookies.txt 含完整登录态，agent 抓成功后必须马上 `rm`，并<u>绝不 commit</u>（推荐把文件放在 gitignore 覆盖的 `_drafts/` 或 `/tmp/`）。

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

### Step 2 — 撰写解读

阅读 `transcript`，写**深度解读**（非流水账摘要）。

风格参考（择近者）：

| 类型 | 范例 |
|------|------|
| 厂商/访谈信号 | `frontier/vendors/anthropic/deep_dives/2026-05-28_alex-albert-research-pm-interview.html` |
| 跨市场概念 | `insights/cross/2026-06_loop-engineering-coding-agent.html` |
| Claude Code 专题 | `frontier/vendors/anthropic/deep_dives/2026-05-28_claude-code-dynamic-workflows.html` |

必备结构：核心结论（lede）、一页要点、分节论证、FDE/ToB 映射（如适用），待验证问题。

**外部图片（新，可选但推荐）**：阅读时如源材料含**关键图表 / 幻灯片 / 产品 UI 截图**，优先纳入正文——bespoke SVG 是主力表达，图片承担「保真」职责。

- 视频截帧：先 `yt-dlp --list-formats` 拿到源，再 `ffmpeg -ss <hh:mm:ss> -i <file> -frames:v 1 -q:v 2 out.webp`；或用 `yt-dlp --write-thumbnail` 拿封面。
- 论文 / 幻灯片图：用 `pdftoppm -png -r 180 in.pdf page` 生成，再挑关键页转 `.webp`。
- 存放到 `readings/_media/<slug>/`（或 `frontier/vendors/<v>/_media/<slug>/`），文件名 snake_case，单张 ≤ 400 KB / ≤ 1600 px。
- 在正文用 `<figure class="ext-fig">` 引用，`<img alt>` 必填，`<figcaption>` 写来源链接 + 抓取日期（视频加 `?t=` 定位）。**规则以 [`_assets/DESIGN_STANDARD.md`](../../_assets/DESIGN_STANDARD.md) §4.5 为准。**

### Step 3 — 选择落盘目录（Agent 自行判断）

| 内容性质 | 路径 | 文件名 |
|----------|------|--------|
| 外部厂商/访谈/行业信号 | `frontier/vendors/<vendor>/deep_dives/` | `YYYY-MM-DD_<slug>.html` |
| 自己的前沿洞察 | `insights/<tob\|toc\|cross>/` | `YYYY-MM_<slug>.html` |

`doc-meta` 必填：日期、受众（toB/toC/跨市场）、主题标签、状态（草案/对内/可对外）。

### Step 4 — 生成 HTML

推荐用 `render`（spec + body 分文件）：

```bash
python3 skill/video-digest/video_digest.py render \
  -o insights/cross/2026-06_example.html \
  -s insights/_drafts/video_<id>/spec.json \
  --body-file insights/_drafts/video_<id>/body.html
```

**spec.json 字段**：`title`, `subtitle`, `date`, `audience`, `tags`（数组）, `status`, `video_url`, `video_label`, `lede`, `brand_sub`, `accent`（可选）, `revision`（可选）

也可直接写完整 HTML，须复用 `_assets/_template_video_digest.html` 的结构与 `doc-meta` 约定。

### Step 5 — 验证

```bash
python3 _assets/build_manifest.py   # 可选，serve.py 会动态扫描
```

确认首页「最新发布」/ feed 出现新文档。筛选需在 **「全部」** 或对应受众（跨市场文选「跨市场」）。

## 工具速查

| 命令 | 作用 |
|------|------|
| `fetch URL` | 拉字幕，JSON 输出 stdout |
| `fetch URL --save` | 额外存草稿（meta.json + transcript.txt + GENERATE.md） |
| `fetch URL --cookies PATH` | YouTube bot check 时携带手动导出的 cookies.txt；抓完立即删 |
| `render -o PATH -s spec.json --body-file body.html` | 渲染站点 HTML |

模板：`_assets/_template_video_digest.html`  
工具源码：`skill/video-digest/video_digest.py`
