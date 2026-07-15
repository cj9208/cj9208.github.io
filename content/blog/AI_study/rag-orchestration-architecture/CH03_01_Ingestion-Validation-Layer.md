---
title: "Ingestion Validation Layer"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "The ingestion validation layer is the upstream data production layer for the RAG system."
summary: "The ingestion validation layer is the upstream data production layer for the RAG system."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"

slug: "CH03_01_Ingestion-Validation-Layer"
---
## Purpose

The ingestion validation layer is the upstream data production layer for the RAG system.

Its job is to transform raw source artifacts into validated canonical documents that are safe enough to pass downstream into enrichment, chunking, and indexing.

This layer should be treated as an independent subsystem.

It should not rely on retrieval, reranking, or downstream generation to discover basic document quality problems.

The key idea is simple:

> Downstream intelligence should not be the first place upstream data defects are discovered.

## Scope

This document covers the pipeline from:

```text
Source
-> Acquire
-> Parse / OCR
-> Structure reconstruction
-> Canonicalize / normalize
-> Validate
-> Publish to downstream processing
```

This document does not cover:

| Out of scope | Why |
| --- | --- |
| enrichment | Happens after validated canonical documents are produced |
| chunking | Belongs to downstream retrieval preparation |
| indexing | Belongs to downstream retrieval preparation |
| retrieval | Belongs to the online evidence-finding subsystem |
| grounded generation | Belongs to downstream answer production |

Those belong to downstream RAG components.

## Why This Layer Should Be Independent

If ingestion and validation are weakly defined, downstream teams discover source defects during retrieval or user-facing answering.

That creates several bad outcomes:

| Bad outcome | Why it matters |
| --- | --- |
| failure is discovered too late | downstream systems become the first detector of upstream defects |
| debugging becomes expensive | root cause is hidden behind retrieval or answer behavior |
| the wrong subsystem gets blamed | model or retrieval teams inherit ingestion failures |
| stronger models are used to compensate for messy input | model cost increases while architecture quality stays weak |
| silent defects become visible only in production usage | users discover issues before engineers do |

This layer exists to contain those failures early.

## Design Goals

1. preserve source lineage and versioning from the start
2. reconstruct document structure before text is treated as trusted content
3. normalize multiple parser or OCR outputs into a unified internal representation
4. detect high-risk extraction failures before downstream publishing
5. repair what can be repaired safely
6. quarantine what cannot be trusted
7. publish only validated canonical documents to downstream systems

## Core Principles

### 1. Ingestion Is a Data Production System

Ingestion is not a file-loading step.

It produces an internal document representation that downstream systems depend on.

### 2. Structure Matters More Than Raw Text Volume

For many business documents, the main failure is not missing text.

The main failure is broken structure:

| Structural failure | Typical impact |
| --- | --- |
| misaligned tables | values map to wrong fields or rows |
| wrong reading order | text becomes nonsensical or misleading |
| lost section hierarchy | local text loses policy or rule context |
| merged headers and body text | section meaning becomes ambiguous |
| flattened forms or lists | structured fields become hard to validate or retrieve |

### 3. Validation Should Be a Publish Gate

Validation is not only for monitoring.

Validation should decide whether a document is allowed to move downstream.

### 4. Repair Must Be Conservative

Safe normalization and structured repair are good.

Speculative content repair is dangerous.

If confidence is too low, quarantine is better than false precision.

### 5. Multiple Independent Signals Are Better Than One Confidence Score

OCR confidence alone is not enough.

A strong validator should combine:

| Signal type | Why it is useful |
| --- | --- |
| OCR or parser confidence | early raw extraction risk signal |
| structural consistency | detects layout and table failures |
| semantic consistency | detects plausible-looking but wrong values |
| business-rule checks when available | catches domain-specific correctness failures |
| cross-extractor agreement | adds independent technical validation |
| cross-language agreement when parallel documents exist | adds independent semantic and structural validation |

## High-Level Architecture

