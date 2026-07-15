---
title: "Networking And Delivery Family"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "Networking and delivery services connect systems, isolate environments, route traffic, and improve reachability and performance."
summary: "Networking and delivery services connect systems, isolate environments, route traffic, and improve reachability and performance."

categories:
  - "AI Study"
tags:
  - "AWS"
  - "Solution Architecture"

slug: "04_Networking-and-Delivery-Family"
---
## Family Role

Networking and delivery services connect systems, isolate environments, route traffic, and improve reachability and performance.

## Main Decision Dimensions

- private vs public connectivity
- regional vs global vs edge reach
- L3/L4 vs L7 routing and control
- internal service traffic vs internet-facing traffic
- hybrid connectivity needs
- latency optimization vs simplicity

## Family Comparison Table

| Service | Model | Management | Best For | Main Strength | Main Weakness | Typical Architect Choice |
|---|---|---|---|---|---|---|
| `VPC` | Network boundary | Managed | Isolated AWS networking | Foundational isolation and routing model | Requires careful subnet and route design | Base network for most AWS architectures |
| `Route 53` | DNS and routing | Managed | Domain resolution and policy-based routing | Flexible DNS and health-based routing | DNS behavior and caching need understanding | Use for domain routing and health-aware DNS |
| `ALB` | Layer 7 load balancer | Managed | HTTP/HTTPS routing | Rich application routing and TLS handling | Not ideal for ultra-low-level protocols | Default for web applications |
| `NLB` | Layer 4 load balancer | Managed | TCP, UDP, very high-performance flows | High performance and static IP options | Less application-aware than ALB | Choose for transport-layer workloads |
| `GWLB` | Traffic appliance load balancer | Managed | Security appliance insertion | Useful for network appliance patterns | Specialized use case | Use for advanced network/security architectures |
| `CloudFront` | CDN and edge delivery | Managed global edge | Global content acceleration and caching | Edge delivery and security integration | Cache behavior requires design discipline | Default for internet-scale static and mixed delivery |
| `API Gateway` | Managed API front door | Managed | Public or private API management | Strong API features and integrations | Can be overkill for simple cases | Choose for managed API governance |
| `Global Accelerator` | Global traffic entry point | Managed global | Improved global routing to regional endpoints | Better pathing and static anycast IPs | Additional service to evaluate and pay for | Use when global latency and failover matter |
| `Transit Gateway` | Network hub | Managed | Multi-VPC and hybrid network hub | Simplifies network transit patterns | Requires network architecture discipline | Use when VPC count and connectivity grow |
| `Direct Connect` | Dedicated private link | Managed service with physical connectivity | Stable hybrid/private connectivity | Predictability and private pathing | More lead time and operational setup | Use for serious hybrid connectivity |
| `Site-to-Site VPN` | Encrypted tunnel | Managed endpoint | Faster hybrid connectivity setup | Simpler than dedicated circuits | Internet-based characteristics | Use for quicker or backup hybrid links |

## Quick Decision Guide

| If You Need | Usually Start With |
|---|---|
| Core AWS network isolation | `VPC` |
| DNS and routing policies | `Route 53` |
| HTTP load balancing | `ALB` |
| TCP or UDP load balancing | `NLB` |
| Global edge delivery | `CloudFront` |
| Managed API front door | `API Gateway` |
| Multi-VPC transit hub | `Transit Gateway` |
| Dedicated hybrid connectivity | `Direct Connect` |
| Faster-to-set-up hybrid tunnel | `Site-to-Site VPN` |

## Common Scenarios

| Scenario | Usually Good Starting Point | Why |
|---|---|---|
| Internal multi-tier application | `VPC` plus internal `ALB` | Isolation and controlled east-west traffic |
| Internet-facing web platform | `CloudFront` plus `ALB` and `Route 53` | Reach, caching, and application routing |
| Public API platform | `API Gateway` or `ALB` depending control needs | Managed API features vs simpler routing |
| Multi-account network hub | `Transit Gateway` | Centralized connectivity |
| Hybrid enterprise connectivity | `Direct Connect` plus VPN backup | Predictable primary path and fallback |

## What To Study Deeply Per Service

- routing model
- traffic scope and exposure boundary
- TLS handling and certificate integration
- failover behavior
- security control points
- cost under traffic scale
- logging and observability hooks

## Per-Service Drill-Down

Use [`00_Architect-Study-Template.md`]({{< relref "./00_Architect-Study-Template.md" >}}) for:

- `VPC`
- `Route 53`
- `ALB`
- `NLB`
- `CloudFront`
- `API Gateway`
- `Transit Gateway`
- `Direct Connect`
- `VPN`
