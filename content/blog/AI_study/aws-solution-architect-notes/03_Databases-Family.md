---
title: "Databases Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Database services persist and query application data. The main architect question is which data model, access pattern, and operational model best fit the workload."
summary: "Database services persist and query application data. The main architect question is which data model, access pattern, and operational model best fit the workload."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "03_Databases-Family"
---
## Family Role

Database services persist and query application data. The main architect question is which data model, access pattern, and operational model best fit the workload.

## Main Decision Dimensions

- relational vs key-value vs document vs graph vs time-series vs warehouse
- OLTP vs analytics
- read-heavy vs write-heavy
- consistency and transaction requirements
- scaling model and partitioning behavior
- operational simplicity vs engine control

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `RDS` | Managed relational DB | Managed | Standard relational workloads | Familiar engines with reduced admin overhead | Less cloud-native scaling than Aurora in some cases | Choose for managed MySQL, PostgreSQL, SQL Server, Oracle, MariaDB |
| `Aurora` | Cloud-optimized relational DB | Managed | High-availability relational workloads | Strong availability, performance, and managed operations | More AWS-specific and feature evaluation is required | Choose for strategic relational workloads on AWS |
| `DynamoDB` | Key-value / document | Serverless managed NoSQL | Massive scale low-latency app data | Elastic scale and low ops | Access pattern design matters a lot | Choose when primary-key access patterns dominate |
| `ElastiCache for Redis` | In-memory cache / data structure store | Managed | Caching, session, queue-like patterns, low-latency reads | Very low latency | Not a direct replacement for durable primary DBs | Choose to reduce DB load or support low-latency state |
| `ElastiCache for Memcached` | In-memory cache | Managed | Simple distributed caching | Simpler cache model | Fewer advanced capabilities than Redis | Use for simpler cache-only needs |
| `Redshift` | Data warehouse | Managed | Analytics at warehouse scale | Strong SQL analytics pattern | Not a primary OLTP store | Choose for reporting and analytical workloads |
| `DocumentDB` | Document database | Managed | Document-oriented application models | Managed document store experience | Not identical to MongoDB feature-for-feature | Use when document model is primary |
| `Neptune` | Graph database | Managed | Highly connected data | Native graph query patterns | Specialized skillset and use case | Use for graph workloads |
| `Timestream` | Time-series database | Managed | Metrics, events, IoT time data | Designed for time-series access patterns | Specialized service | Use when time dimension is primary |
| `Keyspaces` | Cassandra-compatible wide-column | Managed | Cassandra-style workloads | Managed compatibility path | Specialized operational/data model tradeoffs | Use when wide-column model is required |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Managed relational database | `RDS` or `Aurora` |
| Strategic relational platform on AWS | `Aurora` |
| Massive-scale key-value access | `DynamoDB` |
| Low-latency cache | `ElastiCache for Redis` |
| Analytics warehouse | `Redshift` |
| Document model | `DocumentDB` |
| Graph relationships | `Neptune` |
| Time-series events and metrics | `Timestream` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Standard business application | `RDS` or `Aurora` | Relational model and managed operations |
| High-growth SaaS OLTP | `Aurora` | Availability and scaling options |
| User profile / session / cart service | `DynamoDB` | Low-latency key-based access |
| Read-heavy application under DB pressure | `ElastiCache for Redis` plus primary DB | Offload repeated reads |
| BI reporting platform | `Redshift` | Analytical query model |
| IoT telemetry analysis | `Timestream` | Time-ordered data model |

## What To Study Deeply Per Service

- engine/data model fit
- read/write and query access patterns
- scaling model
- consistency and failover behavior
- backup, retention, and recovery settings
- indexing and partition strategy
- cost sensitivity to traffic shape and data volume

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`](./00_Architect-Study-Template.md) for:

- `RDS`
- `Aurora`
- `DynamoDB`
- `ElastiCache`
- `Redshift`
- `DocumentDB`
- `Neptune`
- `Timestream`
