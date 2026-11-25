# Validation Rules

Read this file before running, interpreting, or modifying
`scripts/validate_docs.py`.

## Modes

The validator defaults to migration-friendly mode. Structural adoption issues
are warnings so an existing repository can be assessed without immediately
blocking all work.

- `--strict` (alias `--ci`) promotes every migration-friendly warning to an
  error and returns a nonzero exit code. Use it for governed repositories, CI,
  and completion checks.
- `--format=json` emits one JSON object without changing exit behavior.
- `scripts/runbook.py check` is an execution gate, not a migration audit. It
  treats every Runbook finding as blocking and has no compatibility mode.

## Always-Error Checks

These conditions fail in every mode:

- `status` is present but is not `active`, `superseded`, or `archived`.
- An archived document has `status: active`.
- An active Spec or Plan has `status: archived`.
- A local SOURCE target is absolute or contains `..` path traversal.
- A `covers` entry is absolute, starts with `~`, contains `..`, or is a URL.
- A governed Markdown file or SOURCE compatibility target resolves through a
  symbolic link outside the project's `docs/` directory.
- The supplied project root does not exist or is not a directory.
- A governed Markdown file is not valid UTF-8 or cannot be read (a UTF-8 BOM
  is accepted), or is a symbolic link that does not resolve (broken or
  looping).
- An active Runbook declares an invalid `execution_risk`.
- An active Runbook uses `last_reviewed` or `review_after` as calendar trust.

## Migration Warnings / Strict Errors

- A required governance directory is missing.
- `docs/ideas/` and `docs/backlog/` are created on first use;
  empty optional directories are not required because Git does not preserve
  them.
- A governed Markdown document has missing, unterminated, malformed, nested,
  duplicate, or multiline frontmatter.
- Frontmatter lacks `status`, `supersedes`, `superseded_by`, or `date`; an
  empty `status` or `date` counts as missing. ADRs do not need
  `superseded_by`.
- `date` is not `YYYY-MM-DD`.
- A document in archive is not marked `status: archived`.
- An active Spec or Plan is marked `status: superseded` instead of being
  closed and archived.
- A `document_type`, when present, conflicts with the document's governed
  directory, or `document_type: lessons` is not `docs/lessons.md`, or
  `document_type: prd`/`architecture` is not `docs/prd-v<version>.md` /
  `docs/architecture-v<version>.md`.
- A structured Idea/Backlog record has a missing, duplicate, malformed, or
  path-inconsistent `record_id`, `document_type`, or `record_state`. Both
  `IDEA|BL-YYYYMMDD-NNN` (legacy) and `IDEA|BL-YYYYMMDD-xxxxxx` (6 chars from
  `23456789abcdefghijkmnpqrstuvwxyz`) are valid. Every Markdown file in
  `docs/ideas/` or `docs/backlog/` is a record; non-record notes belong
  elsewhere. Duplicate detection covers active and archive record dirs.
- An archived record in `docs/archive/ideas/` or `docs/archive/backlog/` has a
  non-terminal `record_state` (Idea: closed, promoted, superseded; Backlog:
  done, rejected, converted, superseded). Archived records keep
  `status: archived`.
- An Idea/Backlog field such as `record_id`, `date`, or `updated` still holds
  template text (`unfilled template placeholder`).
- A Backlog omits any field in its complete template header, uses a priority
  other than `urgent`, `high`, `normal`, or `low`, or has an empty
  `item_type`.
- A promoted/converted record lacks a valid `promoted_to`; a deferred Backlog
  lacks `review_after` or `reason`; or a terminal record lacks its required
  result, reason, or successor.
- An ADR lacks `decision_status` or uses one other than `proposed` or
  `accepted`.
- An ADR is marked `status: superseded` or `decision_status: superseded`, sets
  a non-empty `superseded_by`, or lives under `docs/archive/adr/`: replaced and
  stale ADRs are deleted.
- An accepted ADR's `supersedes` names a local ADR that still exists, names a
  local path that no longer exists, or is a URL without a commit hash (7-40
  hex characters) as a path segment. A replaced ADR is linked by a permalink
  pinned to a commit. A `proposed` ADR may name an existing local ADR, which
  stays in force until the replacement is accepted.
- `implementation` has a value other than `in_progress`.
- `verified_at` is not a 7-40 character lowercase hex commit hash, or `covers`
  is non-empty and `verified_at` is missing.
- Code references (the hard gate, below) are missing from the current tree.
- A legacy Plan has neither a heading matching `#+ Source Spec` nor a SOURCE
  reference into `docs/execution/specs/` or `docs/archive/specs/`.
- A SOURCE target does not exist under `docs/`; when the missing target
  contains a template placeholder (`YYYY`, `NNNN`, `X.Y`, `<...>`, `{{...}}`)
  it is reported as `unfilled template placeholder in SOURCE target`.
- An old active Runbook lacks `document_type: runbook`, `execution_risk`, or
  a required Runbook section.
- `docs/runbooks/` contains a superseded or archived Runbook rather than only
  active entries.
- An archived Runbook lacks `document_type: runbook`, has a broken reciprocal
  relationship, or has neither a successor nor `archive_reason`.

Strict mode must leave these findings in `errors`, not `warnings`; a strict run
with any such finding must report `ok: false` and return exit code 1.

## Skill Policy Notices

A file named `TODO.md` or `INDEX.md` anywhere under `docs/` is not a governed
document. The validator reports it once as a warning in every mode, including
`--strict`, and does not check its frontmatter: this skill does not maintain
these files and must not delete them, so their presence must not block strict
validation. Offer to migrate their items into Backlog records.

## Code References (Hard Gate)

