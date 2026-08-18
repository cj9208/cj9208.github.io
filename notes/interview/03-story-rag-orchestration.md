# 03 — Story: RAG → Orchestration（主线脊柱）

> 你的技术主线：一个 messy-input RAG 问题如何演化为受治理的 request orchestration。
> 对应旧版 `Director-Level-Interview-Guide.md` + 两个深潜（Orchestration / RAG Case）。

## 一句话核心

Move from prompt-heavy retrieval to governed request execution, with the harness as the authority boundary.

## 聚焦主线：AI 架构的三个递进层次（不是单一故事，是聚焦的弧线）

> My work is a progression: I built individual AI tools, then wired multiple tools together, and finally worked on the governance, architecture, and audit layer that makes the whole thing safe to operate.

| 层次 | 内容 | 我做过的东西 |
|---|---|---|
| ① 个体工具 | 单点 AI 能力，做对、做好 | RAG 检索 · 意图识别层 · 文档解析（严格验收） |
| ② 多工具 / 编排 | 一个工具 → 一套工具；路由、注册表、编排 | 中央工具注册表 · 域路由 · 能力编排 · 跨域复用控制面 |
| ③ 治理 / 架构 / 审计 | 让整套系统安全可运营；权限、策略、风险、审计、ownership | harness 权威边界 · 非对称阈值 · 正交置信度 · 审计/可追溯 · 运营模型 |

这套弧线的**脊柱实例**就是 RAG→orchestration 故事：脏请求 → 意图识别层 → 发现是控制问题 → RAG 只是能力之一 → harness 是权威边界。它贯穿了①②③三个层次。

**叙事心法**：回答任何具体问题时，可以点出「这是我在哪一层做的事」，让面试官看到你走过整条线，而不是只有一个故事。

## 60 秒脊柱版

> We started with a practical retrieval problem. User requests were often messy, ambiguous, or underspecified, which hurt retrieval quality and wasted downstream cost. So I first designed an intention-recognition layer that does deterministic cleanup, lightweight interpretation, confidence-aware clarification, and graceful fallback.
>
> The bigger insight was that this should not stop at retrieval. Once a system can decide whether a request is clear enough to proceed, it is already becoming the front half of a broader orchestration layer. In that architecture, RAG becomes one capability rather than the default path.
>
> The key boundary is that the model proposes, but the harness decides. The harness owns permissions, policy, risk, and execution control. Today the strongest implemented part is the intention-recognition layer, and the orchestration layer is the path for growing that into a governed platform over time.

## 3 分钟版

> The original problem looked like retrieval quality, but the deeper issue was poor request conditioning. Users often asked in short, messy, or ambiguous ways, so downstream retrieval was noisy, more expensive, and harder to trust. The first thing I designed was an intention-recognition layer that does deterministic cleanup first, then lightweight model-based interpretation, and asks clarifying questions when confidence is low.
>
> That solved an immediate quality problem, but it also exposed a broader architectural pattern. The layering matters not only for modularity, but because it creates fail-fast boundaries where bad requests can be stopped, clarified, or rerouted early, and where each stage can be evaluated separately. Once the system can interpret a request and decide whether to clarify, retrieve, call a tool, or escalate, it no longer makes sense to treat every request as a RAG problem. Some requests should go to retrieval, some to structured APIs, some to deterministic lookup, and some to human escalation. That is what led me from better RAG toward governed request orchestration.
>
> The most important design decision is the control boundary. The model can help with reasoning and propose tool usage, but it does not directly execute important actions. The harness validates schema, identity, permissions, and risk before deciding whether to execute, confirm, reject, or escalate. That keeps authority and auditability outside the model.
>
> I would also scope execution by domain rather than build one giant general agent. That reduces search space, keeps permissions and corpora easier to govern, and creates clearer ownership boundaries for teams. With a small team, I would phase this in: first harden intention recognition, then add capability routing and registry structure, then governed tool execution, and finally stronger observability and review loops. The strongest implemented part today is still the intention layer, but the architecture provides a realistic path toward a reusable control plane.

## 五步回答结构（技术题专用骨架）

1. 先用最小改动解决眼前的实际问题
2. 分层 = fail-fast 边界 + 评估点 + 归属
3. harness 是治理边界（权限/策略/风险/执行在模型外）
4. 自然演化成 request orchestration（可复用控制面）
5. 指标拆分，归属明确

### 五步展开（口语化）

**1. 先解眼前的实际问题：**

> I started by improving the existing RAG flow without forcing a large rewrite. The key insight was that many downstream RAG problems actually came from poor upstream input, so I added an intention-recognition layer that turns messy requests into cleaner retrieval-ready inputs.

**2. 分层创造 fail-fast 边界：**

> I split the system into layers not only for modularity, but to create fail-fast, evaluation, and ownership boundaries. Bad or ambiguous requests can be stopped, clarified, or rerouted early, and each layer can be measured and debugged independently.

**3. harness 是治理边界：**

