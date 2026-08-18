# 05 — Scripts & QA（开场 / 高频题 / 话术库）

> 面试现场直接检索。对应旧版 fast-recall §2/§9–§12 + prep 的 Opening/Q&A/One-Liners + ultra-short 的 Default Answers。

## 开场

**通用版（面 Solution Lead / Architect 岗）：**

> I imagine the hard part of deploying LLM systems in an enterprise is not model capability itself, but satisfying governance, control, and audit expectations while keeping the operating cost predictable. I am curious which part has actually been the biggest bottleneck in practice.

**银行版（面 HSBC/渣打等）：**

> Given HSBC's environment, I imagine the hard part of LLM deployment is not model capability itself, but satisfying HKMA expectations and internal control requirements. I am curious which part has actually been the biggest bottleneck in practice.

开场三要素：从对方运营现实出发 + 抛一个假设 + 请对方讲真正的瓶颈。

为什么银行版开场强：从对方现实出发、展示商业与监管意识、避免像泛泛 AI 爱好者、自然引出你的架构观点。

## 高频题速答（一句话版）

| 问题 | 一句话答案 |
|---|---|
| 银行部署 LLM 最难的是什么？ | 不是能力，是把概率系统塞进确定性机构边界（执行权/数据边界/审计/风险分级） |
| 银行哪里做错了？ | 一个信任模型套所有场景；为 pilot 庆祝却没证明治理契合与单位经济 |
| 信 autonomous agents 吗？ | 只信有界自主：模型提议/分解/提参，确定性系统握权限、校验、最终提交 |
| 怎么设计受监管工作流？ | 分层：确定性路由→风险分类→模型提议→正交校验→确定性执行或人工批准 |
| 先做哪些用例？ | 读为主、高频、低责任；避免直接上 state-changing |
| ROI 怎么看？ | 可预测账单 + 可预测运营结果；质量之外的 retry/延迟/复核都是成本 |
| 可解释性？ | 控制路径可解释（为什么放行/拦截/路由）比解释权重更实用 |
| hallucination 怎么处理？ | 当永久属性来架构化处理：约束输出、限权、读写分离、确定性检查 |
| 模型变强后控制会不需要吗？ | 不会；更强反而增加 over-trust，治理架构更重要 |
| 人才怎么变？ | 编码吞吐贬值，定边界/规范/决策规则的人升值 |
| 你的经验跨度？ | 我从单个 AI 工具做起，到多工具编排，再到治理/架构/审计，是一条聚焦的递进线 |
| 带过团队吗/怎么带？ | 把团队当分布式系统：统一网关+主备隔离，给核心人员研发沙盒；用规格驱动交付；沟通结果在前 |

## 12 个强答案（展开版）

### 1. What do you think is the hardest part of deploying LLMs in a bank?

> The hardest part is not capability. It is forcing a probabilistic system to operate inside deterministic institutional boundaries. In a bank, the real problems become execution authority, data boundary, auditability, and risk-tiering. My bias is that many teams over-focus on the model and under-invest in the control plane around it.

### 2. Where do you think banks get AI wrong today?

> I think a common mistake is using one trust model for all use cases. A read-only assistant, an analyst copilot, and a state-changing workflow agent are three different risk classes and should not share one architecture. Another mistake is celebrating pilots before proving governance fit and stable unit economics.

### 3. Do you believe in autonomous agents for banking?

> Yes, but only in a narrow and controlled sense. I do not believe in giving the model direct authority over high-liability actions. I believe in bounded autonomy: the model can propose, decompose, and extract parameters, but deterministic systems should still own permissions, validation, and final commit. In banking, autonomy should scale only where blast radius is tightly bounded.

### 4. How would you design an LLM system for a regulated workflow?

> I would separate it into layers. First, deterministic routing or policy classification. Second, risk classification. Third, model-based proposal generation. Fourth, orthogonal verification. Fifth, deterministic execution or explicit human approval. The core principle is proposal inside the model, authority outside the model.

### 5. Which use cases would you launch first?

> I would start with read-heavy, high-frequency, low-liability workflows. They give learning value without exposing the bank to asymmetric downside. I would avoid jumping directly into state-changing workflows because the governance and verification burden is much higher. My decision criteria would be risk, auditability, human fallback, and measurable ROI.

