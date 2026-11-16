# Runbook Governance and Execution Workflow

Use this reference whenever creating, reconciling, checking, using,
snapshotting, superseding, or retiring a Runbook. A Runbook is an operational
procedure, not an authorization token.

## Trust Model

An active Runbook is usable only after it proves both of these facts for the
current execution:

1. the executing agent has read the repository sources named in its
   `Authoritative Sources` as they are now and found the procedure consistent
   with them; and
2. a fresh, target-read-only Live-State Preflight matches its safety
   assumptions.

`status: active` is necessary but is never sufficient. A passing structure
check proves neither consistency with current sources nor live applicability,
and does not authorize production, deletion, restore, migration, paid calls,
provider/model changes, identity changes, or any other external mutation.

Runbooks do not use `last_reviewed`, `review_after`, periodic review windows,
or refreshed dates as a trust signal. The common `date` field is document
metadata only. Idea and Backlog review fields are a separate workflow and are
not affected by this rule.

## Active Runbook Structure

Every active Runbook under `docs/runbooks/` must set `execution_risk` to one
of `standard`, `high`, or `critical`. For example, a production Runbook uses:

```yaml
status: active
document_type: runbook
execution_risk: critical
```

Its `Authoritative Sources` section lists the repository files and protected
configuration the procedure depends on. The executing agent reads them before
every use.

It must contain exactly one of each of these ten required level-two headings:

- `Scope`
- `Authoritative Sources`
- `Safety and Preconditions`
- `Live-State Preflight`
- `Procedure`
- `Verification`
- `Evidence`
- `Rollback`
- `Stop Conditions`
- `Troubleshooting`

The validator proves structure, not operational correctness. Reconcile the
meaning against current code, configuration, tests, protected inputs, and live
readback before execution.

A Runbook written under an earlier version of this skill may still carry a
`contract_sha256` field and a `<!-- runbook-contract: -->` block. Both are
ignored. Move any path the block lists into `Authoritative Sources` and remove
the field and the block the next time the Runbook is edited.

## Execution Risk Is a Protection Floor

`execution_risk` describes the highest plausible consequence of the written
mutation steps, not document quality:

| Value | Typical consequences | Mutation gate |
| --- | --- | --- |
| `critical` | production, deletion/restore, migration, identity or security boundaries, real secrets, paid model/provider changes, release pointers, shared hosts | Target-read-only preflight may run first. Immediately before the first target mutation, report the exact target, action, risk, cost, and side effects and obtain explicit authorization for that action. |
| `high` | staging, shared infrastructure, or other non-production external side effects | Require authorization that accurately covers the target and action, fresh preflight, isolated evidence, rollback, and stop conditions. Do not repeat a confirmation when the current request already covers them precisely. |
| `standard` | local, read-only, or directly recoverable work | Still run the static check and applicable preflight. A current explicit request can cover local recoverable writes. |

The effective risk is the highest of the declared value, the actual commands
and effects, and the target identified by live preflight. Unknown or unreliable
classification is `critical`. A declaration can only raise protection; it can
never lower risk inferred from commands or the target.

Static tools validate only the declared field. At execution time the agent must
apply the higher actual risk. For a target-read-only preflight, no target
mutation authorization is requested merely because the Runbook is critical.
At the mutation boundary, critical work always requires immediate, action- and
target-specific authorization.

`runbook.py check` does not infer risk from shell commands, prose, or a live
target, and a successful structure check must never be treated as a risk decision.
Before any mutation, the executing agent must independently classify the actual
commands and effects plus the target discovered by preflight. It then applies
the highest of those classifications and the declared floor through the
authorization policy below. If any classification is unknown or unreliable,
use `critical`.

The mutation boundary is the first action that changes the governed target,
external system, data, permissions, billing, provider/model identity, or
runtime state. Writing bounded, redacted preflight records into an already
approved, protected, per-run evidence directory is evidence bookkeeping, not a
target mutation. It must remain isolated and must not change the governed
target.

## Reconciliation

Reconcile a Runbook because of an event that can change operational truth,
never because of a date:

- create or materially edit a Runbook;
- change a repository source named in its `Authoritative Sources`;
- find live identity, version, configuration, or safety assumptions that do
  not match;
