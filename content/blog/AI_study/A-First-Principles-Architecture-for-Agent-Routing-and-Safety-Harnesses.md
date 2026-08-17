---
title: "A First-Principles Architecture for Agent Routing and Safety Harnesses"
date: 2026-08-04T23:31:21+08:00
lastmod: 2026-08-17T14:41:13+08:00
draft: false

categories:
  - "AI Study"
tags:
  - "AI Study"
  - "Agent"
  - "Architecture"
  - "Safety"

slug: "agent-routing-safety-harness"
---

## Governing Probabilistic Engines via First-Principles System Design

---

# 1. Problem Definition and First-Principles Constraints

## 1.1 The Core Thesis & Enterprise Mismatch

Deploying Generative AI Agents into high-stakes, regulated environments (such as financial services, healthcare, and core infrastructure) exposes a fundamental architectural mismatch: **enterprise software requires deterministic guarantees, whereas Large Language Models (LLMs) are probabilistic token samplers.**

Traditional agent architectures attempt to overcome model instability through empirical prompt engineering—wrapping LLMs in self-reflection prompts or granting them direct API execution handles. This design creates brittle systems susceptible to four systemic enterprise failure modes:

* **Unbounded Execution Liability:** Granting a non-deterministic model direct database or API access allows a single hallucinated payload to trigger irreversible, state-changing transactional errors.
* **Correlated Errors & Single Point of Failure:** When an auto-regressive model evaluates its own confidence within the same context window, it relies on the exact same parameter weights that generated the initial response, routinely rationalizing its own errors.
* **Auditability & Compliance Deficits:** High-dimensional neural network weights cannot be unit-tested, mathematically proven, or reproduced across model versions to satisfy strict regulatory requirements.
* **Catastrophic Failure from Symmetric Risk Treatment:** Standard agent frameworks treat all tool invocations uniformly, ignoring the reality that the operational and financial loss from a false positive on a write operation (e.g., executing a wire transfer) is exponentially higher than on a read operation (e.g., querying a database).

---

## 1.2 The First-Principles Logical Derivation Pipeline

To establish an airtight safety architecture, system requirements must not be invented arbitrarily. They are derived directly from the mathematical properties of transformer neural networks and the risk topology of enterprise state space.

| 1. Enterprise Problem | 2. Intrinsic Math / Domain Fact | 3. System Constraint & Requirement | 4. Design Mechanism *(Sec. 2 Solution)* |
| --- | --- | --- | --- |
| **Unbounded Execution Liability**: Hallucinated payloads execute unauthorized state changes. | **Probabilistic Sampler**: Outputs are sampled from $P(w_t \mid w_{<t})$; factual correctness is non-guaranteed. | **Zero Execution Authority:** Probabilistic model outputs must strictly be treated as unprivileged proposals. | **Proposal vs. Execution Decoupling:** LLM generates JSON payload; hardcoded runtime sandbox validates and executes. |
| **Correlated Error & SPOF**: Model self-checking passes rationalize their own initial hallucinations. | **Shared Parameter Weights ($W$)**: Inference and self-reflection share identical parameter weights and context bias. | **Orthogonal Verification:** Validation must possess zero error correlation with the proposal generation path. | **Heterogeneous Redundancy:** Independent context validator agent paired with non-neural symbolic rule parsers. |
| **Compliance & Audit Deficit**: Black-box decisions cannot be unit-tested, audited, or reproduced. | **Black-Box Latent State**: Neural inference paths are high-dimensional, latent, and non-deterministic. | **White-Box Auditability**: Domain capability boundaries and routing must be 100% deterministic and inspectable. | **Microsecond Pre-Router**: Algorithmic edit distance (Levenshtein/Jaro-Winkler) and Trie-matching before LLM invocation. |
| **Symmetric Loss Exposure**: Identical treatment of read and write actions leads to catastrophic financial loss. | **Asymmetric Risk Topology**: Loss severity is asymmetric across state space: $C_{FP}(\text{Write}) \gg C_{FP}(\text{Read})$. | **Risk-Proportional Authorization:** Execution authorization rigor must scale non-linearly with state-change liability. | **Calibrated Risk Gates & Dynamic HCI:** Asymmetric probability thresholds ($P_{\text{intent}}$) with interactive option chips for ambiguity. |

