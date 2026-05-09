# Document Governance SOP

This file is the canonical SOP for project documentation governance. Projects
should not maintain separate long-form document standards. Project files may add
path configuration or local constraints, but this SOP defines the rules.

## Core Principles

1. **Single Source of Truth**: Every piece of information has one authoritative location.
2. **Code/document consistency**: Code and documents must describe the same reality.
3. **Stable vs. ephemeral**: PRD and Architecture are stable; Specs and Plans are active work artifacts.
4. **Design vs. execution**: Specs describe what the change looks like; Plans describe how to implement it.
5. **Archive, do not erase**: Closed or superseded work moves to archive.

## Document Layers

| Layer | Default Location | Answers | Must Not Contain |
|-------|------------------|---------|------------------|
| PRD | `docs/prd-v*.md` | What to build and why | APIs, classes, schemas, file steps |
| Architecture | `docs/architecture-v*.md` | Current system shape | Task checklists, rejected alternatives |
| ADR | `docs/adr/NNNN-title.md` | Why a durable decision was made | Current implementation inventory |
| Spec | `docs/execution/specs/YYYY-MM-DD-topic-design.md` | Design for one change | File-level implementation steps |
| Plan | `docs/execution/plans/YYYY-MM-DD-topic-plan.md` | Implementation order and verification | New requirements or design decisions |
| Runbook | `docs/runbooks/topic-runbook.md` | Operate, deploy, debug, recover | Product requirements or feature rationale |
| Tracking Ledger | `docs/tracking/*.md` (and the legacy roots `docs/TODO.md`, `docs/lessons.md`) | Provenance, state, lessons, follow-ups | Current truth or execution steps |
| Archive | `docs/archive/**` | Historical traceability | Active source-of-truth content |

> Tracking Ledgers should be authored under `docs/tracking/` going forward.
> The validator still recognizes `docs/TODO.md` and `docs/lessons.md` for
> backward compatibility, but new ledgers should not be placed at the docs root.

## Frontmatter

Every project document, including archived documents, starts with frontmatter.
Frontmatter is parsed line-by-line by `scripts/validate_docs.py`, so each
field must be a single-line `key: value` pair. **Do not use multi-line YAML,
nested mappings, or arrays inside frontmatter.** If you need to record
multiple supersedes/superseded_by links, separate them with commas in a
single string value.

Minimum fields:

```yaml
---
status: active          # active | superseded | archived
supersedes: ""          # filename, path, or comma-separated paths this replaces
superseded_by: ""       # filename, path, or comma-separated paths that replaced this
date: "YYYY-MM-DD"
---
```

Recommended fields:

```yaml
document_type: spec        # prd | architecture | adr | spec | plan | runbook | tracking
version: "X.Y"             # PRD/Architecture only — set on creation
decision_status: accepted  # ADR only: proposed | accepted | superseded
```

## Cross-Document References

Project documents reference each other using a deliberate, machine-checkable
syntax instead of plain Markdown links. The validator parses this form to
detect broken or moved targets:

```text
[SOURCE: <relative-path-from-repo-root>#<optional-anchor>]
```

Rules:

- Path is repo-relative (e.g. `docs/prd-v0.1.md`). Paths starting without
  `docs/` are also resolved relative to `docs/` for convenience.
- Anchors after `#` are kebab-case heading slugs and are not validated.
- Templates may use placeholders like `NNNN`, `YYYY-MM-DD`, `<topic>`; those
  are skipped by the validator.
- External http(s) URLs may also appear in `[SOURCE: ...]` and are skipped.
- Plain Markdown links `[text](path)` are still permitted for prose, but
  cross-document authoritative references should use `[SOURCE: ...]`.

Example:

```markdown
- PRD: [SOURCE: docs/prd-v0.1.md#scope]
- Architecture: [SOURCE: docs/architecture-v0.1.md#data-model]
- ADR: [SOURCE: docs/adr/0007-token-storage.md]
```

## ADR-Specific Rules

ADRs follow the standard pattern (Michael Nygard's original ADR + MADR):
they record one durable architectural decision, with context, options,
chosen option, and consequences. They are an **append-only decision log**,
not a general-purpose doc.

- One ADR records exactly one decision. Keep it short.
- A past ADR's decision, context, options, and consequences are immutable.
  Allowed in-place edits: typo fixes, link repair, cross-references,
  formatting. Not allowed: silently rewriting the recorded decision.
- When the decision changes: create a new ADR. Set `decision_status:
  superseded` and `superseded_by: <new-adr>` on the old one. Set
  `supersedes: <old-adr>` on the new one.
- Architecture describes current behavior; ADRs describe why current
  behavior was chosen. If they conflict, update Architecture to reflect
  reality and create or supersede ADRs to record the new rationale.
- ADRs do not list current implementation inventory, file boundaries, or
  task checklists. Those belong in Architecture, Spec, or Plan.

## Authority Order

Use this order when documents disagree:

1. PRD for product scope and business rules.
2. Architecture for current technical behavior.
3. ADR for decision rationale and trade-offs.
4. Spec for confirmed design of one change.
5. Plan for execution sequence and verification.
6. Runbook for operation and troubleshooting.
7. Tracking Ledger for provenance and follow-up state.

Architecture is current truth; ADR is decision history. If they conflict, update
Architecture for current behavior and create or supersede ADRs for changed
rationale.

## Naming

| Type | Pattern |
|------|---------|
| PRD | `prd-v{major.minor}.md` |
| Architecture | `architecture-v{major.minor}.md` |
| ADR | `NNNN-short-title.md` |
| Spec | `YYYY-MM-DD-topic-design.md` |
| Plan | `YYYY-MM-DD-topic-plan.md` |
| Runbook | `topic-runbook.md`, `topic-setup.md`, `topic-troubleshooting.md` |
| Tracking | `topic-ledger.md` under `docs/tracking/` |

## Default Directory Structure

```text
docs/
├── prd-v0.1.md
├── architecture-v0.1.md
├── adr/
├── execution/
│   ├── specs/
│   └── plans/
├── runbooks/
├── tracking/
└── archive/
    ├── adr/
    ├── specs/
    └── plans/
```

`docs/execution/specs/` and `docs/execution/plans/` are the active execution
queue. They contain only pending or currently executing Specs and Plans.
Implemented, rejected, or superseded Specs and Plans belong in archive.
