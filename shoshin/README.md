# Shoshin

Shoshin adapts PStack's methods for understanding, designing, verifying, and explaining code into Codex skills.
Maintain source in this package. Personal installation copies and generated project verification skills have separate owners.

## Current delivery scope

The source contains 16 skills (15 leaf skills and a lightweight entrypoint), seven cross-skill workflow references, an executable resource validator, and a decision-log helper.
Source implementation is complete. The user explicitly stopped the real-project pilot and requested source completion, so behavioral, full UI, and post-installation acceptance remain incomplete. The full Plan has not passed.
The entrypoint `skills/shoshin/SKILL.md` selects leaf skills and workflows as needed. After installation and host discovery, invoke it explicitly with `$shoshin`.
The [Plan](docs/execution/plans/2026-09-08-shoshin-plan.md) owns the complete execution record, passed checks, and remaining work.

| Capability | Source |
|---|---|
| Mechanisms, rationale, teaching, and impact analysis | `skills/how`, `why`, `teach`, `blast-radius` |
| Regression, types, and project verification | `skills/tdd`, `typescript-best-practices`, `create-verification-skill`, `maintain-verification-skill` |
| Code and comment review, decision logs, and technical writing | `skills/interrogate`, `show-me-your-work`, `technical-writing` |
| Design, complex implementation, retrospectives, and preferences | `skills/architect`, `figure-it-out`, `reflect`, `automate-me` |

`unslop` and `bro` receive assessments only, with no new entrypoints. `arena` remains deferred.
The package does not provide persistent scheduling, continuous PR delivery, shared agent orchestration, or a Cursor-compatible runtime.

## Usage and dependencies

Candidate validation can currently use an explicit source SKILL.md path; this does not imply automatic host discovery.
Each SKILL.md defines triggers, inputs, outputs, and limits, with references loaded as needed.
Cross-skill Markdown links identify the owner and resource for author validation. At runtime, discover the owner in the actual skill inventory before reading its files; do not assume adjacent installation directories.
Reading a cross-skill reference does not start its owning skill's entire workflow or another agent.
If a required owner cannot be discovered, report the affected step rather than skipping it and claiming completion.

Project verification generation uses the host's `skill-creator`. Formal document governance uses `document-governance` only in projects that have adopted it.
Both are existing external capabilities; this package neither copies them nor reimplements their platform interfaces.
Their absence limits the corresponding authoring or governance steps. Browser, terminal, and connector operations depend on the current host's actual capabilities.

## Checks

Use Python 3.10+ with the existing skill-creator validator and its PyYAML dependency:

```bash
python3 shoshin/scripts/validate-skills.py
python3 -m unittest discover -s shoshin/tests -v
python3 scripts/validate_all.py
```

Set `CODEX_SKILL_VALIDATOR` or `--validator` to select the current quick_validate.py.
Use `--skills-root` for an isolated layout and repeat `--external-skill` for externally discovered paths.
The validator reuses quick_validate and adds checks for name collisions, owner boundaries, internal Markdown resources, sections, and declared cross-skill links.
It is not a full Markdown renderer and does not prove triggers, semantics, tool permissions, or application behavior.
The root `skills.json` registers all 16 skills. Aggregate checks run package structure checks, script tests, and Python quality checks; they do not establish behavioral acceptance.

Behavioral requests and review criteria live in `tests/behavior-cases.json` and `tests/reviewer-rubric.md`.
Actual evidence lives in `tests/evidence/`; the presence of case material does not mean every case ran.

## Installation boundaries

The personal target is `~/.agents/skills/<skill-name>/`. Install only when authorized and disclose outstanding behavioral acceptance beforehand.
Inventory name collisions, compare directories, and retain recoverable sources. Update only content established as belonging to this package; do not overwrite unrelated user skills with the same name.
Copy complete skill directories, including references, scripts, agents, and LICENSE, not just the entrypoint.
Then verify discovery and references in an authorized fresh task. Copying files or passing isolated-layout checks does not replace host installation acceptance.
No personal installation has run, and no installer implicitly writes configuration.

Generated artifacts belong to the target project's `.agents/skills/verify-<app>/`. Do not maintain source backward from personal installation copies.
The implementation run exercised an asset CLI in user-selected JUST-RAG. The user later canceled the pilot, and the newly generated, unchanged project verification skill was removed. Retained package evidence does not establish complete RAG or production-path acceptance.

## Sources, language, and license

The user selected MIT. See [LICENSE](LICENSE) and [upstream attribution](THIRD_PARTY_NOTICES.md).
The permitted PStack source is pinned to the 0.15.0 baseline. The Spec records dispositions; `tests/evidence/upstream-inventory.json` records actual paths and SHA-256 values.
That snapshot is source evidence, not a runtime registry. Do not import designs or code from other migration projects.

This package's source text is maintained in English only. This does not require English responses or generated documents. Communication, including teach explanations, defaults to Simplified Chinese unless the user requests another language. Historical user statements and narrative evidence are English translations, not verbatim English transcripts. Original records remain in Git history. Timestamps, hashes, outcomes, and verification limits are preserved. Exact external paths containing non-English characters use JSON Unicode escapes, preserving the decoded locator without renaming external files. Test fixtures use English text while retaining Unicode coverage through an accented English word and a check-mark symbol.

The format was checked against [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) and
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Effective tool schemas remain authoritative at execution time.
