---
title: "Integration And Messaging Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: true

description: "Integration and messaging services decouple systems, absorb spikes, route events, and coordinate workflows."
summary: "Integration and messaging services decouple systems, absorb spikes, route events, and coordinate workflows."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "06_Integration-and-Messaging-Family"
---
## Family Role

Integration and messaging services decouple systems, absorb spikes, route events, and coordinate workflows.

## Main Decision Dimensions

- queue vs pub/sub vs event bus vs workflow
- point-to-point vs fan-out
- ordered vs unordered processing
- synchronous vs asynchronous flow
- business orchestration vs transport only
- retry and failure-handling model

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `SQS Standard` | Queue | Managed | High-throughput asynchronous decoupling | Simple durable buffering | No strict ordering guarantee | Default queue choice for async workloads |
| `SQS FIFO` | Ordered queue | Managed | Ordered or exactly-once-sensitive workflows | Ordering and dedup support | Lower throughput tradeoffs vs Standard | Choose when order matters |
| `SNS` | Pub/sub | Managed | Fan-out notifications and event distribution | Simple publish-to-many pattern | Not a workflow engine | Choose when one event should reach many subscribers |
| `EventBridge` | Event bus | Managed | Event-driven integration across services | Routing rules and event-centric architecture | Event design and governance matter | Choose for event bus style integration |
| `Step Functions` | Workflow orchestration | Managed | Business or technical orchestration | Visibility and durable workflow state | Adds orchestration modeling overhead | Choose for explicit multi-step flows |
| `Amazon MQ` | Traditional message broker | Managed | Legacy protocol and broker compatibility | Familiar messaging patterns for certain migrations | More traditional broker management concepts | Choose when JMS/AMQP/MQTT-style compatibility is required |
| `AppSync` | GraphQL API and real-time integration | Managed | GraphQL backends and client data sync | Strong managed GraphQL features | Specialized app pattern | Choose when GraphQL is central to the app model |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Simple asynchronous work queue | `SQS` |
| Publish one event to many subscribers | `SNS` |
| Event bus across services and SaaS | `EventBridge` |
| Durable multi-step workflow | `Step Functions` |
| Broker compatibility for migration | `Amazon MQ` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Background order processing | `SQS` | Decouple request from processing |
| Broadcast user signup event to multiple systems | `SNS` or `EventBridge` | Fan-out delivery |
| Event-driven microservice architecture | `EventBridge` | Routing by event type and source |
| Payment workflow with retries and human steps | `Step Functions` | Durable orchestration |
| Legacy app migration with broker dependency | `Amazon MQ` | Compatibility path |

## What To Study Deeply Per Service

- delivery guarantees
- ordering and dedup behavior
- retry, DLQ, and replay model
- consumer scaling model
- event schema and governance
- cost per message, event, or state transition

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}}) for:

- `SQS`
- `SNS`
- `EventBridge`
- `Step Functions`
- `Amazon MQ`
- `AppSync`
