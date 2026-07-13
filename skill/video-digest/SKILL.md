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

- 本机已安装 `yt-dlp`（`brew install yt-dlp` 或 `pip install yt-dlp`；若装成 pip user site 而 `which yt-dlp` 找不到，把 `~/Library/Python/3.x/bin` 加到 `PATH`）
- Plan B 备用：`brew install ffmpeg`（remux 音频） + `pip install -U openai-whisper` 或 `pip install faster-whisper`（本地转写）

## Plan A —— 官方字幕 + 妙记 ASR（默认走这条）

**优先级铁律**：能拿到原文字幕就一定用原文；没有原文字幕但拿得到音频，先送 **飞书妙记 ASR**（走 [`lark-minutes`](../../.trae-cn/skills/lark-minutes/SKILL.md)：`drive +upload → minutes +upload → minutes +detail --transcript`）。妙记质量、术语校准、说话人识别都比本地 whisper 稳。

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL"
```

可选保存草稿到 `insights/_drafts/video_<id>/`（把 transcript.txt / meta.json 落盘，避免占对话上下文）：

```bash
python3 skill/video-digest/video_digest.py fetch "视频URL" --save
```

**输出 JSON** 关键字段：`title`、`channel`、`platform`、`duration_label`、`upload_date`、`transcript`、`has_transcript`、`available_sub_langs`、`thumbnail`。

**常见问题**：

- `has_transcript: false` → 视频无官方字幕轨。**先走 Plan A 的音频→妙记路径**，不要立刻跳 Plan B。
- URL 不要转义反斜杠：`"https://youtube.com/watch?v=xxx"` ✓，`watch\?v\=` ✗。
- **YouTube 触发 bot check** → 见下一节。
- **B 站 412 Precondition Failed** → yt-dlp 走 `/x/player/wbi/v2` 拿视频格式会被风控拦；脚本内已回退到直接调 `/x/player/playurl` 拿 DASH 音频链接，遇到旧版脚本手动执行也行（见「B 站 412 应急」节）。

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

### B 站 412 应急

B 站的 `/x/player/wbi/v2` 视频格式接口有时会返回 412（无登录+风控）。**不要直接放弃**，改从 `/x/player/playurl` 直取 DASH 音频链接：

```bash
BVID=BV1i6Nu6vEoy
CID=$(curl -s -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/view?bvid=$BVID" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['cid'])")

AUDIO_URL=$(curl -s -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/video/$BVID/" \
  "https://api.bilibili.com/x/player/playurl?bvid=$BVID&cid=$CID&qn=16&fnval=16&fourk=1" \
  | python3 -c "import sys,json; a=json.load(sys.stdin)['data']['dash']['audio']; a.sort(key=lambda x:x.get('bandwidth',0)); print(a[0]['baseUrl'])")

curl -sSL -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/video/$BVID/" \
  "$AUDIO_URL" -o /tmp/$BVID.m4s
ffmpeg -y -i /tmp/$BVID.m4s -c copy /tmp/$BVID.m4a
```

拿到 m4a 后：Plan A 送妙记（`drive +upload`），Plan B 送本地 whisper。

## Plan B —— yt-dlp 下音频 + 本地 Whisper 转写（**仅当 Plan A 不可行时**）

**什么时候才允许走 Plan B**（任一命中即可）：

- 用户明确指定「不要发到飞书 / 内容敏感不能上传第三方」
- 飞书妙记额度耗尽 / 服务不可用 / 用户身份未登录且无法当场授权
- 内容极短（< 60s）且用户接受质量折扣，不值得走妙记转一圈

否则**默认必须走 Plan A**。Plan B 常见坑：中文口音/术语误识别、说话人不分、噪声段吐幻觉字符——都是要靠事后校对纠正的。

**执行流程**：

```bash
# 1) 只拉音频（yt-dlp 优先 m4a）——若 B 站 412，走上一节应急路径手抓 m4s
python3 skill/video-digest/video_digest.py fetch "<URL>" --save --audio-only

# 2) 本地转写（脚本自动选可用后端：mlx-whisper > faster-whisper > openai-whisper）
python3 skill/video-digest/video_digest.py transcribe insights/_drafts/video_<id>/<id>.m4a \
  --model medium --language zh
```

`transcribe` 会把 `transcript.txt` 写到 draft 目录，并把 `meta.json` 里的 `has_transcript` / `transcript_source` 更新为 `whisper:<model>`；下游 [`insight-write`](../insight-write/SKILL.md) 无需感知差异。

**模型选择**（Apple Silicon 建议）：

| 场景 | 模型 | 备注 |
|------|------|------|
| 中文口播（清晰） | `medium` | 平衡质量/速度，M2/M3 上 5 分钟音频约 1–2 分钟 |
| 中文口播（口音/术语多） | `large-v3` | 慢，但显著减少术语误识 |
| 英文快速试听 | `small` | 极快，仅用于内部预览 |

**Plan B 结束前必做**：产出的逐字稿在 `insights/_drafts/video_<id>/transcript.txt`，**必须人工/AI 通读一遍**做术语校对，尤其：

- 人名 / 公司名 / 产品名（whisper 常写错，如「Sierra」误听成「西拉」「Sarah」）
- 中英夹杂词（如「agent」被写成「艾真特」）
- 数字 / 版本号（模型幻觉高发区）

Plan A（妙记）的产出也建议校对，但优先级低于 Plan B。

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
| `fetch URL` | Plan A：拉字幕 + 元数据，JSON 输出 stdout |
| `fetch URL --save` | 额外存草稿（meta.json + transcript.txt + GENERATE.md） |
| `fetch URL --save --audio-only` | Plan B 第 1 步：跳过字幕，只下最低码率 m4a 存到 draft 目录 |
| `fetch URL --cookies PATH` | YouTube bot check 时携带手动导出的 cookies.txt；抓完立即删 |
| `transcribe <audio_path>` | Plan B 第 2 步：本地 whisper 转写；`--model medium/large-v3`、`--language zh` |

工具源码：[`video_digest.py`](./video_digest.py)（内含 `render` 子命令，历史遗留；新流程一律走 `insight-write`，不要再用 `render`）。
