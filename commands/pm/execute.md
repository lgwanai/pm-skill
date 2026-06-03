---
name: pm-execute
description: "执行阶段 N 的所有计划。逐任务实施→验证→原子提交，生成执行总结。"
argument-hint: "<phase-number>"
---

# /pm-execute — 执行阶段

触发 `pm-skill`，执行阶段 N 的已批准计划。

## 工作流

1. **执行前验证** — 参考 `workflows/execute-plan.md`：
   - 确认 PLAN.md 存在且已批准
   - 检查依赖阶段是否完成
   - 验证工作目录状态（干净或明确了解变更）
   - 如 PLAN.md 有 `user_setup`，确认用户已完成外部配置

2. **任务执行** — 按 PLAN.md 中的任务顺序（Wave 内可并行）：
   - **读优先** — 读取 `<read_first>` 中列出的文件
   - **实现** — 执行任务描述的具体操作（写文档、分析、汇总等）
   - **验证** — 对照 `<acceptance_criteria>` 逐项检查
   - **记录** — 如有 git 仓库，原子提交（一个任务 = 一个 commit）

3. **检查点处理** — 如遇 `checkpoint:human-verify`：
   - 暂停 → 展示当前结果 → 等待用户确认 → 继续

4. **执行后** — 所有任务完成后：
   - 创建 `NN-MM-SUMMARY.md`（遵循 `templates/SUMMARY.md`）
   - 更新 `STATE.md`（记录进度、决策、指标）

## 产出物

- `.planning/phases/NN-name/NN-MM-SUMMARY.md` — 执行总结
- 任务具体产出（研究报告、PRD 文档、策略画布等）
- 更新的 `STATE.md`

## 关键规则

- 只执行已批准的 PLAN.md — 不跳步
- 每个任务独立验证 — 不要批量跳过验收标准
- 错误处理：连续 3 次失败 → 记录问题 → 创建检查点 → 咨询用户
- 上下文溢出：完成当前任务 → 提交 → 创建 `.continue-here.md`
- 中文输出
