---
title: "Request Orchestration Layer"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-07-15T09:00:00+08:00
draft: false

description: "The request orchestration layer is the shared control layer for a company-wide agent system."
summary: "The request orchestration layer is the shared control layer for a company-wide agent system."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"

slug: "CH02_Request-Orchestration-Layer"
---
## Purpose

The request orchestration layer is the shared control layer for a company-wide agent system.

It extends the intention recognition layer into a broader runtime that can:

1. understand user requests
2. classify task type and domain
3. resolve ambiguity
4. choose the right capability
5. adaptively load the relevant tool surface
6. govern execution using company identity and policy systems
7. control cost, risk, and latency
8. escalate safely when automation is weak

In this design, RAG is one capability among several, not the default execution path.

This document describes the main architecture, execution model, operating model, and the remaining open questions.

## Why This Layer Exists

If the company wants a system of agents rather than one isolated feature, the core problem is not only question answering.

The core problem is governed request execution.

Without a shared orchestration layer, each agent tends to implement its own:

- request normalization
- routing logic
- tool selection
- confidence policy
- clarification behavior
- fallback rules
- permission checks
- handoff format

That creates duplicated logic, inconsistent behavior, and weak governance.

The request orchestration layer standardizes those behaviors across agents.

## Relationship to the Intention Recognition Layer

The intention recognition layer remains valid, but it becomes the front half of a broader orchestration runtime.

Previous shape:

```text
User request
-> Intention recognition
-> RAG
```

Extended shape:

```text
User request
-> Request understanding
-> Domain and task framing
-> Capability selection
-> Adaptive schema loading
-> Governed execution
-> Validation and escalation
```

What stays the same:

- deterministic normalization
- lightweight model interpretation
- confidence-aware routing
- clarification-first disambiguation
- bounded retries
- graceful escalation

What extends:

- execution is routed through domain-scoped subsystems
- tool schemas are loaded adaptively by capability
- execution is governed by the harness rather than delegated to the model

## Core Principles

### 1. Deterministic First

Use deterministic methods whenever possible for low-cost, stable, and auditable resolution.

Examples:

- typo repair
- alias mapping
- short-name recovery
- canonical entity resolution
- metadata lookups
- rules and filters

### 2. LLM Reasoning as a Governed Component

Use model reasoning for interpretation, framing, decomposition, and soft disambiguation, but do not treat the model as the controller.

The model is a component inside a harness.

### 3. Clarification Before Expensive Execution

If the request is materially ambiguous, resolve that ambiguity before spending significant retrieval or reasoning budget.

### 4. Capability-Gated Execution

Do not expose all tools to the model at once.

First decide what capability family is needed, then load only the relevant tool schemas.

### 5. Orchestration Owns Sequencing

Tools should be simple executors.

Tools do not call each other. Only the orchestration layer plans and sequences tool calls.

This applies to both read and write operations.

Read access is also treated as tool execution. The model never directly reads protected content or performs actions outside the harness.

### 6. Bounded Autonomy

The system should not loop indefinitely.

Retries, clarifications, model escalations, tool calls, and retrieval breadth should all be bounded.

### 7. Stage-Aware User Expectation Management

Because the orchestration layer knows which execution path is being taken, it should also support path-aware user feedback.

Different paths should produce different user expectations:

- simple lookup paths should feel nearly immediate
- retrieval paths may show a short wait hint
- complex multi-step paths should show visible progress or workflow steps
- human escalation paths should clearly communicate handoff status

### 8. Graceful Human Escalation

When automation cannot safely converge, hand off with structured context rather than producing a low-confidence answer.

## Domain-Scoped Architecture

Even if many agent entry points appear to be "just QA" at the surface, the system should still be split by business functionality or domain.

Examples:

- HR
- customer support
- sales
- finance
- legal
- internal engineering

This keeps each subsystem smaller, simpler, and more maintainable.

Benefits:

1. smaller search space
2. simpler prompts and tool bundles
3. clearer ownership by domain teams
4. less cross-domain ambiguity
5. easier governance and permission control
6. safer and cheaper retrieval and execution

