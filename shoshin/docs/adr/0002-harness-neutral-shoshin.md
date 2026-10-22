---
status: active
document_type: adr
decision_status: accepted
supersedes: docs/adr/0001-shoshin-package-identity.md
superseded_by: ""
date: "2026-10-22"
---

# ADR 0002: Keep Shoshin harness-agnostic and fixed at its current content

## Context

ADR 0001 adopted the Shoshin name and the `shoshin/` source package, but it framed the package as PStack skills adapted for one agent harness and fixed harness-specific locations: a personal installation target under one harness's skill directory and generated verification skills under one project directory layout. The validator also defaulted to a script shipped by one harness.

The repository now requires every skill to work in any agent harness, or with small changes, and installs skills as symbolic links to the repository source (see the repository's `mission.md`). The user asked for Shoshin to follow that rule because its skills are general engineering methods. User's words, 2026-10-22:

> 我是这么想的，shoshin这一套技能，你能不能抽成harness 无关的？因为shoshin这一套技能是软件工程和ai coding领域的通用技能或原则

The user also decided how Shoshin relates to its upstream. User's words, 2026-10-22:

> 上游是 PStack 没错，但除非我主动说让拉取上游 PStack 的最新代码，再去改动 SHOSHIN 技能包里面的东西，否则现在先把 SHOSHIN 的内容固定下来

On where generated verification skills go, user's words, 2026-10-22:

> 生成的验证 skill 不要写死路径，让生成验证 skill 的那一个 skill，还有维护验证 skill 的那一个 skill 自己去判断应该生成在哪里，因为每一个 agent 的 harness 的 skill 所放的位置都不一样

## Decision

Keep the Shoshin name and the `shoshin/` source package from ADR 0001. Replace its harness-specific parts:

- Shoshin is a package of general software-engineering skills written so any coding agent can follow them. Text that only one harness needs goes under a heading that names that harness, or into a file only that harness reads, such as `agents/openai.yaml`.
- Shoshin's content is fixed at the current repository version and maintained here through the repository's normal change process. It is compared with newer PStack releases only when the user explicitly asks.
- Skills are installed only as the user names them, as symbolic links made by the repository's `scripts/install_links.py`. The package names no installation directory.
- create-verification-skill decides where a generated `verify-<app>` skill goes in the target project, from the project's existing skill location or the project skill directory of the harness that will run it, and asks the user when that is unclear. maintain-verification-skill finds existing verification skills by the user's path or by searching the project.
- `scripts/validate-skills.py` uses the repository's own SKILL.md structure check instead of a script from any harness installation.

## Options Considered

### Harness-agnostic package fixed at current content

- Benefits: the skills work in whichever harness loads them; one source; no surprise drift from upstream.
- Costs: upstream improvements arrive only when the user asks for a comparison.

### Keep ADR 0001 as it was

- Benefits: no changes.
- Costs: the package stays bound to one harness, contrary to the repository's rule and the user's request.

### Track upstream PStack continuously

- Benefits: upstream fixes arrive sooner.
- Costs: contrary to the user's decision; each sync can reintroduce harness-specific text.

## Consequences

- Positive: installing Shoshin into another harness needs no change to SKILL.md bodies.
- Negative: generated verification skill locations are decided per project and harness, so reports must state the chosen location.
- Follow-up: the repository check in `scripts/validate_all.py` reports agent names and directories outside agent-named sections.

## Links

- [SOURCE: docs/adr/0001-shoshin-package-identity.md]
- [SOURCE: docs/architecture-v0.1.md]
