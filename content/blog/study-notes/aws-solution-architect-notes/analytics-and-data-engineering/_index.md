---
title: "Analytics And Data Engineering Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-27T09:46:25+08:00
draft: true

description: "Analytics and data engineering services ingest, process, transform, store, search, and visualize large-scale data."
summary: "Analytics and data engineering services ingest, process, transform, store, search, and visualize large-scale data."

categories:
  - "Study Notes"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "08_Analytics-and-Data-Engineering-Family"
---
## Family Role

Analytics and data engineering services ingest, process, transform, store, search, and visualize large-scale data.

## Main Decision Dimensions

- batch vs stream
- lake vs warehouse vs search
- query-in-place vs modeled warehouse
- managed simplicity vs engine flexibility
- latency vs scale vs cost
- data movement vs federation

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `Athena` | Serverless SQL over data lake | Serverless | Querying data in S3 without managing infrastructure | Fast start and low admin effort | Performance and cost depend on data layout | Use for ad hoc and lake queries |
| `Glue` | ETL and data catalog | Managed | Data cataloging and transformation pipelines | Strong AWS data ecosystem integration | ETL design quality still matters | Use for metadata and transformation foundation |
| `EMR` | Big data cluster platform | Managed | Spark, Hadoop, and flexible data processing | Powerful and flexible data engines | More platform decisions and tuning | Use when engine-level control is needed |
| `Kinesis Data Streams` | Streaming ingestion | Managed | Real-time streaming ingestion | Good fit for event streams | Streaming design and shard planning matter | Use for custom stream processing pipelines |
| `Kinesis Data Firehose` | Managed delivery stream | Managed | Low-ops delivery to sinks | Simple ingestion to destinations | Less flexible than custom stream processing | Use for simpler ingestion pipelines |
| `Redshift` | Data warehouse | Managed | Large-scale SQL analytics | Strong warehouse model | Requires warehouse-oriented design | Use for curated analytical serving |
| `OpenSearch Service` | Search and analytics engine | Managed | Search, log analytics, operational analytics | Rich search and indexing capabilities | Index design and cluster sizing matter | Use when search is primary |
| `MSK` | Managed Kafka | Managed | Kafka-based streaming platforms | Kafka compatibility | Kafka operational concepts still matter | Use when Kafka ecosystem is required |
| `QuickSight` | BI visualization | Managed | Dashboards and business reporting | Managed dashboard layer | Depends on source data quality and modeling | Use for AWS-native BI dashboards |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| SQL on S3 data lake | `Athena` |
| Managed metadata and ETL | `Glue` |
| Flexible Spark or Hadoop processing | `EMR` |
| Real-time stream ingestion | `Kinesis` or `MSK` |
| Curated analytics warehouse | `Redshift` |
| Search-centric analytics | `OpenSearch Service` |
| Dashboards | `QuickSight` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Data lake exploration | `S3` plus `Athena` plus `Glue` | Low-admin query model |
| Enterprise ETL pipelines | `Glue` or `EMR` | Managed transformation vs engine flexibility |
| Clickstream or event stream analytics | `Kinesis` or `MSK` | Streaming ingestion |
| Management reporting | `Redshift` plus `QuickSight` | Warehouse plus BI layer |
| Log search and operational analytics | `OpenSearch Service` | Search-first experience |

## What To Study Deeply Per Service

- data ingestion pattern
- schema and catalog strategy
- partitioning and file layout impact
- stream throughput model
- query latency vs cost tradeoff
- data retention and lifecycle strategy

## When Not To Start Here

- Do not start with `Redshift` for OLTP application data or tiny ad hoc datasets.
- Do not start with `Athena` for repetitive low-latency dashboards if the data layout is poor and query frequency is high.
- Do not start with `EMR` when the main goal is the lowest operational overhead.
- Do not use `OpenSearch Service` as a replacement for the primary transactional data store.

## Practical Architect Checks

- Define data freshness, latency, and query-cost expectations before selecting tooling.
- Review partitioning, file layout, indexing, and schema evolution early.
- Check data retention, lifecycle, and reprocessing strategy for both batch and stream paths.
- Confirm governance for sensitive data, access control, and auditability.
- Model spend by data scanned, cluster uptime, stream throughput, and storage growth.

## Expert-Level Coverage Additions

- Distinguish exploratory analytics patterns from governed enterprise data-platform patterns.
- Include data contract, schema evolution, and replay strategy across producers and consumers.
- Record where query-in-place stops being economical or operationally clean.
- Add cross-account data-sharing and data-sovereignty considerations for mature platforms.

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "../00_Architect-Study-Template.md" >}}) for:

- `Athena`
- `Glue`
- `EMR`
- `Kinesis`
- `Redshift`
- `OpenSearch Service`
- `MSK`
- `QuickSight`

## Flagship Service Plan

| Service | Why It Belongs | Link | Status |
|---|---|---|---|
| `Athena` | Default query-in-place model for AWS-native lake exploration | [`athena.md`]({{< relref "./athena.md" >}}) | done |
| `Glue` | Main metadata and managed-transformation backbone for the AWS data platform | [`glue.md`]({{< relref "./glue.md" >}}) | done |
| `Redshift` | Add when curated warehouse serving becomes important enough to deserve a dedicated flagship note | - | conditional |
| `Kinesis` | Add when real-time ingestion and streaming become a stronger focus than batch and lake patterns | - | conditional |
