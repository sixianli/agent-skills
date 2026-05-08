# capture-idea Skill for Codex CLI

## Background: Why capture-idea Exists

### The Moment That Started It

In April 2026, I was using an AI coding agent to explore requirements for a side project. It was one of those long, exploratory conversations — the kind where you start with a vague product question and end up somewhere you didn't expect.

Midway through, I said something unplanned. An analogy. It wasn't in my notes or my outline, but the moment it came out, it connected several vague intuitions into a coherent framework. The agent immediately recognized it as the most valuable insight in the entire discussion and restructured its subsequent recommendations around it.

When the conversation ended, I realized: **if I don't capture this right now, in two weeks I'll vaguely remember "I discussed some kind of layered design," but I won't remember the analogy itself, the exact phrasing, or the product intuition behind it.** So I manually asked the agent to save the conversation as an archived note.

Then I thought: this isn't the first time. Every deep exploration session with an AI agent produces moments like this — an unexpected analogy, a critical shift in thinking, a sentence said off the cuff that crystallized something I'd been circling for days. These moments are as valuable as the code that eventually gets written, but they're ephemeral. The raw conversation transcript is too long and too noisy to dig through after the fact. The good stuff drowns.

**If I have to ask my agent for the same thing twice, the system has failed.** That principle made the decision for me. I turned "idea archiving" into a reusable skill.

### Design Philosophy

Four ideas shaped how capture-idea works.

**Latent vs. deterministic, strictly separated.** Deciding which parts of a conversation are worth preserving — that's a judgment call. It belongs in latent space. Writing the file, generating the slug, updating the index, handling filename collisions — that's deterministic work. It belongs in code. So the skill is split in two: SKILL.md guides the LLM through semantic distillation; a Python script handles every file-system operation. Clean boundary, no leakage.

**Preserve the original words. Don't polish.** The single most important constraint in this skill is that verbatim quotes must remain entirely unaltered. When future-me reads back the exact words I used in that moment, I'm instantly back in that headspace. If the AI sanitizes it into generic technical terminology, all the texture and recognition value is gone. The raw words are the point.

**Capture change, not topics.** The most valuable part of a conversation isn't what was discussed — it's where your thinking shifted. The pivot from Plan A to Plan B. The moment a vague intuition snapped into a clear framework. The transition from "I'm not sure" to "oh, that's what this is about." Those turning points are what you actually want to revisit later. That's why the Thought Trajectory field is designed to record pivots and aha moments, not flat chronological narration.

**A skill is a permanent upgrade.** Before capture-idea existed, saving an insight was a one-off manual operation — interrupt the conversation, ask the agent to archive, come up with a filename, manage the directory yourself. Once it became a skill, the capability was permanently embedded in my development environment. It doesn't degrade. It doesn't forget. And when the underlying model improves, its judgment about what's worth capturing automatically gets better too.

### What It Is Not

capture-idea is not a meeting-notes tool. It's not a conversation summarizer. It's not a note-taking app. It serves one narrow purpose: **extracting fleeting creative insights and thinking shifts from your conversations with AI agents.** The output isn't documentation for a team — it's an idea journal for your future self. The kind of artifact where you open it weeks later and say, "Oh, *that's* what I was thinking," or "So *that's* where this feature actually came from."

## Installation

Most users already have the `~/.codex/skills/` directory. The only setup needed here is to create the `capture-idea/` subdirectory under it and copy the skill files into place:

```bash
mkdir -p ~/.codex/skills/capture-idea
cp -r capture-idea/* ~/.codex/skills/capture-idea/
chmod +x ~/.codex/skills/capture-idea/scripts/capture_idea.py
```

## Directory Structure

```
~/.codex/skills/capture-idea/
├── SKILL.md                      # Skill instruction file read by Codex
├── scripts/
│   └── capture_idea.py           # Deterministic file operation script
├── references/
│   ├── good-capture.md           # Good example
│   └── bad-capture.md            # Bad example
└── tests/
    └── test_capture_idea.py      # 21 pytest tests
```

After running, the skill generates:

```
<current working project>/docs/ideas/
├── INDEX.md                      # Index table
└── YYYY-MM-DD-<slug>.md          # Idea note
```

## Usage

Trigger it in Codex CLI with:

```
$capture-idea
记录一下这个想法
记录我的灵感
记录我的创意
save this idea
```

Run the script manually for a dry-run preview:

```bash
# Run this inside the target project directory
python ~/.codex/skills/capture-idea/scripts/capture_idea.py \
  --title "认知分层 profile 设计" \
  --core-ideas "- profile 不是用户事实档案，而是用户认知状态的分层快照" \
  --thought-trajectory "- 从平面记忆存储出发，转向区分稳定层和漂浮层" \
  --quotes '["有些认知是笃定的深度记忆，有些还在脑海的浅层漂荡", "profile 不能只做事实归档"]' \
  --open-questions "- 是否在 profile 中显式使用分层语言？" \
  --dry-run
```

## Run Tests

```bash
cd ~/.codex/skills/capture-idea
uv run --with pytest python -m pytest tests/ -v
```
