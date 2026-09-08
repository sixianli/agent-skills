---
name: show-me-your-work
description: "Keep one TSV decision log and check its evidence for complex tasks whose decisions need review. Record choices, pivots, verification, and blockers; do not create logs for ordinary operations."
---

# show-me-your-work

Start with the current complex task and actual decision points. Write one TSV at a caller-selected path. Each task has one writer; the log is neither a task-state cache nor an automatic scheduler.

Use the six columns in the [header](references/decision-log-template.tsv): ts, phase, decision, why, evidence, result. Evidence points to a locatable artifact, commit, or source location, never an expected outcome. Record choices, pivots, verification, and blockers as needed, not a copy of tool logs.

Run the helper through this skill's actual path:

```bash
bash scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

These are argument placeholders. Replace them with actual values and pass each as a safely quoted argument. The script creates a header and appends a UTC timestamp, flattens cells to one line, protects against spreadsheet formula prefixes, and rejects an invalid existing header. Authorization to write one task log does not grant access to other paths.

Correct mistakes by appending a row that references the original; preserve history. At the end, check that each row's evidence exists and supports its result, and add any missing pivots that affect the conclusion. Do not scan unrelated conversations. If the host does not expose the current raw transcript, audit only available artifacts and visible events, and state that limit.

If evidence strength is unclear, read only create-verification-skill's [evidence standards](../create-verification-skill/references/evidence-standards.md). Delegate independent checking of a long log or material gaps only when it is worth the extra token cost and the host permits it. For details, read only figure-it-out's [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver the log path, checked scope, weak evidence, and gaps. Do not require a different model family or turn a short log audit into repeating the task.
