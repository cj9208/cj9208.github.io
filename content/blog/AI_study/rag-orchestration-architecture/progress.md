---
title: "Progress"
date: 2026-07-16T14:17:00+08:00
lastmod: 2026-08-27T12:01:00+08:00
draft: true

description: "Internal review note for the RAG orchestration architecture folder. Not linked from published pages."
summary: "Internal review note for the RAG orchestration architecture folder. Not linked from published pages."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"

slug: "rag-orchestration-architecture-progress"
---

## What This File Is

An internal working note, kept out of all indexes and slated for deletion once the set is published.
This is a **note set for a blog**, not an engineering project: the bar is clarity of the design story,
not production readiness. The earlier version of this file wrongly applied project-acceptance criteria
(golden sets, calibrated thresholds, alert rules). Those belong to a real deployment, not to these notes.

## What Already Meets The Blog Bar

- The origin story (dirty input → intention layer → orchestration) is the strongest asset; CH00 carries it well.
- Chapter structure CH00 → CH04 is complete and each chapter has a clear responsibility boundary.
- Decision tables (routing in `CH01`, execution/validation in `CH02_03`) are transferable knowledge as they are —
  readers need the structure and rationale, not our calibrated decimal points.
- `_index.md` already contains an honest "What This Set Does Not Yet Fully Define" section.
  That section is the correct place for limitations; no separate readiness tracking is needed.

## Remaining Work Before Publishing (desk work only)

| # | Task | Why |
|---|---|---|
| 1 | Rewrite `CH03_04_Grounded-Answering-Layer.md` and refresh its front matter | Structurally complete but low density: mostly tables, little of the narrative reasoning the other chapters have; its `lastmod` is still the placeholder time |
| 2 | In `CH03`, settle Elasticsearch vs OpenSearch into one named default, add an end-to-end reference stack summary to `CH03_RAG-Layer.md`, then update the matching limitation line in `_index.md` | Per-layer tooling sections already lean toward ES/OpenSearch plus Qdrant, but the either-or remains unresolved, the parent chapter has no tooling section, and `_index.md` still lists "no single reference stack" as a limitation |
| 3 | (Optional) Add one-line illustrative-value notes to CH01 worked cases and the CH03_02 region-confidence example | CH04 thresholds already carry a disclaimer; only these two spots show bare example decimals |

## Audit Basis For The Task List

The 2026-08-27 review checked each task against current file contents:

- Task 1 confirmed by size/timeline: CH03_01–CH03_03 are 11–34 KB, CH03_04 is 5 KB
  and was not touched in the August thickening pass.
- Task 2 narrowed: CH03_02/CH03_03 already give opinionated defaults;
  what remains is naming one index product, giving `CH03_RAG-Layer.md` a visible stack,
  and syncing `_index.md` so its limitations stay honest.
- Task 3 downgraded: `CH04` already states "These are first-version defaults, not universal
  constants", and runtime examples are framed as "Example shape"; remaining bare numbers are cosmetic.

## Explicitly Out Of Scope (do not do here)

Building golden sets, calibrating thresholds against labeled data, defining alert/intervention rules —
these require a live system and belong to a real deployment or a future ops-oriented follow-up post,
not to this design-note set.

## Publishing Options (pick one)

1. Publish now as "architecture notes in progress": structure is complete, `_index.md` states limitations honestly.
2. Publish after tasks 1–2 above (task 3 optional) as a finished set.

Either is acceptable; the set should not stay in draft indefinitely.

## Decision Log (kept short)

- Interview-related files were moved to repo-level `notes/interview/`; not part of this set.
- This file replaces the earlier engineering-style review; criteria are now blog-appropriate.
- 2026-08-27: task list revised against actual file contents. Task 2 narrowed from
  "pick a stack" (already mostly done per layer) to "name one index default + parent-chapter stack summary".
  Task 3 downgraded to optional since CH04 already carries the illustrative disclaimer.
- 2026-08-27: the two Principles notes (`System-Design-First-Principles-in-the-Era-of-AI.md`,
  `AI-Coding-and-Harness-Engineering-Principles.md`) were deleted. They duplicated, at lower
  density, two already-published articles: `ai-coding-evolution` (sections 1–3 one-to-one,
  same local-growth/observe/promote sequence) and `agent-routing-safety-harness`
  (contract-first, evaluator separation, model-proposes-harness-executes).
  `_index.md` now links the public articles directly and keeps only the four-line
  mapping of principles onto this set. The set is CH00–CH04 only now.
- 2026-08-27: follow-up check confirmed even the context-as-memory line is covered.
  Every bullet of deleted section 7 maps 1:1 into the published
  `harness-engineering/04-The-Systems-Engineering-of-LLM-Context-Management.md`
  (KV-stable prefixes, progress artifacts, sub-agent isolation, registry pruning),
  at higher density. No orphaned ideas remain; nothing needs recovery from git.
  That article is now linked from `_index.md` as well.
- 2026-08-27: the context-management link was retargeted from the single article to the
  `harness-engineering` series index, since that article belongs to a six-part set and
  the index gives readers the whole logic path. Its description stays at the principle
  level (boundary placement, context discipline, comparator design) instead of singling
  out one article.
- 2026-08-27: `_index.md` rewritten from a bare link list into an annotated reading map:
  per-chapter one-line summaries grouped by control path / RAG subsystem / evaluation,
  a concrete how-to-read section, and reflection of the day's changes (reference stack,
  CH03_04 rewrite). Also updated the `harness-engineering` series index in the same style.

