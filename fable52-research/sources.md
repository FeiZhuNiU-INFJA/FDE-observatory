# Claude Fable 5.2 资料索引

检索与访问日期：2026-11-12。共收录 **52 项资料**，其中 50 项获取到可用正文、节选或摘要，2 项正文未取得。长文抓取可能被截断；“已读取”不代表逐字审阅全文。报告引用编号与本索引一致。

P0 = 官方、原始研究或评测发布者；P1 = 专业媒体；P2 = 有方法或案例的专业社区；P3 = 一般综述、营销内容或未经复核的转述。层级衡量出处，不保证结论正确。Anthropic 多份文档算同一证据家族，转载同一实验不增加独立验证次数。

优先阅读：**01 发布页、02 规格、05 提示指南、15 千 Agent 工程、18 独立评测、43 VentureBeat 分析**。接入必读：06、07、08、24、31。

## 官方发布与接入文档

<a id="source-01"></a>
### [cite:1] Anthropic：Introducing Claude Fable 5.2 and Claude Mythos 5.2

https://www.anthropic.com/claude-fable-and-mythos-5-2

P0 · 2026-11-09 发布，11-11 修订 · 已读取正文，并用浏览器补读后半篇与脚注。产品定位、能力表、科学案例、护栏、EFS 与开放范围的总入口。**脚注 4 明确费马实验提供了 60 条陈述、定义、经典路线和 47 条已证引理**。客户引用是厂商选择的证言。

<a id="source-02"></a>
### [cite:2] Claude Platform：Fable 5.2 overview

https://platform.claude.com/docs/en/models/fable-5-2/overview

P0 · 动态文档 · 已读取。模型 ID、1M 上下文、128K 输出、知识截止、价格、API 默认 effort、生命周期与接入限制。确认 API 默认为 `high`。

<a id="source-03"></a>
### [cite:3] Claude Platform：What's new in Fable 5.2

https://platform.claude.com/docs/en/models/fable-5-2/whats-new-fable-5-2

P0 · 动态文档 · 已读取主要正文。四项破坏性变更、思考块绑定、computer use、advisor 配对、拒绝、价格与行为差异。区分新变更与从 5.1 继承的限制。

<a id="source-04"></a>
### [cite:4] Claude Fable 5.2 & Claude Mythos 5.2 System Card

https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card

PDF 原始地址：https://assets.claude.com/27d60918d218125e7504bc7354c4b4626ec56b11.pdf

P0 · 2026-11-09 · 已读取执行摘要、目录与开头节选，**未逐页审阅整份 PDF**。直接下载返回 403，因此不附本地 PDF。重要导航：§5.2 提示注入，§6.4 行为审计，§6.5.1 沙箱逃逸，§6.6 评估可靠性，§8 能力，§8.12 多 Agent。摘要披露 fallback 风险、43% 评估觉察与 SWE-bench Pro 93.0%。

<a id="source-05"></a>
### [cite:5] Claude Platform：Prompting Claude Fable 5.2

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2

P0 · 动态文档 · 已读取主要节选。非常有价值：提前停止、代码所有权、过度谨慎、子 Agent 成本、进度显示。包含提示修改的效果和 token 代价；这些是厂商内部实验。

<a id="source-06"></a>
### [cite:6] Claude Platform：Fable 5.2 / Mythos 5.2 migration guide

https://platform.claude.com/docs/en/models/fable-5-2/migration-guide

P0 · 动态文档 · 已读取主要正文。自建 Messages 请求迁移的主清单；包括 rate limit、采样参数、强制工具、CMEK、思考块和 advisor。Managed Agents 基础迁移更简单，但启用 advisor 时还要同步 advisor 模型。

<a id="source-07"></a>
### [cite:7] Claude Platform：Preserved thinking

https://platform.claude.com/docs/en/build-with-claude/preserved-thinking

P0 · 动态文档 · 已读取主要节选。对会话、记忆与上下文管理尤其关键：prefix / model / account 三类绑定；历史改写、工具变化、客户端压缩、重放会话的处理规则。

<a id="source-08"></a>
### [cite:8] Claude Platform：Refusals and fallback

https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback

P0 · 动态文档 · 已读取主要节选。HTTP 200 的 refusal、拒绝类别、计费、server-side 与 client-side fallback、实际 serving model、`usage.iterations`。API 的自动回退需要配置，不应照搬应用端行为。

<a id="source-09"></a>
### [cite:9] Claude Platform：API and data retention

