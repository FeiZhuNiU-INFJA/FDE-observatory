# CLAUDE.md — work_as_fde（FDE 洞察站）

这是一个以 `index.html` 为唯一入口的静态站点：自己的前沿洞察（`insights/`，含前瞻洞察 / 判断日志 / 落地指南）、阅读材料（`readings/`，论文/文章/视频的深度解读）、厂商信号（`frontier/`）、开源拆解（`opensource-analysis/`）。首页四大板块：insights · frontier · readings · oss。首页与各子 index 的列表由 manifest 自动生成。

**四大板块按「价值形态」分，不按「关于谁」分：** 洞察=我的原创论点 / 前瞻判断；厂商=如实还原+快评某公司的一手动作；阅读=第三方公开内容解读；开源=GitHub 项目拆解。判定看核心价值，不看提到了哪家公司——公司名一律是横切**标签**，不是板块（例：《Anthropic Managed Agents · 第三条路》落点是原创论点 → 归洞察，Anthropic 做 tag）。详见 [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) §7。

## 视觉标准（最重要）—— 动手前必读

**任何 insight / opensource HTML（或 `_assets/insight.css`）的创建、改写、重构，先读 [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) 并遵循。** 那是视觉标准的单一可信源；本文件只放不变的几条铁律。

不可违反：
- **杂志级视觉，不是文字堆。** 每篇长洞察 ≥3 个 bespoke（专属）视觉块，用内联 SVG 把概念画出来。参考实现：`readings/2026-06_loop-engineering-coding-agent.html`、`readings/2026-06_claude-code-artifacts.html`。**外部图片**（论文图 / 演讲截帧 / 产品截图）在保真价值大于统一价值时可用，走 `.ext-fig` 组件、**不抵扣 ≥3 SVG 名额**，规则见 [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) §4.5。
- **CSS 分层。** `_assets/insight.css` = 全站单一外观入口（只在换全站外观时改）；单页差异（强调色、专属组件）一律写在本页 `<head>` 的 `<style>` 里。**绝不为一篇页面去改 insight.css。**
- **每页选一个与众不同的 accent**（写在本页 `:root`，含暗色变体），**避开语义色**（`--warn`/`--con`/`--pro`/`--info`）。
- **`.doc-meta` 必填**（日期 / 受众 / 标签 / 状态 + **全站每篇**两枚判断印章 `时机：X` `信心：Y`），否则 manifest 不收录 / 首页不盖章。印章是「判断台」的通用批注层——洞察/厂商/阅读/开源读完都留一句判断（时机=多久影响我们、信心=多确定）。词表与语义见 [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) §7。
- **SVG 要无障碍**（`role="img" aria-label`）、**动画要兜底**（`prefers-reduced-motion`）。

## 发布机制（要点）

- **预览必须用 `python3 serve.py`**（UTF-8 + `/_manifest.json` 动态端点；**不要**用 `python3 -m http.server`）。
- **新增/改 HTML 后跑 `python3 _assets/build_manifest.py`** 重建静态快照（`file://` 访问需要）。

## Python 环境建议

站点脚本只用 Python 3 标准库（`serve.py` / `build_manifest.py`），任意 Python 3.10+ 均可运行。视频解读工作流依赖第三方 [yt-dlp](https://github.com/yt-dlp/yt-dlp)，按需 `pip install yt-dlp`。

## 进阶文档

| 我要… | 看 |
|-------|-----|
| 建页前查视觉标准 | [`_assets/DESIGN_STANDARD.md`](_assets/DESIGN_STANDARD.md) |
| 视频解读工作流 | `skill/video-digest/SKILL.md` |
| 设计系统源码 | `_assets/insight.css` · `_assets/insight.js` |
| 建页模板 | `_assets/_template_insight.html` |

## 其他

- 提交前用 `python3 serve.py` 肉眼验收亮/暗两套主题 + 移动端。
- 改 `_assets/insight.css` 是全站级变更，改完回来同步 `DESIGN_STANDARD.md` 的 token 描述。
