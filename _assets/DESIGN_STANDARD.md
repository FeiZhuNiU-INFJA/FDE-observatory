# FDE 洞察站 · 视觉设计标准 (Design Standard)

> **这是单一可信源（single source of truth）。** 任何 insight / opensource HTML 动手之前先读本文；要演进标准 = **改本文**（再让两份 enforcer —— 根 `CLAUDE.md` 与 `.cursor/rules/insight-visual.mdc` —— 继续指向这里）。
>
> **参考实现（gold standard，建页时对照这两页）**
> - `insights/cross/2026-06_loop-engineering-coding-agent.html` —— 五个 bespoke 视觉块（双态对照 / 嵌套层级 / 循环引擎 / 流水线 / 递进卡）
> - `insights/cross/2026-06_claude-code-artifacts.html` —— 六个 bespoke 视觉块（终端→页面 / 同名对比 / 发布流水线 / 约束笼 / 模式卡 / AND 门槛）
>
> 初版：2026-06-21 · 维护者：改本文即改标准。

---

## 0. 一句话标准

**杂志级视觉，不是文字堆。** 每篇长洞察必须自带 **≥3 个 bespoke（专属）视觉块**，用内联 SVG 把概念画出来，而不是用段落讲出来。文字服务于视觉，不是反过来。

---

## 1. 分层架构（Layering）—— 最重要的一条

| 层 | 文件 | 改它意味着 |
|----|------|-----------|
| **全站基底** | `_assets/insight.css` | 改 = 全站所有页面变样。**只在确实要换全站外观时动它**（换字体/色板/底纹/基础组件）。 |
| **全站行为** | `_assets/insight.js` | 主题切换、TOC 生成、scroll-spy、reveal 动画。一般不动。 |
| **单页强调色** | 每页 `<style>` 里覆盖 `--accent` / `--accent-soft`（+ 可选 `--accent-deep` / `--accent-ink`） | 改 = 只这一页的强调色变。**这是常规操作。** |
| **单页 bespoke 组件** | 每页 `<style>` 里新增专属 class（`.medium`、`.duo`、`.cage`…） | 改 = 只这一页的专属视觉变。**每页独立，不外溢。** |

**铁律：绝不为一篇页面去改 `_assets/insight.css`。** 单页的一切差异（颜色、组件）都写在自己 `<head>` 的 `<style>` 里。这样全站外观可以在 insight.css 一处统一升级，单页不被牵连、也不会污染别页。

> 底纹 `body::before`（蓝图点阵）是全站统一的工程氛围；某页要纯净背景，在该页 `<style>` 里 `body::before{content:none}` 关掉（特例 opt-out）。

**特例页 opt-out**（自定义设计、脱离全站外观）：除 `body::before{content:none}` 外，可能再加 `:root{--display:var(--serif)}` 让 display 字体回退。当前特例：`index.html`（首页）、`insights/cross/specflow_vericoding_*`（DM Serif + 焦橙）。原则：**统一多数，留特例**；特例是少数、有意的。

**反模式（snapshot drift 气味）**：单页 `<style>` 里**重新定义基础规则**（`body` / `h1` / `.toc-aside` / `.doc-header` 等）= 该页正偏离共享基底、冻成了「快照」。基础规则只该活在 `insight.css`；单页 `<style>` 只放 accent + bespoke 组件。看到这个气味 → 把基础规则还回 insight.css，让该页回到链接共享文件。

---

## 2. 页面骨架（Skeleton）—— 必须的结构

每篇 insight HTML 按这个顺序（复制 `_assets/_template_insight.html` 起步）：

```
<head>
  charset / viewport / title
  fonts <link>（或依赖 insight.css 的 @import，二选一）
  <script mermaid>（仅当用 mermaid 时；偏好 bespoke SVG，可省）
  <link rel="stylesheet" href="<相对深度>/_assets/insight.css">
  <style>  ← 本页 accent 覆盖 + bespoke 组件 CSS 全放这里
</head>
<body>
  .topbar > .topbar-inner
    .brand ( .brand-home[→首页] + 标题 + .brand-sub )
    .actions ( #tocBtn ☰  +  #themeBtn ◐ )
  #drawerOverlay
  aside#drawer ( h5 目录 + ul#drawerToc )
  .container
    aside.toc-aside ( h5 目录 + ul#toc )   ← 桌面侧栏，insight.js 从 article h2/h3[id] 自动生成
    article
      header.doc-header ( h1 + 副标题 p + .doc-meta + .hero-stats + 信源链接 )
      .lede                       ← 核心论点
      .callout.callout-accent     ← 「一页要点」
      h2#id × N ( <span class="sec-num">一</span>标题 + <a class="anchor"> + p.kicker )
        … bespoke 视觉块 / .table-wrap / .callout …
      <hr/> + 修订记录 p
      .doc-footer ( → 总索引 / 相关篇 )
  <script src="<相对深度>/_assets/insight.js">
</body>
```