```text
Source
-> Acquire
-> Parse / OCR
-> Structure reconstruction
-> Canonicalize / normalize
-> Validate
   -> pass
   -> repair and re-validate
   -> quarantine
-> Publish validated canonical document
```

## Module Boundaries

| Step | Responsibility | Outputs | Important rules |
| --- | --- | --- | --- |
| Acquire | fetch files, pages, records, or images from source systems; preserve source identifiers, versions, timestamps, and ACL metadata; attach provenance for every artifact | raw source artifact; source metadata; source lineage information | never lose source id or version; every downstream document must trace back to a source artifact |
| Parse / OCR | extract text from digital documents; run OCR for scanned or image-based documents; detect layout elements such as headings, paragraphs, tables, lists, and forms; capture confidence and coordinates when possible | parser or OCR output in tool-specific form | keep raw extractor output available for inspection; do not flatten everything into plain text immediately |
| Structure reconstruction | recover reading order; reconstruct section hierarchy; separate headers, footers, and body; rebuild tables and structured blocks; resolve layout artifacts such as multi-column flow | document elements with logical structure | chunking must not happen before structure reconstruction; tables must remain structured as long as possible |
| Canonicalize / normalize | map different parser or OCR outputs into one unified internal representation; normalize metadata fields into a standard schema; preserve both source truth and normalized values where needed; attach internal identifiers and trust-related fields | canonical document object; normalized metadata schema; provenance links to source and extraction method | normalization should unify representation, not silently rewrite content meaning; keep authoritative source values separate from inferred or repaired values when possible |
| Validate | detect whether the canonical document is trustworthy enough for downstream processing; attempt safe repair when possible; quarantine risky documents when trust is too low | pass; pass with warning; repair and pass; quarantine; fail | retrieval should not be the first place bad OCR or bad structure is discovered; low-trust content should not be silently published |

---

## Control and Governance in This Layer

Policy may be defined centrally, but this layer must enforce the controls that apply when raw source artifacts first enter the system.

| Control concern | How it applies in this layer |
| --- | --- |
| source-level access metadata | capture ACLs, ownership, tenancy, and visibility scope at acquisition time |
| source lineage | preserve source id, version, and provenance from the start |
| trust gating | quarantine low-trust documents before they reach downstream preparation |
| repair auditability | record whether repair was attempted and what changed |
| publish boundary | only validated canonical documents may move downstream |

Important principle:

> If access scope, lineage, or trust is lost here, downstream layers cannot recover it safely.

This is the stage where a wrapper around multiple OCR methods usually belongs.

If several extractors produce different formats, this stage converts them into one canonical document schema.

## Canonical Document Contract

By the time validation starts, the system should already have a unified internal document representation.

At minimum, it should support:

```text
document_id
source_id
source_version
language
document_type
pages
elements[]
provenance
extractor_info
acl_metadata
```

Each element should support fields such as:

```text
element_id
element_type
text
page_number
bbox_or_span
section_path
confidence
structured_payload
```

This representation gives validation one place to reason about parser output regardless of which OCR or extraction method produced it.

## Validation Framework

Validation should not try to prove the document is perfect.

It should try to detect high-risk failure patterns before they become downstream truth.

The most important design distinction is this:

- offline evaluation can use gold truth
- production gating usually cannot

That means many good evaluation metrics are not directly usable as production publish gates.

The layer therefore needs three validation views.

| Validation view | Goal | Can use gold truth? | Primary output |
| --- | --- | --- | --- |
| Offline evaluation | select extractors, parsers, validators, and thresholds | yes | model choice, rule choice, threshold calibration |
| Production gating | decide pass, warning, repair, quarantine, or fail for each document | no | publish decision |
| Post-production monitoring | detect drift, hidden failures, and quality regressions after publish | sometimes through sampling | alerts, audits, rule updates |

---

The current validation levels in this design are:

| Current level | Main purpose |
| --- | --- |
| OCR and parser confidence validation | Detect low-confidence extraction and suspicious raw OCR quality |
| Structural validation | Detect layout, ordering, hierarchy, and table-shape failures |
| Semantic validation | Detect locally implausible extracted values and field patterns |
| Business-rule validation | Detect domain-specific violations in important document classes |
| Cross-extractor validation | Detect disagreement across multiple parser or OCR methods |
| Cross-language consistency validation | Detect mismatch across bilingual or parallel document versions |

That list is useful conceptually, but it is not the best implementation view because it mixes:

- deterministic technical checks
- model-based technical checks
- business-specific checks
- comparative checks across extractors or languages

For implementation, it is better to group validation by engineering method and ownership.

Recommended flow:

```text
Canonical document
-> risk checks
-> optional repair attempt
-> re-validation
-> pass or quarantine
```

### Validation Categories

For implementation, the validation stack should be grouped into four categories:

| Category | What it covers | Primary owner | Notes |
| --- | --- | --- | --- |
| Technical deterministic validation | Rule-based checks on confidence, structure, fields, and metadata | Platform / ingestion engineering | Default first line of defense |
| Technical model-based validation | Model-assisted checks for messy structure or subtle semantic issues | Platform / applied AI engineering | Bounded support layer, not the default controller |
| Comparative consistency validation | Cross-checks across extractors or language versions | Platform / ingestion engineering | Strong independent validation signal |
| Business-specific validation | Domain checks for important document classes | Domain team with platform support | Selective, high-value, document-type-aware |

This makes it easier to decide:

- what can be implemented as hard rules
- what needs model support
- what depends on multiple views of the same source
- what belongs to domain teams rather than platform teams

### Implementation View

To make the categories implementable, each validator should define:

| Field | Meaning |
| --- | --- |
| signal | the raw measurement or detector output |
| metric | the computed value used for gating |
| threshold | the pass, warning, or fail boundary |
| scope | document, page, section, table, row, or field |
| action | pass, warn, repair, quarantine, or fail |

Thresholds should be treated as calibration inputs, not universal constants.

They should be tuned by:

- document class
- source system
- language
- extractor type
- business risk

In practice, each validation category should be expressed in both of these forms:

| Metric type | Purpose |
| --- | --- |
| Reference metric | offline metric computed against gold truth |
| Proxy metric | online or production-safe metric computed without gold truth |

The gate should use proxy metrics, while offline evaluation should use reference metrics.

### 1. Technical Deterministic Validation

This category should be the default first line of defense.

These checks are usually rule-based, auditable, and stable.

They should run on every document before any model-heavy validation is used.

| Deterministic area | Typical checks | Why it matters | Offline reference metrics | Production proxy metrics | Example gate logic | Typical action |
| --- | --- | --- | --- | --- | --- | --- |
| OCR and parser confidence | low OCR confidence, suspicious substitution density, too many unknown characters, abnormal page quality, weak block-level confidence | Fast early risk signal | CER, WER, token F1 | average OCR confidence, low-confidence token ratio, unknown-character ratio | warn if mean confidence is below class baseline; quarantine if low-confidence token ratio exceeds tolerance | warn, repair, quarantine |
| Structural and layout validation | reading order sanity, heading hierarchy consistency, page sequence consistency, plausible block boundaries, stable section ordering | Catches layout failures before text is trusted | pairwise order accuracy, inversion rate, heading hierarchy accuracy | bbox monotonicity violations, column-switch anomaly count, header-footer intrusion rate, orphan block ratio | quarantine if multiple structure proxies fail together; warn on mild hierarchy anomalies | warn, repair, quarantine |
| Table structural validation | row and column consistency, header-body separation, stable column count, merged-cell plausibility, header alignment, monotonic rows, geometric plausibility | High-impact table failures are usually structural | table cell F1, row grouping accuracy, column grouping accuracy, header alignment accuracy | column-count variance, header-body alignment score, row-order anomaly count, cell-overlap ratio | quarantine if structure proxies fall below minimum trust threshold | repair, quarantine |
| Deterministic semantic validation | dates parse as dates, identifiers match expected formats, enum values are valid, totals reconcile, duplicates appear only where allowed | Catches plausible-looking but wrong extraction | field extraction F1, typed-value accuracy | parse success rate for dates or ids, duplicate-key ratio, enum validity rate | warn if parse success falls below class baseline; quarantine on critical field failure | warn, repair, quarantine |
| Table semantic validation | stable column types, valid dates/currencies/percentages/ids, plausible ranges, expected enums, count or total consistency | Table content can be locally coherent or obviously broken | typed-cell accuracy, key-field extraction accuracy | column-type purity, numeric-range violation count, total-reconciliation error | quarantine if key columns show low type purity or totals diverge materially | repair, quarantine |
| Metadata and control-field validation | metadata completeness, source version consistency, ACL field presence | Prevents downstream filtering and governance failures | field accuracy, schema conformance accuracy | required-field completeness rate, ACL completeness, source-version consistency | quarantine or fail if mandatory fields are missing or control state is inconsistent | fail, quarantine |

