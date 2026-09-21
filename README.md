# Agent Skills

This repository collects reusable Codex skills that I maintain for recurring personal and project workflows.

## Skills

| Skill | Documentation | Installable folder | Purpose | Implicit invocation |
|---|---|---|---|---|
| `opencode-delegation` | [codex-delegate-to-opencode-skill/README.md](codex-delegate-to-opencode-skill/README.md) | `codex-delegate-to-opencode-skill/opencode-delegation/` | Delegate coding work to local OpenCode while Codex supervises, reviews, and verifies. | Yes, only for explicit OpenCode delegation requests |
| `document-governance` | [document-governance/SKILL.md](document-governance/SKILL.md) | `document-governance/` | Govern project documentation, durable Idea/Backlog lifecycles, and fail-closed Runbook execution contracts. | Yes |

Each package README or skill entrypoint explains the specific skill's purpose, install steps, usage examples, and verification commands. The installable skill folders should stay focused on runtime resources: `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/` when needed.

## Shoshin

[Shoshin](shoshin/README.md) 提供 16 个工程技能，源码位于 `shoshin/skills/<skill-name>/`。
已接入本仓库结构与脚本检查；按用户本轮要求，真实项目、完整 UI 与安装后验收保留未完成。
安装时复制完整技能目录并保留 LICENSE，先核查同名目标，详见包说明。

## Install

Install one skill, for example:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R document-governance "$HOME/.agents/skills/"
```

Install both original standalone skills (see the Shoshin package for its installation steps):

```bash
mkdir -p "$HOME/.agents/skills"
cp -R codex-delegate-to-opencode-skill/opencode-delegation "$HOME/.agents/skills/"
cp -R document-governance "$HOME/.agents/skills/"
```

Restart Codex if a newly installed skill does not appear immediately.

## Validate

Run all repository checks:

```bash
python3 scripts/validate_all.py
```

The validation script reads [skills.json](skills.json), runs `quick_validate.py` for each skill, then runs each package's declared tests and Python quality checks.

## Repository Policy

- Keep human-facing package documentation in each `*-skill/README.md`.
- Keep runtime skill folders lean; do not copy package README files into installed skill folders.
- Keep deterministic behavior in scripts and semantic workflow guidance in `SKILL.md`.
