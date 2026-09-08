# Impact review

Work backward from changed values to their consumers. JSON keys, database columns, URLs, event names, and configuration names may have no function-call relationship. Check whether deletions or renames change an external protocol and whether readers ship on separate version schedules.

For asynchronous operations, map creation, queueing, execution, cancellation, and destruction. Check whether callbacks can outlive their owner. For caches, inspect keys, invalidation, and persistence. For third-party APIs, check the pinned version and local patches.

Every risk must describe a concrete failing path. Severity depends on actual trigger conditions and harm, not diff size or whether a sensitive module is touched. Evidence clearing a risk must show why the failing path is unreachable. For unknowns, retain the smallest executable check.
