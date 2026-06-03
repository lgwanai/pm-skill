---
name: pm-research
description: "执行市场/用户/竞品研究。通过 Web 搜索 + wiki 查询 + 综合，生成结构化研究报告。"
argument-hint: "<topic or file>"
---

# /pm-research — 产品研究

触发 `pm-skill`，执行产品研究并生成结构化报告。

## 工作流

1. **定义研究问题** — 参考 `workflows/research.md`：
   - 用户想研究什么？（竞品、市场、用户、技术趋势……）
   - 研究范围和深度？
   - 输出格式偏好？

2. **执行研究**：
   - **Web 搜索**：使用 WebSearch 搜索行业报告、竞品信息、市场数据
   - **Wiki 查询**（如有 llm-wiki-skill）：搜索已有知识库
   - **综合**：交叉验证来源，提炼关键发现

3. **生成报告** — 遵循 `templates/RESEARCH.md`：
   - 摘要
   - 研究对象和方法
   - 主要发现
   - 数据来源
   - 结论和建议

4. **（可选）结晶回 wiki** — 如 llm-wiki-skill 可用，将关键发现结晶

## 产出物

- `RESEARCH.md` — 研究报告（工作目录根下或 `.planning/phases/NN-name/`）

## 研究领域

参考 `references/domain/` 中的领域知识：
- **竞品分析**: `references/domain/market-research.md`
- **用户研究**: `references/domain/discovery-methods.md`
- **市场规模**: TAM/SAM/SOM 方法论
- **技术趋势**: Web 搜索 + 行业报告

## 关键规则

- 所有数据标注来源
- 区分数据（可验证）和洞察（推断）
- 中文输出