**insight.js 依赖的 hook（不要改名）：** `#tocBtn` `#themeBtn` `#drawerOverlay` `#drawer` `#drawerToc` `#toc`。`article h2/h3[id]` 自动进 TOC。主题存 `localStorage: site-theme`。

---

## 3. 必需组件（Required components）—— 每篇长洞察都该有

| 组件 | class | 作用 | 备注 |
|------|-------|------|------|
| 元数据 | `.doc-meta` | manifest 收录的依据 | **必填**，否则页面不进索引。见 §7 |
| 顶部数据条 | `.hero-stats > .hero-stat` | 杂志感「数据条」，3–4 个关键数 | `<div class="num">16<small>MB</small></div><div class="lab">…</div>` |
| 核心论点 | `.lede` | 加粗一句结论抓读者 | 左边框 accent + 渐隐底 |
| 一页要点 | `.callout.callout-accent` | 5–7 条 bullet 速览 | `.callout-tag`「一页要点」 |
| 章节序号 | `<span class="sec-num">一</span>` | 中文序号 + h2 | 序号用 display 斜体、accent 色 |
| 小标题眉 | `p.kicker` | h2 下方一行英文/定位 | mono、字间距大、带「—」前缀 |
| 表格 | `.table-wrap > table` | 任何表格都包一层 | 自带横向滚动 |
| 提示框 | `.callout` + `-pro/-con/-warn/-info/-accent` | 风险/判断/行动框 | `.callout-tag` 标题 |
| 卡片网格 | `.card-grid > .card` | 并列要点 | `.card-eyebrow` 小标题 |
| 入场动画 | `.reveal`（+ `.d1`–`.d4` 延迟） | 滚动触发淡入 | insight.js 自动加 `.in` |
| 页脚 | `.doc-footer` + 修订记录 | 回索引 / 相关篇 / 修订日期 | |

---

## 4. Bespoke 视觉块 —— 真正的区分度

### 4.1 硬性要求
- 每篇长洞察 **≥3 个 bespoke 视觉块**（不是共享组件，是本页专属）。
- 每个块 = 一组**本页命名**的 class（如 `.medium`/`.duo`/`.flow`/`.cage`/`.pats`/`.gate`），CSS 写在本页 `<style>`。
- 视觉用**内联 SVG**（stroke 描边、`currentColor`、配色取自 token），**不用外部图片**（也契合 artifact 的 CSP 友好性）。

### 4.2 一个 bespoke 块的标准 recipe
1. **命名**：取一个语义化的顶层 class（如 `.cage`），子元素带前缀（`.cage-core` `.cage-bar` `.cage-verdict`）。
2. **容器**：`border-radius: 12–18px`、`var(--surface)` 底、`var(--border)` 描边、`var(--shadow)` 阴影。
3. **交互**：hover 微动（`transform: translateY(-3px)` + border 变 accent）。
4. **入场**：顶层加 `.reveal`。
5. **响应式**：`@media (max-width: 760/820/860/980/1024px)` 降列 / 改方向（如横向箭头转纵向 `↓`）。
6. **图标**：统一用 Lucide 风格 24×24 描边 SVG（`stroke-width="1.7"` `stroke-linecap="round"` `stroke-linejoin="round"` `fill="none"`）。

> ⚠ **标题层级别污染 TOC**：`insight.js` 会把 `article h2/h3[id]` 自动收进侧栏 TOC。bespoke 视觉块里的**标签性文字用 `div` / `h4`**（不加 `id`），**不要**用 `h2/h3[id]`，否则 TOC 被视觉块标题刷屏。只有真正的正文章节才用 `h2/h3[id]`。

