---
name: sensitive-information-scan
description: Audit files, publishable repository content, staged Git blobs, reachable history, and commit identities for credentials, personal accounts, local paths, network details, and private project context. Use before sharing or publishing content, or when investigating accidental exposure; reports redact matched values and fail if requested content cannot be completely read.
---

# Sensitive information scan

先检查使用者指定的内容和 Git 范围，再解释哪些信息会暴露凭据、个人或内部项目。默认只检查和报告；发现问题不自动授权撤销密钥、删除资料、改写历史或修改账号设置。

## 选择范围

使用 `scripts/scan_sensitive.py`，仅依赖 Python 标准库和本机 Git：

```bash
python3 <skill-dir>/scripts/scan_sensitive.py <file> [<file> ...] --fail-on-findings
python3 <skill-dir>/scripts/scan_sensitive.py --repo <repository> --current-author --fail-on-findings
python3 <skill-dir>/scripts/scan_sensitive.py --repo <repository> --staged --current-author --fail-on-findings
python3 <skill-dir>/scripts/scan_sensitive.py --repo <repository> --history --fail-on-findings
```

- 默认仓库扫描读取当前已跟踪文件和未忽略的新文件。已删除的工作区文件不再读取。
- `--staged` 读取完整 Git 暂存区中的 blob（Git 保存的文件内容），不读取工作区替代它。未暂存的修改不会改变待提交内容。
- `--history` 读取本机所有引用可达的历史文件、已删除文件、提交作者及提交者的姓名、邮箱和提交说明。报告的历史内容标识是 blob ID；提交身份的标识是 commit ID。
- `--current-author` 检查实际生效的作者和提交者姓名及邮箱，包括环境变量覆盖。GitHub noreply 地址作为可公开的邮箱处理；通用作者名 `Contributor` 和明确的 GitHub 机器人名不作为个人姓名候选。个人姓名仍需独立审查，使用 noreply 邮箱不会自动豁免姓名。
- `--commit-range <full-base-hash>..HEAD` 只检查新增提交身份和提交说明，可用完整目标 hash 替换 `HEAD`。范围不等于文件内容扫描。
- `--include-ignored` 显式加入本机忽略文件。私有本机资料需与待发布内容分开报告。

没有执行 fetch；本机未持有的远端引用、别人保存的副本、旧 fork、GitHub 日志、发布产物和外部服务都不属于本机扫描结果。

## 检查规则和结果

检查私钥、常见服务商令牌、云访问标识、密码与密钥赋值、认证头、会话 cookie、签名链接、含密码的数据库 URL、云服务连接密钥，以及邮箱、姓名字段、账号字段、社交及代码托管账号链接、家庭目录、电话、身份证号、IPv4 和 IPv6 地址、内部域名和项目来源字段。文件名和压缩包成员路径同样检查；凭据文件名也需要审查。

结构化 JSON 字符串会先解码转义内容再检查。ZIP 和基于 ZIP 的办公文件会检查内部成员；默认最多三层、每包一千成员和十 MiB 解压内容。其他二进制只检查可读取的字符串，并明确报告还需专用格式检查。

报告是 JSON 对象，包含 `findings`、`errors` 和 `coverage`。发现项只给出范围、位置、类型、等级和内容标识，`redacted: true` 表示未输出匹配原值。历史姓名、邮箱和当前提交身份同样不输出原值。范围以 `-path` 结尾时，发现来自文件名或成员路径，`line: 1` 表示路径本身，不能当作正文行号。

退出码：`0` 为检查完成；加上 `--fail-on-findings` 后有发现项返回 `1`；读取失败、范围不完整或配置错误返回 `2`。没有该开关时，`0` 仍可带发现项，必须查看报告。

规则是候选检测，不等于判定全部数据安全。任意人名、内部项目名、图片中的文字和未知令牌格式不能只凭通用正则识别，需要使用者提供私人检测词和人工审查。不要把未读取的内容算作没有问题。

## 私人检测词和明确例外

通过 `--private-patterns <local-file>` 增加使用者提供的姓名、账号、项目名、域名和目录特征。文件每行一个正则表达式；空行忽略，匹配空字符串的表达式拒绝执行。私人检测词文件放在 Git 忽略的本机目录，不能把使用者的信息写入通用技能源码或共享配置。

通过 `--policy <file>` 提供确实可以公开的示例值。格式：

```json
{"version": 1, "allow": [{"rule": "email", "pattern": "[^@]+@example\\.com", "reason": "Reserved example-domain fixture"}]}
```

例外只作用于指定类型和完整匹配值，必须有解释。一个邮箱例外不能豁免同一行的密钥，也不能跳过整个测试目录。检查误报时先核对匹配规则和来源，不把真实泄露加入白名单。

## 处理发现

1. 区分真实凭据、个人信息、可公开的配置和合成测试值，在本机核对原文件。
2. 报告类型、文件与行号、暴露范围、证据限制和需要采取的具体动作，不复述敏感原值。
3. 按已授权范围删除或匿名化待共享内容。凭据真的公开过时，向使用者说明撤销或轮换的目标和影响。
4. 重新检查当前内容、暂存区和新增提交。当前文件干净不能证明旧历史干净。
5. 历史或外部副本另行处理；改成私有仓库不会撤回别人已有的副本。
