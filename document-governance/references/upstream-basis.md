# Upstream Basis

Verified against the GitHub `main` tip on 2026-09-21:
`mattpocock/skills@c55ee46073ed923f86ce59a5eb3b6d895095d1b7`.
This is the source snapshot for this integration, not a promise that it remains
latest forever. Before future upstream updates, check the branch again and
compare actual contents. The development evidence manifest records file hashes.

Source: https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7

| Source file | Integration |
| --- | --- |
| skills/productivity/grill-me/SKILL.md | Explicit interview intent routes directly to this skill's interview SOP |
| skills/productivity/grilling/SKILL.md | Decision tree, whole-frontier question rounds, recommendations, answer-dependent recomputation, delegated fact research, final shared-understanding confirmation |
| skills/engineering/grill-with-docs/SKILL.md | Interview plus domain modeling and incremental document recording in one skill |
| skills/engineering/domain-modeling/SKILL.md | Challenge glossary conflicts, sharpen terms, probe concrete scenarios, cross-check code, record settled concepts, offer ADRs selectively |
| skills/engineering/domain-modeling/CONTEXT-FORMAT.md | Context-scoped canonical terms and avoided aliases, using governed glossary locations and metadata |
| skills/engineering/domain-modeling/ADR-FORMAT.md | ADR selection heuristics and sequential numbering; existing governance template and supersession rules take precedence over upstream's minimal template |

## Deliberate adaptations

- One explicit entrypoint, `$document-governance`, and implicit interview
  matching. No `Skill` tool calls, separate interview skill dependency, or old
  host-level skill-name aliases. Existing local one-question defaults are not
  the integration baseline.
- Pure interviews need no repository adoption and do not write files. Interview
  recording requires persistence intent; document adoption stays scoped.
- Keep upstream's whole-frontier rounds and confirmation gate. User instructions
  can override the interview procedure. Delegate read-only fact research when
  supported and permitted; otherwise disclose and investigate directly.
- Writing agreed outcomes during a document interview is allowed before final
  confirmation. Implementation still needs confirmation and applicable authority.
- Keep Document Governance ADR format, SOURCE boundaries, templates, and immutable
  decision history. Add an optional glossary type instead of a parallel root
  CONTEXT document system. Existing CONTEXT files are evidence, not auto-migrated.
- Limit the interview to the requested topic, with all branches of that scoped
  design resolved. Ordinary clear document operations do not become interviews.

MIT attribution is retained in `../THIRD_PARTY_NOTICES.md`.