Design principle:

> Centralize orchestration patterns, decentralize domain knowledge and capability bundles.

## Architecture

### Layer Responsibilities

The request orchestration layer owns the following responsibilities:

1. preserve and normalize the request
2. infer task type and domain
3. resolve target entities and constraints
4. assess ambiguity and confidence
5. choose the best capability family
6. load the smallest relevant tool surface
7. enforce governed execution
8. validate execution results
9. handle fallback, retry, and escalation
10. produce structured logs and handoff artifacts

### End-to-End Flow

```text
User request
-> Input capture
-> Deterministic conditioning
-> Intent and task framing
-> Ambiguity evaluation
-> Domain routing
-> Clarification if needed
-> Capability selection
-> Adaptive schema loading
-> Governed execution
-> Validation
-> Fallback or escalation
-> Logging and handoff
```

## Stage-by-Stage Design

| Stage | Main purpose | Typical inputs | Typical outputs | Key decisions or rules |
| --- | --- | --- | --- | --- |
| 1. Input capture | preserve original wording and context | current user message, chat history, session metadata | original query, contextual request envelope | always preserve untouched user input for traceability and handoff |
| 2. Deterministic conditioning | perform cheap, auditable cleanup before model reasoning | original query, metadata, aliases, lookup rules | normalized query, deterministic candidates, rule hits, score signals | keep transforms low-risk and traceable |
| 3. Intent and task framing | frame what kind of task this is and what the user is asking for | normalized query, session context, deterministic signals | framed request object, task type, candidate domain, target guess, requested fields, confidence, ambiguity flags | model shapes the request but should not silently replace user intent |
| 4. Ambiguity evaluation | decide whether it is safe to proceed | deterministic match strength, model confidence, score gaps, required constraints | proceed, clarify, escalate to stronger model, or human handoff | prefer deterministic signals when strong; clarify if deterministic and model outputs conflict materially |
| 5. Domain routing | choose the domain-scoped subsystem | framed request, task type, candidate domains, scope policy | selected domain, candidate domains with scores, routing confidence | if domain confidence is low, ask a short routing clarification before loading domain tools |
| 6. Clarification gate | resolve material ambiguity before capability execution | ambiguity flags, candidate interpretations, prior failed clarifications | clarification question or resolved request | ask short, specific questions; keep retries bounded; prefer clarification over confident garbage output |
| 7. Capability selection | choose the best execution family in the selected domain | task type, domain, confidence, risk, latency target, cost target, permissions | selected capability, optional fallback capability, routing rationale | candidate capability families include resolution, structured lookup, unstructured retrieval, reasoning, action, and escalation |
| 8. Adaptive schema loading | expose only the relevant tool surface | selected domain, selected capability, policy constraints | tool bundle loaded for the chosen path | load the smallest relevant schema surface; keep early reasoning stages schema-light |
| 8A. Execution graph planning | allow the model to propose a tool graph while the harness retains control | selected tools, request plan, dependency hints | proposed tool graph, dependency plan, parallelization hints | the model may describe a tool graph; the harness owns scheduling, permission checks, dependency enforcement, and partial-result policy |
| 9. Governed execution | execute only after identity, permission, and policy checks | tool proposal, user identity, arguments, permissions, risk policy | execution result, policy decision, risk decision | the model suggests, the harness decides, the executor acts; both read and write tools are governed |
| 10. Validation | verify that the result satisfies user need and quality policy | execution result, request intent, confidence signals, policy checks | accept result, retry, clarify, or escalate | check relevance, completeness, grounding, consistency, confidence sufficiency, and policy compliance |
| 11. Fallback and escalation | recover gracefully when the chosen path fails or remains weak | validation outcome, retry budget, fallback policy | clarification retry, stronger model, alternate capability, or human handoff | cap retries, model escalations, retrieval breadth, tool calls, and end-to-end latency |
| 12. Logging and handoff | produce durable traces and escalation artifacts | full execution path, decisions, tool usage, outcomes | structured logs, replay artifacts, human handoff packet | logs should support audit, replay, monitoring, attribution, and postmortem analysis |

