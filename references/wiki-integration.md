# llm-wiki-skill 桥接指南

> 本文档定义 pm-skill 如何与 llm-wiki-skill 集成。
> pm-skill 不重新实现 wiki 功能，而是通过 Agent 调用 llm-wiki-skill 的能力。

---

## 检测机制

在需要 wiki 的工作流开始时，执行以下检测：

```bash
# 方法 1: 检查 .wiki/ 目录是否存在（最可靠）
ls .wiki/pages/ 2>/dev/null

# 方法 2: 检查 wiki CLI
which wiki 2>/dev/null || python3 -c "import scripts.wiki" 2>/dev/null

# 方法 3: 检查 llm-wiki skill 是否已注册
# （通过 SKILL.md 的 YAML frontmatter 检测）
```

## 安装提示

如未检测到 llm-wiki-skill：

```
⚠️ 此功能需要 llm-wiki-skill（专业级 wiki 知识库引擎）。

📦 安装方法：
   git clone https://github.com/lgwanai/pm-skill ~/.claude/skills/llm-wiki-skill
   cd ~/.claude/skills/llm-wiki-skill && pip install -e .

   安装后重新启动 Claude Code 即可自动加载 wiki 功能。

🔗 详情: https://github.com/lgwanai/pm-skill

---
当前操作将在没有 wiki 增强的情况下继续。
```

---

## llm-wiki-skill 命令速查

| 命令 | 功能 | PM 场景 |
|------|------|---------|
| `/wiki-compile <path>` | 摄入文档 → 提取实体/概念/关系 | 导入竞品报告、行业研究 |
| `/wiki-query <question>` | 搜索 + 综合回答 | PRD 研究、策略验证 |
| `/wiki-lint` | 健康检查 + 自动修复 | 定期维护 |
| `/wiki-status` | 显示 wiki 统计 | 了解知识库规模 |
| `/wiki-consolidate` | 记忆层级固化 | 定期知识整理 |
| `/wiki-init` | 初始化 wiki 目录 | 首次使用 |

CLI 等效命令：
```bash
wiki compile source.md     # 摄入文档
wiki query "问题"          # 搜索查询
wiki status               # 统计信息
wiki lint --auto-heal     # 健康检查
```

---

## PM 工作流中的集成点

### /pm-research 中的 wiki 集成

```
1. 研究开始前:
   wiki query "{研究主题} 竞品分析"
   wiki query "{研究主题} 市场规模"
   → 了解已有知识，避免重复研究

2. 研究完成后:
   wiki compile research.md
   → 将新发现结晶回知识库
```

### /pm-prd 中的 wiki 集成

```
1. PRD 研究阶段（Round 2 — Wiki 搜索）:
   rg "关键词" wiki/entities/ -l
   rg "关键词" wiki/concepts/ -l
   → 搜索已有实体和概念
   → 检测冲突、补充背景

2. PRD 生成后（Phase 4 — 结晶）:
   对每个新发现的实体/概念：
   - 写入 wiki/entities/{name}.md
   - 写入 wiki/concepts/{name}.md
   - 更新 wiki/index.md, wiki/glossary.md, wiki/log.md
```

### /pm-strategy 中的 wiki 集成

```
1. 策略制定前:
   wiki query "{产品} 竞品策略"
   → 搜索已有竞品情报

2. 策略决策后:
   wiki compile strategy.md
   → 策略结论结晶回知识库
```

---

## 知识生命周期（LLM Wiki v2）

| 层级 | 位置 | 内容 | 置信度 |
|------|------|------|--------|
| Working | 原始文档 | 未处理的源文件 | raw |
| Episodic | `wiki/entities/` | 从单个来源提取的事实 | source-count + recency |
| Semantic | `wiki/concepts/` | 跨来源的模式和原则 | 多来源强化 |

知识向上晋升：3+ 来源在 episodic 层 → 有资格进入 semantic 层。

---

## 最佳实践

1. **定期维护**: 每周运行 `wiki lint --auto-heal`
2. **知识结晶**: 每次研究/PRD 结束后将关键发现写入 wiki
3. **来源标注**: 所有 wiki 条目标注来源文档
4. **矛盾不隐藏**: 新旧信息冲突时标记 SUPERSEDED 链，不删除旧内容
5. **实体 vs 概念区分**: 具体事物 → entities，抽象思想 → concepts

---

## 更新指南

- llm-wiki-skill 升级后更新命令速查
- 新增 PM 工作流集成点 → 追加到本文档
- 中文输出
