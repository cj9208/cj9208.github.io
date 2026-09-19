---
title: "AWS Notes Progress"
date: 2026-07-16T09:24:29+08:00
lastmod: 2026-09-19T10:36:00+08:00
draft: true

description: "Roadmap and status guide for the AWS solution architect notes collection."
summary: "Roadmap and status guide for the AWS solution architect notes collection."

categories:
  - "Study Notes"
tags:
  - "AWS"
  - "Solution Architecture"
  - "Progress"

slug: "aws-notes-progress"
---
## Purpose

This file tracks the collection at a roadmap level instead of listing every individual note change.

## 1. Initial Structure

Status: largely done

- [x] Split all main service families into their own folders
- [x] Convert the old flat family notes into family `_index.md` pages
- [x] Rework the study map into a collection-level learning guide
- [x] Add an initial set of flagship deep dives across core families
- [x] Add a top-level `_index.md` for the whole `aws-solution-architect-notes` section when the structure is stable enough

## 2. Flagship Service Plan

Status: in progress and now bounded

- [x] Define a bounded flagship-service plan format for family pages
- [x] Replace duplicated flagship sections with one table-based plan per family
- [x] Add justification for each flagship service in each family plan
- [x] Track service-level note status with `done`, `planned`, and `conditional`
- [x] Compute family flagship plan is in place
- [x] Storage family flagship plan is in place
- [x] Security and identity family flagship plan is in place
- [x] Networking and delivery family flagship plan is in place
- [x] Databases family flagship plan is in place
- [x] Integration and messaging family flagship plan is in place
- [x] Observability and operations family flagship plan is in place
- [x] Analytics and data engineering family flagship plan is in place
- [x] DevOps and infrastructure family flagship plan is in place
- [x] Migration, backup, and DR family flagship plan is in place
- [x] End-user and application services family flagship plan is in place
- [ ] Review whether any current `conditional` service should be promoted to a full planned flagship
- [x] Keep new service additions gated by the family flagship plan instead of adding notes ad hoc

## 3. Publishable Polish

Status: postponed for now

When this phase starts, focus on:

- [ ] Make tone consistent across family pages and service deep dives
- [ ] Standardize front matter fields and slug conventions
- [ ] Standardize section names and note structure where drift has appeared
- [ ] Improve cross-link quality between the collection page, family pages, and deep dives
- [ ] Add better landing-page navigation and reading flow
- [ ] Decide which notes are mature enough to move toward publication

## 4. Long-Term Evolution

Status: active long-term direction

To evolve this collection into a strong long-term lookup reference:

- [ ] Keep refining the collection page as the central mental model of the collection
- [ ] Deepen only the highest-value flagship services instead of expanding the catalog broadly
- [ ] Add more architecture-pattern notes, not just more service notes
- [ ] Strengthen cross-links between family pages and flagship deep dives
- [ ] Add more recovery, cost-shape, and failure-mode realism where notes remain too abstract
- [ ] Periodically review whether a note still belongs in the flagship set
- [ ] Periodically review whether a family needs fewer or more flagship services

## 5. Structure Decisions And Backlog

Absorbed from the deleted study map page on 2026-09-19 (internal record; not part of the published tree).

### Folder Naming Choice

The folders intentionally do not include numeric prefixes.

Use the study sequence on the collection page to express learning order instead of encoding sequence into folder names.

Reasons:

- the folders represent topic domains, not a rigid course syllabus
- the best study order can change as the collection evolves
- unnumbered names make links, filenames, and future deep dives cleaner
- service deep dives can be added naturally under each family without inheriting artificial numbering

The earlier numbered flat files made sense in the previous single-layer layout.

### Recommended Next Expert Deep Dives

To raise the collection meaningfully, prioritize these next:

1. `Redshift`
2. `SES`
3. `Transit Gateway`
4. `Application Migration Service`
5. `X-Ray`
6. `SNS`
7. `CloudFormation Guardrails / Service Catalog`
8. `GuardDuty`
9. `AppSync`
10. `DMS`

### Restructure Record (2026-09-19)

- The study map article was merged into the collection page (`_index.md`) and deleted from the published tree; the layered structure is now collection page → family pages → service pages.
- The old URL is kept as an alias: `/blog/study-notes/aws-solution-architect-notes/study-map/` redirects to the collection root.
- The public page no longer carries the service-level link list (family pages own their flagship plans) nor this backlog.

## Operating Rule

- Current mode: fast personal study notes
- Target direction: gradually become an expert lookup reference
- Growth rule: add depth intentionally, not by catalog expansion
