# 评测是把"什么叫好"编译成代码：Airbnb《Eval-Driven Development》的方法咬合与私有壁垒

> 源文：《Eval-driven development: Lessons from evaluating GenAI at scale》，The Airbnb Tech Blog（Medium），2026-07-28，9 min read。作者 Rohit Girme, Dan Miller, Mia Zhao, Lifan Yang, Clint Kelly。原文：<https://medium.com/airbnb-engineering/eval-driven-development-lessons-from-evaluating-genai-at-scale-e817e5ae5788>
> 这是一篇读后梳理，不是翻译。主线一句话：**EDD 是 ML "先选 metric 再优化" 老逻辑的延续，但 GenAI 让 metric 本身从确定函数变成了需要 eval 的 model、让 failure mode 从 enumerated 变成了 discovered、让 "good" 从数学函数变成了产品 judgment——所以评测不再是 QA 环节，而是把"什么叫好"从模糊共识编译成可执行工件的过程，而这个工件本身也需要被持续 eval。**
> 标注约定：§二–§五 的机制、数字、rubric 例子、walkthrough 均为**源文原样**；§一中"EDD 相对 ML metric-first 的三个质变"、§六的 commoditized vs moat 判断、以及各处标"（我的分析）"的推论均为**我的分析，非源文**，不要当源文事实引用。

## 一、一句话主线 / 透镜

EDD 的形式很像 ML 老逻辑：先定 metric，再优化 model/prompt。文章自己也用了 ML 时代的工具——Cohen's kappa、Krippendorff's alpha、P/R/F1、cosine similarity、golden set（就是 holdout set 缩水版）、"一次一变量"（就是 ML 实验方法论）。但 GenAI 让这个老逻辑发生了三个质变（**我的分析，非源文**——源文没有做这个对比）：

**(a) metric 本身从"确定函数"变成"需要 eval 的 model"。** 传统 ML 里 F1 是纯代码，选好了就能算。这里 LLM-as-Judge 自己是个 model，要先与 human 校准到高80s-90s% agreement 才能用（§2.2.1）。你在优化 A，但 A 的评分函数 B 也需要被 eval；B 的 eval 又依赖 human ground truth C。源文原话："评估器和候选互相锐化直到双双稳定"——这是传统 ML 没有的层次。

**(b) failure mode 从"enumerated"变成"discovered"。** 传统 ML 的 failure taxonomy 基本已知（overfit / class imbalance / drift），选 metric 是在已知空间里取舍。这里 §4 walkthrough 的 15/8/5/3 条错误——faithfulness、verbose、over-refusal、broken JSON——是读 100 条数据才发现的，事先不知道。§1.2 原话很硬："Rather than predicting every failure upfront, EDD builds the infrastructure and habits to **discover, encode, and continuously test** for failure modes as they appear."

**(c) "good" 从"数学函数"变成"产品 judgment"。** F1 vs precision vs recall 反映业务偏好，但都在同一个数学空间里。这里"friendly travel agent" tone、"内部术语不能用"、"结尾必须句号不能感叹号"——这些不是数学函数，是产品人反复拍板出来的 judgment。所以 EDD 五原则里必须"Appoint a decision-maker"、PM 要定期回答"X 比 Y 好还是差"、"evaluation is a team sport"。传统 ML 不需要 decision-maker 这个角色。

三条加起来，EDD 的主线就是：**把"什么叫好"从模糊共识编译成可执行工件（rubric + golden set + VJ + trace eval），而这个工件本身也需要被持续 eval（calibration loop + production sampling）。** 编译的产物是可版本化的代码/数据，编译的过程是产品判断的显性化。

## 二、域背景：GenAI 评测为什么难（源文 §Intro + §1）

源文 Introduction 给了三条根因：

- LLM 输出**非确定性**，"correct" 是主观的
- 需要**用 AI 评 AI**，引入新的 failure mode
- 单次交互可以链式调用 retrieval、reasoning、tool call、generation，**每一环都能独立失败**

没有评测策略时会撞的三堵墙（§1）：

