# Create and confirm a record

In this fictional Records app, a user creates a record from the browser or CLI, cancels an unfinished draft, and checks saved data from the list. This is a worked writing example, not an executable skill or a completed verification. Every command and observation below is illustrative and must be replaced with the actual project's supported behavior and execution evidence.

## Sub-features

- `record-open`: Open creation from the toolbar and keyboard shortcut.
- `record-save`: Save a title and body and confirm persisted values after reopening.
- `record-cancel`: Discard a draft without creating a record.
- `record-cli`: Create and read a record through the CLI.
- `record-filter`: Distinguish a completed empty result from unavailable search, then restore the list.

## How to get to it (user POV)

- Choose the `New record` toolbar button from the Records list.
- Press `n` from the list while focus is outside editable fields.
- Run the Records CLI create command against the same owned data directory.
- Use the list's `Filter records` searchbox to find a saved item or prove its absence.

## Driving it with control-records

Preconditions: use the shared baseline in [the index](README.md#baseline-preconditions). The fictional harness has already been configured with this run's target and data directory. Doctor has confirmed that target. Each independent recipe below starts from the baseline; within a recipe, steps run in order. The commands show the form of an exact recipe, not tools to install or execute here.

**Toolbar creation and persistence (`record-open`, `record-save`; entrypoint `toolbar`)**

| User action | Illustrative exact command | Observable result to require |
|---|---|---|
| Open creation | `control-records browser click --role button --name "New record"` | `Record editor` appears and the Title textbox has focus. |
| Enter title | `control-records browser fill --role textbox --name "Title" --value "Release checklist"` | The Title textbox displays the entered title. |
| Enter body | `control-records browser fill --role textbox --name "Body" --value "Tag and publish"` | The Body textbox displays the text and Save record is enabled. |
| Save | `control-records browser click --role button --name "Save record"` | A `Record saved` status appears. This alone is not persistence proof. |
| Return to list | `control-records browser click --role link --name "All records"` | The list contains Release checklist. |
| Reopen saved item | `control-records browser click --role link --name "Release checklist"` | The editor shows both stored values, independently of the old draft. |

Retain the action transcript and capture the reopened state with `control-records browser snapshot --aria --path artifacts/record-save/toolbar/reopened.aria.txt` and `control-records browser screenshot --path artifacts/record-save/toolbar/reopened.png`. The artifacts identify the app and stored values. Through the documented Delete record action, remove only this run's Release checklist; return to the unfiltered list and require the baseline Budget memo to remain. In this fictional recipe that action is `control-records browser click --role button --name "Delete record"` followed by `control-records browser click --role button --name "Confirm delete"`. If the real app uses another cleanup method, document and verify it instead.

**Keyboard entry and cancellation (`record-open`, `record-cancel`; entrypoint `keyboard`)**

Start from the baseline list with focus outside an editable field. Run `control-records browser press --key "n"`; require the same Record editor and Title focus as the toolbar entry. Run `control-records browser fill --role textbox --name "Title" --value "Discard me"`, then `control-records browser click --role button --name "Cancel"`. Require return to the list without a Discard me link. Prove absence through the completed filter result described below, preserving this recipe's actions and resulting state under `artifacts/record-cancel/keyboard/`. Cancellation does not prove that saving through the keyboard entry works; that combination remains unexecuted until separately exercised.

**CLI creation and readback (`record-cli`; entrypoint `cli`)**

Run `control-records cli -- records create --title "CLI checklist" --body "From terminal" --format json`. Retain the exact command, stdout, stderr and exit code under `artifacts/record-cli/cli/`; require exit 0 and a new record ID with the expected title. Run `control-records cli -- records list --title "CLI checklist" --format json` as a second read-only view; require exactly one stored record with the expected title and body. Then run `control-records cli -- records delete --title "CLI checklist" --exact --format json` and repeat the list command; require an empty array with exit 0. Run `control-records cli -- records list --format json` and require exactly the unchanged Budget memo baseline record. This example assumes exact-title deletion is supported and the initial absence was established; use the actual project's run-owned ID when titles cannot identify ownership safely.

**Completed empty result and state restoration (`record-filter`; entrypoint `list-filter`)**

From the list, run `control-records browser fill --role searchbox --name "Filter records" --value "Discard me"`, then `control-records browser wait --role status --name "No matching records"`. Require the loading state to end and that explicit completed-empty status to appear. An unavailable-search error, absent result container or timeout is not an empty result. Capture the action, query and status with `control-records browser snapshot --aria --path artifacts/record-filter/list-filter/empty.aria.txt` and `control-records browser screenshot --path artifacts/record-filter/list-filter/empty.png`. When used to prove cancellation, retain the corresponding proof under the cancellation recipe's artifact path too. Run `control-records browser click --role button --name "Clear filter"`; require an empty searchbox and the unfiltered list containing Budget memo.

These recipes demonstrate entrypoint-specific proof and do not claim all combinations were exercised. A generated map records the actual verdict for each path, its artifacts, and any attempts and blockers. An unavailable CLI does not inherit the browser's pass.

## Gotchas

- Pressing `n` in an editable field types a character; establish focus before testing the shortcut.
- A saved notification or create response can echo draft input; reopen or query the stored record before claiming persistence.
- Filtering may debounce. Wait for a result or completed-empty state, not a fixed sleep; diagnose errors and timeouts before proceeding.
- Navigation and dialogs change the starting state. Restore the known list state between recipes and rerun Doctor after failures or surprises. If recovery is unsafe, report the affected paths as blocked.
- Remove only records created by this run and restore the known fixture state. Preserve and read back evidence after final cleanup, including evidence from failed iterations.
