# document-governance 独立正向试验记录

这是独立子代理行为试验，属于 skill-creator 要求的 independent forward-testing；不是新 Codex 用户会话验收。使用指定候选技能，未修改技能源码或安装配置，未调用模型 API。

## 输入与执行范围

从 `cases.json` 读取 `docs` 请求。将已有确认作为当前约束：Workspace 是拥有文档的组织空间，退出成员的文档仍归 Workspace，不改变 ADR 0001。用户授权边访谈边记录，只澄清权限与格式，不写代码、不建实施计划。读取项目 AGENTS.md，确认其明确采用 Document Governance。

读取候选技能的 SKILL.md、discovery-workflow.md、sop.md、validation-rules.md。按 discovery-workflow 的事实调查要求，派发有界只读子代理核查导出权限，本代理同时记录术语与运行校验。没有要求重新确认已确认术语，也没有自行回答产品问题。

## 实际文件变化

只修改试验项目的 `docs/glossary.md`。备份保存在 `/private/tmp/dg-integration-trials/docs-before/`，试验报告位于项目目录外。

```diff
-A group of people who own documents together.
+An organizational space that owns documents, distinct from the individual members who participate in it. Documents remain owned by the Workspace when a member leaves.
+
+[SOURCE: docs/adr/0001-retain-documents.md#decision]
```

字节比较确认 `model.py`、`docs/prd-v0.1.md` 和 `docs/adr/0001-retain-documents.md` 未变。没有新增 Spec、Plan、Idea、Backlog、索引或实现文件。此目录不是 Git 仓库，因此未提交；`git status --short` 返回 128 和 not a git repository，随后改用备份差异和字节比较核验。

## 运行检查

- `python3 --version`：Python 3.11.2。
- `python3 /Users/triggerjames/Documents/sxl_code_work_space/agent-skills/document-governance/scripts/validate_docs.py /private/tmp/dg-integration-trials/docs --strict --format=json`：退出码 0，`ok: true`，errors 0，warnings 0。
- 实际统一差异仅包含上述术语及 SOURCE 更新。
- 静态核查 `may_export(role)` 返回 `role == "admin"`。未执行产品代码或真实服务权限检查；未发现调用入口及测试。

## 给用户的完整回复

已把上一轮确认的 Workspace 定义写入 [docs/glossary.md](/private/tmp/dg-integration-trials/docs/docs/glossary.md:11)：它是拥有文档的组织空间，成员退出后，文档仍归该 Workspace；定义同时引用 ADR 0001 的既有决定。ADR 0001、代码和 PRD 均保持原样，没有建立实施计划。严格文档校验已通过，错误和警告均为 0。

独立只读核查确认，[model.py](/private/tmp/dg-integration-trials/docs/model.py:1) 中的 `may_export(role)` 只在角色为 `admin` 时返回允许；[PRD](/private/tmp/dg-integration-trials/docs/docs/prd-v0.1.md:11) 仍将导出政策标为未确定。这只是现有函数的静态证据：项目中未发现调用入口，不能据此证明真实系统已执行该限制，也不能把它当成你已认可的产品决定。ADR 0001 中的“保留访问权”也不自动等于“拥有导出权”。

❓ Q1 — 导出权限：谁可以导出 Workspace 的文档？可以仅允许管理员，也可以允许成员导出自己有权查看的文档；如果希望区分单篇导出与整个 Workspace 批量导出，也请说明。
➡️ 建议：首版仅允许管理员导出，沿用现有函数表达的边界，减少权限规则的分叉。代价是普通成员需要管理员协助获取副本。这是待你决定的建议，尚未写成产品规则。

---

❓ Q2 — 导出格式：导出主要用于继续编辑、迁移备份，还是阅读分享？可选 Markdown 加附件打包、包含结构信息的 JSON，或便于阅读的 PDF；也可以明确需要同时支持哪些格式。
➡️ 建议：若首要目标是把文档带走后继续使用，先选 Markdown 加附件打包，便于阅读和编辑。代价是它未必保留原系统中的全部结构信息；若主要用于完整恢复或正式分享，则应分别优先考虑 JSON 或 PDF。

请一起回答 Q1 和 Q2；下一步会记录你的决定，再澄清依赖这些答案的细节。

## 停止点

等待用户回答同一轮的 Q1 导出权限与 Q2 导出格式。未模拟答案，没有在这两个尚未确认的决定上继续写入文档。术语增量记录与校验已在提问前完成。


# 续测第一轮：已接受决定的 ADR 替代

