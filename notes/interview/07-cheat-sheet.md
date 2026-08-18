# 07 — Cheat Sheet（面试前 20 分钟）

> 全文最浓缩版：只留锚点 + 指针。细节全部回源 `01`–`06`。
> 面试前只看这一页。

## 人设一句话

不是「我懂很多 AI」，而是「我比大多数候选人更懂银行部署的真实问题」。

证明四件事：独立观点 / 把问题框对 / 约束下有明确立场 / 把架构接回银行现实（合规、审计、成本、运营）。

## 岗位画像（1 秒记住）

Solution Lead / Architect（银行 Director，Band 5 / GCB4）= **Google Staff L6**。
所有话术收向：横切面影响力 + 落地。

## 开场（银行版）

> Given HSBC's environment, I imagine the hard part of LLM deployment is not model capability itself, but satisfying HKMA expectations and internal control requirements. I am curious which part has actually been the biggest bottleneck in practice.

从对方现实出发 + 抛假设 + 请他讲瓶颈。

## 三桶框架（宽问题骨架）

> I tend to think about this in three layers: control architecture, ROI, and the engineering operating model around AI.

| 桶 | 一句话核心 |
|---|---|
| ① 控制架构 | 概率模型放确定性边界；模型提议、harness 决策 |
| ② ROI / 运营经济学 | 可预测账单 + 可预测运营结果 > demo |
| ③ AI 时代工程方法 | 编码变便宜，边界设定更值钱 |

## 主线脊柱（60 秒版 → 细节见 `03`）

> We started with a practical retrieval problem. User requests were often messy, ambiguous, or underspecified, which hurt retrieval quality and wasted downstream cost. So I first designed an intention-recognition layer that does deterministic cleanup, lightweight interpretation, confidence-aware clarification, and graceful fallback.
>
> The bigger insight was that this should not stop at retrieval. Once a system can decide whether a request is clear enough to proceed, it is already becoming the front half of a broader orchestration layer. In that architecture, RAG becomes one capability rather than the default path.
>
> The key boundary is that the model proposes, but the harness decides. The harness owns permissions, policy, risk, and execution control. Today the strongest implemented part is the intention-recognition layer, and the orchestration layer is the path for growing that into a governed platform over time.

三层次：个体工具 → 多工具/编排 → 治理/架构/审计。答具体题时点出"我在哪一层"。

## 五步回答结构（技术题）

最小改动解眼前 → 分层=fail-fast 边界 → harness 是治理边界 → 演化成 request orchestration → 指标拆分归属明确。

## 真实案例记忆锚点（30–60 秒/个 → 口语版见 `04`）

1. 意图层 fail-fast + 人工回退：多一轮确认 < 快速错答
2. 文档解析严格验收：无 ground truth 用代理质量门
3. 非对称置信阈值：读低写高（动钱 ~99%）
4. 证据优先辅助人工：AI 分析，人保留决策权
5. 中央工具注册表：RAG/意图/API 都是 tool，声明 schema+owner
6. 正交置信度 + 结构化确认：≤3 选项
7. UAT vs 生产代理指标：离线 recall/precision，线上确定性代理

## 高频题一句话速答（→ 展开见 `05`）

- 最难：把概率系统塞进确定性机构边界
- 银行错哪：一个信任模型套所有场景
- agents？：只信有界自主（模型提议，确定性系统握权限）
- 受监管工作流：确定性路由→风险分类→模型提议→正交校验→执行/人工批准
- 先做哪些：读为主、高频、低责任
- ROI：可预测账单 + 可预测运营结果
- 可解释性：控制路径可解释 > 权重可解释
- hallucination：当永久属性架构化处理
- 模型变强？：更强反而更需治理
- 经验跨度：单工具 → 编排 → 治理/审计，聚焦递进线

## 被 push back 保命句

- That is fair. My view would change if...
- I would handle that differently for low-risk and high-risk cases.
- In a bank, over-trust is usually more expensive than under-automation.

## 收尾观点

> Bank AI deployment is not primarily a model problem. It is a control-plane, workflow, and ROI problem. The architectures that win will not be the ones with the most autonomy, but the ones that place probabilistic intelligence inside deterministic institutional boundaries.

## 最后 3 个提醒

1. 3 个核心观点练熟：控制面先于能力 / 可预测账单 / 边界设定比编码更值钱。
2. 避免：长独白、堆术语、泛 hype、答非所问；组织（≤10 人互信）与经济（只有框架没数字）都要诚实限界。
3. 他记住的不是你的知识量，而是「这个人有判断力」。

## 指针

- 定位/组织层/诚实边界 → `01`
- 三桶深度 + 答题骨架 → `02`
- 脊柱细节 + 深潜（orchestration / RAG 经济学）→ `03`
- 案例口语版 → `04`
- 12 强答案 + 短语库 → `05`
- Mock 演练 + 红标记 → `06`