Representative structured log fields can be grouped as follows:

| Category | Representative fields |
| --- | --- |
| request identity | `request_id`, `session_id`, `user_id` |
| request content | `original_query`, `normalized_query` |
| routing and framing | `candidate_domains`, `selected_domain`, `task_type`, `selected_capability` |
| interpretation signals | `deterministic_signals`, `model_output`, `confidence_breakdown` |
| tool execution | `tool_bundle_loaded`, `tool_call_proposal`, `dependency_status` |
| governance and policy | `policy_decision`, `risk_level`, `redaction_state` |
| result and fallback | `execution_result`, `fallback_reason`, `final_outcome`, `upstream_dependency_failures` |
| timing and versioning | `timestamp_start`, `timestamp_end`, `duration_ms`, `tool_schema_version`, `capability_version`, `domain_subsystem_version`, `queue_or_scheduler_state` |

## Capability Model

Capabilities should be treated as governed products, not ad hoc tool collections.

Some capabilities are global:

- clarification generation
- human handoff building
- generic reasoning utilities

Some capabilities are domain-scoped:

- HR policy lookup
- customer case retrieval
- finance workflow actions
- legal document retrieval

Each capability has:

1. a purpose
2. a usage boundary
3. an input contract
4. a tool schema bundle
5. an output contract
6. confidence and validation signals
7. fallback paths
8. ownership
9. domain scope

### Capability Families

| Capability family | Purpose | Typical tools |
| --- | --- | --- |
| Resolution | resolve entities, aliases, shorthand, and canonical naming | alias matcher, typo recovery, canonical entity resolver |
| Structured lookup | answer exact questions from structured data sources | metadata search, SQL or service query, record lookup APIs |
| Unstructured retrieval | answer questions that require document or long-text evidence | summary retrieval, vector search, keyword retrieval, rerank, raw chunk fetch |
| Reasoning | perform decomposition, comparison, synthesis, or higher-cost interpretation | flash model, pro model, planner or synthesizer |
| Action and workflow execution | perform external actions or guided business operations | API clients, workflow runners, ticketing or case-management actions |
| Escalation | ask clarifying questions or hand off to a human | clarification generator, handoff packet builder, human-agent routing connector |

RAG belongs in the `Unstructured retrieval` family.

### Capability Catalog Template

```yaml
name: <capability_name>
display_name: <human_readable_name>
purpose: <what this capability does>
owner: <team_or_system_owner>
domain_scope: <global|hr|customer|finance|legal|engineering|...>
capability_version: <version>
schema_version: <version>
rollout_status: <draft|staging|active|deprecated>
change_reference: <ticket_or_change_id>

use_when:
  - <condition>

avoid_when:
  - <condition>

task_types_supported:
  - <task_type>

required_inputs:
  - <field_name>

optional_inputs:
  - <field_name>

preconditions:
  - <must_be_true_before_execution>

tool_schema_bundle:
  - <tool_schema_name>

loading_mode: <single_capability|primary_plus_fallback|staged_supervisor>

output_contract:
  required_fields:
    - <field_name>
  optional_fields:
    - <field_name>

confidence_signals:
  - <signal_name>

validation_rules:
  - <rule>

cost_profile: <low|medium|high>
latency_profile: <low|medium|high>
risk_profile: <low|medium|high>

fallbacks:
  - <fallback_capability_or_action>

human_escalation_required_when:
  - <condition>

notes:
  - <implementation_note>
```

Registry model:

- the orchestration layer looks up capability definitions from a registry
- each domain team owns and updates its own subsystem tools and schemas
- the orchestration layer should not own domain tool logic; it should only use the registry to request and load schemas
- every tool and capability should have an explicit owner recorded in the registry or schema metadata
- version and rollout metadata should also be recorded so regressions can be traced to specific changes

