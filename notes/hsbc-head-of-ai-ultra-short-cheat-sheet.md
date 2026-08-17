# HSBC Head of AI Ultra-Short Cheat Sheet

## Core Goal

Do not show that you know a lot.

Show that you can:

- think independently
- frame the real problem
- give a clear opinion
- connect AI to banking constraints

---

## What He Likely Wants

Not a polished resume answer.

He wants to see whether you have:

- real ideas
- real judgment
- real tradeoff awareness
- useful opinions under constraints

---

## Main Strategy

For each question:

1. answer directly
2. reframe one level deeper
3. take a position
4. give one implication

Simple formula:

> My short answer is...
>
> The deeper issue is...
>
> My bias is...
>
> The implication is...

---

## Three-Part Frame

Use this for broad questions:

> I tend to think about this in three layers: control architecture, ROI, and the engineering operating model around AI.

### 1. Control Architecture

- bank AI is a control-plane problem before it is a capability problem
- read-only and state-changing workflows should not share the same trust model
- proposal inside the model, authority outside the model
- for hard cases, AI can analyze and present evidence while humans keep decision authority
- treat RAG, intent recognition, and API calls as tools in a central registry for trace and audit
- use orthogonal confidence checks, not only LLM self-judgment
- structured user confirmation can improve both control and UX
- escalation paths also create clean samples for future improvement

### 2. ROI and Operating Economics

- a successful demo is not enough
- the real question is whether the system can produce a predictable bill and a predictable operating outcome
- retries, latency, review burden, and hidden agent loops can kill enterprise value
- strong outer harnesses help bound worst-case cost
- splitting workflows into simple steps lets you use flash models where possible
- modular pipelines make caching practical and can materially reduce cost

### 3. AI-Era Engineering Method

- AI makes coding cheaper, but boundary-setting more valuable
- the scarce talent is people who can define specs, control logic, and production discipline
- prototype logic and production logic should not be mixed
- clean repo structure helps control AI search space and blast radius
- repeat is often better than abstract too early
- abstraction should follow repeated reality, not imagined reuse

---

## Good Opening

> Given HSBC's environment, I imagine the hard part of LLM deployment is not model capability itself, but satisfying HKMA expectations and internal control requirements. I am curious which part has actually been the biggest bottleneck in practice.

---

## Tiny Scenario Map

- if he asks about governance, hallucination, agents, explainability: use `Control Architecture`
- if he asks about value, scaling, prioritization, adoption: use `ROI and Operating Economics`
- if he asks about talent, AI coding, team structure, execution style: use `AI-Era Engineering Method`

Cost examples to remember:

- outer harness bounds retry cost and worst-case fee
- intent recognition can often use small or flash models
- clean retrieval means synthesis may not need a premium model
- modular intent layers are cache-friendly
- fail fast early to avoid wasting downstream tokens

Control examples to remember:

- AI helps human agents by summarizing, highlighting risk, and quoting evidence
- central tool registry improves governance and ownership
- retrieval and intent layers should have deterministic proxy gates in production
- offline evaluation can use ground truth; production often needs proxy metrics
- one extra clarification turn is often better than a fast wrong answer
- use lightweight structured confirmation before escalating to humans

AI coding examples to remember:

- split repo into platform, utils, and feature to limit AI blast radius
- platform code needs the highest review bar
- do not abstract on the first example just because AI makes coding fast
- blast-radius control is both software robustness and business continuity
- unified design makes fallback data reusable for system upgrades
- modular design improves fault isolation and graceful degradation
- modular building blocks make the system extensible without rebuilding from scratch

---

## Best Phrases To Use

- My bias is that...
- The real issue is...
- I would separate this into three cases...
- I think the common mistake is...
- In a bank, I would optimize for control before capability.
- That works for a demo, but production is a different question.

---

## 6 Strong Default Answers

### Hardest part of bank LLM deployment?

> Not capability. The hardest part is forcing a probabilistic system to operate inside deterministic institutional boundaries.

### Where do banks get AI wrong?

> They often use one trust model for all use cases. That is the wrong abstraction.

### Autonomous agents in banking?

> Yes, but only as bounded autonomy. I would not give high-liability actions direct model authority.

### How would you design it?

> Deterministic routing, risk classification, model proposal, orthogonal verification, then deterministic execution or human approval.

### How do you use AI in high-risk workflows without over-trusting it?

> In harder cases, I prefer AI to do the analysis work and present structured evidence to the human agent, rather than make the final decision. That improves productivity without collapsing accountability.

### How do you think about fail-fast behavior?

> I prefer to fail fast at the intention or retrieval layer if the system has not earned the right to proceed. One extra clarification turn is usually cheaper than a fast wrong answer that damages trust and creates downstream cost.

### How do you think about ROI?

> The real question is whether the system can produce a predictable bill and a predictable operating outcome.

### How do you control cost in practice?

> I try to control cost through architecture, not only through model choice: bounded retries in the outer harness, cheap models for narrow steps like intent recognition, smaller synthesis models when retrieval is already clean, and modular caching where the query distribution is repetitive.

### What changes about engineering talent?

> The scarce talent shifts from pure coding throughput to people who can define boundaries, specs, and control logic.

### What changes about coding practice in the AI era?

> I think structure matters more. Clean repo boundaries help control what AI touches, and I prefer repeat over abstract too early because AI makes over-engineering easier, not harder.

### What is your overall view on AI in banking?

> I see it in three layers: control architecture, ROI, and the engineering operating model around AI.

---

## If He Pushes Back

Use:

- That is fair.
- I agree there is a tradeoff there.
- I would handle that differently for low-risk and high-risk workflows.
- My view would change if the use case were narrower.

---

## What To Avoid

- long speeches
- generic AI hype
- sounding like a memorized article
- answering beyond the question
- trying too hard to sound smart

---

## Final Mental Model

Your articles are the raw thinking.

The interview is not about repeating them.

It is about converting them into useful judgment for the exact question he asks.

---

## Final Line To Remember

> The goal is not to prove I am smart. The goal is to make him feel I would be useful in a serious bank AI deployment discussion.
