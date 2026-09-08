# Evidence standards

Code reading establishes an implementation path. Compilation establishes type or build constraints. Execution establishes behavior for specified inputs and a specified version. A real user path and observed side effects support the corresponding feature's usability. Stronger evidence still does not cover untested environments automatically.

Record the version, initial state, input actions, results, and evidence paths. A final screenshot alone does not prove the action chain. Capture the actions and visible results; also verify side effects involving files, data, or external messages. Internal setters, direct database writes, and test-only endpoints must not stand in for user actions.

Mocks establish behavior only within the isolated boundary. Observe what a dry-run actually skips; its name does not guarantee no network traffic or writes. Mark unauthorized real external side effects as unverified rather than expanding permissions.

Agent summaries are not proof. Spot-check actual files, command exit codes, and raw evidence. Failures and unexercised paths cannot count as passes. Store evidence outside cleanup directories and read or validate it after cleanup. Retain only sensitive material needed for the current verification, and check disclosure scope before linking it in a report.
