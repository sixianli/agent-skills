---
name: teach
description: "Explain the mechanisms and rationale of real code or changes at the learner's requested depth, weaving existing evidence into a coherent account. Use for teaching requests; do not turn a short question into a full investigation."
---

# teach

Start with the learning goal, relevant code or change, and existing findings. Infer prior knowledge and needed depth from the conversation, without a scripted interview or quiz.

When fresh investigation is needed, use [how](../how/SKILL.md) as discovered by the host. Use [why](../why/SKILL.md) only when historical rationale materially helps the explanation. Reuse evidence and recheck only relevant parts after version changes. Cross-skill links identify the owning skill and resource. Resolve the skill by name in the current host's skill inventory, then read the specified file. Do not assume skills are installed side by side or run the owning skill's entire workflow. If it is unavailable, report the affected step; never silently skip it and claim completion.

First define the subject and the problem it solves. Then follow an actual input to explain how state, data, and responsibilities change. Ground concepts in concrete code and explain key boundaries and tradeoffs. A directory listing can help navigation but cannot replace a mechanism-based explanation.

Preserve why's evidence levels and unknowns; do not turn inference into a definite cause. Use Simplified Chinese by default unless the user requests another language; preserve exact symbols. Match the user's requested depth rather than imposing a one- or two-sentence limit or a fixed sequence of diagrams. Use a diagram when it reduces the effort required to understand the subject.

Keep teaching in the main conversation. Split out research only when it has a clear independent benefit and complies with current delegation rules. Having separate how and why skills does not justify launching two agents in parallel. Explanation requests do not authorize code changes or starting the product.

Deliver the explanation itself. Check whether a reader can trace an input to its result and distinguish implementation facts from historical inference.
