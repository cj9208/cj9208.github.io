---
title: "Preface"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-08-27T14:54:47+08:00
draft: true

description: "This design started from a concrete RAG problem."
summary: "This design started from a concrete RAG problem."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"

slug: "CH00_Preface"
---
## Why This Design Exists

This design started from a concrete RAG problem.

The initial issue was simple:

> RAG performs badly when the input request is dirty, ambiguous, underspecified, or expressed in a form that does not match the downstream knowledge system.

So the first architectural move was not to redesign the whole platform.

It was to add an intention layer before RAG in order to clean, normalize, and shape the input.

That is the true starting point of this design set.

## The First Abstraction

The first abstraction was:

```text
dirty user input
-> intention layer
-> RAG
```

The intention layer exists to prepare the request before it reaches the downstream task.

Its role is to:

- clarify ambiguity
- normalize wording
- identify business-relevant constraints
- convert raw user language into task-ready input

At this stage, the problem was still centered on RAG.

## From Intention Layer to Orchestration

The next step was a change in viewpoint.

Instead of treating RAG as the entire system, RAG can be treated as one tool.

Once that happens, the intention layer is no longer only a preprocessor for RAG.

It becomes the starting point of a broader orchestration flow.

That flow looks like:

```text
user request
-> intention handling
-> generate tool input
-> execute tool
```

In the early form, there is only one important tool: RAG.

So the shape becomes:

```text
user request
-> intention layer
-> generate RAG input
-> execute RAG
```

From there, the system extends naturally.

If RAG can be treated as one tool, then other downstream capabilities can also be treated as tools.

That leads to the next extension:

```text
user request
-> intention handling
-> tool search or selection
-> generate tool input
-> execute selected tool
```

This is how the request orchestration layer emerges.

It is not a separate idea invented first.

It is the natural generalization of using intention handling as the starting point for tool execution.

## Two Parts of This Design Set

This document set therefore has two major parts.

| Part | Main question |
| --- | --- |
| Evolution of orchestration | how does the system grow from intention handling for one downstream task into general tool orchestration? |
| Design of RAG | how should the RAG tool itself be designed internally? |

These two parts are related, but they are not the same problem. The first is about control flow and system evolution; the second is about the internal architecture of the most important downstream tool. The same evolve, modularize, and compose logic appears at both levels — across the whole system as intention handling grows into orchestration, and inside RAG as the subsystem is split into smaller reusable modules.

The design style behind this evolution is not original to this set. Which principles it draws on, and how they show up in each layer, are summarized in the Principles section of the section index.

## What Can Be Standardized Early

Even when detailed tool and business contracts are still evolving, some cross-cutting structure benefits from early standardization, because these parts recur in almost every future project:

| Area | Typical common concerns | Where it lands later |
| --- | --- | --- |
| trace | request lineage, session linkage, step identity | `CH02_01` runtime objects and event traces |
| governance | permission scope, policy decision, redaction state | `CH02_03` decision tables; enforced per module |
| audit | timestamps, module, action, outcome, reason | `CH02_01` execution records |
| identity | user identity, actor type, tenant, domain scope | permission context carried through every layer |
| risk | risk level, confirmation need, escalation state | `CH01` routing gates and `CH02_03` validation |
| version | schema version, capability version, module version | publish boundaries in `CH03_01`/`CH03_02` |
| status | state, error, fallback reason | `CH02_02` state machine fields |

So the design standardizes this common control envelope early — it later materializes as the typed runtime objects in `CH02_01_Runtime-Objects.md` — while letting business-specific and tool-specific payloads evolve until stable repeated patterns appear. In other words: standardize only what has already proven universal across projects.

## Why RAG Gets a Full Chapter

RAG is the most important downstream example in this design set.

It is the task that made the input-quality problem concrete in the first place.

It is also the best downstream example for showing:

- ingestion and validation
- OCR and structure reconstruction
- enrichment, chunking, and indexing
- retrieval design
- grounded answering
- local control and governance enforcement

So RAG is not only one tool among many.

It is the most important concrete example used here to make the architecture operational.

## Runtime View

At runtime, the system should be read like this:

```text
user request
-> orchestration begins with intention recognition
-> routing and tool selection
-> tool input construction
-> governed tool execution
  -> most importantly, RAG
```

And inside RAG:

```text
ingestion and validation
-> enrichment, chunking, indexing
-> retrieval
-> grounded answering
```

So the full architecture has two layers of flow:

1. orchestration across tools
2. internal execution inside the chosen tool

Per-chapter responsibilities and reading order live in the section index, so they are not duplicated here.

## Final Note

This design did not start from a desire to create a large architecture.

It started from a practical problem: RAG receives bad input and performs badly.

The intention layer was introduced to solve that problem.

Once RAG was treated as a tool, that same intention layer naturally became the starting point of orchestration.

From there, the architecture splits cleanly into two concerns:

1. how to orchestrate tools
2. how to design the RAG tool well