输入：我们已评审并接受一个新的长期决定：成员离开后，删除其个人上传的文档；不再沿用全部留在 Workspace 的决定。原因是此试验产品的个人数据删除承诺优先于其他成员继续访问的便利；我们明确比较过保留与删除。请只记录这个已接受的新决定和对应的产品文档，按治理规则处理旧 ADR，代码仍不改。

## 实际动作与边界

重新读取最新候选 SKILL.md、discovery-workflow.md、workflows.md、sop.md、validation-rules.md 和 ADR 模板，以及试验项目当前 AGENTS.md、ADR、术语表、PRD。新输入明确覆盖上一轮的永久保留规则，已给出评审和接受，不要求重复确认。先以模板创建 active/accepted ADR 0002，再变更旧 ADR 生命周期元数据；同步 PRD 与已冲突的术语说明。未新增 Architecture，因为没有已实现的新行为；未进入实施计划或实现。

## 实际文件差异

完整差异另存 `/private/tmp/dg-integration-trials/docs-round1.diff`。第一轮前项目快照位于 `/private/tmp/dg-integration-trials/docs-round1-before/`。

```diff
--- docs/adr/0001-retain-documents.md (before)
+++ docs/adr/0001-retain-documents.md (after)
@@ -1,10 +1,10 @@
 ---
-status: active
+status: superseded
 document_type: adr
 supersedes: ""
-superseded_by: ""
+superseded_by: docs/adr/0002-delete-personal-uploads.md
 date: "2026-09-21"
-decision_status: accepted
+decision_status: superseded
 ---

 # ADR 0001: Retain documents when members leave
--- docs/adr/0002-delete-personal-uploads.md (before)
+++ docs/adr/0002-delete-personal-uploads.md (after)
@@ -0,0 +1,42 @@
+---
+status: active
+document_type: adr
+decision_status: accepted
+supersedes: docs/adr/0001-retain-documents.md
+superseded_by: ""
+date: "2026-09-21"
+---
+
+# ADR 0002: Delete personal uploads when members leave
+
+## Context
+
+The product promises deletion of personal data. The reviewed decision gives this promise priority over the convenience of continued access for other members. This changes the durable retention policy recorded in ADR 0001; retention and deletion were explicitly compared.
+
+## Decision
+
+When a member leaves, delete the documents personally uploaded by that member. This accepted decision replaces the previous decision to retain all documents in the Workspace. It records the intended product policy; implementation and execution of deletion are outside this documentation-only change.
+
+## Options Considered
+
+### Retain personal uploads in the Workspace
+
+- Benefits: Other members keep access to the documents.
+- Costs: Conflicts with the personal data deletion promise that the product prioritizes.
+
+### Delete the departing member's personal uploads
+
+- Benefits: Honors the prioritized personal data deletion promise.
+- Costs: Other members lose access to the deleted documents.
+
+## Consequences
+
+- Positive: The agreed policy gives priority to the personal data deletion promise.
+- Negative: Continued access to deleted personal uploads is no longer guaranteed for remaining members.
+- Follow-up: The PRD records the accepted requirement. No implementation plan or code change is authorized by this record.
+
+## Links
+
+- [SOURCE: docs/adr/0001-retain-documents.md]
+- [SOURCE: docs/prd-v0.1.md#member-departure]
+
--- docs/glossary.md (before)
+++ docs/glossary.md (after)
@@ -10,6 +10,6 @@

 ## Workspace

-An organizational space that owns documents, distinct from the individual members who participate in it. Documents remain owned by the Workspace when a member leaves.
+An organizational space that owns documents, distinct from the individual members who participate in it. Ownership by a Workspace does not imply that documents must be retained after a member leaves; the member-departure rule is defined in the PRD.

-[SOURCE: docs/adr/0001-retain-documents.md#decision]
+[SOURCE: docs/prd-v0.1.md#member-departure]
--- docs/prd-v0.1.md (before)
+++ docs/prd-v0.1.md (after)
@@ -9,3 +9,11 @@
 # Team knowledge base

 Documents belong to one workspace. Export policy is undecided.
+
+## Member departure
+
+Accepted product requirement: when a member leaves, delete the documents personally uploaded by that member. The product prioritizes its personal data deletion promise over other members' continued access to those documents.
+
+This replaces the previous blanket retention rule. This document records intended behavior, not evidence that deletion has been implemented or performed. This documentation-only change does not define additional deletion scope or operational details.
+
+[SOURCE: docs/adr/0002-delete-personal-uploads.md#decision]
```

旧 ADR 正文保留检查：按 frontmatter 结束分隔符提取其后全部文本，前后完全相等（True）。旧 ADR 仍在 `docs/adr/0001-retain-documents.md`，未归档。`model.py` 字节比较 True，未改代码。

