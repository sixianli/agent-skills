---
name: interrogate
description: "Independently review specified code or a diff, challenge critical assumptions, and verify findings, including conservative comment review. Review requests do not authorize edits or require a fixed multi-model vote."
---

# interrogate

Establish the review intent, change scope, and actual baseline. Read related requirements, callers, and existing tests. Remain read-only when the user requests a review.

Use the [review criteria](references/review-criteria.md) to find correctness, contract, and maintainability issues that affect the goal. Look for hidden state, layers that require excessive navigation to understand, and redundancy relevant to the task. Recommend removing only confirmed redundancy; the possibility of shorter code does not justify expanding scope. For comments, read [comment review](references/comment-review.md). Preserve rationale, public contracts, external constraints, and safety requirements. Investigate uncertainty before deleting anything.

The primary agent works by default. Delegate only when independent investigation or review offers a concrete benefit worth the additional token cost and the current host permits it. Specify the inputs, required evidence, scope, and stopping point. Verify returned artifacts and report omissions. Complexity or tool availability alone does not justify spawning subagents. Give an independent reviewer the original requirements, code, and necessary context, not just the primary agent's conclusions. Actual tool permissions provide isolation; a role prompt does not. Record the review method actually used. An ordinary subagent is not equivalent to review across model families. Report failed or uncovered review work explicitly.

The lead reviewer verifies each finding's concrete trigger, consequence, and evidence, deduplicates it, and classifies it as Act on, Consider, Noted, or Dismissed. Consensus does not establish validity, and a lone finding may be correct. Explain missing context or counterevidence for dismissed findings. Use discovered [how](../how/SKILL.md) / [why](../why/SKILL.md) skills for necessary mechanism or history investigation. For delegation decisions, read only figure-it-out's [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). To assess added layers, read only architect's [complexity](../architect/references/design-review.md#complexity). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver verified, actionable findings with locations and the smallest useful validation. Preserve material dismissals and coverage limits. Apply changes only when authorized. If there are no findings, state the actual review scope rather than inventing issues.
