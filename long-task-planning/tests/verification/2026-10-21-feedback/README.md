# 第三轮反馈处理验证记录（2026-10-21）

本文记录 `long-task-planning` skill 按 S3-F21、S3-F22 两条反馈修改后的验证方法和结果。改动说明在 [SKILL.md 的 Documentation-only changes](../../../SKILL.md#documentation-only-changes)，文件和检查字段在 [formats.md](../../../references/formats.md)。含项目细节的失败日志和报告只留在维护者本机，不进 git。

- [怎么重跑](#怎么重跑)
- [改了什么](#改了什么)
- [测试方法](#测试方法)
- [红绿记录](#红绿记录)
- [结果](#结果)
- [没有验证的](#没有验证的)

## 怎么重跑

在仓库根目录运行，需要 Python 3.10 以上，只用标准库。

只跑本轮新增的测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k never_committed_alone
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k ignore_test_exclude
```

完整测试和报告：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 long-task-planning/tests/junit_report.py --start long-task-planning/tests --out <报告路径>.xml
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 long-task-planning/tests/junit_report.py --start codex-orchestration/tests --out <报告路径>.xml
```

变异检查（故意把实现改坏，确认对应测试会失败）：

```bash
python3 long-task-planning/tests/mutate.py
```

[返回目录](#第三轮反馈处理验证记录2026-10-21)

## 改了什么

- **S3-F21**：在本机记录测试或命令时，如果 `fingerprint.test_exclude` 非空，记录里多存两个字段：`code_fingerprint`（去掉 `test_exclude` 路径后的摘要）和 `test_exclude`（排序后的列表）。按提交找不到受测内容时，只要这两个字段还在、列表没变、摘要和现在一致，测试证据仍算当前版本，变更文件只列 `test_exclude` 下的路径。测试先于代码提交、之后又改文档再一起提交的场景因此不再被判成旧版本。`--fingerprint-file` 记录和旧记录没有这两个字段，行为不变。
- **S3-F22**：命令类完成条件可以写 `"ignore_test_exclude": true`，通过时按测试检查的规则认 `test_exclude`。不写或写 `false` 时行为完全不变。`lint` 拒绝非布尔值，以及和 `"scope": "environment"` 同时出现。
- **文档**：更新 `SKILL.md` 的 `Documentation-only changes` 一节和 Completion conditions 表里命令检查那一行；更新 `references/formats.md` 的记录字段、检查字段和 `status --json` 说明。
- **测试**：`TestExcludeTests` 新增 5 个含 `never_committed_alone` 的测试和 3 个含 `ignore_test_exclude` 的测试，`LintTests` 新增 2 个含 `ignore_test_exclude` 的测试。`mutate.py` 从 164 个变异增加到 172 个。

[返回目录](#第三轮反馈处理验证记录2026-10-21)

## 测试方法

- 先写测试，在未修改的 `longtask.py` 上运行，确认失败原因就是两个缺陷：记录里没有新字段、只改文档后状态是旧版本而不是当前版本、失败记录的原因里没有记录编号、`lint` 对非法开关值不报错。失败输出按条目分别保存在 `red-f21.log` 和 `red-f22.log`。
- 修复前后都通过的命令类对照用例保留不动：记录后改 `test_exclude` 之外的代码仍是旧版本；`test_exclude` 为空时记录不带新字段；没有开关时只改文档仍是旧版本。它们在修复前就通过，用变异检查证明它们守得住。
- 新增用例都走命令行入口（`record`、`status`、`lint`），不直接调用内部函数。同一入口、同一结果的多个输入用 `subTest` 表驱动。
- 每个新行为都有变异覆盖：新字段比较恒真、`test_exclude` 列表比较被去掉、变更文件列表不再限制在 `test_exclude` 下、未提交记录的说明文字被隐藏、命令开关总是认、命令开关总是不认、`lint` 不检查开关类型、`lint` 不检查开关与环境检查的组合。全量变异要求每个都被测试发现。
- 现有测试的期望值没有修改，特别是 `test_commands_and_reviews_ignore_test_exclude`、`test_evidence_recorded_before_its_commit_is_relaxed_from_that_commit`、`test_uncommitted_or_unknown_test_records_are_not_relaxed`。

[返回目录](#第三轮反馈处理验证记录2026-10-21)

## 红绿记录

修复前（红）：

| 命令 | 结果 |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k never_committed_alone` | `Ran 5 tests`，`FAILED (failures=2, errors=1)` |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k ignore_test_exclude` | `Ran 6 tests`，`FAILED (failures=5)` |

修复后（绿）：同样两条命令分别 `Ran 5 tests` 和 `Ran 6 tests`，都是 `OK`。红运行时通过的对照用例见[测试方法](#测试方法)。

[返回目录](#第三轮反馈处理验证记录2026-10-21)

## 结果

最后一次完整运行在写完本文之后，结果如下：

| 检查 | 结果 |
| --- | --- |
| `long-task-planning/tests` | 通过 131，失败 0，出错 0，跳过 0 |
| `codex-orchestration/tests` | 通过 9，失败 0，出错 0，跳过 0 |
| 变异检查 | `172 of 172 mutants run, survived: []` |

报告和日志分别保存在本机的 `.agents/local/reports/s3-ltp.xml`、`.agents/local/reports/s3-codex.xml`、`.agents/local/reports/s3-mutate.log`。另外在 Python 3.11 下单独跑过两条新增测试命令，分别 `Ran 5 tests` 和 `Ran 6 tests`，都是 `OK`。

[返回目录](#第三轮反馈处理验证记录2026-10-21)

## 没有验证的

- 只在 macOS 上跑过。完整测试用 Python 3.14.7；新增测试另外用 Python 3.11.15 跑过。更低版本和 Linux、Windows 没有跑。
- `--fingerprint-file`（在别的机器上算指纹）不写新字段，只由“旧记录没有新字段、行为不变”的测试覆盖；没有在真实的另一台机器上跑。
- 新字段只覆盖测试和命令记录；审核、文档和环境检查仍不认 `test_exclude`，本轮没有改这些路径。
- 没有提交、推送或建立分支；本文描述的是工作区里的结果。

[返回目录](#第三轮反馈处理验证记录2026-10-21)
