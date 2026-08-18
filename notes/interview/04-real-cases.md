# 04 — Real Cases（真实案例速记）

> 把原则变具体：30–60 秒/个。回答具体问题时引用。
> 对应旧版 `hsbc-head-of-ai-interview-prep.md` 的 Real Trials 部分与 fast-recall §7。

## 使用模式：原则 → 案例 → 设计选择 → 权衡 → 教训

用真实 trial 证明判断，而不是倒项目细节：

1. state the principle（先说原则）
2. give one real trial（给一个真实试验）
3. explain the design choice（解释设计选择）
4. explain the tradeoff you were managing（解释你在管理的权衡）
5. end with the operating lesson（以运营教训收尾）

公式：

> My bias is X. In one trial, we handled it by Y. The reason was Z. The tradeoff was A versus B. What I learned is C.

压缩版模板：

> One thing I learned from real trials is that fail-fast and fallback design matters a lot. For example, in an intent workflow, if the model found the probable intent but did not clear the risk-adjusted threshold, we would not keep pushing the model. We moved into explicit user confirmation, and if ambiguity remained, we escalated to a human. That was really about balancing customer experience, cost, and auditability rather than maximizing automation for its own sake.

## 案例总表

| # | 案例 | 记忆点 |
|---|---|---|
| 1 | 意图层 fail-fast + 人工回退 | 多一轮确认比快速错答便宜；有界失败 > 最大化自动化 |
| 2 | 文档解析严格验收 | 无 ground truth 用代理质量门；生产不达标自动回退 |
| 3 | 非对称置信阈值 | 读操作低阈值、写/动钱接近 99%；不过线→结构化确认→人工 |
| 4 | 证据优先辅助人工 | AI 做分析、给摘要/风险点/引用，人保留决策权 |
| 5 | 中央工具注册表 | RAG/意图/API 都是 tool，声明 schema+owner→可追溯可审计 |
| 6 | 正交置信度 + 结构化确认 | 不只用 LLM 自我判断；≤3 选项让用户确认 |
| 7 | UAT vs 生产代理指标 | 离线有 ground truth 用 recall/precision；线上用确定性代理信号 |

## 案例 1：Fail-fast 设计 + 人工回退（桶 ①）

> My design bias is to fail fast when confidence drops below the operational threshold, especially in customer-facing or high-liability workflows. In one trial, I prioritized fast fallback to human agents instead of allowing repeated low-confidence retries. The reason was that in banking-style workflows, a slow wrong answer is often worse than a fast escalation. The tradeoff is slightly more human involvement, but you gain tighter cost control, better auditability, and lower customer frustration.

意图层版本的打磨版：

> One thing I learned from real deployment work is that fail-fast design matters a lot. In one intent workflow, if the system could not establish intent at the required confidence, I did not want it to keep guessing or burning tokens downstream. I would rather add one clarification turn or escalate early. My bias is that in customer-facing flows, one extra turn is cheaper than a fast wrong answer that damages trust, creates audit issues, and increases rework later.

这展示：UX 与成本一起想、理解有界失败、不只优化模型自主。

## 案例 2：文档解析严格评估 + 回退（桶 ① / ③）

> In a document parsing trial, I did not want to treat a good-looking output as production-ready by default. In offline preparation, I used strict output evaluation and a double-language consistency check as a proxy quality gate where ground truth was incomplete. The model had to clear a predefined benchmark before I would trust it for production. Then at runtime, if the output fell below the acceptance signal, the system would fall back instead of forcing a weak parse through downstream steps. The point was to protect reliability and auditability, not just push automation rate higher.

措辞注意：避免把 "cross-validation" 说成正确性证明，要说成代理质量门/一致性检查（ground truth 不完整时）。

## 案例 3：非对称置信阈值（桶 ①，最强例之一）

> In intent recognition, one thing we found was that recognizing the likely intent was not enough. The confidence threshold had to depend on the risk class. For low-risk read actions, a lower threshold was acceptable. But for high-risk write actions, especially anything close to money movement, the bar had to be much higher. If confidence did not clear that bar, we moved into structured user confirmation, and if ambiguity remained, we escalated to a human agent. That design was really about balancing customer experience, auditability, and the asymmetric cost of being wrong.

可加的成本角度：

> I also liked putting this gate at the intention layer because it prevented the system from wasting downstream tokens on a flow that had not yet earned the right to proceed.

这展示：理解 risk-tiering、能把概率翻译成 workflow 设计、超越原始模型精度思考。

## 案例 4：证据优先辅助人工（桶 ① / ③）

> In harder cases, I do not think the best use of AI is to replace the human decision-maker. I think the better use is to reduce human cognitive load. In one workflow, the AI analyzed the case, summarized the situation, highlighted what needed attention, and quoted the relevant supporting documents. The human agent still owned the decision, but they could act much faster and the customer did not need to repeat the whole story. To me, that is a very practical form of AI leverage in regulated environments.

## 案例 5：中央工具注册表（桶 ①）

> Another design choice I liked was putting all capabilities behind a central tool registry, including RAG, intent recognition, and API calls. Each tool had to declare its schema and ownership. That gave us much better governance because we could see which tool was selected, what confidence justified the choice, and how the component was performing over time. It also made the operating model cleaner, because each team could own its tool instead of hiding everything inside one opaque agent flow.

## 案例 6：正交置信度检查 + 结构化确认（桶 ①）

> On confidence scoring, I do not like relying only on the model's own confidence or even a second LLM judging the output, because both can be correlated and expensive. In practice, I prefer to combine probabilistic signals with orthogonal checks, for example deterministic distance or correction-based signals. If confidence still does not clear the required threshold, I would rather use a lightweight user confirmation step, ideally with at most three explicit choices, than let the model keep guessing. That gives you a much cleaner balance between control and user experience.

## 案例 7：UAT 指标 vs 生产代理指标（桶 ③ / ①）

> One distinction I care about a lot is the difference between UAT evaluation and production gating. Offline, if I have ground truth, I can use metrics like recall and precision, and even use an LLM judge for things like faithfulness against retrieved evidence. But in production, I usually do not have ground truth at decision time, so I need proxy metrics and deterministic signals that can be measured live. I think teams often confuse those two evaluation regimes, and that creates a lot of false confidence.

## 这些案例的共同元论点

> The design problem is not just making the model work. It is balancing user experience, cost, auditability, traceability, and probabilistic uncertainty in a controlled operating workflow.

这正是资深 AI leader 更可能尊重的观点。

## 避免讲太细

- 每个真实案例控制在 30–60 秒
- 结构：问题 → 设计选择 → 阈值/门 → 回退路径 → 为什么重要
- 不要让细节淹没判断
