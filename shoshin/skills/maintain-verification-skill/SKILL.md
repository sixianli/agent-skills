---
name: maintain-verification-skill
description: "Maintain an existing project verification skill and feature map through bidirectional source checks and real user paths. Correct documentation and helpers; report product regressions without automatically creating a PR."
---

# maintain-verification-skill

Locate the target project's `.agents/skills/verify-*/SKILL.md` or the user-supplied path. Resolve multiple candidates before proceeding. If none exists, point to create-verification-skill rather than inventing a maintenance target.

Edit only the target verification skill's own SKILL.md, features, and helpers. Do not change product implementation or rewrite a product regression as the new correct behavior.

1. Read the map and feature files. Fix duplicates, broken links, and missing index entries. Then check both directions: map → source verifies each description; source → map identifies missing features from actual routes, menus, commands, and recent changes. Establish the Git baseline and scope first. Without a trustworthy baseline, inspect current entrypoints and state the limits of historical coverage. Every new entry needs a concrete source anchor. A consistent index does not prove complete coverage.
2. Identify prerequisites and controls for each feature, reusing controllable states where possible. Investigate source directly by default. Delegate only when independent feature groups are large enough to justify the token cost and the host permits it. Require evidence and gaps; do not mechanically assign one agent per feature.
3. One operator controls the shared application. Start it according to its Launch contract. Run Doctor before the first Drive and in every new session. After any failure or unexpected behavior, diagnose again before the next Drive.
4. A healthy process does not mean a usable interface. Restore a known state after leftover modals, hangs, or error pages. If needed, restart only an owned instance you are authorized to control. Do not restart existing user instances or delete user data. If recovery is unsafe, stop the affected verification and report the blocker to avoid cascading false reports.
5. If skill drift causes Doctor to fail, correct it within the allowed edit scope and retry once. Restart only owned resources invalidated by that correction. If it still fails, report blocked. After recovery, retry the affected path with valid prerequisites before distinguishing helper defects from product regressions.
6. Exercise every mapped feature. For unreachable features, record concrete prerequisites such as permissions, accounts, or platform, and the route attempted; do not mark them passed. Incomplete coverage remains incomplete. Report documentation drift, helper defects, and product regressions separately. Rerun affected paths after helper changes.
7. Clean up resources created by the run after each failed iteration and at the end. Startup and cleanup must be repeatably verifiable. Recovery and cleanup must not delete evidence; verify that it survives cleanup.

To assess evidence strength, discover create-verification-skill and read only [evidence standards](../create-verification-skill/references/evidence-standards.md). For complex retries, read only architect's [repetition and interruption](../architect/references/design-review.md#repetition-and-interruption). For dividing large investigations, read only figure-it-out's [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Report clean / changed / blocked, source and execution results for each feature, and locations of changes and evidence. changed means only that the local verification skill was corrected and affected paths were exercised; it does not imply a push or release.
