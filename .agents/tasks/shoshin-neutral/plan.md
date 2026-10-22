# 计划：shoshin-neutral

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- SN-2 交给 Codex：validate-skills.py 和 test_tools.py 改用 scripts/validate_all.py 的 skill_structure_error，删除 --validator、CODEX_SKILL_VALIDATOR 和 ~/.codex 默认路径；先写 HOME 指向空目录运行校验脚本的测试 test_validator_runs_without_any_harness_install，红了再改；证据：junit 和校验命令退出码 0
- SN-1 Claude 改 mission.md 第 3 条和“和 agent harness 无关”一节；证据：doc 检查
- SN-3 Claude 改 shoshin 正文、README、路由用例和评审标准；证据：Claude 审核，SN-5 的检查扫过 shoshin

## 之后

- SN-4 Claude 改 long-task-planning 的两处路径；idea_backlog.py 一句交给 opencode 和 SN-5 同批
- SN-5 SN-2 审核后新开 Codex 会话：扩展 harness_wording_errors，加 harness_files，改掉或登记现有命中（含 idea_backlog.py、两个测试里的示例标签）
- SN-6 用 document-governance 写 ADR 0002 替代 0001
- SN-7 合并前跑 validate_all

## 计划改动记录

- 2026-10-22 19:09 建立任务。
- 2026-10-22 依据 G1 至 G11 建立 SN-1 至 SN-7；G2、G4、G5 是长期规则，写进 mission.md（SN-1），G1、G2 另写进 shoshin ADR 0002（SN-6）。

## 意外和发现

- 2026-10-22 opencode 免费额度用完（429），用户改为交给 Codex（G12）。
- 2026-10-22 codex-orchestration 的启动脚本 check-brief 不带 --task，多个未关闭任务时拒绝启动；已记进该 skill 的 FEEDBACK.md，本批手动检查后直接运行 codex。
- 2026-10-22 human-writing-zh/README.md 仍教复制安装到 ~/.agents/skills，不在本任务范围，收尾时告诉用户。

## 决定
