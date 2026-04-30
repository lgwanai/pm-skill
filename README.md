# PM Skill

Product Manager Knowledge Assistant — 产品经理知识助手。

将产品文档编译为结构化 wiki，并通过多轮专家对话生成专业 PRD。

## 命令

| 命令 | 用途 |
|------|------|
| `/wiki <path>` | 将文档编译为结构化 wiki（entities/ + concepts/ + index.md + glossary.md） |
| `/prd <description>` | 多轮对话生成 PRD，含研究、冲突检测、版本管理 |
| `/prd revise <name> <change>` | 修订已有 PRD，创建新版本 |

## 结构

```
pm-skill/
├── SKILL.md              # 指令定义
├── references/
│   ├── prompts/          # 提示词模板
│   └── templates/        # PRD 模板
└── wiki/                 # 编译后的知识库
    ├── entities/
    └── concepts/
```

## 依赖

零外部依赖。仅使用 agent 原生能力（Read、Write、Grep、rg、question 等）。
