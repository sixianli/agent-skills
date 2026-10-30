# Document Governance SOP

Use this reference for document layers, lifecycle fields, naming, authority,
ADR supersession, and SOURCE-path rules.

## Contents

- [Core Principles](#core-principles)
- [Document Layers](#document-layers)
- [Frontmatter and Lifecycle](#frontmatter-and-lifecycle)
- [Cross-Document References](#cross-document-references)
- [ADR Rules](#adr-rules)
- [Authority Order](#authority-order)
- [Naming and Directories](#naming-and-directories)

## Core Principles

1. Keep each fact in one authoritative location.
2. Keep code and current-truth documents consistent.
3. Separate stable truth from temporary execution artifacts.
4. Separate design from implementation sequencing.
5. Archive closed Specs and Plans, retain ADR decision history in place, and
   move Runbook history out of the active execution directory.
6. Follow user scope and repository instructions before this default taxonomy,
   within the Rule Layers in `SKILL.md`: they override Default Conventions only.

## Document Layers


| Layer           | Default Location                                  | Answers                                    | Must Not Contain                          |
| --------------- | ------------------------------------------------- | ------------------------------------------ | ----------------------------------------- |
| PRD             | `docs/prd-v*.md`                                  | What to build and why                      | APIs, classes, schemas, file steps        |
| Architecture    | `docs/architecture-v*.md`                         | Current system shape                       | Task checklists, rejected alternatives    |
| ADR             | `docs/adr/NNNN-title.md`                          | Why a durable decision was made            | Current implementation inventory          |
| Spec            | `docs/execution/specs/YYYY-MM-DD-topic-design.md` | Design for one change                      | File-level implementation steps           |
| Plan            | `docs/execution/plans/YYYY-MM-DD-topic-plan.md`   | Implementation order and verification      | New requirements or design decisions      |
| Runbook         | `docs/runbooks/topic-runbook.md`                  | Operate, deploy, debug, recover            | Product requirements or feature rationale |
| Idea            | `docs/ideas/IDEA-*.md`                            | A durable insight and its thinking context | A commitment to implement                 |
| Backlog Item    | `docs/backlog/BL-*.md`                            | Future work, priority, state, and outcome  | File-level execution steps                |
| Agent Lessons   | `docs/lessons.md`                                 | Repeated agent mistakes and prevention     | Status, one-off issues, future work       |
| Archive         | `docs/archive/specs/`, `docs/archive/plans/`, `docs/archive/runbooks/`, `docs/archive/ideas/`, `docs/archive/backlog/` | Closed execution, Runbook, and terminal Idea/Backlog history | Active source-of-truth content |

Do not create or maintain `docs/TODO.md`; Backlog is the only durable future-work
inventory. This is Skill Policy and repository conventions do not override it (see
`SKILL.md`, Rule Layers). Maintain `docs/lessons.md` only for mistakes coding agents make
frequently or repeatedly and the explicit rules that prevent recurrence. Do not add
project status, general knowledge, one-off incidents, or future work there. Give each
lesson one heading that states the mistake itself, so an agent can choose relevant
lessons from the headings alone.

Recognize existing `docs/archive/adr/` documents for backward compatibility,
but do not move new or superseded ADRs there.

## Frontmatter and Lifecycle

Start every governed document, including archived documents, with single-line
frontmatter. Do not use nested mappings, arrays, duplicate keys, or multiline
values.

Required fields:

```yaml
---
status: active          # active | superseded | archived
supersedes: ""          # repo-relative path or comma-separated paths
superseded_by: ""       # repo-relative path or comma-separated paths
date: "YYYY-MM-DD"
---
```

Type-specific fields:

```yaml
document_type: spec        # prd | architecture | adr | spec | plan | runbook | idea | backlog | lessons
version: "X.Y"             # PRD/Architecture only
decision_status: accepted  # ADR only: proposed | accepted | superseded
execution_risk: critical   # Active Runbook only: standard | high | critical
contract_sha256: "sha256:<64-hex>" # Active Runbook static contract
record_id: IDEA-YYYYMMDD-xxxxxx  # 6 random chars; legacy -NNN stays valid
record_state: captured      # State set depends on document_type
updated: "YYYY-MM-DD"       # Structured Idea/Backlog only
priority: normal            # Backlog only: urgent | high | normal | low
item_type: enhancement      # Backlog only: non-empty project-defined label
```

Use the lifecycle fields consistently:

- `active`: current truth or open execution work.
- `superseded`: replaced by a named successor. ADRs retain this state in
  `docs/adr/`; non-executable Runbook history is represented as `archived`
  under `docs/archive/runbooks/`, not left in the active directory.
- `archived`: a closed Spec/Plan, a historical/retired Runbook, or a terminal
  Idea/Backlog record under its matching `docs/archive/` directory. An archived
  Idea/Backlog keeps the `record_state` it had when archived.
- For a superseded ADR, set both `status: superseded` and
  `decision_status: superseded`, keep it in `docs/adr/`, and populate
  `superseded_by`.
- For the replacement ADR, set `status: active`, set `supersedes`, and accept
  it before marking the old ADR superseded.
- When a superseded ADR itself replaced an earlier one, keep each `supersedes`
  field and the predecessor's `superseded_by` field unchanged; the validator
  follows the `superseded_by` chain to the final active, accepted ADR.
- Keep only `status: active` Runbooks under `docs/runbooks/`. Historical
  snapshots, superseded Runbooks, and retired Runbooks use `status: archived`
  under `docs/archive/runbooks/`.
- A retired Runbook without a successor sets a one-line `archive_reason`.
- Runbook `date` is document metadata, never execution freshness. Do not add
  Runbook `last_reviewed`, `review_after`, or periodic trust windows.
- Read `references/runbook-workflow.md` for the risk, fingerprint, execution,
  evidence, and archive contract.

## Cross-Document References

Use machine-checkable authoritative references:

```text
[SOURCE: docs/path.md#optional-anchor]
```

Rules:

- Keep local targets inside the project `docs/` tree.
- Reject absolute paths and any `..` traversal.
- Resolve a path without a `docs/` prefix relative to `docs/` only, never the
  repository root.
- Treat anchors as kebab-case heading slugs; the validator does not verify the
  anchor itself.
- Skip external `http://` and `https://` targets.
- Do not leave template placeholders such as `NNNN`, `YYYY-MM-DD`, and
  `<topic>` in a governed document. Only files under `docs/templates/` may keep
  them; elsewhere the validator reports an unfilled placeholder.
- Permit ordinary Markdown links for prose, but use SOURCE for authoritative
  cross-document dependencies.
- Preserve links to closed Specs, Plans, and archived Idea/Backlog records
  through the active-to-archive compatibility mapping. The mapping also applies
  to the record fields `promoted_to`, `source_idea`, `supersedes`, and
  `superseded_by`. Resolve a missing legacy active Runbook path to an
  exact undated archive or one unambiguous dated archive; otherwise require an
  exact archive path. Preserve legacy ADR links similarly, but do not archive
  ADRs going forward.

## ADR Rules

- Record exactly one durable decision per ADR.
- Do not rewrite an ADR's recorded decision, context, options, or consequences.
  Permit only typo, formatting, broken-link, and cross-reference repairs that
  do not change the historical decision.
- When a decision changes, follow the in-place supersession workflow in
  `references/workflows.md`; do not run the archive script on an ADR.
- Keep Architecture aligned with current behavior. ADRs explain rationale;
  Architecture describes the current system.
- Keep implementation inventory and task checklists in Architecture, Specs, or
  Plans rather than ADRs.

## Authority Order

Resolve conflicts in this order:

1. PRD for product scope and business rules.
2. Architecture for current technical behavior.
3. ADR for decision rationale and trade-offs.
4. Spec for confirmed design of one change.
5. Plan for execution sequence and verification.
6. Runbook for operation and troubleshooting.

Current repository evidence still matters: when code and current-truth
documents disagree, inspect the implementation and reconcile the appropriate
authoritative document rather than blindly trusting stale prose.

## Naming and Directories


| Type            | Pattern                                                          |
| --------------- | ---------------------------------------------------------------- |
| PRD             | `prd-v{major.minor}.md`                                          |
| Architecture    | `architecture-v{major.minor}.md`                                 |
| ADR             | `NNNN-short-title.md`                                            |
| Spec            | `YYYY-MM-DD-topic-design.md`                                     |
| Plan            | `YYYY-MM-DD-topic-plan.md`                                       |
| Runbook         | `topic-runbook.md`, `topic-setup.md`, `topic-troubleshooting.md` |
| Archived Runbook | `YYYY-MM-DD-{stable-runbook-name}.md`; legacy undated names remain readable |
| Idea            | `IDEA-YYYYMMDD-xxxxxx-short-title.md` under `docs/ideas/`        |
| Backlog         | `BL-YYYYMMDD-xxxxxx-short-title.md` under `docs/backlog/`        |
| Agent Lessons   | `docs/lessons.md`                                                |

```text
docs/
├── prd-v0.1.md
├── architecture-v0.1.md
├── adr/
├── execution/
│   ├── specs/
│   └── plans/
├── runbooks/
├── ideas/
├── backlog/
├── lessons.md
└── archive/
    ├── specs/
    ├── plans/
    ├── runbooks/
    ├── ideas/
    └── backlog/
```

Keep only pending or executing work in `docs/execution/specs/` and
`docs/execution/plans/`. Move closed Specs and Plans to the matching archive
directory after completing the closure checklist.

Keep a current Runbook at a stable path under `docs/runbooks/`. Use
`scripts/archive_doc.py` with one of its explicit Runbook modes for snapshots,
supersession, or retirement. Never execute from `docs/archive/runbooks/`.

Move a terminal Idea or Backlog record to `docs/archive/ideas/` or
`docs/archive/backlog/` with `scripts/archive_doc.py` as soon as it reaches its
terminal state. The file name does not change.

Do not create a hand-maintained Idea or Backlog index. Query the
frontmatter-bearing source records with `scripts/idea_backlog.py list` or
`scripts/idea_backlog.py review`.
