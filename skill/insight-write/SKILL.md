---
name: insight-write
description: >-
  Writes a new deep-dive HTML for the FDE insight site from any source
  (vendor blog / paper / repo / video / original idea), following the site's
  Design Standard (bespoke SVG, ext-fig, judgment stamps). Use when the user
  asks 写一篇新的文章 / 解读这篇 / 深度解读 / 拆一下这个开源项目 / 我想写个洞察 / 解读这个视频.
  视频的字幕提取先走 video-digest fetch，后续写作/落盘统一在这里。
  触发词：写洞察、解读博客、拆开源、读论文、解读视频、写深度文章。
---

# 深度文章写作 → 站点发布

FDE 洞察站**所有深度文章**的统一工作流。四种源类型（厂商博客 / 论文长文 / 原创洞察 / 开源拆解 / 视频）走同一条流程，只在 Step 1「拿源材料」上分岔。

**这个 skill 会做的事**：把「一份源材料 / 一个论点」→ 一篇符合 [DESIGN_STANDARD](../../_assets/DESIGN_STANDARD.md) 的杂志级 HTML，落到正确板块，manifest 自动收录。

**不做的事**：视频字幕的**底层提取**（工具在 [`skill/video-digest`](../video-digest/SKILL.md)，本 skill 会调用它）、首页布局改动、跨篇观点汇编。

---

## 覆盖的五种源类型（决定落盘板块）

| 源类型 | 核心问题 | 落盘板块 | 目录 |
|--------|---------|----------|------|
| 厂商博客 / 官方研究 / 访谈 | 「某公司**做了什么**，怎么看？」 | 厂商动态 | `frontier/vendors/<vendor>/deep_dives/` |
| 论文 / 长文 / 第三方演讲 | 「这份**公开材料**里的判断和局限？」 | 阅读材料 | `readings/` |
| 视频（YouTube / Bilibili） | 「这段访谈 / 演讲**说了什么信号**？」 | 视按核心价值归入以上三类之一 | 同上 |
| 原创洞察 / 前瞻判断 | 「**我自己的**论点是什么？」 | 前沿洞察 | `insights/<tob\|toc\|cross>/` |
| 开源项目拆解 | 「这个 repo 的**代码级**架构与取舍？」 | 开源拆解 | `opensource-analysis/` |

**判定看核心价值**，不看提到了哪家公司、不看载体（视频 / 博客 / 论文）。参考 [DESIGN_STANDARD §7](../../_assets/DESIGN_STANDARD.md)。例：读了 Anthropic 官方论文却主要在讲我自己的论点 → 归**洞察**，Anthropic 降级为 tag。视频访谈某厂商 PM 讲他们内部做法 → 归**厂商动态**。

---

## 工作流

```
Task Progress:
- [ ] 1. 抓源材料 + 判断板块 + 定 slug
- [ ] 2. 提取外部图片（如有）→ _media/<slug>/
- [ ] 3. 选 accent（避开语义色 + 已用色）
- [ ] 4. 起页面骨架（doc-header + hero-stats + lede + 一页要点）
- [ ] 5. 选 ≥3 bespoke SVG 模式（§4.4）+ 写章节
- [ ] 6. 盖两枚判断印章 + 修订记录
- [ ] 7. build_manifest + serve.py 亮/暗验收
```

### Step 1 — 抓源 + 判断板块 + 定 slug

**按载体取源（这一步分岔，之后合流）**：

