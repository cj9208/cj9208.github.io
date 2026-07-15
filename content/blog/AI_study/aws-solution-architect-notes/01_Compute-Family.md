---
title: "Compute Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Compute services run application logic. The main architect question is where code should run and how much operational responsibility the team should keep."
summary: "Compute services run application logic. The main architect question is where code should run and how much operational responsibility the team should keep."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "01_Compute-Family"
---
## Family Role

Compute services run application logic. The main architect question is where code should run and how much operational responsibility the team should keep.

## Main Decision Dimensions

- control vs abstraction
- operational burden vs delivery speed
- long-running vs event-driven execution
- packaging model: VM, container, function
- predictable vs bursty traffic
- platform standardization vs simplicity

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `EC2` | Virtual machine | Managed infrastructure, self-managed OS and app | Maximum control workloads | Full runtime and OS control | Highest ops burden | Choose when you need custom OS, agents, drivers, or legacy patterns |
| `Auto Scaling` | Capacity control for EC2 | Managed scaling layer | Elastic EC2 fleets | Handles variable capacity better than static EC2 | Still requires instance/platform management | Pair with EC2 for scalable VM-based platforms |
| `Lambda` | Function | Serverless | Event-driven and bursty workloads | Minimal ops and very fast elasticity | Runtime, duration, and execution-model limits | Choose for short-lived event-based logic |
| `ECS` | Containers | Managed orchestrator | Containerized apps without Kubernetes complexity | Good balance of control and simplicity | Less portable than Kubernetes-centric platforms | Choose for AWS-native container platforms |
| `EKS` | Kubernetes | Managed control plane | Teams that need Kubernetes features or standardization | Ecosystem compatibility and portability | Highest platform complexity in this family | Choose only when Kubernetes is a real requirement |
| `Fargate` | Serverless container runtime | Serverless for ECS or EKS tasks | Containers without host management | Removes node management | Less host-level control and sometimes higher unit cost | Choose when container simplicity matters more than host tuning |
| `Elastic Beanstalk` | Managed app platform | Managed platform | Simpler traditional web app hosting | Fast path for standard app stacks | Less flexible and less strategic for modern platforms | Use when team wants managed app hosting with basic customization |
| `App Runner` | Managed app runtime | Managed / serverless-like | Simple web services from source or container | Very low operational effort | Limited control compared with ECS or EC2 | Choose for straightforward web apps and APIs |
| `Batch` | Batch scheduler | Managed scheduler over compute | Offline jobs, scheduled processing, queue-based jobs | Strong fit for non-interactive compute | Not meant for serving traffic | Choose for batch pipelines and large job queues |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Full machine control | `EC2` |
| Event-driven code with minimal ops | `Lambda` |
| Containers with simpler AWS-native operations | `ECS` with `Fargate` or EC2 |
| Kubernetes platform | `EKS` |
| Simple managed web service hosting | `App Runner` |
| Scheduled or queued jobs | `Batch` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Startup MVP API | `Lambda` or `App Runner` | Fast delivery, low ops |
| Enterprise internal app | `ECS` or `EC2` | Stronger control and integration flexibility |
| Multi-team platform standardizing on Kubernetes | `EKS` | Shared operating model |
| Legacy application needing OS-level agents | `EC2` | Host-level control |
| Bursty background image processing | `Lambda` or `Batch` | Elastic execution |
| Long-running microservices | `ECS` or `EKS` | Better fit than short-lived functions |

## What To Study Deeply Per Service

- scaling model
- packaging and deployment model
- network attachment model
- security boundary and IAM usage
- execution limits and quotas
- observability model
- cost shape under steady vs bursty load

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}}) for:

- `EC2`
- `Lambda`
- `ECS`
- `EKS`
- `Fargate`
- `App Runner`
- `Batch`