Every active document under `docs/` that is not a Spec, Plan, Idea, Backlog
record, or archived file is checked against the current tree. The tree is the
files `git ls-files --cached --others --exclude-standard` lists, or every file
outside `.git`, `node_modules`, and virtual environments when the project is
not a git working copy. Missing references are migration warnings and strict
errors, except in a document with `implementation: in_progress`, where they are
always warnings.

- Each `covers` entry must match at least one file or directory.
- Inline code in prose (not fenced blocks):
  - A path with a `/` is checked when it starts with `./`, its first segment
    is a top-level entry of the project, or its extension is one the project
    uses. It passes when it exists, when a glob matches, or when a tracked path
    ends with it (paths relative to a sub-package). Line suffixes such as
    `:12` or `#L5` are ignored. Home-directory, absolute, URL, and
    placeholder paths, hidden directories that are not in the project, and
    paths git ignores (build output) are skipped.
  - A call such as `renderPage()` or `api.client.send()` must name an
    identifier that appears in a non-Markdown file outside `docs/`.
  - An environment-style key such as `API_TOKEN_NAME` must appear the same way.
  - A dotted key that starts lowercase and has a camelCase segment, such as
    `runPolicy.inbox`, must have every segment appear the same way. A dotted
    name ending in a project file extension is treated as a file name.
  - `npm|pnpm|bun|yarn run <script>` must name a script in some
    `package.json`; `make <target>` must name a target when the project has a
    Makefile; `python3|node|bash|... <path>` checks the path.
- Each line of a fenced block is checked only as a command, as above.
- `docs/.governance-references-ignore` lists, one per line, exact references or
  `fnmatch` patterns to skip, such as an upstream project's file paths or
  platform API names. Blank lines and `#` lines are ignored.

The gate cannot tell whether a sentence about an existing file is still true;
the drift audit covers that.

## SOURCE Resolution

- Resolve `docs/...` from the project root.
- Resolve paths without the `docs/` prefix from the project `docs/` directory.
- Never fall back to a same-named file at the project root.
- Recognize missing `docs/execution/specs|plans/X`, `docs/ideas/X`, and
  `docs/backlog/X` paths whose files moved to the matching `docs/archive/...`
  directory. This applies to SOURCE links and to the record fields
  `promoted_to`, `source_idea`, `superseded_by`, and `supersedes`.
- Recognize a missing legacy active Runbook path when there is an exact
  undated archive match or exactly one dated archive match, keeping the
  subpath under `runbooks/` (a date prefix applies to the filename only). Multiple dated
  matches are ambiguous and require an exact archive SOURCE path.
- Do not map ADR paths to `docs/archive/adr/`; ADRs are deleted, not archived.
- Skip external HTTP(S) URLs after enforcing local path-boundary rules.
  Placeholder-looking targets are not skipped: they pass when the file
  exists and are otherwise reported as unfilled template placeholders.
- Do not validate heading anchors.

## Files Considered

- Scan all `*.md` files under the target project's `docs/` tree.
- Skip `docs/templates/**` because it may contain unfilled placeholders.
- Skip every path listed in `docs/.governance-exclude`, a project file with one
  repo-relative path per line, for example `docs/ocr-eval`. Blank lines and
  lines starting with `#` are ignored. Use it for Markdown that is not
  project documentation, such as generated reports or store copy.
  - A path must be relative, start with `docs/`, and contain no `..`;
    otherwise it is an error.
  - `docs` itself, `docs/adr`, `docs/execution`, `docs/runbooks`,
    `docs/ideas`, `docs/backlog`, `docs/archive` and anything under them, and
    `docs/lessons.md`, `docs/prd-v*.md`, `docs/architecture-v*.md` cannot be
    excluded; listing one is an error.
  - A listed path that does not exist is a migration warning and a strict
    error, so a stale entry is noticed.
- Do not scan the skill's own `assets/templates/**` when validating a project.
- Open records and overdue `review_after` dates are work state, not validation
  failures. Use `scripts/idea_backlog.py review` to surface them.
- The validator can enforce the location and frontmatter shape of
  `docs/lessons.md`, but it cannot prove that an entry represents a repeated
  coding-agent mistake. Review that semantic boundary manually.
- Validate the structure of active Runbooks using the shared `runbook.py`
  logic: location, lifecycle fields, `execution_risk`, and required sections.
  The validator does not compare a Runbook with the sources it depends on;
  the executing agent does that before each use. A legacy `contract_sha256`
  field or `runbook-contract` block is ignored. For archived Runbooks,
  validate historical location, status, type, and relationships.
- There is no date-based Runbook expiration. Backlog `review_after` remains a
  work-state field and is not a Runbook trust signal.

## Coverage Tracking

`scripts/doc_coverage.py` reads `covers` and `verified_at`; it never fails a
build.

- `changed --base <ref> [--head <ref>] [--format text|json|github]` lists
  documents whose covered code changed in `<base>...<head>` while the document
  did not. It always exits 0.
- `audit [--format text|json]` lists documents whose covered code changed since
  `verified_at`, counting committed and uncommitted changes but not changes in
  a commit that also changed the document. It lists documents without `covers`
  separately, and reports a `verified_at` that is not in local history (for
  example in a shallow clone).
- `stamp <document>... [--commit <ref>]` writes the full commit hash into
  `verified_at`.

## What the Validator Cannot Prove

The validator cannot prove semantic consistency between code and prose,
confirm that a Spec matches its Plan, determine whether a code change required
a PRD update, or prove that work is truly closed. Inspect repository evidence
and complete the workflow checklist before declaring semantic or release
readiness.

The validator also cannot classify the real commands or live target for an
execution. `execution_risk` is only a declared protection floor. The executing
agent must raise risk from current commands and preflight and enforce the
mutation-boundary authorization described in `references/runbook-workflow.md`.