| 载体 | 命令 | 产出 |
|------|------|------|
| 网页（博客 / 官方研究 / 长文） | `curl -sL "<URL>" -o /tmp/src.html` 或 WebFetch | HTML / Markdown 文本 |
| 论文 PDF | WebFetch 摘要页；PDF 存 `/tmp/paper.pdf` | 摘要 + 后续 Step 2 提图 |
| 视频（YouTube / Bilibili） | `python3 skill/video-digest/video_digest.py fetch "<URL>"` | JSON 含 `title`/`channel`/`transcript` 等；YouTube bot-check 处理见 [`video-digest/SKILL.md`](../video-digest/SKILL.md#youtube-触发-bot-检查怎么办) |
| GitHub 项目 | `git clone` 到 `/tmp/`；关键文件 Read | 代码 + README |
| 原创洞察 | 直接从对话/笔记进入 Step 3 | 论点 outline |

> **视频关键点**：`video-digest fetch` 只负责**拉字幕 + 元数据**。拿到 `transcript` 后回到本 skill 继续 Step 2–7。之前 `video-digest` 里的写作/落盘步骤已经并入本 skill，不要再走那条老路径。

**判定板块**（自问一次）：
1. **核心价值是什么？** —— 我的原创论点 / 还原某公司动作 / 解读第三方公开材料 / 拆代码架构
2. 若同时含多种，取「最重的那份」，其余降级为 tag。
3. **拿不准就归洞察 `insights/cross/`**（判断台的默认落点）。

**slug 命名**：`YYYY-MM-DD_<描述性-kebab>.html`（`frontier/`）或 `YYYY-MM_<slug>.html`（`insights/` / `readings/` / `opensource-analysis/`）。slug 用「概念名」而不是「厂商名 + 事件」（`global-workspace-j-space` ✓，`anthropic-new-post` ✗）。

### Step 2 — 提取外部图片（可选，规则参照 [§4.5](../../_assets/DESIGN_STANDARD.md)）

**何时提**：源材料含**关键图表 / 论文实验图 / 产品 UI 真截图 / 演示截帧**且用 SVG 复刻会失真 → 提；纯装饰图、AI 生图、可用 SVG 讲清楚的概念图 → **不提**。

**存放**（就近，`_media/` 目录以 `_` 开头，不进 manifest）：

| 板块 | 图片目录 |
|------|---------|
| `frontier/vendors/<v>/deep_dives/` | `frontier/vendors/<v>/_media/<slug>/` |
| `readings/` | `readings/_media/<slug>/` |
| `insights/<audience>/` | `_assets/media/<slug>/` |
| `opensource-analysis/` | `opensource-analysis/_media/<slug>/` |

**提取命令**：

```bash
# 官方博客 / 论文页里的关键图
curl -sL "https://cdn.example.com/fig1.png" -o frontier/vendors/<v>/_media/<slug>/fig1_key_result.png

# 论文 PDF 分页转图（选关键页）
pdftoppm -png -r 180 paper.pdf page   # 生成 page-1.png ...
# 挑几张，可选转 webp：
cwebp -q 82 page-4.png -o frontier/vendors/<v>/_media/<slug>/fig1_setup.webp

# 视频截帧（先 yt-dlp 拿源、再 ffmpeg 定位到关键时刻）
yt-dlp -f "bv[ext=mp4]/b" -o /tmp/vid.mp4 "<URL>"
ffmpeg -ss 00:12:30 -i /tmp/vid.mp4 -frames:v 1 -q:v 2 /tmp/frame.webp
# 或用封面：yt-dlp --write-thumbnail --skip-download "<URL>"

# 大图压缩到 ≤ 400KB / ≤ 1600px：
sips -Z 1600 in.png --out out.png
```

**引用结构**（**必须**用共享组件，CSS 已在 `_assets/insight.css`）：

```html
<figure class="ext-fig">
  <img src="../_media/<slug>/fig1_key_result.webp"
       alt="一句话描述图中信息（不是"图 1"）"
       loading="lazy" width="1600" height="900">
  <figcaption>
    来源署名 · <cite>论文/演讲/文章标题</cite> · 
    <a href="<原文 URL>#<anchor|?t=秒>" rel="noopener">来源</a> · 抓取 YYYY-MM-DD
  </figcaption>
</figure>
```

**硬约束**：
- 外部图片**不抵扣** §4.1 的 ≥3 个 SVG 名额（bespoke SVG 才是主力）
- `alt` 必填（信息描述）、`<figcaption>` 必写来源 + 抓取日期
- 单张 ≤ 400 KB / 宽 ≤ 1600 px、优先 `.webp`（透明用 `.png`）、文件名 snake_case

### Step 3 — 选 accent（写在本页 `<style>`）

**已登记**（[DESIGN_STANDARD §5](../../_assets/DESIGN_STANDARD.md)）：
- teal `#0d9488` (Loop Engineering)
- blue `#2563eb` (Dynamic Workflows；与 `--info` 撞，新页避开)
- violet `#7c3aed` (Artifacts)
- 深湖蓝 `#0f6a8a` / dark `#6dbfd8` (Global Workspace J-space) — 厂商动态推荐色

**避开语义色**：`--warn #b45309` / `--con #dc2626` / `--pro #16a34a` / `--info #2563eb`。

**必须写 dark 变体**：

```html
<style>
  :root {
    --accent: #0f6a8a;
    --accent-soft: #e6f1f6;
    --accent-deep: #0b4a62;
    --accent-ink: #093a4d;
  }
  [data-theme="dark"] {
    --accent: #6dbfd8;
    --accent-soft: #0f2a35;
    --accent-deep: #4ea3bd;
    --accent-ink: #b9e0ec;
  }
</style>
```

写完把新 accent + 页面路径回填到 [DESIGN_STANDARD §5](../../_assets/DESIGN_STANDARD.md) 登记表（Step 7 一起做）。

### Step 4 — 起页面骨架

从 [`_assets/_template_insight.html`](../../_assets/_template_insight.html) 复制起步。**相对路径深度**（到 `_assets/`）：

| 目录 | 前缀 |
|------|------|
| `insights/<audience>/` | `../../_assets/` |
| `readings/` | `../_assets/` |
| `frontier/vendors/<v>/deep_dives/` | `../../../../_assets/` |
| `opensource-analysis/` | `../_assets/` |

**doc-header 必备（[§3](../../_assets/DESIGN_STANDARD.md) + [§7](../../_assets/DESIGN_STANDARD.md)）**：

```html
<header class="doc-header">
  <h1>【中英混排 · display 大标题】</h1>
  <p style="font-size: 1.05rem; color: var(--text-muted); margin-top: -.3em;">【副标题：一句话定位】</p>
  <div class="doc-meta">
    <span>2026-07-06</span>                          <!-- 日期，第 1 个 span -->
    <span>【跨市场 / ToB / ToC】</span>              <!-- 受众判定关键词 -->
    <span>【主题标签 1】</span><span>【标签 2】</span>
    <span>【状态：草案 / 对内 / 可对外】</span>
    <span>时机：进行中</span>                        <!-- 判断印章 · 必填 -->
    <span>信心：中</span>                            <!-- 判断印章 · 必填 -->
  </div>
  <!-- hero-stats：3–4 个数据条 -->
  <div class="hero-stats">
    <div class="hero-stat"><div class="num">5<small>属性</small></div><div class="lab">GWT 判据</div></div>
    <!-- ... -->
  </div>
  <!-- 信源链接 -->
  <p style="color: var(--text-soft); font-size: .95rem;">
    源：<a href="<URL>" target="_blank" rel="noopener">【源标题】</a>
  </p>
</header>

<!-- 核心论点 -->
<div class="lede"><strong>核心论点：</strong>【一句话抓读者】</div>

<!-- 一页要点 -->
<div class="callout callout-accent">
  <div class="callout-tag">一页要点</div>
  <ul>
    <li>【要点 1】</li>
    <li>【要点 2】</li>
    <!-- 5–7 条 -->
  </ul>
</div>
```

**时机 / 信心值域**（[§7](../../_assets/DESIGN_STANDARD.md)）：
- 时机：`已发生` / `进行中` / `6–12 月` / `1–2 年` / `2 年+`
- 信心：`高` / `中` / `观察中`

**语义按板块自适应**：洞察 = 我的预测应验窗口；厂商 / 阅读 / 开源 = 这个一手信号对我们的意义与可信度。

### Step 5 — 挑 ≥3 个 bespoke SVG 模式 + 写章节

**从 [§4.4 已验证模式](../../_assets/DESIGN_STANDARD.md) 选型**（按你要表达的概念）：

| 想表达 | 模式 | 参考 class |
|--------|------|-----------|
| 前后对比 / 范式转移 | 双态对照 | `.shift` / `.medium` |
| 概念嵌套 | 套娃 | `.nest` |
| 自循环系统 | 中心闭环 | `.engine` |
| 流水线 / 流程 | 横向 N 步 | `.pipe` / `.flow` |
| 递进风险 | 严重度卡 | `.debts` |
| 同名不同物 | 双卡 + VS | `.duo` |
| 约束 / 边界 | 放射栅栏 | `.cage` |
| 能力清单 | 图标网格 | `.mods` / `.pats` |
| AND 逻辑门 | 开关卡 | `.gate` |

**每块 recipe**（[§4.2](../../_assets/DESIGN_STANDARD.md)）：
1. 命名 `.foo` + 子元素 `.foo-x`（前缀化，避免污染）
2. 容器：`border-radius: 12–18px` + `var(--surface)` + `var(--border)` + `var(--shadow)`
3. hover：`transform: translateY(-3px)` + border 变 accent
4. 顶层 `.reveal`（入场动画）
5. 响应式：≤ 760/820/860px 降列
6. SVG 内文字：CSS 里指定 `font-family`（**别在 SVG 属性里写 `var()`**，不解析）
7. 着色：`<g style="color:var(--accent)" stroke="currentColor">` 包一组
8. 每个 SVG 加 `role="img" aria-label="…"`

**章节结构（长文推荐 9 节，可裁）**：

```html
<h2 id="context"><span class="sec-num">一</span>背景与触发<a href="#context" class="anchor">#</a></h2>
<p class="kicker">— WHY NOW</p>
<!-- 章节正文 -->

<h2 id="claim"><span class="sec-num">二</span>核心论点<a href="#claim" class="anchor">#</a></h2>
<!-- ... -->

<h2 id="evidence"><span class="sec-num">三</span>关键证据 / 五属性核对<a href="#evidence" class="anchor">#</a></h2>
<!-- bespoke SVG 块 #1 -->

<h2 id="mechanism"><span class="sec-num">四</span>机制拆解<a href="#mechanism" class="anchor">#</a></h2>
<!-- bespoke SVG 块 #2 -->

<h2 id="fde-map"><span class="sec-num">五</span>FDE / ToB 映射<a href="#fde-map" class="anchor">#</a></h2>
<div class="table-wrap"><table>...</table></div>

<h2 id="strategy"><span class="sec-num">六</span>策略与取舍<a href="#strategy" class="anchor">#</a></h2>

<h2 id="pitfalls"><span class="sec-num">七</span>典型陷阱<a href="#pitfalls" class="anchor">#</a></h2>
<div class="callout callout-warn"><div class="callout-tag">风险</div>...</div>

<h2 id="actions"><span class="sec-num">八</span>下一步 (1–2 周)<a href="#actions" class="anchor">#</a></h2>
<div class="callout callout-pro"><div class="callout-tag">行动清单</div>...</div>

<h2 id="open-questions"><span class="sec-num">九</span>待验证 6 问<a href="#open-questions" class="anchor">#</a></h2>
<ol><li>...</li></ol>
```

**⚠ TOC 污染防线**（[§4.2](../../_assets/DESIGN_STANDARD.md)）：bespoke 块内的标签性文字用 `<div>` 或 `<h4>`（**不加 id**），只有真正的正文章节才用 `h2/h3[id]`。否则侧栏 TOC 被视觉块标题刷屏。

### Step 6 — 印章、修订记录、页脚

页尾必须有：

```html
<hr />
<p style="font-size: .85rem; color: var(--text-muted); text-align: center;">
  修订记录：2026-07-06 初稿
</p>

<div class="doc-footer">
  <a href="../../index.html">← 首页</a>
  ·
  <a href="../index.html">相关板块索引</a>
</div>

<!-- reduced-motion 兜底：本页动画一律关掉 -->
<style>
  @media (prefers-reduced-motion: reduce) {
    .reveal { opacity: 1 !important; transform: none !important; }
    /* 本页 bespoke 动画（如 @keyframes orbit / dash-flow）都在这里关掉 */
  }
</style>
```

`insight.js` 会自动生成 TOC、加 reveal 动画、装主题切换。别改 hook 名（`#tocBtn` `#themeBtn` `#drawer*` `#toc`）。

### Step 7 — 收尾验证

```bash
# 1. 重建 manifest 静态快照
python3 _assets/build_manifest.py

# 2. 起本地预览（UTF-8 + 动态 /_manifest.json）
python3 serve.py                     # 默认 8000，被占用则用 python3 serve.py 8766

# 3. 肉眼验收（必做，参考 §8 pre-flight）
#    - 亮色 + 暗色两套主题
#    - 移动端（<640px）不塌
#    - 侧栏 TOC 无冗余（bespoke 块的标签没被抓进去）
#    - 首页 feed / 板块 index 出现新文章
#    - 两枚印章渲染成圆章（feed 一行右侧）
```

**如果新 accent 是全新色**，回填到 [DESIGN_STANDARD §5](../../_assets/DESIGN_STANDARD.md) 登记表。

---

## Pre-flight 清单（[§8 精简版](../../_assets/DESIGN_STANDARD.md)）

```
- [ ] 板块选对（价值形态 vs 提到谁）
- [ ] 相对路径深度算对（到 _assets/）
- [ ] <style> 里设 accent + 暗色变体，避开语义色 & 已用色
- [ ] doc-meta 齐：日期/受众/标签/状态 + 时机：X + 信心：Y
- [ ] lede + callout-accent 一页要点
- [ ] ≥3 个 bespoke 视觉块（命名 class + 内联 SVG + reveal + 响应式）
- [ ] SVG 有 role/aria-label；动画有 reduced-motion 兜底
- [ ] 外部图片（如用）走 .ext-fig，alt + figcaption 必填，落 _media/
- [ ] 章节用 sec-num + kicker；表格包 .table-wrap
- [ ] 页脚：修订记录 + 回索引
- [ ] python3 _assets/build_manifest.py → 确认被收录
- [ ] python3 serve.py 亮/暗 + 移动端肉眼验收
```

---

## 常见坑（历次踩过）

| 坑 | 现象 | 对策 |
|----|------|------|
| SVG 属性里写 `var(--x)` | 颜色不生效 | 换 `<g style="color:var(...)" stroke="currentColor">` 或 `style="fill:var(...)"` |
| bespoke 块用 `h2[id]` | TOC 被刷屏 | 用 `<div>` / `<h4>` 无 id |
| 单页覆盖了 `body` / `h1` 基础规则 | 「快照漂移」 | 基础规则还回 `insight.css`；单页只放 accent + bespoke |
| 忘了写暗色 accent | 暗色下强调色刺眼 | `<style>` 里配 `[data-theme="dark"] { --accent... }` |
| 用外链图片 | 失效 / CSP 挡 | 落库到 `_media/<slug>/` |
| 印章漏填 | 首页 feed 无圆章 | 补 `<span>时机：X</span><span>信心：Y</span>` |
| 8000 端口被占 | serve.py 起不来 | `python3 serve.py 8766`（位置参数） |

---

## 参考

| 我要… | 看 |
|-------|-----|
| 视觉标准（**先读**） | [`_assets/DESIGN_STANDARD.md`](../../_assets/DESIGN_STANDARD.md) |
| 建页模板 | [`_assets/_template_insight.html`](../../_assets/_template_insight.html) |
| 参考实现（gold standard） | `insights/cross/2026-06_loop-engineering-coding-agent.html` · `insights/cross/2026-06_claude-code-artifacts.html` · `frontier/vendors/anthropic/deep_dives/2026-07-06_global-workspace-j-space.html`（含 `.ext-fig` 示范） |
| 视频解读工作流 | [`skill/video-digest/SKILL.md`](../video-digest/SKILL.md) |
| CSS 基底 | [`_assets/insight.css`](../../_assets/insight.css) |
| manifest 构建 | [`_assets/build_manifest.py`](../../_assets/build_manifest.py) |
