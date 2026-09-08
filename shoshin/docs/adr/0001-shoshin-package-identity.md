---
status: active
document_type: adr
decision_status: accepted
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# ADR 0001：采用 Shoshin 名称及独立源码包位置

## Context

用户希望从 PStack 借鉴适合 Codex 的工程技能，名字不必严肃，但应有辨识度。讨论中曾使用 engineering-skills 作为暂定名称，也比较过 ducksmith、measure-twice 等候选。用户最终明确接受 Shoshin。

需要把源码维护位置与安装位置分开，防止维护过程中在多个副本分别修改，或把项目专用验证配置混入通用包。agent-skills 仓库 README 建议 *-skill 包名；本次遵循用户明确选定的 shoshin 目录，不改名为 shoshin-skill。

## Decision

采用 **Shoshin** 作为展示名、**shoshin** 作为包目录名，源代码包位于 `agent-skills/shoshin/`。

当前机器上的源码根是 `/Users/triggerjames/Documents/sxl_code_work_space/agent-skills/shoshin/`。该绝对路径只用于本机定位，不写进运行时技能的依赖或调用指令。

- 包的受治理文档根为 `shoshin/docs/`。对治理工具传入 `shoshin` 作为 project root，SOURCE 中的 `docs/` 相对这个根解析。
- 通用技能源码位于 `shoshin/skills/<skill-name>/`。
- 个人安装目标为 `~/.agents/skills/<skill-name>/`，安装副本不是独立维护来源。具体更新方式由实施前验证决定；不得覆盖同名用户技能。
- 项目专用验证技能生成到目标项目 `.agents/skills/verify-<app>/`，不进入 Shoshin 通用源码目录。
- 本次只建立文档，不创建运行时占位技能、不安装、不发布。详细目标树属于 Spec，不把将来目录当成当前实现。

## Options Considered

### Shoshin 独立源码包

短而稳定，表达保持好奇、愿意检查假设的态度；用户已明确接受。源码和文档集中，可独立验证和安装。

### 沿用 engineering-skills

用途直白，但只是早期临时名字，不符合用户最终选择。

### 沿用 PStack 名称并整体复制

容易与上游和既有迁移项目混淆，并暗示保留原版完整编排能力，不符合已确认范围。

## Consequences

- 后续文档、目录和安装说明统一使用 Shoshin/shoshin。
- 不因新增技能、修改安装形式而另建重复维护目录。
- 保留上游 MIT 归属与来源记录，不冒充完整原版或跨宿主行为等价版本。
- 本 ADR 记录命名与位置这一项持久决定。要修改该决定时创建后继 ADR，不改写本条历史。
- 当前没有技能实现，不创建声称描述当前运行系统的 Architecture 文档。实现后按真实结构补充。

## Links

- [SOURCE: docs/prd-v0.1.md]
- [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]
