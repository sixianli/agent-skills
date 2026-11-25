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
5. Keep only documents that are true now; version control holds the history.
   Delete closed Specs, Plans, Runbooks, terminal Idea/Backlog records, and
   replaced or stale ADRs (see `SKILL.md`, Core Principle).
6. Treat the code as the source of truth. A document that no longer matches the
   code is fixed when most of it is still the current design, otherwise
   deleted. A design still being implemented carries
   `implementation: in_progress` until the code catches up.
7. Follow user scope and repository instructions before this default taxonomy,
   within the Rule Layers in `SKILL.md`: they override Default Conventions only.

## Document Layers


| Layer           | Default Location                                  | Answers                                    | Must Not Contain                          |
| --------------- | ------------------------------------------------- | ------------------------------------------ | ----------------------------------------- |
| PRD             | `docs/prd-v*.md`                                  | What to build and why                      | APIs, classes, schemas, file steps        |
| Architecture    | `docs/architecture-v*.md`                         | Current system shape                       | Task checklists, rejected alternatives    |
| ADR             | `docs/adr/NNNN-title.md`                          | Why a durable decision was made            | Current implementation inventory          |
| Spec            | `docs/execution/specs/YYYY-MM-DD-topic-design.md` | Design for one change                      | File-level implementation steps           |
| Plan (legacy)   | `docs/execution/plans/YYYY-MM-DD-topic-plan.md`   | Implementation order of earlier work; no longer created | New requirements or design decisions |
| Runbook         | `docs/runbooks/topic-runbook.md`                  | Operate, deploy, debug, recover            | Product requirements or feature rationale |
| Idea            | `docs/ideas/IDEA-*.md`                            | A durable insight and its thinking context | A commitment to implement                 |
| Backlog Item    | `docs/backlog/BL-*.md`                            | Future work, priority, state, and outcome  | File-level execution steps                |
| Agent Lessons   | `docs/lessons.md`                                 | Repeated agent mistakes and prevention     | Status, one-off issues, future work       |
| Archive (optional) | `docs/archive/specs/`, `docs/archive/plans/`, `docs/archive/runbooks/`, `docs/archive/ideas/`, `docs/archive/backlog/` | Closed documents, only in a repository that keeps an archive instead of deleting | Active source-of-truth content |

Do not create or maintain `docs/TODO.md`; Backlog is the only durable future-work
inventory. This is Skill Policy and repository conventions do not override it (see
`SKILL.md`, Rule Layers). Maintain `docs/lessons.md` only for mistakes coding agents make
frequently or repeatedly and the explicit rules that prevent recurrence. Do not add
project status, general knowledge, one-off incidents, or future work there. Give each
lesson one heading that states the mistake itself, so an agent can choose relevant
lessons from the headings alone.

ADRs are never archived. A legacy `docs/archive/adr/` directory is reported by
the validator; delete its files.

Do not create Plan documents. A coding agent plans execution order itself,
and the project's task tracker and change history record progress; a Plan
file repeats both and goes stale. Keep validating and archiving Plans that
already exist. A repository may override this default and keep writing Plans.

## Frontmatter and Lifecycle

Start every governed document, including archived documents, with single-line
frontmatter. Do not use nested mappings, arrays, duplicate keys, or multiline
values.

Required fields:

```yaml
---
status: active          # active | superseded | archived
supersedes: ""          # repo-relative path(s); for an ADR, pinned commit permalink(s)
superseded_by: ""       # repo-relative path(s); not used by ADRs
date: "YYYY-MM-DD"
---
```

An ADR does not need `superseded_by`; if present it must be empty, because a
replaced ADR is deleted.

Code-tracking fields, for documents that describe code (Architecture, ADR,
Runbook, and any other long-lived document):

```yaml
covers: "src/inbox/**, scripts/deploy.sh"  # repo paths or globs, one line; "" = describes no code
verified_at: "0123abc"                      # commit the document was last checked against
implementation: in_progress                 # only while a new design is being implemented
```

- `covers` entries are repository-relative, without `..` or URLs. `*`
  matches within one path segment, `**` across segments, and a plain path
  covers everything below it. Every entry must match a file in the current
  tree, except while `implementation: in_progress`.
- `verified_at` is required once `covers` is non-empty. Set it with
  `scripts/doc_coverage.py stamp`, never by hand-copying a date.
- Documents without `covers` are reported by `scripts/doc_coverage.py audit`
  so they can be given one; missing `covers` does not fail validation.

Type-specific fields:

