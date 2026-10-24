# 计划：feedback-round4

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- F4-1：按 G1 交给 CodeBuddy（hy3；deepseek-v4.1-flash 的频率限制 22:56 才恢复），和 F4-2 合成一个任务，只改 codebuddy-orchestration/SKILL.md。Known pitfalls 记 429 原文、CLI 退出 0、脚本以 3 退出并在 `!!` 行给出 stderr、免费额度按账号共用；Rework 写明不能 resume、告诉用户恢复时间、先 `clean --discard` 再换 id 重新 start 或换用户确认免费的模型。证据：我的逐行审核、validate_all
- F4-2：同一个任务改 templates/worker-rules.md：被拒先照原样重跑、不建临时或调试文件、空行照周围代码。证据：审核、validate_all、codebuddy 的测试
- F4-4：交给 CodeBuddy（hy3），和 F4-1、F4-2 的任务同时跑（路径不重叠），改 document-governance 的 idea_backlog.py、测试和说明；先写测试留下失败输出。证据：两个测试名、我的逐行审核

## 之后

- F4-3：交给 CodeBuddy，只改 opencode-orchestration/SKILL.md 的 Known pitfalls
- F4-8：交给 CodeBuddy，改 longtask.py 里 tag、selector、command 三类检查“没有通过记录”的提示和测试；和 F4-5、F4-7 改同一个文件，先于它们单独做
- F4-5：交给 CodeBuddy，和 F4-7 合成一个任务（都改 longtask.py 的 check-brief 选任务部分）；先写测试
- F4-7：同上，另改 codex-launch.sh 和三个 SKILL.md 的说明

## 计划改动记录

- 2026-10-24 17:06 建立任务。
- 2026-10-24 17:08 按 G2 把剩下的反馈和修订方案没做的两条全部列成 F4-1 到 F4-7；F4-7 来自修订方案评审时确认、方案没排上的问题。第一批 F4-1、F4-2、F4-6，第二批 F4-3、F4-4，第三批 F4-5、F4-7。
- 2026-10-24 17:17 F4-6 查明 F24 的原因后加 F4-8（提示里说出别的主机上的通过记录）。F4-4 提前到第一批，和 F4-1、F4-2 的任务同时跑；F4-8 排在 F4-3 之后、F4-5 之前。

## 意外和发现

- 2026-10-24 F24 的原因不是指纹：另一个项目里那个条目的 8 条测试记录，主机名都是测试机自己报的名字，完成条件写的却是连接时用的别名，按主机筛完一条不剩，status 就报“没有通过记录”。临时仓库里复现过，改成同一个主机名后同一份证据就算通过。

## 决定

- 2026-10-24 G1、G2 都只管这一次任务，记为 once。G2 之后不再逐条问用户；付费模型、新下载、删用户文件仍要先问，这些规则来自用户的全局说明，G2 没有改它们。
