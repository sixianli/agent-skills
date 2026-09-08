---
name: blast-radius
description: "Assess the impact of a diff or proposed change, including implicit consumers and critical safety assumptions. Work read-only by default; discovering a risk does not authorize fixing it."
---

# blast-radius

Start with an explicit diff, baseline, or proposed change. Distinguish implemented behavior from a proposal. Do not guess the default branch or overwrite the worktree.

1. Explain the observable contract that changes and the critical assumptions its safety depends on. There may be several; do not force them into one.
2. Trace actual callers, configuration, persisted fields, serialization formats, readers in other languages, and asynchronous lifecycles. Use the [impact review](references/impact-review.md) to check relationships symbol searches miss.
3. Separate confirmed risks, cleared risks, and unverified conditions. For each, state the trigger, consequence, evidence, and smallest useful check. A code citation, logical elimination, executable check, and running-app reproduction are different kinds of evidence.
4. Under strict read-only constraints, do not write scripts or start processes. If experiments are authorized, choose the smallest real check and report exactly what it proves. Deliver findings when a defect is found; do not fix it automatically.

Use [how](../how/SKILL.md) through host discovery for missing mechanism details, or [why](../why/SKILL.md) when historical constraints affect compatibility. Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

The primary agent works by default. Delegate only when independent investigation or review offers a concrete benefit worth the additional token cost and the current host permits it. Specify the inputs, required evidence, scope, and stopping point. Verify returned artifacts and report omissions. Complexity or tool availability alone does not justify spawning subagents.

Deliver an explanation of the change, the degree of proof for its critical assumptions, risks, and reasons for clearing other risks. Check at least one relationship that is not an explicit call. Do not treat an empty search, reviewer agreement, or successful compilation as proof of production safety.