---

## 1.3 Deductive Derivation of Architectural Constraints

From this four-stage derivation, four non-negotiable architectural constraints logically follow:

### Constraint 1: Zero Execution Authority (Proposal vs. Execution Isolation)

* **Requirement:** Because an auto-regressive model operates purely on probability distributions $P(w_t \mid w_{<t})$, its output can never possess execution authority ($Cmd$).
* **Invariant:** Model output must strictly function as an unprivileged **Intent Proposal** ($Prop$). The actual execution command must be a deterministic function enforced entirely outside the model:

$$Cmd = \text{DeterministicHarness}(Prop)$$



### Constraint 2: Orthogonal Verification

* **Requirement:** To eliminate Single Points of Failure (SPOF), validation mechanisms must have zero error correlation with the proposal generator.
* **Invariant:** A validator cannot share the generator's context window, prompt state, or neural parameters. Verification requires complete structural, parameter, or algorithmic independence from the generating process.

### Constraint 3: White-Box Deterministic Governance

* **Requirement:** To satisfy legal auditability and regulatory compliance, the primary boundary decision—determining whether a user query falls within valid system capabilities—must be fully reproducible and unit-testable.
* **Invariant:** Primary domain routing decisions cannot be delegated to black-box neural networks. Initial intent evaluation must produce deterministic, white-box audit logs prior to token generation.

### Constraint 4: Risk-Proportional Authorization Bounds

* **Requirement:** Because the financial and operational cost of a False Positive ($C_{FP}$) is non-uniform across system operations:

$$C_{FP}(\text{Read}) \ll C_{FP}(\text{Write})$$



the system cannot enforce static or uniform authorization boundaries.
* **Invariant:** The verification burden and required confidence bounds must scale proportionally with the potential blast radius of the requested state change, automatically enforcing human confirmation when model uncertainty overlaps with high liability.

---

# 2. Architectural Design: Encapsulating Probabilistic Engines in Deterministic Shells

To operationalize the four derived constraints, the system architecture decouples intent evaluation, risk gating, proposal generation, and execution into distinct, single-responsibility layers. The non-deterministic LLM is completely enclosed within a deterministic software shell.

```
                      [ Unstructured User Input ]
                                   │
                                   ▼
      ┌─────────────────────────────────────────────────────────┐
      │ 2.1 Microsecond Pre-Router Engine (Mechanism 3)         │
      │  • Algorithmic Distance (Levenshtein, Jaro-Winkler)     │
      │  • Trie & Schema Graph Matching                         │
      └────────────────────────────┬────────────────────────────┘
                                   │ Yields Prior P_intent
                                   ▼
      ┌─────────────────────────────────────────────────────────┐
      │ 2.2 Calibrated Risk Gate & Dynamic HCI (Mechanism 4)    │
      │  • Asymmetric Thresholds: P_read ≥ 0.65, P_write ≥ 0.99 │
      │  • Ambiguous Traffic ──► Option Chips (≤ 3)             │
      └────────────────────────────┬────────────────────────────┘
                                   │ Validated Intent Stream
                                   ▼
      ┌─────────────────────────────────────────────────────────┐
      │ 2.3 LLM Proposal Engine (Mechanism 1)                   │
      │  • Zero Execution Handle / No Network Credentials       │
      │  • Generates Strict JSON Proposal Payload (Prop)        │
      └────────────────────────────┬────────────────────────────┘
                                   │ Proposal (Prop)
                                   ▼
      ┌─────────────────────────────────────────────────────────┐
      │ 2.4 Heterogeneous Orthogonal Verification (Mechanism 2) │
      │  • Layer 1: Context-Isolated Validator Agent            │
      │  • Layer 2: Hardcoded Sandbox Harness (RBAC/Limits)     │
      └────────────────────────────┬────────────────────────────┘
                                   │ Validated Command (Cmd)
                                   ▼
                     [ API / Database Execution ]

```

