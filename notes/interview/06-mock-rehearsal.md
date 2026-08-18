# 06 — Mock Rehearsal（演练）

> 面试前一天朗读演练。对应旧版 `Director-Level-Mock-Interview-QA.md` + prep 的 Final Reminders。

## 怎么用本页

- 先用自己话说出来，再看参考答案收紧结构，不要逐字背
- 大多数答案控制在 30–90 秒
- 追问更深就分支到 `03` 的深潜 A/B
- 结尾用红标记清单检查弱框架

## Opening Questions（开场题）

### Tell me about this design.

> We started with a practical retrieval problem. User requests were often messy, ambiguous, or underspecified, which hurt retrieval quality and wasted downstream cost. So I first designed an intention-recognition layer that does deterministic cleanup, lightweight interpretation, confidence-aware clarification, and graceful fallback.
>
> The bigger insight was that this should not stop at retrieval. Once a system can decide whether a request is clear enough to proceed, it is already becoming the front half of a broader orchestration layer. In that design, RAG becomes one capability rather than the default path.
>
> The key boundary is that the model proposes, but the harness decides. The harness owns permissions, policy, risk, and execution control. Today the strongest implemented part is the intention-recognition layer, and the orchestration layer is the path for growing that into a governed platform over time.

### What problem were you really trying to solve?

> At first glance it looked like a retrieval-quality problem, but the deeper issue was poor request conditioning. If the request is messy or ambiguous, better retrieval is often just a more expensive way to process bad input. So the real problem was how to improve request quality and keep execution governed before expensive downstream steps begin.

### Why is this a director-level story and not just a feature story?

> Because the value is not only the local fix. The stronger part is recognizing the right control boundary, turning that into a reusable pattern, and showing how it could scale across domains with clearer governance, ownership, and operating rules. That moves it from feature work into platform and organizational design.

## Architecture Questions（架构题）

### Why did you start with intention recognition?

> Because it was the earliest useful control point. Many downstream RAG problems were really upstream input problems. If I could clean, interpret, or clarify the request early, I could improve quality without forcing a large rewrite of the rest of the pipeline.

### Why not just improve RAG directly?

> Better RAG still assumes retrieval is the right path. The deeper issue was that some requests should be clarified, some should be rerouted, and some should never enter RAG at all. So I treated request conditioning as the earlier and more important control problem.

### Why use layers?

> The layers are not just for clean diagrams. They create fail-fast boundaries, evaluation points, and ownership boundaries. That makes it much easier to stop bad requests early, measure where quality is failing, and avoid pushing every problem downstream.

### When did you realize this was becoming orchestration rather than just preprocessing?

> The key moment is when the system is no longer only cleaning input, but deciding whether to clarify, retrieve, call a tool, or escalate. At that point it is acting as a control layer, not just a preprocessing step. That is what makes the abstraction shift from better RAG to request orchestration.

## Governance Questions（治理题）

### What is the most important boundary in the design?

> The most important boundary is that the model proposes, but the harness decides. The model can help with reasoning, but it should not directly own permission, policy, risk, or execution. Those need to stay in software policy outside the model.

### Why do you need a harness instead of just a better prompt?

> Prompts can shape model behavior, but they do not enforce permission checks, schema validity, confirmation rules, or auditability. Those are runtime controls, so they need to live in the harness.

### Why split by domain instead of building one general agent?

> One general agent sounds simpler, but it creates too much ambiguity in routing, retrieval scope, permissions, and debugging. Domain scoping keeps each execution surface smaller and easier to govern, while the shared orchestration layer keeps the control pattern consistent.

### How do you handle risky actions?

> The model can propose a structured action, but the harness checks identity, permission, and risk before anything executes. Low-risk actions can run directly. Higher-risk actions require confirmation or are rejected. The important part is that the model never becomes the final authority.

## RAG And Economics Questions（RAG 与经济题）

### Why does upstream conditioning matter so much economically?

> Because the savings compound across multiple stages. Fewer bad requests enter RAG, the requests that do enter are cleaner, retrieval brings back less noise, the context window gets smaller, and more cases can run on cheaper models. So the gains can be multiplicative rather than additive.

### How do you talk about the `80x` example without overclaiming?

> I would frame it as a directional systems argument, not a forecast. The point is not the exact number. The point is that upstream conditioning changes several cost drivers at once, so the leverage can compound.

### Why does this improve user experience, not just cost?

> Because ambiguous requests get clarified earlier, noisy requests stop producing bad retrieval, and the answering stage works from cleaner context. So users get better path selection and better answer quality, not just lower runtime cost.

### Why does this make the system easier to build?

> Because once noisy and ambiguous cases are handled earlier, each downstream module can stay narrower. Retrieval can focus on finding evidence, grounded answering can focus on citation and synthesis, and prompts do not have to compensate for every upstream failure mode at once.

## Maturity And Execution Questions（成熟度与执行题）