## 实际校验

`python3 --version`：3.11.2。

`python3 /Users/triggerjames/Documents/sxl_code_work_space/agent-skills/document-governance/scripts/validate_docs.py /private/tmp/dg-integration-trials/docs --strict --format=json`：退出码 0，`ok: true`，errors 0，warnings 0。没有运行产品行为测试或真实删除操作，这次只验证文档结构、链接及历史保留。

## 第一轮完整回复

已记录这项已评审并接受的新决定，并完成相关产品文档更新。

- 新增 [ADR 0002](/private/tmp/dg-integration-trials/docs/docs/adr/0002-delete-personal-uploads.md)，标记为 `accepted`：成员离开后删除其个人上传文档，优先履行个人数据删除承诺。记录了保留与删除的备选方案，以及剩余成员失去这些文档访问权的代价。
- [ADR 0001](/private/tmp/dg-integration-trials/docs/docs/adr/0001-retain-documents.md) 留在原目录，标为 `superseded`，与 ADR 0002 建立双向替代关系。字节比较确认旧 ADR 的标题和全部历史正文保持原样，只修改生命周期元数据。
- [PRD](/private/tmp/dg-integration-trials/docs/docs/prd-v0.1.md) 增加成员离开后的产品规则，明确这是已接受的目标行为，不能作为代码已实现或删除已执行的证据。
- [术语表](/private/tmp/dg-integration-trials/docs/docs/glossary.md) 保留“Workspace 是拥有文档的组织空间”的含义，移除与新决定冲突的永久保留承诺，转而引用 PRD 中的规则。

严格文档校验通过：错误 0、警告 0；替代关系与 SOURCE 引用检查通过。代码未变，也没有执行任何文档删除、建立实施计划或编写实现。导出权限和格式仍未决定；本轮文档记录任务已完成。

# 续测第二轮：停止写入，只讨论格式

独立输入：先停止写文档。关于导出格式，我想再比较 Markdown 和 PDF，请只讨论，不修改任何文件。

## 实际动作与检查

按后续只读指令停止项目写入。仅生成比较说明及一个聚焦首要用途的问题，等待回答；没有写入格式决定，没有重新提出导出权限等不在本轮范围的问题。问题是比较后的下一项决定，没有假装用户已接受建议。

本轮前后对项目内全部 6 个文件生成 SHA-256 映射，包含路径集合检查，结果完全一致（True），未增加、删除或修改项目文件。前快照位于 `/private/tmp/dg-integration-trials/docs-round2-before.json`。本轮不运行纯访谈不需要的文档验证；第一轮严格验证结果仍适用于字节完全不变的文档。

项目外的本报告追加及试验清单属于调用方明确要求的试验记录，不是第二轮访谈的产品文档写入。

## 第二轮完整回复

已停止文档写入，这一轮只比较 Markdown 和 PDF。

| 你希望导出后做什么 | Markdown | PDF |
| --- | --- | --- |
| 继续编辑文字 | 纯文本形式便于继续修改，但具体排版会受编辑器影响 | 主要用于成品阅读，重新编辑通常更费力 |
| 给别人阅读或打印 | 接收者可能需要支持 Markdown 的工具才能看到格式 | 页面排版相对固定，适合阅读、打印和正式分享 |
| 搬到另一套知识库 | 文字和标题较便于转换；附件、内部链接仍需要额外处理 | 页面内容可阅读，但不适合直接恢复成可编辑的知识库结构 |

两者都不能单靠文件格式完整保留成员权限、评论和版本历史；是否需要这些内容，是导出范围的另一个决定。

❓ Q1 — 首要用途：这次导出最想满足“带走后继续编辑或迁移”，还是“得到方便分享、打印的固定版面”？如果两个用途都必须满足，也请说明。
➡️ 建议：延续知识库文档可继续使用的目标时，优先 Markdown；代价是版式不固定，而且附件和链接需要配套处理。如果你的优先目标是直接交付给人阅读，则优先 PDF，代价是后续修改和结构恢复更困难。

先确定这个用途，下一轮再讨论由它决定的附件、链接或页面呈现细节。我不会把建议当成已确认的格式选择。

## 续测完成边界

第一轮文档任务完成；第二轮停在等待用户回答首要用途，没有模拟回答。以上仍是独立子代理试验，不是新 Codex 用户会话验收；未修改源技能、安装配置或其他项目，未调用模型 API。

Display-only diff excerpts normalize whitespace-only context lines. The exact ADR diff is retained in `docs-round1.json`; original trial output remains in its recorded temporary path.
