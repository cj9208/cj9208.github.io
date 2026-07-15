---
title: "Retrieval Layer"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "The retrieval layer is the online evidence-finding subsystem of RAG."
summary: "The retrieval layer is the online evidence-finding subsystem of RAG."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"

slug: "CH03_03_Retrieval-Layer"
---
## Purpose

The retrieval layer is the online evidence-finding subsystem of RAG.

Its job is to turn a well-shaped user request into a grounded context set that downstream answering can trust.

It does this by:

1. representing the request in retrieval-friendly form
2. narrowing or expanding the search space as needed
3. retrieving candidate evidence
4. reranking and assembling the best context

The key idea is simple:

> Clear user intention is necessary, but it does not by itself locate the right evidence in the corpus.

## Scope

This document covers:

```text
Retrieval
-> Query shaping
-> Metadata and security filtering
-> Candidate retrieval
-> Fusion and reranking
-> Context assembly
```

This document does not cover:

| Out of scope | Why |
| --- | --- |
| ingestion and validation | belongs to `CH03_01_Ingestion-Validation-Layer.md` |
| enrichment, chunking, and indexing | belongs to `CH03_02_Enrichment-Chunking-Indexing-Layer.md` |
| grounded generation | belongs to `CH03_04_Grounded-Answering-Layer.md` |

## Relationship to Other Layers

The upstream dependency is the intention recognition and orchestration path.

The retrieval layer expects:

- normalized wording
- clarified target entity or scope when needed
- confidence and ambiguity signals
- permission context
- access to published retrieval indexes

The downstream dependency is grounded answering.

The retrieval layer should output:

- ranked evidence candidates
- citation-ready context
- retrieval scores and rationale signals
- insufficiency or ambiguity signals when evidence is weak

## Design Goals

1. find the right evidence with high recall and precision
2. support both exact lookup and semantic retrieval
3. keep retrieval explainable and stage-aware
4. use metadata and permissions safely
5. preserve traceability from retrieved chunk back to source
6. support abstention when evidence quality is weak

## Core Principles

### 1. Retrieval Is a Pipeline, Not a Single Search Call

High-quality retrieval usually requires several stages:

- query shaping
- candidate retrieval
- fusion
- reranking
- context assembly

### 2. Exact Match and Semantic Match Are Complementary

Sparse retrieval is good at exact names, policy ids, codes, and keyword-heavy lookup.

Dense retrieval is good at paraphrase, semantic similarity, and fuzzier concept recall.

Use both when possible.

### 3. Metadata Is a First-Class Signal

Metadata can dramatically improve precision, but bad filters can destroy recall.

### 4. Retrieval Should Be Failure-Driven

Each retrieval transformation should exist to correct a known failure mode, not to make the pipeline look sophisticated.

## Retrieval Architecture

| Step | Responsibility | Typical outputs |
| --- | --- | --- |
| Query shaping | make the request retrievable without changing intent | retrieval query, sub-queries, strategy hints |
| Metadata and security filtering | narrow the space safely | filter set, filter confidence, permission-trimmed scope |
| Candidate retrieval | retrieve sparse, dense, or hybrid candidates | top-k candidates with raw scores |
| Fusion and reranking | combine and reorder candidates by final usefulness | reduced ranked set with relevance signals |
| Context assembly | build the final grounded context window | packed evidence set with citation anchors |

---

## Control and Governance in This Layer

This layer is one of the main enforcement points for data access control because it touches retrievable content directly.

| Control concern | How it applies in this layer |
| --- | --- |
| permission-aware filtering | narrow retrieval to authorized scope before candidates are returned |
| retrieval-time trimming | prevent unauthorized chunks from entering the candidate set |
| secure expansion | re-check permissions when parent, neighbor, or section expansion adds more context |
| score and filter auditability | record what filters were applied and why |
| insufficiency signaling | prefer weak-evidence or no-evidence outcomes over over-broad retrieval |

Important principle:

> Permission should be interpreted early, enforced during retrieval, and re-checked whenever additional context is pulled in.

## 1. Query Shaping

The user query should usually be conditioned before search.

Even when user intention is already clear, retrieval can still fail because the search expression does not match how the corpus stores knowledge.

Typical causes include:

1. the query uses different language than the documents
2. the query is too narrow and misses the right level of abstraction
3. the query is too broad and fails to emphasize key constraints
4. the question contains multiple constraints or subproblems that need structure
5. the answer is distributed across neighboring chunks or multiple documents
6. the corpus stores the truth in a different representation than the user question

The job of query shaping is not to reinterpret the user's intent, but to represent that intent in a form the retrieval system can use effectively.

### Retrieval Transformation Framework

To keep retrieval-side techniques systematic rather than ad hoc, organize them by the failure they are trying to correct.

Recommended flow:

```text
Clear user intention
-> Represent the intent for retrieval
-> Choose retrieval scope
-> Choose retrieval operators
-> Expand or refine if first-pass evidence is weak
-> Rank and assemble evidence
```

