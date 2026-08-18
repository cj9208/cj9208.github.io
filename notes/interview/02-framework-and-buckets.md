# 02 — Framework & Buckets（三桶框架 + 答题骨架）

> 宽问题的骨架。面试时先用一句话摆框架，再按桶展开。
> 对应旧版 `hsbc-head-of-ai-interview-prep.md` 的 Three-Part Frame 与 Part 1–3。

## 三桶框架（所有宽问题的骨架）

> I tend to think about this in three layers: control architecture, ROI, and the engineering operating model around AI.

| 桶 | 一句话核心 | 记忆锚点 |
|---|---|---|
| ① 控制架构 | 概率模型放进确定性边界；模型提议、harness 决策 | 读写不同信任模型 · 工具注册表 · 正交置信度 · 结构化确认 · 人工保留决策权 |
| ② ROI / 运营经济学 | 可预测账单和运营结果 > demo | 外层 harness 限 retry · 窄步骤用 flash · 干净检索用便宜合成 · 模块化缓存 · 早期 fail-fast |
| ③ AI 时代工程方法 | 编码变便宜，边界设定更值钱 | repo 分层（platform/utils/feature）· 重复优于过早抽象 · blast radius · prototype→production 要有 graduation gate |

## 通用答题骨架（任何问题都能用）

1. direct answer（先给结论）
2. reframe one level deeper（把问题框深一层）
3. your position（My bias is...）
4. practical implication（落到银行现实）

> My short answer is... The deeper issue is... My bias is... The implication is...

示例：

> My short answer is yes, but only in tightly bounded use cases. The deeper issue is that banking workflows have asymmetric downside, so I would not treat read-only and state-changing workflows the same way. My bias is that autonomy should only grow where the blast radius is already tightly controlled. The implication is that architecture should follow risk class, not just capability.

## 场景 → 桶 映射

- 治理 / hallucination / agents / 可解释性 → ① 控制架构
- 价值 / 优先级 / 规模化 / CFO → ② ROI
- 人才 / AI 编码 / 组织 / 实验 vs 执行 → ③ 工程方法（组织/沟通类 → `01` 组织层）
- 模糊大问题 → 先给框架（三桶，或「模型能做什么 vs 机构能治理什么」两层）
- 被挑战 → 承认权衡 + 重申原则 + 银行不对称下行

---

# 桶 ① Control Architecture（控制架构）

这是你最强的银行专属桶。

## 核心观点

LLMs 是概率的，但银行需要确定性边界。

## 关键论断

- 模型生成提议（proposal），不持有执行权（execution authority）
- 确定性系统应拥有：路由、权限、校验、限额、审计、最终执行
- 只读与 state-changing 工作流不应共享同一信任模型
- 更强的模型减少 babysitting，但不消除外部治理需求
- over-trust 会随模型变强而变得更危险

## 口语版本

> My bias is that in banking, the real challenge is not making the model smarter. It is building deterministic control around a probabilistic model.

> I do not think better models remove the need for strong outer control. If anything, they make governance architecture more important because people are more tempted to over-trust them.

## 桶内主题

proposal vs execution 分离 · routing · risk-tiering · RBAC · auditability · human-in-the-loop · 确定性外层 harness

## 深度观点（来自真实系统设计）

### 1. 复杂/高风险工作流里，AI 做分析、人保留决策权

- 最难查询里，AI 提升人的生产力但不拿走最终决策权
- 有用输出不只是答案，而是给人工 agent 的结构化证据：UI 线索、风险高亮、理由、引用原文
- 口语版：

> In more complex or higher-risk workflows, I prefer AI to act as an analysis layer rather than a final decision-maker. The goal is to give the human agent a clean summary, the likely intent, the key evidence, and the parts that need attention. That way, the human does not need to start from zero, and the customer does not need to repeat the whole situation. I think this is one of the most practical ways to boost productivity without losing control.

### 2. 把 RAG、意图识别、API 调用都当作中央注册表下的 tool

- 每个 tool 声明 schema、contract、ownership
- 意图识别本身也可以当作可观测输出的 tool
- 产生清晰审计链：为什么选这个 tool、置信度是否达标
- 归属清晰：各团队可独立拥有并改进自己的 tool
- 口语版：

> For governance, I like to treat everything as a tool, including RAG, intent recognition, and API calls, and put them behind a central registry. That forces each tool to declare its schema, ownership, and expected behavior. Then the system has a much clearer audit trail: which intent was detected, which tool was selected, what the confidence was, and why it was allowed to proceed. It also helps operationally because you can review tool performance offline and route issues back to the responsible team.

#### 2.1 统一设计让系统持续变好

- 升级路径不只是回退机制，也是数据收集机制
- 难案例转给人工时，就变成模型/流程改进的新样本
- 统一设计让采集、标注、分析、回流更容易
- 口语版：

> Another reason I like unified design is that it improves the system over time. For example, when a case escalates to a human agent, that is not just a fallback event. It is also a valuable new sample. If the workflow is structured properly, we can collect those cases, analyze where the system was uncertain, and use them to improve the next version. So the control architecture is also part of the learning loop.

