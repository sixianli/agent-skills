# 计划：feedback-round2

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- S2-F18a：items.json 的 fingerprint.include 只让列出的路径进指纹（exclude 在其中再排除），lint 要求每个路径都对应仓库里的文件，status 显示只看的路径，fingerprint 命令读 include 并支持 --include；同步 SKILL.md、formats.md、remote-evidence.md；证据：四个新测试先失败后通过，变异检查
- S2-F18b：新记录写入当时的指纹范围（include、exclude），status 在记录的范围和现在不同时说明是设置变了；远程指纹文件带的范围也照此比较；证据：两个新测试先失败后通过，变异检查

## 之后

- S2-R1、S2-R2、S2-R3：最后一个提交上跑总校验、变异检查、私人信息检查
- S2-R4：写本轮验证记录
- S2-R5：FEEDBACK.md 补“已处理”，更新记忆
- S2-R6：看定时任务第一次运行的结果

## 计划改动记录

- 2026-10-02 23:53 建立任务。
- 2026-10-03 00:05 按用户批准的方案（G2）建立条目 S2-F18a 到 S2-F20b 和最终检查 S2-R1 到 S2-R5；按 G3、G4 加 S2-R6。当前批次 S2-F20a、S2-F20b、S2-F19，先做 F20，因为另一个真实项目已经靠手工挪行绕过报错，挪行会改变审核结果。
- 2026-10-03 00:14 当前批次改为 S2-F18a、S2-F18b。原因：status 显示当前版本已验证 3、未完成 8；S2-F20a、S2-F20b、S2-F19 的测试都在当前版本上通过（E20261003T001324-7084c5、E20261003T001324-7c9e7d）。

## 意外和发现

- 2026-10-03 核实时发现三处 FEEDBACK 没写到的问题：给已有任务改 fingerprint.exclude 后，status 写“之后代码改过”但文件列表为空；check-brief 把全文任何位置的编号都当本批条目，没有本批列表的简报也能通过；evidence.jsonl 的“不是只追加”报错一旦提交就永久留在历史里，手工挪行会让审核检查取错“最近一次”。分别并入 S2-F18b、S2-F19、S2-F20b。
- 2026-10-03 S2-F20a 的调换/删除测试和 goal/plan 插行测试在改代码前就通过：它们守的是不能放宽的现有行为，靠变异检查证明有效（“evidence order ignored”“goal insertions allowed”“plan log insertions allowed”都被发现）。
- 2026-10-03 codex-orchestration 的 test_codex_launch.py 用的简报没有“范围”一节，S2-F19 后被拒；这是用户批准的写法变化，测试简报改成模板格式，无效简报的用例也改成“范围里的编号不存在”。用新规则对另一个真实项目最近 3 份简报只读试跑：两份通过且取出的本批条目和本意一致，一份因为其中的条目后来被撤回而被拒，符合预期。

## 决定

- 2026-10-03 S2-F18b 不靠“文件列表为空”去猜原因，因为记录时有未提交改动或测试机文件不同也会这样；改为新记录写入当时的指纹范围（include、exclude），范围不同时才说明是设置变了。
- 2026-10-03 S2-F18a 落地后，本任务自己的 items.json 也加 fingerprint.include（只看本任务的两个 skill 和共用文件），作为多 skill 仓库里的真实试用；加的时候旧证据会变旧，这是预期。
- 2026-10-03 测试证据照第一轮的做法：tests/junit_report.py 生成 JUnit 报告放在 .agents/local/reports/，用 record --junit 记录；LONGTASK_HOST=mac。