### 6. How do you think about ROI for enterprise AI?

> I think enterprise AI is ultimately judged by whether it can generate a predictable bill and a predictable operating outcome. Capability alone is not enough. If token consumption, retries, latency, or review load are unstable, the business case collapses. So I would measure not just quality, but controllability of cost and failure.

### 7. How do you think about explainability for LLMs in banking?

> I do not think the main answer is full explainability of the model internals. In practice, what matters more is explainability of the control path. Can we explain why the system allowed or blocked an action? Can we reproduce the routing, permission, validation, and escalation decisions? In a bank, operational explainability is often more useful than trying to fully explain neural weights.

### 8. How would you handle hallucination risk?

> I would not treat hallucination as something to be solved by better prompting alone. I would treat it as a permanent property of the underlying model and architect around it. That means constraining output formats, limiting authority, separating read and write paths, and using deterministic checks wherever the cost of error is asymmetric.

### 9. What changes about engineering talent in the AI era?

> I think the value of pure coding throughput declines, while the value of people who can define boundaries, specs, and decision rules increases. The scarce talent becomes people who can translate ambiguous business intent into controlled systems. Fewer people are valuable because they type fast; more are valuable because they think clearly under constraints.

### 10. How would you balance experimentation with governance?

> I think teams need two distinct states: exploration and bounded execution. In exploration, you allow speed and loose experimentation. But before anything moves toward production, there must be a graduation gate: a sharp use case, a proven differentiator, tested infrastructure, and clear controls. A lot of AI confusion comes from mixing prototype logic with production logic.

### 11. If models keep improving, won't many of these controls become less necessary?

> I do not think so. Better models may reduce some local error rates, but they do not remove the core mismatch between probabilistic generation and deterministic accountability. In fact, stronger models can increase over-trust, which makes governance architecture more important, not less.

### 12. What would you ask me if you joined this team?

> I would want to understand where the real bottleneck is today: model quality, data access, governance approval, or production integration. I would also want to know whether the organization has already agreed on a risk taxonomy for AI use cases, because without that, architecture discussions tend to stay abstract.

## 判断力短语库（强候选信号）

- My short answer is...
- The real issue underneath that is...
- I would separate this into three cases...
- My bias is that...
- I think the common mistake is...
- This is really a governance problem disguised as a model problem.
- In a bank, I would optimize for control before capability.

## 可自然使用的强单句

- In a bank, AI is a control-plane problem before it is a capability problem.
- Read-only and state-changing workflows should not share the same trust model.
- Better models do not remove the need for governance; they increase the consequences of over-trust.
- The real production question is not "can the model do it," but "can the institution govern it?"
- I would rather have bounded autonomy with clear liability than impressive autonomy with unclear failure modes.
- In regulated environments, proposal and execution should be treated as separate authorities.
- A successful pilot is not the same thing as a production-worthy operating model.
- Predictable billing and predictable liability matter more than benchmark magic.

## 被 push back 时的保命句

- That is fair. My view would change if...
- I agree there is a tradeoff there.
- I would handle that differently for low-risk and high-risk cases.
- Better models help, but they do not remove the accountability mismatch.
- In a bank, over-trust is usually more expensive than under-automation.
- I do not think there is one answer for every workflow.

**追问处理总则：**

- 被 push back → 不防御。That is fair + 我的观点在什么条件下会变。
- 宽问题 → 立刻摆框架（三桶 / 两层：模型能做什么 vs 机构能治理什么）。
- 不知道具体细节 → 不硬编。I do not know the exact current HSBC implementation detail, but my general view would be...

## 强收尾观点（被问整体看法时的收尾）

> Bank AI deployment is not primarily a model problem. It is a control-plane, workflow, and ROI problem. The architectures that win will not be the ones with the most autonomy, but the ones that place probabilistic intelligence inside deterministic institutional boundaries.

## 迁移路径（如被问怎么 rollout）

1. 内部只读用例
2. analyst copilots
3. 有界 workflow 辅助
4. 窄领域里小心控制的自动化