### Technique Categories

| Category | Goal | Typical techniques | Failure addressed |
| --- | --- | --- | --- |
| Representation alignment | make the query look more like the corpus | query rewrite, alias expansion, entity normalization, field-aware query construction | vocabulary mismatch |
| Scope control | search at the right abstraction level | step-back query, constraint extraction, temporal scoping | query too narrow or too broad |
| Query multiplicity | search with more than one valid formulation | multi-query retrieval, decomposition, hypothetical answer generation | single phrasing misses evidence |
| Retrieval operator selection | choose the right search operators | metadata filtering, sparse retrieval, dense retrieval, hybrid retrieval | wrong operator for task or corpus |
| Evidence expansion | recover surrounding context | parent-child expansion, neighbor expansion, section expansion | right neighborhood but incomplete answer |
| Second-pass refinement | use first-pass evidence to refine retrieval | iterative retrieval, retrieve-then-refine | first pass is on-topic but not answer-complete |
| Ranking and selection | choose the best evidence from candidates | cross-encoder reranking, metadata-aware rerank, diversity-aware selection | correct evidence exists but is not ranked high enough |

### Minimal Decision Policy

```text
If vocabulary mismatch is likely:
  use rewrite, alias expansion, or entity normalization

If the query is too specific:
  add a step-back query

If the query is under-constrained:
  extract constraints and generate metadata filters

If the question has multiple parts:
  decompose it or use multi-query retrieval

If the corpus contains both exact identifiers and semantic prose:
  use hybrid retrieval

If the top result is relevant but incomplete:
  expand to parent, neighbor, or section context

If first-pass retrieval is on topic but still weak:
  run second-pass refinement

Then rerank and assemble context
```

The core moves are:

1. rephrase the query
2. constrain or broaden the search scope
3. expand and rerank the evidence

## 2. Metadata and Security Filtering

Metadata filters deserve explicit treatment because they strongly influence precision and recall.

| Filter type | Example |
| --- | --- |
| document type | policy |
| business unit | finance |
| time window | effective date range |
| source system | HR wiki |
| region | APAC |
| permission scope | access label within user permissions |

Rules:

- apply hard filters only when confidence is high enough
- use soft preference or rerank signals when confidence is moderate
- keep security trimming mandatory regardless of other confidence signals
- record why a filter was applied

## 3. Candidate Retrieval

This stage retrieves an initial candidate set.

Recommended approach:

- run sparse retrieval for exact or keyword-rich matching
- run dense retrieval for semantic matching
- optionally retrieve from parent and child indexes separately
- merge candidate sets before reranking

Typical outputs:

- top-k sparse candidates
- top-k dense candidates
- retrieval scores by method
- candidate metadata

## 4. Fusion and Reranking

Candidate retrieval should usually be followed by ranking refinement.

Recommended sequence:

1. combine sparse and dense candidates using a fusion method such as reciprocal rank fusion
2. deduplicate overlapping chunks or same-source near-duplicates
3. rerank the reduced set with a cross-encoder or stronger relevance model
4. preserve score explanations and source lineage

Why reranking matters:

- initial retrieval is optimized for recall
- reranking is optimized for final relevance ordering

## 5. Context Assembly

Retrieval is not finished when the best chunk is found.

The system still needs to assemble the final grounded context window.

| Function | Purpose |
| --- | --- |
| choose how many items to include | balance token cost and evidence quality |
| attach parent or neighbor context | recover missing scope or exceptions |
| merge overlaps | avoid redundant evidence |
| preserve citation anchors | support grounded answering |
| order final context | improve reasoning quality |

Possible packing strategies:

- top-ranked only
- top-ranked plus parent context
- answer-focused packing by sub-question
- diversity-aware packing across sources

Control note:

- context assembly should re-check access scope before sending context downstream to generation

## Tooling Options

Keep this section short and practical.

| Use case | Recommended option | Why |
| --- | --- | --- |
| best practical open-source lexical retrieval | Elasticsearch or OpenSearch | mature BM25, metadata filters, and operational stability |
| best practical open-source vector retrieval | Qdrant | strong semantic retrieval with metadata filtering |
| strongest open-source unified hybrid retrieval | Vespa | strong hybrid retrieval and ranking control in one system |
| best practical open-source reranker | BGE reranker family | strong open reranking quality with wide community use |
| easiest commercial rerank fallback | Cohere Rerank | simple API and solid rerank quality |

Practical recommendation:

- use Elasticsearch or OpenSearch plus Qdrant as the practical default open-source stack
- use Vespa when you want a stronger unified retrieval platform and can accept higher complexity
- add reranking after baseline sparse and dense retrieval are already working well

## Final Note

The retrieval layer should be treated as an evidence-finding system, not a thin wrapper around vector search.

When query shaping, filtering, retrieval, reranking, and context assembly are designed well, grounded answering becomes much more reliable.
