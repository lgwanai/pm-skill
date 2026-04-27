# PM Skill

## What This Is

一个产品经理日常工作辅助 Skill，使用 create-skill 创建。主要功能包括：
- 竞品分析
- PRD 编写
- 文档管理（LLM Wiki 方法）

该 Skill 帮助产品经理自动化处理文档、生成知识库、编写规范的 PRD，提升工作效率。

## Core Value

让产品经理能够快速将各类文档转化为可查询的知识库，并基于知识库生成高质量、符合行业标准的 PRD 文档。

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 创建 Skill 基础架构（使用 create-skill）
- [ ] 实现 LLM Wiki 文档管理功能
- [ ] 实现文档转换功能（PDF/DOC/HTML → Markdown）
- [ ] 实现知识库编译功能（raw → wiki）
- [ ] 实现 CLI 查询和管理功能
- [ ] 实现 PRD 编写能力（多轮对话收集信息）
- [ ] 实现知识库检索增强 PRD 功能
- [ ] 实现竞品分析功能

### Out of Scope

- 实时协作编辑 — 简化 MVP，暂不支持多人协作
- 版本控制集成 — 暂不与 Git 等版本控制系统深度集成
- 移动端支持 — Web/Desktop 优先

## Context

LLM Wiki 方法论来自 Karpathy 的 gist：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

PRD 编写需要遵循行业标准，包括：
- ToC 产品：重体验、重流程、重异常、重数据埋点
- ToB 产品：重业务、重权限、重审批、重交付验收
- 后台系统：重列表、重权限、重操作日志、重效率
- 小程序：重场景、重平台规则、重授权、重性能

## Constraints

- **Tech Stack**: 使用 create-skill 创建 Skill，需要遵循 Skill 架构规范
- **Dependencies**: markitdown 用于文档转换，大模型 API 用于编译知识库
- **Storage**: 文档存储在 raw/wiki/log 目录结构中

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 create-skill 创建 | 标准化 Skill 开发流程，便于维护和扩展 | — Pending |
| LLM Wiki 方法 | 结构化知识管理，便于检索和复用 | — Pending |
| 支持多种文档格式 | 覆盖常见文档类型，提升适用性 | — Pending |

---
*Last updated: 2026-04-27 after initialization*