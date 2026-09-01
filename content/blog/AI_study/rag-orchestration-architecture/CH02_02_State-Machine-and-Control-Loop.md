---
title: "State Machine and Control Loop"
date: 2026-07-20T09:43:56+08:00
lastmod: 2026-09-01T22:32:00+08:00
draft: true

description: "How requests move through the orchestration runtime, including states, retries, caps, fallback, and events."
summary: "How requests move through the orchestration runtime, including states, retries, caps, fallback, and events."

categories:
  - "AI Study"
tags:
  - "RAG"
  - "Architecture"
  - "Orchestration"
  - "Runtime Contract"

slug: "CH02_02_State-Machine-and-Control-Loop"
---
## Purpose

This note defines how the request orchestration runtime moves.

It focuses on lifecycle control rather than object structure.

The main questions are:

1. what states can a request enter
2. how control returns to routing
3. how retries and loop caps are bounded
4. how fallback remains harness-owned
5. what events the runtime should emit

Related notes:

- [`CH02_Request-Orchestration-Layer.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_request-orchestration-layer/)
- [`CH02_01_Runtime-Objects.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_01_runtime-objects/)
- [`CH02_03_Confidence-Safety-and-Validation.md`](https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/ch02_03_confidence-safety-and-validation/)

## Why This Design Exists

This note exists because LLM-driven orchestration can appear simple in a flowchart while still becoming unstable in implementation.

The main risks are:

- unclear current state
- hidden control flow
- unbounded retries
- ad hoc fallback behavior
- poor replayability after failure

The state machine and control loop are therefore designed to make control explicit, bounded, and replayable.

## Request State Machine

The runtime needs a minimal state model so each request has one current status.

Recommended first-version states:

1. `captured`
2. `interpreting`
3. `awaiting_clarification`
4. `routing`
5. `executing`
6. `validating`
7. `completed`
8. `handoff`
9. `rejected`
10. `failed`

State intent:

- `captured`: request has been received and preserved
- `interpreting`: normalization and framing are running
- `awaiting_clarification`: user response is required before safe continuation
- `routing`: harness is selecting the next path
- `executing`: a governed capability is running
- `validating`: the system is checking whether the result is acceptable
- `completed`: a final answer or valid partial answer has been produced
- `handoff`: the case has been escalated to a human
- `rejected`: the system declined to execute
- `failed`: execution stopped because of system or dependency failure

### State Transition View

```mermaid
stateDiagram-v2
    [*] --> captured
    captured --> interpreting
    interpreting --> routing
    routing --> awaiting_clarification: clarify
    routing --> executing: execute_capability
    routing --> interpreting: stronger_model
    routing --> handoff: handoff_human
    routing --> rejected: reject
    awaiting_clarification --> interpreting: user_reply_received
    executing --> validating
    validating --> completed: accepted
    validating --> routing: retry_or_fallback
    executing --> failed: backend_or_policy_failure
    failed --> routing: failure_result_returned
```

Minimal transition rules:

- only one active state per request
- every transition should record timestamp and trigger
- clarification and human handoff are terminal for the current turn, but not necessarily for the broader session

Why this exists:

- one shared answer to "where is this request now?" instead of spaghetti retry logic spread across handlers

What it prevents:

- components disagreeing about whether a request is running or done
- ambiguous ownership of next-step decisions

Boundary with nearby components:

- the state machine describes allowed movement
- the runtime objects (`CH02_01`) describe what data each state works with

## Control Loop Principle

The control loop should remain the single authority for what happens next.

That means:

- execution should return a structured result
- validation should return a structured weak-result or acceptance signal
- neither execution nor validation should decide retry, escalation, rejection, or handoff on their own
- routing should decide the next branch after reading the returned result

This keeps the harness boundary clean.

Why this exists:

- The harness must remain the control authority even when the model proposes the next step.

What it prevents:

- tools or validators deciding their own retries or escalations
- control logic being duplicated in multiple places
- unclear ownership when the system loops or fails

Boundary with nearby components:

- execution and validation report status
- routing decides what happens next

## Loop Budget And Fallback Policy

This section is the concrete home of the escalation-budget boundary declared in `CH02_Request-Orchestration-Layer.md`: the caps below are the policy behind that boundary.

If the runtime uses an LLM to think about the next step, it still needs a harness-owned limit on how many times each branch may repeat.

The key rule is:

- the LLM may propose the next action
- the harness checks whether that action is still allowed
- if the branch is at cap, the harness blocks that branch and chooses the next legal fallback through the routing loop

Why this exists:

- LLM-driven control is useful, but it is naturally inclined to keep trying unless the harness imposes explicit limits.

What it prevents:

- runaway loops
- rising cost and latency with weak user value
- repeated retries that look active but are no longer productive

Boundary with nearby components:

- loop budget answers whether a branch may continue
- fallback policy answers what legal branch remains after a cap is hit

