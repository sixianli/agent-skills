# File formats

Back to [SKILL.md](../SKILL.md). All files live in `<repo>/.agents/tasks/<task>/` and are UTF-8.

- [goal.md](#goalmd)
- [items.json](#itemsjson)
- [plan.md](#planmd)
- [evidence.jsonl](#evidencejsonl)
- [Fingerprint](#fingerprint)
- [status --json](#status---json)

## goal.md

```markdown
# 目标：round2

## G1 2026-09-28 转述：.ci-output/handoff/2026-09-28-codex-round2-brief.md

> 尽量把工具执行相关的缺陷全部找出来

## G2 2026-09-29 用户原话

> 把一经发现的bug修掉然后再收尾吧

## CLOSED 2026-10-20 用户原话

> 验收通过
```

- Headings match `## G<number> <YYYY-MM-DD> <source>` or `## CLOSED <YYYY-MM-DD> <source>`. Source is `用户原话` or `转述：<where from>`.
- The quote lines start with `> `. IDs are unique; `CLOSED` is last and makes the task inactive.
- Append only: every committed version and the working copy must start with the previous version's lines.

## items.json

```json
{
  "task": "round2",
  "prefix": "R2",
  "fingerprint": {"test_exclude": ["docs/", "AGENTS.md"]},
  "items": [
    {
      "id": "R2-D1",
      "title": "Job Host 期限分类",
      "goal_ref": ["G2"],
      "done_when": [
        {"type": "test", "tag": "R2-D1", "host": "test-server"},
        {"type": "review", "by": "claude"}
      ],
      "added": {"by": "claude", "on": "2026-10-02", "why": "第二轮缺陷清单 D1"}
    },
    {
      "id": "R2-L4",
      "title": "生产部署",
      "goal_ref": ["G3"],
      "done_when": [{"type": "user", "ref": null, "question": "什么时候部署到生产？"}],
      "added": {"by": "claude", "on": "2026-10-02"},
      "withdrawn": {"on": "2026-10-05", "ref": "G7"}
    }
  ]
}
```

- `prefix`: letters and digits, starting with a letter. Every `id` starts with `<prefix>-`.
- `fingerprint.exclude`: path prefixes left out of the fingerprint for every check. Add one only after checking that no test, command or review depends on those paths.
- `fingerprint.test_exclude`: path prefixes that only test checks ignore, for documents no test reads. See [Documentation-only changes](../SKILL.md#documentation-only-changes). It does not change the fingerprint.
- Check fields: `test` needs `tag`, or both `file` and `name` (`name` appears verbatim in the file and in the reported names, with no placeholder such as `%s`); `doc` needs `path`, optional `heading`; `review` optional `by`; `user` needs `ref` (null until decided) and `question`; `command` needs `run`. `test` and `command` accept `host`.
- `lint` compares with the version in `HEAD`: a removed item, or a changed `done_when` / `withdrawn` without a new `计划改动记录` line naming the item, is an error.

## plan.md

```markdown
# 计划：round2

## 当前批次

- R2-D2：先写红测试复现 ACK 丢失，再修；证据：云服务器上 [R2-D2] 全过 + Claude 审核
- R2-E1：……

## 之后

- R2-D13
- R2-B4

## 计划改动记录

- 2026-10-02 10:00 建立任务。
- 2026-10-02 11:30 当前批次改为 R2-D2、R2-E1。原因：status 显示 未完成 12、无法判断 0。

## 意外和发现

- 2026-10-02 D17：夹具套接字路径超过 107 字节。

## 决定

- 2026-10-02 D18 不在本批修，见 BL-20261002-002。
```

- The five `##` sections are required. `当前批次` lists at most three item IDs (one bullet each).
- No checkboxes or status words outside the last three sections. HTML comments are ignored.
- The last three sections are append only, checked against git history.

## evidence.jsonl

One JSON object per line, appended under a file lock. Common fields:

| Field | Meaning |
| --- | --- |
| `id` | `E<YYYYMMDD>T<HHMMSS>-<6 hex>` |
| `time`, `by`, `host` | When, which agent, which machine |
| `kind` | `test`, `command`, `review` or `retract` |
| `fingerprint`, `commit`, `dirty` | The code it applies to; `dirty` means uncommitted changes existed. `fingerprint` is `unknown` for results recorded without one; each such record is judged on its own |
| `note` | Optional free text |

Kind-specific fields:

- `test`: `source` (`vitest-json` or `junit-xml`), `counts` `{passed, failed, skipped}`, `tags` `{TAG: {passed, failed, files}}` (skipped tests excluded), `selected` (results for `file`+`name` checks), `failures` (first 20 names), `artifacts` `[{path, sha256}]`, optional `ran`, `ran_at` (when the tests ran, from the report) and `unresolved_files`.
- `command`: `command`, `exit_code`, optional `artifacts`.
- `review`: `items`, `verdict`, `files` `{path: git blob hash at review time}`, optional `reviewed_commit` (recorded with `--commit`; the hashes then come from that commit). `files` is `{}` for a `--no-files` review; its `note` says what was reviewed.
- `retract`: `target` (an evidence id), `reason`. The target stops counting; the failure or pass it recorded is ignored.

## Fingerprint

1. Start from the index (`git ls-files -s`), skipping the task directory, `fingerprint.exclude` prefixes and `.DS_Store`, `Thumbs.db`, `._*`.
2. Re-hash files that differ from the index (`git diff-files`) and untracked files git does not ignore; drop deleted files. Modes are `120000` (symlink), `100755` (executable) or `100644`.
3. Sort lines `<mode> <blob> <path>` by path, join with `\n`, SHA-256. `fingerprint --list` prints these lines.
4. `dirty` is true when the same computation over `HEAD`'s tree gives a different value.

Same content gives the same fingerprint on any machine and whether or not it is committed.

## status --json

```json
{
  "task": "round2", "dir": ".agents/tasks/round2",
  "fingerprint": "…", "commit": "…", "dirty": false,
  "counts": {"verified": 3, "older": 5, "not_done": 12, "unknown": 1, "waiting": 0, "withdrawn": 1},
  "items": [{"id": "R2-D4", "title": "…", "status": "unknown", "reasons": ["…"], "changed_files": [], "checks": [{"type": "test", "status": "unknown", "reason": "…", "changed_files": []}]}],
  "changes_since_last": [{"id": "R2-D1", "from": "verified", "to": "older"}],
  "warnings": []
}
```

- `reasons`: for an unfinished item, one line per check not yet verified on the current code, worst first; for a verified item, its checks.
- `changed_files` of an item: files changed since the older evidence of any check that is not verified.
- `changed_files` of a check: the files behind its status. For a test check verified under `test_exclude`, the files changed since the tested commit, all under `test_exclude`.