---

## 2.1 Mechanism 3: Microsecond White-Box Pre-Router Engine

* **Addressed Requirement:** **White-Box Auditability** (Requirement 3) derived from the Black-Box Latent State of neural networks.
* **Core Objective:** Evaluate input validity and compute intent prior probabilities without invoking downstream LLM tokens.

Before passing raw text to a neural model, the pipeline executes a microsecond-level algorithmic pre-processing pass. This stage matches unstructured user inputs against the system's registered schema registry using deterministic string and graph topology metrics:

$$\text{Metric} = \mathbf{f}_{\text{dist}}(\text{Input}, \text{Schema Entities})$$

### Algorithmic Metric Combination

1. **Syntactic Edit Distance:** Calculates Levenshtein and Jaro-Winkler distances to handle typos, character transpositions, and minor noise in structured arguments.
2. **Prefix Trie Matching:** Evaluates exact and prefix token matches against system command dictionaries and registered API function names.
3. **Schema Graph Distance:** Computes topological shortest-path distances across domain entity-relationship graphs to verify semantic cohesion among detected entities.

### Output Metrics & Prior Probability Conversion

The algorithm yields a deterministic prior probability score, denoted as $P_{\text{intent}} \in [0, 1]$.

$$\text{If } P_{\text{intent}} < \tau_{\text{min}}, \quad \text{Halt Pipeline Immediately}$$

* **Microsecond Execution SLA:** Operates in $< 5 \text{ ms}$, incurring zero token generation costs.
* **White-Box Auditability:** Every evaluation produces an exact, mathematically reproducible decision trail that can be unit-tested using standard software testing suites.

---

## 2.2 Mechanism 4: Calibrated Risk Gates & Dynamic HCI

* **Addressed Requirement:** **Risk-Proportional Authorization Bounds** (Requirement 4) derived from Asymmetric Risk Topology ($C_{FP}(\text{Write}) \gg C_{FP}(\text{Read})$).
* **Core Objective:** Enforce non-symmetric execution confidence gates and eliminate probabilistic guessing on ambiguous inputs.

Instead of applying uniform confidence thresholds, the system enforces non-symmetric probability boundaries calibrated directly to state-change liability:

| Action Category | Operational Impact | Confidence Threshold ($\tau$) | Governance Requirement |
| --- | --- | --- | --- |
| **Low-Risk (Read-Only)** | Knowledge Base RAG, Balance Inquiry | $P_{\text{intent}} \ge 0.65$ | Autonomous Execution allowed if $P_{\text{intent}}$ meets threshold. |
| **High-Risk (State-Changing)** | Fund Transfer, Account Update, DB Write | $P_{\text{intent}} \ge 0.99$ | Mandatory secondary parameter diff confirmation at UI level. |

### Dynamic Human-Computer Interaction (HCI) Fallback

When $P_{\text{intent}}$ falls into an ambiguous confidence interval ($\tau_{\text{min}} \le P_{\text{intent}} < \tau_{\text{required}}$), the system halts autonomous execution. Rather than prompting the LLM to guess user intent, it triggers a structured HCI step:

```
[ Input Ambiguity Detected ] ──► Compute Top-3 Schema Matches ──► Render UI Option Chips (≤ 3)
                                                                            │
[ Deterministic User Selection ]  ◄─────────────────────────────────────────┘

```

Adhering to Hick's Law, the UI presents at most **three explicit Option Chips**. This converts open-ended probabilistic ambiguity into an explicit, deterministic authorization event with minimal cognitive friction.

---

## 2.3 Mechanism 1: Intent Proposal Engine (Zero Execution Authority)

* **Addressed Requirement:** **Zero Execution Authority** (Requirement 1) derived from the Probabilistic Sampler nature of transformers.
* **Core Objective:** Isolate token generation from API execution, ensuring model output can never directly alter state.

