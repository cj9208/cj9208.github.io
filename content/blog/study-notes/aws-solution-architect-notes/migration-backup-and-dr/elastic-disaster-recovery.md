---
title: "Elastic Disaster Recovery Service Deep Dive"
date: 2026-07-16T09:29:12+08:00
lastmod: 2026-07-27T09:46:25+08:00
draft: true

description: "An expert-level architect deep dive for Elastic Disaster Recovery."
summary: "An expert-level architect deep dive for Elastic Disaster Recovery."

categories:
  - "Study Notes"
tags:
  - "AWS"
  - "Solution Architecture"
  - "Elastic Disaster Recovery"
  - "Recovery"

slug: "elastic-disaster-recovery-service-deep-dive"
---
Use this as a fast expert note. `Elastic Disaster Recovery` is not a universal DR answer. It is strongest for server-style recovery where infrastructure-level replication is the practical path.

## 1. Service Identity

| Field | Notes |
|---|---|
| Service name | `Elastic Disaster Recovery` |
| Family | Migration, Backup, and DR |
| Primary purpose | Replicate server workloads for disaster recovery and controlled failover |
| Abstraction model | Managed server replication and recovery orchestration |
| Management model | Managed |
| State model | Continuous replication state and recovery orchestration metadata |
| Scope | Regional with cross-region recovery design |
| Closest AWS alternatives | native application DR patterns, snapshots, backup-only approaches |

## 2. Default Fit And Non-Fit

- Right default when server-style workloads need strong recovery posture and application modernization is not yet the immediate answer.
- Strong fit for legacy or rehosted estates where infrastructure-level replication is the fastest realistic DR improvement.
- Dangerous default when teams try to apply it to cloud-native services that need service-native recovery patterns.
- Wrong default when the application should be redesigned around managed services rather than replicated as-is.

## 3. Key Design Drivers

- server dependency mapping
- RPO/RTO targets
- failover and failback runbooks
- network and identity readiness during recovery
- cross-region recovery ownership

## 4. Failure And Cost Notes

- Main failure mode: replication exists but full application recovery still breaks on DNS, secrets, or dependencies.
- Main cost driver: replicated storage, testing, and recovery readiness overhead.
- Main anti-pattern: calling infrastructure replication a complete application DR design.

## 5. Expert Warnings

- Do not use it as a substitute for architecture review.
- Do not skip recovery drills.
- Do not ignore application dependencies outside the servers.
- Do not let DR ownership sit only with infrastructure teams if application recovery needs app-team action.
