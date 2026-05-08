# Validation Rules

Use this file before running or modifying this skill's `scripts/validate_docs.py`.

## How To Run

Run the validator from the skill folder, not from the target project. Pass the
target project root as the script argument.

```bash
python3 <skill-dir>/scripts/validate_docs.py <target-project-root>
```

If your shell is already in the target project root:

```bash
python3 <skill-dir>/scripts/validate_docs.py .
```

## Modes

Default mode is migration-friendly: legacy documents and moved archive links are
reported as warnings so the validator can be introduced into existing projects.

Use `--strict` for CI or final hardening when warnings should become failures.

## Error-Level Checks In Default Mode

- Required document directories are missing.
- `status` is not one of `active`, `superseded`, or `archived`.
- A document under `docs/archive/**` has `status: active`.
- A document under `docs/execution/specs/` or `docs/execution/plans/` has `status: archived`.

## Warning-Level Checks

- A project document lacks frontmatter.
- Frontmatter lacks `status`, `supersedes`, `superseded_by`, or `date`.
- A document in archive is not marked `status: archived`.
- A document in active execution is marked `status: superseded`.
- A Tracking Ledger contains Plan-like headings such as `File Boundaries`,
  `Implementation Tasks`, or `Verification`.
- An ADR lacks `decision_status`.
- A Plan lacks a `Source Spec` section or a local source reference.
- A local `[SOURCE: ...]` reference points to a missing file or a document that
  has likely moved to archive.

## Strict Mode Escalation

With `--strict`, missing frontmatter, missing required frontmatter fields, and
missing local SOURCE targets become errors.

## Required Manual Review

The validator cannot prove semantic consistency between code and documentation.
Before completion, manually check whether code changes require PRD, Architecture,
ADR, README, Runbook, Tracking Ledger, Spec, or Plan updates.
