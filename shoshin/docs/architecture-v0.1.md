---
status: active
document_type: architecture
version: "0.1"
supersedes: ""
superseded_by: ""
date: "2026-09-08"
---

# Shoshin Architecture v0.1

## Current System

The source contains 16 skills (15 independent leaf skills and the shoshin entrypoint), seven workflow references, a resource validator, and a TSV logging helper. The user canceled the real-project pilot and requested completion of the source. The entrypoint is connected; real behavior and installation acceptance remain incomplete.

Each SKILL.md can be reviewed through an explicit source path. It contains the task scope and necessary short contracts, with longer methods loaded conditionally from references. agents/openai.yaml preserves implicit invocation, but source presence does not mean host discovery or installation. There is no MCP service, plugin manifest, scheduler, or shared agent layer.

## Boundaries

- Shared source: shoshin/skills; maintain it only there.
- Host capabilities: tools, permissions, skill discovery, and actual user authorization; the package does not replace them.
- Author validation: validate-skills.py reuses current quick_validate.py and checks declared resources, owners, and sections; it does not execute skills.
- Deterministic runtime helper: show-me-your-work/scripts/log.sh appends TSV through one writer, protecting the existing header and escaping cells.
- Project-generated artifacts: the target project's .agents/skills/verify-<app>, maintained with its code and actual control tools.
- Personal installation target: ~/.agents/skills; not installed in this run.

## Data Model

Standard YAML frontmatter identifies skills by name/description. Metadata and execution methods live separately, without an additional runtime registry.

Cross-skill links express a name, resource, and optional section. Runtime discovery resolves the actual owner. Report a dependency gap when the owner is absent. Reading a detailed method does not recursively execute its owner's workflow.

The decision log has six columns: ts, phase, decision, why, evidence, result. Control characters are flattened to one line; formula-prefix protection and double-quote escaping preserve TSV readability. Corrections append rather than rewrite history. Single-writer operation is the current contract, not a claim of a multiprocess mutex.

## Main Flows

Explanations and reviews use independent leaf skills. Complex work follows explicit dependencies and verifies actual artifacts. Verification generation requires real user paths, preserved evidence, and cleanup of owned resources. Maintenance requires bidirectional coverage checks and recovery after failure. Workflow text does not automatically create persistent tasks or remote delivery.

An asset CLI was run in JUST-RAG during implementation. The user later canceled the pilot, and unchanged project artifacts created by this task were cleaned up. Full UI, model calls, complete AC15/AC16 paths, and some behavioral scenarios remain unpassed. Evidence and unfinished work stay in the execution Plan; this architecture document does not manually synchronize test counts.

## Backlog Links

- [SOURCE: docs/backlog/BL-20260908-001-implement-shoshin.md]
- [SOURCE: docs/backlog/BL-20260908-002-arena-scope-decision.md]

## Decision Links

- [SOURCE: docs/adr/0001-shoshin-package-identity.md]
- [SOURCE: docs/execution/specs/2026-09-08-shoshin-design.md]
- [SOURCE: docs/execution/plans/2026-09-08-shoshin-plan.md]
