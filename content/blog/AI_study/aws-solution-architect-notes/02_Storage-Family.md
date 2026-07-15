---
title: "Storage Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Storage services persist data outside compute. The main architect question is what storage model matches the workload: object, block, file, or archive."
summary: "Storage services persist data outside compute. The main architect question is what storage model matches the workload: object, block, file, or archive."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "02_Storage-Family"
---
## Family Role

Storage services persist data outside compute. The main architect question is what storage model matches the workload: object, block, file, or archive.

## Main Decision Dimensions

- object vs block vs file
- latency vs durability vs cost
- attached vs shared access
- hot vs cold data
- throughput pattern vs size pattern
- regional durability vs zonal attachment

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `S3 Standard` | Object storage | Managed | General object storage | Very high durability and ecosystem reach | Not a POSIX file system and not block storage | Default for files, media, artifacts, logs, and data lake objects |
| `S3 Intelligent-Tiering` | Object storage tiering | Managed | Unpredictable object access patterns | Balances storage cost without manual tier management | Monitoring and retrieval economics still matter | Use when access pattern is unclear |
| `S3 Glacier` tiers | Archive object storage | Managed | Long-term retention and archives | Very low storage cost | Slow retrieval and archive workflow constraints | Use for compliance archives and cold backups |
| `EBS` | Block storage | Managed volume attached to EC2 | Boot volumes and low-latency instance-attached storage | Strong VM-attached storage performance | Not shared like a file system and tied to EC2 patterns | Use with EC2 when applications need block devices |
| `EFS` | Shared file storage | Managed | Shared POSIX file access across instances | Simple shared Linux file system | Higher cost than object storage and not block-like | Use when many compute nodes need shared files |
| `FSx for Windows File Server` | Managed Windows file system | Managed | Windows SMB workloads | Native Windows integration | Specialized service, not general default | Use for Windows file shares and enterprise Windows apps |
| `FSx for Lustre` | High-performance file system | Managed | HPC and analytics workloads | High throughput for parallel workloads | More specialized and costlier than general-purpose options | Use for performance-heavy file workloads |
| `FSx for NetApp ONTAP` | Enterprise file storage | Managed | Workloads needing ONTAP features | Rich storage capabilities | More storage-admin complexity | Use when enterprise NAS features are required |
| `Storage Gateway` | Hybrid storage bridge | Managed appliance/service | On-prem to AWS storage integration | Eases hybrid transitions | Adds hybrid operational considerations | Use when on-prem integration is required |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Durable object storage | `S3` |
| Low-latency disk attached to VM | `EBS` |
| Shared Linux file system | `EFS` |
| Windows file shares | `FSx for Windows File Server` |
| Archive retention | `S3 Glacier` tiers |
| Hybrid on-prem storage integration | `Storage Gateway` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Static website assets | `S3` | Durable and simple object hosting |
| EC2 database or application disk | `EBS` | Instance-attached block storage |
| Shared content repository for app fleet | `EFS` | Shared file semantics |
| Data lake raw zone | `S3` | Scale, ecosystem, and low admin overhead |
| Long-term backups | `S3 Glacier` tiers | Low storage cost |
| HPC scratch or analytics file workload | `FSx for Lustre` | Throughput-oriented design |

## What To Study Deeply Per Service

- durability and availability scope
- performance model: IOPS, throughput, latency, retrieval
- access protocol and client assumptions
- lifecycle and tiering behavior
- encryption and data protection settings
- replication, backup, and restore patterns
- pricing model under real access patterns

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`](./00_Architect-Study-Template.md) for:

- `S3`
- `EBS`
- `EFS`
- `FSx`
- `Storage Gateway`
