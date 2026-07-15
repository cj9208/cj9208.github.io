---
title: "Architect Study Template"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: true

description: "Use this template for any AWS service."
summary: "Use this template for any AWS service."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "00_Architect-Study-Template"
---
Use this template for any AWS service.

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

## 2. When To Choose It

Answer these:

- What problem does it solve better than nearby alternatives?
- What kind of team is it good for?
- What type of workload naturally fits it?
- What are the main reasons not to choose it?

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

## 5. Scenario Matrix

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

## 6. Failure Mode Review

For the service, answer:

- What are the most common scaling failures?
- What are the most common availability failures?
- What are the most common security misconfigurations?
- What settings most often create unexpected bills?
- What limits or quotas matter early?

## 7. Metrics, Logs, and Alerts

| Signal Type | What To Watch | Why It Matters |
|---|---|---|
| Capacity |  |  |
| Latency |  |  |
| Errors |  |  |
| Saturation |  |  |
| Throttling |  |  |
| Cost |  |  |
| Security |  |  |

## 8. Architecture Decision Notes

Capture decisions in this style:

| Question | Decision | Why | Revisit Trigger |
|---|---|---|---|
| Why this service over alternatives? |  |  |  |
| Which settings were customized? |  |  |  |
| Which defaults were intentionally kept? |  |  |  |
| What would trigger redesign? |  |  |  |

## 9. Comparison Snapshot

Keep a short comparison with the nearest alternatives.

| Service | Better For | Worse For |
|---|---|---|
| Current service |  |  |
| Alternative 1 |  |  |
| Alternative 2 |  |  |

## 10. Practical Study Loop

1. Read the AWS overview and best-practice docs.
2. Identify the nearest competing services.
3. List high-impact settings only.
4. Build scenario-specific recommendations.
5. Tie each decision to metrics and cost.
6. Write down what would make you change the design.