https://platform.claude.com/docs/en/manage-claude/api-and-data-retention

P0 · 动态文档 · 已读取主要节选。数据处理方与 ZDR / HIPAA 的一般规则。**部分 Covered Models 列表仍仅列到 5.1**；涉及 5.2 时优先结合 02、06、31 与云平台具体说明。

<a id="source-10"></a>
### [cite:10] Claude Platform：Advisor tool

https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool

P0 · 动态文档 · 已读取主要节选。较小 executor 咨询较强 advisor；advisor 读取全轨迹、不执行工具、单独计费。部分通用模型列表未同步 5.2，应结合 03、06 确认配对与加密结果。

<a id="source-11"></a>
### [cite:11] Claude Managed Agents：Multiagent orchestration

https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration

P0 · 动态文档 · 已读取主要节选。subagents、dynamic workflows、advisor 的责任划分；子线程上限、持久性、共享环境和凭据。**产品的子 Agent 模式与千 VM 实验不是同一架构**。

<a id="source-12"></a>
### [cite:12] Anthropic：Developing Enterprise Frontier Safeguards with our customers

https://www.anthropic.com/news/enterprise-frontier-safeguards

P0 · 2026-09-01 · 已读取主要正文。EFS 的设计缘由：客户持有日志、密钥和人工复核权，自动系统做跨请求检测。5.2 的最新实施阶段看 01。

<a id="source-29"></a>
### [cite:29] Claude Platform：Fast mode

https://platform.claude.com/docs/en/build-with-claude/fast-mode

P0 · 动态文档 · 已读取节选。相同模型、更快推理配置；提升重点是输出速率，**不是首 token 延迟**。Messages 用 `speed: "fast"`；Microsoft Foundry 使用独立的 `-fast` 模型部署。

<a id="source-30"></a>
### [cite:30] Anthropic：Strengthening our defenses against distillation attacks

https://www.anthropic.com/research/distillation-defenses

P0 · 2026-10-12 · 已读取节选。5.2 发布页引用的反蒸馏背景。90%–99% 是 Anthropic 对被采集数据量减少的早期估计，**不是独立验证的 Fable 5.2 性能指标**。

<a id="source-31"></a>
### [cite:31] Claude Help Center：Covered Models

https://support.claude.com/en/articles/15425695

P0 · 本周更新 · 已读取节选。明确将 Fable / Mythos 5.2 列为 Covered Models；默认至少 30 天留存，调查或法律要求可能延长。例外应按资格及平台核实。

<a id="source-32"></a>
### [cite:32] Claude Help Center：Cyber Verification Program

https://support.claude.com/en/articles/14604842-cyber-verification-program

P0 · 动态文档 · 已读取节选。Defense / Red Team / Specialized 三层。**个人研究者、开源维护者和赏金猎人可以申请 Defense Access**，不能一概表述为 Mythos 仅接受机构申请。

<a id="source-50"></a>
### [cite:50] Claude Help Center：Fable 5.2 launch offers

https://support.claude.com/en/articles/17506494

P0 · 动态文档 · 已读取。Pro / Team standard 的一周额度至 11-16；reset 不是提高周额度。明确排除 Free 和若干 Enterprise 类型，不能说免费用户全面可用。

<a id="source-51"></a>
### [cite:51] Claude Platform：Effort

https://platform.claude.com/docs/en/build-with-claude/effort

P0 · 动态文档 · 已读取节选。参数写法 `output_config.effort`；effort 是行为信号，不是严格预算。通用模型枚举部分未同步 5.2；5.2 专属建议以 03、05 为准。

<a id="source-52"></a>
### [cite:52] Claude Platform：Compaction on demand

https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand

P0 · 动态文档 · 已读取主要节选。返回带签名的 compaction block；压缩完成后替换旧消息，原样保留 block。与客户端改写历史导致的 preserved thinking 问题直接相关。

## 科学与千 Agent 实验

<a id="source-13"></a>
### [cite:13] Anthropic：Testing Claude on real-world electronics design

https://www.anthropic.com/research/claude-electronics-design

P0 · 2026-11-09 · 已读取主要正文。Diode 合作的三款硬件、几何推理、自动布线、DFM、固件与装配；工作原型仍不能等同于量产认证完成。

<a id="source-14"></a>
### [cite:14] Anthropic：Formalizing Fermat's Last Theorem

https://www.anthropic.com/research/formalizing-fermats-last-theorem

