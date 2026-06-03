# 计划执行工作流

## 概述

执行已批准的计划文件中的任务。逐任务读取→实现→验证→提交。

改编自 spec-skill 的 `workflows/execute-plan.md`，适配 PM 工作场景。

## 前置条件

- PLAN.md 存在且已获用户批准
- 用户已确认"继续执行"
- 如 PLAN.md 有 `user_setup`，用户已完成外部配置
- 工作目录状态干净（或用户明确知晓变更）

## 执行步骤

### 步骤 0：执行前准备

1. 读取 `{NN-MM-PLAN}.md` 到上下文
2. 确认所有 `depends_on` 的依赖计划已完成
3. 确认 `user_setup` 中的项目已就绪（如 API 配置、外部账号等）
4. 确认工作目录状态

### 步骤 1：任务执行循环

对于 PLAN.md 中的每个 `<task>`：

```
FOR each task in wave order:
  1. READ FIRST — 读取 <read_first> 中列出的文件
  2. IMPLEMENT — 执行任务的具体操作
  3. VERIFY — 逐项检查 <acceptance_criteria>
  4. COMMIT — 如有 git repo，原子提交
```

**1. READ FIRST**
- 读取 `<read_first>` 中的所有文件
- PM 场景常见：读取研究文档、PRD 模板、参考框架

**2. IMPLEMENT**
- 使用 Write 工具创建/更新文档
- 使用 WebSearch/WebFetch 进行外部研究
- 使用 Grep 检查已有内容

**3. VERIFY**
- 逐项对照 `<acceptance_criteria>` 检查
- 如果验收标准不满足 → 修复 → 重新验证
- 最多重试 3 次

**4. COMMIT**（如有 git repo）
- 提交消息格式：`{phase}-{plan}: {task-description}`
- 结尾添加：`Co-Authored-By: Claude Code <noreply@anthropic.com>`
- 原子提交：一个任务 = 一个 commit

### 步骤 2：检查点处理

如果任务是 `type="checkpoint:human-verify"`：
1. 暂停执行
2. 展示当前结果和相关产物
3. 使用 `AskUserQuestion` 请求用户验证
4. 等待用户确认后继续

### 步骤 3：执行后处理

所有任务完成后：

1. **创建 SUMMARY.md** — 遵循 `templates/SUMMARY.md`：
   ```yaml
   ---
   phase: {N}
   plan: {MM}
   completed: "{date}"
   summary: "{一句话总结}"
   artifacts_created: ["{文件列表}"]
   decisions_made: ["{关键决策}"]
   deviations: ["{与计划的偏差}"]
   ---
   ```

2. **更新 STATE.md**：
   - 更新当前进度位置
   - 记录完成的任务
   - 添加新发现的关键信息
   - 保持 < 100 行

### 步骤 4：计划间切换

如果该阶段有多个计划（01-PLAN.md, 02-PLAN.md）：
- 完成 01 后，自动询问是否继续执行 02
- 如果是 Wave 1/2 关系：Wave 1 全部完成 → 再执行 Wave 2

## 错误恢复

**单个任务失败**（< 3 次）：
- 分析失败原因
- 修正方法
- 重新执行任务

**连续 3 次失败**：
- 记录问题到 STATE.md 的 Blockers 部分
- 创建 `.planning/.continue-here.md` checkpoint
- 向用户汇报并请求指导

**上下文溢出**：
- 完成当前任务并提交
- 创建 `.planning/.continue-here.md`：
  ```markdown
  # Continue Here
  **当前执行**: Phase {N}, Plan {MM}, Task {id}
  **状态**: {完成了哪些，还剩哪些}
  **下一步**: 继续 Task {next-id}
  ```
- 提示用户在新会话中运行 `/pm-next`

## 关键规则

- 不执行未批准的计划
- 每个任务独立验证 — 不批量跳过
- 原子提交，不合并任务
- 遇到检查点必须暂停
- 中文输出
