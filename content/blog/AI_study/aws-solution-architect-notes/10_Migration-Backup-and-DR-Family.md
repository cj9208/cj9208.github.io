---
title: "Migration Backup And DR Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Migration, backup, and disaster recovery services move workloads into AWS and help protect and restore them."
summary: "Migration, backup, and disaster recovery services move workloads into AWS and help protect and restore them."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "10_Migration-Backup-and-DR-Family"
---
## Family Role

Migration, backup, and disaster recovery services move workloads into AWS and help protect and restore them.

## Main Decision Dimensions

- one-time migration vs continuous replication
- backup vs standby vs full disaster recovery
- acceptable downtime during migration
- RPO and RTO targets
- centralized backup governance vs workload-local recovery design
- data movement scale and network limits

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `AWS Backup` | Central backup management | Managed | Policy-based backup across services | Central control and reporting | Recovery design still needs workload context | Use as backup governance baseline |
| `DMS` | Database migration and replication | Managed | Migrating and replicating databases | Reduced migration friction | Complex schema/app behavior still needs planning | Use for database transition projects |
| `Application Migration Service` | Server migration | Managed | Lift-and-shift server migration | Lower-friction server moves | Does not replace app modernization design | Use for rehosting workloads |
| `Elastic Disaster Recovery` | DR replication and recovery | Managed | Recovering server-based workloads | Managed DR path for many server workloads | Not a substitute for all app-native DR patterns | Use when server-level DR is needed |
| `Snow Family` | Physical data transfer / edge device | Managed hardware/service | Large-scale or constrained-connectivity transfers | Solves data movement constraints | Logistics and batch-style workflow | Use when networks are the bottleneck |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Centralized backup governance | `AWS Backup` |
| Database migration | `DMS` |
| VM/server rehosting | `Application Migration Service` |
| DR for server workloads | `Elastic Disaster Recovery` |
| Massive data transfer with limited network | `Snow Family` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Enterprise backup standardization | `AWS Backup` | Policy and coverage centralization |
| On-prem database migration | `DMS` | Replication and cutover support |
| Data-center server migration | `Application Migration Service` | Rehost path |
| DR program for critical legacy apps | `Elastic Disaster Recovery` | Managed recovery workflow |
| Petabyte-scale data import | `Snow Family` | Network bypass |

## What To Study Deeply Per Service

- replication and consistency model
- cutover strategy
- restore validation process
- RPO/RTO alignment
- backup coverage gaps and exclusions
- testing frequency and runbook maturity

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}}) for:

- `AWS Backup`
- `DMS`
- `Application Migration Service`
- `Elastic Disaster Recovery`
- `Snow Family`
