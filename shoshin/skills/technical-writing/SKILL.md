---
name: technical-writing
description: "Write or review technical tutorials, how-to guides, reference material, and explanations while preserving facts, terminology, and evidence qualifications. Use adopted document-governance for document lifecycle operations."
---

# technical-writing

Start with the purpose, audience, and existing factual material. Deliver technical prose suited to that purpose. Mentioning a deployment, PR, or commit in the text does not authorize performing it.

Identify the main purpose first: a tutorial guides a learning exercise, a how-to guide solves a specific task, reference material supports factual lookup, and an explanation develops mechanisms and tradeoffs. Mixed documents can assign these purposes to separate sections; do not force an entire file into one mode. See [writing guidelines](references/writing-guidelines.md) for organization.

Use real symbols, files, commands, and terminology. Do not invent mechanisms or numbers merely to sound concrete. Preserve exact command arguments and prerequisites. Separate executed results from expected output. Rewriting must preserve the user's structural requirements, conditions, negations, numbers, and confidence levels.

Follow the user's requested output language, using Simplified Chinese by default. When writing in Chinese, use natural Chinese syntax rather than mechanically applying English word-count, article, or -ing rules. Lead with the conclusion, then explain the mechanism and its consequences. Give observable results in tutorials and guides, and link to long background explanations. Explain unfamiliar technical terms on first use and keep their names consistent.

For formal document creation, status changes, or archiving in a project that has adopted governance, discover and use document-governance. Ordinary wording edits do not require introducing a lifecycle. If governance tools are missing, deliver reviewable prose and identify the blocked steps; do not claim governance is complete.

Before delivery, verify factual sources, commands, and cross-references. Remove filler while preserving real uncertainty. The primary agent usually writes directly; do not launch a reviewer for every writing task.
