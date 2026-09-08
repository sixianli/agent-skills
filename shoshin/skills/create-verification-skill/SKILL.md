---
name: create-verification-skill
description: "为指定真实项目生成并实跑本地验证技能和功能地图，覆盖启动、诊断、用户操作、取证及清理；未实跑的产物只能称草稿。"
---

# create-verification-skill

输入为获准目标项目、要验证的用户路径和现有操作能力。输出位于目标项目 `.agents/skills/verify-<app>/`，不能生成到通用 Shoshin 源码。使用当前发现的 skill-creator 进行编写与验证；缺失时说明能力缺口，不假装执行过它。

1. 从代码和现有文档确认入口、固定版本、启动命令、就绪信号、数据/账号要求、操作工具、可观测结果及隔离方式。优先现有控制能力；缺少项目范围或真实操作权限时只问必需信息，继续不依赖它的调查。
2. 记录本次自有实例、端口和数据目录；自有启动/清理必须可重复检查。已有用户实例不因生成技能而可被重启。共享实例只能由单一操作者控制。
3. 生成 SKILL.md 的 Launch、Doctor、Drive、Evidence、Cleanup、Helpers：写入核实的具体命令、选择器/路由和成功条件，不留下示例命令。短生命周期 CLI 每次新会话先 Doctor；持续实例依其 Launch 合同诊断。
4. 从实际路由、菜单或命令列出用户功能，生成 features/README.md 和功能文件。地图记录实际覆盖范围，每项有前提、操作和成功结果，不能把只验证一个入口称为整个产品通过。组织方式见 [功能地图示例](references/feature-map-example/README.md)。
5. 实跑 Launch → Doctor → 一项真实 Drive → Evidence → Cleanup，随后检查证据仍存在。每次失败迭代也清理自有资源，保留失败证据；不能按进程名批量杀进程，不删用户数据。
6. 失败或意外状态后先重新诊断；健康进程仍有弹窗或错误页面时恢复已知状态，再继续 Drive。不能安全恢复时停止相关操作，记录阻塞。生成过程中发现产品缺陷，只有原请求包含修复才在范围内处理，否则报告。

证据设计与 dry-run 副作用判断读 [证据标准](references/evidence-standards.md)；用户需要视觉比较时读 [视觉比较](references/visual-parity.md)。涉及复杂的重复与中断语义时，通过 architect 的发现路径仅读取 [重复与中断](../architect/references/design-review.md#重复与中断)。跨技能链接标识 owner 和资源：先按名称从当前宿主技能清单取得实际路径，再读取指定文件；不假定技能相邻，不因此执行 owner 的完整流程。缺失时报告受影响步骤，不能静默跳过后声称完整完成。

实际操作缺失、环境无法启动或账号不足时，交付草稿/阻塞原因和未覆盖功能，不宣称验证技能可用。交付经过验证的启动、操作及清理证据后，说明可用 maintain-verification-skill 按需维护，不安排自动任务。
