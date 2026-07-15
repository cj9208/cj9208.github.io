---
title: "Preface"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

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

These two parts are related, but they are not the same problem.

The first part is about control flow and system evolution.

The second part is about the internal architecture of the most important downstream tool.

The same evolve, modularize, and compose logic appears at both levels:

- across the whole system as intention handling grows into orchestration
- inside RAG as the subsystem is split into smaller reusable modules

## Why This Design Uses Evolving Modular Architecture

This design follows two strong ideas:

1. evolve from real problems
2. modularize when responsibilities become stable

It also follows a third idea:

3. compose larger behavior from small reusable parts

This is deliberate.

The architecture was not designed as a full platform first.

It was discovered by solving a concrete problem, identifying the reusable control pattern, and then generalizing only when that pattern proved real.

This is close to Unix or Linux design logic, though not identical to it:

- keep modules small
- keep boundaries explicit
- let larger behavior emerge through composition rather than one giant controller

| Principle | Meaning |
| --- | --- |
| evolve from real problems | abstractions should come from concrete failure modes, not from premature platform design |
| generalize gradually | move from one task to many only when the control pattern proves reusable |
| modularize by stable responsibility | split modules when ownership, inputs, outputs, and failure boundaries become clear |
| compose from small modules | prefer reusable narrow components over one large mixed controller |
| keep control local | policy may be central, but enforcement should happen in the module that touches the data |
| avoid over-design | clear fixed problems can often be designed directly; messy problems benefit from progressive abstraction |

This design style is especially useful for general, messy, or evolving problems where the right abstraction is not obvious at the start.

For tasks that are already clear, fixed, and well-specified, a more direct specification-first design is often better.

## Avoiding Fake Abstraction

One reason this design prefers evolution over premature generalization is to avoid fake abstraction.

Fake abstraction often looks like architecture, but in practice it is only:

- one more wrapper
- one more indirection layer
- one more function or class that forwards the same parameters without changing responsibility

That is usually not meaningful modularity.

A new layer should earn its existence by doing at least one of the following:

- defining a real responsibility boundary
- hiding unstable implementation details
- creating a stable contract
- reducing cognitive load for callers
- improving reuse, replacement, or ownership

If a layer only passes the same parameters inward without simplifying behavior or ownership, it is probably not a good abstraction.

This is another reason the design grows incrementally.

Evolving from real problems makes it easier to see whether an abstraction actually changes the structure of the system or merely adds ceremony.

## What Can Be Standardized Early

Even when detailed tool and business contracts are still evolving, some cross-cutting structure can still be standardized early.

The best candidates are the parts that are likely to remain useful across almost all future projects.

| Area | Typical common concerns |
| --- | --- |
| trace | request lineage, session linkage, step identity |
| governance | permission scope, policy decision, redaction state |
| audit | timestamps, module, action, outcome, reason |
| identity | user identity, actor type, tenant, domain scope |
| risk | risk level, confirmation need, escalation state |
| version | schema version, capability version, module version |
| status | state, error, fallback reason |

The design therefore does not avoid all standardization.

Instead, it standardizes the common control envelope earlier, while allowing business-specific and tool-specific payloads to evolve until stable repeated patterns appear.

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

## Reading Guide

| If you want to understand... | Start with... |
| --- | --- |
| the origin of the design | `CH00_Preface.md` |
| the intention-handling starting point | `CH01_Intention-Recognition-Layer.md` |
| the generalized orchestration logic | `CH02_Request-Orchestration-Layer.md` |
| the overall RAG design | `CH03_RAG-Layer.md` |
| ingestion and validation inside RAG | `CH03_01_Ingestion-Validation-Layer.md` |
| enrichment, chunking, and indexing inside RAG | `CH03_02_Enrichment-Chunking-Indexing-Layer.md` |
| retrieval inside RAG | `CH03_03_Retrieval-Layer.md` |
| grounded answering inside RAG | `CH03_04_Grounded-Answering-Layer.md` |

## Chapter Logic

| Chapter | Main responsibility |
| --- | --- |
| `CH01` | intention recognition as the starting point of orchestration |
| `CH02` | generalized request orchestration and tool routing |
| `CH03` | overview of RAG as the main downstream tool |
| `CH03_01` | ingestion and validation inside RAG |
| `CH03_02` | enrichment, chunking, and indexing inside RAG |
| `CH03_03` | retrieval inside RAG |
| `CH03_04` | grounded answering inside RAG |

## Final Note

This design did not start from a desire to create a large architecture.

It started from a practical problem: RAG receives bad input and performs badly.

The intention layer was introduced to solve that problem.

Once RAG was treated as a tool, that same intention layer naturally became the starting point of orchestration.

From there, the architecture splits cleanly into two concerns:

1. how to orchestrate tools
2. how to design the RAG tool well
