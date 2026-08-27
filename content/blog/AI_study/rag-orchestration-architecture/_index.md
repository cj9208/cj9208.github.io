---
title: "RAG Orchestration Architecture"
date: 2026-07-16T14:17:00+08:00
lastmod: 2026-08-27T14:54:47+08:00
draft: true

description: "A structured note set on intention recognition, request orchestration, governed execution, and the RAG subsystem design behind them."
summary: "A structured note set on intention recognition, request orchestration, governed execution, and the RAG subsystem design behind them."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Orchestration"

slug: "rag-orchestration-architecture"
---
This note set starts from a concrete failure pattern — messy user input destroying downstream RAG quality — and follows the control logic that fixes it all the way up to a general request orchestration architecture.

The central idea is:

```text
messy request
-> intention recognition
-> capability selection and governed execution
-> RAG as one capability
```

The design follows one discipline throughout: place a deterministic boundary at each point where probabilistic behavior causes damage, instead of trying to make the model smarter.

## How To Read This Set

1. CH00 tells the origin story; read it first to see why the architecture looks the way it does.
2. CH01–CH02 are the control path (intention → orchestration); CH03 is the largest capability behind it.
3. Use the internal-layer and evaluation chapters as reference depth, not front-to-back reading.

## The Control Path

- [`CH00_Preface.md`]({{< relref "./CH00_Preface.md" >}})
  The origin story: a real dirty-input RAG problem, and why the fix had to move upstream of retrieval.
- [`CH01_Intention-Recognition-Layer.md`]({{< relref "./CH01_Intention-Recognition-Layer.md" >}})
  The first deterministic boundary: routing contract, ambiguity handling, and worked cases showing clarify/reject/execute decisions before any expensive work runs.
- [`CH02_Request-Orchestration-Layer.md`]({{< relref "./CH02_Request-Orchestration-Layer.md" >}})
  The shared runtime for a company-wide agent system: capabilities, tools, and why only the orchestration layer may sequence tool calls.
  - [`CH02_01_Runtime-Objects.md`]({{< relref "./CH02_01_Runtime-Objects.md" >}}) — the typed objects (interpretations, decisions, records) that make every step replayable and testable.
  - [`CH02_02_State-Machine-and-Control-Loop.md`]({{< relref "./CH02_02_State-Machine-and-Control-Loop.md" >}}) — request states, retries, budgets, fallback, and event flow through the loop.
  - [`CH02_03_Confidence-Safety-and-Validation.md`]({{< relref "./CH02_03_Confidence-Safety-and-Validation.md" >}}) — stage-scoped confidence assessment and the execution/validation decision tables.

## The RAG Subsystem

- [`CH03_RAG-Layer.md`]({{< relref "./CH03_RAG-Layer.md" >}})
  Entry overview for the knowledge pipeline, plus the named end-to-end reference stack (MinerU → Elasticsearch + Qdrant → BGE reranker → direct LLM API with Instructor/Guardrails helpers).
- [`CH03_01_Ingestion-Validation-Layer.md`]({{< relref "./CH03_01_Ingestion-Validation-Layer.md" >}})
  Offline quality gate: parse / OCR, structure reconstruction, validation, and quarantine so bad documents never reach the index.
- [`CH03_02_Enrichment-Chunking-Indexing-Layer.md`]({{< relref "./CH03_02_Enrichment-Chunking-Indexing-Layer.md" >}})
  Turning validated documents into retrievable units: enrichment with authoritative/inferred separation, structure-aware chunking, lexical plus vector indexing.
- [`CH03_03_Retrieval-Layer.md`]({{< relref "./CH03_03_Retrieval-Layer.md" >}})
  The online evidence-finding pipeline: query shaping, permission-aware filtering, hybrid candidate retrieval, fusion and reranking, context assembly.
- [`CH03_04_Grounded-Answering-Layer.md`]({{< relref "./CH03_04_Grounded-Answering-Layer.md" >}})
  The final guard: thin grounded generation with citation integrity, five explicit outcomes including abstention, and known failure modes of this layer.

## Evaluation

- [`CH04_Testing-and-Evaluation.md`]({{< relref "./CH04_Testing-and-Evaluation.md" >}})
  What makes the design reviewable rather than aspirational: minimum test matrix, golden-case structure, first-version acceptance thresholds, and regression strategy on top of the CH02_01 runtime objects.

## Principles Behind The Design

The worldview is not re-derived here; it lives in standalone articles:

- [AI Coding 的防御性进化：平台化、业务解耦与结构的自然生长](https://cj9208.github.io/blog/ai_study/ai-coding-evolution/)
  Why bounded sandboxes, rigid platform foundations, and late abstraction beat premature DRY when AI writes most of the code.
- [文艺复兴：从 Linux 老派教条看 AI 时代的函数开发](https://cj9208.github.io/blog/ai_study/linux-revival-ai-functions/)
  Why small pure modules with strong contracts and explicit boundaries hold up under an AI caller.
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
- no platform was designed first; orchestration grew out of a concrete RAG fix (the origin story is `CH00_Preface.md`)
- RAG was split into internal layers only after each layer's responsibility stabilized
- policy stays central in definition but local in enforcement

One guardrail that follows from this style: a new layer earns its existence only by defining a real responsibility boundary, hiding unstable details, creating a stable contract, or improving reuse and ownership. A wrapper that forwards the same parameters inward without changing responsibility or ownership is ceremony, not modularity.

## What This Set Covers And What It Does Not

Covered:

- why bad input harms downstream RAG quality and cost
- why intention recognition should happen before expensive retrieval
- how that control pattern grows into broader request orchestration
- why the harness is the authority boundary for execution
- how RAG fits as one capability inside a governed system
- a named end-to-end reference stack, assembled in `CH03_RAG-Layer.md`

Not yet defined:

- calibration of the first-version confidence thresholds against labeled data
- detailed per-domain golden sets for routing, permission, and retrieval
- full production alert thresholds for latency, failure, and escalation drift
