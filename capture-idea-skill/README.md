# capture-idea Skill

## What It Does

`capture-idea` preserves meaningful ideas, creative insights, original wording, thinking shifts, and open questions from an AI conversation. It is meant for moments where the conversation produced a product or design insight worth revisiting later.

It is not a meeting-notes tool, a generic conversation summarizer, or an implementation log.

## How It Works

The skill deliberately separates semantic judgment from deterministic file operations:

- `SKILL.md` guides Codex to identify the core idea, thought trajectory, verbatim quotes, and open questions.
- `scripts/capture_idea.py` creates the note, updates the index, generates the slug, and handles filename collisions.

The generated files are written to the current working project's `docs/ideas/` directory.

## Installation

Copy the installable skill folder into Codex's user skill directory:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R capture-idea "$HOME/.agents/skills/"
```

Restart Codex if the skill does not appear immediately.

## Installed Skill Layout

```text
$HOME/.agents/skills/capture-idea/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── capture_idea.py
└── references/
    ├── good-capture.md
    └── bad-capture.md
```

This README is package-level documentation for humans. It is not part of the runtime skill folder.

## Usage

Trigger it in Codex with:

```text
$capture-idea
记录一下这个想法
记录我的灵感
记录我的创意
save this idea
```

Run the script manually for a dry-run preview:

```bash
python "$HOME/.agents/skills/capture-idea/scripts/capture_idea.py" \
  --title "认知分层 profile 设计" \
  --core-ideas "- profile 不是用户事实档案，而是用户认知状态的分层快照" \
  --thought-trajectory "- 从平面记忆存储出发，转向区分稳定层和漂浮层" \
  --quotes '["有些认知是笃定的深度记忆，有些还在脑海的浅层漂荡", "profile 不能只做事实归档"]' \
  --open-questions "- 是否在 profile 中显式使用分层语言？" \
  --dry-run
```

## Verification

Run checks from the repository root:

```bash
uv run --with pytest python -m pytest capture-idea-skill/capture-idea/tests -q
uv run --with ruff ruff check capture-idea-skill/capture-idea/scripts capture-idea-skill/capture-idea/tests
```