- **False confidence**：泛"helpfulness"指标分数好看，上线后才发现没覆盖真实 failure mode
- **Undetected regressions**：prompt 改一动，某个没在测的维度悄悄退化
- **Wasted effort**：给一个跟结果不相关的指标建了规模化 pipeline

源文原话："Expect to spend a meaningful share of your total project effort on evaluation. This is not unnecessary overhead, it's how you build products that actually work."

Airbnb 的组织形态（§Intro）：产品团队（review highlights、AI customer support、smart communication for guests/hosts 等）各有自己的评测标准/流程/workflow，但都建在**一个 infrastructure 团队提供的共同基础**上——tooling + best practices + 跨域学习沉淀。这篇文章就是这个 infrastructure 团队的输出。

## 三、困难↔方案咬合（按评测生命周期分四组）

### 起手：从"看数据"到"三层栈"

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 事先不知道要评什么 | **100 条数据读输出 + 读 trace**，分类错误，再建 eval（§1.1） | 源文原话："This single habit will do more for your product quality than any framework, tool, or methodology in this document." |
| 凭空发明的指标与产品目标不相关 | **让真实错误引导指标**，与跨职能伙伴共同定义（EDD 原则 2） | 指标必须从观察到的 failure 里长出来，不是从抽象的"quality dimensions"里推出来 |
| 一个评估器什么都想管 → 噪声大 | **3–5 个校准良好的 LLM-as-judge > 20–30 个噪声评估器**，每个只管一个 correctness 维度（EDD 原则 3） | 一维一评估器，rubric 才能写得足够锐 |
| 团队对"good"分歧 | **Appoint a decision-maker**（EDD 原则 4）——最终由一个 human 拍板 | "good" 不是数学函数，需要 judgment；judgment 需要 accountability |
| 专家自己都分歧 | **停下，先解决人的分歧再自动化**（§2.4） | 人都 calibrate 不了的 rubric，LLM 更 calibrate 不了 |

起手原则一句话：**从数据里发现指标，用小而锐的评估器集合编码它，用一个 decision-maker 兜底判断分歧。**

EDD 五原则完整列表（§1.2，源文原样）：① Define goals and gates upfront；② Let real errors guide your metrics；③ Keep your evaluator set small and sharp；④ Appoint a decision-maker；⑤ Collaborate continuously（PM 定期回答"Is X better or worse than Y?"和"What's actually wrong with this output?"）。

### 让 LLM-as-Judge 可信：rubric + calibration

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| VJ 未校准 → 给假信心 | **golden set 50–100 条，必须含 bad examples** → 跑 VJ → 目标 agreement **高80s–90s %**（Cohen's kappa / Krippendorff's alpha）→ 分析分歧 → 改 rubric + few-shot → 循环 → 定期重校准（§2.2.1） | 源文原话："A virtual judge that hasn't been calibrated is worse than no judge at all, because it gives you false confidence." |
| rubric 模糊 → 人类都 apply 不了 | **Ambiguity is the enemy**：明确列 error types、binary/有序 score、few-shot examples、显式 output schema（§2.2 五规则） | 源文原话："if a human can't apply the rubric consistently, an LLM certainly can't." |
| judge 与 generator 同源偏差 | **judge 用不同的 model**，配 chain-of-thought（§4 Step 2） | 同模型自评会共享盲区 |
| VJ 与 human 分歧仲裁 | **Human eval 是 gold standard**，用于 ground truth 生成、safety/high-stakes、nuance & creativity、评估器分歧仲裁（§2.3） | 三层栈的最上层，校准下面两层 |
| 规模化标注的时机 | **起手 20–100 条 SME 标注**；只有 rubric 稳固、量成为瓶颈时才上规模化标注团队（§2.4） | rubric 没稳就规模化，等于把噪声放大 |

VJ 层原则一句话：**VJ 不是"写一句 criteria 求 LLM 理解"，是一个需要被 eval 的 model——它的 rubric 要锐到人类能一致 apply，它的输出要与 human 校准到高80s-90s%，它的校准要随 failure mode 演化定期重做。**

