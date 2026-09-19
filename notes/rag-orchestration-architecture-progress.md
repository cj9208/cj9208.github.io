---
title: "RAG Orchestration Architecture - Progress"
date: 2026-07-16T14:17:00+08:00
lastmod: 2026-09-19T10:20:00+08:00
draft: true
---

## What This File Is

A status record for the RAG orchestration architecture note set, now kept at the repo-level
`notes/` (outside the Hugo build, like `notes/interview/`). It started as an internal
review note inside `content/blog/AI_study/rag-orchestration-architecture/` and was moved out on
2026-09-19, when the owner chose to hold the set in draft rather than publish it. The `draft`
flag above is vestigial; the file no longer passes through Hugo.

This is a **note set for a blog**, not an engineering project: the bar is clarity of the design
story, not production readiness. An earlier version of this file wrongly applied
project-acceptance criteria (golden sets, calibrated thresholds, alert rules). Those belong to a
real deployment, not to these notes.

## What Already Meets The Blog Bar

- The origin story (dirty input → intention layer → orchestration) is the strongest asset; CH00 carries it well.
- Chapter structure CH00 → CH04 is complete and each chapter has a clear responsibility boundary.
- Decision tables (routing in `CH01`, execution/validation in `CH02_03`) are transferable knowledge as they are —
  readers need the structure and rationale, not our calibrated decimal points.
- `_index.md` already contains an honest "What This Set Does Not Yet Fully Define" section.
  That section is the correct place for limitations; no separate readiness tracking is needed.

## Remaining Work: Completed (verified 2026-09-19)

The desk-work list from the 2026-08-27 review is fully done. Verification against current files
and git history:

| # | Task | State | Evidence |
|---|---|---|---|
| 1 | Rewrite `CH03_04_Grounded-Answering-Layer.md` and refresh its front matter | Done 2026-08-27 | Commit `7581fe7` (+128 lines); file now 275 lines / 12.5 KB, prose-first, `lastmod` refreshed to `2026-08-27T11:21:30+08:00` |
| 2 | Settle Elasticsearch vs OpenSearch, add a reference stack to `CH03_RAG-Layer.md`, sync `_index.md` | Done 2026-08-27 | `CH03_RAG-Layer.md` §Reference Stack names Elasticsearch as default (OpenSearch = drop-in alternative); `_index.md` limitation removed, "named end-to-end reference stack" listed under Covered |
| 3 | (Optional) Illustrative-value notes on bare example decimals | Done 2026-08-27 | `CH01` line 261: "Signal values are illustrative examples, not calibrated production thresholds."; `CH03_02` line 176: "The confidence value above is an illustrative example, not a calibrated production value." |

No TODO / placeholder markers remain anywhere in the set. All chapters still carry
`draft: true`, which is the correct state while publication is on hold.

## Why The Earlier Table Looked Stale

The "remaining work" table was written 2026-08-27 around 09:30, from a file-state snapshot taken
before the day's work landed. The CH03_04 rewrite, the reference stack, and the disclaimers all
happened that same day between 11:21 and 21:22, but the table was never refreshed afterward
(the 2026-08-28 session went to CH02 instead). The 2026-09-19 pass re-checked each claim against
file contents, commit history, and timestamps before closing the list.

## Explicitly Out Of Scope (do not do here)

Building golden sets, calibrating thresholds against labeled data, defining alert/intervention rules —
these require a live system and belong to a real deployment or a future ops-oriented follow-up post,
not to this design-note set.

## Publishing Options (pick one when resuming)

1. Publish as "architecture notes in progress": structure is complete, `_index.md` states limitations honestly.
2. Publish after one more read-through pass (cross-chapter consistency along the reference stack).
3. A third option was added on 2026-09-19: hold without a date. The owner chose this for now.