---

#### 1.1 OCR and Parser Confidence Checks

Useful signals:

- low overall OCR confidence
- suspicious character substitution density
- too many unknown characters
- abnormal page-level quality
- weak extractor confidence on key blocks

Limitations:

- high OCR confidence does not guarantee correct structure
- tables can be wrong even when token confidence is acceptable

#### 1.2 Structural and Layout Validation

This is often the highest-value validation layer.

Checks may include:

- reading order sanity
- heading hierarchy consistency
- page sequence consistency
- plausible block boundaries
- stable section ordering

Table-specific structural checks belong here, not in a separate validation bucket.

Examples:

- table row and column consistency
- header and body separation
- stable column count across body rows
- plausible merged-cell behavior
- header alignment with body columns
- monotonic row ordering
- non-chaotic blank-cell pattern
- geometric plausibility of cell boundaries

This layer is especially important for layout-heavy documents.

#### 1.3 Deterministic Semantic Validation

Checks whether extracted content makes sense in its local structure.

Examples:

- dates parse as dates
- identifiers match expected formats
- enum-like values match known categories
- totals approximately reconcile when that is expected
- duplicated keys appear only where valid

Table-specific semantic checks also belong here.

Examples:

- currency columns look like currency columns
- stable column types
- valid dates, currencies, percentages, and identifiers
- plausible value ranges
- expected enums where applicable
- approximate consistency of totals or counts when relevant

- metadata completeness checks
- source version consistency checks
- ACL field presence checks

This often catches extraction errors that still look superficially plausible.

### 2. Technical Model-Based Validation

This category is used when deterministic checks are not enough.

It is useful for messy layouts, subtle semantic mismatches, and ambiguity that is hard to encode as rules.

These checks may use LLMs or smaller task-specific models, but they should remain bounded and auditable.

| Model-based area | Typical uses | Guardrail | Offline reference metrics | Production proxy metrics | Example gate logic | Typical action |
| --- | --- | --- | --- | --- | --- | --- |
| Semantic plausibility review | semantic comparison of aligned sections, content plausibility beyond pattern matching | Use only after deterministic checks | agreement with human review, semantic defect detection precision and recall | model consistency score, contradiction score, evidence coverage score | use as support signal only when confidence exceeds calibrated floor; do not hard-gate alone | warn, route to repair |
| Structural ambiguity resolution | classify ambiguous structural blocks, interpret messy table headers | Do not let the model silently redefine structure without trace | block classification accuracy, header interpretation accuracy | header interpretation confidence, block classification confidence | use only when deterministic checks are inconclusive and confidence is high | repair suggestion, manual review |
| Repair suggestion support | low-confidence repair suggestions, likely OCR corruption hints | Suggestions must be re-validated deterministically | repair success rate after re-validation | repair confidence, predicted corruption severity | never publish from this alone; require deterministic re-validation after repair | repair then re-validate |