Once an input clears the pre-router and risk gate, it is passed to the LLM. The model's runtime environment is strictly isolated:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LLM Proposal Container                          │
│                                                                        │
│   • ZERO Database Handles                 • ZERO Network API Credentials│
│   • ZERO Shell/Exec Privileges            • STRICT JSON Schema Output  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Unprivileged Payload
                                    ▼
                 Intent Proposal Payload (Prop)

```

The model functions strictly as a **Parameter-Filling Compiler**. Its output is forced via grammar-constrained sampling (e.g., JSON schema constraints) into an unprivileged **Intent Proposal** ($Prop$):

```json
{
  "proposal_id": "prop_982347102",
  "target_action": "ExecuteWireTransfer",
  "parameters": {
    "source_account": "ACC-8821",
    "destination_account": "ACC-3004",
    "amount": 5000.00,
    "currency": "USD"
  }
}

```

Because the LLM container holds zero environment tokens, database connection handles, or network sockets, a hallucinated payload cannot execute an unauthorized transaction natively.

---

## 2.4 Mechanism 2: Heterogeneous Orthogonal Verification & Runtime Harness

* **Addressed Requirement:** **Orthogonal Verification** (Requirement 2) derived from Shared Parameter Weights ($W$) and context bias.
* **Core Objective:** Eliminate Single Points of Failure (SPOF) and confirmation bias through multi-layer verification prior to execution.

Before an Intent Proposal ($Prop$) is converted into an actual Execution Command ($Cmd$), it must pass through two independent, non-correlated validation layers:

```
 [ Proposal Payload (Prop) ]
              │
              ▼
 ┌───────────────────────────┐
 │ Layer 1: Isolated Agent   │ ──► Context/Prompt Isolated Model Evaluates Logic
 └────────────┬──────────────┘
              │ Passed
              ▼
 ┌───────────────────────────┐
 │ Layer 2: Hardcoded Harness│ ──► Deterministic Code Validates RBAC & Boundaries
 └────────────┬──────────────┘
              │ Passed
              ▼
   [ Executable Command (Cmd) ]

