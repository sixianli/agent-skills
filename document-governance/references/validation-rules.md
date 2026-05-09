# Validation Rules

Read this file before running or modifying `scripts/validate_docs.py`.
For invocation syntax see `SKILL.md` (the `Resolving the Skill Directory`
section). This file only documents what the validator checks.

## Modes

The validator runs in **default (migration-friendly)** mode unless told
otherwise. In default mode most structural problems are reported as
`WARNING` so the script can be introduced into existing projects without
forcing immediate rework.

- `--strict` (alias: `--ci`) — promotes legacy / soft warnings to errors.
  Use this in CI or when hardening a project.
- `--format=json` — emit a single JSON object instead of human-readable
  output. The exit code is unchanged. Suitable for piping into higher-level
  review agents.

## Always-Error Checks

These conditions always exit non-zero, even in default mode:

- `status` is set but is not one of `active`, `superseded`, `archived`.
- A document under `docs/archive/**` has `status: active`.
- A document under `docs/execution/specs/` or `docs/execution/plans/`
  has `status: archived` (it should already have been moved).

## Warning-Level Checks (default mode) / Errors in `--strict`

- A required directory listed in `references/sop.md` is missing.
- A project document lacks frontmatter or has unterminated frontmatter.
- Frontmatter lacks any of `status`, `supersedes`, `superseded_by`, `date`.
- A document in archive is not marked `status: archived`.
- A document in active execution is marked `status: superseded`
  (it should usually be archived instead).
- A Tracking Ledger contains Plan-like headings such as `## File Boundaries`,
  `## Implementation Tasks`, `## Verification`, or `### Task ...`.
- An ADR lacks `decision_status`.
- A Plan lacks a `Source Spec` section or a `[SOURCE: ...]` reference.
- A `[SOURCE: ...]` reference points to a path that does not exist
  (anchors and template placeholders like `NNNN`/`YYYY-MM-DD` are skipped;
  paths that have moved into `docs/archive/**` are recognized in default
  mode).

## Files Considered

- All `*.md` under the target project's `docs/` tree.
- `docs/templates/**` is skipped — that subtree is reserved for project-local
  copies of skill templates and is not subject to governance checks.
- The skill's own `assets/templates/**` is never scanned (it lives outside
  the target project).

## What The Validator Cannot Prove

- Semantic consistency between code and documentation.
- Whether a Spec's design actually matches the Plan that implements it.
- Whether a PRD update should have been made for a given code change.

These require human review. Use the Closure Checklist in
`references/workflows.md` before declaring a change complete.
