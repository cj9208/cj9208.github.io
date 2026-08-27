---
title: "RAG Orchestration Architecture"
date: 2026-07-16T14:17:00+08:00
lastmod: 2026-08-27T11:49:55+08:00
draft: true

description: "A structured note set on intention recognition, request orchestration, governed execution, and the system-design principles behind them."
summary: "A structured note set on intention recognition, request orchestration, governed execution, and the system-design principles behind them."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Orchestration"

slug: "rag-orchestration-architecture"
---
This folder explains how a messy-input RAG problem can evolve into a broader request orchestration architecture, and how that architecture connects to AI system design and harness engineering.

The central idea is:

```text
messy request
-> intention recognition
-> capability selection and governed execution
-> RAG as one capability
```

## Recommended Reading Order

1. Read the architecture notes to understand the design itself.
2. Use the deep dives only for follow-up depth.
3. Read the principles and philosophy notes when you want the broader worldview behind the design.

## Architecture Notes

These are the main design notes for the architecture itself.

- [`CH00_Preface.md`]({{< relref "./CH00_Preface.md" >}})
- [`CH01_Intention-Recognition-Layer.md`]({{< relref "./CH01_Intention-Recognition-Layer.md" >}})
- [`CH02_Request-Orchestration-Layer.md`]({{< relref "./CH02_Request-Orchestration-Layer.md" >}})
- [`CH02_01_Runtime-Objects.md`]({{< relref "./CH02_01_Runtime-Objects.md" >}})
- [`CH02_02_State-Machine-and-Control-Loop.md`]({{< relref "./CH02_02_State-Machine-and-Control-Loop.md" >}})
- [`CH02_03_Confidence-Safety-and-Validation.md`]({{< relref "./CH02_03_Confidence-Safety-and-Validation.md" >}})
- [`CH03_RAG-Layer.md`]({{< relref "./CH03_RAG-Layer.md" >}})

## RAG Internal Layers

These break the RAG subsystem into narrower internal components.

- [`CH03_01_Ingestion-Validation-Layer.md`]({{< relref "./CH03_01_Ingestion-Validation-Layer.md" >}})
- [`CH03_02_Enrichment-Chunking-Indexing-Layer.md`]({{< relref "./CH03_02_Enrichment-Chunking-Indexing-Layer.md" >}})
- [`CH03_03_Retrieval-Layer.md`]({{< relref "./CH03_03_Retrieval-Layer.md" >}})
- [`CH03_04_Grounded-Answering-Layer.md`]({{< relref "./CH03_04_Grounded-Answering-Layer.md" >}})

## Execution Readiness Notes

These notes turn the design into something reviewable and testable.

- [`CH04_Testing-and-Evaluation.md`]({{< relref "./CH04_Testing-and-Evaluation.md" >}})
  Defines the minimum test matrix, golden-case structure, and acceptance thresholds for the orchestration and RAG behavior.

## Principles And Philosophy Notes

The broader engineering worldview behind this design is not re-derived inside the set. It lives in these standalone articles:

- [AI Coding 的防御性进化：平台化、业务解耦与结构的自然生长](https://cj9208.github.io/blog/ai_study/ai-coding-evolution/)
  Why bounded sandboxes, rigid platform foundations, and late abstraction beat premature DRY when AI writes most of the code.
- [A First-Principles Architecture for Agent Routing and Safety Harnesses](https://cj9208.github.io/blog/ai_study/agent-routing-safety-harness/)
  The full derivation of model-proposes-harness-executes, orthogonal verification, and risk-proportional authorization.
- [Harness Engineering 合集](https://cj9208.github.io/blog/ai_study/harness-engineering/)
  The six-part series on harnesses as the deterministic runtime around a probabilistic engine — boundary placement, context discipline, comparator design, and governed execution.

How those principles show up in this set:

- intention recognition exists because input quality is the earliest useful control point
- the harness owns permissions and escalation because reasoning should not imply execution authority
- evaluator contracts sit outside generation because correctness needs an external comparator
- context discipline exists because state is costly, degradable, and attention-limited
- layers stay modular so failures remain local and ownership stays clear

## What This Set Covers

- why bad input harms downstream RAG quality and cost
- why intention recognition should happen before expensive retrieval
- how that control pattern grows into broader request orchestration
- why the harness is the authority boundary for execution
- how RAG fits as one capability inside a governed system
- a named end-to-end reference stack, assembled in `CH03_RAG-Layer.md`
- how the same architecture connects to system-design and AI-coding principles

## What This Set Does Not Yet Fully Define

- calibration of the first-version confidence thresholds against labeled data
- detailed per-domain golden sets for routing, permission, and retrieval
- full production alert thresholds for latency, failure, and escalation drift