Whenever publication resumes, the mechanical steps are: flip `draft: true` → `false` on all
CH00–CH04 files plus `_index.md`, refresh `lastmod` on each edited file, commit, then verify the
deployed pages and all cross-links on `cj9208.github.io`.

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
- 2026-08-27: `harness-engineering/_index.md` rewritten in English with per-article
  summaries and cross-links to this set and the first-principles article. While verifying
  links, found that `01-From-Prompts-to-Autopilot` was excluded from the build via
  `build: render: never`, so every link to it (including the old relref) was silently dead.
  Lock removed with owner approval; article now publishes and all six series links resolve.
  Remaining unverifiable-until-publish: links into this draft set (expected; resolves on publish).
- 2026-08-27: CH00 deduplicated. Kept the origin story and RAG-chapter rationale in full;
  merged the three principle sections (evolving modularity, Unix/Linux analogy, fake
  abstraction) into one "Design Principles Inherited From Elsewhere" section that states
  only the consequences for this set and links the published articles
  (ai-coding-evolution, linux-revival-ai-functions, harness-engineering series).
  Standardization table kept but compacted with a pointer to CH02_01 runtime objects.
  Removed the Reading Guide / Chapter Logic tables (duplicated by `_index.md`).
  `_index.md` principles list now links `linux-revival-ai-functions` too and gained a
  sixth mapping line about growing orchestration from a concrete fix.
