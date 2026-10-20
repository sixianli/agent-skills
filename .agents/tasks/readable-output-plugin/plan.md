# 计划：readable-output-plugin

<!-- 只写打算，不写进度；做没做完用 longtask.py status 算。
     当前批次最多 3 项，每项一行、以条目编号开头，写清做法和需要的证据；
     同一次测试顺带验证的条目写在不以编号开头的一行里，不占名额；之后的条目每项一行；
     最后三段只追加，不改旧内容。 -->

## 当前批次

- RO-1 先写测试再改 `WORD` 规则，让连字符连起来的词算一个词；证据：两条测试通过
- RO-2 先写测试，再加 `.claude-plugin/plugin.json` 和 `hooks/hooks.json`（exec 形式，状态目录放 `${CLAUDE_PLUGIN_DATA}`）；证据：测试通过、`claude plugin validate` 退出码 0
- RO-3 写 `plugin_session_e2e.py`，用 `claude -p` 开真实会话，检查插件已加载、Stop hook 拦下英文；证据：脚本退出码 0 和留存的输出

## 之后

- RO-4 改文档和 skills.json，跑仓库全量检查

## 计划改动记录

- 2026-10-20 10:15 建立任务。
- 2026-10-20 RO-4 的完成条件从整个 `validate_all.py` 退出码 0 改成 readable-output 自己登记的检查（结构、py-compile、ruff；unittest 由 RO-1/RO-2 的测试证据覆盖）。原因：`opencode-orchestration` 在当前 HEAD 上就有 py-compile、unittest、ruff 失败（测试文件的 f-string 含反斜杠），与本任务无关，`validate_all.py` 不能只跑一个 skill。状态：未完成 4。
- 2026-10-20 指纹排除 `readable-output/tests/verification/`，让验证说明写在证据之后也不会让证据失效。

## 意外和发现

- 2026-10-20 第一次端到端运行失败是测试本身的问题：提示词要求模型原样说“构建和测试都通过了”，模型拒绝说没有依据的话、换了一句英文，脚本却要求拦截理由包含原句。改成没有事实断言的英文问题，只检查拦截理由引用了模型第一次回复的英文。
- 2026-10-20 反向对照：用 `--settings` 关掉 `readable-output@skills-dir` 后，端到端脚本的 4 项检查失败，说明脚本能分辨插件是否生效，`enabledPlugins` 开关有效。

## 决定

- 2026-10-20 用 skill 文件夹自带插件清单的方式（`readable-output@skills-dir`），不另建 marketplace：`~/.claude/skills/readable-output` 已是指向仓库的符号链接，插件原地加载，改仓库立刻生效；开关用 `enabledPlugins` 里的 `readable-output@skills-dir`。依据：官方 plugins/loading 文档。
- 2026-10-20 连字符误报一并修掉，归在 G1“以最佳的方式维护”之下：不修的话插件装回去会立刻重现用户截图里的问题。
