# Agent Skills

This repository collects reusable Codex skills that I maintain for recurring personal and project workflows.

## Skills

| Skill | Documentation | Installable folder | Purpose | Implicit invocation |
|---|---|---|---|---|
| `opencode-delegation` | [codex-delegate-to-opencode-skill/README.md](codex-delegate-to-opencode-skill/README.md) | `codex-delegate-to-opencode-skill/opencode-delegation/` | Delegate coding work to local OpenCode while Codex supervises, reviews, and verifies. | Yes, only for explicit OpenCode delegation requests |
| `document-governance` | [document-governance/SKILL.md](document-governance/SKILL.md) | `document-governance/` | Govern project documentation, durable Idea/Backlog lifecycles, and fail-closed Runbook execution contracts. | Yes |
| `grill-me` | [grill-skill/README.md](grill-skill/README.md) | `grill-me/` | Run the latest imported upstream interview without live document capture. | Yes |
| `grill-with-docs` | [grill-skill/README.md](grill-skill/README.md) | `grill-with-docs/` | Interview and capture terms and decisions through Document Governance. | Yes |
| `siblog-blog-workflow` | [siblog-blog-workflow/SKILL.md](siblog-blog-workflow/SKILL.md) | `siblog-blog-workflow/` | Prepare, translate, format, and publish SiBlog posts through the repository-owned blog commands, and draft a SiBlog technical post from the current Claude Code or Codex thread with `blog:tilian`. | Yes, for SiBlog blog commands |
| `video-download` | [video-download/SKILL.md](video-download/SKILL.md) | `video-download/` | Download the highest available and verifiable video resolution from a supplied URL. | Yes |
| `long-task-planning` | [long-task-planning/SKILL.md](long-task-planning/SKILL.md) | `long-task-planning/` | Keep a long coding task's goal, plan and done/not-done state from drifting; status is computed from recorded evidence, never written by hand. | Yes |
| `codex-orchestration` | [codex-orchestration/SKILL.md](codex-orchestration/SKILL.md) | `codex-orchestration/` | Let Claude Code manage the local Codex CLI as a delegated coding agent: briefs, stop files, rulings, commit reviews and sessions. | Yes, when Claude Code delegates work to Codex |
| `readable-output` | [readable-output/SKILL.md](readable-output/SKILL.md) | `readable-output/` | Make every response to the user easy to understand and check: plain text with writing rules adapted from ASD-STE100, an ASCII diagram checked by `scripts/check_ascii.py` (display width aware, so Chinese counts as 2 columns), or an HTML Artifact with its link in the response. | Yes |
| `hermes-ssh` | [hermes-ssh/SKILL.md](hermes-ssh/SKILL.md) | `hermes-ssh/` | Connect to the Hermes Linux server through SSH and Cloudflare Access, verify the remote host, and diagnose connection failures. | Yes, for Hermes server access |

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

Install either additional standalone skill by copying its complete folder after checking for an existing installation:

```bash
cp -R siblog-blog-workflow "$HOME/.agents/skills/"
cp -R video-download "$HOME/.agents/skills/"
```

The SiBlog workflow requires the SiBlog repository and its publishing checks. Video downloads require `yt-dlp` and FFmpeg (`ffprobe`); see the skill entrypoints for usage and access limits.

Restart Codex if a newly installed skill does not appear immediately.

### Claude Code skills

`long-task-planning` and `codex-orchestration` run from Claude Code. Install both side by side in `~/.claude/skills/`, because `codex-orchestration/scripts/codex-launch.sh` calls `../../long-task-planning/scripts/longtask.py`. A symbolic link keeps the installed skill and this repository the same files, so edits made while using a skill show up in `git status`:

```bash
ln -s "$PWD/long-task-planning" "$HOME/.claude/skills/long-task-planning"
ln -s "$PWD/codex-orchestration" "$HOME/.claude/skills/codex-orchestration"
```

`readable-output` publishes pages through Claude Code's Artifact tool and needs no other skill. Install it the same way:

```bash
ln -s "$PWD/readable-output" "$HOME/.claude/skills/readable-output"
```

`long-task-planning` also needs its session-start hook in `~/.claude/settings.json` (Claude Code) and `~/.codex/hooks.json` (Codex, matcher `startup|resume|clear|compact`; then trust it in Codex `/hooks`). Use the absolute path of the installed script:

```json
{"type": "command", "command": "python3 /absolute/home/.claude/skills/long-task-planning/scripts/longtask.py hook", "timeout": 20}
```

Point the global agent instructions (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) at `long-task-planning/SKILL.md` so every hands-on task picks light or full mode. `long-task-planning/FEEDBACK.md` and `*/tests/verification/*/local/` stay on the maintainer's machine and are git-ignored, because they hold private project details.

## Validate

Run all repository checks (the structure check needs PyYAML):

```bash
uv run --no-project --with pyyaml python scripts/validate_all.py
```

The validation script reads [skills.json](skills.json), checks each skill's `SKILL.md` structure with the rules of Codex `quick_validate.py` except that extra frontmatter keys such as Claude Code's `argument-hint` are allowed, then runs each package's declared tests and Python quality checks.

## Repository Policy

- Keep human-facing package documentation in each `*-skill/README.md`.
- Keep runtime skill folders lean; do not copy package README files into installed skill folders.
- Keep deterministic behavior in scripts and semantic workflow guidance in `SKILL.md`.
