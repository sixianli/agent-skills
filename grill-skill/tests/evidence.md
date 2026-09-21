# Standalone Skill Verification — 2026-09-21

## Source and preservation

- `git ls-remote` and a fresh clone both resolved upstream `main` to
  `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`; a second remote check agreed.
- The installer imported both complete entrypoint directories before adaptation.
  All original files and their dependencies are retained in `../upstream/`,
  with hashes in `../upstream-lock.json`.
- Runtime `grill-me/references/grilling.md` is byte-identical to that upstream
  interview. Runtime modeling preserves terminology challenges, scenarios,
  code cross-checking, immediate capture, context boundaries, and ADR criteria;
  all persistence instructions are replaced by the governance handoff.
- Before/after file hashes confirm no changes to repository Document Governance,
  installed Document Governance, or the separately installed customized `grilling`.

## Independent behavior trials

See [pure-result.md](pure-result.md) and [docs-result.md](docs-result.md) for
the requests, loaded resources, actual output, commands, and limitations.

- Pure interview: loaded the bundled upstream workflow, asked a numbered ready
  frontier with recommendations, left dependent details for later, invented no
  answers, and made no project writes.
- Discussion-only `grill-with-docs`: respected the explicit no-write boundary.
- Documented interview: loaded Document Governance and its actual ADR template
  before writing; immediately captured accepted terminology and a changed storage
  decision, preserved the old ADR body byte-for-byte, and maintained reciprocal
  supersession. It distinguished accepted design from unimplemented migration.
- The original document fixture lacked six governance directories before the
  trial. Strict validation failed for exactly those pre-existing problems both
  before and after capture; the agent reported them without unrelated repairs.
  The same captured documents subsequently passed strict validation in a complete
  directory scaffold, using both repository and installed governance validators.

## Executed checks

- `python3 -m unittest discover -s grill-skill/tests -v`: 5 passed, including
  upstream completeness, exact interview/license preservation, packaged reference
  resolution, captured-document strict validation, and immutable prior ADR body.
- `python3 scripts/validate_all.py`: all checks passed, including the new 5 tests,
  existing Document Governance 46 tests, Shoshin 18 tests, skill structure checks,
  Python compilation, and declared Ruff checks. A task-specific UV cache was used.
- Installed `grill-me`, `grill-with-docs`, and Document Governance each passed
  `quick_validate.py`. Installed new-skill files match repository runtime hashes.
- The old `grill-me` wrapper was backed up outside discovery before replacement.
  The new skills are colocated in the existing personal `~/.agents/skills/`
  installation; Document Governance remains at its existing installed location.

## Limits

These are isolated model trials, persisted-document checks, metadata checks,
and installation readback. They do not prove that every future implicit request
will select the intended skill. The pre-install trial inventory did not expose
the new `grill-me`; it was supplied by its candidate path. The next host turn
must load the new installed inventory. The handoff is a model instruction, not
a tool-level filesystem enforcement mechanism. Subagent research was disabled
inside the isolated evaluators; the upstream workflow itself was preserved.
