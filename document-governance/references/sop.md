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
| Tracking Ledger | `docs/TODO.md`, `docs/lessons.md`, `docs/tracking/*.md` | Provenance, state, lessons, follow-ups | Current truth or execution steps |
| Archive | `docs/archive/**` | Historical traceability | Active source-of-truth content |

## Frontmatter

Every project document, including archived documents, starts with frontmatter.

Minimum fields:

```yaml
---
status: active          # active | superseded | archived
supersedes: ""          # filename or path this replaces
superseded_by: ""       # filename or path that replaced this
date: "YYYY-MM-DD"
---
```

Recommended fields:

```yaml
document_type: spec     # prd | architecture | adr | spec | plan | runbook | tracking
version: "0.1"          # PRD/Architecture only
decision_status: accepted  # ADR only: proposed | accepted | superseded
```

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
| Tracking | `topic-ledger.md` or established root document |

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