- 2026-08-27: de-duplicated principles between CH00 and `_index.md`. Division of labor:
  `_index.md` owns the annotated link list (navigation hub); CH00 dropped its duplicated
  3-link list and points to the index instead, keeping only what is unique there — the
  four consequences for this architecture and the fake-abstraction guardrail.
  Removed the sixth mapping line from `_index.md` (now owned by CH00's consequence list).
- 2026-08-27: responsibility split finalized per owner decision: origin story lives only
  in CH00; all principle content (annotated links, style-consequence list, fake-abstraction
  guardrail) lives only in `_index.md`. CH00 keeps a one-sentence pointer to the index.
  Net effect: single lookup point for "why the design looks this way" and zero cross-page
  duplication; the removed CH00 list was redundant with its own narrative anyway.
- 2026-08-27: CH01 restructured around an explicit mental model — four-stage pipeline ×
  first-match routing contract (5 outcomes) × two cross-cutting policies (escalation
  budgets, traceability). The old Core Principles section dissolved into stage annotations;
  Routes A-D merged into per-outcome subsections under the decision table; former
  "Stage 5-8" no longer mislabeled as stages (routing is a contract, clarify/retry/handoff
  are outcomes and policies). Vocabulary unified to "escalation budget(s)" (was bounded
  retries / budgets / retry attempts); duplicate text flow diagram removed (mermaid kept);
  Why-This-Is-A-Harness list folded into Purpose. 618 → 430 lines, no content loss:
  every unique detail relocated, duplicates deleted.
- 2026-08-27: CH02 restructured in the same style (761 → 447 lines). New mental model:
  FLOW (inherited CH01 front half + eight back-half steps) × REGISTRY (capabilities as
  governed products) × four HARD BOUNDARIES (governance, cross-domain policy, escalation
  budgets, latency UX). Duplicates removed: Core Principles P1/P3 restated CH01 verbatim
  (now a one-line inheritance note); P7 folded into the Latency UX section; P8 folded into
  the Human Handoff Contract; the 90-line subchapter-split essay compressed to a
  State/Transition/Policy table; stage-table rows 1-4/6 marked as CH01-inherited instead
  of restated; Failure Taxonomy merged into Measurement And Operations (dropped from open
  questions); Deferred Memory Scope merged with Open Question #5. Vocabulary unified to
  escalation budget(s). Remaining open questions: confidence calibration, testing strategy,
  alert thresholds.
- 2026-08-27: CH03_RAG-Layer restructured the same way (292 → 208 lines). New mental model:
  offline knowledge-preparation pipeline × online per-request pipeline, meeting at published
  indexes, under locally-enforced cross-cutting controls; single mermaid now carries what four
  separate text diagrams previously repeated. Core Principles section dissolved: P1/P2/P3/P4
  became one-line design rationales inside their owning component subsections (removing
  verbatim duplication with CH03_02/03/04 principle sections), P5/P6 folded into Cross-Cutting
  Controls. Whole Picture preview merged into Mental Model. Upstream/downstream contract
  tables kept.   Baseline + Reference Stack (added earlier today) unchanged.
- 2026-08-27: CH04 rewritten with narrative-first presentation (278 → 250 lines, tables
  13 → 9; all test cases and thresholds preserved verbatim). New mental model stated
  explicitly: three layers × one golden shape × contract-to-test mapping — each of the seven
  test classes now opens with a why-narrative naming the failure it catches and the cost of
  skipping it, and the classes are ordered by request lifecycle. Small gratuitous tables
  (golden-case fields, confidence-evaluation columns, out-of-scope list, class mapping)
  converted to prose or text blocks; tables retained only for genuinely tabular case
  matrices, thresholds, and regression cadence. Added rationale paragraph on why thresholds
  mix percentage vs 100% shapes.
- 2026-08-27: the three CH02 subchapters audited and aligned. Decisions:
  (1) canonical escalation-budget schema now defined once, on the request envelope in
  CH02_01 (adds max_total_loops / max_reinterpretations / max_execution_retries to the
  envelope); CH02_02 keeps only the attempt_counters snapshot and points back;
  (2) first-version default caps unified to one definite set (6/2/2/2/1/8000), removing the
  "1 or 2" / "5 or 6" hedges and the YAML-vs-prose value mismatch;
  (3) CH02_01 routing-decision enum now includes proceed_conservative, aligned with CH01
  row 8, and the handoff packet references its contracts in CH01/CH02;
  (4) CH02_03 "Core Routing Rules" reframed as "Ordering Principles Shared By All Decision
  Tables" (they were the rationale behind CH01's row order and the two tables below);
  (5) CH02_03 Calibration Guidance reduced to a pointer to CH04 (third restatement of the
  expected/model-proposed/harness-selected trio removed); the prose Minimal Validation Rules
  list folded into the validation-table intro (same altitude as the table);
  (6) boilerplate Why/Prevents/Boundary/Tradeoff blocks compressed in CH02_02 (state
  machine, event model) and CH02_03 (safety principle, input safety gate); fallback table
  now states its division of labor vs the CH02_03 execution table.
  Line counts: CH02_01 570→580 (schema canon), CH02_02 339→302, CH02_03 549→490.
- 2026-08-27: the three CH03 subchapters audited and aligned in the same pass style.
  CH03_01 (703→570): Scope flow diagram removed (High-Level Architecture is the single
  pipeline diagram, including pass/repair/quarantine branches); the six-level validation
  taxonomy compressed to one conceptual paragraph feeding the four implementation
  categories; §1.1–1.3 bullet restatements of the deterministic master table replaced by
  three narrative notes carrying only new information (OCR-confidence limits, structural
  layer's highest-value role, semantic-check scope) and the broken dangling list at the old
  §1.3 fixed; §2's duplicated Typical-uses/Examples bullets merged into one governing-rule
  paragraph; §3.1/§3.2 bullet restatements trimmed while keeping the independent-disagreement
  principle and the cross-language caution; Tooling section now states the
  set-wide MinerU default from CH03_RAG-Layer's Reference Stack. CH03_02 (442→433): removed
  High-Level Architecture section duplicating the Scope flow. CH03_03 (322→308): Scope
  diagram removed in favor of the authoritative five-stage table; Core Principles P1 slimmed
  to a pointer. All three: front-matter lastmod refreshed (CH03_01 was still on the July
  placeholder).
- 2026-08-27: removed from `CH02` The Flow section the restating responsibility-summary
  sentence and the representative-log-fields table (a flattened preview of CH02_01's
  runtime objects). Replaced with one pointer paragraph: logging is structured per step,
  authoritative schema = CH02_01's six runtime objects. The only incremental content
  (deployment-specific extensions: scheduler/queue state, upstream dependency failures,
  redaction state) moved into CH02_01's execution-record notes as allowed contract
  extensions.
- 2026-08-27: CH02 now names the implicit two-level tool-resolution funnel: domain
  (which bounded context owns the answer) then capability (which execution family inside
  it), feeding the minimal schema surface for the resolved pair. New "Tool Resolution"
  subsection in The Flow explains why one decision is made at two altitudes (different
  signals, different failure modes, asymmetric cost — wrong domain invalidates downstream
  capability choice) and why the clarification gate sits between the levels. Mental-model
  FLOW construct and table rows 5/7 updated to carry the level-1/level-2 labels.
- 2026-08-27: moved the capability Catalog Template (YAML) from `CH02` into `CH02_01`
  as a "Registry Object: Capability Catalog Entry" section — parent keeps the conceptual
  families table, nine-element contract summary, and registry rules (now pointing at the
  schema's new home); CH02_01 scope updated to "six request-lifecycle objects plus one
  config-time artifact". Rationale: the template is a field-level schema, matching the
  object-contract style of CH02_01 rather than the parent chapter's conceptual altitude.
- 2026-08-27: split CH02's Measurement And Operations against CH04 by launch boundary.
  CH02's Offline Evaluation subsection deleted (it previewed CH04's golden sets and
  thresholds); section intro now points to CH04 for pre-launch measurement and keeps only
  post-launch operations: online measures, ownership attribution, nightly review, failure
  classification. CH04's operational-monitoring layer bullet now points back to CH02 for
  the operating model. Division: CH04 = credible before launch; CH02 = operated after.
- 2026-08-28: de-duplicated the last three CH02↔subchapter overlaps and aligned writing
  style across CH02_01/02/03. Main chapter now carries only boundary declarations plus
  pointers: Escalation Budgets → pointer to CH02_02's Loop Budget And Fallback Policy
  (which now declares itself the concrete home of that boundary); Human Handoff Contract
  → dropped the 5-item field list, points to CH02_01 Object 6; Capability Registry
  "nine things" → one-line enumeration, points to CH02_01's catalog schema. Content moved
  in its destination format: CH02_01 Object 6 gained a budget_state field (+ required) and
  a contract-item→field mapping table; Registry Object gained a nine-elements→concrete-field
  mapping table. Style unified to CH02_01's four-piece rationale blocks (Why this exists /
  What it prevents / Boundary with nearby components / Main tradeoff): CH02_02 State Machine,
  Clean Failure Handling, and Event Model prose converted; CH02_03 Safety Gate "Why This
  Belongs Before Interpretation" and both Validation sections converted; Confidence Policy
  already conformed. Narrative prose kept where it is not a discrete design decision.
  Line counts: CH02_01 580→678 (schema canon + mappings), CH02_02 302→341,
  CH02_03 490→517, CH02 main 391→365. Hugo build passes; cross-links intact.
- 2026-09-01: link format unified across the repo (commit `31e203f`): article bodies now
  cite other posts by public URL instead of `{{< relref >}}`; `_index.md` pages keep relref.
  CH01, CH02_01/02/03 front-matter `lastmod` refreshed to the same timestamp.
- 2026-09-19: verification pass re-checked the entire remaining-work list against current
  files, commit history, and mtimes. All three items were already done on 2026-08-27 (see
  table above); the stale list came from a snapshot taken before the day's edits landed.
  Nothing else in the set shows open work. Next actions when resuming: pick publishing
  option 1 or 2 above, then flip drafts + refresh lastmod + verify deployed links.
- 2026-09-19: owner decision after verification — do not publish for now; move this file
  from `content/blog/AI_study/rag-orchestration-architecture/` to repo-level `notes/`
  (consistent with `notes/interview/`). While it stays inside `content/`, it keeps
  `draft: true` so Hugo never renders it.
