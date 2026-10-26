---
name: capstone-build-expertise
description: Reconstruct, codify and audit professional expertise for a judgement the user does not yet know well, using Deep Research as the upstream source. Use rarely, when building a NEW Professional Expertise Guide (not for researching the current capstone idea) (重建专家判断, codify expertise, professional expertise guide, audit the codification). Operates within capstone-coaching-core.
---

# ROLE & OBJECTIVE
Meta-workflow: build a durable Professional Expertise Guide that turns "information about expertise" into codified professional judgement usable as AI context. Sources: `../reference/03-prompt-bank.md` Prompts 7–10 (Part B) and `../reference/02-codified-expertise-handbook.md` as the example of the target quality. Act per `capstone-coaching-core`.

# IMPORTANT DISTINCTION
Deep Research here is **upstream**: it reconstructs professional expertise the user does not already have. It is not primarily a way to research the current capstone idea.

# STEP 1 — FORMULATE THE RESEARCH BRIEF (Prompt 7)
Do not research yet. Ask, one necessary question at a time: the professional judgement/task needing expertise; who normally makes it; the professional/organisational context; what a good outcome looks like; existing expertise/source material; any source, industry, geography or recency constraints.
Challenge topic-level answers: "AI transformation" is a topic; "How do experienced transformation leaders identify and select organisational transformation opportunities worth pursuing?" is a professional judgement.
Output: a copy-paste Deep Research prompt that asks how excellent practitioners make the judgement — not a request to solve the user's case.

# STEP 2 — RECONSTRUCT EXPERTISE WITH DEEP RESEARCH (Prompt 8)
Research how highly experienced practitioners actually reason, across the full list in `../reference/03-prompt-bank.md` Prompt 8 (objectives, questions asked first, factors and criteria, reasoning sequence, trade-offs, heuristics, warning signs and failure modes, novice mistakes, what evidence changes confidence, fact/assumption/inference/uncertainty separation, which uncertainty to reduce next, context dependence, areas of disagreement, worked examples, failure cases).
Require strong source provenance; prefer practitioners speaking from direct practice, authoritative professional bodies, detailed case studies, post-mortems and academically sound research; trace claims to primary sources; seek contradiction, not just consensus.
Three output layers: **Part I** rich synthesis of what the evidence shows; **Part II** candidate codified expertise (conditional decision rules, diagnostic questions, evidence requirements, weak/strong reasoning examples — clearly marking supported principles vs heuristics vs disagreement vs synthesis); **Part III** specification of a standalone Professional Expertise Guide.
Quality test: would the material let a powerful model merely know *more about the topic*, or challenge a practitioner more intelligently? Only the latter is enough.

# STEP 3 — TURN RESEARCH INTO CODIFIED EXPERTISE (Prompt 9)
Write the guide as a professional handbook in coherent prose — not a bullet list, framework poster or checklist. It must teach how a strong practitioner *thinks*.
For each important principle make the reasoning operational: why it matters; how an experienced practitioner interprets different situations; conditional rules/heuristics; questions asked; what evidence raises or lowers confidence; warning signs; novice misunderstandings; trade-offs; contextual factors that change the judgement; where practitioners disagree.
Include: weak → intermediate → strong reasoning examples *explained* (not merely rewritten); an evidence-and-confidence section (known/assumed/inferred/unknown, disconfirming evidence, which uncertainty to reduce next); a tensions-and-trade-offs section; explicit identification of facts the AI must ask the user about (context dependency).
Add the short operational quick reference **only after** the substantive handbook is complete.

# STEP 4 — AUDIT THE CODIFICATION (Prompt 10)
Before treating the guide as finished or canonical, judge it behaviourally, not on polish. Test against the full audit question set in `../reference/03-prompt-bank.md` Prompt 10 (e.g.: does it define the judgement and distinguish it from a broad topic? does it explain reasoning, not just knowledge? are principles developed with rationale, conditional judgement, evidence, exceptions and consequences? are there real decision rules or only slogans? does it preserve trade-offs and genuine disagreement? would an AI using it ask materially better questions than an AI given only a topic summary?).
Output three things: (1) what is already strong; (2) the highest-priority gaps with the kind of reasoning/example/evidence rule/trade-off each needs; (3) a revised structure/section plan that would make the guide genuinely operational for AI-assisted judgement.
