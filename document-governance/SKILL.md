---
name: document-governance
description: "治理已采用本体系的仓库中的 docs/：创建、协调一致、验证、替代、归档并关闭 PRD、Architecture、ADR、Spec、Plan、Runbook、Idea、Backlog 和 Tracking 记录。适用于明确的治理或文档产物请求、持久化 Idea 或未来 TODO、已跟踪工作的评审与状态转换，以及已采用本体系且公开行为或长期契约发生变化的仓库。不适用于未采用本体系的仓库中的普通修改、无持久化意图的随意头脑风暴、项目状态或工作恢复报告、仅修改措辞的 README 编辑、PR/commit/issue 文案或行内注释。遵循仓库既有约定。"
---

# 文档治理

治理项目文档，但不要将这套分类体系强加给无关仓库。当项目说明要求使用此工作流，
或者现有文档采用了本技能可识别的结构/frontmatter 时，将该仓库视为已采用本体系。
用户明确要求使用本技能时，也视为在所请求的范围内采用本体系。对于项目状态或工作恢复，
应检查最新的仓库、测试、产物和运行时证据，而不是创建手工维护的项目根目录状态缓存。

## 只加载所需内容

- 如需了解文档层次、frontmatter、命名、权威性、ADR 替代和 SOURCE 路径规则，
  请读取 `references/sop.md`。
- 如需了解创建、协调一致、关闭、回滚和冲突处理，请读取 `references/workflows.md`。
- 捕获、评审、推进、关闭或迁移 Idea 与 Backlog 条目时，请读取
  `references/idea-backlog-workflow.md`。
- 在解释或修改验证器之前，请读取 `references/validation-rules.md`。
- 创建文档时，从 `assets/templates/` 复制对应文件。
- 运行 `scripts/validate_docs.py` 验证项目。
- 运行 `scripts/tracking.py` 执行确定性的 Idea/Backlog 文件操作和一次性的
  Capture Idea 迁移。不要创建手工维护的索引。
- 仅使用 `scripts/archive_doc.py` 归档已关闭的 Spec 或 Plan。

## 必须遵循的工作流

1. 在治理 `docs/` 之前，要求仓库明确采用或已经采用本体系。
2. 检查用户限定的范围，以及 `AGENTS.md`、`CLAUDE.md` 和 `README.md` 等项目说明。
   如果这些说明与本技能不同，应遵循仓库约定。
3. 检查相关 diff、文件或现有文档；不要仅根据请求措辞推断文档影响。
4. 对工作进行分类，并且只读取与之匹配的参考资料章节。
5. 保持仅回答或仅评审的范围。获得编辑授权后，在同一个变更集中使受影响的代码和文档
   保持一致。
6. 在 `docs/adr/` 中原地替代 ADR；绝不归档 ADR。仅归档已完成关闭检查清单的
   Spec 和 Plan。
7. 根据技能清单或运行框架提供的源路径，解析当前已启用技能所在的目录。不要假定
   `CODEX_SKILL_DIR` 存在。运行随技能提供的脚本之前，确认可通过 `python3` 使用
   Python 3.10 或更高版本，然后使用解析得到的绝对路径调用脚本。
8. 对首次采用本体系的审计使用便于迁移的验证模式。对受治理的项目、CI 和完成情况检查
   使用 `--strict`；在宣称结构验证通过之前，解决所有错误。
9. 报告已更新和有意保持不变的文档、跳过的检查、尚未解决的漂移，以及任何必要的
   ADR 后续工作。

## 不可妥协的规则

- 保持 `policy.allow_implicit_invocation: true`，同时遵守本文件中的采用条件和范围边界。
- 不要悄悄重写 ADR 中已经记录的决策、背景、选项或后果。遵循
  `references/workflows.md` 中的替代工作流。
- 将已被替代的 ADR 保留在 `docs/adr/` 中，保持生命周期字段一致，并维护双向的
  `supersedes` / `superseded_by` 链接。
- 将 Tracking Ledger 用作来源追踪和状态记录，而不是当前产品事实或实施计划。
- 将需要持久保存的 Idea 存放在 `docs/tracking/ideas/` 下，将未来工作存放在
  `docs/tracking/backlog/` 下。不要重新创建 `docs/ideas/` 或 `INDEX.md`。
- 将 Backlog 作为持久的工作清单。不要仅仅为了证明临时状态报告合理，就虚构
  Backlog 条目。
- 不要创建或维护单独的项目根目录状态缓存。应根据当前的仓库、文档、测试、产物和
  运行时证据得出状态。
- 将本地 SOURCE 引用限制在目标项目的 `docs/` 树内。
- 如果代码被回滚，应在同一个变更集中修正相关的、反映当前事实的文档。
