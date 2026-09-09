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

## Structural safeguards

When a correction recurs or the same instruction must be repeated, identify the common failure, its trigger, and the boundary that can prevent it. Implement the strongest suitable mechanism: make the invalid state unrepresentable where practical, otherwise use a lint rule or prohibited API check, a canonical helper, a runtime check, or a deterministic verification script. Reuse the established mechanism and make the correct path easy to follow; do not scatter equivalent checks everywhere.

Capture an example of the observed failure and a valid case. Verify that the safeguard detects or prevents the failure and still permits the valid case. Name its maintenance owner and connect it to the existing build, test, or runtime path so it actually runs. Generating an unused script or merely proposing a lint rule does not complete this step.

Remove only redundant task-owned instructions made obsolete by the verified mechanism; retain explanations of non-obvious intent and external constraints. If judgment cannot be encoded reliably, strengthen the relevant task guidance with a concrete failure example and report this as a documented limit, not an enforced guarantee. One-off incidents do not automatically warrant permanent machinery.

Record the correction, mechanism, evidence, and remaining limitations in the run's decision trail. Apply the task's safeguards directly without a separate approval request or a full reflect workflow. Do not turn this into unrelated cleanup or personal-memory maintenance. If host controls block implementation or execution, report the concrete blocker and the unverified result rather than claiming prevention.