> I made the harness the governance boundary. The model can help with reasoning, but permission, policy, risk, and execution control stay outside the model.

**4. 自然演化成 request orchestration：**

> Once the system can understand requests and decide whether to clarify, retrieve, call a tool, or escalate, it becomes a reusable control pattern. That gives you a path to unify similar AI-agent efforts across the company instead of having each team build isolated flows.

**5. 指标拆分，归属明确：**

> I would separate metrics across the platform, orchestration layer, and individual tools or capabilities so ownership is explicit. That makes it easier to identify where quality, latency, cost, or reliability issues come from and creates a fair basis for convergence over time.

## 为什么这听起来资深

**强框架**：

- 从真实失败模式开始
- 在引入更大抽象前先改进当前路径
- 把控制边界放在模型外
- 区分当前实现与未来方向
- 展示小团队如何分阶段推进
- 让归属与治理可见

**弱框架（避免）**：

- 一开口就是 agent platform / multi-agent system
- 把 RAG 当成一切的中心
- 暗示模型拥有执行权
- 夸大实现成熟度
- 只列组件，不讲边界为什么存在

## 当前状态 vs 未来方向（必须明确拆分）

当前最强：

- intention-recognition 层
- 明确的 orchestration 架构方向
- harness 周围清晰的受控执行边界

仍需加固：

- 置信度校准规则
- 评估深度与回归覆盖
- 告警阈值与运行时 triage
- 更丰富的能力注册表与域接入规则

好句式：

> We are strongest today in the intention-recognition layer. The broader orchestration layer is the path for growing that into a reusable governed platform over time.

## 分阶段落地计划（小团队怎么 rollout——必问 follow-up）

> I would phase it in. First harden intention recognition and the clarification policy. Then add domain routing and a capability registry. Then introduce governed tool execution behind the harness. Finally add stronger observability, review loops, and operational thresholds. That gives near-term value while building toward the platform.

记忆链：意图识别加固 → 域路由/注册表 → 有治理的工具执行 → 观测/复盘/阈值。

## 数字话术（80x 之类被追问时）

> I would not treat those numbers as a forecast. The point is that the savings are multiplicative because they happen at different layers of the pipeline. The exact number needs measurement against a real deployment.

要点：方向性论证不是承诺；数字待真实部署测量；别让倍数转移掉架构重点。

---

# 深潜 A：Orchestration Case

> 追问细节：为什么 orchestration 是对的抽象、域边界、harness 控制与运行时策略、工具暴露与排序。

## 核心论断（一段话版）

> The deeper problem is not only retrieval quality. It is governed request execution. Once a system can interpret a request, resolve ambiguity, and decide whether to proceed or clarify, it should also decide which capability should handle the request and under what policy. That is why RAG should sit inside an orchestration layer rather than act as the default path. The model helps with reasoning, but the harness owns validation, permission, risk, execution policy, and escalation.

## 为什么 orchestration 是更好的抽象

- retrieval 只是执行路径之一
- 模糊应在能力选择前解决
- 执行策略应留在模型外
- 权限与风险随域和动作类型变化
- 系统需要可复用控制面，而不是每个 workflow 一个 prompt
- 团队不应各自重造同一套合规与请求安全逻辑

关键转变：

> not every unclear request needs better retrieval; many need better routing, clarification, or refusal.

## 运行时边界

1. 请求进入 intention 层
2. 确定性规范化 + 轻量解释产生更清晰的请求状态
3. orchestration 层选择域与能力路径
4. 模型可提出结构化 tool call
5. harness 校验 schema、身份、权限、风险
6. harness 决定：执行 / 确认 / 拒绝 / 升级
7. 系统记录足够结构供复盘与调试

边界之所以重要：权威留在软件策略中，而非模型行为中。

## harness 拥有什么

模型应：

- 推理可能的下一步
- 提出结构化工具使用
- 在确定性逻辑不足时支持模糊解决

harness 应：

- 校验 schema
- 校验身份与权限
- 执行风险与确认策略
- 确定性执行工具
- 限制 retry 与按类 retry
- 捕获输出与错误
- 策略要求时拒绝或升级

这是把模型推理变成受治理执行的**生产边界**。

## 为什么域切分（domain scoping）重要

是务实的治理选择，不是理论：

收益：更小的检索范围 · 更少同时暴露的工具 · 更清晰的归属边界 · 更易建模权限 · 更低的回归 blast radius · 更好的可审计性

代价：共享能力仍需公共接口 · 跨域请求需显式协调规则

要点：控制面共享，执行面有界。

## 为什么工具要保持窄

orchestration 层应拥有排序与依赖控制：

- 工具只做一件窄事
- 工具不应递归互相调用
- 模型不应即兴创造隐藏执行路径
- retry、上限、回退属于 orchestrator / harness

这让工具更易测、更安全暴露、更易分配归属。

## 值得说出口的权衡

**Deterministic First vs Model First**：别名修复、拼写纠正、规范化、精确匹配常见时，deterministic-first 更便宜、更稳、更易审计；确定性逻辑不足处再加模型推理。