- change an external contract the Runbook depends on;
- learn from a failure, incident, stop, or rollback that the procedure is
  incomplete.

Inspect the relevant diff and current facts, correct the Runbook, and run the
relevant tests in the same change set. Then run:

```text
runbook.py check ROOT RUNBOOK
```

No tool records that reconciliation happened. A Runbook that was not
reconciled after such an event is caught at its next use by the per-execution
gate, which reads the current sources again.

A procedure that is always run the same way is better turned into a tested
script. Keep the Runbook for the judgment the script cannot make: when to run
it, the preflight, the stop conditions, and the rollback.

## Per-Execution Gate

For every actual use, in this order:

1. Confirm the entry is under `docs/runbooks/` and has `status: active`. If the
   supplied entry is archived or superseded, stop. When it names exactly one
   repository-valid `superseded_by` candidate, report that candidate as the
   possible active entry, but never follow or execute it automatically; a user
   who chooses it must begin again at gate 1.
2. Run `runbook.py check ROOT RUNBOOK` and stop on every finding.
3. Read the current Git HEAD, worktree state, every source named in
   `Authoritative Sources`, and protected configuration. Compare the procedure
   with them and stop when a step, path, command, or assumption no longer
   matches; reconcile the Runbook before continuing. Do not reuse a cached
   conclusion from another task.
4. Run only the target-read-only `Live-State Preflight`. Read back the exact
   host/environment, account, workspace/tenant, privileges, deployed version
   or image digest, release/source identity, configuration, model/provider,
   mounts, network and resources, backups, locks, health, protections, and
   rollback prerequisites that apply.
5. Stop if access is unavailable, evidence is incomplete, identity is
   ambiguous, or any readback conflicts with the Runbook.
6. Compute effective risk from declaration, commands/effects, and live target.
   Report the exact target, action, risk, cost, and side effects. Apply the
   corresponding mutation authorization gate.
7. Execute bounded steps without silently changing provider, widening scope,
   or bypassing a stop condition.
8. Verify the result and close the isolated evidence record.

If the Runbook, sources, worktree, or live target changes after its gate, rerun
the affected gate. Archived and superseded Runbooks are historical evidence
and are never executable.

## Evidence, Stop, and Rollback

The `Evidence` section defines a project-approved protected evidence root and
a unique run ID. Critical and high executions use a new isolated directory;
never reuse a prior run. If the project does not provide an approved root,
fail closed rather than inventing a personal host path.

Preserve redacted structure-check results, target identity and preflight, actual
commands and exit status, verification, stop/rollback state, and final
conclusion. Do not record tokens, passwords, private keys, raw environment
files, or unredacted secret-bearing command output. Raw evidence does not
belong in a Runbook, Idea, Backlog, `docs/lessons.md`, or chat. Chat reports
only the necessary conclusion and protected evidence path.

Every Runbook names conditions that stop execution before further attempts and
defines bounded rollback prerequisites and verification. Do not promise a
rollback that has not been proven available by live readback.

## Snapshot, Supersession, and Retirement

`docs/runbooks/` contains only active stable entry paths.
`docs/archive/runbooks/` contains `status: archived` history. New archive files
are dated; unique legacy undated files remain readable for compatibility.

Use only these mutually exclusive archive operations:

```text
archive_doc.py ROOT RUNBOOK --snapshot --archive-date YYYY-MM-DD [--dry-run]
archive_doc.py ROOT RUNBOOK --superseded-by ACTIVE_PATH --archive-date YYYY-MM-DD [--dry-run]
archive_doc.py ROOT RUNBOOK --retire --reason TEXT --archive-date YYYY-MM-DD [--dry-run]
```

- Snapshot copies the current stable entry to a dated archive, makes that
  archive its direct predecessor, and keeps the stable path active for the
  forthcoming major revision.
- Supersession moves the old Runbook to archive and adds reciprocal lineage to
  a distinct active successor.
- Retirement moves it to archive with a one-line `archive_reason` and no
  successor.

The tool validates every path, lifecycle, target, conflict, and existing
reverse link before writing. It uses same-directory atomic file replacement
plus compensating restoration for ordinary process-level failures; multiple
filesystem writes cannot provide database-level crash atomicity.

Existing archives are never checked against current sources.