### 4.3 SVG 硬规则
- **字体**：SVG 内文字一律用样式表指定（`.xxx text { font-family: var(--mono) }`）；**不要**在 SVG 属性里写 `var()`（仅 CSS 上下文解析）。display 数字另起一条 `.nums text { font-family: var(--display); font-weight:700 }`。
- **`var()` 陷阱（完整版）**：`var(--x)` 在 SVG 表现属性里**不解析**——`fill="var(...)"`、`stroke="var(...)"`、`stop-color="var(...)"`、`font-family="var(...)"` 全都会失效。正确做法：用 `<g style="color:var(--x)">` 包一组 + 内部 `stroke="currentColor"`；需要双色时用内联 `style="fill:var(--x)"`（`style` 属性走 CSS 上下文，能解析）。**`currentColor` 写在表现属性里是 OK 的**（它不是 `var()`）。
- **着色**：用 `<g style="color:var(--accent)" stroke="currentColor">` 包一组；数据可视化配色取 token：`--pro` `--con` `--warn` `--info` `--rust`。
- **无障碍**：每个装饰性 `<svg>` 加 `role="img" aria-label="…"`。
- **动画**：克制的循环（`orbit` 旋转、`dash-flow` 流光、`live-pulse` 呼吸），**必须**在页尾 `@media (prefers-reduced-motion: reduce)` 里关掉本页动画。

### 4.4 已验证的视觉模式（建页时按概念选型）
| 想表达 | 推荐模式 | 参考页 class |
|--------|---------|-------------|
| 范式转移 / 前后对比 | 双态对照（左旧右新 + 中间箭头） | `.shift` / `.medium` |
| 概念嵌套层级 | 套娃式嵌套框 | `.nest` |
| 循环 / 自运转系统 | 中心闭环 + 节点 + 基座 | `.engine` |
| 流程 / 流水线 | 横向 N 步 + 步间箭头 + 循环回注 | `.pipe` / `.flow` |
| 递进风险 / 多维度 | 递进卡片（带严重度条） | `.debts` |
| 同名不同物 / 对照 | 双卡 + VS 标 | `.duo` |
| 约束 / 边界 | 中心物 + 放射栅栏 | `.cage` |
| 模式清单 / 能力集 | 图标卡网格 + 横通栏 | `.mods` / `.pats` |
| 启用条件（AND 逻辑） | 开关/LED 卡 + AND 注脚 | `.gate` |

---

## 5. 配色 / Accent 登记

**每页选一个与众不同的 accent**（写在本页 `:root`），**避免与语义色撞车**：

| 已用 accent | 色 | 页面 |
|-------------|-----|------|
| 默认 | `#4338ca` indigo | （未覆盖时） |
| teal | `#0d9488` | Loop Engineering |
| blue | `#2563eb` | Dynamic Workflows（注：与 `--info` 同值，老页，新页避免） |
| violet | `#7c3aed` | Artifacts |

**禁用页面 accent（它们是语义色，撞了会让 callout/pill 失去含义）：**
`--warn #b45309` · `--con #dc2626` · `--pro #16a34a` · `--info #2563eb`

**暗色必须配套**：本页 `<style>` 里同时写 `[data-theme="dark"]` 的 `--accent` / `--accent-soft` / `--accent-ink` 变体（参考 Artifacts 页）。

**完整 token 清单**见 `_assets/insight.css` `:root` 与 `[data-theme="dark"]`。

---

## 6. 可访问性 & 响应式（底线）
- 每个 `<svg>` 有 `role="img" aria-label`。
- 断点：`1024px`（TOC 侧栏隐藏 / 抽屉出场）、`980/860/820/760`（网格降列）、`640/560`（数据条/卡片 2 列或 1 列）。
- 锚点偏移已由 `--anchor-offset: 88px` 处理；新增固定头组件时别破坏它。
- 所有动画受 `@media (prefers-reduced-motion: reduce)` 约束。
- 中英文混排：标题中英用 `<span class="en">`（display 斜体 / accent 色）。

---

## 7. 文件 / 路径 / manifest（发布机制要点）

> 完整发布规范见 `.cursor/rules/site-publishing.mdc`，这里只列与视觉相关的硬约束。

- **四大板块按「价值形态」分，不按「关于谁」分**（避免一篇文章两边都想放）：
  - **前沿洞察** `insights/` = 这篇的核心价值是**我的原创论点 / 前瞻判断**（市场只是原料）。
  - **厂商动态** `frontier/` = 价值是**如实还原 + 快评某公司的一手动作**（重点在准确记录它做了什么）。
  - **阅读材料** `readings/` = 第三方公开内容（论文 / 播客 / 演讲 / 视频）的深度解读。
  - **开源拆解** `opensource-analysis/` = GitHub 开源项目的代码级拆解。
  - **判定看核心价值，不看提到了哪家公司。** 例：《Anthropic Managed Agents · 第三条路》落点是「第三条路」这个原创论点 → 归**洞察**，而「Anthropic」降级成主题标签（在厂商语境下靠 tag 照样筛得到）。公司名一律是横切标签，不是板块。
