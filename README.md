# Agent Skills

This repository collects reusable agent skills. Each skill works with the user-selected project and current environment; shared source must not assume a particular person, account, host, site, or private project.

## Skills

| Skill | Documentation | Installable folder | Purpose | Implicit invocation |
|---|---|---|---|---|
| `document-governance` | [document-governance/SKILL.md](document-governance/SKILL.md) | `document-governance/` | Govern project documentation, durable Idea/Backlog lifecycles, and fail-closed Runbook execution contracts. | Yes |
| `grill-me` | [grill-skill/README.md](grill-skill/README.md) | `grill-me/` | Run the latest imported upstream interview without live document capture. | Yes |
| `grill-with-docs` | [grill-skill/README.md](grill-skill/README.md) | `grill-with-docs/` | Interview and capture terms and decisions through Document Governance. | Yes |
| `blog-workflow` | [blog-workflow/SKILL.md](blog-workflow/SKILL.md) | `blog-workflow/` | Prepare, translate, format, and publish posts in a selected Hugo project; draft technical articles from a selected session. | Yes, for blog commands |
| `video-download` | [video-download/SKILL.md](video-download/SKILL.md) | `video-download/` | Download the highest available and verifiable video resolution from a supplied URL. | Yes |
| `human-writing-zh` | [human-writing-zh/README.md](human-writing-zh/README.md) | `human-writing-zh/` | Write or edit natural Chinese articles while preserving facts, conditions, quotations, and the author's voice. | Yes, for Chinese writing and editing requests |
| `long-task-planning` | [long-task-planning/SKILL.md](long-task-planning/SKILL.md) | `long-task-planning/` | Keep a long coding task's goal, plan and done/not-done state from drifting; status is computed from recorded evidence, never written by hand. | Yes |
| `codex-orchestration` | [codex-orchestration/SKILL.md](codex-orchestration/SKILL.md) | `codex-orchestration/` | Let Claude Code manage the local Codex CLI as a delegated coding agent: briefs, stop files, rulings, commit reviews and sessions. | Yes, when Claude Code delegates work to Codex |
| `readable-output` | [readable-output/SKILL.md](readable-output/SKILL.md) | `readable-output/` | Make every response to the user easy to understand and check: plain text with writing rules adapted from ASD-STE100, an ASCII diagram checked by `scripts/check_ascii.py` (display width aware, so Chinese counts as 2 columns), or an HTML Artifact with its link in the response. | Yes |
| `ssh-access` | [ssh-access/SKILL.md](ssh-access/SKILL.md) | `ssh-access/` | Connect to a selected SSH target using existing configuration, verify the host, and diagnose connection failures. | Yes, for SSH access |
| `sensitive-information-scan` | [sensitive-information-scan/SKILL.md](sensitive-information-scan/SKILL.md) | `sensitive-information-scan/` | Check files, staged content, local history, and Git identities for credentials and private context without printing matched values. | Yes, for privacy audits and pre-publication checks |

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

Install either additional standalone skill by copying its complete folder after checking for an existing installation:

```bash
cp -R blog-workflow "$HOME/.agents/skills/"
cp -R video-download "$HOME/.agents/skills/"
```

The blog workflow reads conventions and publishing checks from the selected Hugo repository. Install `sensitive-information-scan` separately when using its pre-publication check. Video downloads require `yt-dlp` and FFmpeg (`ffprobe`); see the skill entrypoints for usage and access limits.

For `human-writing-zh`, follow its [installation and usage guide](human-writing-zh/README.md). Copy the complete folder after checking for an existing installation, and retain `LICENSE` and `THIRD_PARTY_NOTICES.md`. The optional text review script needs Python 3.9+ and uses only the standard library. Its tests check the script's behavior; they do not establish writing quality or factual accuracy.

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
{"type": "command", "command": "python3 /absolute/path/to/skills/long-task-planning/scripts/longtask.py hook", "timeout": 20}
```

Point the global agent instructions (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) at `long-task-planning/SKILL.md` so every hands-on task picks light or full mode. `long-task-planning/FEEDBACK.md` and `*/tests/verification/*/local/` stay on the maintainer's machine and are git-ignored, because they hold private project details.

## Validate

Run all repository checks (the structure check needs PyYAML):

```bash
uv run --no-project --with pyyaml --with ruff python scripts/validate_all.py
```

The validation script reads [skills.json](skills.json), checks each skill's `SKILL.md` structure with the rules of Codex `quick_validate.py` except that extra frontmatter keys such as Claude Code's `argument-hint` are allowed, then runs each package's declared tests and Python quality checks.

## Repository Policy

- Keep human-facing package documentation in each `*-skill/README.md`.
- Keep runtime skill folders lean; do not copy package README files into installed skill folders.
- Keep deterministic behavior in scripts and semantic workflow guidance in `SKILL.md`.


## Privacy and portable source

Shared examples must use synthetic data, relative paths, placeholders, or parameters supplied by the user. Keep raw project transcripts, credentials, scan reports, and private detection patterns in ignored local storage. Anonymizing a project name alone is insufficient when its private data, implementation inventory, or personal directory still appears in a report.

The repository validator scans publishable working files and effective Git names and email identities. Current content allowances cover reserved example-domain email fixtures and explicitly listed public upstream documentation URLs; the policy requires a specific rule, full value match, and reason. This does not exclude test or documentation folders from scanning.

Install the versioned pre-commit hook in this checkout:

```bash
git config --local core.hooksPath .githooks
```

The hook scans the complete staged content and effective author and committer names and emails, including environment overrides. Select an appropriate public Git identity locally; GitHub provides a noreply email in account settings. Do not copy a maintainer's address or login into the skill. Hook installation is local to each checkout; cloning the repository does not automatically activate it.

Optional private detection patterns belong in `.agents/local/private-patterns.txt`, one regular expression per line. The hook reads that file when present; its contents remain ignored. Run a manual current-content check with those patterns:

```bash
python3 sensitive-information-scan/scripts/scan_sensitive.py --repo . --current-author --policy sensitive-information-scan/assets/repository-policy.json --private-patterns .agents/local/private-patterns.txt --fail-on-findings
```

Omit `--private-patterns` if no local file is configured. Use `--history` for reachable local history and `--include-ignored` for a separate local-only audit. A clean current checkout does not remove sensitive information from old commits or previously downloaded copies. Scan findings are candidates for review, and incomplete reads return an error rather than a clean result.

The portable skills are named `blog-workflow` and `ssh-access`. Older site- and host-specific names have been retired. Update the installed folder and skill invocation when migrating; draft placement now uses `--blog-root`, and sensitive scanning is a separate skill. Existing installation copies outside this repository are not updated by source changes.
