---
name: hermes-ssh
description: Connect to the user's Hermes Linux server through the configured SSH alias and Cloudflare Access, verify the remote host, and diagnose local sandbox or authentication failures. Use for Hermes server access and read-only connection checks; not for configuring the unrelated Hermes Agent framework.
---

# Hermes SSH

通过 Mac 上已有的 `ssh hermes` 配置访问用户的 Hermes Linux 服务器。连接成功后，仍按当前任务的授权范围执行远端操作。

## 已验证的连接方式

2026-10-02 在用户的 Mac 上验证成功：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=15 hermes hostname
```

命令退出码为 `0`，并返回远端主机名。后续连接仍需检查退出码，并在本机核对实际返回的主机名。具体连接参数和检查结果保留在本机，不在公开说明中填写内部地址或账户信息。

`BatchMode=yes` 禁止 SSH 交互式询问密码或密钥口令；它不会阻止代理程序 `cloudflared` 打开 Cloudflare 登录页面。`ConnectTimeout=15` 限制 SSH 建连和初始握手的等待时间，不能用来限制远端命令的运行时长。

## 先读取当前配置

`hermes` 是 SSH 别名。先在本机检查当前生效配置，不要把它当作需要直接解析的主机名：

```bash
ssh -G hermes
```

核对 `HostName`、`User`、`IdentityFile`、`HostKeyAlias` 和 `ProxyCommand`。具体值以本机配置为准，不要自动覆盖 SSH 配置，也不要将这些值复制到公开仓库。

本次成功路径由 `ProxyCommand` 调用 `cloudflared access ssh --hostname %h`。`%h` 由 SSH 替换为配置中的目标主机名。先确认当前配置指定的 `cloudflared` 可执行文件存在；不同机器的安装位置可能不同。

Cloudflare 授权决定代理通道能否使用；随后 SSH 使用本机已有的密钥，以配置中的用户身份登录服务器。两步都完成才算连上。`HostKeyAlias` 指定 SSH 核对服务器主机密钥时使用的名称；保留既有主机密钥检查，不通过关闭检查来修复连接问题。

## 授权和执行

1. 执行当前任务需要的 SSH 命令。只检查连接时，使用上面的 `hostname` 命令。
2. 当 Cloudflare 会话需要授权时，让用户完成 `cloudflared` 打开的浏览器登录流程。用户已为本次连接完成授权时，继续使用该授权。
3. 浏览器显示 `Success!` 和 token 已返回发起请求的机器，表示 Cloudflare 授权步骤完成。保持发起请求的进程可继续运行；浏览器页面本身不能证明 SSH 已连接成功。
4. 如果原 SSH 请求在等待浏览器授权时已经超时，在授权完成后重试同一条命令。检查命令退出码和远端输出，再执行已授权的操作。

在本机记录命令、退出码、远端主机名和检查日期。公开仓库只记录连接步骤；不保存内部地址、登录账户、个人路径、带签名或 token 的授权 URL、Cloudflare 凭据缓存、SSH 私钥或浏览器授权截图。

## 根据失败发生的位置处理

| 现象 | 本次经验和下一步 |
| --- | --- |
| `cloudflared` 写本机授权缓存或临时认证文件时出现 `operation not permitted`，随后 SSH 握手超时 | 本次在 Codex 文件系统沙箱内遇到过。使用工具提供的 `require_escalated` 审批机制，按实际命令申请访问本机授权缓存所需的权限，再执行同一条已授权命令。只有工具批准后才执行；不要更改沙箱规则或复制凭据绕过限制。 |
| Cloudflare 浏览器页面成功，但原 SSH 命令已退出并报告超时 | 授权完成后重试。以新的 SSH 退出码和远端输出判断结果。 |
| SSH 拒绝密钥或报告主机密钥变化 | 在本机核对生效的用户、密钥路径和主机身份；不要自动修改凭据、服务器授权或 `known_hosts`。 |
| 备用直连通道被服务器关闭 | 本次备用通道未连上，Cloudflare 通道随后连接成功。分别判断两条通道；不要把备用通道失败当作服务器或 Cloudflare 通道不可用的证据。 |

本机沙箱外执行获准，不等于取得服务器管理员权限。连接成功也不授权安装、部署、删除、修改服务或调用付费接口。
