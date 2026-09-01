---
title: "Runtime Objects"
date: 2026-07-20T09:43:56+08:00
lastmod: 2026-09-01T22:32:00+08:00
draft: true

description: "The core runtime objects used by the request orchestration layer."
summary: "The core runtime objects used by the request orchestration layer."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Orchestration"
  - "Runtime Contract"

slug: "CH02_01_Runtime-Objects"
---
## Purpose

This note defines the main runtime objects used by the request orchestration layer.

Its job is to answer a simple question:

> What durable objects should exist if the orchestration runtime is to be executable, observable, and reviewable?

This note is a concrete extension of [`CH02_Request-Orchestration-Layer.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_request-orchestration-layer/).

Related notes:

- [`CH02_02_State-Machine-and-Control-Loop.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_02_state-machine-and-control-loop/)
- [`CH02_03_Confidence-Safety-and-Validation.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_03_confidence-safety-and-validation/)

## Scope

This note defines six request-lifecycle objects:

1. request envelope
2. interpretation record
3. routing decision
4. capability execution record
5. final outcome
6. human handoff packet

and one config-time artifact that the runtime reads during capability selection and schema loading:

7. capability catalog entry (see Registry Object below)

## Contract Principles

| # | Principle | Meaning |
|---|---|---|
| 1 | Preserve Original Input | The untouched user request must remain available throughout the lifecycle. |
| 2 | Separate Interpretation From Decision | What the model inferred is not the same thing as what the harness decided. Interpretation artifacts and routing decisions are stored as separate objects. |
| 3 | Record Why, Not Only What | The contract should preserve enough reasoning signals to explain later why a route, fallback, or escalation happened. |
| 4 | Keep The First Version Small | This is a minimum serious contract, not a final enterprise schema catalog. |

## Why These Objects Exist

These objects are not arbitrary schema cuts.

Each one exists to prevent a specific failure mode in LLM-driven orchestration:

- the request envelope prevents state from being scattered across prompts, tool arguments, and session memory
- the interpretation record prevents model belief from being treated as execution authority
- the routing decision prevents hidden control flow inside prompts or tool wrappers
- the capability execution record prevents execution from becoming opaque and hard to govern
- the final outcome prevents raw execution output from being confused with accepted user-facing results
- the human handoff packet prevents escalation from becoming manual log reconstruction

The broader design principle is:

> Separate the things the system knows, the decisions it makes, the actions it takes, and the outcomes it accepts.

## Core Object 1: Request Envelope

The request envelope is the root object for one user request.

Purpose:

- preserve request identity
- preserve original input and context
- carry execution-wide policy and budget constraints
- hold current state references

Example shape:

```yaml
request_id: req_01JXYZ...
session_id: sess_01JXYZ...
user_id: user_12345
entrypoint: chat
timestamp_start: 2026-07-20T16:30:00+08:00

original_input:
  text: "Tell me about spring saver"
  attachments: []
  locale: en

context:
  chat_history_ref: hist_456
  prior_request_refs: []
  tenant_id: corp_a

policy_context:
  identity_tier: authenticated_employee
  permission_profile: hr_basic_read
  risk_profile: low
  data_scope: internal

execution_budget:
  # canonical escalation-budget schema; semantics and first-version
  # defaults are discussed in CH02_02_State-Machine-and-Control-Loop.md
  max_total_loops: 6
  max_tool_calls: 4
  max_reinterpretations: 2
  max_execution_retries: 2
  max_clarification_turns: 2
  max_model_escalations: 1
  max_wall_clock_ms: 8000

state:
  current_status: interpreting
  selected_domain: null
  selected_capability: null
  final_outcome_ref: null
```

Required fields:

- `request_id`
- `session_id`
- `user_id` or anonymous identity marker
- `timestamp_start`
- `original_input`
- `policy_context`
- `execution_budget`
- `state.current_status`

Recommended fields for customer-facing systems:

- `scope_policy.domain`
- `scope_policy.allowed_topics`
- `scope_policy.refusal_mode`
- `safety_flags`
- `injection_screening_result`

Notes:

- `original_input.text` should never be overwritten by rewrites
- policy and budget fields belong to the harness, not the model

Why this exists:

- The runtime needs one stable root object that carries identity, original input, policy context, and execution budget together.

What it prevents:

- state scattered across prompts, tool calls, and session caches
- losing the untouched user request after rewrites or clarification
- policy or budget checks being applied inconsistently across stages

Boundary with nearby components:

- the request envelope stores request-wide facts and constraints
- it does not store the system's latest interpretation or routing choice as the source of truth for meaning

Main tradeoff:

- a larger root object increases structure, but that structure is what makes the runtime auditable and governable

## Core Object 2: Interpretation Record

The interpretation record captures what the system currently believes the request means.

Purpose:

- preserve normalization output
- preserve model framing output
- capture ambiguity and confidence signals before routing

Example shape:

```yaml
interpretation_id: int_01JXYZ...
request_id: req_01JXYZ...
timestamp: 2026-07-20T16:30:01+08:00

normalized_query: "tell me about spring saver promotion"
task_type: information_lookup
candidate_domains:
  - domain: customer_support
    score: 0.82

target_entity_guess: spring_saver
requested_attributes:
  - general_description

deterministic_signals:
  alias_hits:
    - spring_saver_2025
    - spring_saver_plus
    - student_spring_saver
  top_match_score: 0.78
  top2_gap: 0.04

model_signals:
  model_name: flash-model
  confidence: 0.68
  ambiguity_flags:
    - multiple_candidate_entities
  alternative_interpretations:
    - spring_saver_2025
    - spring_saver_plus
    - student_spring_saver

interpretation_summary: "Likely promotion lookup, but entity remains ambiguous."
```

Required fields:

- `interpretation_id`
- `request_id`
- `normalized_query`
- `task_type`
- `deterministic_signals`
- `model_signals`

Notes:

- this object may be regenerated after clarification
- interpretation output is evidence, not authority

Why this exists:

- The system needs a place to preserve what it currently thinks the request means without turning that belief into an action automatically.

What it prevents:

- model guesses being mixed directly into control decisions
- losing alternative interpretations too early
- ambiguity signals being hidden inside prompt text instead of stored explicitly

Boundary with nearby components:

- the interpretation record captures candidate meaning
- the routing decision chooses what to do about that meaning

Main tradeoff:

- separating interpretation from routing creates another object, but it makes control behavior much easier to test and review

## Core Object 3: Routing Decision

The routing decision captures what the harness decided to do next.

Purpose:

- separate decision from interpretation
- make runtime control auditable
- provide a stable object for testing and replay

Example shape:

```yaml
routing_decision_id: route_01JXYZ...
request_id: req_01JXYZ...
interpretation_id: int_01JXYZ...
timestamp: 2026-07-20T16:30:01+08:00

decision: clarify
decision_reason:
  primary: multiple_close_entity_candidates
  supporting_signals:
    - top2_gap_below_threshold
    - model_marked_ambiguous

selected_domain: customer_support
candidate_domains:
  - domain: customer_support
    score: 0.82

selected_capability: clarification_generation
fallback_capability: human_handoff

constraints:
  tool_bundle: clarification_only
  max_next_tool_calls: 1
  max_next_wall_clock_ms: 1500

next_action:
  type: ask_user_question
  payload:
    question: "I found multiple likely matches for 'spring saver': Spring Saver 2025, Spring Saver Plus, and Student Spring Saver. Which one did you mean?"
```

Allowed `decision` values in the first version, aligned with the routing contract outcomes in `CH01_Intention-Recognition-Layer.md`:

- `proceed`
- `proceed_conservative` (the CH01 row-8 low-risk read-only path)
- `clarify`
- `stronger_model`
- `execute_capability`
- `retry`
- `handoff_human`
- `reject`

Required fields:

- `routing_decision_id`
- `request_id`
- `interpretation_id`
- `decision`
- `decision_reason`
- `next_action`

Notes:

- `selected_capability` may be null for `reject`
- `clarify` and `handoff_human` are first-class routing outcomes, not failure afterthoughts
- `proceed_conservative` exists so a low-confidence but low-risk read-only case can return a narrowly scoped answer instead of being forced into clarification or handoff

Why this exists:

- The harness needs an explicit control artifact that says what branch was chosen and why.

What it prevents:

- hidden branching inside prompts or ad hoc orchestration code
- unclear responsibility for retry, fallback, and escalation
- difficulty replaying why a case proceeded, clarified, or handed off

Boundary with nearby components:

- interpretation says what the request might mean
- routing says what the system is allowed to do next

Main tradeoff:

- this adds one more object to store, but it is the key object that makes orchestration behavior explicit rather than implicit

## Core Object 4: Capability Execution Record

The capability execution record captures one governed execution attempt.

Purpose:

- describe what capability the harness allowed
- preserve policy checks and execution outputs
- support replay, debugging, and ownership attribution

Example shape:

```yaml
execution_id: exec_01JXYZ...
request_id: req_01JXYZ...
routing_decision_id: route_01JXYZ...
timestamp_start: 2026-07-20T16:30:02+08:00

domain: customer_support
capability_name: promotion_document_retrieval
capability_version: 1.2.0
tool_schema_version: 2026-07-15

tool_bundle_loaded:
  - metadata_search
  - vector_search
  - rerank
  - raw_chunk_fetch

policy_check:
  allowed: true
  permission_profile: cs_read_basic
  risk_decision: approved

execution_plan:
  tool_calls:
    - step: 1
      tool: metadata_search
    - step: 2
      tool: vector_search
    - step: 3
      tool: rerank

result:
  status: success
  output_ref: result_01JXYZ...
  evidence_refs:
    - doc_111#summary
    - doc_111#chunk_07
  confidence_signals:
    retrieval_agreement: 0.84
    grounding_coverage: 0.91

timestamp_end: 2026-07-20T16:30:03+08:00
duration_ms: 942
```

Required fields:

- `execution_id`
- `request_id`
- `routing_decision_id`
- `domain`
- `capability_name`
- `policy_check.allowed`
- `result.status`
- `timestamp_start`

Notes:

- the record should exist for both success and failure
- read operations are also governed execution and should use the same contract shape
- deployments may extend the record with environment-specific fields (scheduler or queue state, upstream dependency failures, redaction state, extra version markers) without changing the contract shape

Why this exists:

- Execution should be treated as governed action, not as an invisible consequence of model reasoning.

What it prevents:

- plan and action being collapsed into one opaque step
- weak accountability for permission checks, tool selection, and failure causes
- inability to distinguish interpretation quality from backend execution quality

Boundary with nearby components:

- the routing decision authorizes the path
- the execution record captures what actually ran and what came back

Main tradeoff:

- explicit execution records increase logging and schema volume, but that cost buys replayability and governance

## Core Object 5: Final Outcome

The final outcome records the request-level result after validation.

Purpose:

- define how the request ended
- separate raw execution output from validated user outcome

Example shape:

```yaml
final_outcome_id: out_01JXYZ...
request_id: req_01JXYZ...
timestamp: 2026-07-20T16:30:03+08:00

outcome_type: answered
user_response_ref: resp_01JXYZ...

validation_summary:
  relevance: pass
  completeness: pass
  grounding: pass
  policy_compliance: pass

used_execution_ids:
  - exec_01JXYZ...

fallback_history: []
```

Allowed `outcome_type` values in the first version:

- `answered`
- `clarification_requested`
- `partial_answer`
- `human_handoff`
- `rejected`
- `failed`

Required fields:

- `final_outcome_id`
- `request_id`
- `outcome_type`
- `timestamp`

Why this exists:

- The system needs a request-level conclusion that is distinct from raw execution output.

What it prevents:

- returning raw tool output as if it were already validated
- confusion between "something ran" and "the request is now satisfactorily handled"
- weak audit trails around partial answers, rejection, and failure outcomes

Boundary with nearby components:

- execution produces a result candidate
- final outcome records what the system ultimately accepted and returned

Main tradeoff:

- this adds another lifecycle artifact, but it makes acceptance and termination explicit

## Core Object 6: Human Handoff Packet

The handoff packet is a specialized outcome object for unresolved or policy-constrained cases.

Purpose:

- let a human continue without reconstructing the case from raw logs
- keep escalation compact and operationally useful

This packet implements the handoff contract defined in `CH01_Intention-Recognition-Layer.md`, extended with the orchestration-level state described in `CH02_Request-Orchestration-Layer.md`.

Example shape:

```yaml
handoff_id: handoff_01JXYZ...
request_id: req_01JXYZ...
timestamp: 2026-07-20T16:30:05+08:00

reason:
  code: ambiguity_not_resolved
  summary: "Multiple promotion candidates remained after two clarification attempts."

conversation_context:
  original_input: "Tell me about spring saver"
  clarification_history:
    - "Which one did you mean: Spring Saver 2025, Spring Saver Plus, or Student Spring Saver?"
    - "Is this for a student offer or a general promotion?"

current_interpretation:
  normalized_query: "spring saver promotion"
  candidate_entities:
    - spring_saver_2025
    - spring_saver_plus
    - student_spring_saver

attempt_history:
  routing_decision_ids:
    - route_01JXYZ...
  execution_ids: []

budget_state:
  total_loops_used: 2
  clarification_turns_used: 2
  model_escalations_used: 0
  execution_retries_used: 0

recommended_next_step:
  type: human_question
  payload: "Confirm the exact promotion name or campaign code before answering."
```

Required fields:

- `handoff_id`
- `request_id`
- `reason`
- `conversation_context`
- `current_interpretation`
- `budget_state`
- `recommended_next_step`

The orchestration-level handoff contract in `CH02_Request-Orchestration-Layer.md` maps onto these fields:

| Contract item (orchestration state) | Packet field |
| --- | --- |
| original user request and relevant history | `conversation_context.original_input` |
| normalized query and framed interpretation | `current_interpretation` |
| attempted capabilities and outcomes | `attempt_history` |
| current budget states | `budget_state` |
| recommended next action | `recommended_next_step` |

Why this exists:

- Human escalation should be a designed runtime path, not an operational afterthought.

What it prevents:

- forcing human agents to reconstruct context from raw logs
- poor-quality handoffs after repeated ambiguous or failed automation loops
- treating escalation as a silent system failure rather than a product behavior

Boundary with nearby components:

- the final outcome may say that handoff happened
- the handoff packet contains the actual case payload a human needs to continue

Main tradeoff:

- this requires more structured escalation data, but it greatly improves operational continuity and reviewability

## Registry Object: Capability Catalog Entry

The six objects above live for the duration of one request. The runtime also reads a config-time artifact: the capability catalog entry, looked up from the capability registry during capability selection and adaptive schema loading (steps 7–8 of the orchestration flow in `CH02_Request-Orchestration-Layer.md`).

Catalog entries are owned by domain teams, versioned, and published through rollout states so regressions trace to specific changes. The orchestration layer only reads the registry; it never hardcodes domain tool logic. The nine conceptual contract elements are summarized in `CH02_Request-Orchestration-Layer.md`; this is the concrete schema:

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

Required fields: `name`, `owner`, `domain_scope`, `capability_version`, `rollout_status`, `use_when`, `avoid_when`, `tool_schema_bundle`, `output_contract`, `fallbacks`.

The nine conceptual contract elements in `CH02_Request-Orchestration-Layer.md` map onto the concrete schema like this:

| Conceptual element | Concrete field |
| --- | --- |
| purpose | `purpose` |
| usage boundary (`use_when` / `avoid_when`) | `use_when`, `avoid_when` |
| input contract | `required_inputs`, `optional_inputs`, `preconditions` |
| tool schema bundle | `tool_schema_bundle` |
| output contract | `output_contract` |
| confidence and validation signals | `confidence_signals`, `validation_rules` |
| fallback paths | `fallbacks`, `human_escalation_required_when` |
| owner | `owner` |
| domain scope | `domain_scope` |

Notes:

- entries are config-time artifacts, not per-request state; the runtime reads them, requests only reference them by id
- `loading_mode` drives how step 8 exposes the tool surface (single capability, primary plus fallback, or staged supervisor)
- `confidence_signals` and `validation_rules` here feed the confidence and validation policies in `CH02_03_Confidence-Safety-and-Validation.md`
