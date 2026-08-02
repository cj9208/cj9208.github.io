---
title: "Architect Study Template"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-27T09:46:25+08:00
draft: true

description: "Use this template for any AWS service."
summary: "Use this template for any AWS service."

categories:
  - "Study Notes"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "00_Architect-Study-Template"
---
Use this template for any AWS service.

This version is aimed at expert-level architecture notes, not just associate-level summaries.

Examples:

- `Aurora`
- `Lambda`
- `EKS`
- `CloudFront`
- `SQS`

## 1. Service Identity

| Field | Notes |
|---|---|
| Service name |  |
| Family | Compute, storage, database, networking, etc. |
| Primary purpose |  |
| Abstraction model | VM, function, object store, relational DB, queue, CDN, etc. |
| Management model | Self-managed, managed, serverless |
| State model | Stateless, stateful, durable, cache, ephemeral |
| Scope | Zonal, regional, global, edge |
| Closest AWS alternatives |  |

## 2. Default Fit And Non-Fit

Answer these:

- What problem does it solve better than nearby alternatives?
- What kind of team is it good for?
- What type of workload naturally fits it?
- What are the main reasons not to choose it?

Also answer:

- When is it the best default choice?
- When is it a dangerous default choice?
- What assumptions must be true for the recommendation to hold?

## 3. High-Impact Settings

List only the settings that materially change architecture, cost, risk, or operations.

| Setting | What It Controls | Default / Common Baseline | Increase / Enable When | Decrease / Disable When | Risks | Cost Impact | Metrics To Watch |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |

## 4. Decision Dimensions

Use these as the main tradeoff lenses.

- performance
- availability
- durability
- scalability
- security
- recovery
- cost
- operational simplicity
- compliance
- portability

## 5. Constraint-Driven Decision Matrix

Expert-level notes should show how the answer changes under constraints.

| Constraint | Recommended Posture | Why | What Changes vs Default | Main Risks |
|---|---|---|---|---|
| Lowest operational burden |  |  |  |  |
| Lowest steady-state cost |  |  |  |  |
| Lowest migration risk |  |  |  |  |
| Highest compliance pressure |  |  |  |  |
| Lowest latency requirement |  |  |  |  |
| Highest team autonomy requirement |  |  |  |  |
| Strict multi-account governance |  |  |  |  |
| Fastest time to market |  |  |  |  |

## 6. Scenario Matrix

This section is the most important. Learn settings through scenarios.

| Scenario | Workload Traits | Recommended Baseline | Why | Main Risks | Metrics / Validation |
|---|---|---|---|---|---|
| Dev / sandbox | low criticality, low cost priority |  |  |  |  |
| Small production | moderate traffic, moderate risk |  |  |  |  |
| Enterprise production | strong availability and control needs |  |  |  |  |
| Spiky workload | bursty traffic |  |  |  |  |
| Read-heavy | high read ratio |  |  |  |  |
| Write-heavy | high write ratio |  |  |  |  |
| Latency-sensitive | tight response targets |  |  |  |  |
| Regulated workload | strict security/compliance |  |  |  |  |
| Disaster-recovery sensitive | strict RPO/RTO |  |  |  |  |
| Cost-optimized | cost is primary constraint |  |  |  |  |

## 7. Failure Mode Review

For the service, answer:

- What are the most common scaling failures?
- What are the most common availability failures?
- What are the most common security misconfigurations?
- What settings most often create unexpected bills?
- What limits or quotas matter early?
- Which failure modes are self-healing, and which still need human action?
- What degrades first when traffic, data volume, or dependency latency grows?

## 8. Cost Shape Review

Do not list prices. Describe cost behavior.

- What drives cost at low scale?
- What drives cost at medium scale?
- What drives cost at high scale?
- What hidden or secondary costs appear around this service?
- Under what workload shape does this service become economically weak?
- What metrics best predict cost drift?

## 9. Metrics, Logs, and Alerts

| Signal Type | What To Watch | Why It Matters |
|---|---|---|
| Capacity |  |  |
| Latency |  |  |
| Errors |  |  |
| Saturation |  |  |
| Throttling |  |  |
| Cost |  |  |
| Security |  |  |

## 10. Security And Governance Model

| Topic | Questions To Answer |
|---|---|
| Human access | How do operators and engineers access it? |
| Workload identity | How do applications and automation access it? |
| Encryption | Who owns keys and key policy? |
| Network boundary | Public, private, hybrid, edge? |
| Secrets | Where do credentials or tokens live? |
| Auditability | Which logs, trails, and findings matter? |
| Org design | Does the service belong in workload accounts, shared services, or centralized security/ops accounts? |

## 11. Multi-Account And Org Considerations

- What changes when the design moves from one account to many accounts?
- Which cross-account access patterns are clean, and which are risky?
- Does the service create centralization pressure, or should it remain workload-local?
- How does it interact with SCPs, centralized logging, or shared networking?
- What account boundary reduces blast radius most effectively?

## 12. Resilience And Recovery Design

| Topic | Notes |
|---|---|
| Availability scope | Single AZ, multi-AZ, regional, global, edge |
| Stateful dependency risks |  |
| Backup model |  |
| Restore model |  |
| DR posture | backup only, pilot light, warm standby, active/passive, active/active |
| Target RPO / RTO fit |  |
| Test method |  |

## 13. Evolution Path

Expert notes should describe how architectures evolve.

| Stage | Recommended Design | Why | Trigger To Move Forward |
|---|---|---|---|
| MVP |  |  |  |
| Growth |  |  |  |
| Enterprise |  |  |  |
| Regulated / mission-critical |  |  |  |

## 14. Architecture Decision Notes

Capture decisions in this style:

| Question | Decision | Why | Revisit Trigger |
|---|---|---|---|
| Why this service over alternatives? |  |  |  |
| Which settings were customized? |  |  |  |
| Which defaults were intentionally kept? |  |  |  |
| What would trigger redesign? |  |  |  |

## 15. Comparison Snapshot

Keep a short comparison with the nearest alternatives.

| Service | Better For | Worse For |
|---|---|---|
| Current service |  |  |
| Alternative 1 |  |  |
| Alternative 2 |  |  |

## 16. Anti-Patterns And Expert Warnings

- What are the most common overengineering mistakes here?
- What are the most common underengineering mistakes here?
- What advice is often repeated but becomes wrong at scale?
- What looks simple in a lab but becomes painful in production?

## 17. Practical Study Loop

1. Read the AWS overview and best-practice docs.
2. Identify the nearest competing services.
3. List high-impact settings only.
4. Build scenario-specific recommendations.
5. Analyze failure modes and cost shape.
6. Decide how org boundaries, security, and DR change the answer.
7. Write down what would make you change the design later.
