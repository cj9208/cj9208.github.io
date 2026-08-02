---
title: "Lambda Service Deep Dive"
date: 2026-07-16T08:34:56+08:00
lastmod: 2026-07-27T09:46:25+08:00
draft: true

description: "A completed architect-style deep dive for AWS Lambda."
summary: "A completed architect-style deep dive for AWS Lambda."

categories:
  - "Study Notes"
tags:
  - "AWS"
  - "Solution Architecture"
  - "Lambda"

slug: "12_Lambda-Service-Deep-Dive"
---
Use this as a worked example of how to fill the study template.

## 1. Service Identity

| Field | Notes |
|---|---|
| Service name | `Lambda` |
| Family | Compute |
| Primary purpose | Run event-driven code without managing servers |
| Abstraction model | Function |
| Management model | Serverless |
| State model | Stateless execution with externalized state |
| Scope | Regional service with multi-AZ managed control plane |
| Closest AWS alternatives | `ECS` with `Fargate`, `App Runner`, `EC2`, `Batch` |

## 2. When To Choose It

- Choose `Lambda` when workloads are event-driven, bursty, and operational simplicity matters more than host-level control.
- It is a strong fit for API backends, file processing, automation, glue logic, scheduled jobs, and stream consumers.
- It is especially effective when idle time is high and you do not want to pay for always-on servers.
- Do not choose it when execution time is long, runtime behavior is highly stateful, or specialized networking and host tuning are central.

## 3. High-Impact Settings

| Setting | What It Controls | Default / Common Baseline | Increase / Enable When | Decrease / Disable When | Risks | Cost Impact | Metrics To Watch |
|---|---|---|---|---|---|---|---|
| Memory size | CPU and memory allocation together | Start from a moderate memory tier and test | Latency matters, CPU-bound work exists, or init time is high | Workload is light and over-provisioned | Under-sizing increases duration and timeouts | More memory raises per-ms price but can reduce total duration | `Duration`, `Max Memory Used`, tail latency |
| Timeout | Maximum runtime per invocation | Keep tight and scenario-specific | Upstream dependency latency is variable or batch unit is larger | Retry loops should fail fast | Long timeouts hide stuck work and increase concurrency pressure | Longer execution can increase total spend | `Duration`, timeout errors, retry rate |
| Reserved concurrency | Hard cap and guaranteed capacity slice | Leave unset unless isolation is needed | Need blast-radius control or guaranteed concurrency for critical path | Shared regional pool is acceptable | Too low causes throttling; too high can starve other functions | Mainly indirect via concurrency behavior | `ConcurrentExecutions`, throttles |
| Provisioned concurrency | Pre-warmed execution environments | Off unless cold-start sensitivity is real | User-facing latency is strict and cold starts are painful | Background or asynchronous workloads tolerate init delay | Waste if traffic is low or burst pattern is misunderstood | Adds steady-state cost | init duration, p95 latency, provisioned utilization |
| VPC attachment | Private network access | Avoid unless private resources require it | Need private subnets, private databases, or internal services | Public AWS service access is enough | Adds network complexity, ENI scaling concerns, and egress cost | Can increase NAT and data transfer spend | cold-start trend, ENI errors, NAT usage |
| Event source batch size | Unit of work per poll | Keep conservative at first | Consumer overhead dominates or throughput target is high | Fine-grained failure isolation matters more | Large batches can amplify retries and partial-failure cost | Better batching can reduce invocation count | iterator age, retries, DLQ volume |

## 4. Decision Dimensions

- performance
- availability
- scalability
- security
- cost
- operational simplicity
- portability

## 5. Scenario Matrix