### 3. 置信度不能只靠 LLM 自评

- 原始模型概率只是弱信号
- 第二个 LLM 判断仍相关、还加成本延迟
- 正交信号（拼写纠正距离、词法距离、确定性预检）更适合生产 gating
- 口语版：

> On confidence scoring, I would not rely only on the model's own signal or even on another LLM judging it, because that can still be correlated and expensive. I prefer to mix probabilistic signals with orthogonal checks, for example deterministic distance or correction-based measures. And if confidence is still not good enough, I would rather ask the user for structured confirmation than pretend the system knows more than it does.

### 4. 结构化用户确认 = 控制机制 + UX 机制

- 置信度低于阈值时系统不应乱猜
- 回退不必是自由文本循环
- ≤3 个选项的小选择框即可低摩擦确认意图
- 口语版：

> If confidence is below the required threshold, I do not think the right answer is to let the model keep guessing. A better pattern is structured user confirmation, for example with at most three explicit choices. That keeps the interaction lightweight while turning ambiguity into a clearer control event.

### 5. 模块化设计提升可测性与 fail-fast

- 每个模块暴露自己的可测量验收门
- 意图识别可在置信度上 fail fast；检索可在相似度/排序质量上 fail fast（在生成之前）
- 运行时 gating 用确定性代理指标往往优于再请一个 LLM 验证
- 口语版：

> Another reason I prefer modular design is testability. Each layer can have its own acceptance gate. For retrieval, for example, you can inspect the similarity profile of the top returned chunks and stop early if the signal is weak, instead of paying for another LLM verification step in production. That improves latency, cost, and robustness at the same time.

### 6. UAT 与生产需要不同的评估逻辑

- UAT/离线有 ground truth，可用 recall、precision、甚至 LLM judging 做 truthfulness 分析
- 生产决策时刻往往没有 ground truth
- 生产 gating 必须依赖可实时测量的代理指标与确定性信号
- 口语版：

> I think it is important to separate UAT evaluation from production gating. Offline, if you have ground truth, you can use recall, precision, and even LLM judging for things like truthfulness against retrieved chunks. But in production, you usually do not have ground truth in the moment, so you need proxy metrics and deterministic signals that are measurable live. That distinction matters a lot.

### 何时用这个桶

问他：hallucination / safety / agents / explainability / governance / regulated deployment / high-risk workflows。

---

# 桶 ② ROI and Operating Economics（ROI 与运营经济学）

这是让你听起来有商业底子的桶。

## 核心观点

企业 AI 的生死取决于**可预测的 ROI**，而不是 demo 质量。

## 关键论断

- 能跑的 demo 不够
- 成本、retry 行为、延迟、复核负担必须可预测
- 隐性 retry 和 agent 循环是数字浪费
- 银行想要可控资产，不想要计费黑箱
- 成功的 pilot 在进入企业成本与控制现实时经常失败

## 口语版本

> Even if a use case works technically, it still fails if cost, latency, retries, and review burden are not predictable.

> The real question is not just whether the model performs well, but whether the system can produce a predictable bill and a predictable operating outcome.

## 桶内主题

token 经济学 · retry 浪费 · 延迟 · 复核负担 · 有界下行（bounded downside）· pilot vs production 经济学

## 深度观点（来自真实系统设计）

### 1. 外层 harness 限制最坏情况成本

- 外层 harness 控制 retry、网络行为、超时策略、升级规则
- 这既是治理也是成本控制
- 最坏成本由 retry 策略 + 回退成本决定，而不是开放式模型空转
- 口语版：

> One reason I like a strong outer harness is that it bounds worst-case cost. If retries, timeouts, and fallback are controlled outside the model, the fee ceiling becomes much more predictable. In the worst case, you pay for a fixed retry budget and then escalate, instead of letting the system burn tokens in an uncontrolled loop.

### 2. 拆分简单子步骤，用更便宜模型

- 不是每步都需要大/贵模型
- 意图识别常常只需要短 prompt 和简单原则
- 任务窄时，small/flash 模型常以几分之一成本完成
- 口语版：

> Another cost-control principle I use is step separation. For example, intent recognition usually does not need a long prompt or a frontier model. If the task is just deciding whether the intent is clear, what class it belongs to, and whether a tool should be called, a flash-tier model is often enough. That alone can reduce cost dramatically.

### 3. 检索质量高时，合成不一定需要高端模型

- 人们常过度在最终答案步使用大模型
- 检索干净、相关 chunk 少时，合成可用更便宜模型
- 原则：只在不确定度高的地方花钱
- 口语版：

> I also do not assume the synthesis layer always needs a premium model. If retrieval is already clean and the key chunks are small and relevant, a flash model can often handle the synthesis step well enough. My general view is that capability spend should follow uncertainty, not habit.

### 4. 模块化设计让缓存可落地

- 模块化管道比单体 prompt 更易缓存
- 意图识别尤其 cache-friendly（输出空间小、查询模式重复）
- 常见查询偏斜意味着实践中命中率可以很高
- 口语版：

