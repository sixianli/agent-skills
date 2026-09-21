# Integration verification — 2026-09-21

## Source and scope

- Initial repository: one worktree, local `main`, HEAD `fc7c8b20556e0122cc5f3be8aaae6a34dc07d2f4`.
- Read-only `git ls-remote --heads origin` confirmed the same remote main tip.
- Four modified and two untracked files were earlier drafts of this same task;
  no staged or unrelated work was present.
- Upstream branch tip was freshly read from the GitHub API and pinned to
  `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`. See `upstream-basis.json` for
  source paths and byte hashes; latest means the observed integration baseline.

## Automated checks actually executed

- Earlier glossary tests failed before support: unsupported `glossary` type,
  undetected conflicting type at glossary paths, and missing template. The
  existing no-root-SOURCE-fallback case already passed. These were new feature
  tests, not evidence of an old production regression.
- `python3 -m unittest discover -s document-governance/tests -p test_validate_docs.py -k glossary -v`: four tests passed after support was added.
- `UV_CACHE_DIR=/private/tmp/dg-uv-cache python3 scripts/validate_all.py`: exit 0;
  all skill structure checks, Python compile and Ruff checks passed;
  Document Governance 50 tests and Shoshin 18 tests passed.
- Skill structure and `git diff --check` passed again after final prose refinements.
- ADR template and archive implementation bytes match the pre-change commit.
  ADR status and supersession validation code was not changed.

## Behavioral evidence

Inputs and fixture contents are in `discovery-cases.json`. Recreate required
empty directories as well as files; snapshot copies containing only files omit
those directories. The reports retain actual responses and observations:

- `pure-result.md`: candidate selected for an unnamed clarification request;
  two independent questions in one round; supplied follow-up resolves the
  scoped frontier; summary requests confirmation without acting; no project
  writes. A casual wait request did not start an interview.
- `docs-result.md`: explicit candidate use records confirmed terminology before
  further questions, delegates bounded read-only code research, and separates
  static evidence from accepted product policy. Follow-up acceptance creates a
  successor ADR, retains predecessor body verbatim, updates reciprocal links
  and current product documentation, and passes strict validation. A subsequent
  read-only request leaves all six fixture file paths and hashes unchanged.
- `ordinary-result.md`: an explicit title typo request changes only that title,
  without an interview. Initial strict validation exposed a trial setup defect:
  the before-snapshot copy omitted six empty directories. Original failure is
  preserved. Restoring the fixture's declared directories made the same strict
  validator pass, without changing the product or weakening assertions.
- `docs-round1.json`: exact unified ADR supersession and related document diff,
  JSON-encoded to preserve whitespace in context lines.

Parent independently compared the old ADR body, product code, and all six
read-only snapshot hashes. All matched the corresponding invariants.

These are native independent subagent trials, not model-API calls or fresh
Codex user conversations. The host still injected old skill metadata; the pure
trial used a supplied replacement candidate description. This is evidence for
candidate-guided implicit selection and workflow behavior, not proof of isolated
installed-host routing or guaranteed selection for every natural-language prompt.
The ordinary and negative follow-ups reused a trial context. No product service
or UI behavior is claimed.

## Local installation readback

- Synced ten changed runtime files into the existing personal
  `~/.codex/skills/document-governance` installation after tests passed.
- Moved standalone `~/.agents/skills/grill-me` and `grilling` outside discovery
  roots into a recoverable `~/.codex/skill-backups/` backup.
- Independently verified all ten installed runtime hashes against the reviewed
  source manifest and absence of standalone grill-me, grilling, grill-with-docs,
  and domain-modeling folders in both personal skill roots.
- Installed skill `quick_validate.py`: passed. Installed `validate_docs.py` on
  the resulting ADR fixture with `--strict --format=json`: exit 0, zero errors
  and warnings.
- Old host-level `$grill-me` / `$grilling` aliases are not registered. The
  installed explicit entrypoint is `$document-governance`; absorbed names are
  recognized as natural-language workflow intent. Implicit invocation remains on.

The current conversation may retain previously injected metadata. A completely
fresh app conversation after installation was not launched for this verification.
