# Requirements: PM Skill

**Defined:** 2026-04-27
**Core Value:** 让产品经理能够快速将各类文档转化为可查询的知识库，并基于知识库生成高质量、符合行业标准的 PRD 文档

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation

- [ ] **FND-01**: Skill 使用 create-skill 创建，遵循标准 Skill 架构（SKILL.md + scripts/ + references/）
- [ ] **FND-02**: 配置文件支持设置文档存放位置（raw/wiki/log 目录路径）
- [ ] **FND-03**: 目录结构自动初始化（raw/、wiki/、log/、index.db）

### Document Import

- [ ] **IMP-01**: 支持导入 PDF 文档并转换为 Markdown
- [ ] **IMP-02**: 支持导入 DOC/DOCX 文档并转换为 Markdown
- [ ] **IMP-03**: 支持导入 HTML 文档并转换为 Markdown
- [ ] **IMP-04**: 使用 markitdown 工具进行文档转换
- [ ] **IMP-05**: 转换后的 Markdown 文件存入 raw/ 目录
- [ ] **IMP-06**: 转换结果包含基本验证（表格语法、图片引用、格式完整性）

### Knowledge Compilation

- [ ] **CMP-01**: 支持将 raw/ 目录的文件编译为 wiki/ 知识库
- [ ] **CMP-02**: 为每个 raw 文件生成对应的 entity 页面（wiki/entities/）
- [ ] **CMP-03**: 自动提取概念并创建 concept 页面（wiki/concepts/）
- [ ] **CMP-04**: 维护 wiki/index.md 总索引
- [ ] **CMP-05**: 维护 wiki/glossary.md 术语表
- [ ] **CMP-06**: 在 log/ 目录记录编译变更日志
- [ ] **CMP-07**: 使用配置的大模型 API 进行编译
- [ ] **CMP-08**: 编译结果包含置信度标注（EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED）

### Knowledge Retrieval

- [ ] **RET-01**: 支持 CLI 关键词搜索（rg 命令封装）
- [ ] **RET-02**: 支持列出所有 Markdown 文件（find 命令封装）
- [ ] **RET-03**: 支持带上下文的搜索（显示3行上下文）
- [ ] **RET-04**: SQLite FTS5 全文索引用于快速检索

### PRD Writing

- [ ] **PRD-01**: 支持多轮对话收集用户需求信息
- [ ] **PRD-02**: 基于收集信息自动联想相关概念、功能、接口、数据项
- [ ] **PRD-03**: 使用联想结果作为关键词检索知识库
- [ ] **PRD-04**: 迭代检索：理解检索结果 → 提取新关键词 → 再次检索，直到无新内容
- [ ] **PRD-05**: 对比用户输入与知识库信息，检测冲突并确认
- [ ] **PRD-06**: 评估实现成本和风险（技术/业务/法律风险）
- [ ] **PRD-07**: 生成的 PRD 符合行业标准语法规范
- [ ] **PRD-08**: 支持 ToC 产品 PRD 模板（重体验、重流程、重异常、重数据埋点）
- [ ] **PRD-09**: 支持 ToB 产品 PRD 模板（重业务、重权限、重审批、重交付验收）
- [ ] **PRD-10**: 支持后台系统 PRD 模板（重列表、重权限、重操作日志、重效率）
- [ ] **PRD-11**: 支持小程序 PRD 模板（重场景、重平台规则、重授权、重性能）

### Competitive Analysis

- [ ] **ANA-01**: 支持竞品分析功能（基于知识库中的竞品文档）

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced PRD

- **PRD-12**: 自动生成数据埋点方案
- **PRD-13**: 接口数据结构建议
- **PRD-14**: 视觉 UI 规范集成

### Knowledge Enhancement

- **KNW-01**: 向量嵌入用于语义搜索
- **KNW-02**: 知识图谱可视化
- **KNW-03**: 多知识库管理

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| 实时协作编辑 | 高复杂性，CLI Skill 面向单用户，导出到共享文档即可 |
| Git 版本控制集成 | 增加依赖复杂性，手动 git 足够，简单日志文件追踪变更 |
| 移动端支持 | Web/Desktop 优先，移动端需要全新 UX 范式 |
| 复杂权限系统 | 单用户 CLI 工具，文件系统权限足够 |
| 富文本编辑器 | Markdown 是标准格式，任何编辑器都可使用 |
| AI 聊天界面 | CLI Skill 已提供 Claude 访问，无需额外界面 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 1: Foundation & Document Pipeline | Pending |
| FND-02 | Phase 1: Foundation & Document Pipeline | Pending |
| FND-03 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-01 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-02 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-03 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-04 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-05 | Phase 1: Foundation & Document Pipeline | Pending |
| IMP-06 | Phase 1: Foundation & Document Pipeline | Pending |
| CMP-01 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-02 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-03 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-04 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-05 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-06 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-07 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| CMP-08 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| RET-01 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| RET-02 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| RET-03 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| RET-04 | Phase 2: Knowledge Compilation & Retrieval | Pending |
| PRD-01 | Phase 3: PRD Generation | Pending |
| PRD-02 | Phase 3: PRD Generation | Pending |
| PRD-03 | Phase 3: PRD Generation | Pending |
| PRD-04 | Phase 3: PRD Generation | Pending |
| PRD-05 | Phase 3: PRD Generation | Pending |
| PRD-06 | Phase 3: PRD Generation | Pending |
| PRD-07 | Phase 3: PRD Generation | Pending |
| PRD-08 | Phase 3: PRD Generation | Pending |
| PRD-09 | Phase 3: PRD Generation | Pending |
| PRD-10 | Phase 3: PRD Generation | Pending |
| PRD-11 | Phase 3: PRD Generation | Pending |
| ANA-01 | Phase 4: Competitive Analysis | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-04-27*
*Last updated: 2026-04-27 after roadmap creation*