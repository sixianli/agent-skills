已完成只读调查。JUST-RAG 浏览器聊天判断一次响应完整结束，需要区分两层：`streamChat()` 确认同一 Run 的 `done` 已到达、网络流已读完且尾部已解析；聊天 reducer 则要求已有 `final.response`，随后收到 `done`，才能把消息置为 `complete`。`done` 代表协议结束，不单独代表业务成功，`error → done` 仍是失败。

这是当前源码的静态结论，不是运行验证。检查时项目 HEAD 为 `efb58712923a43e523d4e4184c509c12289dfd71`，开始和结束的 `git status --porcelain` 均为空。

以用户发送一个问题为例，真实链路如下：

1. 浏览器 `App.tsx:235–255` 创建 assistant 消息和 `AbortController`，调用 `streamChat`，把 Run ID 和后续事件分别交给 reducer。`client.ts:111–123` 使用 POST `/api/v1/chat/stream`，读取响应头 `X-Chat-Run-ID`；缺失即报错。服务端注册在 `bootstrap/application.py:237`，路由本身的 `/chat` 前缀在 `routers/chat.py:25`；容器在 `bootstrap/application.py:190–194` 实际注入 `ChatAnswerService` 和 `ChatAnswerGenerator`。
2. HTTP 路由 `routers/chat.py:91–104` 生成 UUID，将同一 `run_id` 传给应用服务，并把事件编码成 SSE；`sse.py:21` 以 `event: …\ndata: …\n\n` 输出。应用服务正常生成路径是阶段状态、预览片段、模型最终结构校验、记录结果，再发送 `final → status(complete) → done`。证据是 `application/chat/service.py:182–225`。没有可回答证据时直接 `final(insufficient_evidence) → done`，见该文件 `174–180`；这仍是完成的一次受控业务响应。
3. 浏览器 `sse.ts:9–14` 合并上次尾部和当前文本，用双换行划分完整事件。网络 chunk 不等于事件：一个事件可能横跨多次读取。`client.ts:124–154` 在内存里维护 decoder、buffer、sawDone；每个解析出的事件必须与响应头 Run ID 一致，done 之后再有解析出的事件就抛错。即使已收到 done，它仍继续 `reader.read()`，直到网络 EOF，再 flush decoder 并消费尾部。最后没有 sawDone 就报“聊天流未完整结束”。
4. reducer 的内存状态另外持有 assistant 的 runId、response、status 和片段索引。`chatReducer.ts:121–137` 收到 final 时以最终正文覆盖内容并清除预览；收到 done 时若无 response，就失败，有 response 才 complete。`status(complete)` 只是阶段提示，不足以代替 done；相关处理见 `76–84`。已经 failed/complete 或跨 Run 的事件被忽略，见 `69–75`。

这里有一个容易遗漏的时序区别：reducer 在 done 回调当下就可以把消息置为 complete，`streamChat()` 的 Promise 此时未必结束，它还在等 EOF。假如之后有额外事件或读取失败，`App.tsx:256–265` 会再 dispatch fail，并在 finally 清除当前流的活动标记。失败补丁在已有 final 时保留可信正文、同时标记失败，否则清除正文和预览，见 `chatReducer.ts:140–148`。所以不能把“曾出现 complete 状态”当作整条网络流已经验证完毕。

常见边界可以这样理解：

| 收到的序列 | 当前代码的结果 |
|---|---|
| final → done → EOF | 流函数可成功返回，未先失败的消息完成 |
| final → EOF，没有 done | 流函数抛未完整结束；消息失败，但保留已有 final 正文 |
| done → EOF，没有 final | 流函数可以成功返回；消息层失败，提示答案生成未完成 |
| error → done → EOF | 协议正常结束，消息保持失败 |
| final → done → 另一个可解析事件 | 流函数抛终止后仍有数据；App 再标记失败 |
| Run ID 不同 | 流函数拒绝事件；reducer 也有独立隔离检查 |

用户取消走 `App.tsx:301–307`：abort fetch，主动标记“已取消”，清除正在生成标记。`streamChat` 没有自己的 reader.cancel/releaseLock finally；这次未验证服务端断连取消如何传播到模型 Provider，不能声称取消必然终止全部后端工作。