---

Typical uses:

- semantic comparison of aligned sections
- content plausibility checks that go beyond pattern matching
- low-confidence repair suggestions
- classification of ambiguous structural blocks

Important rule:

- model-based validation should support technical validation, not replace it

Examples:

- LLM-based section consistency review
- model-based table header interpretation when header structure is messy
- semantic comparison between extracted summary and underlying block content
- model-assisted detection of likely OCR corruption patterns that deterministic rules missed

### 3. Comparative Consistency Validation

This category compares independent representations of the same content.

It is often stronger than trusting one extractor's internal confidence.

This category can combine deterministic and model-based checks.

| Comparative area | What is compared | Typical signals | Offline reference metrics | Production proxy metrics | Example gate logic | Typical action |
| --- | --- | --- | --- | --- | --- | --- |
| Cross-extractor validation | multiple OCR or parser outputs for the same source | structure mismatch, table shape mismatch, reading-order mismatch, key-field disagreement | best-extractor agreement with gold, disagreement precision for defect detection | extractor agreement rate, structure edit distance, key-field disagreement count | warn if disagreement exceeds class baseline; quarantine if key fields disagree materially | warn, repair, quarantine |
| Cross-language consistency validation | parallel language versions of the same document | section mismatch, table-shape mismatch, key-field mismatch, coverage mismatch, semantic mismatch | aligned-field match rate, section match accuracy, bilingual table field accuracy | section alignment rate, normalized key-field match rate, coverage gap count | warn on small drift; quarantine when key sections or key numeric fields diverge materially | warn, repair, quarantine |
| Comparative table validation | tables across extractor outputs or bilingual versions | same approximate dimensions, same key values, same row coverage, same field mapping | bilingual key-field accuracy, table alignment accuracy | table-shape similarity, row-coverage overlap, key-value match rate | quarantine if table-shape similarity or key-value match rate falls below minimum trust threshold | repair, quarantine |

---

#### 3.1 Cross-Extractor Validation

When multiple OCR or parsing methods are available, disagreement is a useful signal.

Checks may include:

- major structure mismatch between extractors
- table shape mismatch
- different reading order
- different field extraction for key attributes

Design principle:

> Independent disagreement is often more informative than one model's self-confidence.

#### 3.2 Cross-Language Consistency Validation

When documents exist in parallel language versions, cross-language agreement can be a very strong validation signal.

This is especially useful for bilingual corpora where the same document exists in two maintained language versions.

Checks may include:

- same document family or pair id
- same major section structure
- same table count and approximate shapes
- same normalized key fields such as dates, amounts, percentages, or codes
- semantic consistency of aligned sections
- coverage consistency so one version is not missing a section, table, or note

Table validation should also use this category when bilingual versions exist.

Examples:

- same approximate table dimensions
- same key numeric or coded values
- same row coverage
- same major field mapping

Important caution:

- mismatch does not automatically mean one side is correct and the other side is wrong
- mismatch may indicate OCR failure, layout failure, translation drift, version drift, or source inconsistency

Cross-language consistency should therefore be used as:

- a validation signal
- a repair hint
- a trust-scoring input

not as blind overwrite logic

### 4. Business-Specific Validation

For high-value document classes, domain-specific checks are often worth the effort.

| Business-specific area | Typical checks | Example document classes | Offline reference metrics | Production proxy metrics | Example gate logic | Typical action |
| --- | --- | --- | --- | --- | --- | --- |
| Required field presence | expected fields are present | policy tables, forms, contracts | required-field extraction accuracy | required-field hit rate | quarantine if critical fields are missing | quarantine |
| Domain value validation | known codes, worker types, product ids, region sets | fee schedules, eligibility matrices, catalogs | domain-field accuracy | valid-domain-value ratio, unknown-code count | warn on minor unknown values; quarantine on critical code mismatch | warn, quarantine |
| Numerical reconciliation | totals, rates, counts, limits are internally consistent | invoices, rate cards, finance tables | reconciliation accuracy on gold set | absolute reconciliation error, percentage reconciliation error | quarantine when error exceeds domain tolerance | repair, quarantine |
| Regulatory or policy structure validation | expected section presence or clause layout | legal docs, policies, compliance documents | mandatory-clause detection accuracy | expected-section coverage, mandatory-clause presence | quarantine if mandatory sections or clauses are absent | quarantine |

