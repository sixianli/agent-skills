# Feature implementation

Understand existing user paths and data contracts. State the new observable behavior, failure results, and compatibility requirements. Implement directly when the existing design is sufficient. Use architect only for real structural tradeoffs, preserving the user's stopping point.

Implement and verify in dependency order, with one owner for shared contracts. The primary agent writes code by default. Delegation of independent artifacts needs a concrete benefit and explicit write boundaries. Verify inputs, state, and side effects through real user paths and identify untested environments separately. Do not automatically proceed to a PR or continuous delivery.
