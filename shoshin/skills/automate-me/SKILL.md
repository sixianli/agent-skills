---
name: automate-me
description: "Extract stable working preferences from user-selected material across conversations and propose rule improvements. Distinguish one-off instructions and project constraints; do not scan history, create personal modes, or write configuration automatically."
---

# automate-me

Inputs must be accessible cross-conversation material explicitly selected by the user and existing rules. If historical access is unavailable, use supplied material and state coverage. Do not guess past preferences.

1. Retain each candidate preference's original wording, source location, date, project, and scope. Distinguish stable preferences, one-off instructions, project constraints, and conflicts. See [preference review](references/preference-review.md).
2. Compare existing global instructions, project rules, and skills. Reuse the existing location when it already expresses the preference accurately. Do not generate a handle-mode by default or invent a skill because a topic recurs.
3. Propose evidence-based replacement text, its target location, and affected scope. Unresolved conflicts need a user decision; frequency cannot override a more explicit or more recent qualifying instruction.
4. Apply changes only with actual authorization. Recommendations do not authorize memory, configuration, or external writes. Use discovered skill-creator when authoring a skill. Cross-conversation preference review does not execute the current project's tasks or schedule automation.

The primary agent handles small inputs directly. Delegate large, self-contained excerpts only when the analysis benefit justifies extra tokens and the host permits it. The primary agent checks conflicts across excerpts. For details, read only figure-it-out's [context and delegation](../figure-it-out/references/execution-methods.md#context-and-delegation). Read reflect's [mechanism selection](../reflect/references/reflection-criteria.md#mechanism-selection) only when a proposal concerns mechanisms for recurring engineering mistakes; do not run its entire current-task retrospective.

Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Deliver candidate preferences, evidence, conflicts, existing locations, concrete proposals, and reasons for rejecting others. Do not generalize a one-off request into a global habit or claim to have searched unavailable history.