### What is implemented today versus what is still a direction?

> The strongest implemented part is the intention-recognition layer and the control logic around early clarification. The broader orchestration layer is the architecture direction. I would be explicit that the value today is strongest in the upstream control boundary, while the longer-term path is governed capability routing and execution.

### How would you phase this with a small team?

> I would phase it in. First harden intention recognition and clarification policy. Then add domain routing and capability registry structure. Then introduce governed tool execution behind the harness. Finally add stronger observability, review loops, and operational thresholds. That gives near-term value while building toward the broader platform.

### What are the biggest risks or gaps?

> The biggest gaps are operational rather than conceptual. Confidence calibration still needs formal rules. Evaluation depth and regression coverage need hardening. Alert thresholds, runtime triage, and onboarding rules for new capabilities also need more work.

### How would you measure success?

> I would split metrics across routing quality, execution quality, efficiency, and safety. That keeps ownership explicit and makes it easier to see whether a problem came from request understanding, routing, policy enforcement, tool behavior, or grounded answering.

## Leadership Questions（领导力题）

### What leadership judgment does this design show?

> The main judgment is solving the narrow real problem first, then generalizing only after the control pattern proves useful. It also shows that I think about governance, ownership, and rollout at the same time as architecture, rather than treating them as cleanup work later.

### How would this help multiple teams, not just one workflow?

> The shared value is the control pattern. Different teams can own different domains or capabilities, but they can inherit the same request handling, validation, routing, permission, and escalation model. That reduces duplicated platform and compliance work across teams.

### If you did not have full implementation authority, how would you talk about your contribution?

> I would focus on architectural ownership. I identified the failure mode, reframed the problem, defined the control boundary, and laid out a realistic phased path. Even if broader execution depended on sponsorship beyond my direct scope, the design work still shaped the technical direction.

## Adversarial Questions（对抗题）

### This sounds like you took a simple RAG issue and wrapped a lot of architecture around it. Why is that not overengineering?

> That would be a fair concern if I had started with a big platform rewrite. I did not. I started with the narrowest useful fix: intention recognition in front of the existing RAG path. The broader orchestration framing came only after the control pattern became clear. So the sequence was solve the real local problem first, then generalize only after the boundary proved useful.

### How do you know this is the right abstraction and not just a story you built after the fact?

> I would defend it based on the failure mode. The recurring problem was not only retrieval quality. It was ambiguity, poor request conditioning, and weak control over what happened next. Once the system needs to decide whether to clarify, retrieve, call a tool, or escalate, that is already an orchestration problem. So the abstraction follows the runtime decisions the system actually has to make.

### If the orchestration layer is mostly a direction, are you overclaiming the maturity of the design?

> I would be careful not to overclaim it. The strongest implemented part is still the intention-recognition layer. What I am claiming is that the architectural direction is strong, the control boundary is clear, and the rollout path is realistic. I would separate current implementation from future platform direction very explicitly.

### Why should anyone believe the economics if you do not have precise numbers?

> I would not ask them to believe a precise multiplier. I would ask them to evaluate the systems logic. If fewer bad requests enter RAG, retrieval returns less noise, context gets smaller, and cheaper models become viable more often, then the savings compound across multiple stages. The exact number needs measurement, but the shape of the leverage is still real.

### Why not just fix the prompts and move on?

> Better prompts can help, but they do not solve the control problem. They do not tell you whether the request should enter RAG at all, they do not enforce permission or risk policy, and they do not create clear ownership boundaries. Prompt tuning is useful inside the system, but it is not the system design.

### This sounds like standard industry thinking. What is actually distinctive about your contribution?

> I would not claim every component is novel. The distinctive part is the synthesis and the boundary placement. I followed the failure upstream, put the deterministic control boundary there, separated reasoning from authority, and turned a local RAG fix into a reusable orchestration pattern. That combination is the contribution, not the claim that I invented each ingredient.

### Why not build one strong agent and let it learn the routing itself?

> Because that pushes too much responsibility into the least governable part of the system. It increases ambiguity in routing, widens the permission surface, and makes failures harder to localize. A shared control plane plus domain-scoped execution is slower to design, but much easier to govern and operate.

### If I were your manager, how would I know this is better than just shipping a narrow fix and stopping there?

> The narrow fix is still worth shipping. I am not arguing against that. The additional value is that the same boundary can be reused across domains, which reduces duplicated platform work and gives a cleaner operating model over time. So the real choice is not narrow fix versus platform. It is narrow fix only versus narrow fix plus a credible path to reusable control.

### What is the weakest part of your argument?

> The weakest part today is not the conceptual model. It is the operational hardening. Confidence calibration, regression depth, alert thresholds, and domain onboarding rules still need more work. I would rather say that directly than pretend the hard part is already finished.

### What would make you change your mind about this design?

