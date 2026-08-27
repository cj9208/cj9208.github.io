---
title: "Request Orchestration Layer"
date: 2026-07-15T09:00:00+08:00
lastmod: 2026-08-27T21:14:40+08:00
draft: true

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

It extends the intention recognition layer (`CH01`) into a broader runtime: the front half — request conditioning, interpretation, ambiguity evaluation, clarify-or-route — is inherited unchanged; this chapter owns the back half, where requests are routed to domains, matched to capabilities, executed under governance, validated, and handed off when automation cannot converge.

In this design, RAG is one capability among several, not the default execution path.

## Mental Model

Three constructs explain everything in this chapter:

```text
1. FLOW       the request lifecycle:
              inherited CH01 front half
              -> domain routing -> capability selection -> schema loading
              -> governed execution -> validation -> fallback / handoff
2. REGISTRY   capabilities as governed products with owners, contracts,
              tool bundles, and lifecycle metadata - looked up, never hardcoded
3. BOUNDARIES three hard controls around the flow:
              cross-domain policy, security/governance (model proposes,
              harness decides), and escalation budgets
```

And when the runtime itself must be designed in detail, its three aspects map one-to-one onto the subchapters:

| Aspect | Question | Subchapter |
| --- | --- | --- |
| State | what exists now? | `CH02_01_Runtime-Objects.md` |
| Transition | what can happen next? | `CH02_02_State-Machine-and-Control-Loop.md` |
| Policy | what should be allowed next? | `CH02_03_Confidence-Safety-and-Validation.md` |

`State`, `Transition`, `Policy` is also the smallest split that keeps the runtime readable: merging them makes the runtime dense, splitting them further fragments the design.

## Why A Shared Runtime Exists

If the company wants a system of agents rather than one isolated feature, the core problem is not question answering — it is governed request execution at scale.

Without a shared orchestration layer, each agent tends to implement its own:

- request normalization
- routing logic
- tool selection
- confidence policy
- clarification behavior
- fallback rules
- permission checks
- handoff format

That creates duplicated logic, inconsistent behavior, and weak governance. The request orchestration layer standardizes those behaviors once, across agents.

### From Intention Layer To Orchestration

The intention recognition layer remains valid; it becomes the front half of this runtime.

Previous shape:

```text
User request
-> Intention recognition
-> RAG
```

Extended shape:

```text
User request
-> Request understanding        (front half, inherited from CH01)
-> Domain and task framing      \
-> Capability selection          |
-> Adaptive schema loading       |  back half,
-> Governed execution            |  this chapter
-> Validation and escalation    /
```

What stays the same from `CH01`: deterministic normalization, lightweight model interpretation, confidence-aware routing, clarification-first disambiguation, escalation budgets, graceful handoff.

What extends: execution routes through domain-scoped subsystems, tool schemas load adaptively by capability, and execution is governed by the harness rather than delegated to the model.

Design principle:

> Centralize orchestration patterns; decentralize domain knowledge and capability bundles.

## Why Domains

Even if many agent entry points look like "just QA" at the surface, the system should still split by business functionality or domain — HR, customer support, sales, finance, legal, internal engineering.

Benefits:

1. smaller search space
2. simpler prompts and tool bundles
3. clearer ownership by domain teams
4. less cross-domain ambiguity
5. easier governance and permission control
6. safer and cheaper retrieval and execution

## The Flow

Twelve steps describe a request end to end. Steps 1–4 (input capture, deterministic conditioning, intent framing, ambiguity evaluation) and the clarification gate are inherited from `CH01_Intention-Recognition-Layer.md` unchanged; they appear in the table below only so the sequence stays readable in one place.

| Step | Main purpose | Key decisions or rules | Owned by |
| --- | --- | --- | --- |
| 1. Input capture | preserve original wording and context | always preserve untouched user input for traceability and handoff | CH01 front half |
| 2. Deterministic conditioning | cheap, auditable cleanup before model reasoning | transforms low-risk and traceable | CH01 front half |
| 3. Intent and task framing | frame task type, candidate domains, target guess, requested fields | model shapes the request, never silently replaces user intent | CH01 front half |
| 4. Ambiguity evaluation | decide whether it is safe to proceed | prefer strong deterministic signals; clarify on material conflict between rule and model outputs | CH01 front half |
| 5. Domain routing | choose the domain-scoped subsystem | if domain confidence is low, ask a short routing clarification before loading domain tools | this chapter |
| 6. Clarification gate | resolve material ambiguity before capability execution | short specific questions; bounded retries; clarification over confident garbage output | CH01 policy |
| 7. Capability selection | choose the best execution family in the selected domain | candidate families: resolution, structured lookup, unstructured retrieval, reasoning, action, escalation | this chapter |
| 8. Adaptive schema loading | expose only the relevant tool surface | smallest relevant schema surface; early reasoning stages stay schema-light | this chapter |
| 8A. Execution graph planning | let the model propose a tool graph while the harness keeps control | model may describe the graph; harness owns scheduling, permissions, dependency enforcement, partial-result policy | this chapter |
| 9. Governed execution | execute only after identity, permission, and policy checks | the model suggests, the harness decides, the executor acts; read tools are governed exactly like write tools | this chapter |
| 10. Validation | verify the result satisfies user need and quality policy | relevance, completeness, grounding, consistency, confidence sufficiency, policy compliance | this chapter |
| 11. Fallback and escalation | recover gracefully when the chosen path fails or stays weak | every recovery path spends an escalation budget: clarification retry, stronger model, alternate capability, human handoff | both halves |
| 12. Logging and handoff | produce durable traces and escalation artifacts | logs support audit, replay, monitoring, attribution, postmortems | this chapter |

