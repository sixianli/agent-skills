---
name: engineering-workflow
description: "为明确的工程请求选择必要的解释、调查、审查、设计、实施或复盘方法；简单任务直接完成，不默认多代理、长期模式或自动交付。"
---

# engineering-workflow

先识别用户要的结果和停止点：解释、调查、审查、设计、实施、复盘或偏好整理。简单问题与明确小修改直接完成，不为了入口存在而加载多个技能；闲聊和普通文字重述不使用工程流程。

## 选择必要方法

| 任务 | 读取条件与方法 |
|---|---|
| 当前代码机制 | 需要调查时使用 [how](../how/SKILL.md)；已有证据足够就直接解释 |
| 设计动机与历史 | 使用 [why](../why/SKILL.md)，保留未知与竞争解释 |
| 学习理解 | 使用 [teach](../teach/SKILL.md)，不默认重新运行 how/why 全调查 |
| diff 影响或安全前提 | 使用 [blast-radius](../blast-radius/SKILL.md)，默认只读 |
| 代码/注释审查 | 使用 [interrogate](../interrogate/SKILL.md)，不自动修复 |
| 结构与接口设计 | 真正需要取舍时使用 [architect](../architect/SKILL.md)；设计请求完成后停止 |
| 复杂实施 | 多阶段依赖需要组织时使用 [figure-it-out](../figure-it-out/SKILL.md)，保持原始完成条件 |
| 回归验证 | 明确 TDD 或有效测试目标时使用 [tdd](../tdd/SKILL.md) |
| TypeScript 契约 | 任务涉及类型状态/边界问题时使用 [typescript-best-practices](../typescript-best-practices/SKILL.md) |
| 项目验证能力 | 要生成验证技能时使用 [create-verification-skill](../create-verification-skill/SKILL.md)；维护已有产物用 [maintain-verification-skill](../maintain-verification-skill/SKILL.md) |
| 决策过程 | 复杂工作确需审阅轨迹时使用 [show-me-your-work](../show-me-your-work/SKILL.md) |
| 技术材料 | 按用途使用 [technical-writing](../technical-writing/SKILL.md)，文案不授权对应外部动作 |
| 当前任务复盘 | 仅用户要求复盘时使用 [reflect](../reflect/SKILL.md) |
| 跨会话偏好 | 仅用户指定材料并要求整理时使用 [automate-me](../automate-me/SKILL.md) |

跨技能链接标识 owner 和资源：先按名称从当前宿主技能清单取得实际路径，再读取指定文件；不假定技能相邻，不因此执行 owner 的完整流程。缺失时报告受影响步骤，不能静默跳过后声称完整完成。

## 选择流程

只读调查需要多步时读 [调查](references/workflows/investigation.md)；获准缺陷修复读 [缺陷修复](references/workflows/bug-fix.md)；新增行为读 [功能](references/workflows/feature.md)；行为保持的结构变化读 [重构与调用者迁移](references/workflows/refactoring.md)。不能因跨函数或 diff 较大就触发架构评审。

围绕一个真实决策的隔离实验才读 [原型](references/workflows/prototype.md)；需可比较性能证据时读 [性能](references/workflows/performance.md)；既有 trace 或获准 live 诊断读 [取证](references/workflows/forensics.md)。原型写文件、测量启动进程和 live 注入可能有副作用，调查入口本身不授权这些动作。

工作流需要详细材料时，同样按名称发现 owner，仅读指定章节；假设复查、工具选择、上下文与阶段方法由 figure-it-out 的 [实施方法](../figure-it-out/references/execution-methods.md) 维护；设计取舍由 architect 的 [设计审查](../architect/references/design-review.md) 维护。不要递归调用本入口，也不要预加载全部方法。

默认主 agent 执行；只有明确独立收益值得额外总 token 与核实成本、且宿主允许时才委派。保持写入归属，真实共享应用由单一操作者控制。技能调用不是子代理创建，也不创建用户侧独立任务。

交付与用户目标相符的结果、证据和实际限制。用户明确不执行某类验收时记录未验证，不暗中扩大测试；不能把未验证改写为通过。入口不建立持久 mode、定时任务、自动 PR 或外部消息流程。
