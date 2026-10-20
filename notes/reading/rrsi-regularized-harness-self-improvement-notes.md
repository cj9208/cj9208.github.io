# 自进化也会过拟合：RRSI 给 Harness RSI 施加正则化，与"优化优化过程本身"的递归结构

> 源文：《RSI火了，但自进化也会过拟合：Google等提出RRSI，给自进化施加正则化》，机器之心，2026-10-06。
> 论文：RRSI (Regularized Recursive Self-Improvement of Agent Harnesses)，Google Research，arXiv:2609.24972。项目页 https://regularized-rsi.com/ ，GitHub https://github.com/google-research/rrsi 。
> 这是一篇读后梳理，不是翻译。主线一句话：**Agent Harness 的递归自我改进本质上是对有限 evolve tasks 的 adaptive search，因此必然遭遇 overfitting；RRSI 的解法不是限制 modification space，而是 regularize 搜索过程本身——在 Proposal 端控制每轮变更的复杂度与归因性，在 Selection 端用 noise-adjusted floor + cost-benefit gating + pruning 过滤伪进步。**
> 标注约定：§二（方法）、§三（证据）中的所有数字与机制描述均为**源文原样**。§四（我的评价）整节是**我的分析，非源文**。

## 一、问题

Agent 层面的 RSI 已有现实路径：不改模型权重，改 Agent Harness（Prompt、Control Flow、Tool、Memory、Skill、Context Management、Subagent）。闭环是：执行任务→观察失败→修改 Harness→再执行→再修改。

当 Harness 在同一批 evolve tasks 上被反复迭代（10 轮、30 轮），进化过程退化为对有限数据的 adaptive search，出现三类耦合问题：

1. **Benchmark-specific fitting** — 记住当前 benchmark 独有 pattern
2. **Evaluation noise chasing** — 把随机涨分误认为真实 improvement
3. **Complexity accumulation** — 不断加 instructions/context/recovery，用更多 test-time compute 换 evolve set 上的微弱提升

反直觉结果：evolve score 持续涨，离开 evolution set 后收益迅速缩水甚至消失。

## 二、方法（RRSI）

核心设计：不限制 Agent 能改什么（modification space 保持开放），而是 regularize "它怎么改自己"。把 Harness RSI 拆成 Proposal 和 Selection 两个环节分别施加正则。

**Proposal 端正则化：**

- 限制一次 self-improvement 同时塞入多少相互纠缠的修改（前期宽探索，后期窄归因）
- 保留完整 Evolution History（哪个 hypothesis 成功/失败、score 变化、cost）作为下一轮 search 的 evidence
- 搜索长期停滞时，把 capacity 转向此前较少探索的 Harness component

**Selection 端正则化：**

- Benchmark-specific 改动提前筛掉
- 落在 evaluation noise 范围内的涨分不写入永久状态（noise-adjusted floor）
- 额外增加的 Context/Token 必须用足够 Performance Gain 证明价值
- 长期没有贡献的机制直接 Prune

一句话：不是阻止 Agent 变化，而是要求每一个想永久留下来的变化都"证明自己"。

## 三、证据（源文数字）

**Ablation（Agentic Workspace）：**

| 方法 | Evolve Score | OOD Average | Policy Tokens/Trial |
|---|---|---|---|
| Unregularized Evolution | 92.8 | 40.3 | 3.80M |
| RRSI | 90.5 | 43.6 | 2.42M |

→ Evolve score 更高反而 OOD 更差、token 更贵。

**跨域迁移**（Harness 只在一个 benchmark 上 evolve，冻结后直接测未见 benchmark）：

- Coding: Terminal-Bench 2.1 → SWE-bench Verified 82.0→83.8
- Agentic Workspace: JobBench 36.0→40.7, GDPval 48.8→52.3, APEX-Agents 34.2→37.9
- Engineering Design: Frontier-Eng 17.7→22.0
- 最高 OOD improvement +4.7 points，held-out splits 全部提升

**30 轮进化曲线**（Gemini 3.5 Flash, Terminal-Bench 2.1）：

- Incumbent 从 64.6→78.7（+14.1）
- 30 轮中仅 10 个 candidate 被接受为新 incumbent
- 9 个 gain 不足，6 个 screening 阶段拒绝，2 个 smoke test 失败，3 轮无 proposal
- 存在 noise-adjusted floor：分数微变不足以证明真实进步

**Cost 比较**：RRSI 在 Agentic Workspace 上每 trial 约 2.42M Policy Tokens，Unregularized Evolution 3.80M。RRSI 处于"更少 Token、更高 OOD"区域。

## 四、我的评价（非源文）

1. **核心贡献的准确定位**：这不是一篇提出新能力的论文，而是一篇给已有能力施加约束的论文。它的贡献恰好就是"regularization"这个词在 ML 里的标准含义——不增加模型的表达力，而是限制搜索过程对有限数据的利用效率，以换取泛化。放到 RSI 语境下：不是让 Agent 改得更多，而是让真正有用的改动能被识别出来。

2. **递归结构**：RSI 本身是一个优化过程；RRSI 是对这个优化过程的优化——即 meta-optimization。这与 Dream-RSI 的思路同构（Dream-RSI 把已完成的探索历史冻结成 replay simulator，用离线 replay 来改进探索策略），只是 RRSI 的 meta 层更薄：它不学一个 world model，只用 engineering heuristics（noise floor、cost gate、pruning）做 Selection。

3. **与 Search Pathology 的镜像关系**：RRSI 的 "complexity accumulation" 正是 The Search Pathology 一文描述的 Goodhart's Law 在 harness evolution 层面的投影——scaling test-time compute on an imperfect proxy leads to over-engineering。区别在于 Search Pathology 讨论的是单次推理内的搜索退化，RRSI 讨论的是跨轮次自我修改的搜索退化。两者的解法方向也一致：不是限制搜索能力，而是硬化评估景观（harden the evaluation landscape）。

4. **局限**：实验只在 Gemini 3.5 Flash 上跑（单一 base model），evolution 轮次上限 30；当 task distribution 本身有 shift（而非纯 OOD）时，regularization 强度如何自适应调整未讨论；Selection 的 noise-adjusted floor 如何设定（固定阈值 vs 动态估计）文中未给出足够细节。

## 延伸阅读

- `notes/reading/dream-rsi-replay-simulator-notes.md` — 同为 Google 的 RSI 工作，但从 meta-strategy 角度切入：把发现历史冻结成 replay simulator 来离线改进探索策略。与 RRSI 互补——Dream-RSI 优化"往哪搜索"，RRSI 优化"搜索结果怎么筛选"。
- [The Search Pathology: Why Scaling Test-Time Compute Can Degrade Code Agent Quality](https://cj9208.github.io/blog/ai_study/search-pathology-test-time-compute/) — RRSI 的 "complexity accumulation" 是这篇所述 Goodhart's Law 在 harness evolution 层面的投影；两者解法方向一致（硬化评估而非限制搜索）。
- [Harness Engineering 合集](https://cj9208.github.io/blog/ai_study/harness-engineering/) — 定义了什么是 Agent Harness、为什么它是可靠性的关键层。RRSI 操作的正是这一层。