## Cross-Domain Handling Policy

Cross-domain requests are allowed when the query genuinely requires them.

Default policy:

1. single-domain by default
2. clarify if domain scope is ambiguous
3. allow multi-domain execution only for explicitly supported workflows

Additional rules:

- tools do not call each other
- only the orchestration layer can sequence cross-domain calls
- permission is checked by the harness for each call
- multi-domain execution may be sequential or parallel when dependencies allow
- if a prerequisite call fails, dependent calls should not run
- if one call fails, return the successful scoped information and clearly label the missing part
- if sources conflict, do not infer a conclusion; present the conflict and recommend human confirmation
- if ambiguity remains material, ask for clarification rather than infer

Example response style for partial success:

```text
We could retrieve the general policy information, but we could not verify your identity at this time.
General information:
...
For account-specific conclusions, please try again later or contact a human agent.
```

Example response style for conflicting sources:

```text
We found conflicting information:
- Source A says ...
- Source B says ...
We cannot provide a reliable conclusion from the available data.
Please confirm with the related human agent.
```

## Measurement and Reliability

The platform should be evaluated both offline and online.

### Offline Evaluation

Use golden datasets and controlled benchmarks for:

- routing quality
- tool selection precision
- schema generation precision
- answer quality
- cost reduction
- safety and policy correctness

### Online Monitoring

Reliability should be monitored over time.

If behavior drifts, engineers should investigate logs, failure patterns, and recent changes.

This monitoring should support both scheduled review and operational intervention when important distributions drift materially.

Useful online measures include:

- percentage of flash-model paths
- percentage of pro-model escalations
- percentage of human handoffs
- user satisfaction signals
- repeated user retries as a negative signal
- failure or rejection rates
- latency and cost trends over time

## Operational Ownership and Nightly Review

The architecture should support clear operational ownership.

Because the system is split by domain, capability, tool schema, and owner, failures and regressions can be attributed more precisely.

This makes it easier to answer:

- which tool is slow or failing
- which capability is degrading
- which domain subsystem is unstable
- which team should investigate

Design principle:

> Every tool and capability should have an explicit owner so performance, failures, and regressions can be attributed and reviewed automatically.

### Nightly Review Loop

The platform can run a nightly summary job that analyzes orchestration and tool activity across the day.

Example review dimensions:

| Level | Example Metrics |
|---|---|
| Tool | latency distribution, failure rate, timeout rate, bad schema rate |
| Capability | success rate, fallback rate, retry rate |
| Domain | volume, latency, handoff rate, top failure patterns |
| Orchestration | wrong-route signals, clarification rate, escalation rate |

Useful outputs:

- latency trends
- failed cases
- timeout clusters
- schema mismatch patterns
- unusual escalation spikes
- owner-routed issue summaries

Because owner information is recorded in the registry or tool schema metadata, summary results can be sent directly to the relevant team.

### Failure Classification

The nightly review should classify issues rather than treat all failures the same.

Useful categories:

- orchestration issue
- schema issue
- tool or backend issue
- permission or policy issue
- dependency outage
- user ambiguity cluster

This helps teams focus on the real source of degradation instead of routing all issues to one group.

Monitoring can be both:

- scheduled, such as nightly review summaries
- operational, where engineers inspect significant drift or abnormal distributions and step in when needed

## SLA and Latency UX

The orchestration layer should not only control latency internally. It should also help the product expose appropriate user expectations.

Because execution is modular, the system can estimate the rough shape of work before it finishes.

Examples:

- simple API or structured lookup -> near-immediate response
- RAG or retrieval-heavy path -> short wait hint such as "searching documents, may take about 2 seconds"
- complex multi-step path -> visible progress states or workflow steps
- human escalation path -> explicit handoff message

Why this matters:

1. better perceived performance
2. clearer user anticipation
3. less confusion when work takes longer
4. higher trust and satisfaction
5. better alignment between system behavior and user expectation

Suggested latency tiers:

