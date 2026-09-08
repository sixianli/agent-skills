---
name: architect
description: "Design types, interfaces, ownership, and module boundaries from caller usage, data, and invariants. Use for explicit design requests or necessary structural tradeoffs; stop after a design-only request rather than implementing automatically."
---

# architect

Start with requirements, caller goals, and current constraints. For an existing system, reuse findings or discover [how](../how/SKILL.md). Use [why](../why/SKILL.md) when historical compatibility constraints matter. Do not repeat investigation already supported by reliable evidence.

1. Write how users and maintainers accomplish the task before deriving types, signatures, and module boundaries. Model real relationships and states rather than hiding mutual exclusion in bags of optional fields.
2. Establish data sources, ownership, and necessary dependencies. Parse external inputs at explicit boundaries and maintain explainable internal invariants. When a new constraint appears, ask how the system would have been designed with that constraint from day one; this does not expand refactoring authorization.
3. Compare genuinely different, viable options and their costs for material unresolved tradeoffs. Do not require a fixed number of candidates or multiple designs merely because code crosses function boundaries. Assess the effort to understand and coordinate the design, not file length or layer count.
4. For side effects, explain results after repetition, cancellation, and interruption. For concurrent writes, first decide whether sharing is necessary. Separate ownership where possible; use explicit serialization for genuinely shared state.
5. Deliver an implementable sketch, invariants, interfaces, tradeoffs, risks, and the first verifiable step, using the [design template](references/design-template.md) as needed. Stop here for a design request. Continue implementation or refactoring only within existing authorization; a completed sketch does not authorize product code changes.

Read [boundaries](references/design-review.md#boundaries), [alternatives](references/design-review.md#alternatives), [complexity](references/design-review.md#complexity), [domain modeling](references/design-review.md#domain-modeling), [repetition and interruption](references/design-review.md#repetition-and-interruption), or [shared state](references/design-review.md#shared-state) as needed, not all at once.

The primary agent can compare options directly. Delegate under host rules only when independent review of a significant unresolved tradeoff is worth its cost. Supply the original requirements and constraints and verify the results. Use discovered [interrogate](../interrogate/SKILL.md) for actual disputes, without depending on a competition platform.

Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

Check that the caller-to-result contract is complete and unverified assumptions are explicit. Scaffolding and pseudocode do not mean implementation is complete.
