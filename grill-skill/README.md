# Standalone Grill Skills

`grill-me` and `grill-with-docs` remain independent installable skills.
`document-governance` retains its existing entrypoint, discovery description,
templates, scripts, and document lifecycle rules without modification.

## Upstream basis

Source: [mattpocock/skills](https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7).
Commit `c55ee46073ed923f86ce59a5eb3b6d895095d1b7` was verified as upstream
`main` on 2026-09-21 before import. [upstream-lock.json](upstream-lock.json)
records SHA-256 hashes of every imported original file.

The complete, unmodified source directories and MIT license are retained in
`upstream/` for review and future comparison:

- `skills/productivity/grill-me/`
- `skills/productivity/grilling/`
- `skills/engineering/grill-with-docs/`
- `skills/engineering/domain-modeling/`

These are maintenance snapshots, not additional skills to install. Install only
the two runtime directories at the repository root. Each carries the MIT license.

## Local adaptations

| Upstream behavior | Codex adaptation |
|---|---|
| `grill-me` calls `grilling` through a `Skill` tool | Loads the byte-identical upstream interview bundled in `grill-me/references/grilling.md`; no separate interview skill dependency |
| `grill-with-docs` calls `grilling` and `domain-modeling` | Reuses the installed `grill-me` interview and carries the domain-modeling method as a reference |
| Domain modeling directly writes root `CONTEXT.md` and minimal ADRs | All project-document writes execute the installed Document Governance workflow; governed glossary placement, full ADR headers, immutable history, reciprocal supersession, and strict validation apply |
| Both entrypoints are explicit-only | Both runtime skills permit implicit invocation as well as explicit invocation, with distinct descriptions for interview-only and interview-with-documents requests |
| Claude-specific `disable-model-invocation` frontmatter | Removed from runtime files; Codex invocation policy lives in `agents/openai.yaml` |

Use `$grill-me` for an interview and `$grill-with-docs` for an interview with
governed documentation. Both use the pinned upstream whole-frontier rounds.
The legacy, locally customized standalone `grilling` has been removed to avoid
competing interview entrypoints. Its old one-question workflow is not part of
these runtime packages. The upstream `grilling` snapshot and bundled reference
are the new implementation's source, not an installation of the legacy skill.

## Document ownership

`grill-with-docs` decides when a settled term or decision is ready for capture.
It hands content, evidence, and unresolved assumptions to Document Governance,
which governs and performs the file operation. The same executing Codex agent
can follow both skills; no additional process or subagent is required.

An explicit documented-interview request selects Document Governance for those
captures, not a repository-wide migration. A read-only instruction wins. If a
required skill is missing, report it and do not improvise a writing fallback.

## Installation

Keep the existing installed Document Governance. Copy the complete runtime
folders `grill-me/` and `grill-with-docs/` to a Codex-discoverable personal skills
directory. On this machine the existing `grill-me` lives in `~/.agents/skills/`,
so replace that entry in place after backing it up, and install
`grill-with-docs` beside it. Do not create duplicate same-name installations.
Do not install the legacy standalone `grilling` alongside these entrypoints.

The upstream installer alone installs the unadapted wrappers; to obtain the
Document Governance handoff, install the runtime folders from this repository.
Skills are available on the next turn after installation.

## Verification

Run `python3 scripts/validate_all.py` from the repository root. The manifest
includes both entrypoints and the package's integrity and document-contract
tests. See [tests/scenarios.md](tests/scenarios.md) for repeatable forward-test
requests. Automated fixture tests check captured documents and source integrity;
they do not prove future model selection or behavior. Real trial results are
recorded separately in `tests/evidence.md`.
