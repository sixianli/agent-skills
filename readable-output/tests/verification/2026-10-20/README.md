# readable-output 验证记录（2026-10-20）

这次改动把中文回复检查从“手工抄进 `~/.claude/settings.json` 的 4 条 hook（Claude Code 在特定时机自动运行的命令）”改成 skill 文件夹自带的插件，并修掉带连字符的英文术语被误判成英文句子的问题。

被测版本：基于提交 `03d01a8` 加上本次改动，长任务指纹（只看 `readable-output/`、`README.md`、`skills.json` 的内容哈希）`ec34a6514503`。

| 文件 | SHA-256 |
| --- | --- |
| `scripts/check_chinese_reply.py` | `859b5fbef770e3ae0a6a388d2232ea61de80e29f3369d8f0e5e5748337bdf006` |
| `hooks/hooks.json` | `1d71ddd7388d5fdf91af649f40997dc8290e3b0fadee815917850cf63e07f822` |
| `.claude-plugin/plugin.json` | `d156aef4acf2c6efa16afea3161bea2c42481bc2da4b61a63c90dc4833e2f5f0` |

## 环境

- Mac，Python 3.14.7，Claude Code 2.1.302 命令行。
- 安装方式：`~/.claude/skills/readable-output` 是指向本仓库 `readable-output/` 的符号链接，`~/.claude/settings.json` 里没有任何 `check_chinese_reply.py` 条目。
- 端到端测试需要联网、已登录的 Claude Code，并且要在沙箱之外运行：hook 要写 `~/.claude/plugins/data/`。

## 怎么重跑

在仓库根目录运行：

```bash
python3 -m unittest discover -s readable-output/tests -p 'test_*.py' -v
claude plugin validate readable-output
python3 readable-output/tests/plugin_session_e2e.py
```

证据报告用的是 pytest 生成的 JUnit 报告（同一批测试）：

```bash
UV_CACHE_DIR="$TMPDIR/uv-cache" uv run --no-project --with pytest python -m pytest readable-output/tests -q --junitxml=readable-output/tests/verification/2026-10-20/local/unit-junit.xml
```

## 结果

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| 单元测试 | 45 个通过，0 个失败 | `local/unit-junit.xml`（SHA-256 `fa419fb7…20925`）、`local/unit.log` |
| 先写测试再改代码 | 改代码前跑同一套测试：3 个连字符用例失败（正是本次会话里被误拦的原句），插件测试因 `.claude-plugin/plugin.json` 不存在而报错 | 会话记录 |
| 插件清单校验 | `claude plugin validate` 通过，只有“没写 version”“没写 author”两条提醒 | `local/plugin-validate.log` |
| 真实会话（端到端） | 7 项检查全部通过 | `local/plugin-session/summary.json`（SHA-256 `69807e73…82829`）、`local/plugin-session/stream.jsonl`（SHA-256 `2daff19c…c55c85`） |
| 反向对照 | 用 `--settings '{"enabledPlugins":{"readable-output@skills-dir":false}}'` 关掉插件跑同一提示词：“插件已加载”“Stop hook 拦截”“收到反馈”“最终回复是中文”4 项失败 | 会话记录 |
| readable-output 的仓库检查 | 结构、py-compile、unittest、ruff 全部通过 | `local/validate-all.log` |
| 整个仓库的检查 | 退出码 1：只有 `opencode-orchestration` 的 py-compile、unittest、ruff 失败，那个目录本次没改，提交 `03d01a8` 上就是这样 | `local/validate-all.log` |

`local/` 目录被 `.gitignore` 忽略，只留在运行的机器上。

## 端到端测试检查了什么

`plugin_session_e2e.py` 在一个空的临时目录里运行 `claude -p`，提示词要求只用英文回答一个问题，然后从输出流里检查：

1. `claude` 退出码为 0。
2. 会话启动信息的插件列表里有 `readable-output@skills-dir`。
3. 模型第一次回复是英文。
4. `Stop` hook 返回 `"decision": "block"`，拦截理由里引用了那句英文。
5. Claude 收到了 “Stop hook feedback”。
6. 会话正常结束。
7. 最后一条回复里没有英文句子（用同一个检查脚本判断）。

这次运行的最终回复是用中文解释天空为什么是蓝色，并说明上一条是英文、已改为中文。

第一次写这个脚本时，提示词要求模型原样说出“构建完成、测试全部通过”，模型拒绝说没有依据的话，换了一句英文，脚本因为只认原句而报失败。hook 本身那次也拦下了。现在的提示词不含事实断言，第 4 项只检查拦截理由引用了模型实际说的英文。

## 第二轮：只拦完整句子，不拦术语

用户要求只拦完整的英文句子，不拦 `ai agent`、`llm as judge` 这类英文专有名词。旧规则只看“至少 4 个词、其中 2 个是虚词”，而 `a`、`the`、`of`、`in` 在术语里也很常见，所以 `LLM as a judge`、`human in the loop`、`state of the art`、`out of the box` 都会被拦。

新规则要求一段英文同时有虚词和“句子特征”才拦。句子特征指以下任一种：大写开头、句末标点（忽略行首的列表编号）；含助动词、主语代词、`let`、`please`、`now`、`then` 或疑问词；4 个词以上、2 个虚词、带 `-ing` 或 `-ed` 结尾的动词；6 个词以上、2 个虚词。另外，首字母大写、末尾没有句号的名称会放行。

| 项目 | 结果 |
| --- | --- |
| 先写测试再改代码 | 23 个术语（每个放进 3 种位置：句中、列表项、表格）里有 7 个被旧规则拦下，测试失败；12 个必须拦的句子当时都能拦 |
| 漏拦补救 | 和旧规则逐行对比英文文档，发现 `1. Re-read the user's words in goal.md.` 和 `Print what the hook injects` 两种完整句子会漏拦，先补测试（失败），再修：判断大写开头时去掉列表编号，疑问词算句子特征 |
| 本机真实回复对比 | 最近 40 个 Claude Code 会话里 3977 条中文回复：新旧规则都拦下同样 23 行，全是真正的英文句子，没有术语 |
| 英文文档对比 | `long-task-planning/SKILL.md` 旧 102 行、新 100 行；新规则放行的是 `Needs a user decision`、`Check the rules in` 这类短语和残句 |

已知会放行的情况：不含虚词的英文句子（如 `Tests passed.`）、3 个词以内的祈使句（如 `Ask the user`），旧规则也一样放行。

## 没有覆盖的部分

- 交互式会话里 `PostToolBatch` 和 `AskUserQuestion` 的拦截：只在单元测试里按 Claude Code 的执行方式跑过，真实会话只验证了 `MessageDisplay` 和 `Stop`。
- Codex：插件文件对 Codex 没有作用，Codex 那边只读取 `SKILL.md` 和 `agents/openai.yaml`。
