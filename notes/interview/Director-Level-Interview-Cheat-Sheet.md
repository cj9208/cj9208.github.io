---
title: "Director-Level Interview Cheat Sheet"
date: 2026-07-17T08:17:50+08:00
lastmod: 2026-08-18T00:00:00+08:00
draft: true

description: "Fast rehearsal page for the director-level RAG and orchestration story."
summary: "Fast rehearsal page for the director-level RAG and orchestration story."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Interview"

slug: "Director-Level-Interview-Cheat-Sheet"
---
## Core Story In One Line

Move from prompt-heavy retrieval to governed request execution, with the harness as the authority boundary.

## Focused Arc: Three Layers Of Progression

The story is a focused arc, not a single anecdote:

1. Individual tool — build one AI capability well.
2. Multi-tool / orchestration — go from one tool to a tool set: registry, routing, capability orchestration.
3. Governance / architecture / audit — permissions, policy, risk, audit, ownership, operating model.

The RAG-to-orchestration story is the concrete spine running through all three layers.

## Position Profile

Target role = Solution Lead / Architect (bank Director, Band 5 / GCB4). Cross-cutting technical influence + small-team leadership + hands-on. Frame every answer toward "cross-cutting influence + landing".

## 5-Point Answer Structure

1. Solve the immediate RAG problem with minimal disruption.
2. Use layers for fail-fast boundaries, evaluation, and ownership.
3. Make the harness the governance boundary.
4. Evolve naturally into request orchestration.
5. Split metrics so ownership stays explicit.

## 60-Second Version

> We started with a practical retrieval problem. User requests were often messy, ambiguous, or underspecified, which hurt retrieval quality and wasted downstream cost. So I first designed an intention-recognition layer that does deterministic cleanup, lightweight interpretation, confidence-aware clarification, and graceful fallback.
>
> The bigger insight was that this should not stop at retrieval. Once a system can decide whether a request is clear enough to proceed, it is already becoming the front half of a broader orchestration layer. In that architecture, RAG becomes one capability rather than the default path.
>
> The key boundary is that the model proposes, but the harness decides. The harness owns permissions, policy, risk, and execution control. Today the strongest implemented part is the intention-recognition layer, and the orchestration layer is the path for growing that into a governed platform over time.

## Signals To Emphasize

- practical improvement before platform expansion
- fail-fast boundaries and evaluation at each layer
- governance outside the model
- domain-scoped ownership
- reduced duplicated platform work across teams
- honesty about current maturity versus future direction
- org dimension: team as a distributed system (gateway + active/standby + spec-driven), small high-trust teams

## Risks To State Honestly

- confidence calibration still needs formal rules
- testing depth still needs hardening
- alert thresholds and runtime triage need refinement
- current implementation is strongest in the intention layer
- org layer is small-team only (≤10 people, trust-based)
- economics: framework exists, deployed numbers do not (org did not give rollout runway)

## Closing Line

> We are strongest today in the intention-recognition layer, and the broader orchestration layer is the path for growing that into a company-ready platform over time.