P0 · **2026-09-04，旧实验** · 已读取。11 天、约 60 亿输出 token、Prove2Me、DAG 和人类高层指导。不是 11 月 5.2 的 28.7 小时实验。

<a id="source-15"></a>
### [cite:15] Claude engineering：Safely scaling multi-agent teams with Claude Fable 5.2

https://claude.dev/blog/safely-scaling-multi-agent-teams-with-fable-5-2/

P0 · 2026-11-09 · 已读取主要正文。**最值得读的工程材料**：1 lead + 999 helpers、独立 VM、Git、Postgres、gateway、五张自建协作表、错误难度估计、动态重分配、18 小时恢复点。还明确区分实验当时监控配置与后来加强的配置。

<a id="source-16"></a>
### [cite:16] Hexagon：The Hawking-Page transition at weak coupling

https://hexagonmath.org/2611.00175v1

P0 · 2026-11-07 · 已读取摘要与 provenance。Anthropic 提交，主要由 AI 生成，页面标注人类理解部分内容。物理学家提示并核对已知特例；是预印本，不等于社区已全面复核。

<a id="source-17"></a>
### [cite:17] Hexagon：The spinless modular bootstrap at large central charge

https://hexagonmath.org/2611.00174v1

P0 · 2026-11-07 · 已读取摘要与 provenance。给出约 9.1266 的精确渐近常数。**声明 Opus 5.5 后来也独立得到同一结果**，不能当作 Fable 独占能力的证明。

## 独立评测与公开产物

<a id="source-18"></a>
### [cite:18] Artificial Analysis：Fable 5.2 Release Intelligence, Performance & Price

https://artificialanalysis.ai/models/releases/claude-fable-5-2

P0（独立评测发布者）· 动态榜单，访问时指数 v5.0.1 · 已读取。五档 effort 的综合分、每题加权成本与推算时间。配置名包含 **Default Fallback**；不能当作无回退的纯模型结果。

<a id="source-19"></a>
### [cite:19] Artificial Analysis：Intelligence Benchmarking Methodology

https://artificialanalysis.ai/methodology/intelligence-benchmarking

P0（评测方法）· v5.0.1 · 已读取主要节选。9 项评测、四类各占 25%、重复次数、评分器、token 与 cache 成本口径。主要为英语文本评测，不能直接代表中文长文与所有多模态任务。

<a id="source-20"></a>
### [cite:20] Testing Models：What Claude Fable 5.2 can do

https://testingmodels.com/fable-5-2

P0（作者自测的原始发布页）/ P2（评测质量）· 已读取。41 份输出、21 个任务，含五 effort 档同题比较，成品可以直接打开。单次运行、没有统一质量分；费用为站方报告，未核对账单。

<a id="source-21"></a>
### [cite:21] Testing Models：How we test models

https://testingmodels.com/method

P0（方法原页）· 2026-11-12 页面计数 · 已读取。明确 one-shot、无成品修复、盲投票和局限。**通用方法页使用文件字符估算且不计思考 token，20 的专页却声明计入思考 token**，两个口径不能混算。

<a id="source-36"></a>
### [cite:36] Artificial Analysis：Fable 5.1 (Max, Default Fallback)

https://artificialanalysis.ai/models/claude-fable-5-1

P0 · 动态页 · 已读取节选。本次抓取显示 **53 分、7.63 美元/题**，与 26 发布日报道的 49 分、12.99 美元不同。缺少同版历史快照，不能用跨时点数据断言 5.2 成本准确翻倍。

## 云平台与产品接入

<a id="source-22"></a>
### [cite:22] AWS：Claude Fable 5.2 is now available on AWS

https://aws.amazon.com/about-aws/whats-new/2026/11/claude-fable-5-2-aws/

P0 · 2026-11-09 · 已读取。明确 **Amazon Bedrock 和 Claude Platform on AWS 两条路径**；列出符合资格客户的 ZDR 过渡例外。

<a id="source-23"></a>
### [cite:23] Microsoft Foundry：Fable 5.2 and Mythos 5.2 bring frontier intelligence

https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/claude-fable-5-2-and-mythos-5-2-bring-frontier-intelligence-to-microsoft-foundry/4564282

P0 · 2026-11-09 · 已读取。Foundry GA、Anthropic hosted、标准 / fast 价格、Mythos 授权、数据留存例外。大部分能力论述转述 Anthropic，不是微软独立评测。

<a id="source-24"></a>
### [cite:24] Vercel：Fable 5.2 now available on AI Gateway

