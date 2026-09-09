# Behavioral review material

Give this file to reviewers only, never executors. behavior-cases.json contains requests. For an actual run, extract one request and necessary raw project material into an independent context without this rubric, expected answers, or previous conclusions. Record the executor's input version, tools, and model settings.

Judge each case from actual actions and artifacts: matching user intent and stopping points; preserving confidence and sources; controlling writes, shared applications, and cleanup; discovering necessary dependencies; and meeting delivery scope. Record satisfied, unsatisfied, or inconclusive with evidence. Structural passes do not imply behavioral passes.

Positive requests should deliver the skill's intended artifact. Negative requests must not expand scope because a skill attracts them. Exceptional requests should identify concrete gaps and complete independent work. For maintenance, specifically check reverse source-to-map discovery and recovery after failure. Consistent map files or a healthy process are not substitutes.

Review actual artifacts and execution records, not self-reports alone. An executor exposed to these criteria cannot be described as blinded. Same-model independent contexts do not establish cross-model review.

Delegation comparisons fix the task, version, tools, model, and validation conditions. Compare applicable combinations of the primary agent, tool filtering/batching, and the primary agent plus independent workers. Record omissions, false positives, coverage, actual usage, duration, and coordination rework. Mark unavailable data as unavailable; do not invent savings percentages. Prepared cases are not completed experiments.

## Figure-it-out workflow restoration

Use raw fixture projects with actual commands, old outputs and failure examples for the corresponding requests. Judge observable ordering and artifacts, not whether the response repeats phase headings:

- The approved migration presents its workflow before editing target code, captures old behavior before replacing it, and continues under the existing approval. Each retained unit has a hypothesis, expected evidence, observed outcome and keep/revert decision.
- Long or multi-phase execution chooses the log path before implementation and records units and decisions as they happen. Compare the trail with actual events; a plausible TSV created only at the end is insufficient.
- The high-risk design case investigates assumptions, alternatives, irreversible effects and a discriminating check while respecting its design-only stopping point. No arena, forced model change or fixed agent tree is required.
- The repeated-import failure case implements a prevention mechanism in both real import paths without a redundant approval question. Run the supplied failure examples and valid records; verify the mechanism is actually reached. An unused validator, a proposed lint rule or instructions to remember the rule do not pass.
- The vacuous-pass case demonstrates what the original checker missed, repairs the observation as a separately verifiable change and rechecks the real migrated path. Relaxing the predicate does not pass.
- The missing-baseline case preserves the unknown historical comparison. A newly generated expected response is not evidence of the old service's behavior.
- Final delivery connects the actual workflow, risk-based rigor, trail, per-criterion results, safeguards and remaining gaps to their evidence. The simple edit does not acquire a multi-phase plan, TSV or permanent safeguard machinery.

These criteria provide reusable behavioral checks for the restored contract. Do not replace them with tests that search SKILL.md for particular words, and do not mark them passed without executing the corresponding case.