**宽工具暴露 vs 自适应工具加载**：自适应加载通常更好——收窄动作空间、减小 prompt、提升选择质量。宽暴露仅在工具集极小且低风险时成立。

**一个通用 agent vs 域切分执行**：通用 agent 听着简单，但把复杂度推给路由模糊、权限面、调试。域切分执行更易治理与运营。

**模型自主 vs harness 控制**：更高模型自主在 demo 里更快，但削弱可审计性与策略执行。harness 控制设计更慢，但对生产系统强得多。

## 高频追问速答

- **为什么不只建一个强大的通用 agent？** 因为单一通用 agent 在路由、工具选择、权限、检索范围上制造太多模糊。域切分让每个子系统更小更易跑，共享 orchestration 层保持控制模式一致。
- **为什么不把所有工具一次暴露给模型？** 宽暴露增加 prompt 大小、选择噪声、误用风险。自适应 schema 加载收窄动作空间、提升可靠性。
- **为什么需要 harness 而不是更聪明的 prompt？** Prompt 能塑造模型行为，但无法强制权限、schema 有效性、确认规则、审计。这些需要模型外的软件策略。
- **为什么不让模型直接执行动作？** 因为权限、风险策略、审计不应依赖模型判断。harness 必须是强制点。
- **如何防止系统在模糊上无限循环？** 有界 retry + 显式上限。少量澄清尝试或失败路由后，带结构化上下文交给人工。
- **RAG 在这个设计里的位置？** RAG 是 orchestration 层内的一个能力，任务需要非结构化证据时才被选中，不是默认路径。

## 诚实开口（越直说越可信）

仍需加固：置信度校准规则 · 回归与策略评估深度 · 告警阈值与运行时 triage · 跨域协调模式 · 新能力接入标准。

---

# 深潜 B：RAG Case

> 追问细节：上游条件化（upstream conditioning）为何产生质量、成本、UX 的乘法收益。

## 核心论断

1. 不是每个请求都应进入 RAG
2. 进入 RAG 的请求应该更干净
3. 更干净的请求应检索更少、更相关的 chunk
4. 更小更干净的上下文常可用更便宜的模型档

> upstream conditioning improves both economics and answer quality because the savings happen at multiple stages of the pipeline.

## 为什么上游条件化有杠杆

没有上游条件化时，RAG 常花昂贵的下游工作抢救坏输入。

常见失败模式：模糊请求检索到错误证据 · 未明确请求拉入过多无关上下文 · 噪声请求在检索与回答上浪费 token · 用户得到自信的答案而不是早期澄清。

改进请求后再检索，系统可以：停止/改道本不该进 RAG 的请求 · 更早问澄清问题 · 降低检索噪声 · 缩小上下文 · 提升答案精度。

## 乘法成本逻辑（面试友好的心算模型）

- 大约一半噪声请求在 RAG 前被停止/澄清/改道 → 约 `2x`
- 请求塑形把检索上下文从约 `20` chunk 降到约 `5` chunk → 约 `4x`
- 更干净上下文让很多场景从 `pro` 降到 `flash` → 约 `10x`

方向性逻辑：

```text
2 * 4 * 10 = 80x
```

**这不是精确预测。** 正确框架：

> the leverage is multiplicative because the savings happen at different layers of the pipeline.

## 质量与 UX 也提升

- 更少噪声请求产生坏检索
- 更多模糊请求更早澄清
- 更小更干净上下文提升答案精度
- 更好的路径选择减少不必要下游失败

这不是优化技巧，它改变了交互质量。

## 下游模块因此更简单

- prompt 可更简单（无需防御每个上游边界情况）
- 检索逻辑专注找证据而非输入抢救
- grounded answering 专注引用与合成而非修复坏上下文
- 每个模块更易测、易调、可替换

设计同时提升运行时效率与工程简单性。

## 高频追问速答

- **为什么不只把检索调得更狠？** 检索调优仍假设检索是对的路。更关键的问题是请求是否该进 RAG、以什么清理后的形式进。
- **为什么这强于 prompt 优化？** 因为它一次改变多个阶段的成本与质量，而不是只改进管道末端的一个 prompt。
- **为什么杠杆这么大？** 因为节省是复合的：更少请求进 RAG、剩下的检索更少噪声、上下文窗口更小、更多场景可用更便宜模型。
- **为什么让系统更易运营？** 每个下游模块专注更窄问题，而不是补偿混乱的上游输入。

## 要谨慎说的话

不要把乘法例子当承诺。作为方向性系统论证说：

> I would not treat those numbers as a forecast. The point is that upstream conditioning changes several cost and quality drivers at once, so the gains can compound rather than add linearly.

## 收尾句

> The value of the design is not a small prompt optimization. It changes which requests enter RAG, improves the quality of the ones that do, reduces downstream noise and cost, and makes the remaining RAG modules simpler to build and operate.
