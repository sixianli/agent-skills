# Feature map example

This illustrates a fictional Records app; it is not an executable verification skill or evidence of an actual run. The `control-records` harness and all commands in the worked example are illustrative, not shipped tools. During generation, inspect the real project's commands and selectors and replace examples with verified paths. Do not generate an entry if the feature does not exist.

The generated map is the maintained source for user-facing verification. Tell its reader to read the index before driving, then follow the matching feature file.

## Baseline preconditions

Record the actual launch contract, expected build, address or executable, authentication when needed, and run-owned data directory. Define the shared fixture state and how to establish it through the project's supported setup. Run Doctor to check the expected target and state before driving; diagnosis does not perform setup or repair.

For the fictional example, assume an owned, healthy Records instance and disposable data containing exactly one record, `Budget memo`, with body `Draft budget`. No `Release checklist`, `CLI checklist` or `Discard me` record exists. The Records list is visible, no modal is open and no filter is active. Both the browser and CLI use the same owned data directory. Evidence lives outside that directory. These are teaching assumptions, not verified project facts.

## Driving conventions

- Start each recipe from the shared baseline unless its own preconditions state otherwise. Establish required fixtures explicitly; do not depend on another recipe having run.
- Use the selected harness and exact documented commands, including quoting and flags. Prefer stable semantic handles to coordinates and tab order.
- Wait for meaningful state changes, including completion of asynchronous work. A delay alone does not prove readiness.
- Restore owned fixture data and UI state after mutations or navigation. Preserve evidence and avoid modifying unrelated user state. If safe recovery is unavailable, stop the affected path and report the blocker.

## Evidence and skip reporting

- Carry the applicable evidence rules into the target skill, in its body or a bundled reference with an explicit read instruction; do not leave them available only in the generator.
- Capture action and result. Use semantic snapshots and screenshots for UI where supported, and command, stdout, stderr and exit code for CLI. Check mutations through a read-only second view of stored state.
- Attach the feature/sub-feature ID and entrypoint to each artifact, using filenames or a manifest. Preserve evidence through teardown and verify it can still be read.
- Distinguish passed, failed, unexecuted and blocked paths. For unreachable paths, record attempted commands or tool calls and the unmet precondition. Do not invent an attempt for an unexecuted path or transfer another entrypoint's pass to it.

## Feature entry contract

Each file begins with a title and a short account of the user-visible behavior, then uses these four sections:

1. **Sub-features:** Short IDs and the behaviors they identify.
2. **How to get to it (user POV):** Every identified user entrypoint within scope, including applicable permissions and focus or navigation conditions.
3. **Driving it with the selected harness:** Preconditions, followed by steps pairing user action, exact command or tool call and observable result. Record inputs, side effects and evidence status.
4. **Gotchas:** Conditions that invalidate proof, recovery, cleanup and concrete blockers.

Keep implementation internals out of the user recipe. Source anchors may establish discovery and coverage, but must not replace executable user steps. Include cancellation, negative or empty states and persistence checks when supported by the actual feature, not as invented product requirements.

## Features

| Feature | User entrypoint | Verification guide |
|---|---|---|
| Create and confirm a record | Toolbar, keyboard shortcut, CLI; list filter for confirmation | [Create a record](create-record.md) |

The target project's map lists the entire identified scope, not a fixed three to five features. Consistency among existing files does not establish that no features are missing.