> If the real failure mode turned out not to be upstream ambiguity, or if domain differences were too small to justify scoped execution, then I would simplify the design. I am attached to the control goals, not to adding layers for their own sake. If a simpler structure solved the same governance and quality problems, I would prefer the simpler structure.

### Why are you talking so much about governance and control? Could that make you sound too defensive or slow-moving?

> I would frame it as production realism, not fear. In AI systems, reasoning quality matters, but so do permissions, auditability, and failure containment. Governance is what makes the system safe to scale beyond a demo. I still care about speed, which is why the rollout starts with a narrow practical fix rather than a full platform build.

### If another leader said, "This is interesting, but I still do not see the business value," what would you say?

> I would make it concrete: better request conditioning reduces wasted retrieval cost, improves answer quality, reduces bad user experiences, and gives teams a shared control pattern instead of each team rebuilding its own safety and routing logic. So the value is not only technical elegance. It is better quality now and lower duplicated platform cost later.

## Closing Practice（收尾练习）

### What is the one sentence you want them to remember?

> I started by fixing messy upstream requests hurting RAG, then realized that the same control boundary naturally generalizes into governed request orchestration, with the harness as the authority boundary.

## 常见红标记（Common Red Flags）

### 一上来堆术语

坏：`I designed an agent platform with orchestration, adaptive tool loading, governance, and RAG.`
好：`We started with a practical retrieval problem. User requests were often messy or ambiguous, which hurt quality and wasted downstream cost.`

### 把 RAG 当一切中心

坏：`The whole system is basically a better RAG architecture.`
好：`RAG was the original problem area, but the deeper issue was governed request execution. That is why the design grows into orchestration rather than stopping at retrieval.`

### 夸大成熟度

坏：`We built a governed orchestration platform for the company.`
好：`The strongest implemented part is the intention-recognition layer. The orchestration layer is the broader architecture direction and rollout path.`

### 混淆推理与权威

坏：`The model decides which actions to take and then executes them.`
好：`The model proposes, but the harness decides. Permission, policy, risk, and execution control stay outside the model.`

### 只讲组件不讲决策

坏：`There is an intention layer, an orchestration layer, a RAG layer, a harness layer, and a tool layer.`
好：`I split the system into layers to create fail-fast boundaries, evaluation points, and cleaner ownership. The structure matters because it stops bad requests early and makes failures easier to localize.`

### 听起来第一天就想要平台

坏：`The goal was to build a general orchestration platform.`
好：`I started with the narrowest useful fix. The platform direction only became clear after the upstream control boundary proved useful.`

### 经济框架弱

坏：`It saves a lot of money because the architecture is smarter.`
好：`The leverage comes from changing several stages at once: fewer bad requests enter RAG, cleaner ones retrieve less noise, context gets smaller, and cheaper models become viable more often.`

### 把 `80x` 当承诺

坏：`This design gives around 80x savings.`
好：`I would treat that as a mental model, not a forecast. The point is that the savings can be multiplicative because they happen at different layers of the pipeline.`

### 回避硬缺口

坏：`The main thing left is just implementation detail.`
好：`The biggest remaining work is operational hardening: confidence calibration, regression depth, alert thresholds, runtime triage, and onboarding rules for new capabilities.`

### 没有归属模型

坏：`The platform would just support multiple teams.`
好：`I would keep the control plane shared, while domain teams own their capabilities, policies, and corpora. That gives consistency without turning everything into one central bottleneck.`

### 抽象太久

坏：`I think system design is about boundaries, contracts, validation, state, control, and governance.`
好：`In this case, the principle showed up as intention recognition before RAG and the harness as the authority boundary. That is how the abstract idea became an actual architecture choice.`

### 只以 IC 身份回答

坏：`I designed the architecture and the components in the flow.`
好：`The design matters technically, but the more senior part is the operating model around it: how to phase it, how to govern it, how to split ownership, and how to reduce duplicated work across teams.`

### 显得过于确定

坏：`This is definitely the right architecture.`
好：`I think this is the right design for the failure mode we observed. If the real bottleneck turned out to be somewhere else, I would simplify accordingly.`

### 起手失败后的补救

> Let me restate that more clearly. The actual problem was not just retrieval quality. It was poor request conditioning and weak control over what happened next. That is why the design starts with intention recognition and grows into orchestration.

## 面试前最终清单

- 准备并练熟 3 个核心观点：控制面先于能力 / 可预测账单 / 边界设定比编码更值钱。
- 检查回答是否：从真实失败模式开始 → 解释首个实用修复 → 展示 RAG→orchestration 的抽象迁移 → 明确 harness 边界 → 区分当前实现与未来方向 → 提到归属/rollout/治理 → 避免膨胀数字或平台夸大 → 先具体后哲学。
- 避免：长独白、上来堆术语、泛泛 hype、答非所问、试图显得聪明；组织层与经济层的缺口都要诚实限界。
- 结束后他记住的不是你的知识量，而是「这个人有判断力」。
