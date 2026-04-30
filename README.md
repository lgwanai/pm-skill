# PM Skill

Product Manager Knowledge Assistant — 产品经理知识助手。

基于 [LLM Wiki v2](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) 方法论，将产品文档编译为结构化、带置信度评分的知识库，并通过多轮专家对话生成专业 PRD。

## 理念

**停止重复推导，开始积累编译。** RAG 检索后即忘，wiki 积累后复利增长。每次摄入新文档，知识库变得更丰富——交叉引用已存在，矛盾已被标记，综合结论已反映所有已读内容。

## 命令

| 命令 | 用途 |
|------|------|
| `/wiki <path>` | 摄入文档，提取实体/概念/关系，生成或更新 wiki |
| `/prd <description>` | 多轮产品专家对话 → 生成 PRD（含研究、冲突检测、结晶回流） |
| `/prd revise <name> <change>` | 修订已有 PRD，创建新版本 |

## 结构

```
pm-skill/
├── SKILL.md              # 指令定义（schema — 最重要的文件）
├── README.md
├── package.sh            # 打包脚本 → dist/pm-skill-YYYYMMDD.zip
├── references/
│   ├── prompts/
│   │   ├── compile.md        # /wiki 编译提示词（v2 scored confidence）
│   │   ├── prd-research.md   # /prd 产品专家研究流程
│   │   └── collect.md        # PRD 模板类型检测规则
│   └── templates/
│       ├── prd-tob.md        # ToB 后台系统模板
│       └── prd-toc.md        # ToC 消费产品模板
└── wiki/                 # 编译后的知识库（运行时生成）
    ├── entities/         # 实体页面（具体事物：系统、指标、数据表）
    ├── concepts/         # 概念页面（抽象思想：方法论、模式、原则）
    ├── index.md          # 知识索引
    ├── glossary.md       # 术语表
    └── log.md            # 操作日志
```

## 核心机制

### Wiki — 知识生命周期管理 (v2)

| 机制 | 说明 |
|------|------|
| **置信度评分** | `Confidence = (sources / (sources + 2)) × recency_weight`，随时间衰减，每次确认重置 |
| **Supersession** | 新旧矛盾显式链式追踪：`⬅ SUPERSEDED 旧说法` → `➡ CURRENT 新说法` |
| **Consolidation tiers** | Working（原始文档）→ Episodic（实体页面）→ Semantic（概念页面），三层压缩晋升 |
| **Typed relations** | `depends_on`, `supersedes`, `embodies`, `triggers`, `contradicts` 等 8 种关系类型 |
| **Quality self-score** | 每轮 ingest 后四维自评：实体精度、关系覆盖、数据保留、矛盾处理 |

### PRD — 产品专家对话 (Ask-Plan-Execute)

| Phase | 内容 | Gate |
|-------|------|------|
| 1. Research | 4 轮对话：开放提问 → wiki 搜索 → 专家挑战 → 缺口分析 | 等待确认 |
| 2. Template | 自动检测 + 确认 PRD 类型 | 等待确认 |
| 3. Generate | 生成 `prd/{name}/v1/prd.md` + changelog | — |
| 4. Crystallize | PRD 关键决策回流 wiki，知识库闭环 | — |
| N. Revise | 版本管理：V1.0 → V1.1 / V2.0 | — |

## 依赖

零外部依赖。仅使用 agent 原生能力：Read、Write、Grep、rg、question。

## 打包

```bash
./package.sh  # → dist/pm-skill-YYYYMMDD.zip
```

## 参考

- [LLM Wiki v2 (rohitg00)](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) — 知识生命周期、置信度评分、结晶化
- [LLM Wiki (karpathy)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — 原始方法论
- [agentmemory](https://github.com/rohitg00/agentmemory) — 持久记忆引擎
