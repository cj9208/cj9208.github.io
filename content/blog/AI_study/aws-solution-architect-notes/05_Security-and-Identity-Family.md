---
title: "Security And Identity Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Security and identity services control access, protect data, manage secrets, and improve security posture."
summary: "Security and identity services control access, protect data, manage secrets, and improve security posture."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "05_Security-and-Identity-Family"
---
## Family Role

Security and identity services control access, protect data, manage secrets, and improve security posture.

## Main Decision Dimensions

- authentication vs authorization
- human identity vs workload identity
- prevention vs detection
- encryption at rest vs in transit
- centralized governance vs local autonomy
- compliance depth vs operational simplicity

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `IAM` | Access control | Managed | AWS authorization and workload permissions | Fine-grained policy control | Policy design can become complex | Foundation for least-privilege access |
| `IAM Identity Center` | Workforce identity and access | Managed | Centralized human access to accounts and apps | Cleaner enterprise access model | Depends on identity integration design | Use for multi-account human access |
| `KMS` | Key management | Managed | Encryption key control | Central encryption governance | Key policy and usage model need careful design | Use for most AWS encryption control needs |
| `Secrets Manager` | Secret storage and rotation | Managed | Credentials, tokens, API keys | Rotation support and service integration | Costlier than simple config storage | Use for sensitive application secrets |
| `Parameter Store` | Config and optional secret storage | Managed | Simpler configuration storage | Lightweight and broadly useful | Less dedicated secret lifecycle focus than Secrets Manager | Use for config and lower-complexity secret needs |
| `Cognito` | App user identity | Managed | Customer-facing auth flows | Managed user sign-in capabilities | Identity flows still require careful design | Use for application user identity |
| `WAF` | Layer 7 request filtering | Managed | Web request protection | Managed rule and custom filter support | Needs tuning to reduce false positives or gaps | Use in front of web apps and APIs |
| `Shield` | DDoS protection | Managed | DDoS resilience | Native AWS protection layers | Advanced capabilities require evaluation | Use for internet-exposed critical workloads |
| `GuardDuty` | Threat detection | Managed | Security finding generation | Low-friction threat visibility | Findings still require response process | Use as a baseline detective control |
| `Inspector` | Vulnerability assessment | Managed | Compute and container vulnerability insight | Managed vulnerability visibility | Requires remediation workflow maturity | Use for runtime and image posture review |
| `Security Hub` | Security posture aggregation | Managed | Centralized security findings | Single pane across controls/findings | Value depends on broader security setup | Use to aggregate security posture |
| `Macie` | Sensitive data discovery | Managed | Data classification in S3 | Helps locate sensitive data | Specialized and cost-sensitive to scope | Use when data discovery/compliance matters |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| AWS permissions | `IAM` |
| Multi-account workforce access | `IAM Identity Center` |
| Encryption key control | `KMS` |
| Secret rotation and app secrets | `Secrets Manager` |
| Web request filtering | `WAF` |
| Threat detection | `GuardDuty` |
| Security findings aggregation | `Security Hub` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Startup account baseline | `IAM`, `KMS`, `Secrets Manager`, `GuardDuty` | Strong basic controls |
| Multi-account enterprise | `IAM Identity Center`, `Security Hub`, `GuardDuty`, `KMS` | Centralized governance |
| Public web application | `WAF`, `Shield`, `IAM`, `KMS` | Exposure protection and access control |
| Compliance-sensitive data platform | `KMS`, `Macie`, `Security Hub`, `CloudTrail` | Encryption, discovery, and governance |

## What To Study Deeply Per Service

- trust model and policy model
- human vs workload identity patterns
- encryption ownership and key lifecycle
- secret rotation paths
- detection coverage and response expectations
- integration points with logging and audit services

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`](./00_Architect-Study-Template.md) for:

- `IAM`
- `IAM Identity Center`
- `KMS`
- `Secrets Manager`
- `Cognito`
- `WAF`
- `GuardDuty`
- `Security Hub`
