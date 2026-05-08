# Good Capture Example

This example is good because it captures the actual idea, the user's shift in thinking, memorable wording worth preserving, and unresolved questions worth revisiting. It does **not** try to summarize the whole conversation.

---

# Eval-First RAG Tuning

**Date:** 2026-04-14
**Context/Project:** enterprise-rag

## Core Ideas

- The user stopped treating chunk size as a one-time configuration choice and reframed it as an eval-driven tuning parameter.
- RAG tuning should be approached like a regression-tested retrieval system, not like prompt fiddling.

## Thought Trajectory

- Started with a narrow question: what chunk size to use.
- The turning point came when the user recognized the real problem was not selecting a universally correct chunk size, but building an evaluation loop that can measure trade-offs on real queries.
- Framing shifted from "find the best number" to "treat retrieval settings as system parameters that should be validated continuously."

## Verbatim Quotes

> "不要纠结于找'最优值'"
> "Chunk size 是需要用 eval 驱动调优的超参数"
> "我想要的是能回归验证的企业级 RAG，不是 demo"

## Open Questions

- What should a representative evaluation set look like for this product domain?
- When should reranking be introduced instead of continuing to tune chunking parameters?
