# Agent Skills

This repository collects reusable Codex skills that I maintain for recurring personal and project workflows.

## Skills

| Skill | Documentation | Installable folder | Purpose | Implicit invocation |
|---|---|---|---|---|
| `capture-idea` | [capture-idea-skill/README.md](capture-idea-skill/README.md) | `capture-idea-skill/capture-idea/` | Preserve product ideas, original wording, thinking shifts, and open questions from an AI conversation. | Yes |
| `project-status` | [project-status-skill/README.md](project-status-skill/README.md) | `project-status-skill/project-status/` | Maintain project-level `current.md` working-state notes for resumable agent sessions. | Yes |
| `opencode-delegation` | [codex-delegate-to-opencode-skill/README.md](codex-delegate-to-opencode-skill/README.md) | `codex-delegate-to-opencode-skill/opencode-delegation/` | Delegate coding work to local OpenCode while Codex supervises, reviews, and verifies. | Yes, only for explicit OpenCode delegation requests |
| `document-governance` | [document-governance/SKILL.md](document-governance/SKILL.md) | `document-governance/` | Govern project documentation layers, templates, archives, validation, and code-document consistency. | Yes |

Each package README or skill entrypoint explains the specific skill's purpose, install steps, usage examples, and verification commands. The installable skill folders should stay focused on runtime resources: `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/` when needed.

## Install

Install one skill:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R capture-idea-skill/capture-idea "$HOME/.agents/skills/"
```

Install all skills:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R capture-idea-skill/capture-idea "$HOME/.agents/skills/"
cp -R project-status-skill/project-status "$HOME/.agents/skills/"
cp -R codex-delegate-to-opencode-skill/opencode-delegation "$HOME/.agents/skills/"
cp -R document-governance "$HOME/.agents/skills/"
```

Restart Codex if a newly installed skill does not appear immediately.

## Validate

Run all repository checks:

```bash
python3 scripts/validate_all.py
```

The validation script reads [skills.json](skills.json), runs `quick_validate.py` for each skill, then runs package-specific checks such as pytest and ruff for `capture-idea` and Python checks for `document-governance`.

## Repository Policy

- Keep human-facing package documentation in each `*-skill/README.md`.
- Keep runtime skill folders lean; do not copy package README files into installed skill folders.
- Keep local working-state files such as `current.md` out of Git unless a project explicitly treats them as shared documentation.
- Keep deterministic behavior in scripts and semantic workflow guidance in `SKILL.md`.
