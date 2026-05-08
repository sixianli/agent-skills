# project-status

A skill for AI coding agents that maintains a `current.md` file at the project root, recording what you're working on, what you just finished, where you're blocked, and what to do next.

Works with **OpenAI Codex** and **Claude Code**.

## Why this exists

AI coding agents have no memory between sessions. You close a thread, come back a week later, and the agent has no idea what you were doing before. You probably don't remember either. Maybe last time you were debugging a weird flush issue, tried three approaches and none worked, and then something interrupted you, like your newborn starting to cry, so you just closed the terminal.

`current.md` solves this by keeping a lightweight, real-time status file in the repo. When you return to the project, you or your coding agent can read this file and quickly reconstruct the current state of the work.

### Design decisions

**Manual read, auto write.** Reading old context into a new session can pollute the agent's reasoning when you want to work on something completely new. So reads are manual — you ask for it when you need it. Writes, however, are automatic — they trigger after commits, milestone completions, and repeated failures. This matters because the moment you most need to record state is the moment you're least likely to do it yourself.

**No fixed template.** The skill describes structural rules rather than a template the agent should copy word for word. This prevents rigid boilerplate and lets the agent write in the language you actually use.

**Five-entry retention.** Only the 5 most recent log entries stay in `current.md`. Older entries are archived to `current-archive.md`. This keeps the file short enough to be useful without becoming noise.

## What `current.md` looks like

The file has two parts:

**Snapshot** — a fixed summary block at the top of the file that always reflects the latest state. Five fields: working on, just finished, blocked by, next step, last updated.

**Log** — reverse chronological entries, each tagged as one of three types:

- `checkpoint` — recorded after a commit. Most common.
- `milestone` — recorded when a task or feature is fully complete.
- `blocker` — recorded when progress stops due to a dependency, design question, or repeated failures.

Each entry only includes the fields relevant to its type, without empty values or filler like "None".

## Installation

### OpenAI Codex

**1. Copy the skill directory:**

```bash
mkdir -p "$HOME/.agents/skills"
cp -R project-status "$HOME/.agents/skills/"
```

**2. Add write triggers to your global `AGENTS.md`:**

Append the following to `~/.codex/AGENTS.md` (create it if it doesn't exist):

```markdown
## Project status tracking

When any of these happen, update current.md using the project-status skill:
- You made a commit
- You observed repeated failed attempts at solving a problem
- You completed a task or feature that was the goal of this session

Do NOT read current.md at session start unless the user explicitly asks.
```

**3. Restart Codex.**

### Claude Code

**1. Copy the skill directory:**

```bash
# User-level (all projects)
cp -r project-status ~/.claude/skills/

# Or project-level (single project)
cp -r project-status your-project/.claude/skills/
```

**2. Add write triggers to your `CLAUDE.md`:**

Append the following to `~/.claude/CLAUDE.md` (user-level) or `your-project/CLAUDE.md` (project-level):

```markdown
## Project status tracking

When any of these happen, update current.md using the /project-status skill:
- You made a commit
- You observed repeated failed attempts at solving a problem
- You completed a task or feature that was the goal of this session

Do NOT read current.md at session start unless the user explicitly asks.
```

**3. Claude Code detects skill changes automatically.** If it doesn't appear, restart Claude Code.

## Usage

### Reading status (manual)

Say any of these to your agent:

- "What's the current status?"
- "Where did I leave off?"
- "Continue the unfinished work"

In Codex: `$project-status`
In Claude Code: `/project-status`

The agent reads `current.md` and summarizes the current state in 2-3 sentences.

### Writing status (automatic)

You don't need to do anything. The AGENTS.md / CLAUDE.md rules trigger writes automatically:

- **After a commit** → `checkpoint` entry
- **After completing a feature** → `milestone` entry
- **After repeated failures** → `blocker` entry

You can also trigger a write manually by saying "record current status" or "update current.md".

### First-time setup (bootstrap)

If `current.md` does not exist when a write is triggered, the skill scans your project (README, recent git log, TODO/FIXME comments, current branch) and creates an initial entry. It tells you what it inferred and asks whether it is accurate.

## File structure

```
project-status/
├── SKILL.md              # Skill instructions
└── agents/
    └── openai.yaml       # Codex UI metadata (ignored by Claude Code)
```

## Retention

`current.md` keeps the 5 most recent log entries. Older entries are moved to `current-archive.md` in the same directory. These files are working-state artifacts; commit them only when the project intentionally treats status history as shared documentation.

## Boundaries

These things do **not** belong in `current.md`:

- Long-term product vision → README or PRD
- Architecture decisions → DESIGN.md or ADRs
- Implementation plans → plan files
- Meeting notes or stream-of-consciousness
- Anything already in other project documents — just reference them

## License

MIT
