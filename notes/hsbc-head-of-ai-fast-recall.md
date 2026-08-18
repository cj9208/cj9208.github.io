# HSBC Head of AI — 面试前 20 分钟快速回忆

> 来源：`hsbc-head-of-ai-interview-prep.md`、`hsbc-head-of-ai-ultra-short-cheat-sheet.md`、`notes/interview/` 目录。此文件是压缩版，细节回源文件。

## 1. 人设一句话

不是「我懂很多 AI」，而是「我比大多数候选人更懂银行部署的真实问题」。

面试要证明四件事：独立观点 / 把问题框对 / 约束下有明确立场 / 把 AI 架构接回银行现实（合规、审计、成本、运营）。

## 2. 开场

> Given HSBC's environment, I imagine the hard part of LLM deployment is not model capability itself, but satisfying HKMA expectations and internal control requirements. I am curious which part has actually been the biggest bottleneck in practice.

从对方运营现实出发 + 抛一个假设 + 请对方讲真正的瓶颈。

## 3. 三桶框架（所有宽问题的骨架）

> I tend to think about this in three layers: control architecture, ROI, and the engineering operating model around AI.

| 桶 | 一句话核心 | 记忆锚点 |
|---|---|---|
| ① 控制架构 | 概率模型放进确定性边界；模型提议、harness 决策 | 读写不同信任模型 · 工具注册表 · 正交置信度 · 结构化确认 · 人工保留决策权 |
| ② ROI / 运营经济学 | 可预测账单和运营结果 > demo | 外层 harness 限 retry · 窄步骤用 flash · 干净检索用便宜合成 · 模块化缓存 · 早期 fail-fast |
| ③ AI 时代工程方法 | 编码变便宜，边界设定更值钱 | repo 分层（platform/utils/feature）· 重复优于过早抽象 · blast radius · prototype→production 要有 graduation gate |

## 4. 聚焦主线：AI 架构的三个递进层次（不是单一故事，是聚焦的弧线）

> My work is a progression: I built individual AI tools, then wired multiple tools together, and finally worked on the governance, architecture, and audit layer that makes the whole thing safe to operate.

| 层次 | 内容 | 我做过的东西 |
|---|---|---|
| ① 个体工具 | 单点 AI 能力，做对、做好 | RAG 检索 · 意图识别层 · 文档解析（严格验收） |
| ② 多工具 / 编排 | 一个工具 → 一套工具；路由、注册表、编排 | 中央工具注册表 · 域路由 · 能力编排 · 跨域复用控制面 |
| ③ 治理 / 架构 / 审计 | 让整套系统安全可运营；权限、策略、风险、审计、ownership | harness 权威边界 · 非对称阈值 · 正交置信度 · 审计/可追溯 · 运营模型 |

这套弧线的**脊柱实例**就是 RAG→orchestration 故事：脏请求 → 意图识别层 → 发现是控制问题 → RAG 只是能力之一 → harness 是权威边界。它贯穿了①②③三个层次。

面试叙事心法：**回答任何具体问题时，可以点出「这是我在哪一层做的事」，让面试官看到你走过整条线，而不是只有一个故事。**

### 60 秒脊柱版（RAG→orchestration）

> We started with a practical retrieval problem. User requests were often messy, ambiguous, or underspecified, which hurt retrieval quality and wasted downstream cost. So I first designed an intention-recognition layer that does deterministic cleanup, lightweight interpretation, confidence-aware clarification, and graceful fallback.
>
> The bigger insight was that this should not stop at retrieval. Once a system can decide whether a request is clear enough to proceed, it is already becoming the front half of a broader orchestration layer. In that architecture, RAG becomes one capability rather than the default path.
>
> The key boundary is that the model proposes, but the harness decides. The harness owns permissions, policy, risk, and execution control. Today the strongest implemented part is the intention-recognition layer, and the orchestration layer is the path for growing that into a governed platform over time.

## 5. 组织层（可聊，但诚实限界）

这部分来自你的真实思考，只能覆盖「沟通 + 带队」，不装更复杂的组织经验。

### 核心视角：把组织看成分布式系统

- 管人和管系统，底层协议逻辑是通的。沟通 = 状态机复制，目标是让节点达成共识、防止脑裂（split-brain）。
- **对齐 Schema**：研发节点收 Log/Trace，高管/客户节点只收 SLA/ROI/合规。别把 Raw Data 广播给高管，要在接口处做序列化。
- **结果在前（State Root）**：前 3 秒先交出终局（"业务大盘绝对安全"），解除对方焦虑后再补细节。不要功劳叙事、流水账。
- **Outside-In 逆向流控**：以对方节点的焦虑和约束为起点，包装成求解对方约束的过程。
- **信号传递机制**：面对高压，用定频 cadence（如每 2 小时固定看板同步）拉平信息差，把对方的风险溢价（催促/微管理）清零。
- **激励相容**：让技术方案变成对方写晋升述职、刷战功的素材，对方就会从博弈者变成你最强的共识节点。

### 带队视角：分布式共生 + Tit-for-Tat