- **位置**：`insights/{tob,toc,cross}/YYYY-MM_<slug>.html`；阅读材料 = `readings/YYYY-MM_<slug>.html`；opensource = `opensource-analysis/`。
- **相对路径深度**（到 `_assets/`）：
  - `insights/<audience>/` → `../../_assets/`
  - `insights/<audience>/<subdir>/` → `../../../_assets/`
  - `readings/` → `../_assets/`
  - `frontier/vendors/<v>/deep_dives/` → `../../../../_assets/`
- **`.doc-meta` 必填**（manifest 解析规则）：
  - 第 1 个 `<span>` = 日期（`YYYY-MM-DD` / `YYYY-MM` / `YYYY-QN`）
  - 含「ToB/B端/企业」→ tob；「ToC/C端/消费者」→ toc；「跨市场」→ cross
  - 其余 span = 主题标签；状态 = 草案 / 对内 / 可对外 / 已归档
  - **两枚判断印章（全站每篇必填）**：写 `<span>时机：X</span>` `<span>信心：Y</span>`，会自动渲染成首页 feed / 精选卡上的两枚圆形钤印。这是「判断台」的通用批注层 —— 不管洞察 / 厂商 / 阅读 / 开源，读完都留一句判断。
    - 时机（这个信号多久会影响我们 / 该多快行动）：`已发生` / `进行中` / `6–12 月` / `1–2 年` / `2 年+`
    - 信心（我多确定这个判断成立 / 这个信号有多可信）：`高` / `中` / `观察中`
    - 语义按板块自适应：洞察=我的预测应验窗口；厂商/阅读/开源=这个一手信号对我们的意义与可信度。
    - 若文章没写，`_assets/stamps.json` 里按 path 的兜底值才会生效（文章内写的优先）。
- **`_` 开头的目录/文件**（`_drafts/`、`_source/`、`_test.html`）不进 manifest。
- **预览必须用** `python3 serve.py`（UTF-8 + `/_manifest.json` 动态端点）。
- **新增/改 HTML 后**：`python3 _assets/build_manifest.py` 重建静态快照（`file://` 访问场景需要）。
- **站点边界**：`projects/`、`references/` 不进导航。

---

## 8. 新建 insight 页面 · Pre-flight 清单

```
- [ ] 从 _assets/_template_insight.html 复制起步，放对目录、命名 YYYY-MM_<slug>.html
- [ ] 相对路径深度算对（到 _assets/）
- [ ] <style> 里设本页 accent（避开语义色）+ 暗色变体
- [ ] doc-header：h1（中英混排）+ 副标题 + doc-meta（日期/受众/标签/状态 + 两枚印章「时机：X」「信心：Y」）+ hero-stats + 信源链接
- [ ] lede 核心论点 + callout-accent「一页要点」
- [ ] ≥3 个 bespoke 视觉块（命名 class + 内联 SVG + reveal + 响应式）
- [ ] SVG 有 role/aria-label；动画有 reduced-motion 兜底
- [ ] 章节用 sec-num + kicker；表格包 .table-wrap；判断框用对应 callout
- [ ] doc-footer：回总索引 + 相关篇 + 修订记录
- [ ] hook 齐全：#tocBtn #themeBtn #drawer* #toc，<script insight.js>
- [ ] python3 _assets/build_manifest.py → 确认被收录、title/date/audience/tags 正确
- [ ] python3 serve.py 肉眼验收亮/暗两套主题 + 移动端
```

---

## 9. 如何更新本标准（这就是「可更新」的那一处）

1. **小改**（新组件 recipe、新 accent、措辞）：直接编辑本文。
2. **新 gold-standard 页落地后**：把它的**新** bespoke 模式回填到 §4.4 表格 + §5 accent 登记（保持「标准 = 最佳实践的提取」闭环）。
3. **全站外观升级**：改 `_assets/insight.css`，再回来同步本文的 §1/§3/§5 token 描述。
4. 改完 **`python3 _assets/build_manifest.py` 不影响本文**（本文是 Markdown，不进 manifest）。
5. enforcer（`CLAUDE.md` / `.cursor/rules/insight-visual.mdc`）**只放不变的几条铁律 + 指针**，细节全在本文，避免三处漂移。

> 原则：**标准本体只此一份；enforcer 越薄越好。**
