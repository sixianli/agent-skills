# 目标：shoshin-neutral

<!-- 只追加，不改旧内容。每条以“## G<编号> <YYYY-MM-DD> <来源>”开头，来源写“用户原话”“用户选择”或“转述：<出处>”，
     下面用“> ”引用原话；回答离开问题看不懂时，引用前写一行“问题：<原问题>”。
     任务结束时追加“## CLOSED <日期> 用户原话”和用户的验收原话。 -->

## G1 2026-10-22 用户原话

> 我是这么想的，shoshin这一套技能，你能不能抽成harness 无关的？因为shoshin这一套技能是软件工程和ai coding领域的通用技能或原则

## G2 2026-10-22 用户原话

问题：shoshin 的上游是 PStack

> 上游是 PStack 没错，但除非我主动说让拉取上游 PStack 的最新代码，再去改动 SHOSHIN 技能包里面的东西，否则现在先把 SHOSHIN 的内容固定下来

## G3 2026-10-22 用户原话

问题：create-verification-skill 和 maintain-verification-skill 写死了 .agents/skills

> 生成的验证 skill 不要写死路径，让生成验证 skill 的那一个 skill，还有维护验证 skill 的那一个 skill 自己去判断应该生成在哪里，因为每一个 agent 的 harness 的 skill 所放的位置都不一样

## G4 2026-10-22 用户原话

问题：校验脚本默认用 Codex 的路径

> 我说了很多次了，就是不要固定在某一个 agent harness 上

## G5 2026-10-22 用户原话

问题：建议：只允许在标题写明是某个 agent 专用的小节里写 agent 名字和它的目录（例如标题是 “In Codex”），别处一律报错；检查范围从 SKILL.md 扩大到脚本和测试。

> 同意

## G6 2026-10-22 用户原话

问题：long-task-planning 里写死的 ~/.claude/skills/... 路径，建议这次一起改成"skill 所在目录下的 scripts/longtask.py"。

> 同意

## G7 2026-10-22 用户原话

> 可以重写shoshin了

## G8 2026-10-22 用户原话

> 如果有编码和测试相关的工作，代理给oepncode来做

## G9 2026-10-22 用户原话

问题：blog-workflow 和你说过"不要动"的那个博客 skill（siblog-blog-workflow）是不是同一套？

> 是同一套

## G10 2026-10-22 用户原话

问题：真问题，本来就该改（这次一起改）：shoshin 的 reflect 2 行、create-verification-skill 和 maintain-verification-skill 各 1 行；long-task-planning 两处写死的 ~/.claude/skills/... 路径；document-governance/scripts/idea_backlog.py 写着"内容提炼仍由调用该 skill 的 Codex 完成"。

> 改！

## G11 2026-10-22 用户原话

问题：已确定的部分：shoshin 以当前内容为准、mission.md 第 3 条照此修改；reflect 去掉"Codex native subagents"；两个验证 skill 自己判断位置；shoshin 校验脚本改用仓库自己的结构检查；README、测试用例和评审标准改成不绑定 agent 的写法；long-task-planning 两处路径；写新 ADR 替代 0001-shoshin-package-identity.md；校验代码和测试交给 opencode，skill 正文和文档由 Claude 改。

> 已确定的地方同意你开始做

## G12 2026-10-22 用户原话

问题：opencode 免费额度用完了，校验脚本这批代码交给谁写？

> 这批交给 Codex 写，用 codex-orchestration，简报照现在这份改。

## G13 2026-10-22 用户原话

问题：第 2 类（该点名 agent 但位置不对）：举例时提到的改成不点名；只对某个 agent 有用的安装和钩子步骤放进标题点名该 agent 的小节；资料来源条目保留原文、标题补上 agent 名；blog-workflow 正文不改只登记。第 3 类（专门为某个 agent 写的代码）：skills.json 加 harness_files 登记哪个文件为哪些 agent 写，登记过的只能出现登记的 agent、登记的文件必须存在、没登记的脚本和测试出现 agent 名字或目录就报错；能换中性写法的（--by codex、# Codex Lessons）不登记。这两类做法你回一句“同意”或指出要改的地方，我就把它们写进新检查（SN-5）。

> 同意

## G14 2026-10-22 用户原话

问题：范围外发现的一处：human-writing-zh/README.md 还在教人把整个文件夹复制到 ~/.agents/skills，跟“只建链接”的规则冲突。README 不在这次检查范围内，你也没批这一处，所以我没改，收尾时再一起问你。

> 改！