```

### Layer 1: Context-Isolated Validator Agent

The proposal ($Prop$) is evaluated by a distinct Validator Agent operating in a completely isolated context window, with distinct prompt instructions (or an alternate model family). This eliminates single-chain confirmation bias where a model rationalizes its own prior errors.

### Layer 2: Deterministic Harness Safety Sandbox

Upon passing Layer 1, $Prop$ enters a hardcoded software harness written in standard deterministic code (e.g., Python/Rust). The harness independently validates the payload against operational rules:

1. **Role-Based Access Control (RBAC):** Validates user credentials against session identity tokens.
2. **Boundary & Limit Verification:** Enforces transfer limits, maximum payload sizes, and parameter schema types.
3. **State Verification:** Checks real-time database preconditions (e.g., sufficient account balance).

Only when all hardcoded checks pass does the harness construct and execute the final API/database call:

$$Cmd = \text{DeterministicHarness}(Prop)$$

---

## Summary of Architectural Traceability

| Subsection & Mechanism | Target Requirement | Operational Realization |
| --- | --- | --- |
| **2.1 Microsecond Pre-Router** | **White-Box Auditability** | Edit/Graph distance algorithm; prior probability $P_{\text{intent}}$ in $<5 \text{ ms}$. |
| **2.2 Calibrated Risk Gates** | **Risk-Proportional Authorization** | Asymmetric gates ($\tau_{\text{read}} = 0.65$, $\tau_{\text{write}} = 0.99$); Dynamic HCI option chips. |
| **2.3 Intent Proposal Engine** | **Zero Execution Authority** | Unprivileged JSON proposal generation ($Prop$); zero execution handles. |
| **2.4 Heterogeneous Verification** | **Orthogonal Verification** | Dual-pass check: Isolated Validator Agent + Hardcoded Runtime Harness ($Cmd$). |

---

# 3. Comparative Analysis of Architectural Approaches

To evaluate the operational resilience of the proposed architecture, we compare it against traditional "All-LLM" agent designs across six critical software reliability engineering (SRE) dimensions.

Whereas traditional architectures treat the LLM as an end-to-end autonomous controller, the proposed design encapsulates the neural model as an unprivileged component within a deterministic state machine.

| Dimension / Feature | Traditional All-LLM Agent Architecture | Proposed Deterministic Harness Architecture | Architectural Traceability & Advantage |
| --- | --- | --- | --- |
| **3.1 Primary Intent Routing** | **LLM Self-Assessment:** Black-box neural routing pass; high token latency; susceptible to hallucinated tool matches. | **Microsecond Pre-Router (Mechanism 3):** White-box algorithmic matching (Levenshtein, Jaro-Winkler, Trie, Graph Distance). | Eliminates token costs on invalid inputs; guarantees sub-5ms routing latency and 100% deterministic decision logs. |
| **3.2 Execution Privilege Level** | **Direct Authority:** Model holds live API credentials, DB connection handles, or shell execution rights. | **Zero Execution Authority (Mechanism 1):** Model outputs unprivileged JSON Intent Proposals ($Prop$) only. | Zero blast radius. Hallucinated payloads cannot execute natively without harness sandbox validation ($Cmd$). |
| **3.3 Validation Engine** | **Homogeneous Self-Reflection:** Re-evaluates output within the same context window or parameter space. | **Heterogeneous Orthogonal Validation (Mechanism 2):** Isolated Validator Agent + Hardcoded RBAC/Limit Sandbox Harness. | Breaks error correlation. Prevents the model from using identical weight parameters ($W$) to rationalize initial mistakes. |
| **3.4 Risk Governance** | **Static / Symmetric Evaluation:** Applies uniform execution logic regardless of transaction liability. | **Asymmetric Risk Gates (Mechanism 4):** Dynamic confidence thresholds ($\tau_{\text{read}} = 0.65$, $\tau_{\text{write}} = 0.99$) + Dynamic HCI option chips. | Prevents high-liability state-changing errors ($C_{FP}(\text{Write}) \gg C_{FP}(\text{Read})$) while optimizing read-path latency. |
| **3.5 Auditability & SRE Testing** | **Opaque / Probabilistic:** Black-box latent inference paths cannot be unit-tested or reproduced. | **100% White-Box Audit Trail:** Pre-router distance metrics and harness validation logs are fully unit-testable. | Meets strict regulatory compliance standards (e.g., FINRA, SEC, HIPAA) by providing deterministic proof of execution boundaries. |
| **3.6 Disaster Recovery (Failover)** | **Cold Conditional Prompts:** Fallback paths rely on complex prompt branches that remain unexercised during normal operations. | **Pre-Warmed HITL Pipeline:** Continuous low-confidence traffic exercises human queues; instant fallback via $P_{\text{threshold}} \to 1.00$. | Guarantees zero-blast-radius emergency failover without cold-start failures or unmonitored circuit breakage. |

---


# 4. System-Level Benefits: Regulatory Alignment and Disaster Recovery

Deploying AI systems in mission-critical environments requires compliance with legal frameworks and integration with standard enterprise disaster recovery (DR) protocols.

```
                                [ NORMAL OPERATION ]
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        │                                                                 │
        ▼                                                                 ▼
[ High Confidence Traffic ]                                   [ Low Confidence Traffic ]
(P_intent ≥ Threshold)                                        (Ambiguous / Marginal)
        │                                                                 │
        ▼                                                                 ▼
[ Autonomous Execution Harness ]                              [ Active HITL Pipeline ]
                                                              (Continuously Exercised)
                                                                          ▲
                                                                          │
                                [ EMERGENCY STATE ]                       │
                                         │                                │
                        [ Global Threshold Override: ]                    │
                        [      P_threshold ──► 1.00  ] ───────────────────┘
                                                        (Instant Seamless Failover)