The layer-level responsibility summary follows from the table: preserve and frame requests (front half), route and select capabilities, load minimal schema surfaces, enforce governed execution, validate results, and produce logs and handoffs.

Representative structured log fields:

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

These field groups are the runtime-facing preview of the durable objects defined in `CH02_01_Runtime-Objects.md`.

## The Capability Registry

Capabilities are governed products, not ad hoc tool collections.

Some are global — clarification generation, human handoff building, generic reasoning utilities. Some are domain-scoped — HR policy lookup, customer case retrieval, finance workflow actions, legal document retrieval.

Every capability declares nine things:

1. purpose
2. usage boundary (use_when / avoid_when)
3. input contract
4. tool schema bundle
5. output contract
6. confidence and validation signals
7. fallback paths
8. owner
9. domain scope

### Capability Families

| Capability family | Purpose | Typical tools |
| --- | --- | --- |
| Resolution | resolve entities, aliases, shorthand, canonical naming | alias matcher, typo recovery, canonical entity resolver |
| Structured lookup | answer exact questions from structured data sources | metadata search, SQL or service query, record lookup APIs |
| Unstructured retrieval | answer questions requiring document evidence | summary retrieval, vector search, keyword retrieval, rerank, raw chunk fetch |
| Reasoning | decomposition, comparison, synthesis, higher-cost interpretation | flash model, pro model, planner or synthesizer |
| Action and workflow execution | perform external actions or guided business operations | API clients, workflow runners, ticketing or case-management actions |
| Escalation | clarifying questions or human handoff | clarification generator, handoff packet builder, human-agent routing connector |

RAG belongs in the `Unstructured retrieval` family.

### Catalog Template

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

### Registry Rules

- the orchestration layer looks up capability definitions from a registry; it never hardcodes domain tool logic
- each domain team owns and updates its own subsystem tools and schemas
- every tool and capability records an explicit owner in the registry or schema metadata
- version and rollout metadata are recorded so regressions trace to specific changes

This owner metadata is what later powers operational attribution (see Measurement And Operations).

## Hard Boundaries

Four boundaries apply to every path through the flow. They exist so that safety and cost do not depend on prompt compliance.

### Governance Boundary

Security and permission enforcement belong to the harness and company policy systems, never to prompts alone:

- the model may propose a tool call
- the harness decides whether the call is allowed

Read access is governed exactly like write access: the model never directly reads protected content or acts outside the harness. This keeps permissions, risk rules, approvals, and content exposure controls in code and company systems.

Tools are simple executors. Tools do not call each other; only the orchestration layer plans and sequences tool calls — including all cross-domain calls.

### Cross-Domain Policy

Cross-domain requests are allowed when the query genuinely requires them.

Default policy:

1. single-domain by default
2. clarify if domain scope is ambiguous
3. allow multi-domain execution only for explicitly supported workflows

Additional rules:

- permission is checked by the harness for each call
- multi-domain execution may be sequential or parallel when dependencies allow
- if a prerequisite call fails, dependent calls must not run
- if one call fails, return the successful scoped information and clearly label the missing part
- if sources conflict, do not infer a conclusion; present the conflict and recommend human confirmation
- if ambiguity remains material, clarify rather than infer

Response style for partial success:

```text
We could retrieve the general policy information, but we could not verify your identity at this time.
General information:
...
For account-specific conclusions, please try again later or contact a human agent.
```

Response style for conflicting sources:

```text
We found conflicting information:
- Source A says ...
- Source B says ...
We cannot provide a reliable conclusion from the available data.
Please confirm with the related human agent.
```

### Escalation Budgets

Everything that loops spends a finite budget from the same policy family introduced in `CH01`: clarification turns, reinterpretations, stronger-model retries, alternate-capability attempts, tool-call counts, retrieval breadth, and end-to-end wall-clock time.

Budget state is visible to routing at all times; an exhausted budget forces `handoff_human` instead of another guess. This is what makes the layered fallback path predictable instead of emergent.

### Latency UX

