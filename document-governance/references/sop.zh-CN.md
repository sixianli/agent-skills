# 文档治理 SOP

使用本参考文档来规范文档层级、生命周期字段、命名、权威性顺序、
ADR 替代机制以及 SOURCE 路径规则。

## 目录

- [核心原则](#核心原则)
- [文档层级](#文档层级)
- [Frontmatter 与生命周期](#frontmatter-与生命周期)
- [跨文档引用](#跨文档引用)
- [ADR 规则](#adr-规则)
- [权威性顺序](#权威性顺序)
- [命名与目录](#命名与目录)

## 核心原则

1. 每一项事实只保存在一个权威位置中。
2. 保持代码与描述当前事实的文档一致。
3. 将稳定事实与临时执行产物分离。
4. 将设计与实现顺序分离。
5. 将已关闭的 Spec 和 Plan 归档；ADR 的决策历史则原地保留。
6. 优先遵循用户限定的范围和仓库指令，其优先级高于这套默认分类体系。

## 文档层级


| 层级          | 默认位置                                          | 回答的问题                         | 不得包含                         |
| ------------- | ------------------------------------------------- | ---------------------------------- | -------------------------------- |
| PRD           | `docs/prd-v*.md`                                  | 要构建什么，以及为什么要构建       | API、类、Schema、文件级实施步骤 |
| Architecture  | `docs/architecture-v*.md`                         | 当前系统的整体架构是什么样的       | 任务检查清单、被否决的备选方案  |
| ADR           | `docs/adr/NNNN-title.md`                          | 为什么做出了某项长期有效的决策     | 当前实现清单                    |
| Spec          | `docs/execution/specs/YYYY-MM-DD-topic-design.md` | 某一项变更的详细设计               | 文件级实现步骤                  |
| Plan          | `docs/execution/plans/YYYY-MM-DD-topic-plan.md`   | 实现顺序与验证方式                 | 新需求或新的设计决策            |
| Runbook       | `docs/runbooks/topic-runbook.md`                  | 如何运行、部署、调试和恢复         | 产品需求或功能设计理由          |
| Idea          | `docs/ideas/IDEA-*.md`                            | 一项值得长期保留的洞见及其思考背景 | 对实现该想法的承诺              |
| Backlog Item  | `docs/backlog/BL-*.md`                            | 未来工作、优先级、状态和预期结果   | 文件级执行步骤                  |
| Codex Lessons | `docs/lessons.md`                                 | Codex 反复犯的错误与防复发规则         | 项目状态、一次性问题、未来工作 |
| Archive       | `docs/archive/specs/`、`docs/archive/plans/`      | 已关闭的执行历史                   | 当前生效的权威事实内容          |

不要创建或维护 `docs/TODO.md`；Backlog 是唯一持久的未来工作清单。
`docs/lessons.md` 只用于记录 Codex 经常或反复犯的错误，以及防止
同类错误再次发生的明确规则。不要写入项目状态、普通知识、一次性问题
或未来工作。

出于向后兼容目的，应识别现有的 `docs/archive/adr/` 文档，但不要再把新的
ADR 或已被替代的 ADR 移动到该目录中。

## Frontmatter 与生命周期

每一份受治理的文档，包括已经归档的文档，都必须以单行值形式的
frontmatter 开头。不要使用嵌套映射、数组、重复键或多行值。

必填字段：

```yaml
---
status: active          # active | superseded | archived
supersedes: ""          # 仓库相对路径，或以逗号分隔的多个路径
superseded_by: ""       # 仓库相对路径，或以逗号分隔的多个路径
date: "YYYY-MM-DD"
---
```

文档类型专属字段：

```yaml
document_type: spec        # prd | architecture | adr | spec | plan | runbook | idea | backlog | lessons
version: "X.Y"             # 仅用于 PRD/Architecture
decision_status: accepted  # 仅用于 ADR：proposed | accepted | superseded
record_id: IDEA-YYYYMMDD-NNN
record_state: captured      # 状态集合取决于 document_type
updated: "YYYY-MM-DD"       # 仅用于结构化 Idea/Backlog
```

应一致地使用生命周期字段：

- `active`：当前事实，或仍处于开放状态的执行工作。
- `superseded`：原地保留，但已由明确指定的后继文档取代。
- `archived`：已关闭并移动到 `docs/archive/` 下的 Spec 或 Plan。
- 对于已被替代的 ADR，同时设置 `status: superseded` 和
  `decision_status: superseded`，将其继续保留在 `docs/adr/` 中，并填写
  `superseded_by`。
- 对于用于替代旧 ADR 的新 ADR，设置 `status: active`，填写 `supersedes`，
  并先将其接受为正式决策，然后再把旧 ADR 标记为 superseded。

## 跨文档引用

使用可由机器校验的权威引用：

```text
[SOURCE: docs/path.md#optional-anchor]
```

规则：

- 本地目标必须位于项目的 `docs/` 目录树内部。
- 拒绝绝对路径，以及任何包含 `..` 的路径穿越。
- 对于不带 `docs/` 前缀的路径，只允许相对于 `docs/` 解析，绝不能相对于
  仓库根目录解析。
- 将 anchor 视为 kebab-case 格式的标题 slug；验证器不会验证 anchor 本身。
- 跳过外部 `http://` 和 `https://` 目标。
- 在完成路径边界校验后，跳过明确的模板占位符，例如 `NNNN`、`YYYY-MM-DD`
  和 `<topic>`。
- 普通正文可以使用一般的 Markdown 链接，但权威性的跨文档依赖必须使用 SOURCE。
- 通过 active-to-archive 兼容映射，保留指向已关闭 Spec 和 Plan 的链接。
  旧版 ADR 链接也应以类似方式保留，但今后不要再归档 ADR。

## ADR 规则

- 每个 ADR 只记录一项长期有效的决策。
- 不要重写 ADR 中已经记录的决策、背景、备选方案或后果。
  只允许修复拼写错误、格式问题、失效链接和跨文档引用，且这些修复不得改变
  历史决策本身。
- 当决策发生变化时，遵循 `references/workflows.md` 中的原地替代工作流；
  不要对 ADR 运行归档脚本。
- 保持 Architecture 与当前实际行为一致。ADR 用于解释决策理由；
  Architecture 用于描述当前系统。
- 实现清单和任务检查清单应放在 Architecture、Spec 或 Plan 中，而不是 ADR 中。

## 权威性顺序

发生冲突时，按以下顺序解决：

1. PRD：产品范围和业务规则。
2. Architecture：当前技术行为。
3. ADR：决策理由和权衡。
4. Spec：某项变更已经确认的设计。
5. Plan：执行顺序和验证方式。
6. Runbook：运行和故障排查。

当前仓库中的实际证据仍然非常重要：当代码与描述当前事实的文档发生冲突时，
应检查实际实现，并协调更新相应的权威文档，而不是盲目信任已经过时的文字说明。

## 命名与目录


| 类型          | 命名模式                                                       |
| ------------- | -------------------------------------------------------------- |
| PRD           | `prd-v{major.minor}.md`                                         |
| Architecture  | `architecture-v{major.minor}.md`                                |
| ADR           | `NNNN-short-title.md`                                           |
| Spec          | `YYYY-MM-DD-topic-design.md`                                    |
| Plan          | `YYYY-MM-DD-topic-plan.md`                                      |
| Runbook       | `topic-runbook.md`、`topic-setup.md`、`topic-troubleshooting.md` |
| Idea          | `docs/ideas/` 下的 `IDEA-YYYYMMDD-NNN-short-title.md`          |
| Backlog       | `docs/backlog/` 下的 `BL-YYYYMMDD-NNN-short-title.md`          |
| Codex Lessons | `docs/lessons.md`                                               |

```text
docs/
├── prd-v0.1.md
├── architecture-v0.1.md
├── adr/
├── execution/
│   ├── specs/
│   └── plans/
├── runbooks/
├── ideas/
├── backlog/
├── lessons.md
└── archive/
    ├── specs/
    └── plans/
```

`docs/execution/specs/` 和 `docs/execution/plans/` 中只保留待处理或正在执行的工作。
完成关闭检查清单后，将已经关闭的 Spec 和 Plan 移动到对应的归档目录。

不要手工维护 Idea 或 Backlog 索引。使用 `scripts/idea_backlog.py list` 或
`scripts/idea_backlog.py review` 查询带有 frontmatter 的源记录。