| Tier | Typical Path | User-Facing Behavior |
|---|---|---|
| Fast | deterministic lookup, single API read | immediate or minimal loading state |
| Standard | normal retrieval, light clarification, bounded tool chain | short wait hint |
| Careful | multi-step reasoning, conflict resolution, higher-risk checks | progress steps or staged status |
| Escalation | unresolved ambiguity or blocked execution | explicit human handoff or retry guidance |

Latency policy should also be configurable by task, capability, or tool preferences.

Examples:

- internal tools may prefer throughput or performance over immediate latency and can be served through queue-based execution
- customer-support flows may prefer shorter first responses, even if the answer is partial
- retrieval-heavy capabilities may cap number of chunks or rerank depth differently depending on latency preference

Examples of configurable latency-related preferences:

- max retrieved chunks
- max rerank candidates
- max tool calls
- max model escalations
- queue-allowed or not
- partial-response preferred or not
- max wall-clock budget

Design principle:

> Modular orchestration makes latency visible and predictable. Because the system knows which path it is taking, it can provide appropriate progress cues and expected wait times for each class of work.

## Security and Governance Boundary

Security and permission enforcement belong to the harness and company policy systems, not to prompt-only behavior.

The same rule applies to both read access and write access:

- the model may propose a tool call
- the harness decides whether the call is allowed

This keeps permissions, risk rules, approvals, and content exposure controls in code and company systems rather than in prompts.

## Deferred Memory Scope

General long-term agent memory is not part of the current design.

Current scope:

- treat most requests as one-time interactions
- optionally resume a previous unresolved session
- retrieve the previous session and generate a summary for the next agent or human to continue

Out of scope for now:

- broad durable conversational memory
- automatic persistence of inferred facts across unrelated sessions

## Human Handoff Contract

When escalation is required, the handoff should include:

1. original user request
2. relevant conversation history
3. normalized query and framed interpretation
4. candidate meanings and scores
5. attempted capabilities and outcomes
6. ambiguity and confidence state
7. recommended next action

Resolved human cases should be recorded so the system can improve aliases, routing rules, prompts, and escalation policy over time.

## Remaining Open Design Questions

The overall architecture is now largely defined. The main remaining work is in operational detail rather than top-level structure.

### 1. Confidence Calibration

The design relies heavily on confidence-aware routing, so confidence still needs a more formal runtime decision policy.

It should likely combine:

- deterministic match strength
- model confidence
- retrieval agreement
- ambiguity signals
- execution outcome signals

The main open question is not whether confidence matters, but exactly how the harness should turn these signals into decisions such as:

- proceed
- clarify
- retry
- escalate
- reject tool execution

### 2. Failure Taxonomy

The platform should classify failures more explicitly so diagnosis and ownership are cleaner.

Examples:

- orchestration issue
- schema issue
- tool or backend issue
- permission or policy issue
- dependency outage
- user ambiguity cluster

This matters for online monitoring, nightly review, and owner-routed follow-up.

### 3. Testing Strategy

The orchestration layer needs more than prompt or answer-quality evaluation.

It likely needs:

- routing test cases
- ambiguity and clarification tests
- policy enforcement tests
- capability output contract tests
- schema loading regression tests
- high-risk action confirmation tests
- dependency-graph execution tests

These tests should cover both offline validation and production regression protection.

### 4. Operational Alert Thresholds

The design now includes online monitoring and nightly review, but it still needs explicit intervention thresholds.

Examples:

- how much latency drift is acceptable before investigation
- when timeout-rate changes become urgent
- when escalation or rejection spikes indicate a system issue
- when schema mismatch frequency suggests a bad rollout

Without alert thresholds, monitoring exists but responses may remain inconsistent.

### 5. Stateful Memory Boundaries

General long-term agent memory is intentionally out of scope for now.

However, once the platform resumes unresolved sessions more often, it will need explicit rules for:

- what session context persists
- what inferred facts may be reused
- how user corrections override prior assumptions
- what information may be stored durably

Without clear memory boundaries, later orchestration behavior can become inconsistent or unsafe.
