# 第三轮反馈 F23 决策文档验证记录（2026-10-21）

本文记录 `long-task-planning` skill 按 S3-F23 修改后的验证方法和结果：每条 `goal.md` 原话在 `items.json` 的 `decisions` 里分类，长期决定必须有带原话核对的文档条目。用法说明在 [SKILL.md 的 Long-term decisions](../../../SKILL.md#long-term-decisions)，文件和检查字段在 [formats.md](../../../references/formats.md)。含项目细节的失败日志和报告只留在维护者本机，不进 git。

- [怎么重跑](#怎么重跑)
- [改了什么](#改了什么)
- [测试方法](#测试方法)
- [新增测试的价值](#新增测试的价值)
- [红绿记录](#红绿记录)
- [结果](#结果)
- [没有验证的](#没有验证的)

## 怎么重跑

在仓库根目录运行，需要 Python 3.10 以上，只用标准库。

只跑本轮新增的测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k durable_decision
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

只跑其中几个时把名字写在后面，例如 `python3 long-task-planning/tests/mutate.py "init writes no decisions"`。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 改了什么

- **S3-F23**：`items.json` 新增可选键 `decisions`（G 编号到 `"once"` / `"durable"`）和 `decision_docs`（决策文档路径前缀，默认 `["docs/adr/"]`）。有 `decisions` 时，`lint` 报告没分类的原话、没有合格文档条目的长期决定、把 `durable` 改回 `once` 或删掉却没有计划记录、整个删掉 `decisions` 键却没有计划记录，以及类型写错。合格条目指没有 `withdrawn`、`goal_ref` 含这条 G、`done_when` 里有路径在 `decision_docs` 下且 `quotes` 含这条 G 的 `doc` 检查。
- **原话核对**：`doc` 检查新增可选 `quotes`（一个 G 编号或列表）。文件存在且 `heading` 满足后，`quotes` 里的 G 必须在 `goal.md` 里存在；其原话和文档全文都去掉行首空白和 `>`，再去掉所有空白后比较，文档不含原话时条目为未完成。用户选择条目的问题行不算原话，所选项的标签和说明才算。
- **可见性**：`status --json` 的 `warnings` 和会话开始注入的 `context` 都显示“没分类”和“长期决定没有文档条目”；`context` 的那一行在长度预算内，空间不够时截断而不是整行去掉。
- **init**：新任务在 `items.json` 里写 `"decisions": {"G1": "once"}`，并提示 G1 若是长期规则要改成 `durable`。
- **测试和文档**：`DecisionTests` 新增 11 个含 `durable_decision` 的测试；`Base.init_task` 只在测试没有显式给 `decisions` 时删掉 init 写入的键，现有测试的断言没有改。`mutate.py` 从 172 个变异增加到 186 个。更新 `SKILL.md` 的目录、Full mode files 表、Completion conditions 表和新的 Long-term decisions 一节，更新 `references/formats.md`。

没有提交、推送或建立分支；本文描述的是工作区里的结果。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 测试方法

- 先写测试，在未修改的 `longtask.py` 上运行：`lint` 不报分类问题、`init` 不写 `decisions`、`status` 的文档检查不看 `quotes`、`context` 不显示长期决定。确认失败原因都是功能还没有，再改实现。
- 新增用例都通过命令行入口（`init`、`lint`、`status --json`、`context`），不直接调用内部函数。同一入口、同一结果的多个输入用 `subTest` 表驱动。
- `test_task_without_durable_decision_key_keeps_old_behaviour` 是旧行为对照：修复前就应当通过，修复后仍然通过。它守的是“没有 `decisions` 键的任务行为完全不变”。
- `test_durable_decision_needs_a_qualified_item` 在同一个未提交的任务里依次改 `items.json`，覆盖没有条目、路径不在 `decision_docs` 下、`quotes` 缺失、条目已 `withdrawn` 四种情况，最后再覆盖合格条目通过。
- 每个新行为都有变异覆盖：没分类不报错、长期决定没有合格条目不报错、原话核对恒为真、不去空白、不去 `>`、`decision_docs` 前缀不检查、改回 `once` 不要求记录、G 编号按子串匹配、`init` 不写 `decisions`、没有 `decisions` 键也做检查、删掉 `decisions` 键不要求记录、未知的 `quotes` G 被接受、`decisions` 值不检查、`decision_docs` 类型不检查。全量变异要求每个都被测试发现。
- 现有测试的期望值没有修改。`Base.init_task` 的调整只影响测试准备：没有显式给 `decisions` 时删掉 init 新写入的键。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 新增测试的价值

| 测试 | 入口与可观察结果 | 依据 | 现有覆盖的缺口 | 最小失败输入 | 层 | 单独运行 |
| --- | --- | --- | --- | --- | --- | --- |
| `test_init_writes_durable_decision_default` | `init` 写 `decisions: {"G1": "once"}`，输出含 `G1 先记为 once`，`lint` 通过 | 规则 F | 现有 InitTests 只检查文件存在和旧的 items 字段 | 新任务 items.json 没有 `decisions` | 命令行 | 0.46 s |
| `test_unclassified_durable_decision_is_reported` | `lint` 失败并点名 G2；`status --json` 的 warnings 含 G2；`context` 含“长期决定”和 G2 | 规则 B2、D、E | LintTests 不检查 `decisions`；ContextHookTests 不检查长期决定 | 只有 G1 分类，追加 G2 | 命令行 | 0.99 s |
| `test_invalid_durable_decision_fields_fail_lint` | 值 `maybe`、键 `G9`、`decision_docs` 写成字符串，各自 `lint` 失败 | 规则 B1 | 没有 `decisions` 类型检查的测试 | `{"decisions": {"G1": "maybe"}}` | 命令行 | 1.45 s |
| `test_durable_decision_needs_a_qualified_item` | 四种不合格条目都让 `lint` 点名 G2；合格条目通过；没有条目时 warnings 和 `context` 也显示 G2 | 规则 B3、D、E | 没有“长期决定必须有文档条目”的测试 | G2 为 `durable`，items 为空 | 命令行 | 1.66 s |
| `test_durable_decision_quote_must_appear_verbatim` | 文档不存在、文档没有原话 → `not_done`；原话换行、加 `> `、加空格 → `verified` | 规则 C | StatusTests 的 `test_doc_check` 只检查文件与标题 | 文档存在但不含 G2 原话 | 命令行 | 1.11 s |
| `test_durable_decision_quote_needs_a_known_goal` | 文档存在，`quotes` 写 `G8` → 条目 `unknown` | 规则 C | 没有未知 `quotes` G 的测试 | `quotes: "G8"` | 命令行 | 0.54 s |
| `test_durable_decision_docs_prefix` | `decision_docs: ["AGENTS.md"]` 时 `AGENTS.md` 条目合格；默认前缀下不合格 | 规则 A、B3 | 没有自定义决策文档前缀的测试 | 默认前缀下的 `AGENTS.md` 条目 | 命令行 | 1.37 s |
| `test_durable_decision_downgrade_needs_a_plan_record` | 从 `durable` 改成 `once`：没有记录失败；只提 G21 仍失败；提到 G2 通过 | 规则 B4 | 现有测试只覆盖完成条件和条目删除，不覆盖 `decisions` | 提交 `durable` 后改成 `once`，计划无新行 | 命令行 | 1.26 s |
| `test_removing_durable_decision_key_needs_a_plan_record` | 删掉整个 `decisions` 键：没有记录失败；新记录含 `decisions` 通过 | 补充分支（规则 B4） | 没有“删键退回未启用”的测试 | HEAD 有 `decisions`，工作区删掉 | 命令行 | 0.85 s |
| `test_task_without_durable_decision_key_keeps_old_behaviour` | 没有 `decisions` 键时追加未分类的 G2，`lint` 通过 | 规则 A 的旧任务分支 | 没有“未启用时行为不变”的测试 | G1、G2 都未分类且没有 `decisions` | 命令行 | 0.57 s |
| `test_selected_durable_decision_quote_uses_the_answer` | ADR 只有问题行 → `not_done`；含所选项两行 → `verified` | 规则 C、附录第 10 条 | 没有“用户选择条目原话不含问题行”的测试 | ADR 只写 `问题：…` | 命令行 | 0.76 s |

每项都在本机单独运行过，最长 1.66 秒，均在 2 秒内。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 红绿记录

修复前（红）：

| 命令 | 结果 |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py -k durable_decision` | `Ran 10 tests`，`FAILED (failures=15)` |
| 补充“删掉 `decisions` 键要记录”后，同一条命令 | `Ran 11 tests`，`FAILED (failures=1)` |

第一次红运行时 `test_task_without_durable_decision_key_keeps_old_behaviour` 通过，符合预期：它守的是旧行为。整套测试在红运行时除了 `DecisionTests` 之外没有失败或出错。

修复后（绿）：

| 命令 | 结果 |
| --- | --- |
| 同一条 `-k durable_decision` 命令（Python 3.14.7） | `Ran 11 tests`，`OK` |
| 同一条命令（Python 3.11.15） | `Ran 11 tests`，`OK` |
| `python3 -m unittest discover -s long-task-planning/tests -p test_longtask.py`（只跑 `test_longtask.py`） | `Ran 138 tests`，`OK` |
| `PYTHONDONTWRITEBYTECODE=1 python3 long-task-planning/tests/junit_report.py --start long-task-planning/tests --out <报告路径>.xml`（跑 `long-task-planning/tests` 下全部测试文件） | `通过 142，失败 0，出错 0，跳过 0` |

上面 138 是只跑 `test_longtask.py` 的数字；最终报告跑的是 `long-task-planning/tests` 下全部测试文件，所以是 142（上一批 131 加本轮新增 11）。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 结果

最后一次完整运行的结果：

| 检查 | 结果 |
| --- | --- |
| `long-task-planning/tests`（`junit_report.py --start long-task-planning/tests`，全部测试文件） | 通过 142，失败 0，出错 0，跳过 0 |
| `codex-orchestration/tests`（`junit_report.py --start codex-orchestration/tests`） | 通过 9，失败 0，出错 0，跳过 0 |
| 变异检查（`python3 long-task-planning/tests/mutate.py`） | `186 of 186 mutants run, survived: []` |

报告和日志保存在本机的 `.agents/local/reports/s3b-ltp.xml`、`.agents/local/reports/s3b-codex.xml`、`.agents/local/reports/s3b-mutate.log`；红运行输出在 `.agents/local/red/red-f23.log`。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)

## 没有验证的

- 只在 macOS 上跑过。完整测试用 Python 3.14.7；新增测试另外用 Python 3.11.15 跑过。更低版本和 Linux、Windows 没有跑。
- 没有在真实项目上盘点并把旧任务升级为带 `decisions` 的任务；本轮只验证脚本和文档，没有生成 ADR 本身。
- 没有和 `document-governance` 的实际调用一起跑；只验证了 `doc` 检查能核对 ADR 路径和原话。
- 没有提交、推送或建立分支；本文描述的是工作区里的结果。

[返回目录](#第三轮反馈-f23-决策文档验证记录2026-10-21)
