---
name: figure-it-out
description: "Organize an authorized complex goal into verifiable implementation units with explicit dependencies and revise assumptions using evidence. Use for multi-phase work; do not create persistent tasks, automatic scheduling, or delivery pipelines."
---

# figure-it-out

Start with the goal, scope, constraints, and completion criteria. State the final observable result and current unknowns. Understand the system through existing evidence or discovered [how](../how/SKILL.md). Analysis and planning requests authorize their respective deliverables, not implementation.

1. Organize verifiable units around actual dependencies. Address risky unknowns that could change the design first. Give each unit inputs, artifacts, and pass criteria. Intermediate progress is not final completion.
2. Compare direct execution, batched tool calls, and deterministic scripts. Build tools when repeatable transformations or checks benefit; do not require a script for every nontrivial task. Filter large output before deciding whether isolated context is worthwhile.
3. After repeated failures, state the shared premise, check the observation method and counterevidence, then choose another experiment. Do not keep patching to preserve an old hypothesis. If design assumptions change, use [architect](../architect/SKILL.md) to reassess within the approved scope.
4. Execute clear, authorized work and continue after verifying each unit. Distinguish artifact defects, faulty checks, and inadequate environments. Keep, revert, or redesign based on evidence. Never lower acceptance standards to hide problems.
5. Use [show-me-your-work](../show-me-your-work/SKILL.md) when a complex task needs a reviewable decision trail; do not duplicate its format. Finally, check each original goal and report actual completion and gaps.

For repeated failures, read [premise review](references/execution-methods.md#premise-review). For batch work, read [tool selection](references/execution-methods.md#tool-selection). For large material or possible delegation, read [context and delegation](references/execution-methods.md#context-and-delegation). For migrations with permitted intermediate states, read [phase acceptance](references/execution-methods.md#phase-acceptance).

The primary agent works by default; complexity or decomposability alone does not justify delegation. When independent benefits justify total token and coordination costs and the host permits it, bound inputs, write ownership, outputs, agent count, and stopping points. Verify every artifact. Success elsewhere does not cancel a failure or omission.

Use the discovered document-governance skill for formal Specs and Plans in projects that have adopted it. For real product verification, discover the project's verification skill; report gaps if it is missing or the product cannot be controlled. Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

This method does not create a goal, heartbeat, persistent mode, or automatic PR. Completion means meeting the user's criteria; a passing test run or time remaining does not excuse an undelivered goal.
