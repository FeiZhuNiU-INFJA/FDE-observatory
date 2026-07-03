<div align="center">

# 🛰️ FDE·OBS — Frontier Observatory

**走在最前沿的 AI 前沿观测台**

对未来行业形态、技术演进、真实落地路径——保持 **可验证的深刻判断**。
一线探索只为沉淀可复用洞察，而非一次性交付。

[**🌐 打开观测站 →**](https://feizhuniu-infja.github.io/FDE-observatory/)

<br />

[![GitHub stars](https://img.shields.io/github/stars/FeiZhuNiU-INFJA/FDE-observatory?style=for-the-badge&logo=github&color=eab308)](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/FeiZhuNiU-INFJA/FDE-observatory?style=for-the-badge&logo=github&color=6366f1)](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/FeiZhuNiU-INFJA/FDE-observatory?style=for-the-badge&logo=github&color=10b981)](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/watchers)
[![Last commit](https://img.shields.io/github/last-commit/FeiZhuNiU-INFJA/FDE-observatory?style=for-the-badge&logo=git&color=f97316)](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/commits/main)

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue?style=flat-square)](LICENSE)
[![Content: CC BY-NC 4.0](https://img.shields.io/badge/Content-CC%20BY--NC%204.0-orange?style=flat-square)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Built with GitHub Pages](https://img.shields.io/badge/Built%20with-GitHub%20Pages-181717?style=flat-square&logo=github)](https://pages.github.com/)

</div>

---

## ⚡ 30 秒读懂

这是一个**不发牢骚、不追热点**、只做深度判断的 AI 前沿知识站。

- **每一篇 = 一次可复用洞察**：不写"新闻"，写"我读完 / 拆完 / 想通了什么"
- **杂志级视觉**：每篇长洞察 ≥ 3 个专属 SVG 视觉块，不是 markdown 堆
- **四条主线**：自己的判断、厂商的信号、别人的好东西、开源里的实现

站点结构：一个 `index.html` 就是入口。**加了新文档只要跑一次 `build_manifest.py`，首页列表自动更新**——你不需要手动改任何 HTML。

## 🧭 四大板块

<table>
<tr>
<td width="25%" align="center"><h3>🔮</h3><b>前沿洞察</b><br /><sub>insights/</sub><br /><br />自己的判断日志与落地推演——ToB / ToC / 跨市场</td>
<td width="25%" align="center"><h3>📡</h3><b>厂商动态</b><br /><sub>frontier/</sub><br /><br />Anthropic / OpenAI 等头部厂商信号的深度解读与周期摘要</td>
<td width="25%" align="center"><h3>📚</h3><b>阅读材料</b><br /><sub>readings/</sub><br /><br />论文 / 长文 / 视频的深度拆解，只留"读完能用"的部分</td>
<td width="25%" align="center"><h3>🧬</h3><b>开源拆解</b><br /><sub>opensource-analysis/</sub><br /><br />拆项目架构，看什么设计聪明、什么问题没解决</td>
</tr>
</table>

## 🌟 为什么值得 Star？

- **一次读完就能用的深度**：不是链接集，不是新闻聚合——每篇都有独立观点、可验证的判断、可迁移的方法论
- **视觉认真到过分**：亮/暗双主题、mermaid 图表、bespoke SVG、移动端全适配。不糊弄读者
- **完全静态、零依赖**：GitHub Pages 直挂，随时 fork 自己搭一个
- **manifest 自动索引**：加新文档不改 HTML，首页永远最新

<div align="center">

**如果这个站有帮到你 —— [ ⭐ 点个 Star](https://github.com/FeiZhuNiU-INFJA/FDE-observatory) 是我持续更新的最大动力。**

</div>

## 🚀 快速开始

### 只是想看内容

直接打开线上版：**<https://feizhuniu-infja.github.io/FDE-observatory/>**

### 本地跑一份

```bash
git clone https://github.com/FeiZhuNiU-INFJA/FDE-observatory.git
cd FDE-observatory
python3 serve.py           # 默认 8080
# 打开 http://localhost:8080
```

> 必须用 `serve.py`，**不要**用 `python3 -m http.server`。前者提供 UTF-8 charset（防止中文 md 乱码）+ `/_manifest.json` 动态端点（改完 HTML 立即反映在首页列表）。

### Fork 后想改成自己的站

```bash
# 1. 修改 index.html 的品牌名 / footer GitHub 链接
# 2. 修改本 README 里 badges 的用户名
# 3. 加自己的洞察 HTML 到 insights/cross/ 下（复制 _assets/_template_insight.html）
# 4. 跑 python3 _assets/build_manifest.py 重建索引
# 5. git push，GitHub Pages 自动部署
```

## 🗂️ 目录结构

```
FDE-observatory/
├── index.html                     # 站点唯一入口
├── _assets/
│   ├── insight.css                # 全站设计系统（色板 / 组件 / 排版）
│   ├── insight.js                 # 主题切换 / TOC / mermaid
│   ├── manifest-render.js         # 动态渲染各 index 列表
│   ├── build_manifest.py          # 扫描文档、生成 manifest.json
│   ├── DESIGN_STANDARD.md         # 视觉标准 · 单一可信源
│   └── _template_insight.html     # 新建洞察模板
│
├── insights/cross/                # 跨市场底层洞察
├── frontier/vendors/{anthropic,openai}/  # 厂商深度 + 周期摘要
├── readings/                      # 论文 / 文章 / 视频解读
├── opensource-analysis/           # 开源架构拆解
└── skill/video-digest/            # 视频解读工作流
```

## ✍️ 写一篇新洞察

1. 复制 [`_assets/_template_insight.html`](_assets/_template_insight.html) 到目标目录（如 `insights/cross/YYYY-MM_<slug>.html`）
2. 填好 `doc-meta` 区块：**日期 / 受众（toB / toC / 跨市场）/ 主题标签 / 状态**
3. 遵循 [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) 视觉铁律（≥ 3 个 bespoke SVG 视觉块、page-level accent 色、CSS 分层）
4. 跑 `python3 _assets/build_manifest.py` 重建索引
5. `git push` —— GitHub Pages 自动上线

> **⚠️ 铁律**：不要为一篇文章去改 `_assets/insight.css`。单页差异全部写在自己的 `<head><style>` 里。这是保证全站视觉一致 + 单页可以有个性的唯一办法。

## 📹 视频解读工作流

看到值得深度拆解的 YouTube / Bilibili 视频？告诉 Agent「帮我总结这个视频」即可：

```bash
python3 skill/video-digest/video_digest.py fetch "https://youtube.com/watch?v=..."
```

流程会自动拉字幕 → LLM 阅读 → 生成 HTML → 收录进 `readings/`。需要本机装 [yt-dlp](https://github.com/yt-dlp/yt-dlp)。

完整规范见 [`skill/video-digest/SKILL.md`](skill/video-digest/SKILL.md)。

## 🤝 参与方式

这不是一个多人协作的项目（内容强个人视角），但欢迎：

- ⭐ **[Star](https://github.com/FeiZhuNiU-INFJA/FDE-observatory)** —— 让我知道有人在看
- 👀 **[Watch](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/subscription)** —— 新洞察上线时收到通知
- 🍴 **[Fork](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/fork)** —— 拿去改成自己的站点
- 💬 **[Discussions](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/discussions)** —— 讨论、反馈、指正
- 🐛 **[Issue](https://github.com/FeiZhuNiU-INFJA/FDE-observatory/issues)** —— 发现 typo / 事实错误 / 死链

## 📜 License

| 类型 | 授权 |
|---|---|
| **代码**（`_assets/*`、`serve.py`、`skill/*` 等） | [MIT](LICENSE) — 随便用 |
| **内容**（`insights/*.html`、`readings/*.html`、`frontier/**/*.md` 等） | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — 允许署名转载，禁止商用 |

## 📈 Star History

<a href="https://star-history.com/#FeiZhuNiU-INFJA/FDE-observatory&Date">
  <img src="https://api.star-history.com/svg?repos=FeiZhuNiU-INFJA/FDE-observatory&type=Date" alt="Star History Chart" width="600" />
</a>

---

<div align="center">

**由 [@FeiZhuNiU-INFJA](https://github.com/FeiZhuNiU-INFJA) 维护 · 持续观测中**

<sub>如果这个站有帮到你，Star 一下 ⭐ 就是最好的鼓励。</sub>

</div>
