# Task: <一句话说清要做什么>

## Context
<worker 必须知道的背景：相关类/模块、现有约定、为什么要做。只写它从代码里读不出来的东西。>

## Goal
<可验证的完成状态。例：OrderService.cancel() 在已发货订单上抛出 OrderStateException，并有单测覆盖。>

## Allowed paths
<!-- cb-delegate.sh check 只读本节。每行一个 glob；`*` 可跨目录。只列真正需要改的范围。 -->
- src/main/java/com/example/order/*
- src/test/java/com/example/order/*

## Non-goals
- <明确不做的事，例：不改 OrderController，不调整数据库 schema>

## Constraints
- 不新增依赖，不修改 public API 签名，沿用现有代码风格
- <其他约束>

## Acceptance
<!-- worker 会尝试运行；Claude 验收时一定会自己重跑。命令要能在仓库根目录直接执行。 -->
- ./mvnw -q -Dtest=OrderServiceTest test

## References
- <可选：相关文件路径、已有的类似实现、issue 链接。工作副本从 HEAD 建出，未提交或被 git 忽略的文件请写绝对路径>