---

### Validation Decision Policy

A simple implementation pattern is to maintain separate scores or flags per category rather than one opaque global score.

The production gate should use proxy metrics, not offline reference metrics.

Offline reference metrics are for:

- selecting OCR or parser models
- selecting repair methods
- calibrating thresholds
- deciding which proxy metrics are trustworthy enough to gate on

| Category | Example policy |
| --- | --- |
| Technical deterministic | hard gate for critical failures |
| Technical model-based | supporting signal only |
| Comparative consistency | strong gate when independent views disagree materially |
| Business-specific | hard gate for high-risk document classes |

Practical decision rules:

| Condition | Recommended decision |
| --- | --- |
| critical metadata or ACL failure | `fail` or `quarantine` |
| severe structural failure in key tables or reading order | `quarantine` |
| deterministic checks mostly pass but comparative drift is moderate | `pass_with_warning` or `repair_and_pass` |
| model-based validator suspects corruption but deterministic checks are clean | `warn` and queue for sampling, not immediate quarantine |
| repair succeeds and deterministic re-validation passes | `repair_and_pass` |

### Post-Production Monitoring

Some failures will still escape production gates.

The system should therefore monitor published content using:

| Monitoring method | Purpose |
| --- | --- |
| sampled manual audits | catch hidden quality failures |
| downstream retrieval or answer failure review | trace missed defects back to ingestion |
| drift dashboards by source, language, or extractor | detect quality regressions over time |
| periodic re-evaluation on gold sets | detect whether model or parser upgrades helped or harmed |

This closes the loop between offline evaluation, online gating, and production feedback.

Business-specific validation should remain selective and document-type-aware.

## Repair Strategy

Misaligned tables are one of the highest-impact ingestion failures because the output often looks plausible while being structurally wrong.

Common failure patterns:

- rows merged incorrectly
- columns shifted by one cell
- headers attached to wrong columns
- multi-line cells split into extra rows
- merged cells flattened incorrectly
- table values extracted as free text with lost cell boundaries

### Recommended Repair Strategy

```text
Suspicious table
-> re-run extraction differently
-> re-check structure
-> re-check semantics
-> compare with alternate extractor or paired language version
-> pass, repair and pass, or quarantine
```

| Repair method | When to use | Limitation |
| --- | --- | --- |
| deskew image and rerun OCR | page image is skewed or visually noisy | may not fix logical table structure |
| crop and rerun table extraction | table region is known but full-page extraction is poor | depends on good region detection |
| use a table-specialized extractor | generic OCR preserved text but lost cell structure | adds tool complexity |
| use geometry-aware row or column reconstruction | bounding boxes exist but row or column grouping is weak | still needs re-validation |
| use stronger paired-language extraction as a repair hint | bilingual version is structurally cleaner | should guide repair, not overwrite blindly |

Important rule:

- do not perform speculative semantic repair when structure remains uncertain

## Common Failure Modes and Responses