```yaml
document_type: spec        # prd | architecture | adr | spec | plan | runbook | idea | backlog | lessons
version: "X.Y"             # PRD/Architecture only
decision_status: accepted  # ADR only: proposed | accepted
execution_risk: critical   # Active Runbook only: standard | high | critical
record_id: IDEA-YYYYMMDD-xxxxxx  # 6 random chars; legacy -NNN stays valid
record_state: captured      # State set depends on document_type
updated: "YYYY-MM-DD"       # Structured Idea/Backlog only
priority: normal            # Backlog only: urgent | high | normal | low
item_type: enhancement      # Backlog only: non-empty project-defined label
```

Use the lifecycle fields consistently:

- `active`: current truth or open execution work.
- `superseded`: replaced by a named successor. Not valid for ADRs, which are
  deleted when replaced; non-executable Runbook history is represented as
  `archived` under `docs/archive/runbooks/`, not left in the active directory.
- `archived`: a closed Spec/Plan, a historical/retired Runbook, or a terminal
  Idea/Backlog record under its matching `docs/archive/` directory. An archived
  Idea/Backlog keeps the `record_state` it had when archived.
- When an ADR is replaced, the replacement sets `status: active` and
  `supersedes` to a permalink pinned to the last commit that had the old ADR;
  the old ADR is deleted in the same change set once the replacement is
  accepted. While the replacement is only `proposed`, `supersedes` may name the
  old ADR's local path, and the old ADR stays in force.
- Keep only `status: active` Runbooks under `docs/runbooks/`. Historical
  snapshots, superseded Runbooks, and retired Runbooks use `status: archived`
  under `docs/archive/runbooks/`.
- A retired Runbook without a successor sets a one-line `archive_reason`.
- Runbook `date` is document metadata, never execution freshness. Do not add
  Runbook `last_reviewed`, `review_after`, or periodic trust windows.
- Read `references/runbook-workflow.md` for the risk, execution, evidence,
  and archive rules.

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
  exact archive path. A link to a deleted document, including a deleted ADR,
  becomes a permalink pinned to the last commit that had it.
- Inline-code paths, symbols, commands, and config keys in current documents
  must exist in the current tree; see `references/validation-rules.md`.

## ADR Rules

- Write an ADR only for a decision that passes both tests: reversing it later
  would be costly, and a future reader would otherwise ask why it was made.
  Typical subjects are system structure, non-functional qualities such as
  security or durability, dependencies, interfaces and contracts, construction
  techniques, and durable product-scope choices.
- Do not write an ADR for a routine, cheaply reversible change such as tuning a
  limit, resizing a machine, adjusting a pipeline setting, or upgrading a
  dependency without a design consequence. Record its reason in the change
  description. When unsure, ask whether anyone would need the reason a year
  from now; if not, do not write an ADR.
- Keep an ADR to one or two pages. It states the forces, the decision, and the
  consequences. Put detailed design in a Spec and link it instead of growing
  the ADR.
- Record exactly one durable decision per ADR.
- Do not change an ADR's recorded decision. A changed decision gets a new ADR,
  and the old one is deleted in the same change set (Supersede by Deletion in
  `references/workflows.md`); do not run the archive script on an ADR.
- Keep an ADR's text true to the code it still governs. When only part of it
  is replaced or no longer matches the code, rewrite or remove that part in the
  same change set; this is not a decision change. When most of it is stale,
  delete it.
- Keep Architecture aligned with current behavior. ADRs explain rationale;
  Architecture describes the current system.
- Keep implementation inventory and task checklists in Architecture, Specs, or
  Plans rather than ADRs.

## Authority Order

Resolve conflicts in this order:

1. PRD for product scope and business rules.
2. Architecture for current technical behavior.
3. ADR for decision rationale and trade-offs (every ADR in the repository is
   current; replaced ones are deleted).
4. Spec for confirmed design of one change.
5. Legacy Plan for the execution sequence of earlier work.
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
| Plan (legacy)   | `YYYY-MM-DD-topic-plan.md`                                       |
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
└── lessons.md
```

Keep only pending or executing work in `docs/execution/specs/`. Delete a
Spec, and any legacy Plan or handoff note that belongs to it, in the same
change set that merges, completes, or abandons its work; see Spec and Plan Closure and Closing by
Deletion in `references/workflows.md`. A Spec is a point-in-time record: it is
not updated to match later code. `docs/execution/plans/` exists only in
projects that hold legacy Plans.

Keep a current Runbook at a stable path under `docs/runbooks/` and delete it
when it is retired or replaced. Never execute from `docs/archive/runbooks/`.

Delete a terminal Idea or Backlog record as soon as it reaches its terminal
state.

`docs/archive/` and every archive rule in this file apply only to a repository
that chooses to keep an archive, and to archives that already exist. Such a
repository moves documents there only with `scripts/archive_doc.py`.

Do not create a hand-maintained Idea or Backlog index. Query the
frontmatter-bearing source records with `scripts/idea_backlog.py list` or
`scripts/idea_backlog.py review`.
