# 头部 AI 厂商博客深度调研

存放 **Anthropic、OpenAI** 等头部公司官方博客/发布会的**单篇深度分析**与**周期性动态摘要**。

## 与其他目录的关系

| 目录 | 用途 |
|------|------|
| `frontier_vendors/` | 外部头部厂商：原文脉络 + 深度拆解 + 对 ToB/进化的启示 |
| `insights/` | **你自己的**判断、结论、对内对齐材料 |
| `projects/` | 客户/专项 POC（如顺丰进化） |
| `references/company_docs/` | 公司内部文档、方案、项目介绍 |
| `toB_insight/` | ToB 行业洞察与布局调研 |

## 子目录

```
frontier_vendors/
├── README.md
├── _template_deep_dive.md
├── anthropic/
│   ├── README.md
│   ├── deep_dives/      # 单篇博客深度分析
│   └── digests/         # 多期动态汇总（原 frontier_ai_updates 迁入）
└── openai/
    ├── README.md
    ├── deep_dives/
    └── digests/
```

## 命名规范

- 深度分析：`YYYY-MM-DD_<slug>.md`（与发布日期对齐）
- 动态摘要：`YYYY-MM-DD_<主题>.md`
- 每篇深度文首保留：来源 URL、发布日期、产品/类型标签

## 写作标准（深度文）

1. 一句话结论
2. 发布了什么（事实）
3. 产品/技术架构拆解
4. **核心实现拆解（剧透式）** — 有工程实现（repo / API / SDK / 可执行配置包）时**必填**：只剧透 **2–4 个最核心模块** 的实现方式（主路径 data flow、扩展点如何挂接），不求面面俱到；超大仓库可另附 `*_实现拆解.md`
5. 对 ToB Agent 落地的启示
6. 与当前工作（进化、FDE、客户 POC）的关联
7. 待跟踪信号

新建深度文可复制 [`_template_deep_dive.md`](_template_deep_dive.md)。
