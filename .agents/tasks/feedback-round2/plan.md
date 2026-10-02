# 计划：feedback-round2

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- S2-F20a：append_only_errors 对 evidence.jsonl 改用“旧版本每一行在新版本里原样存在、相对顺序不变”，goal.md 和 plan.md 日志仍要求旧内容是新内容的开头；证据：三个新测试先失败后通过，变异检查
- S2-F20b：Evaluation 读取记录后按 time 稳定排序，time 读不出来时 load_records 报错；证据：三个新测试先失败后通过，变异检查
- S2-F19：check-brief 从标题含“范围”的一节里取以编号开头（可带反引号）的列表行作为本批条目，空、超过 3 个、不存在、已撤回都拒绝，别处不存在的编号拒绝、已撤回的只警告；同步 SKILL.md 和简报模板；证据：新测试先失败后通过，变异检查

## 之后

- S2-F18a：fingerprint.include，lint 检查每个路径都存在，status 显示只看的路径，fingerprint 命令支持 --include；同步 SKILL.md、formats.md、remote-evidence.md
- S2-F18b：新记录写入指纹范围，status 在范围不同时说明原因；证据：新测试先失败后通过
- S2-R1、S2-R2、S2-R3：最后一个提交上跑总校验、变异检查、私人信息检查
- S2-R4：写本轮验证记录
- S2-R5：FEEDBACK.md 补“已处理”，更新记忆
- S2-R6：看定时任务第一次运行的结果

## 计划改动记录

- 2026-10-02 23:53 建立任务。
- 2026-10-03 00:05 按用户批准的方案（G2）建立条目 S2-F18a 到 S2-F20b 和最终检查 S2-R1 到 S2-R5；按 G3、G4 加 S2-R6。当前批次 S2-F20a、S2-F20b、S2-F19，先做 F20，因为另一个真实项目已经靠手工挪行绕过报错，挪行会改变审核结果。

## 意外和发现

- 2026-10-03 核实时发现三处 FEEDBACK 没写到的问题：给已有任务改 fingerprint.exclude 后，status 写“之后代码改过”但文件列表为空；check-brief 把全文任何位置的编号都当本批条目，没有本批列表的简报也能通过；evidence.jsonl 的“不是只追加”报错一旦提交就永久留在历史里，手工挪行会让审核检查取错“最近一次”。分别并入 S2-F18b、S2-F19、S2-F20b。

## 决定

- 2026-10-03 S2-F18b 不靠“文件列表为空”去猜原因，因为记录时有未提交改动或测试机文件不同也会这样；改为新记录写入当时的指纹范围（include、exclude），范围不同时才说明是设置变了。
- 2026-10-03 S2-F18a 落地后，本任务自己的 items.json 也加 fingerprint.include（只看本任务的两个 skill 和共用文件），作为多 skill 仓库里的真实试用；加的时候旧证据会变旧，这是预期。
- 2026-10-03 测试证据照第一轮的做法：tests/junit_report.py 生成 JUnit 报告放在 .agents/local/reports/，用 record --junit 记录；LONGTASK_HOST=mac。
