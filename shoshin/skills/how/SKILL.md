---
name: how
description: "Explain code mechanisms, call chains, ownership, and boundaries for code walkthroughs and understanding before a change. Use why for historical rationale; explanation requests do not authorize edits."
---

# how

Start from the question and supplied code scope. Work read-only by default. For a narrow function question, trace only the paths needed to answer it. For a system question, state the scope of the explanation; a directory tree is not a system model.

1. Find the user action or call entrypoint and follow actual callers through to the output. Check configuration, registration, dependency injection, and callbacks. Matching symbol names alone do not establish a call chain.
2. Explain how inputs are parsed, how data changes, who owns state, and how asynchronous work starts and ends. Distinguish memory, persistence, network, and process boundaries.
3. Anchor key invariants in code or tests. Cover errors, cancellation, and cleanup. Leave untraceable dynamic behavior unknown instead of filling diagrams with guesses.
4. Lead with the subsystem's role, then use a concrete request to connect mechanisms, tradeoffs, and boundaries a change must preserve. Separate source evidence from execution results. Check that each citation supports the adjacent claim.

Read [exploration](references/exploration.md) for multiple modules, dynamic routing, or coverage checks; read [explanation](references/explanation.md) when organizing a long explanation. Reuse existing findings and recheck only relevant facts when the version changes.

The primary agent works by default. Delegate only when independent investigation or review offers a concrete benefit worth the additional token cost and the current host permits it. Specify the inputs, required evidence, scope, and stopping point. Verify returned artifacts and report omissions. Complexity or tool availability alone does not justify spawning subagents. If the volume of material makes the delegation tradeoff unclear, locate figure-it-out and read only [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation).

Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver the mechanism, evidence, and unknowns. Check at least one actual entry-to-result chain. An explanation alone does not authorize starting the application, creating scripts, or fixing issues; experiments must fall within the current authorization.