Because execution is modular, the layer knows which path a request is taking before it finishes — so the product can set correct expectations per class of work.

Suggested latency tiers:

| Tier | Typical Path | User-Facing Behavior |
|---|---|---|
| Fast | deterministic lookup, single API read | immediate or minimal loading state |
| Standard | normal retrieval, light clarification, bounded tool chain | short wait hint |
| Careful | multi-step reasoning, conflict resolution, higher-risk checks | progress steps or staged status |
| Escalation | unresolved ambiguity or blocked execution | explicit human handoff or retry guidance |

Latency-related preferences are configurable per task, capability, or tool:

- max retrieved chunks, max rerank candidates
- max tool calls, max model escalations
- queue-allowed or not, partial-response preferred or not
- max wall-clock budget

For example: internal tools may accept queue-based throughput over immediacy; customer-support flows may prefer shorter first responses even when partial; retrieval-heavy capabilities may cap chunk counts differently by latency preference.

> Modular orchestration makes latency visible and predictable: because the system knows which path it is taking, it can provide appropriate progress cues and expected wait times for each class of work.

### Human Handoff Contract

When escalation fires, the handoff carries the packet shape defined in `CH01` (conversation context, system summary, candidates, evidence, attempt history, suggested next step), extended with orchestration state:

1. original user request and relevant history
2. normalized query and framed interpretation
3. attempted capabilities and outcomes
4. current budget states
5. recommended next action

Resolved human cases are recorded and fed back: recurring corrections become alias updates, routing-rule adjustments, prompt fixes, and escalation-policy tuning.

## Measurement And Operations

The platform is evaluated offline and monitored online; operations attribute failures to owners.

### Offline Evaluation

Golden datasets and controlled benchmarks cover:

- routing quality
- tool selection precision
- schema generation precision
- answer quality
- cost reduction
- safety and policy correctness

### Online Monitoring

Useful online measures:

- percentage of flash-model paths versus pro-model escalations
- percentage of human handoffs
- user satisfaction signals; repeated user retries as a negative signal
- failure or rejection rates
- latency and cost trends over time

Monitoring runs both scheduled and operationally: nightly summaries review aggregate drift, while engineers inspect significant anomalies and intervene as needed.

### Ownership And Nightly Review

Because the system is split by domain, capability, tool schema, and owner, failures attribute precisely:

- which tool is slow or failing
- which capability is degrading
- which domain subsystem is unstable
- which team should investigate

A nightly job summarizes the day's activity:

| Level | Example Metrics |
|---|---|
| Tool | latency distribution, failure rate, timeout rate, bad schema rate |
| Capability | success rate, fallback rate, retry rate |
| Domain | volume, latency, handoff rate, top failure patterns |
| Orchestration | wrong-route signals, clarification rate, escalation rate |

Outputs go to issue queues routed by owner: latency trends, failed cases, timeout clusters, schema mismatch patterns, escalation spikes.

Failures are classified, not pooled:

- orchestration issue
- schema issue
- tool or backend issue
- permission or policy issue
- dependency outage
- user ambiguity cluster

Classification matters because it sends issues to the real source of degradation instead of to one catch-all group.

## Deferred And Out Of Scope

General long-term agent memory is intentionally deferred. Current scope treats most requests as one-time interactions, with optional resume of a previous unresolved session via retrieval-plus-summary for the next agent or human.

Not yet decided — but will become necessary as session resume becomes common:

- what session context persists
- whether inferred facts may persist across unrelated sessions (and how user corrections override them)
- what may be stored durably at all

Without these boundaries, later orchestration behavior becomes inconsistent or unsafe, so memory stays out until the boundaries are designed.

## Remaining Open Design Questions

The architecture is now largely defined; remaining work is operational detail rather than top-level structure.

### 1. Confidence Calibration

Confidence-aware routing depends on turning signal patterns into decisions. Candidate inputs: deterministic match strength, model confidence, retrieval agreement, ambiguity signals, execution-outcome signals.

The open question is the exact runtime decision policy mapping these signals to proceed, clarify, retry, escalate, or reject-tool-execution. `CH02_03_Confidence-Safety-and-Validation.md` owns the structural side; calibration against labeled data is still pending.

### 2. Testing Strategy

Beyond prompt or answer-quality evaluation, the orchestration layer needs:

- routing test cases
- ambiguity and clarification tests
- policy enforcement tests
- capability output-contract tests
- schema-loading regression tests
- high-risk action confirmation tests
- dependency-graph execution tests

covering both offline validation and production regression protection. See `CH04_Testing-and-Evaluation.md`.

### 3. Operational Alert Thresholds

Online monitoring and nightly review exist, but intervention thresholds are still unspecified: how much latency drift warrants investigation, when timeout-rate changes become urgent, when escalation spikes indicate a system issue, when schema-mismatch frequency indicates a bad rollout.

Without thresholds, monitoring exists but responses remain inconsistent.
