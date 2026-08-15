---
title: "Director-Level Interview Guide: Orchestration Case"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-17T14:52:00+08:00
draft: true

description: "Orchestration deep dive for follow-up questions about runtime control, governance, and domain-scoped execution."
summary: "Orchestration deep dive for follow-up questions about runtime control, governance, and domain-scoped execution."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Interview"

slug: "Director-Level-Interview-Guide-Orchestration-Case"
---
## Purpose

This page is the orchestration-specific deep dive for `Director-Level-Interview-Guide.md`.

Use it only after the main interview story is clear.

Its job is to answer follow-up questions about runtime control, harness authority, domain scoping, and governed execution.

## Core Orchestration Position

If you need the orchestration argument in one paragraph, use this:

> The deeper problem is not only retrieval quality. It is governed request execution. Once a system can interpret a request, resolve ambiguity, and decide whether to proceed or clarify, it should also decide which capability should handle the request and under what policy. That is why RAG should sit inside an orchestration layer rather than act as the default path. The model helps with reasoning, but the harness owns validation, permission, risk, execution policy, and escalation.

## Why Orchestration Is The Better Abstraction

The strongest framing is as a control problem:

- retrieval is only one execution path
- ambiguity should be resolved before capability selection
- execution policy should stay outside the model
- permissions and risk vary by domain and action type
- the system needs a reusable control plane, not one prompt per workflow
- teams should not each rebuild the same compliance and request-safety logic

The key shift is:

> not every unclear request needs better retrieval; many need better routing, clarification, or refusal.

## Runtime Boundary

The clean runtime split is:

1. the request enters the intention layer
2. deterministic normalization and lightweight interpretation produce a clearer request state
3. the orchestration layer selects domain and capability path
4. the model may propose a structured tool call
5. the harness validates schema, identity, permission, and risk
6. the harness decides whether to execute, confirm, reject, or escalate
7. the system logs enough structure for review and debugging

This boundary matters because authority stays in software policy rather than in model behavior.

## What The Harness Owns

The model should:

- reason about likely next actions
- propose structured tool usage
- support ambiguity resolution when deterministic logic is insufficient

The harness should:

- validate schemas
- verify identity and permissions
- enforce risk and confirmation policy
- execute tools deterministically
- cap retries and retries-by-class
- capture outputs and errors
- reject or escalate when policy requires it

This is the production boundary that turns model reasoning into governed execution.

## Why Domain Scoping Matters

Domain scoping is a practical governance choice, not a theoretical one.

Benefits:

- smaller retrieval scope
- fewer tools exposed at once
- cleaner ownership boundaries
- easier permission modeling
- lower blast radius for regressions
- better auditability

Tradeoffs:

- shared capabilities still need common interfaces
- cross-domain requests need explicit coordination rules

The point is to keep the control plane shared while keeping execution surfaces bounded.

## Why Tools Should Stay Narrow

The orchestration layer should own sequencing and dependency control.

That means:

- tools do one narrow job
- tools should not recursively call each other
- the model should not improvise hidden execution paths
- retries, caps, and fallback belong in the orchestrator or harness

This keeps tools easier to test, safer to expose, and easier to assign ownership to.

## Tradeoffs Worth Saying Out Loud

### Deterministic First Versus Model First

Deterministic-first logic is preferable when alias repair, typo correction, canonicalization, or exact matching are common. It is cheaper, more stable, and easier to audit. Model reasoning is added where deterministic logic stops being sufficient.

### Broad Tool Exposure Versus Adaptive Tool Loading

Adaptive loading is usually better because it narrows the action space, reduces prompt size, and improves selection quality. Broad exposure only makes sense when the tool set is already tiny and low risk.

### One General Agent Versus Domain-Scoped Execution

One general agent sounds simpler, but it pushes complexity into routing ambiguity, permission surfaces, and debugging. Domain-scoped execution is usually easier to govern and operate.

### Model Autonomy Versus Harness Control

Higher model autonomy may look faster in demos, but it weakens auditability and policy enforcement. Harness control is slower to design, but much stronger for production systems.

## High-Value Follow-Up Answers

### Why not just build one powerful general agent?

Because a single general agent creates too much ambiguity in routing, tool selection, permissions, and retrieval scope. Splitting by domain keeps each subsystem smaller and easier to run, while a shared orchestration layer preserves consistent control patterns.

### Why not expose all tools to the model up front?

Because broad tool exposure increases prompt size, selection noise, and accidental misuse. Adaptive schema loading keeps the action space narrow and improves reliability.

### Why does this need a harness instead of just a smarter prompt?

Because prompts can shape model behavior, but they do not enforce permission, schema validity, confirmation rules, or audit. Those controls need to live in software policy outside the model.

### Why not let the model execute the action directly?

Because permissions, risk policy, and audit should not depend on model judgment. The harness must remain the enforcement point.

### How do you prevent the system from looping forever on ambiguity?

Use bounded retries and explicit caps. After a small number of clarification attempts or failed routes, hand off to a human with structured context.

### Where does RAG fit in this design?

RAG is one capability inside the orchestration layer. It is selected when the task requires unstructured evidence, not treated as the default path for every request.

## Open Areas To State Honestly

This deep dive is stronger when you are explicit about what still needs hardening:

- confidence calibration rules
- regression and policy evaluation depth
- alert thresholds and runtime triage
- cross-domain coordination patterns
- onboarding standards for new capabilities

Being direct about these gaps makes the orchestration story more credible, not weaker.
