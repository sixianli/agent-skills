# 计划：harness-agnostic

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- HA-5 先写判别测试：问每个 agent 一句只在主文件里有、旧 ~/.codex/AGENTS.md 里没有的内容（Repeated Mistakes 一节），改动前 Codex 应答不出、Claude Code 应答得出；再建主文件、两个链接和导入；改动后三个 agent 都要答对。原文件整份进备份目录。证据：global-links.sh 和三条 global-read.sh 退出码 0，输出留在 .agents/local/harness-checks/。
- HA-1 在 mission.md 里写长期决定，每条原样引用用户原话和日期；证据：doc 检查和审核。

## 之后

- HA-2 三个 skill 改写、skills.json 字段、README 安装说明，以及拦住 harness 专用写法的校验（代码和测试交给 opencode）。
- HA-3 安装脚本和测试（交给 opencode）。
- HA-4 用安装脚本把本机拷贝换成链接，再在每个 agent 新会话里验证。

## 计划改动记录

- 2026-10-22 14:40 建立任务。
- 2026-10-22 建立 HA-1 至 HA-5（G1-G20）；status 共 5 项未完成。第一批 HA-5、HA-1：用户要求把全局说明“好好测试一下”。

## 意外和发现

- 2026-10-22 AGENTS.md 标准只规定项目里的位置，没有全局位置；opencode 没有自己的全局 AGENTS.md 时会改读 ~/.claude/CLAUDE.md，所以 CLAUDE.md 只剩一行导入会让 opencode 丢掉全局规则，要给它单独建链接。

## 决定
