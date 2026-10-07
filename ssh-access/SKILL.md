---
name: ssh-access
description: Connect to a user-selected SSH target using its existing local configuration, verify the remote host, and diagnose transport, proxy, authentication, or sandbox failures. Use for SSH access and connection checks without assuming a personal host alias, account, provider, or directory.
---

# SSH access

通过使用者指定的 SSH 目标访问服务器。目标、账户、密钥和代理方式以当前请求及本机配置为准，不预设某位维护者的服务器。

## 确定目标

优先使用本次请求给出的 SSH 别名或主机。已有任务明确选定的目标可以继续使用；无法确定目标时询问使用者。不要从其他项目记录猜测主机或登录账户。

在本机检查该目标的生效配置：

```bash
ssh -G <selected-target>
```

核对 `HostName`、`User`、`IdentityFile`、`HostKeyAlias` 和 `ProxyCommand`。这些值在本机检查和记录，不复制到共享文档，也不自动修改 SSH 配置。

## 检查连接

在已有连接授权范围内执行：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=15 <selected-target> hostname
```

`BatchMode=yes` 禁止 SSH 询问密码或密钥口令；代理程序仍可触发自己的登录流程。`ConnectTimeout=15` 限制建立连接及初始握手，不能限制远端命令的运行时间。

检查退出码和远端输出，并与任务期望的主机核对。只有两者都符合预期，才继续执行已授权的远端操作。网页授权成功或代理建立成功本身不能证明 SSH 已登录。

## 代理和认证

没有 `ProxyCommand` 时按当前配置直连。有代理时检查实际指定的可执行文件和认证方式，不默认要求某一服务商。

例如，配置使用 `cloudflared access ssh --hostname %h` 时，Cloudflare 授权先建立代理通道，SSH 再使用配置中的用户和密钥登录。需要浏览器授权时让使用者完成该流程；请求已超时则在授权完成后重试同一条检查命令。

保留主机密钥检查。服务器身份变化或密钥被拒绝时，先核对配置和主机身份；不要通过关闭检查、覆盖 `known_hosts` 或更换凭据来隐藏问题。

## 诊断与记录

| 失败位置 | 下一步检查 |
| --- | --- |
| DNS、路由或连接超时 | 核对当前目标、网络和代理配置；区分直连与代理通道的结果 |
| 代理程序报缓存权限错误 | 核对实际失败的文件和沙箱限制；需要额外权限时使用工具审批，获准后重试已授权的命令 |
| 浏览器授权成功但 SSH 请求已退出 | 重试连接检查，以新的退出码和远端输出判断结果 |
| SSH 账户或密钥被拒绝 | 核对生效账户、密钥和服务器授权，保留凭据变更的授权边界 |
| 服务器主机密钥变化 | 独立核实服务器身份，再按使用者确认的方式处理 |

在本机私有目录保存必要的命令、结果和日期。共享文档不保存内部地址、账户、个人路径、签名链接、认证缓存、私钥或授权截图。

本机工具权限获准不等于服务器管理员权限。连接成功后，安装、部署、删除和服务修改仍按当前任务的授权范围执行。
