# Ordinary edit forward-testing result

## Request

使用 $document-governance，把 docs/prd-v0.1.md 标题中的 knowlege 修正为 knowledge，其他内容不变。

## Actual workflow

Used candidate document-governance explicitly. Reused its SKILL.md already read during this trial context; additionally read references/validation-rules.md. Read the fixture AGENTS.md, which declares governance adoption. No interview was started and no requirement questions were asked, since this is a fully specified spelling edit. This is not a fresh-context routing test; inherited host skill descriptions remain present.

## Exact file diff

```diff
--- before/docs/prd-v0.1.md
+++ after/docs/prd-v0.1.md
@@ -6,6 +6,6 @@
 date: "2026-09-21"
 ---

-# Team knowlege base
+# Team knowledge base

 Documents belong to one workspace. Export policy is undecided.
```

## Verification actually run

- Before and after byte comparison of every fixture file: only docs/prd-v0.1.md changed, with exactly the specified heading replacement. No files added or removed in the fixture.
- Python version: 3.11.2.
- Validator command: `python3 -B /Users/triggerjames/Documents/sxl_code_work_space/agent-skills/document-governance/scripts/validate_docs.py /private/tmp/dg-integration-trials/ordinary --strict --format=json`
- Validator exit code: 1.

```json
{
  "root": "/private/tmp/dg-integration-trials/ordinary",
  "strict": true,
  "ok": false,
  "errors": [
    "missing required directory: docs/execution/specs",
    "missing required directory: docs/execution/plans",
    "missing required directory: docs/archive/specs",
    "missing required directory: docs/archive/plans",
    "missing required directory: docs/archive/runbooks",
    "missing required directory: docs/runbooks"
  ],
  "warnings": [],
  "summary": {
    "errors": 6,
    "warnings": 0
  }
}
```

Validator stderr:

```text

```

The fixture is not a Git repository; `git status --short` reported this, so no commit or Git diff was available. The byte comparison and unified diff above provide change evidence. No source skill or installation files were modified. Only the authorized fixture heading and this report were written. Validation used `-B` to avoid import bytecode writes.

## Actual final reply

已将 `docs/prd-v0.1.md` 的标题从 `Team knowlege base` 修正为 `Team knowledge base`，其余文件和该文件的其他内容保持不变。没有启动访谈。文档严格校验未通过；发现的是现有项目治理结构问题，未为此次拼写修正扩大修改范围。


## Coordinator fixture correction

The copy of the before snapshot contained files but omitted the empty governance directories. This was a trial setup defect, not a product defect. The coordinator restored the six required empty directories specified by the fixture contract and reran the same strict validator. Original failure evidence above is retained. No document assertion or validator rule was weakened.

```json
{
  "root": "/private/tmp/dg-integration-trials/ordinary",
  "strict": true,
  "ok": true,
  "errors": [],
  "warnings": [],
  "summary": {
    "errors": 0,
    "warnings": 0
  }
}
```

Display-only diff excerpts normalize whitespace-only context lines. The exact ADR diff is retained in `docs-round1.json`; original trial output remains in its recorded temporary path.
