# 计划：feedback-round1

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，写清做法和需要的证据；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- SK-R9：新增 tests/junit_report.py，用标准库跑 unittest 并写 JUnit 报告；先写测试（各种结果的标记、记录后能满足按测试名的检查），看它失败再写脚本；证据：两个测试通过
- SK-F14：items.json 新增 fingerprint.test_exclude，只对测试类检查生效；记录对应干净提交且之后改的文件都在 test_exclude 里时按当前版本算，失败记录同样处理；先写 6 个测试看它们失败；证据：6 个测试通过
- SK-F9：record --review --commit 按那个提交里的文件内容记录；证据：2 个测试通过

## 之后

- SK-F15
- SK-F11
- SK-F2
- SK-F6
- SK-F3
- SK-F13
- SK-F16
- SK-F7
- SK-F12
- SK-F1
- SK-F8
- SK-F10
- SK-F4
- SK-F17
- SK-R4
- SK-F5：按批准的计划放在最后做
- SK-R1、SK-R5、SK-R2：全部改完后在最终版本上跑仓库总校验、全部变异检查、私人信息检查
- SK-R6：在真实项目的临时克隆上试用，试完删除克隆
- SK-R7：写本轮验证记录
- SK-R3：把安装目录换成符号链接，原目录移到备份位置
- SK-R8：FEEDBACK.md 补“已处理”，更新记忆文件

## 计划改动记录

- 2026-10-02 13:53 建立任务。
- 2026-10-02 14:05 从轻量升级，原因：两个 skill 迁入 agent-skills 后有了 git 仓库；需要分别验证的验收项超过 3 个，且是压缩前没做完的任务。条目按批准的计划 A1–A5、B1–B6、C1–C4 加 F17 和迁移相关的 SK-R1–R9 建立；当前批次 SK-R9、SK-F14、SK-F9。

## 意外和发现

## 决定

- 2026-10-02 本任务的进度记录用安装目录里的旧版 longtask.py，换成符号链接后改用仓库里的新版；测试证据用 tests/junit_report.py 生成的 JUnit 报告记录，报告放在不进 git 的 .agents/local/reports/。
- 2026-10-02 记录证据时设 LONGTASK_HOST=mac，避免把本机主机名写进公开仓库。
- 2026-10-02 test_exclude 只放文档：本仓库的测试只读脚本和测试文件本身，不读 SKILL.md、references/、README.md 和验证记录。
