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

### Step 2 — 撰写解读

阅读 `transcript`，写**深度解读**（非流水账摘要）。

风格参考（择近者）：

| 类型 | 范例 |
|------|------|
| 厂商/访谈信号 | `frontier/vendors/anthropic/deep_dives/2026-05-28_alex-albert-research-pm-interview.html` |
| 跨市场概念 | `insights/cross/2026-06_loop-engineering-coding-agent.html` |
| Claude Code 专题 | `frontier/vendors/anthropic/deep_dives/2026-05-28_claude-code-dynamic-workflows.html` |

必备结构：核心结论（lede）、一页要点、分节论证、FDE/ToB 映射（如适用）、待验证问题。

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
| `render -o PATH -s spec.json --body-file body.html` | 渲染站点 HTML |

模板：`_assets/_template_video_digest.html`  
工具源码：`skill/video-digest/video_digest.py`
