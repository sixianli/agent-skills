# 仓库纳入检查

日期：2026-10-06。来源版本：human-writing-zh 1.0.0。
执行环境：macOS，Python 3.14.7。
仓库基线：`daac10f7aeb6abf55e0e5ab6b9a1a8d941bbc5e6`。
检查覆盖本次新增的技能目录，以及根目录 README.md 和 skills.json 的登记改动。

## 纳入内容与适配

完整纳入 17 个原始文件，包括技能入口、参考资料、模板、案例、脚本、测试和两份许可说明。
根目录技能清单登记了安装目录、说明入口、调用策略和语法、测试、Ruff 检查命令。

两份说明文件移除了个人服务器名称。脚本与测试调整了导入顺序，脚本调整了类型标注并增加执行权限。
除导入和函数类型标注外，脚本与测试的语法树和原始版本一致；工具的执行逻辑未改变。
本轮未修改原始目录，文件差异与 SHA-256 保存在本地检查记录中。

## 实际执行结果

- 技能的 38 项 unittest 全部通过。
- 仓库总检查全部通过，10 组 unittest 共 298 项测试通过；包含新技能的 38 项测试。
- SKILL.md 与 agents/openai.yaml 的 YAML 解析、名称、版本、默认调用名称和调用策略检查通过。
- 10 个本地 Markdown 文件引用均能找到目标文件。
- 18 条行为案例的 JSONL、必要字段和唯一 ID 检查通过。
- 两个 Python 文件按 Python 3.9 语法解析通过；未执行 Python 3.9 运行检查。
- 本次新增内容通过仓库私人信息规则及本地绝对路径、密钥模式检查。

通过实际命令行入口运行四个场景，并对输入目录和文件哈希进行独立回读：

| 场景 | 断言 | 实际退出码 |
|---|---|---|
| 正常删去套话 | 数值、代码、frontmatter、链接和引用保留；未报告字面差异 | 0 |
| 修改受保护内容 | JSON 指出代码块、行内代码和链接变化；严格模式拒绝通过 | 1 |
| 只修改数值 | JSON 报告数值差异；严格模式保留数值提示的原有处理方式 | 0 |
| 输入文件不存在 | 输出读取错误 | 2 |

四个场景的实际退出码均符合原有契约。每个场景结束后，输入文件内容和目录中的文件列表均未改变。

## 复跑与证据

从仓库根目录运行：

```bash
python3 -m unittest discover -s human-writing-zh/tests -v
uv run --no-project --with pyyaml python scripts/validate_all.py
python3 human-writing-zh/tests/verification/2026-10-06-import/local/replay_cli.py
```

总检查使用 `UV_CACHE_DIR=/private/tmp/codex-human-writing-zh-import-uv-cache` 和
`UV_PYTHON_PREFERENCE=only-system`，将依赖缓存放在任务临时目录并使用已安装的 Python。

`local/` 按仓库规则被 Git 忽略，保留在维护者机器上：

- `repository-checks.log`、`repository-checks-result.json`：总检查输出、完整命令、环境、时间与退出码。
- `unit-tests.log`、`unit-tests-result.json`：技能测试输出与命令。
- `cli-result.json`、`fixtures/`、各场景的 `.stdout` 和 `.stderr`：命令、断言、输入前后哈希和实际输出。
- `replay_cli.py`：使用保留的合成输入复跑四个命令行场景。
- `structural-review.json`、`final-import-review.json`、`tracked-changes.diff`：结构检查、原始与纳入文件的哈希及登记改动。

首次总检查中的六项 Ruff 问题及修正前的记录保留在 `*-before-lint.*`。
复跑辅助脚本首次选择了仓库上一级目录，导致脚本路径读取失败；修正目录层级后四个场景通过。
该辅助脚本错误的原始版本、错误输出和分类记录保留在 `replay-cli-before-root-fix.py`、
`preserved-helper-root-error.*` 和 `helper-root-error.json`。
本轮未清理这些检查证据；它们位于技能检查目录，不依赖临时缓存目录。

## 验证范围

这些结果证明本次仓库登记、文件结构和离线工具检查通过。
18 条行为案例只检查了数据格式，未运行模型写作回归、读者盲测或 A/B 评估。
本轮未执行 Codex 或 Claude Code 的安装后调用检查。
工具测试通过不等于文章质量或事实真实性已经验证。