https://vercel.com/changelog/claude-fable-5-2-now-available-on-ai-gateway

P0 · 2026-11-09 · 已读取。网关 ID `anthropic/claude-fable-5.2`；多 API 格式和 gateway fallbacks。**网关开 ZDR 会报错**；其模型回退列表与 Anthropic 原生 server-side fallback 不同。

<a id="source-33"></a>
### [cite:33] Microsoft Copilot：Available today, Fable 5.2 in Microsoft Copilot

https://techcommunity.microsoft.com/blog/microsoft-copilot-blog/available-today-anthropic-claude-fable-5-2-in-microsoft-copilot/4571829

P0 · 2026-11-11 · 已读取。Copilot Cowork / Studio 开始向符合资格用户推出，Work IQ 注入企业上下文；区域、组织和管理员配置影响可用性。

<a id="source-34"></a>
### [cite:34] Amazon Bedrock：Fable 5.2 model card

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5-2.html

P0 · 动态文档 · 已获取正文节选。平台规格、端点、程序接入、区域、服务层级等的导航入口。本次没有逐项核对区域清单。

<a id="source-35"></a>
### [cite:35] Amazon Bedrock：Abuse detection

https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html

P0 · 动态文档 · 已获取正文节选。AWS 平台数据留存与滥用检测规则入口；具体实施以云账户条款与配置为准。

## 专业媒体、中文实测与社区解读

<a id="source-25"></a>
### [cite:25] MarkTechPost：Same Model, Different Safeguards

https://www.marktechpost.com/2026/11/10/anthropic-claude-fable-5-2-mythos-5-2-release/

P1/P2 · 2026-11-10 · 已读取。覆盖广，清楚标注很多 benchmark 为厂商自报，方便快速扫描。页面转述不构成独立复现。

<a id="source-26"></a>
### [cite:26] R&D World：Hardware-design score and cost per task

https://www.rdworldonline.com/anthropic-says-fable-5-2-nearly-doubles-its-predecessors-hardware-design-score-token-prices-fell-20-but-the-cost-per-task-doubled-at-full-effort/

P1 · Brian Buntz，2026-11-09 · 已读取。硬件原型边界与 AA 成本的专业报道。**5.1 发布日数据与本次动态原页不一致**，其“翻倍”标题仅能代表文章当时口径。

<a id="source-27"></a>
### [cite:27] Clauding：1,000 Agents Formalize Fermat in 28.7 Hours

https://clauding.de/en/posts/fable-5-2-tausend-agenten-fermat-beweis/

P2/P3 · 2026-11-10 · 已读取，标注 AI-generated。德语社区英文解读；找到官方工程原页的有效线索。技术细节最终引用 15。

<a id="source-28"></a>
### [cite:28] nowosci.ai：Fable 5.2 in 41 Tests

https://nowosci.ai/en/article/fable-5-2-tests-max-effort-cost-tokens

P3 · 2026-11-11 · 已读取，明确 AI 生成且未编辑复核。与 Testing Models 同一发布者，**不是第二份独立实验**。提示高 effort 的成本与失败案例，最终看 20、21。

<a id="source-37"></a>
### [cite:37] Habr / GPTunneL：Claude Fable 5.2 подробный обзор

https://habr.com/ru/companies/gptunnel/articles/1106358/

P3 · 页面使用相对时间 · 已读取节选。俄语供应商综述，便于了解当地开发者传播；夸张表述、曝光量和命名解释不作事实依据。

<a id="source-38"></a>
### [cite:38] MindStudio：What Anthropic Actually Shipped

https://www.mindstudio.ai/blog/claude-fable-5-2-mythos-5-2-release

P2/P3 · 2026-11-10 · 已读取节选。低代码 Agent 厂商视角，突出 daily driver / advisor / orchestrator 与训练期限制。主要是发布材料分析，没有单独复现实验。

<a id="source-39"></a>
### [cite:39] AIToolsReview：Full Review, November 2026

https://aitoolsreview.co.uk/insights/claude-fable-5-2-mythos-5-2

P3 · 2026-11-10 · 已读取节选。广泛综述与创作者反应线索；标题“Review”不代表做了标准化实验，未将其所列创作者视为本次已验证来源。

<a id="source-40"></a>
### [cite:40] 赛博禅心 / 人人都是产品经理：实测 Claude Fable 5.2，78 分钟捏了个操作系统

https://www.woshipm.com/evaluating/6491703.html

