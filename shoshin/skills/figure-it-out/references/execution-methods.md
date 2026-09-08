# Execution methods

## Premise review

When two fixes based on the same premise fail, write down that premise, the expected observation, and actual counterexamples. Check whether the instrumentation reaches the real path. Distinguish invalid inputs, observation errors, and system behavior. Choose a next check that separates competing explanations instead of accumulating compatibility branches.

For imbalances in resources or work distribution, measure each actor's share to determine whether fixed roles create skew. Reject that hypothesis if the distribution is uniform. This method does not apply to every defect; do not require an unrelated census.

## Tool selection

Work through one representative sample to understand the transformation. Write a script or codemod when the operation repeats and the same check can be rerun. Verify the output against the sample before expanding scope. Bound tool inputs and outputs, make failures visible, and preserve existing user content. Two clear one-off edits do not need tooling.

## Context and delegation

Compare sequential work by the primary agent, tool filtering or batched queries, and subagents. Identify whether the benefit is coverage, independent discovery, less noise in the main context, or reduced waiting time; using multiple agents is not itself a benefit. Keep work in the main context when it depends closely on the same changing state, is small, or requires frequent back-and-forth.

Self-contained investigations, large traces that still need substantial interpretation after filtering, and important independent reviews can benefit. Delegate only when those benefits justify total extra tokens, context reconstruction, and verification costs, and current host rules permit it. Inherit the effective model by default rather than prescribing model tables or agent counts.

Provide the task, actual input version, necessary constraints, permitted write scope, expected artifacts and evidence, coverage ceiling, and stopping point. Different agents do not automatically have isolated filesystems. One owner edits shared contracts, and one operator controls a shared application. Role prompts do not create permission isolation.

The primary agent spot-checks raw evidence, especially boundary connections. Stop reviews that add no new information instead of spawning indefinitely. Record usage as unavailable when it cannot be observed; a short summary does not prove lower total token use. Independent contexts are not independence across model families.

## Phase acceptance

Each unit has fixed inputs, artifacts, and a checkable result. Verify it before layering on another change. An explicitly approved migration design may permit temporarily incomplete states, with their impact, dependencies, and recovery path recorded. Ordinary refactoring does not thereby gain permission to break behavior.

Classify phase results as verified, unverified, or inconclusive. Check the user's original criteria individually at the end and leave unmet items open. Record executable checks, manual review, and real operations as distinct evidence. Use the existing lifecycle for governed plans rather than duplicating PR counts, fixed model-validation tracks, or state indexes.
