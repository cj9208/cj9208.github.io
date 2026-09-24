---
title: "Good System Design and Good Presentations Both Hide Complexity"
date: 2026-09-24T00:18:35+08:00
lastmod: 2026-09-24T10:15:00+08:00
draft: false

categories:
  - "AI Study"
tags:
  - "Architecture"
  - "LLM"
  - "Harness Engineering"

slug: "good-system-design-and-good-presentations-both-hide-complexity"
---

In presenting technical work, a common failure is to treat displayed complexity as proof of capability. Framework names fill the slides, layers fill the diagrams; after a thirty-minute talk the audience cannot say what problem the work solves, and something that demos smoothly can still fail in production. AI projects, with terms like multi-agent orchestration, dynamic RAG, and context engineering, are the most visible example today.

Good system design puts complexity inside the system. The hard work stays in the code, the user sees clear behavior, and the business gets predictable results. Good presentations reduce the cognitive load on the audience. The two are the same discipline, applied at two different points.

## 1. Abstraction: Encapsulation, Not Concealment

There is a false kind of abstraction: it displays complexity to cover thin substance. The clearest case I know is the OCBC AI Lab paper *Detection, Attribution, Narration: An End-to-End Pipeline for Explainable Money Mule Identification* ([arXiv:2607.17586](https://arxiv.org/abs/2607.17586)). The falseness there has two parts: a false name and a false problem.

The name is false. The title claims an end-to-end system, but the pipeline is three modules in sequence plus a human review at the end: a LightGBM classifier flags suspicious accounts, TreeSHAP values list the features behind each flag, and a large language model turns those fields into a narrative for the investigator. The talk made this worse by reporting 5.7 seconds as a latency. Latency is a real-time word: it promises a system that answers while the transaction is still open. The paper's own table says no such thing. The number there is the inference time of the narration model for one alert, measured in after-the-fact triage, where nothing waits on it. An audience that trusts the frame understands neither the technology nor the problem. In that talk, I was that audience.

The problem is false in the same way. The deliverable is a paragraph of review opinion for a human investigator, written from fixed fields. In function, this is a controlled translation task. A template engine such as Jinja could render each attributed feature into its risk sentence, at least as reliably, and it would add no failures of its own. Put honestly, the paper is a classifier with a narrative front end. The everyday engineering form of this is an API call plus a prompt plus a human clicking confirm, presented as if the system did the work end to end. Same structure in both: the complexity is not gone; what it hides is the absence of substance.

Real abstraction organizes a messy situation into a clear model and keeps the complexity inside the system. Prompt-only engineering is an open loop, like a toaster that heats for a fixed time regardless of whether the bread is done or burning. A production agent harness must be a closed loop, like a thermostat: it measures, compares with the target, and adjusts. The [From Prompts to Autopilot](https://cj9208.github.io/blog/ai_study/harness-engineering/from-prompts-to-autopilot-why-harness-engineering-is-the-true-key-to-llm-reliability/) article develops this control-loop mapping in full. The consequence for presentations is direct: an encapsulated system shows the user only a small interface, so slides full of internals mean the interface has not been thought through.

## 2. Presentation: Reducing the Audience's Cognitive Load

The example I know best is my own. I built a personal knowledge system and wrote it up in [Technology Comes Last](https://cj9208.github.io/blog/ai_study/blog-system-evolution/). The article opens with a friend who spent months choosing a perfect architecture and shipped nothing. It then names the value my own system protects: one scarce resource, the momentum of thinking. Technology arrives only in the last third of the article, and each layer enters as the fix for a break I had actually observed.

The article carries two slide decks, and the split between them is the small-interface rule applied to two audiences. [AI-Augmented Personal Blogging](/blog-system-evolution/AI-Augmented-Personal-Blogging-2026-Sep-20.pdf), 8 pages, is for the business side: what the system is for, what problem it solves, and what it gave back. [My Personal Knowledge Engine](/blog-system-evolution/My-Personal-Knowledge-Engine.pdf), 12 pages, is for technologists: the three index layers, the design logic behind them, and how they map onto a production RAG stack — with the purpose restated so the internals stay answerable to it. Each deck exposes what its audience needs to judge, and hides the complexity that judgment does not require.

Two decks are not the only way to keep value and technology apart. A single deck for both audiences can separate them in time: what the system does and what it gave back first, then the technology choices, why they were made, and their effect — each technical section answering a value stated earlier. The failure is not a mixed audience but mixed content: internals scattered through the value story leave the business side unable to follow and technologists unable to judge. The paper's talk in §1 is this failure in miniature: "end-to-end" was the wrong word for three modules in series, and worse, the modules were presented one by one without the problems they solve, so the audience was shown technology but given no value to judge.

That is the rule. You do not prove yourself with complexity. You prove yourself with value. State what the system protects and what it lets break, and the audience can ask sensible questions about the rest.

## 3. Depth Shows as Containment, Not Enumeration

With the complexity out of sight in both the system and the slides, what is left to show? Depth — and depth shows as the match between a real problem and the mechanism that solves it. A simple method that solves a big problem is the best thing a speaker can show: no design is too plain when the problem behind it is large. What costs trust is a speaker who cannot say what problem the design solves; a long list of layers with no problem on it proves nothing. The problem comes first; the mechanism answers it.

**Context governance.** Multi-turn tasks degrade through context rot and rising token cost. The response is layered memory management: keep prompt prefixes stable for caching, keep progress records outside the conversation, run dense exploration in sub-agents that discard their logs and return only validated results, and load tools only when needed. The design is set out in [The Systems Engineering of LLM Context Management](https://cj9208.github.io/blog/ai_study/harness-engineering/the-systems-engineering-of-llm-context-management/), and the reason for concentrating design effort on context in [The Algorithm of Compute](https://cj9208.github.io/blog/ai_study/harness-engineering/the-algorithm-of-compute-why-modern-agent-harnesses-focus-80-of-their-design-on-context-management/).

**Staged deterministic defense.** When model output is malformed or wrong, blind retries are expensive and rarely converge. The alternative is a five-layer degradation strategy: local repair in milliseconds, schema validation, one retry on a cheap model, escalation to a stronger reasoning model, and finally a human interrupt. Each layer is detailed in [Harness as an OS](https://cj9208.github.io/blog/ai_study/harness-engineering/harness-as-os-reasonix/).

**The comparator problem.** In finance, law, and medicine, nothing can decide in one second whether a clause edit has silently voided a disclaimer. Code has native comparators for this — the compiler and the tests — but these domains have no equivalent, and having a model judge its own output produces confirmation bias. Production harnesses use proxy simulators and hard invariant constraints instead. The harness does not produce the answer; it removes the answers that are certainly wrong, and the value is the size of what is left: no human can check a million candidate answers, but ten can be checked by hand. The system does not need to understand the law; it only needs to reject out-of-contract output deterministically. See [The Comparator Trap](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/).

That is the pattern. The problem arrives first; the mechanism answers it. Depth is the fit between them, not the size of the machinery.

## 4. Conclusion

The shared principle is simple outside, complex inside. The designer digests the complexity inside the system and gives the user an interface with clear behavior. The presenter digests it in preparation and gives the audience a clear model, instead of terms and diagrams. Both come from the same demand: solve real production problems, not the demo. The failure this protects against has the same root: a team that has not mastered the engineering essentials of what it builds falls back on jargon and on claims of end-to-end automation.

## Further Reading

**Harness Engineering series**

- [From Prompts to Autopilot](https://cj9208.github.io/blog/ai_study/harness-engineering/from-prompts-to-autopilot-why-harness-engineering-is-the-true-key-to-llm-reliability/): the open-loop/closed-loop control framing behind §1.
- [The Algorithm of Compute](https://cj9208.github.io/blog/ai_study/harness-engineering/the-algorithm-of-compute-why-modern-agent-harnesses-focus-80-of-their-design-on-context-management/) and [The Systems Engineering of LLM Context Management](https://cj9208.github.io/blog/ai_study/harness-engineering/the-systems-engineering-of-llm-context-management/): the context design summarized in §3.
- [Harness as an OS](https://cj9208.github.io/blog/ai_study/harness-engineering/harness-as-os-reasonix/): the five-layer degradation strategy cited in §3.
- [The Comparator Trap](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/): why high-stakes domains lack comparators.
- [A First-Principles Architecture for Agent Routing and Safety Harnesses](https://cj9208.github.io/blog/ai_study/agent-routing-safety-harness/): the same principles as a first-principles derivation.