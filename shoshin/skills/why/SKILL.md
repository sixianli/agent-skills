---
name: why
description: "Trace design rationale, historical tradeoffs, regressions, and the origins of thresholds while separating direct evidence from inference. Use how for current mechanisms; do not scan unrelated history automatically."
---

# why

Start with a design question and a code anchor. Investigate only relevant, accessible sources and remain read-only.

1. Locate the file, symbols, and target lines. Read recent relevant commits, then trace blame, renames, the introducing commit, and its parent version to the original change. The last edit to a line may not be the original decision.
2. Discover relevant PRs, ADRs, issues, or available connectors from those anchors. Stop if one commit answers the question. Do not require seven source categories, enable write access, or add a connection merely to query it.
3. Classify each material conclusion as Direct, Supported, Inferred, Speculative, or Unknown using the [evidence levels](references/evidence-levels.md). Current code can explain an effect; it cannot by itself establish the author's motivation.
4. For conflicting accounts, preserve dates, applicability, and competing explanations. Use [source investigation](references/source-investigation.md) to choose the smallest next check that distinguishes them. Distinguish inaccessible sources, searches with no results, and sources not searched.

The primary agent works by default. Delegate only when independent investigation or review offers a concrete benefit worth the additional token cost and the current host permits it. Specify the inputs, required evidence, scope, and stopping point. Verify returned artifacts and report omissions. Complexity or tool availability alone does not justify spawning subagents. For detailed cost decisions in a multi-source investigation, locate figure-it-out and read only [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver supported rationale, inferences, competing explanations, and gaps. If a change will follow, summarize constraints as Preserve, Change, Avoid, and Risk. Check citations and confidence language; a recent commit must not erase earlier contradictory evidence.