P2 · 页面为相对时间 · 已读取主要节选。四个作者自测：浏览器迷你 OS、故宫角楼、黑洞渲染、动效短片。**浏览器模拟机不是 Anthropic 的笔记本原生 OS**。时间和额度仅为作者记录，未复跑。

<a id="source-41"></a>
### [cite:41] 硅星人 / 投资界：实测 Fable 5.2，IPO 味儿最冲的超强模型

https://news.pedaily.cn/202611/571624.shtml

P2 · 王兆洋、董道力，2026-11-10 · 已读取正文。模拟单摆数据的盲测、假设比较、异常值和外推；另有视觉产物不理想的反例。**0.26% 误差为作者自报，未获得原始数据与完整轨迹复核**；IPO 动机属评论。

<a id="source-42"></a>
### [cite:42] Tom's Hardware France：Gears of War 风格游戏演示

https://www.tomshardware.fr/il-demande-a-une-claude-fable-5-2-de-recreer-gears-of-war-avec-3-lignes-de-texte-le-resultat-est-bluffant/

P1/P2 · 2026-11-11 · 已读取。Matthew Berman 演示的二次报道，明确单关卡、动画缺陷、长时构建和理论 API 成本。**未读取原始完整会话/账单，不引用 8.63B token 或约 15,000 美元为已核实成本**。

<a id="source-43"></a>
### [cite:43] VentureBeat：New record benchmarks with 20% API cost reduction

https://venturebeat.com/technology/anthropic-releases-claude-fable-5-2-and-mythos-5-2-pairing-new-record-high-benchmarks-with-20-api-cost-reduction

P1 · 发布日报道 · 已读取。**最有价值的媒体分析**：FrontierCode 分 effort 成绩 / 成本、超时口径、OSWorld 完整通过与部分评分、客户证言的局限、有效任务成本。精确分档表为该媒体引自系统卡，本次未逐项回读 PDF 原表。

<a id="source-44"></a>
### [cite:44] DevX：What Is Claude Fable 5.2?

https://www.devx.com/artificial-intelligence-ai/what-is-claude-fable-5-2-anthropic-model-explained/

P2/P3 · 2026-11-11 · 已读取。FAQ 型技术综述。部分句子将 Mythos 说成“更强兄弟”、将 Xhigh 写成最高档、将促销 50% 口径表述得不准确；以 01、03、50 纠正。

<a id="source-45"></a>
### [cite:45] Basic Tutorials：Anthropic lowers the price and improves coding

https://basic-tutorials.com/news/claude-fable-5-2-is-here-anthropic-lowers-the-price-and-improves-coding-capabilities/

P2/P3 · 2026-11-10 · 已读取。覆盖面较全，但把 capsid 案例写成 Fable、将费马描述为没有数学参考，与 01 的最新脚注冲突。可作阅读线索，不能替代官方原文。

<a id="source-48"></a>
### [cite:48] TonyTechLab：API price down 20%, Mythos vulnerability finding

https://tonytechlab.com/tin-claude-fable-5-2-mythos-5-2-ra-mat-10-11-2026/

P3 · 2026-11-10 · 已读取节选。越南语成本和风险解读。**新 tokenizer 是早先代际变化，不能额外算成 5.1→5.2 的新涨幅**；该文不作为 tokenizer 定量依据。

<a id="source-49"></a>
### [cite:49] El Ecosistema Startup：Fable 5.2 / Mythos 5.2, 20% más barato

https://ecosistemastartup.com/anthropic-lanza-fable-5-2-y-mythos-5-2-20-mas-barato/

P3 · 已获取正文并提取来源链接。西语创业综述；用于追溯 43 的原始文章，不作为额外独立性能证据。

## 未获得正文的线索

<a id="source-46"></a>
### [cite:46] The Verge：Fable / Mythos 5.2

https://www.theverge.com/ai-artificial-intelligence/1030005/anthropic-claude-fable-mythos-5-2

预期 P1 · 由 27 引出，抓取为空。**未核验，不支撑报告事实**。检索中还出现对 TechCrunch 的转述，但未取得可用原始正文，未把这些转述算作 TechCrunch 已验证报道。

<a id="source-47"></a>
### [cite:47] 36氪：“话痨”Fable 5.2，降价是 Anthropic 说的，我可没答应

https://36kr.com/p/4063250504570757

搜索摘要可见，正文停留在安全检测页面。**未核验，不支撑报告事实**。标题和摘要仅提示继续关注 token 使用与动态榜单口径。
