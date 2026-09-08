# Refactoring

Establish the current behavior using valid existing tests or representative inputs and outputs. Type checking alone does not prove behavioral equivalence. Define the target structure and user-approved scope. Preserve the record of existing defects rather than mixing fixes into a behavior-preserving task.

## Caller migration

For an authorized complete internal API migration, inspect actual callers, serialized names, dynamic registration, configuration, and documentation references. Migrate and verify callers in batches, then remove unused old interfaces. Do not remove external compatibility contracts without a decision or keep old paths indefinitely for imagined consumers.

Remove only confirmed redundancy within scope. Make small changes and keep behavior checks passing after each step. Compare direct edits with scripting before a mechanical batch change. Discover figure-it-out and read only the Tool selection section of references/execution-methods.md for details. Keep new structure because it reduces actual comprehension and coordination costs, not because the diff is smaller.

Deliver structural changes and before/after equivalence evidence, stating limits when a baseline is missing. Do not rebase, create branches, or change external interfaces without authorization.
