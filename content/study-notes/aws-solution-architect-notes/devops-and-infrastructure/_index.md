---
title: "DevOps And Infrastructure Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-27T09:46:25+08:00
draft: true

description: "DevOps and infrastructure services define environments, package artifacts, and deliver changes safely and repeatedly."
summary: "DevOps and infrastructure services define environments, package artifacts, and deliver changes safely and repeatedly."

categories:
  - "Study Notes"
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

## When Not To Start Here

- Do not start with `Service Catalog` unless platform governance and self-service standardization are real goals.
- Do not force `CodePipeline` if the team already depends on a broader non-AWS delivery ecosystem that fits better.
- Do not adopt `CDK` abstractions without understanding the `CloudFormation` behaviors underneath them.
- Do not treat a container registry such as `ECR` as the whole software supply-chain story.

## Practical Architect Checks

- Decide which repository is the source of truth for infrastructure and environment promotion.
- Check drift detection, rollback workflow, and failure visibility before rollout.
- Keep artifacts immutable and traceable from source commit to deployment target.
- Review secret handling inside builds and pipelines, not just inside runtime workloads.
- Match approval steps to risk level so safety does not collapse into manual bottlenecks.

## Expert-Level Coverage Additions

- Include multi-account delivery boundaries, promotion models, and change-approval ownership.
- Record how platform standards are enforced without blocking delivery speed unnecessarily.
- Document supply-chain security posture, not just build success paths.
- Compare the operating model for small teams, platform teams, and regulated enterprises separately.

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "../00_Architect-Study-Template.md" >}}) for:

- `CloudFormation`
- `CDK`
- `CodePipeline`
- `CodeBuild`
- `CodeDeploy`
- `ECR`
- `Service Catalog`

## Flagship Service Plan

| Service | Why It Belongs | Link | Status |
|---|---|---|---|
| `CloudFormation` | AWS-native IaC foundation and drift-control baseline | [`cloudformation.md`]({{< relref "./cloudformation.md" >}}) | done |
| `CDK` | Main higher-level code abstraction for AWS-native IaC | [`cdk.md`]({{< relref "./cdk.md" >}}) | done |
| `ECR` | Main artifact-registry and container supply-chain baseline for AWS workloads | [`ecr.md`]({{< relref "./ecr.md" >}}) | done |
| `CodePipeline` | Add when delivery-pipeline design becomes important enough to deserve its own flagship note | - | conditional |
