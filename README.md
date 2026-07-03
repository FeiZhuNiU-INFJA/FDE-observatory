# work_as_fde · FDE 洞察站

> **走在最前沿**：对未来行业形态、技术演进、真实落地路径保持可验证的深刻判断；一线探索只为沉淀可复用洞察，而非一次性交付。
>
> toB / toC / 跨市场，永远走在最前沿。

## 本地预览

```bash
cd /path/to/work_as_fde
python3 serve.py           # 默认 8080
# python3 serve.py 9000    # 自定义端口
# 打开 http://localhost:8080
```

> 必须用 `serve.py`，**不要**直接用 `python3 -m http.server`。`serve.py` 提供两件事：
>
> 1. **UTF-8 charset** —— 所有 `.md`/`.txt`/`.html` 强制 UTF-8，避免中文乱码
> 2. **`/_manifest.json` 动态端点** —— 实时扫描所有文档生成元数据 manifest，首页和各子 index 页面的列表通过 fetch 这个端点自动渲染

## 动态索引（重要）

**新增 HTML / MD 文件后，不需要手动改任何 `index.html`**。只要：

1. 把文件放到正确目录（`insights/<audience>/`、`frontier/vendors/<vendor>/{deep_dives,digests}/` 等）
2. 写好 HTML 的 `doc-meta` 区块（日期 / 受众 / 标签 / 状态）
3. 刷新页面 —— 各 index 列表会自动包含新文档

详细规范见 [`.cursor/rules/site-publishing.mdc`](.cursor/rules/site-publishing.mdc)。手动重建静态 manifest 快照（用于 file:// 直接访问场景）：

```bash
python3 _assets/build_manifest.py
```

## 目录结构（站点）

```
work_as_fde/
├── index.html                     # 站点唯一入口（可视化首页）
├── README.md                      # 本文件
│
├── _assets/                       # 共享 HTML 设计系统
│   ├── insight.css                # CSS（色板、排版、组件）
│   ├── insight.js                 # JS（主题切换、TOC、mermaid）
│   ├── manifest-render.js         # 动态渲染：各 index 列表从 manifest 自动生成
│   ├── build_manifest.py          # 扫描站点文档、提取元数据、生成 manifest.json
│   ├── manifest.json              # serve.py 启动时构建的快照（运行时由 /_manifest.json 端点覆盖）
│   └── _template_insight.html     # 新建洞察模板
│
├── insights/                      # 核心产出：自己的前沿洞察（含判断日志/落地指南）
│   ├── index.html
│   └── cross/                     # 跨市场底层洞察（agent_future、person_mining 等）
│
├── frontier/                      # 外部头部厂商信号
│   ├── index.html
│   ├── _template_deep_dive.md
│   └── vendors/
│       ├── anthropic/{deep_dives, digests}
│       └── openai/{deep_dives, digests}
│
├── readings/                      # 论文/文章/视频的深度解读
│   └── index.html
│
├── opensource-analysis/           # 开源项目架构拆解
│   └── index.html
│
└── skill/                         # Agent Skills（工作流 + 工具脚本）
    └── video-digest/
        ├── SKILL.md               # 视频解读 → 站点发布
        └── video_digest.py        # 拉字幕 / 渲染 HTML
```

## 新增材料规范

| 材料类型 | 格式 | 位置 |
|----------|------|------|
| 前沿洞察 | **HTML**（从 `_assets/_template_insight.html` 复制） | `insights/cross/YYYY-MM_<slug>.html` |
| 厂商博客单篇拆解 | Markdown | `frontier/vendors/<vendor>/deep_dives/YYYY-MM-DD_<slug>.md` |
| 周期动态摘要 | Markdown | `frontier/vendors/<vendor>/digests/YYYY-MM-DD_<主题>.md` |
| 论文/视频深度解读 | HTML | `readings/YYYY-MM_<slug>.html` |
| 开源项目拆解 | HTML | `opensource-analysis/<slug>.html` |

## 文档 doc-meta 必填字段

每篇洞察 HTML 的 `doc-meta` 区块必须包含：

- **日期**（`YYYY-MM-DD`）
- **受众标签**（`toB` / `toC` / `跨市场`）
- **主题标签**（如 `Agent OS` / `Persona` / `评测` / `落地`）
- **状态**（`草案` / `已发布`）

## 命名规范

- 洞察：`YYYY-MM_<slug>.html`（如 `2026-05_tob-agent-direction.html`）
- 厂商深度文：`YYYY-MM-DD_<slug>.md`

## 设计系统说明

> **视觉标准（必读）**：[`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) 是单一可信源——杂志级视觉、≥3 bespoke 视觉块、CSS 分层、accent 登记、pre-flight 清单全在这里。根 [`CLAUDE.md`](CLAUDE.md) 引用它。**改标准 = 改这一份。**

所有 HTML 共享 `_assets/insight.css` + `_assets/insight.js`，风格与 `insights/cross/person_mining_persona_distillation_2026-05.html` 保持一致：

- 亮/暗主题切换（`localStorage: site-theme`）
- 侧边栏 TOC + 移动端 drawer（自动从 `article h2/h3[id]` 生成）
- Mermaid 图表（主题自动联动）
- 组件：`callout-*`、`card-grid`、`pill-*`、`stats`、`table-wrap`、`lede`
- 默认 accent 色 `#4338ca`；单篇可在局部 `<style>` 覆盖 `--accent`

## 视频解读工作流

看到有价值的 YouTube / Bilibili 视频，说「帮我总结这个视频」即可。完整流程见项目 Skill：[skill/video-digest/SKILL.md](skill/video-digest/SKILL.md)

Agent 会：

1. 运行 `python3 skill/video-digest/video_digest.py fetch "<URL>"` 拉取字幕与元数据（需本机已装 [yt-dlp](https://github.com/yt-dlp/yt-dlp)）
2. 阅读字幕，撰写深度解读
3. 根据内容落盘到 `frontier/`、`insights/` 或 `readings/`（首页自动收录）

手动拉字幕：

```bash
python3 skill/video-digest/video_digest.py fetch "https://www.youtube.com/watch?v=xxx"
```

## 快速索引

| 我要… | 去这里 |
|--------|--------|
| 站点首页 | [`index.html`](index.html) |
| 看所有前沿洞察 | [`insights/index.html`](insights/index.html) |
| 看厂商动态 | [`frontier/index.html`](frontier/index.html) |
| 新建洞察 HTML | 复制 [`_assets/_template_insight.html`](_assets/_template_insight.html) |
