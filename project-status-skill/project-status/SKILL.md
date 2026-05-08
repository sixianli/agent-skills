---
name: project-status
description: >
  Maintain a current.md file that tracks real-time project state — what's in progress,
  what just completed, what's blocked, and what to do next. Activated when the user
  asks about current project state, wants to resume previous work, or when triggered
  by AGENTS.md rules after commits, task completion, or repeated failures.
---

# Project Status Tracker

## Purpose

You maintain a file called `current.md` at the project root. Its sole job is to let
a developer (or a future agent session) recover full working context in under 60 seconds.

`current.md` answers five questions:
1. What am I currently working on?
2. What did I just finish?
3. Where am I stuck?
4. Why am I stuck?
5. What's the first thing to do next?

## When to READ

Read `current.md` ONLY when the user explicitly asks. Examples:
- `$project-status`
- "What's the current status?"
- "Where did I leave off?"
- "Continue the unfinished work"
- "What was I working on?"

When reading:
1. Read `current.md` from the project root.
2. Use the snapshot and recent log entries to restore context.
3. Briefly summarize the state to the user in 2-3 sentences.

Do NOT read `current.md` at session start automatically. The user may be starting
something entirely new, and injecting old context would interfere with that.

## When to WRITE

Write triggers come from AGENTS.md rules. When triggered, follow the update
procedure below. There are three entry types:

### checkpoint

Triggered after a commit or a sequence of closely related commits for one
logical change. This is the most common entry type.

Required fields: Working on, Done, Next step.

### milestone

Triggered when a clearly defined task, feature, or phase is completed.

Signs of a milestone:
- Tests passing for a new feature
- A module fully wired up and pushed to main
- A complete integration working end-to-end
- A version tag or a deployment

Required fields: Completed, Verification, Next step.

### blocker

Triggered when progress stops — a dependency issue, a design question, an
external constraint, or repeated failed attempts at solving a problem.

Required fields: Blocked on, Reason, Attempted, Next step.

## What NOT to record

- Long-term product vision (belongs in README or PRD)
- Stable architecture decisions (belongs in DESIGN.md or ADRs)
- Detailed implementation plans (belongs in plan files)
- Meeting notes or stream-of-consciousness
- Information already captured in other project documents — just reference them

## File structure

`current.md` has two sections:

### Section 1: Snapshot

The top of the file. A concise summary of the latest state with these fields:
- Working on
- Just finished
- Blocked by (or state that there are no blockers)
- Next step
- Last updated (YYYY-MM-DD HH:MM TZ)

Every time you write a new log entry, overwrite this section to match.

### Section 2: Log

Below the snapshot. Reverse chronological list of entries.
Each entry is a level-3 heading with format: `YYYY-MM-DD HH:MM TZ | <type>`
where type is one of: checkpoint, milestone, blocker.

Each entry contains only the fields relevant to its type. Do not include
fields with empty or "None" values.

## Language

Write all content in the same language the user is using in the conversation.
Do not use fixed English headings or boilerplate text if the user communicates
in another language. The structure (heading levels, field labels, timestamp format)
must stay consistent, but the actual text must match the project's language context.

## Retention

Keep the most recent **5** log entries in `current.md`.
When appending a new entry would exceed 5, move the oldest entries to
`current-archive.md` in the same directory before appending.
If `current-archive.md` does not exist, create it with an appropriate heading.

## Update procedure

When writing an update:

1. Determine the entry type (`checkpoint`, `milestone`, or `blocker`).
2. Compose the log entry with only the relevant fields.
3. Insert the new entry at the top of the Log section (reverse chronological).
4. Overwrite the Snapshot section to reflect the new entry.
5. Check entry count. If > 5, move overflow to `current-archive.md`.
6. Write the file.

## Bootstrap

If `current.md` does not exist when a write is triggered:

1. Scan the project for context: README, recent git log (last 5 commits),
   any TODO/FIXME comments, current branch.
2. Create `current.md` with the triggering entry plus inferred project state.
3. Tell the user what you inferred and ask if it's accurate.

If the user explicitly asks to create `current.md` from scratch (e.g. "initialize
project status"), follow the same procedure.