| Scenario | Workload Traits | Recommended Baseline | Why | Main Risks | Metrics / Validation |
|---|---|---|---|---|---|
| Dev / sandbox | low criticality, low cost priority | small memory, short timeout, no provisioned concurrency | fast to ship and cheap to idle | noisy retries and weak observability discipline | error rate, log usefulness |
| Small production API | moderate traffic, low ops tolerance | API Gateway plus Lambda, right-sized memory, alarms, no VPC unless needed | good balance of speed and ops simplicity | cold starts, dependency latency, poor timeout settings | p95 latency, throttles, timeout count |
| Enterprise production async | queue or event driven, strong reliability needs | `SQS` plus Lambda, DLQ, reserved concurrency, idempotency keys | safe async scaling with failure isolation | poison messages, duplicate processing, runaway retries | queue depth, age, DLQ count |
| Spiky workload | bursty traffic with idle periods | Lambda with concurrency review and downstream protection | elasticity without paying for idle hosts | downstream saturation and throttling | concurrency, downstream error rate |
| Latency-sensitive public endpoint | strict response target | provisioned concurrency, tuned memory, minimal dependencies | reduces cold-start impact | steady spend if traffic pattern is misread | p95/p99 latency, provisioned utilization |
| Regulated workload | stricter controls and audit expectations | KMS, least privilege, CloudTrail, private access only if needed | managed execution with strong surrounding controls | over-broad IAM and hidden secret sprawl | IAM review findings, secret access logs |

## 6. Failure Mode Review

- Common scaling failures: unbounded fan-out into a weak downstream system, concurrency spikes, and queue backlog growth.
- Common availability failures: regional dependency issues, timeouts to databases or third-party APIs, and deployment mistakes across aliases.
- Common security misconfigurations: overly broad execution roles, plaintext secrets in environment variables, and public API exposure without layered controls.
- Common billing surprises: high invocation volume from retries, unnecessary provisioned concurrency, NAT-heavy VPC traffic, and over-sized memory.
- Limits that matter early: concurrency quotas, payload size, timeout ceiling, deployment package size, and event-source specific throughput constraints.

## 7. Metrics, Logs, and Alerts

| Signal Type | What To Watch | Why It Matters |
|---|---|---|
| Capacity | `ConcurrentExecutions`, reserved concurrency utilization | Shows scaling headroom and throttling risk |
| Latency | p95 and p99 `Duration` | Captures user impact and downstream slowness |
| Errors | invocation errors and timeout count | Core reliability signal |
| Saturation | queue age, iterator age, downstream connection exhaustion | Reveals backlog and consumer stress |
| Throttling | throttles and rejected upstream requests | Indicates concurrency or downstream guardrail breach |
| Cost | invocation count, GB-seconds, provisioned concurrency hours, NAT traffic | Shows real unit economics |
| Security | role changes, secret access, unusual invoke patterns | Flags control drift and misuse |

## 8. Architecture Decision Notes

| Question | Decision | Why | Revisit Trigger |
|---|---|---|---|
| Why this service over alternatives? | Use `Lambda` for bursty event-driven logic | Lowest ops burden and natural AWS event integration | Need for long-running or host-tuned runtime grows |
| Which settings were customized? | memory, timeout, reserved concurrency, event-source batch size | These settings change latency, safety, and cost materially | Traffic pattern or downstream constraints change |
| Which defaults were intentionally kept? | no VPC and no provisioned concurrency by default | Simpler networking and cheaper idle pattern | Private resource access or strict latency requirement appears |
| What would trigger redesign? | sustained steady load or complex runtime dependencies | Container or VM model may fit better | Always-on traffic, tighter runtime control, or portability needs |

## 9. Comparison Snapshot

| Service | Better For | Worse For |
|---|---|---|
| `Lambda` | Bursty event-driven code with minimal ops | Long-running or host-dependent workloads |
| `ECS` with `Fargate` | Longer-lived container services and custom runtimes | Very small event-driven functions |
| `App Runner` | Simple always-on web services | Deep event fan-in and async triggers |

## 10. Practical Study Loop

1. Compare `Lambda` against `ECS` with `Fargate` and `App Runner` for the same workload.
2. Test memory tuning before making cost conclusions.
3. Simulate retries, DLQ behavior, and downstream failure.
4. Measure cold starts with and without VPC attachment.
5. Document when the workload would outgrow the function model.