```

## 4.1 Regulatory Auditability and Deterministic Governance

Regulatory bodies in financial services and healthcare enforce strict requirements regarding software governance:

1. **Verifiable Execution Logic:** Every state change must be traceable to a specific, deterministic authorization rule.
2. **Reproducible Test Coverage:** Systems must support automated unit and regression testing where identical inputs yield identical outputs.
3. **Bounded Failure States:** Systems must prove an explicit upper bound on potential transactional loss.

By extracting intent routing into **Mechanism 3 (Microsecond Pre-Router)** and parameter validation into **Mechanism 2 (Deterministic Sandbox Harness)**, the architecture satisfies these requirements:

* **The Black Box is Bounded:** Probabilistic reasoning is constrained to data transformation and parameter extraction ($Prop$).
* **The Control Plane is White Box:** Routing decisions, privilege verification, and parameter limit enforcement ($Cmd$) are executed by standard, deterministic software modules that generate 100% reproducible audit logs and run within standard CI/CD unit testing frameworks.

---

## 4.2 Unified Control Plane & Pre-Warmed HITL Failover

A primary vulnerability in software disaster recovery is the **Cold Failover Paradox**: backup recovery circuits that remain unexercised during normal operations frequently fail when abruptly triggered during an emergency.

To eliminate this vulnerability, the proposed architecture integrates Human-in-the-Loop (HITL) workflows directly into daily baseline operations:

### Baseline Operation (Continuous Warm State)

Under normal operational conditions, queries yielding marginal prior confidence ($P_{\text{intent}}$ in the ambiguous region) automatically route to the HITL interface via **Mechanism 4 (Dynamic HCI Option Chips)**. This ensures that:

* Human operator queues, administrative UI interfaces, and authorization pathways remain continuously active and validated.
* System telemetry continuously measures human response SLAs and queue drain rates.

### Emergency State (Instant Circuit Breaker)

In the event of an upstream model provider outage, severe latency degradation, or suspected adversarial prompt injection attack, system administrators adjust the global routing threshold configuration:

$$P_{\text{threshold}} \to 1.00$$

Adjustment of this single parameter instantly re-routes **100% of incoming system traffic** directly into the active HITL pipeline.

### Zero Blast-Radius Advantage

Because the failover path is identical to the baseline ambiguous traffic path, the transition incurs **zero cold-start latency**, requires no unmonitored circuit switching, and guarantees that no non-deterministic commands reach execution engines during system anomalies.

---

## 4.3 Graceful Recovery and State Reconciliation

When upstream services recover or threat conditions clear, administrators dynamically adjust $P_{\text{threshold}}$ back to baseline operational parameters ($\tau_{\text{read}} = 0.65, \tau_{\text{write}} = 0.99$).

```
[ Active Emergency Failover (P_threshold = 1.00) ]
                        │
                        ▼ Restores Threshold Config
[ Dynamic Traffic Redistribution (Tau_read = 0.65, Tau_write = 0.99) ]
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
[ Autonomous Execution ]      [ Baseline HITL Queues ]

```

* **Zero Service Interruptions:** Traffic redistributes automatically according to transaction risk profiles without requiring application restarts, container redeployments, or state cache clearing.
* **Deterministic Transaction Log Integrity:** Because all proposals ($Prop$) and executed commands ($Cmd$) maintain explicit, immutable database trace IDs throughout both normal and emergency states, post-incident auditing requires zero state reconciliation or manual database repair.

---

# 5. Conclusion

Building resilient enterprise AI systems requires accepting the fundamental mathematical reality of Large Language Models: **they are auto-regressive probability engines, not deterministic execution controllers.** Attempting to eliminate hallucinations or guarantee safety purely through empirical prompt engineering is an architectural category error.

By encapsulating probabilistic models within a deterministic software harness—employing algorithmic white-box pre-routing, enforcing zero execution authority, requiring orthogonal verification, and applying asymmetric risk gates—this architecture establishes a provable, auditable, and operationally stable blueprint for deploying Generative AI into safety-critical enterprise environments.