### Attempt Budget Fields

Budget limits and live counters live on the request envelope's `execution_budget` field — the canonical schema is defined in `CH02_01_Runtime-Objects.md`. The runtime additionally tracks attempt counters as state:

```yaml
attempt_counters:
  total_loops: 0
  reinterpretations: 0
  execution_retries: 0
  clarification_turns: 0
  model_escalations: 0
```

Separate counters matter because the loops they bound are different failure modes:

- reinterpretation loops and execution retries fail in different ways and need independent ceilings
- clarification loops consume user attention, not just compute
- stronger-model escalation is expensive and should be tightly capped
- total loop count prevents the whole request from cycling even when no individual branch cap is exhausted

### Control-Loop Decision Rule

Every time control returns to `routing`, the harness should do four things in order:

1. read the latest result object from interpretation, execution, or validation
2. increment the relevant attempt counter
3. compare counters against the request budget
4. either allow the proposed next action or replace it with a fallback action

The LLM may propose actions such as:

- `clarify`
- `reinterpret`
- `stronger_model`
- `retry_execution`
- `switch_capability`
- `handoff_human`
- `reject`

But the harness is the final authority on whether that branch is still legal.

### Fallback Decision Table

When a branch hits its cap, the system should not fail open or keep looping. Division of labor with `CH02_03`: the execution decision table there governs how routing reacts to a completed execution attempt; this table governs what remains legal after a cap is hit.

| Cap reached | Typical meaning | Allowed fallback actions | Preferred fallback |
| --- | --- | --- | --- |
| Reinterpretation cap | The system has already tried enough low-cost reinterpretation passes. | clarify, stronger model, human handoff | clarify if the ambiguity is user-resolvable; otherwise stronger model or handoff |
| Clarification cap | The user-facing ambiguity loop is no longer productive. | conservative execution, human handoff, reject | human handoff unless a conservative low-risk path is clearly available |
| Execution retry cap | The selected capability or dependency is not recovering fast enough. | switch capability, partial answer, human handoff, failed | switch capability first if a real fallback exists; otherwise handoff or fail |
| Model escalation cap | The system already used the stronger-model budget. | clarify, human handoff, reject | clarify if the user can resolve it; otherwise handoff |
| Total loop cap | The request has consumed enough control-loop churn overall. | answered, partial answer, human handoff, rejected, failed | choose a terminal outcome only |

### Fallback Selection Rules

The fallback table should not be treated as one fixed string per cap.

The actual fallback choice should still consider:

- ambiguity type
- risk level
- whether user clarification is still meaningful
- whether an alternate capability actually exists
- whether the path is read-only or action-taking
- whether partial answer is acceptable
- whether policy allows any further automated action

So the better model is:

- cap exhaustion limits what is no longer allowed
- fallback policy defines what is still allowed
- routing chooses the best remaining legal action

Why this exists:

- A cap only says "stop doing this." The system still needs a principled answer to "what next?"

What it prevents:

- brittle dead ends after cap exhaustion
- arbitrary fallback behavior chosen differently by different engineers or prompts
- systems that are bounded but not operationally complete

### Clean Failure Handling Rule

Execution and validation should return structured results to routing rather than branching on their own.

Examples:

- execution returns `dependency_timeout`
- execution returns `permission_denied`
- validation returns `grounding_insufficient`
- validation returns `result_incomplete`

Routing then decides whether to:

- retry the same capability
- switch capability
- ask clarification
- escalate to stronger model
- hand off to a human
- reject
- fail the request

Why this exists:

- structured results keep retry, escalation, and rejection decisions in one place — the routing loop

What it prevents:

- tools or validators deciding their own retries or escalations
- control logic being duplicated in multiple places
- unclear ownership when the system loops or fails

Boundary with nearby components:

- execution and validation report status
- routing decides what happens next

### First-Version Default Caps

The canonical values carried by the envelope schema in `CH02_01` are:

- `max_total_loops: 6`
- `max_reinterpretations: 2`
- `max_execution_retries: 2`
- `max_clarification_turns: 2`
- `max_model_escalations: 1`
- `max_wall_clock_ms: 8000`

These values are not universal. They are only good starting points until evaluation data justifies tighter or looser bounds.

## Event Model

Even if the runtime stores object snapshots, it should also emit simple events.

Useful first-version events:

- `request_captured`
- `interpretation_created`
- `routing_decided`
- `clarification_requested`
- `clarification_received`
- `capability_execution_started`
- `capability_execution_completed`
- `validation_completed`
- `human_handoff_created`
- `request_completed`
- `request_rejected`
- `request_failed`

Why this exists:

- routing, retry, and escalation behavior can be reconstructed during incident review without raw-log archaeology

What it prevents:

- requiring a fully event-sourced system just to gain replayability

Boundary with nearby components:

- object snapshots remain the source of truth
- events are a small, derived projection for monitoring and replay
