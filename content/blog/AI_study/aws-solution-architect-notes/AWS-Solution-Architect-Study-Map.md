---
title: "AWS Solution Architect Study Map"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "This folder is a structured study set for building an architect-level overview of AWS."
summary: "This folder is a structured study set for building an architect-level overview of AWS."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "AWS-Solution-Architect-Study-Map"
---
This folder is a structured study set for building an architect-level overview of AWS.

The goal is not to memorize every parameter. The goal is to:

- understand the role of each AWS service family
- compare similar services inside each family
- learn the main decision dimensions and tradeoffs
- use one repeatable study method for deeper service-by-service work

## How To Use This Folder

Study in 3 layers:

1. Read this overview to understand the whole landscape.
2. Read each family file to compare services within that family.
3. Use `00_Architect-Study-Template.md` when drilling into a single service such as `Aurora`, `Lambda`, or `CloudFront`.

## AWS Service Families

| Family | Role | Main Architect Question | File |
|---|---|---|---|
| Compute | Run application logic | Where should code run? | [`01_Compute-Family.md`]({{< relref "./01_Compute-Family.md" >}}) |
| Storage | Persist objects, blocks, and files | How should data be stored and accessed? | [`02_Storage-Family.md`]({{< relref "./02_Storage-Family.md" >}}) |
| Databases | Persist and query application data | What data model and engine fit the workload? | [`03_Databases-Family.md`]({{< relref "./03_Databases-Family.md" >}}) |
| Networking and Delivery | Connect, route, protect, and accelerate traffic | How do systems communicate and get exposed? | [`04_Networking-and-Delivery-Family.md`]({{< relref "./04_Networking-and-Delivery-Family.md" >}}) |
| Security and Identity | Control access and protect assets | Who can do what, and how is risk reduced? | [`05_Security-and-Identity-Family.md`]({{< relref "./05_Security-and-Identity-Family.md" >}}) |
| Integration and Messaging | Decouple systems and coordinate workflows | How should services exchange work and events? | [`06_Integration-and-Messaging-Family.md`]({{< relref "./06_Integration-and-Messaging-Family.md" >}}) |
| Observability and Operations | Monitor, audit, automate, and operate | How will the platform be seen and run? | [`07_Observability-and-Operations-Family.md`]({{< relref "./07_Observability-and-Operations-Family.md" >}}) |
| Analytics and Data Engineering | Process and analyze large-scale data | How is data ingested, transformed, queried, and visualized? | [`08_Analytics-and-Data-Engineering-Family.md`]({{< relref "./08_Analytics-and-Data-Engineering-Family.md" >}}) |
| DevOps and Infrastructure | Define infra and deliver changes safely | How do teams build, deploy, and standardize systems? | [`09_DevOps-and-Infrastructure-Family.md`]({{< relref "./09_DevOps-and-Infrastructure-Family.md" >}}) |
| Migration, Backup, and DR | Move, protect, and recover workloads | How do workloads migrate and recover? | [`10_Migration-Backup-and-DR-Family.md`]({{< relref "./10_Migration-Backup-and-DR-Family.md" >}}) |
| End-User and Application Services | Add user-facing and app-level managed capabilities | Which managed app services reduce custom build effort? | [`11_End-User-and-Application-Services-Family.md`]({{< relref "./11_End-User-and-Application-Services-Family.md" >}}) |

## Recommended Comparison Dimensions

When comparing services in the same family, use the same dimensions each time.

| Dimension | What To Ask |
|---|---|
| Primary purpose | What exact problem does this service solve? |
| Abstraction model | VM, container, function, queue, object store, relational DB, CDN, etc. |
| Management model | Self-managed, managed, or serverless? |
| State model | Stateless, stateful, cache, durable store, ephemeral? |
| Scope | Zonal, regional, global, edge? |
| Access pattern | Sync, async, stream, batch, interactive? |
| Scaling model | Manual, autoscaling, elastic, partition-based, event-based? |
| Main strength | What makes it attractive? |
| Main weakness | What complexity or limit comes with it? |
| Typical use case | When is it the natural choice? |
| Main alternatives | What else in AWS competes with it? |
| Key settings | What knobs matter first? |

## Architect Study Workflow

Use this sequence for any service:

1. Understand the family role.
2. Compare the service against its nearest alternatives.
3. Identify the 5 to 10 highest-impact settings.
4. Study the settings through scenarios, not definitions alone.
5. Tie each setting to metrics, failure modes, and cost impact.
6. Record a decision matrix for common workload patterns.

## Suggested Study Order

1. `05_Security-and-Identity-Family.md`
2. `04_Networking-and-Delivery-Family.md`
3. `01_Compute-Family.md`
4. `02_Storage-Family.md`
5. `03_Databases-Family.md`
6. `06_Integration-and-Messaging-Family.md`
7. `07_Observability-and-Operations-Family.md`
8. `09_DevOps-and-Infrastructure-Family.md`
9. `08_Analytics-and-Data-Engineering-Family.md`
10. `10_Migration-Backup-and-DR-Family.md`
11. `11_End-User-and-Application-Services-Family.md`

## Drill-Down Template

Use this file when going from overview to deep study:

- [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}})
