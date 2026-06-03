# PLAN.md — 可执行阶段计划

> 本文档是阶段的执行蓝图。**BLOCKING gate**: 必须经用户确认后才能执行。

---

```yaml
---
phase: {N}
plan: {MM}
phase_name: "{phase-name}"
phase_type: "{discovery|strategy|prd|execution|release}"
wave: {1|2|3}
depends_on: [{dependency-plan-ids}]
must_haves:
  truths:
    - "{可观察的产品事实 — 验证方式}"
  artifacts:
    - "{文件路径 — 必须存在且实质化}"
  key_links:
    - "{交叉引用模式 — grep 可验证}"
user_setup: []
---
```

---

```xml
<plan>
<objective>{该计划要达成的单一目标}</objective>

<context>
{从 PROJECT.md、前置 SUMMARY.md 和讨论中提取的关键上下文}
</context>

<tasks>

<task id="{N}.{MM}.1" type="auto">
<description>{具体、可执行的任务描述}</description>
<read_first>{开始前必须读取的文件，逗号分隔}</read_first>
<acceptance_criteria>
- {可 grep 验证的完成条件 1}
- {可 grep 验证的完成条件 2}
</acceptance_criteria>
<produces>{产出的文件路径，逗号分隔}</produces>
</task>

<task id="{N}.{MM}.2" type="auto">
<description>{具体、可执行的任务描述}</description>
<read_first>{文件列表}</read_first>
<acceptance_criteria>
- {条件 1}
- {条件 2}
</acceptance_criteria>
<produces>{文件路径}</produces>
</task>

</tasks>

<dependencies>
- {MM}-PLAN.md: depends_on [{deps}], files_modified [{files}]
</dependencies>

<verification>
{执行后如何验证计划成功的说明}
</verification>
</plan>
```

---

## Must_Haves 设计指南

### truths（产品真相 — 可观察的行为/事实）
定义该计划完成后，从产品视角可观察到的事实。
- ✅ 好: "竞品分析涵盖 5 家直接竞品，每家包含定价、功能、GTM 策略"
- ❌ 差: "竞品分析完成"

### artifacts（产物 — 必须存在的文件）
定义必须存在的具体文件。
- ✅ 好: "prd/auth-system/v1/prd.md — 存在且 ≥ 100 行，无占位符"
- ❌ 差: "PRD 文档完成"

### key_links（关键关联 — 产物间的交叉引用）
定义产物间可 grep 验证的关联模式。
- ✅ 好: "PRD.md 引用 RESEARCH.md 中的用户画像数据"
- ❌ 差: "文档之间有关联"

---

## 任务设计原则

1. **纵向优先**: 每个任务产出完整的端到端交付物，不分层
2. **可验证**: 每个验收标准能用 grep 在 5 秒内验证
3. **上下文友好**: <read_first> 只列真正需要读取的文件（不要引用整个代码库）
4. **大小适中**: 2-3 个任务/计划，约 50% 上下文上限

---

## Wave 分配

- **Wave 1**: 独立任务，无前后依赖，可并行
- **Wave 2**: 依赖 Wave 1 的产物
- **Wave 3**: 依赖 Wave 1+2

同一 Wave 内的任务可安全并行执行。

---

## 更新指南

- 计划获批后修改 → 标记变更 → 重新确认
- 执行中发现问题 → 记录到 SUMMARY.md 的 deviations
- 验证失败 → 更新 PLAN.md 并重新执行
