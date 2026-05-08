---
name: document-governance
description: Use when creating, modifying, archiving, validating, or restructuring project documentation; when writing PRDs, architecture docs, ADRs, specs, plans, runbooks, tracking ledgers, or resolving code-document drift.
---

# Document Governance

This skill is the global SOP for project documentation governance. It is the
source of truth for how Codex should create, classify, update, archive, validate,
and close project documents.

## Progressive Disclosure

Load only what the task needs:

- For layer definitions, naming, frontmatter, and authority rules: read `references/sop.md`.
- For new feature docs, closure, rollback, and conflict handling: read `references/workflows.md`.
- For deterministic checks and validator expectations: read `references/validation-rules.md`.
- For creating new documents: use templates in `assets/templates/`.
- For validation: run this skill's `scripts/validate_docs.py` with the target project root as the argument.

## Required Workflow

1. Inspect project instructions such as `AGENTS.md` before editing.
2. Classify the request: PRD, Architecture, ADR, Spec, Plan, Runbook, Tracking Ledger, or Archive.
3. Read the relevant reference file listed above.
4. Use the matching template for new documents.
5. Keep code and documents consistent in the same change set.
6. Archive completed, rejected, or superseded Specs and Plans only after closure is complete.
7. Run the validator and `git --no-pager diff --check` before claiming completion.

Validator command shape:

```bash
python3 <skill-dir>/scripts/validate_docs.py <target-project-root>
```

## Non-Negotiables

- Do not create or maintain separate project-specific document SOP files unless the human explicitly asks for an exception.
- Project files may configure paths or add local constraints, but they do not duplicate this SOP.
- Tracking Ledgers preserve provenance and state; they do not replace Specs or Plans.
- ADRs explain why durable technical decisions were made; Architecture describes the current system.
- If code is reverted, related documents must be reverted or corrected with it.