§2.2 五规则（源文原样，从图示读出）：one evaluator per dimension、different judge than generator、few-shot examples、explicit output schema、clear scoring。

源文给了一个完整 rubric 例子（Airbnb listing explanation 可读性，§2.2）：binary 0/1，5 类 error（tone、internal terms、formatting、grammar、complexity），3 条 few-shot，JSON 输出 `{reason, score}`。"friendly travel agent: warm but professional, simple, natural, grammatically complete" 是 tone 的锚点；"结尾必须句号，不能 ! 或 ?" 是 formatting 的硬约束；"用 pool 不用 aquatic recreation area"、"用 near 不用 proximate" 是 complexity 的具体化；"a backyard, grill, and kitchen"（系列里 article 只用一次然后省略）是 grammar 的具体化。这些**都是产品判断的显性化**，不是数学函数——正是 §一 (c) 的具体化。

Programmatic 层（§2.1）的检查类型（源文图示）：format validity（JSON/schema，always）、length & presence（empty/suspicious lengths，always）、keyword/regex（forbidden words，safety/compliance）、classical ML metrics（P/R/F1，classification）、semantic similarity（cosine，有 gold ref 时）。Do：structured output + JSON schema 强类型；Don't：只靠 prompt 约束格式（会 break downstream data pipelines）。

### Agent 系统：step / trajectory / session 三层

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 正确 final answer 可能掩盖 broken reasoning path / 错的 tool params / 低效 trajectory | **三层评测**（§3）：step-level（单次 tool call / 推理步）、trajectory-level（整条路径是否合理高效）、session-level（整场交互是否达成用户目标） | 只评 final output 不够 |
| trace 结构复杂，怎么 scope 到特定 agent/subagent | agent 把 trace/span 推到 **application root**（含 agent 类型、子 agent、I/O、调用的工具），写到 observability platform 或持久化存储；然后 **DFS 或树遍历**在内存里重建 trace | 重建后就能验证子 agent 调用时机、工具选择、并 scope 评测到特定 agent/subagent |

Agent 层原则一句话：**评的是系统不是模型；评的是轨迹不只是终点。**

### 迭代与生产：一次一变量 + 持续抽样

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 迭代时变量耦合，分不清是谁的功劳 | **一次固定一个变量**（§4 Step 3 NOTE）：先固定 model 变 prompt，再固定 prompt 变 model，再固定两者变 serving config | VJ 结果收窄候选池；再用 top 候选的样本改进 VJ——**评估器和候选互相锐化直到双双稳定** |
| 生产 failure mode 会演化 | **每日抽样 5% de-identified 流量**跑 programmatic + VJ；flagged 输出交人审；**每周 PM review** 闭环——新 failure mode → 新 eval → 系统改进（§4 Step 4） | 源文原话（Key takeaways）："Mirror evals in production. Pre-production metrics are not one-and-done." |
| 隐私 | 持续抽样用 **privacy-preserving 技术**，所有数据 **robust de-identification** prior to human review，usage **strictly purpose-limited** to safety and quality assurance，符合 Airbnb Privacy Principles | 生产 eval 的前提是数据合规 |

迭代/生产层原则一句话：**评测不是一次性的 gate，是一个持续运行的闭环——evaluator 和 candidate 互相锐化，生产流量持续注入新 failure mode。**

## 四、标杆案例：travel policy 问答助手（源文 §4，fictionalized real use case）

把整个流程走一遍，每一步对应到用了哪个能力：

**Step 1 探索（100 条）**——读输出、分类错误：

- **15** 条生成了源文档里没有的政策细节 → **faithfulness issue**
- **8** 条正确但太啰嗦 → **conciseness**
- **5** 条拒答了合理问题 → **over-refusal**
- **3** 条 JSON 坏了 → **format**

这一步对应 §1.1 "look at your data" 和 EDD 原则 2 "let real errors guide your metrics"。**四类错误事先都不知道**——这就是 §一 (b) failure mode 从 enumerated 变成 discovered 的具体化。

**Step 2 建 evals**：