| Failure mode | Typical symptoms | Primary response |
| --- | --- | --- |
| Misaligned tables | wrong row or column mapping; table looks readable but answers are wrong | structural validation; semantic validation; alternate extraction; cross-language comparison; quarantine if unresolved |
| Small OCR typos | ids, names, policy numbers, or codes are slightly wrong | keep source and normalized variants; apply safe normalization for known patterns; compare against expected identifier formats; use fuzzy recovery cautiously for validation |
| Broken reading order | multi-column text interleaves; headers or footers mix into body text | layout-aware parsing; reading-order validation; document-type-specific heuristics |
| Lost section hierarchy | text is locally correct but globally ambiguous | preserve heading levels during reconstruction; validate section ordering and nesting; compare against paired-language structure where available |
| Missing or wrong metadata | source version, language, or ACL fields are missing or inconsistent | required metadata checks; explicit unknown state rather than fake defaults; quarantine when mandatory fields are absent |
| Duplicate or stale artifacts | old versions appear alongside new versions; deletes are not reflected in staging corpus | strict source versioning; tombstone handling; pre-publish consistency checks |
| Overaggressive normalization | semantically meaningful formatting is lost | preserve raw representation alongside normalized form; use conservative normalization policies |

## Publish and Quarantine Policy

Validation should produce explicit decision artifacts.

| Artifact | Purpose |
| --- | --- |
| `quality_score` | overall quality signal for downstream trust decisions |
| `risk_flags` | explicit record of detected issues |
| `repair_attempted` | indicates whether any repair flow was used |
| `trust_level` | compact trust summary for downstream systems |
| `publish_decision` | final gate decision |

| Publish decision | Meaning |
| --- | --- |
| `pass` | trusted for downstream processing |
| `pass_with_warning` | usable but marked with known limitations |
| `repair_and_pass` | usable after repair and re-validation |
| `quarantine` | blocked from downstream use pending review or reprocessing |
| `fail` | unusable extraction outcome |

Only trusted outputs should move downstream by default.

Quarantined outputs should remain inspectable for debugging and manual review.

## Downstream Contract

The output of this layer should be a validated canonical document that downstream systems can depend on.

Downstream consumers should not need to guess:

| Downstream question | Must be answered by this layer |
| --- | --- |
| which extractor produced the content | yes |
| whether the structure is trusted | yes |
| whether a repair was attempted | yes |
| whether the document passed bilingual consistency checks | yes |
| whether the content is quarantined | yes |

| Downstream output field | Purpose |
| --- | --- |
| canonical document content | validated content for downstream use |
| source lineage | traceability back to source artifact |
| validation status | publish-state summary |
| trust score or trust level | downstream confidence input |
| risk flags | explicit known issues |
| repair history | auditability of repair flow |

## Minimal Serious Baseline

For a practical baseline, this layer should at least provide:

| Baseline capability | Why it matters |
| --- | --- |
| source id, version, and ACL preservation | preserves traceability and governance |
| layout-aware parsing or OCR | avoids flattening structure too early |
| structure reconstruction before chunking | prevents downstream chunking on corrupted layout |
| unified canonical representation across extractors | gives validation one stable interface |
| structural and semantic validation | catches high-risk extraction failures early |
| table-specific validation | tables are high-impact and structurally fragile |
| cross-language consistency checks when paired documents exist | provides strong independent validation |
| quarantine for low-trust documents | blocks bad content from becoming downstream truth |
| explicit publish decisions and traceability | makes system behavior inspectable and governable |

## Tooling Options

Keep this section short and practical.

| Use case | Recommended option | Why |
| --- | --- | --- |
| smallest strong open-source OCR baseline | PaddleOCR | practical multilingual OCR, good performance, relatively lightweight |
| strongest open-source document parsing and extraction stack | MinerU | strong open-source performance for document understanding and structured extraction |
| managed commercial fallback | Azure Document Intelligence | strong OCR, layout, and table extraction with enterprise support |

Practical recommendation:

- start with PaddleOCR when you want a lightweight open-source OCR base
- use MinerU when document understanding quality matters more than minimal footprint
- use a managed commercial service only when support, compliance, or document complexity justifies it

## Final Note

The goal of this layer is not to guarantee perfect OCR or perfect parsing.

The goal is to prevent low-trust extracted content from quietly becoming downstream truth.

That is why ingestion and validation should be treated as a first-class independent subsystem rather than a preprocessing detail.
