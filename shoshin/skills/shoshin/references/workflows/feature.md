# Feature implementation

Understand existing user paths and data contracts. State the new observable behavior, failure results, and compatibility requirements. Implement directly when the existing design is sufficient. Use architect only for real structural tradeoffs, preserving the user's stopping point.

Before implementing new or changed state, data structures or ownership, name the intended representation, its owner and key invariants, including invalid combinations and side-effect boundaries where relevant. Reuse an adequate existing model. This short contract does not require a full architecture review; use architect when a material unresolved tradeoff needs it.

Implement and verify in dependency order, with one owner for shared contracts. The primary agent writes code by default. Delegation of independent artifacts needs a concrete benefit and explicit write boundaries. Verify inputs, state, and side effects through real user paths and identify untested environments separately. Do not automatically proceed to a PR or continuous delivery.
