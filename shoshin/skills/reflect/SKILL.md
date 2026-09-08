---
name: reflect
description: "When the user requests a retrospective on the current task, distinguish execution mistakes, skill defects, opportunities for structural safeguards, and one-off issues. Propose evidence-based improvements without mining unrelated history or writing memory automatically."
---

# reflect

Use only the current work or evidence explicitly selected by the user. Work from visible events, artifacts, and a reliable locator for the current task. If raw records are unavailable, state the scope; do not scan other tasks as a substitute.

1. Identify actual errors or friction and their consequences, and verify the corresponding artifacts. One-off incidents and generic advice do not automatically become lasting rules.
2. Distinguish execution mistakes, insufficient skill guidance, enforceable constraints, and one-off issues. If an existing rule was clear but ignored, improve execution rather than adding duplicate text. For recurring failures, read [mechanism selection](references/reflection-criteria.md#mechanism-selection).
3. Give each proposal evidence, a cause, an owner, and a concrete change. Explain rejected proposals. Where types, checks, or tools can reliably enforce a constraint, evaluate that mechanism first; not every preference belongs in lint.
4. Apply only changes already authorized. A retrospective request alone yields proposals; it does not authorize editing skills, configuration, or memory, or filing external issues. For authorized substantive skill changes, use discovered skill-creator and check the resulting behavior.

Reflect directly by default. Delegate under host rules only when large material or independent questions offer a clear benefit worth the cost, and verify all proposals. For details, read only figure-it-out's [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver recommended improvements, reasons for rejecting others, and changes actually applied, if authorized. This skill does not organize personal preferences across conversations or present a proposal as a completed fix.
