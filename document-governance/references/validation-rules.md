# Validation Rules

Read this file before running, interpreting, or modifying
`scripts/validate_docs.py`.

## Modes

The validator defaults to migration-friendly mode. Structural adoption issues
are warnings so an existing repository can be assessed without immediately
blocking all work.

- `--strict` (alias `--ci`) promotes every migration-friendly warning to an
  error and returns a nonzero exit code. Use it for governed repositories, CI,
  and completion checks.
- `--format=json` emits one JSON object without changing exit behavior.

## Always-Error Checks

These conditions fail in every mode:

- `status` is present but is not `active`, `superseded`, or `archived`.
- An archived document has `status: active`.
- An active Spec or Plan has `status: archived`.
- A local SOURCE target is absolute or contains `..` path traversal.
- The supplied project root does not exist or is not a directory.

## Migration Warnings / Strict Errors

- A required governance directory is missing.
- `docs/tracking/ideas/` and `docs/tracking/backlog/` are created on first use;
  empty optional directories are not required because Git does not preserve
  them.
- A governed Markdown document has missing, unterminated, malformed, nested,
  duplicate, or multiline frontmatter.
- Frontmatter lacks `status`, `supersedes`, `superseded_by`, or `date`.
- A document in archive is not marked `status: archived`.
- An active Spec or Plan is marked `status: superseded` instead of being
  closed and archived.
- A `document_type`, when present, conflicts with the document's governed
  directory.
- A Tracking Ledger contains Plan-like headings such as `## File Boundaries`,
  `## Implementation Tasks`, `## Verification`, or `### Task ...`.
- A structured Idea/Backlog record has a missing, duplicate, malformed, or
  path-inconsistent `tracking_id`, `tracking_kind`, or `tracking_state`.
- A promoted/converted record lacks a valid `promoted_to`; a deferred Backlog
  lacks `review_after` or `reason`; or a terminal record lacks its required
  result, reason, or successor.
- An ADR lacks `decision_status`, uses an invalid decision status, or has
  inconsistent `status`, `decision_status`, and supersession links.
- A Plan lacks a Source Spec section or SOURCE reference.
- A SOURCE target does not exist under `docs/`.

Strict mode must leave these findings in `errors`, not `warnings`; a strict run
with any such finding must report `ok: false` and return exit code 1.

## SOURCE Resolution

- Resolve `docs/...` from the project root.
- Resolve paths without the `docs/` prefix from the project `docs/` directory.
- Never fall back to a same-named file at the project root.
- Recognize active Spec/Plan paths whose files moved to the corresponding
  archive directory.
- Recognize legacy ADR paths whose files already live in `docs/archive/adr/`,
  but do not archive ADRs going forward.
- Skip external HTTP(S) URLs and explicit template placeholders after enforcing
  local path-boundary rules.
- Do not validate heading anchors.

## Files Considered

- Scan all `*.md` files under the target project's `docs/` tree.
- Skip `docs/templates/**` because it may contain unfilled placeholders.
- Do not scan the skill's own `assets/templates/**` when validating a project.
- Treat any remaining `docs/ideas/` directory as an always-error condition.
  The integrated workflow has no legacy reader or compatibility mode.
- Open records and overdue `review_after` dates are work state, not validation
  failures. Use `scripts/tracking.py review` to surface them.

## What the Validator Cannot Prove

The validator cannot prove semantic consistency between code and prose,
confirm that a Spec matches its Plan, determine whether a code change required
a PRD update, or prove that work is truly closed. Inspect repository evidence
and complete the workflow checklist before declaring semantic or release
readiness.