- **Programmatic**：JSON 合法性 + 长度界限
- **VJ for faithfulness**：separate prompt、different model、chain-of-thought
- **VJ for conciseness**：另一个独立评估器
- **Golden set**：PM/SME 标 **60 条**（含 failures）

这一步对应三层栈的 Layer 1 + Layer 2 + Layer 3（human 做 golden set）。**一维一评估器**：faithfulness 和 conciseness 分开，不糊成一个"quality"评估器——正是 EDD 原则 3。

**Step 3 校准**：

- faithfulness VJ 与 PM agreement **78%**——不够（目标高80s-90s%）
- 分析：VJ 把"准确的改写"当不忠实
- 改 rubric + 加 few-shot examples → agreement 跳到 **88%**
- 改 retrieval step → faithfulness failures 显著下降

这一步对应 §2.2.1 calibration loop。**78% → 88% 是源文逐字数字**。注意这里同时动了两个东西：VJ 的 rubric（让评估器更准）和 retrieval（让系统更 faithful）——这就是"评估器和候选互相锐化"的具体形态。

**Step 3 附带的迭代纪律（NOTE，源文原样）**：一次固定一个变量（model → prompt → serving config），VJ 收窄候选池，再用 top 候选样本改进 VJ。源文还配了一张图：三个迭代 workflow 都用 fixed Virtual Judges 测 latency 和 serving performance，每个流程都有 feedback loop。

**Step 4 规模化 + 生产监控**：

- eval 扩到 **5,000 条**
- 生产上**每日抽样 5% de-identified 流量**跑 programmatic + VJ
- flagged 输出交人审
- **每周 PM review** 闭环

这一步对应 §2.4 "move to scaled annotation workforce only when rubric is rock-solid" 和 Key takeaways "Mirror evals in production"。

## 五、效果（源文逐字数字）

- faithfulness VJ 与 PM agreement：**78% → 88%**（改 rubric + few-shot 后）
- golden set：**60 条**（PM/SME 标注，含 failures）
- 校准目标：**高80s–90s %** agreement（Cohen's kappa / Krippendorff's alpha）
- 起手数据量：**100 条**（探索）；**20–100 条**（SME 标注起手）；**50–100 条**（golden set for VJ calibration，必须含 bad examples）
- 规模化 eval：**5,000 条**
- 生产抽样：**每日 5% de-identified 流量**
- 评估器数量建议：**3–5 个**校准良好的 VJ > **20–30 个**噪声评估器
- PM review 频率：**每周**

Key takeaways 完整 10 条（源文原样）：① Look at your data；② Avoid generic metrics；③ Start with 50–100 rows；④ One evaluator per dimension（no "God evaluators"）；⑤ Calibrate to high 80s-90s% agreement；⑥ Use all three methods as layered defenses；⑦ Include bad examples in Gold Set；⑧ Evaluate the system, not just the model（agents → trajectory, not only final answer）；⑨ Mirror evals in production；⑩ Evaluation is a team sport——"The teams that succeed with AI aren't the ones with the best models, they're the ones with the best communication and clearest product vision."

## 六、收束：commoditized vs moat

**可复制的通用件（方法论层）**：

- 三层评测栈（programmatic / LLM-as-Judge / human）
- EDD 五原则（goals & gates upfront / real errors guide metrics / small & sharp evaluator set / decision-maker / continuous collaboration）
- golden set + calibration loop（50–100 条、含 bad examples、高80s-90s% agreement、Cohen's kappa / Krippendorff's alpha）
- 一次一变量的迭代纪律（model → prompt → serving config）
- Agent 评测三层（step / trajectory / session）+ trace DFS 重建
- 生产 5% 日抽样 + 每周 PM review 闭环

这些是任何做过 GenAI 产品的人都能照搬的方法论，没有秘密。文章自己也说："the recommendations here are not intended to be prescriptive; there is no one-size-fits all approach when it comes to running evals."

**不可复制的壁垒（私有层）**：

