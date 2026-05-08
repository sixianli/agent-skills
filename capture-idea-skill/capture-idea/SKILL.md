---
name: capture-idea
description: Capture a meaningful idea, creative insight, or thinking shift from the current conversation into a durable project note under the current project's docs/ideas/. Use when the user wants to preserve an idea for future reference, not for routine debugging or factual Q&A.
---
# capture-idea

Distill a valuable idea from the current conversation into a structured note under the current project's `docs/ideas/`, preserving the user's original thinking, key quotes, and open questions.

## When to Use

Trigger on expressions like:

- "记录我的灵感", "记下我的创意", "capture", "save this idea"
- "$capture-idea"
- "我不想丢失这个想法"
- Or any close semantic equivalent where the user clearly wants to preserve a non-trivial idea.

Do **not** trigger for routine bug fixes, narrow implementation troubleshooting, pure factual lookup, or low-level technical Q&A with no broader design or product insight.

## Execution Flow

### Step 1 — Determine Project (deterministic)

Infer the project name from the current working project's repository or folder name. The skill itself is installed under `~/.codex/skills/capture-idea/`, but the output target is still the current working project. If ambiguous, ask the user before proceeding.

### Step 2 — Distill the Idea (latent — this is the core judgment step)

Review the current conversation and produce exactly four sections:

**Core Ideas** — 1-2 core ideas. Use the user's own phrasing where possible. Do not sanitize into generic language.

**Thought Trajectory** — How the user's thinking evolved. Focus on pivots, "aha" moments, reframing, and priority shifts. Do not write flat chronological narration.

**Verbatim Quotes** — 2-3 high-value quotes from the user. These must remain entirely unaltered. Prefer lines that preserve intent, taste, insight, or strategic thinking.

**Open Questions** — Unresolved questions that emerged. Include only questions still meaningfully open.

### Step 3 — Write Files (deterministic)

Run the helper script installed under `~/.codex/skills/capture-idea/` to handle all file operations while keeping the shell's current working directory inside the target project:

```bash
python ~/.codex/skills/capture-idea/scripts/capture_idea.py \
  --title "..." \
  --project "..." \
  --core-ideas "..." \
  --thought-trajectory "..." \
  --quotes '["...", "..."]' \
  --open-questions "..."
```

The script will:

- Create `docs/ideas/YYYY-MM-DD-<slug>.md` inside the current working project (auto-deduplicates if same-day collision)
- Append a row to the current working project's `docs/ideas/INDEX.md` (creates if missing)

### Step 4 — Display Result

Output the generated file path and a 1-3 line summary. Do not output the full file contents unless asked.

## Quality Bar

A good capture preserves the user's actual idea (not a sanitized version), surfaces why it mattered, retains evidence of changing thinking, and is useful when revisited weeks later. See `references/good-capture.md` and `references/bad-capture.md` for examples.

## Boundaries

This skill is specifically for preserving promising ideas and the thinking shifts around them. Do not use it to create meeting minutes, generic conversation summaries, implementation docs, troubleshooting logs, or research notes without idea-level synthesis.