- TFT 四准则：**友善**（不先背叛）/**报复**（被背叛必反击）/**宽恕**（对方回归协作立即释然）/**清晰**（完全可预判）。长周期协作里这是数学上收益最高的策略。
- 团队拓扑：**统一网关**（主管拦脏流量，成员拿到的都是边界清晰的标准化任务）+ **主备隔离**（一主一辅，热备切换，防单点故障）+ **研发沙盒**（给核心人员干净的深度思考空间）。
- 交付反馈：**规格驱动（Spec-Driven）**，先收敛模糊输入、定边界和契约；核心不动，只写胶水代码，边际交付成本趋近于零。
- 组织层最低标准：**技术硬实力定底线，风险/期望/干系人管理定上限。** 平时对外价值锚定，被懂行的首席架构师挑战底层时能瞬间拔刀，用技术公信力压住场面。

### 诚实边界（被追问就直说）

- **组织层（小团队，≤10 人）**：真实经验是沟通 + 带小团队（互信型），核心是"少而精"。超过 ~10 人、靠互信跑通就会失真——筛错一个人、引入 bad one，团队纯净度就坏了。再往上（预算、跨部门政治、大规模组织设计）没有深度经验，不硬撑。

> On the organizational side, my hands-on experience is leading small high-trust technical teams. The model I trust is "small and selective": mutual trust only holds at that scale — beyond roughly ten people, one bad hire degrades the whole team, so screening quality becomes the bottleneck. Large budgets, cross-department politics, and big org design I have not done hands-on, and I would rather say that than pretend otherwise.

- **经济层（框架有，数字缺）**：ROI 框架做过分析（成本结构、retry 浪费、分层模型、缓存），但架构没在组织内得到推广——受组织问题所限，这也是我这次想换环境的原因。所以只能给出框架和机制，具体数字遇到真实部署场景再填。

> On the economics side, I have the analytical framework — where the cost leaks are, why the savings compound across layers. What I do not have is a fully deployed system with measured numbers: the architecture did not get the organizational runway to roll out broadly, which is part of why I am looking to move. So I would present the framework and the mechanism, and fill in the actual numbers against a real deployment.

## 6. 五步回答结构（技术题通用骨架）

1. 先用最小改动解决眼前的实际问题
2. 分层 = fail-fast 边界 + 评估点 + 归属
3. harness 是治理边界（权限/策略/风险/执行在模型外）
4. 自然演化成 request orchestration（可复用控制面）
5. 指标拆分，归属明确

## 7. 真实案例速记（30–60 秒/个，把原则变具体）

| # | 案例 | 记忆点 |
|---|---|---|
| 1 | 意图层 fail-fast + 人工回退 | 多一轮确认比快速错答便宜；有界失败 > 最大化自动化 |
| 2 | 文档解析严格验收 | 无 ground truth 用代理质量门；生产不达标自动回退 |
| 3 | 非对称置信阈值 | 读操作低阈值、写/动钱接近 99%；不过线→结构化确认→人工 |
| 4 | 证据优先辅助人工 | AI 做分析、给摘要/风险点/引用，人保留决策权 |
| 5 | 中央工具注册表 | RAG/意图/API 都是 tool，声明 schema+owner→可追溯可审计 |
| 6 | 正交置信度 + 结构化确认 | 不只用 LLM 自我判断；≤3 选项让用户确认 |
| 7 | UAT vs 生产代理指标 | 离线有 ground truth 用 recall/precision；线上用确定性代理信号 |

口语模板：`My bias is X. In one trial, we handled it by Y. The reason was Z. The tradeoff was A versus B. What I learned is C.`

## 8. 场景 → 桶 映射

- 治理 / hallucination / agents / 可解释性 → ① 控制架构
- 价值 / 优先级 / 规模化 / CFO → ② ROI
- 人才 / AI 编码 / 组织 / 实验 vs 执行 → ③ 工程方法（组织/沟通类 → 第 5 节组织层）
- 模糊大问题 → 先给框架（三桶，或「模型能做什么 vs 机构能治理什么」两层）
- 被挑战 → 承认权衡 + 重申原则 + 银行不对称下行

## 9. 高频题速答

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

## 10. 被 push back 时的保命句

- That is fair. My view would change if...
- I agree there is a tradeoff there.
- I would handle that differently for low-risk and high-risk cases.
- Better models help, but they do not remove the accountability mismatch.
- In a bank, over-trust is usually more expensive than under-automation.

## 11. 强收尾观点

> Bank AI deployment is not primarily a model problem. It is a control-plane, workflow, and ROI problem. The architectures that win will not be the ones with the most autonomy, but the ones that place probabilistic intelligence inside deterministic institutional boundaries.

## 12. 最后 3 个提醒

- 准备并练熟 3 个核心观点：控制面先于能力 / 可预测账单 / 边界设定比编码更值钱。
- 避免：长独白、上来堆术语、泛泛 hype、答非所问、试图显得聪明；组织层与经济层的缺口都要诚实限界，被追问就直说（组织≤10 人互信、经济只有框架没落地数字）。
- 结束后他记住的不是你的知识量，而是「这个人有判断力」。