- **你产品自己的 failure mode 目录**——Airbnb 的 15/8/5/3 是 travel policy 问答的，你的产品是另一组
- **你的 golden set**，尤其是 bad examples——这是 SME 判断力的物化，复制不走
- **rubric 里的领域约束**——"friendly travel agent" tone、"internal terms 不能用"、"结尾必须句号"、"用 pool 不用 aquatic recreation area"——这些是产品判断的显性化，不是通用模板
- **SME 判断力 + PM decision-maker 文化**——源文原话："The teams that succeed with AI aren't the ones with the best models, they're the ones with the best communication and clearest product vision."
- **生产 trace 数据 + privacy-preserving 抽样管道**——这是基建，不是方法论
- **每周 PM review 的组织习惯**——闭环能跑起来的前提是产品人真的每周来看

**收束**：方法论是通用的，但**"什么叫好"是产品/领域私有的**。评测栈就是把这个私有的"好"编译成可执行工件（rubric + golden set + VJ + trace eval）的过程。编译的产物可版本化、可 CI、可监控；编译的过程是产品判断的显性化。所以 EDD 的真正壁垒不在"知道三层栈"，而在**你的 golden set 有多锐、你的 rubric 有多具体、你的 PM review 有多频繁**——这些都是日复一日的 context 工程，复制不走。

迁移到其他域的通用启示：**先读 100 条数据发现 failure mode，再用一维一评估器编码它，用 50–100 条 golden set 校准 VJ 到高80s-90s%，用一次一变量的纪律迭代，最后在生产上镜像 eval 并每周闭环。** 模型会持续变强，红利只留给那些已经把"什么叫好"编译成可执行工件的人。

---

## 延伸阅读（本仓）

- `notes/reading/jev-deepeval-judgment-model-notes.md` — 同一个问题（LLM-as-Judge 不可靠）的另一个方向：Airbnb 选择**校准 VJ**（与 human 对齐到高80s-90s%），JEV 选择**换掉 VJ**（用非语言判断模型返回 typed probabilities）。两者都承认"评估器本身需要被 eval"，但解法不同——Airbnb 的 calibration loop 是工程习惯，JEV 的 System One 是模型替换。对照读能看清"VJ 校准"这条路的边界：它把 variance 从"prompt 玄学"变成"confidence + threshold 的工程参数"，但没消除 LLM-as-Judge 的 cost/latency 结构问题。
- `notes/reading/kuaishou-conan-stability-agent-notes.md` — 同为"方法即通用件、Context 才是壁垒"的收束。快手的 Bad Case 驱动闭环 = Airbnb 的每周 PM review 闭环；快手的 Skill 承载私域知识 = Airbnb 的领域特定 rubric；快手的"确定性归代码、概率性归模型" = Airbnb 的三层栈（programmatic / VJ / human）。两篇都收敛到同一个判断：方法论早熟了，难的是把 context 工程日复一日做下去。
- `notes/reading/rrsi-regularized-harness-self-improvement-notes.md` — Airbnb §4 Step 3 NOTE 的"评估器和候选互相锐化直到双双稳定"正是 harness RSI 的一次迭代。RRSI 提醒：这个循环本身会 overfit（benchmark-specific fitting / evaluation noise chasing / complexity accumulation），需要 regularization（noise-adjusted floor、cost gate、pruning）才不会退化成 Goodhart。Airbnb 的"每周 PM review + 生产 5% 抽样"可以看作一种工程化的 regularization——用持续注入的新 failure mode 防止 eval 集过拟合。
- `notes/reading/sift-self-improvement-fast-tree-search-notes.md` — SIFT 的核心是"用便宜 judge 排序、昂贵评估只投给 rank 靠前的"，这是 Airbnb "3–5 校准良好的 VJ > 20–30 噪声评估器" + "golden set 校准 VJ" 的极端化版本。SIFT 明确说 judge "most useful when it comes to providing a ranking signal rather than as a surrogate for benchmark accuracy"——这与 Airbnb 让 VJ 逼近 human 的路线相反：Airbnb 要 VJ 的绝对分可信，SIFT 干脆放弃绝对分只用 rank。对照读能看清"VJ 校准到高80s-90s%"这个目标的代价与替代方案。
