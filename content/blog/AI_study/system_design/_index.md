---
title: "System Design 学习地图"
date: 2026-09-01T22:21:00+08:00
lastmod: 2026-09-01T22:21:00+08:00
draft: false

categories:
  - "AI Study"
tags:
  - "Architecture"
  - "Distributed Systems"
  - "System Evolution"

slug: "system-design"
---

This section treats system design as the discipline of solving scaling bottlenecks — not as a laundry list of patterns to memorize.

```text
Every architectural pattern exists to solve the physical or organizational
bottleneck that broke the previous, simpler design.
```

The map is deliberately framed as an evolutionary story: an application travels from a single in-memory script to a consensus-governed distributed cluster, and every stage is the answer to the specific bottleneck that just broke the previous design. Two cross-cutting axes run through the ladder — the availability axis (replication / HA) and the scalability axis (partitioning) — and a short practice loop turns the reading into hands-on intuition.

## Articles

* [System Design Master Roadmap: Evolutionary Architecture & Complete Learning Blueprint]({{< relref "./system_design_master_roadmap.md" >}})
  A six-stage evolutionary map (Stage 0 → 5) with a book-to-stage learning matrix, a 3-step synthetic mastery loop (trade-off cards, micro-primitive labs, whiteboard simulations), and real-world migration post-mortems to ground the theory.
