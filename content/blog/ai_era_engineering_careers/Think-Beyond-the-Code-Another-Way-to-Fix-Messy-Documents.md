---
title: "Think Beyond the Code: Another Way to Fix Messy Documents"
date: 2026-09-09T12:13:36+08:00
lastmod: 2026-09-09T12:49:32+08:00
draft: false

categories:
  - "Engineering Method"
tags:
  - "Architecture"
  - "Governance"
  - "Enterprise AI"

slug: "beyond-the-code-workflow-design"
---

**Instead of writing more code to clean up messy documents, try fixing the workflow that produces them.**

> **A note on scope.** This essay is a reframing exercise, not a blueprint. The document-ingestion example is deliberately simplified: in real deployments you will still face legacy files, externally produced documents, and organizational constraints that no template can remove. Read it as an invitation to widen the design space—*there is an upstream option you may not have considered*—rather than a recipe to copy. Before applying the idea, ask where the input you are fighting actually comes from, and whether it is yours to govern.

---

## 1. The Task and the Technical Default

Imagine you are tasked with building an AI-powered document processing and search engine for an enterprise. The system must ingest raw MS Office documents—Word files, slide decks, and financial tables—and convert them into structured text so downstream AI can answer client queries quickly.

When developers encounter raw documents, they immediately hit a problem: human authoring is chaotic. Authors use floating text boxes, merge table cells, force side-by-side text using the Tab key, and skip official heading styles.

Because engineers are trained to solve technical puzzles, they instinctively see this as a software challenge. Their response is to treat the messy input as an unchangeable law of physics and build technical mitigations to cope with it:

* **Parser Fallback Chains:** Writing complex heuristic rules to handle layout anomalies.

* **Multimodal LLM Calls:** Falling back on expensive vision models when standard text parsers fail.

* **Human-in-the-Loop (HITL):** Route failed documents to manual human verification queues.

This code-first mindset assumes that because the input arrives messy, software must be built to clean it up.

---

## 2. What the Technical Default Costs

Building fallback pipelines is not a mistake—it is the natural technical response. The reason to revisit it is that, left as the standing default, it accrues three kinds of cost that are easy to overlook:

* **Economic Scaling Limits:** Relying on multimodal models or complex fallback chains at query time drives up compute costs ($/search) and introduces noticeable latency.

* **Perpetual Technical Debt:** Engineers end up writing endless code routines to handle every new visual habit authors invent, turning pipeline maintenance into a full-time job.

* **The Strategic Glass Ceiling:** Post-hoc parser guessing can never guarantee 100% data extraction accuracy. Occasional parsing errors may be tolerable in low-stakes, read-only search, but the same ceiling separates the pipeline from high-stakes, automated business operations, where even occasional extraction errors are unacceptable.

The natural response is to say: build it better. Even the strongest version of this path—a modular parser platform where each document type gets its own decoupled component, and every new authoring habit means one more adapter—is what a mature technical architect would build. Done well, it genuinely makes the system more robust and extensible.

What I came to notice is that this path still has a direction: it designs an ever-larger machine to absorb variety that already exists. Every new format or authoring habit means a new component, a new maintenance surface, a new testing matrix; the system grows to match the chaos, while the chaos itself is never reduced.

Seen this way, the problem was never that the mitigations were badly engineered—it was that engineering hours and compute budgets were being spent to accommodate unmanaged authoring habits. A better machine only accommodates them more gracefully; the more I noticed this, the more the alternative felt elegant by comparison: not a smarter parser, but a workflow that stops producing the mess.

The interesting move, then, is not to optimize harder inside the project boundary, but to look at the system that surrounds it.

---

## 3. Reframing the Problem Upstream

The framing I found most useful rests on a simple principle: **avoid writing code to compensate for a workflow you could fix at the source**.

When you step back to view the whole enterprise system, your thinking process shifts across three core steps:

### Step 1: Trace Data to Its Human Source

Stop asking *"How do I parse this messy layout?"* and start asking *"Who created this input, and what habit made it messy?"* Instead of treating erratic Word files as unalterable facts, treat them as broken schema contracts.

### Step 2: Locate Upstream Leverage Points

The brute-force paths—retraining every document author, or special-casing every layout—both scale with the number of people or edge cases. The more useful question is whether a single choke point controls the defaults for everyone.

In an enterprise, that choke point is often the **Central Template Team**. By baking 3–5 structural constraints directly into corporate Word/PPT templates—such as locked table header properties, native column controls, and inline callout blocks—documents go a long way toward arriving structured at the moment of creation.

### Step 3: Align Incentives Across Boundaries

To make upstream changes succeed, you must translate technical friction into currency other teams care about:

* **For the Template Team:** Frame layout constraints as visual polish, brand governance, and accessibility improvements.

* **For Authors:** Ensure template changes are invisible so they can continue working in MS Office without learning new tools like Markdown.

* **For the Business:** Show that upstream template governance removes per-query compute spend and provides the reliability that future high-stakes automation would depend on.

---

## Conclusion

A code-first reading asks, *"How do I write code to handle this data?"* An upstream reading asks, *"Why does this data arrive this way—and who controls that?"*

When bad inputs are solved at their origin, the messy documents the parser existed to survive start to disappear—and with them a slice of system complexity, operating cost, and uncertainty about automation. The most elegant move in this example was not a cleverer parser; it was deciding that the messy input did not need to exist in the first place.

## Related Reading

These ideas are explored further—from a software-architecture angle—in the following posts on this blog (in Chinese):

- [《实战诊断 —— 某企业 AI Platform 的正确蓝图与五重反模式解构》](https://cj9208.github.io/blog/ai_era_engineering_careers/ai-platform-blueprint-anti-patterns/) — why AI Platform teams degrade into downstream ticket-fixing factories (OCR / parsing / human-in-the-loop anti-patterns)
- [《技术的终点是解决问题：从“硬核崇拜”到系统设计与组织管理》](https://cj9208.github.io/blog/ai_era_engineering_careers/hardcore-worship-system-design/) — the highest form of system design dissolves constraints instead of adding code
- [《定义 AI 时代的 Staff：从交付负责到确定性负责》](https://cj9208.github.io/blog/ai_era_engineering_careers/staff-accountability-ai-era/) — accuracy floors and deterministic accountability for high-stakes AI automation
- [《重力回归：企业 ROI 约束与 AI '确定性账单'的控盘人》](https://cj9208.github.io/blog/ai_era_engineering_careers/gravity-roi-ai-deterministic-billing/) — why token-metered AI spend must be converted into a deterministic bill
- [《从波利亚解题法到技术专家的生存闭环：用同理心换空间，用硬约束造引擎》](https://cj9208.github.io/blog/ai_era_engineering_careers/polya-problem-solving-technical-expert/) — translating technical friction into the stakeholder’s own currency of risk and cost
- [《走出「工单驱动」的无意识退化：软件工程中的达克效应与技术破产》](https://cj9208.github.io/blog/ai_era_engineering_careers/dunning-kruger-ticket-driven/) — why patch-driven development quietly accumulates the same debt parser fallback chains do

