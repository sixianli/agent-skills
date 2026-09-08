已完成指定工具的只读审查，发现 3 个真实可触发问题，均可在 /tmp 的最小样例复现。现有 `test_tools.py` 的 13 项测试实际执行且全部通过，说明这些边界未被现有用例覆盖，不代表工具全部行为已验证。未修改仓库文件。

审查意图：内外资源引用可解析；日志保护用户已有内容并保留可审阅的六列 TSV。遵循 interrogate SKILL.md 及 review-criteria.md，阅读两个工具、对应测试和 show-me-your-work 的使用合同。当前范围是新包未提交文件，git status 显示 shoshin/scripts、skills、tests 等未跟踪，未把它当作已有发布版本。

## 行动：P2，已有日志缺换行时追加破坏已有行

位置：`shoshin/skills/show-me-your-work/scripts/log.sh:16–22,40–43`。

脚本校验表头字符串但不检查末尾换行。用户已有文件仅为合法表头 `ts\tphase\tdecision\twhy\tevidence\tresult` 且末尾没有 LF 时，`read ... || true` 仍接受它；追加直接把时间戳接在 `result` 后，退出码为 0。

实际结果：

```
NO_FINAL_NEWLINE 0
 'ts\tphase\tdecision\twhy\tevidence\tresult2026-09-08T13:33:50Z\tp\td\tw\te\tr\n'
row widths [11]
```

影响：合法已有表头被改成损坏行，下一次写入将因表头不符而失败。已有最后一条数据缺 LF 时也会发生行拼接（后一场景由相同追加机制可推得，未另作运行）。这不是并发问题，不违反单一写者前提；手工编辑、外部工具保存日志即可出现。

修正方向：打开输出前检查非空文件最后字节；缺 LF 可以明确拒绝并保持原样，或在确认结构有效后单独补换行。新增观察最终行和列结构的测试，覆盖仅表头和已有数据两类输入。

## 行动：P2，引号字段与现有测试采用的 TSV 读取方式不兼容

位置：`log.sh:23–30,42`，对应 `test_tools.py` 的 `csv.reader(..., delimiter='\t')`。

输入 phase=`p`、decision=`"quoted decision"`、why=`"open quote`、evidence=`e`、result=`r` 时，脚本直接输出引号且退出 0。按现有测试同样的 csv.reader 读取，decision 的字面双引号消失；未闭合引号又把 evidence/result 吞进 why 单元格。

实际解析结果：

```
['2026-09-08T13:33:50Z', 'p', 'quoted decision', 'open quote\te\tr\n']
```

原本应为六列数据，却只剩四列，审阅证据和结果的对应关系丢失。引述代码或原话是日志的正常内容，无法靠调用者永远不写双引号解决。

修正方向：先明确 TSV dialect。若延续测试的标准 csv.reader 规则，用相匹配的 TSV writer 对引号字段引用和转义；若刻意定义纯 Tab 分隔、不支持引号语义，应同时明确读者契约并更改测试解析方式，但通用导入工具仍需相应设置。添加带成对引号、单边引号以及 Tab/换行清洗后字段的 round-trip 检查。

## 行动：P2，引用式 Markdown 的缺失资源得到假通过

位置：`shoshin/scripts/validate-skills.py:90–92`。

检查器只识别 inline `[label](target)`，完全忽略合法 Markdown reference-style 链接。例如 SKILL.md 正文：

```markdown
Read [method][method].

[method]: references/missing.md
```

即便资源不存在，实际 `validate()` 返回 `[]`；将同一内容改成 `[method](references/missing.md)` 就正确返回 missing resource。这会令“declared references passed”的成功输出对使用引用式链接的技能失真。

复现为了隔离链接解析，注入 `quick_validate=lambda _: (True, 'ok')`；输入仍具备 name/description frontmatter。未假称运行了完整 CLI/frontmatter 验证。问题发生在链接枚举阶段，不依赖外部 owner 路径。

修正方向：识别引用定义并解析 full/collapsed/shortcut reference links，或者明确只允许 inline 语法并对其他引用式语法报错；不能静默忽略后声称引用已通过。测试需要缺失和存在目标的对照。

## 驳回与记录

- 驳回“每次调用都会重复写表头”：现有 first-write/append 测试实际通过；脚本只在空文件写表头。
- 驳回“明显的公式前缀未处理”：`= + - @` 及前导空白已有清洗/前缀保护，实际现有测试通过。没有扩张为所有电子表格导入模式的安全保证。
- 驳回“外部技能必须物理相邻”：owner 由读取的 frontmatter name 映射实际路径，已有异地 external skill 测试实际通过。
- 驳回“符号链接可以越过 owner 引用任意资源”：目标 resolve 后检查 is_relative_to，现有逃逸测试实际通过。
- 记录：单一写者是明确合同；没有以并发竞争制造问题。未审查符号链接日志目标或重试幂等性，因为没有足够已授权用法/契约证据，不报假设性发现。
- 记录：interrogate 默认只读审查不创建实验脚本；此次上级明确授权 /tmp 最小样例，因此仅在该授权范围内写入复现脚本与报告。

## 可重跑证据

脚本：[shoshin-tools-probes.py](/tmp/shoshin-tools-probes.py)。执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/shoshin-tools-probes.py
PYTHONDONTWRITEBYTECODE=1 python3 /Users/triggerjames/Documents/sxl_code_work_space/agent-skills/shoshin/tests/test_tools.py
```

第一次实际执行输出上述三个失败边界及 inline 链接对照；第二次输出 `Ran 13 tests ... OK`。使用系统可用 Python 和 PyYAML 6.0.3，没有安装依赖。`PYTHONDONTWRITEBYTECODE=1` 防止在仓库写入字节码缓存，样例都在 TemporaryDirectory 中清理。唯一保留的审查产物是 /tmp 脚本和此报告。

审查限制：这是同模型的独立子代理上下文审查，既不是跨模型家族评审，也不是由权限隔离的独立运行环境。共享同一文件系统，可能共享模型偏差；上级仍需核实发现。未读取其他项目、未启动其他 agent、未联网、未修改源码。未执行全部包校验或行为场景，只运行指定工具测试与三个边界样例；报告位置基于本次读取时的源码，后续主任务修改后应复查行号与是否仍可触发。

后续：主 agent 已将 3 个问题加入 test_tools.py，先记录失败再修正；修复后的 16 项结果见 tools-after.txt。原审查结论保留作为发现历史。
