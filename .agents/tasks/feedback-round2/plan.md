# 计划：feedback-round2

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- S2-R1：最后一个提交上跑 uv run --no-project --with pyyaml python scripts/validate_all.py（设 UV_OFFLINE=1，只用本机缓存）
- S2-R2：最后一个提交上跑 python3 long-task-planning/tests/mutate.py
- S2-R3：最后一个提交上跑 items.json 里的私人信息检查命令

## 之后

- S2-R6：定时任务下一次运行（约 12:17 之后）结束后读它的会话记录，确认它判断出没有待处理条目、没有改仓库里的文件；证据：我的审核
- 请用户验收；用户说可以关闭后在 goal.md 追加 CLOSED

## 计划改动记录

- 2026-10-02 23:53 建立任务。
- 2026-10-03 00:05 按用户批准的方案（G2）建立条目 S2-F18a 到 S2-F20b 和最终检查 S2-R1 到 S2-R5；按 G3、G4 加 S2-R6。当前批次 S2-F20a、S2-F20b、S2-F19，先做 F20，因为另一个真实项目已经靠手工挪行绕过报错，挪行会改变审核结果。
- 2026-10-03 00:14 当前批次改为 S2-F18a、S2-F18b。原因：status 显示当前版本已验证 3、未完成 8；S2-F20a、S2-F20b、S2-F19 的测试都在当前版本上通过（E20261003T001324-7084c5、E20261003T001324-7c9e7d）。
- 2026-10-03 00:23 当前批次改为 S2-R6、S2-R4、S2-R5，并在本任务试用 fingerprint.include。原因：status 显示当前版本已验证 5、未完成 6；S2-F18a、S2-F18b 的测试在当前版本上通过（E20261003T002248-39ccad、E20261003T002248-9186fe）；总校验、变异和私人信息检查是命令检查，要等最后一个提交再跑。
- 2026-10-03 10:00 当前批次去掉 include 试用（已做完），保留 S2-R6、S2-R4、S2-R5。原因：加 fingerprint.include 后 status 显示当前版本已验证 5、未完成 6，两套测试在新设置下通过（E20261003T095805-87d168、E20261003T095805-e46b21）；定时任务建好时是停用状态，06:17 那次没有运行，10:00 已启用并打开完成通知，S2-R6 等下一次运行（约 12:17 之后）。
- 2026-10-03 10:03 当前批次改为 S2-R1、S2-R2、S2-R3，S2-R6 移到之后。原因：status 显示当前版本已验证 7、未完成 4；S2-R4 有验证记录和审核（E20261003T100148-383e9c），S2-R5 有审核（E20261003T100306-bad92d）；FEEDBACK 的 20 条都已结束，定时任务下一次运行应只回复没有新条目。

## 意外和发现

- 2026-10-03 核实时发现三处 FEEDBACK 没写到的问题：给已有任务改 fingerprint.exclude 后，status 写“之后代码改过”但文件列表为空；check-brief 把全文任何位置的编号都当本批条目，没有本批列表的简报也能通过；evidence.jsonl 的“不是只追加”报错一旦提交就永久留在历史里，手工挪行会让审核检查取错“最近一次”。分别并入 S2-F18b、S2-F19、S2-F20b。
- 2026-10-03 S2-F20a 的调换/删除测试和 goal/plan 插行测试在改代码前就通过：它们守的是不能放宽的现有行为，靠变异检查证明有效（“evidence order ignored”“goal insertions allowed”“plan log insertions allowed”都被发现）。
- 2026-10-03 codex-orchestration 的 test_codex_launch.py 用的简报没有“范围”一节，S2-F19 后被拒；这是用户批准的写法变化，测试简报改成模板格式，无效简报的用例也改成“范围里的编号不存在”。用新规则对另一个真实项目最近 3 份简报只读试跑：两份通过且取出的本批条目和本意一致，一份因为其中的条目后来被撤回而被拒，符合预期。
- 2026-10-03 S2-F18 把 excludes 参数统一换成 scope 后，整套测试里 test_mutate 报 3 个变异的匹配文本失效（untracked files skipped、porcelain diff for changed files、dirty always false），记录 E20261003T002039-690440 有 1 个失败；改成新写法后 3 个变异都被发现，重跑整套通过。第一轮加的 test_mutate 在这里拦住了变异检查悄悄失效。
- 2026-10-03 在本任务试用 fingerprint.include：先只列两个 skill 目录和 .gitignore，status 对旧证据写“记录时的指纹范围（看全部文件）和现在的设置（只看 …）不同，要在现在的设置下重跑”，没有再写“之后代码改过”加空列表，S2-F18b 的效果在真实任务上成立。随后发现总校验 validate_all.py 还读 skills.json 和 scripts/，只列两个 skill 会让它们改了也不让 S2-R1 变旧，于是把 scripts/ 和 skills.json 也加进 include。status 第二行的 include 按 items.json 原顺序显示，范围不同的说明里按字母排序显示；两处顺序不同，但都列全了路径，不影响判断，没有改。

## 决定

- 2026-10-03 S2-F18b 不靠“文件列表为空”去猜原因，因为记录时有未提交改动或测试机文件不同也会这样；改为新记录写入当时的指纹范围（include、exclude），范围不同时才说明是设置变了。
- 2026-10-03 S2-F18a 落地后，本任务自己的 items.json 也加 fingerprint.include（只看本任务的两个 skill 和共用文件），作为多 skill 仓库里的真实试用；加的时候旧证据会变旧，这是预期。
- 2026-10-03 测试证据照第一轮的做法：tests/junit_report.py 生成 JUnit 报告放在 .agents/local/reports/，用 record --junit 记录；LONGTASK_HOST=mac。