> Modular design also makes caching far more practical. Intent recognition is a good example because the output space is clean and repetitive. In real usage, a large share of traffic is usually common queries, so cache hit rates can be very high. That can cut cost materially before you even touch model quality.

### 5. 意图层尽早 fail-fast（模糊未决时）

- 快速错答往往比慢速正确路径更糟
- 意图层是在弱流污染下游步骤前停下的正确位置
- 除成本外还改善 UX、可追溯性、审计性
- 口语版：

> On fail-fast behavior, I prefer to stop weak flows early at the intention layer. My bias is that a correct answer with one extra turn is better than a fast wrong answer that creates downstream confusion. Early gating also improves traceability and audit quality because the uncertainty is surfaced at the right point in the workflow.

### 何时用这个桶

问他：business value / use-case prioritization / scaling beyond pilots / enterprise adoption / CFO concerns / investment decisions。

---

# 桶 ③ AI-Era Engineering Method（AI 时代工程方法）

这桶比"AI 编码"更宽：关于工程工作本身如何改变。

## 核心观点

AI 让编码变便宜，但让规格、边界、生产纪律更值钱。

## 关键论断

- 纯编码吞吐量没那么重要了
- 稀缺技能是把模糊业务需求变成有界、可治理的系统
- 强工程师定义边界并执行确定性思考
- 探索（exploration）与生产（production）是不同状态
- 很多 AI 项目失败是因为 prototype 逻辑泄漏进生产预期
- 好的 repo 结构帮助控制 AI 搜索空间与 blast radius
- AI 编码时代，重复常常优于过早抽象
- 抽象应跟随重复出现的现实，而非想象出的未来复用
- blast-radius 控制既关乎软件稳健性，也关乎业务连续性

## 口语版本

> I think AI increases the value of people who can define boundaries, not just generate output.

> A lot of AI confusion comes from mixing prototype logic with production logic. In a bank, you need a very explicit graduation gate.

## 桶内主题

AI coding · spec-driven development · 边界定义 · prototype vs production 纪律 · 工程角色变化 · 组织执行方法 · repo 结构 · 抽象时机 · blast-radius 控制

## 深度观点（来自真实系统设计）

### 1. repo 分层（platform / utils / feature）控制 AI 搜索空间

- 好结构帮助人和 AI 都理解代码该放哪
- 减少意外耦合，让模型少触碰代码库
- platform 代码应有最高 review 门槛（错误会到处扩散）
- 拆分让系统更可扩展：新功能由既有积木拼装
- 口语版：

> One thing I care about in the AI coding era is repository structure. I like separating code into platform, utils, and feature layers because it narrows the AI search space and limits blast radius. If the structure is clean, the model is less likely to write code in the wrong place or create hidden coupling. I also think platform code needs the strongest review standard, because errors there can spread across the whole system.

> Another benefit of that split is extensibility. If the system already has good building blocks, adding new functionality becomes much easier because you are usually composing existing modules with a small amount of glue code rather than rebuilding from scratch. It is a very Linux-like way of thinking: keep components focused, make them reusable, and let power come from composition.

### 2. 重复优于过早抽象

- AI 让代码生成便宜，过早抽象更危险
- 首次实现常把第一个用例的形状硬编码进假抽象
- 抽象应等真实代码里重复模式出现后再提取
- 口语版：

> Another view I have is that in the AI coding era, repeat is often better than abstract too early. Since AI can generate code so quickly, the cost of duplication is lower, but the cost of premature abstraction is higher. If you create an abstract class or framework too early, you often end up encoding the shape of the first example and pretending it is a general solution. I would rather wait until the pattern repeats a few times, then extract the right utility or submodule.

### 3. blast-radius 控制既是技术也是业务问题

- 更小的 blast radius 改善软件稳健性
- 也降低跨系统级联失败风险
- AI 增加代码量与变更频率时这点更重要
- 模块化改善故障隔离与优雅降级
- 口语版：

> I also think blast-radius control becomes more important when AI increases code volume and change frequency. Technically, it improves robustness because a bad change is more contained. From a business point of view, it also reduces cascade failure risk, where one weak change in one place ends up breaking several connected systems. So for me, controlling blast radius is not just an engineering preference. It is part of operational risk management.

> Another advantage of modular design is fault isolation. If one module degrades or fails, the rest of the system can often continue operating in a bounded way instead of collapsing as a whole. That gives you much better resilience and a cleaner path to graceful degradation.

### 4. 统一设计让系统演化更快

- 升级/回退/模块边界结构一致时，生产 miss 容易转成新训练或评估样本
- 系统环境不断变化，干净设计让系统快速追赶而非变脆
- 口语版：

> I also like unified design because it makes the system easier to improve over time. If escalation and fallback paths are structured consistently, production misses become much easier to capture and turn into new samples for evaluation or model upgrades. That matters because these systems are never fully stable. User behavior and workflow patterns keep evolving, so the architecture should help the system catch up instead of falling behind.

### 何时用这个桶

问他：engineering productivity / talent / 团队如何与 AI 协作 / capability building / experimentation vs execution / hiring 与 org design / AI 时代编码标准 / repo 结构与可维护性 / over-engineering 与抽象。