为什么这样设计，需要把历史记录和推断分开：

- **Direct：最终可信结果与预览分开。** 归档设计 `docs/archive/specs/2026-04-27-token-level-streaming-design.md:45–47,70–79` 明确说明希望避免把生成中预览当作完成答案，并保留引用校验边界：先流出预览，完整 JSON 和 citation 校验后才能 final，失败则 error/done 且废弃预览。当前服务 `service.py:185–200,211–225` 和 reducer 的 final 覆盖逻辑继续体现这个约束。更早的 `2026-04-27-chat-stream-and-web-design.md:69–71` 采用完整校验后再切片，明确优先引用正确性；这是旧阶段方案，不能拿它声称当前还没有 token 预览。
- **Direct（合同），Inferred（原因）：final 与 done 各负其责。** 原 SSE 设计 `2026-04-27-chat-stream-and-web-design.md:177–178,200–209,256–257` 明确规定 final 承载结构化结果和引用，连接关闭但缺 final 或 done 应失败。从这个合同和当前代码可推断，显式 done 让浏览器区分预期的协议结束与提前断流，final 则证明拿到了业务结果；但没有找到针对“为何不用一个事件”的完整设计讨论，不应把这段推导写成作者原话。
- **Supported：当前严格校验是后续补强，不能归给最近的注释提交。** 本地 `git log --follow`、`git blame -L 121,155`、引入提交和父版本对照显示：`971d271`（2026-04-27）中的客户端读到 EOF 就离开循环，没有 sawDone 校验；`ed41c061f061fe1da0906325f442165b141ea98e`（2026-08-05，`fix: enforce client stream and request identity`）加入响应头 Run ID、sawDone、终止后拒绝事件和 EOF 尾部解析。其父版本与该提交 diff 已直接检查。`3261c8e` 后来增加中文说明，不是这套机制的起源。当前 `client.test.ts:213–241` 还把 Run ID 不匹配、缺 done 流关闭作为拒绝案例；这里只读了测试，没有执行。
- **Inferred：等待 EOF 的代价。** 继续读到 EOF 才返回，可以检查 done 后是否追加了事件；相应地，如果对方发送 done 后一直不关连接，函数会继续等待。当前函数没有自带超时，这一后果由循环可推得，本次未模拟验证，也没有找到解释该取舍的专门记录。

还必须限定“完整校验”的实际能力：`sse.ts:18–28` 并非完整 SSE/schema 验证器，它只取 `event: ` 和 `data: ` 行，缺任一行会忽略该块，JSON 被直接类型断言；`client.ts:149–152` 还会给 EOF 尾部补双换行再解析。因此，它拒绝的是 done 后的可解析事件，并非任意额外原始字节；不能说已证明每个尾部字节都合法，或所有未知事件类型都会拒绝。上述正常序列结论适用于服务端当前发送的事件合同。

后续修改应保留 Run 隔离、final 的可信结果职责、done 的结束职责、失败不能由后续 done 变成成功，以及 EOF 缺 done 要失败的行为。若要改变“done 即返回”或允许未知事件，应先明确是否继续检测尾部违规，而不是直接删除检查。

已检查范围：Shoshin how/why 两份技能及其相关探索、解释、证据等级参考；JUST-RAG 的 App 调用/取消/清理、客户端传输和 parser、reducer、API 路由/注册/容器、应用层 streaming、SSE encoder、客户端相关测试源码、两份相关归档设计以及上述文件的局部本地 Git 历史。没有读取 Shoshin tests 或评分材料，没有网络访问、启动应用、执行测试、修改 JUST-RAG、查询私人聊天历史或启动其他 agent。远程 PR/工单没有搜索，实际浏览器与代理行为没有验证；Provider 内部 token 处理和数据库记录实现不在本次结束合同调查范围。唯一写入是本报告。

源码根目录：/Users/triggerjames/Documents/sxl_code_work_space/JUST-RAG。文中相对路径均在此根目录之下。
