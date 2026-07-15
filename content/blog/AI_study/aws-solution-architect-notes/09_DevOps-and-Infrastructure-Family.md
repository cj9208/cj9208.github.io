---
title: "DevOps And Infrastructure Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "DevOps and infrastructure services define environments, package artifacts, and deliver changes safely and repeatedly."
summary: "DevOps and infrastructure services define environments, package artifacts, and deliver changes safely and repeatedly."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "09_DevOps-and-Infrastructure-Family"
---
## Family Role

DevOps and infrastructure services define environments, package artifacts, and deliver changes safely and repeatedly.

## Main Decision Dimensions

- declarative infra vs imperative setup
- code-defined platform vs console-driven drift
- deployment speed vs deployment safety
- native AWS tooling vs external platform standardization
- build isolation and artifact traceability

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `CloudFormation` | Infrastructure as code | Managed | Declarative AWS infrastructure definition | Native IaC foundation | Large templates can become hard to manage | Use as baseline AWS-native IaC engine |
| `CDK` | Infrastructure as code in programming languages | Managed synthesis to CloudFormation | Teams wanting higher-level abstractions | Better composition and reuse | Still depends on CloudFormation concepts | Use when teams prefer code over raw templates |
| `CodePipeline` | CI/CD orchestration | Managed | AWS-native delivery pipelines | Integrated release stages | Less flexible than some external CI/CD ecosystems | Use for AWS-centric pipelines |
| `CodeBuild` | Managed build execution | Managed | Build and test stages | Disposable isolated builds | Workflow design still needed | Use for build steps in native pipelines |
| `CodeDeploy` | Deployment automation | Managed | EC2, Lambda, and some app deployment workflows | Built-in deployment strategies | Often part of broader delivery stack | Use when native deployment controls fit |
| `ECR` | Container registry | Managed | Container image storage | Native AWS registry integration | Not a full software supply-chain solution by itself | Default registry for AWS container platforms |
| `Service Catalog` | Curated product catalog | Managed | Standardized approved infrastructure offerings | Governance for self-service | Requires platform maturity to get value | Use in enterprises standardizing deployments |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| AWS-native infrastructure as code | `CloudFormation` or `CDK` |
| AWS-native CI/CD orchestration | `CodePipeline` |
| Managed build environment | `CodeBuild` |
| Container image registry | `ECR` |
| Governed self-service templates | `Service Catalog` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Small AWS-native team | `CDK` plus `CodePipeline` plus `CodeBuild` | Productive native workflow |
| Enterprise platform team | `CloudFormation` or `CDK` plus `Service Catalog` | Standardization and governance |
| Container platform delivery | `ECR` plus pipeline tooling | Artifact and deployment flow |
| Highly regulated releases | `CodePipeline` with explicit approval and deployment stages | Controlled delivery |

## What To Study Deeply Per Service

- state and drift model
- environment promotion strategy
- artifact immutability and traceability
- rollback strategy
- approval and governance controls
- integration with external CI/CD tools when needed

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}}) for:

- `CloudFormation`
- `CDK`
- `CodePipeline`
- `CodeBuild`
- `CodeDeploy`
- `ECR`
- `Service Catalog`
