# Independent tool review

English translation of the original review. Findings, source locations, and test counts describe the review-time version. They are historical evidence, not current failures. Original wording remains in Git history.

The requested read-only review is complete. Three real defects were reproduced with minimal fixtures in /tmp. All 13 existing `test_tools.py` tests ran and passed, showing those boundaries were uncovered, not that all tool behavior was verified. No repository files were modified.

Review intent: resolve internal/external resource references and protect existing log content while preserving six reviewable TSV columns. The reviewer followed interrogate SKILL.md and review-criteria.md and read both tools, their tests, and show-me-your-work's contract. The scope was the new package's uncommitted files; git status showed untracked shoshin/scripts, skills, and tests, not an existing release.

## Act on: P2, appending to a log without a final newline corrupts its last row

Locations: `shoshin/skills/show-me-your-work/scripts/log.sh:16–22,40–43`.

The script validates the header string without checking the final newline. An existing file containing only the valid header `ts\tphase\tdecision\twhy\tevidence\tresult` without LF is accepted by `read ... || true`. Appending joins the timestamp directly to `result` and exits 0.

Observed output:

```
NO_FINAL_NEWLINE 0
 'ts\tphase\tdecision\twhy\tevidence\tresult2026-09-08T13:33:50Z\tp\td\tw\te\tr\n'
row widths [11]
```

Impact: a valid header becomes a corrupt row, causing the next write to fail header validation. A final data row without LF would likewise concatenate with the next row; that case is inferred from the same append mechanism and was not separately run. This does not involve concurrency or violate the single-writer premise. Manual editing or external log tools can produce it.

Correction direction: inspect the last byte of a nonempty file before opening output. Explicitly reject missing LF without changing the file, or add a newline after validating structure. Test final row/column structure for header-only and existing-data inputs.

## Act on: P2, quoted cells are incompatible with the TSV reader used by existing tests

Locations: `log.sh:23–30,42`, with `csv.reader(..., delimiter='\t')` in `test_tools.py`.

With phase=`p`, decision=`"quoted decision"`, why=`"open quote`, evidence=`e`, and result=`r`, the script writes quotes directly and exits 0. Reading with the same csv.reader as existing tests removes decision's literal quotes, while the unclosed quote consumes evidence/result into why.

Actual parsed result:

```
['2026-09-08T13:33:50Z', 'p', 'quoted decision', 'open quote\te\tr\n']
```

Six intended columns become four, losing the correspondence between evidence and result. Quoting code or statements is ordinary log content; requiring callers never to use double quotes is not a valid solution.

Correction direction: define the TSV dialect. If retaining standard csv.reader behavior, use matching quoting/escaping when writing. If deliberately using plain tab separation with no quote semantics, document that reader contract and change test parsing; general import tools still need corresponding settings. Add round-trip checks for paired quotes, unmatched quotes, and cells after tab/newline sanitization.

## Act on: P2, missing resources in reference-style Markdown links falsely pass

Location: `shoshin/scripts/validate-skills.py:90–92`.

The validator recognizes only inline `[label](target)` and ignores valid reference-style Markdown. For example:

```markdown
Read [method][method].

[method]: references/missing.md
```

Even with no resource, actual `validate()` returns `[]`. The equivalent `[method](references/missing.md)` correctly reports missing resource. This makes declared-reference success misleading for skills using reference-style links.

To isolate link parsing, the reproduction injected `quick_validate=lambda _: (True, 'ok')`. Input still had name/description frontmatter. It did not claim full CLI/frontmatter validation. The defect occurs during link enumeration and does not depend on external owner paths.

Correction direction: resolve definitions and full/collapsed/shortcut references, or explicitly allow only inline syntax and reject reference syntax. Never silently ignore it and report passed references. Test both missing and existing targets.

## Dismissed and noted

- Dismissed repeated headers on every call: first-write/append tests passed; the script writes a header only for an empty file.
- Dismissed unhandled obvious formula prefixes: `= + - @` and leading whitespace already have sanitization/prefix protection, and existing tests passed. This is not a guarantee for every spreadsheet import mode.
- Dismissed a requirement for physical adjacency of external skills: frontmatter names map to actual owner paths, and the non-adjacent external-skill test passed.
- Dismissed symlink escape to arbitrary resources: resolved targets are checked with is_relative_to, and the escape test passed.
- Noted: single-writer behavior is explicit; no race was invented. Symlink log destinations and retry idempotency were not reviewed because authorized-use/contract evidence was insufficient; no hypothetical findings were reported.
- Noted: interrogate's default read-only review does not create experimental scripts. The parent explicitly authorized minimal /tmp fixtures here, so reproduction scripts and this report stayed within that scope.

## Reproducible evidence

Script: [shoshin-tools-probes.py](/tmp/shoshin-tools-probes.py). Commands:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/shoshin-tools-probes.py
PYTHONDONTWRITEBYTECODE=1 python3 /Users/triggerjames/Documents/sxl_code_work_space/agent-skills/shoshin/tests/test_tools.py
```

The first execution produced the three boundary failures and inline-link control above. The second reported `Ran 13 tests ... OK`. It used available system Python and PyYAML 6.0.3, without installing dependencies. `PYTHONDONTWRITEBYTECODE=1` prevented repository bytecode writes; fixtures were cleaned in TemporaryDirectory. The only retained review artifacts were the /tmp script and this report.

Review limits: this used an independent subagent context with the same model, not cross-family review or a permission-isolated environment. It shared the filesystem and potentially model biases; the parent still needed to verify findings. No other projects were read, no agents launched, no network used, and no source changed. Only specified tool tests and three boundary fixtures ran, not complete package validation or behavioral scenarios. Source locations reflect the review-time files and need rechecking after later edits.

Follow-up: the primary agent added the three defects to test_tools.py, recorded failures, then fixed them. The subsequent 16-test result is in tools-after.txt. The original findings remain as discovery history.
