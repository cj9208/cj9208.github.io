---
title: "Architecture Learning Map: Machine, Trust & Coordination Regimes"
date: 2026-09-01T22:21:00+08:00
lastmod: 2026-09-02T23:42:00+08:00
draft: false

categories:
  - "AI Study"
tags:
  - "Architecture"
  - "Distributed Systems"
  - "System Evolution"
  - "Enterprise Governance"
  - "Organizational Design"

slug: "system-design"
---

This section treats architecture as the discipline of resolving *friction* — not as a checklist of patterns to memorize. Three kinds of friction shape every real system, and each one deserves its own learning map:

```text
1. Machine friction        — physics & scale: the bottleneck that broke the previous design.
2. Trust friction          — external accountability: proving to regulators, auditors,
                             courts and enterprise clients that the system can be believed.
3. Coordination friction   — internal collaboration: Conway's Law, cognitive load and
                             platform engineering decide what architecture can actually ship.
```

**The three regimes:**

* **Machine regime** — a *timeline*. An application evolves from a single in-memory script to a consensus-governed cluster; every rung is the answer to the specific bottleneck that just broke the design below it. Covered by the *System Design Master Roadmap*.
* **Trust regime** — a *constraint field*, not a workload. Compliance never triggers a scale migration; it silently forbids the poles you are allowed to choose. Any product that touches money, personal data, health records, or regulated markets acquires this regime — it is not a second species of company. Covered by the *Trust & Governance Regime* article.
* **Coordination regime** — an *org decision* the machine ladder hides. The roadmap's Stage 2→3 trigger is literally "multi-team collisions": team boundaries determine system shape (Conway), and cognitive load determines how much a team can own. Covered by the *Coordination Regime* article.

**Reading order.** Start with the Master Roadmap to build the machine model, then read the Coordination Regime to understand why teams choose one pattern over another, and finish with the Trust Regime for the constraints that decide which poles are even legal.

## Articles

* [System Design Master Roadmap: Evolutionary Architecture & Complete Learning Blueprint]({{< relref "./system_design_master_roadmap.md" >}})
  A six-stage evolutionary map (Stage 0 → 5) driven by scaling bottlenecks, with a book-to-stage learning matrix and a synthetic mastery loop.
* [Trust & Governance Regime: Architecting Systems That Must Prove Themselves]({{< relref "./trust_governance_regime.md" >}})
  Organizational milestones (SOC2 → payments → data residency → breach/audit → IPO) as the triggers, and constraint axes (evidence, retention, identity, data protection, control, recovery) that rewrite which poles of the machine roadmap are permissible.
* [Coordination Regime: Conway's Law, Cognitive Load & the Platform]({{< relref "./org_coordination_regime.md" >}})
  Conway's Law, cognitive load budgets, Team Topologies and platform engineering — the org dimension embedded but never made explicit in the machine ladder.
