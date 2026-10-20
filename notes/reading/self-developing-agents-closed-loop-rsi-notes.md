# 半环到闭环：自进化 Agent 的三处漏水，与"可见增益 ≠ 真实改进"——一篇站在 RSI 集群之上的审计

> 源文：《Self-Developing Agents — From Half-Loop to Closed-Loop RSI》，ByteDance Seed + TokenWave，2026-09-01，研究观点页。原始 URL <https://self-developing-agents.github.io/>。三个 benchmark：Aspire、S³Gym、HarnessDev。
> 这是一篇读后梳理，不是翻译。主线一句话：**今天大多数"递归自我改进（RSI）"系统是"半环"——它们偷偷假设了一个"黄金验证器（Golden Verifier）"在替模型把关方向；真正的"闭环 RSI"必须自己回答三个问题（目标从哪来、经验怎么学、改进怎么留存），而这篇用三个 benchmark 的负面证据证明：这三环目前每一环都在漏水，且漏的是同一件事——可见增益 ≠ held-out 上的真实改进。**
> 标注约定：§二–§五 的所有数字、机制、模型名、benchmark 设定均为**源文原样**（源文用的模型名如 Opus 4.8 / GPT-5.5 / Gemini3.1 Pro / Qwen 3.7Max / DeepSeekV4 Pro 等均照抄，未替源文核对真伪）。§六（审计层：对照本仓 RSI/eval 集群、"之前的方案为什么走得通"）整节是**我的分析，非源文**——源文没有提到 SIFT/Dream-RSI/RRSI/JEV/Airbnb 中的任何一个。§一里"审计层定位"那段、§七收束里的跨篇综合，也是**我的分析**，已就地标注。

## 一、透镜：先把"半环 vs 闭环"钉精确

核心不变量只有一句：**半环 RSI 假设了一个不会出错的方向裁判（Golden Verifier），闭环 RSI 必须自己造出这个裁判——而造裁判这件事，恰恰是今天最不成立的一环。**

源文把"像人一样学习改进"拆成三个问题，这三问就是后面全部结构的脊柱：

1. **一个宽泛、模糊的目标，怎么变成具体行动？**（目标从哪来）
2. **没有老师，能否判断自己行为的好坏、并从中学习？**（经验怎么学）
3. **经验怎么变成"行动方式"的一部分并留存下来？**（改进怎么持久）

三问分别对应三层、三个 benchmark。源文的整体判断是悲观的：不是"再堆一个机制就能闭环"，而是"用隐藏评测/held-out 一照，现有每一环的可见增益都大面积蒸发"。

**这篇在本仓 RSI/eval 集群里的定位（我的分析，非源文）**：已有的五篇笔记（SIFT、Dream-RSI、RRSI、JEV、Airbnb EDD）每篇都是**让闭环某一段能转起来**的机制提案；这一篇不是第六个机制，而是**站在闭环之上做体检的"审计层"**——用同一把手术刀（可见增益 vs held-out 增益）证明三段都在漏水，反过来解释了集群里那些成功案例**为什么走得通**。详见 §六。

## 二、框架：三个问题 = 三层 = 三个 benchmark（源文原样）

| 层 | 问题 | Benchmark | 测什么 |
|---|---|---|---|
| **01 TARGET 目标形成** | Agent 该改进什么？宽泛模糊的目标能否落成具体行动？ | **Aspire** | 给一个模糊目标（如"提升数学推理"），**不透露下游任务与最终评测**；看 agent 自建的目标能否迁移到**隐藏评测** |
| **02 EXPERIENCE 经验整合** | 没有老师，能否判断自己行为的好坏并从中学习？ | **S³Gym** | 拆成 Self-Testing / Self-Judging / Self-Improvement，七个有可执行验证器的游戏；看经验能否迁移到 held-out 条件 |
| **03 SYSTEM 系统整合** | 改进能否**持久**？ | **HarnessDev** | 让模型造一个可运行的 agent harness，再用下游执行反馈进化它；看改动能否泛化到 held-out、固定 executor 下进化是否还成立 |

三个 benchmark 各自还提供一件"可复用的测试"（源文"What the benchmarks provide"）：Aspire 把**隐藏评测**与**可审计轨迹**配对；S³Gym 把探索与严格 held-out 评测分开、并用**可执行验证器**核对自评；HarnessDev **冻结可运行工件**再测 held-out 泛化，Creation 阶段用 Unified-Eval 做跨 executor 可移植、Evolution 阶段在**固定 Gemini executor** 下跑独立 lineage。

## 三、三处漏水（核心，源文逐字数字）

### 01 TARGET / Aspire —— 搜索变了，但目标没被验证

**问题**：给模糊目标后，agent 会把预算花在"解释目标、选代理指标"上，而不是训练与评测——这是"更多目标操作化（target operationalization）"，不是"更好的目标"。agent 能完成一次更新，却没改进它本想改进的能力。

**证据（源文）**：
- 30 个"配置×目标"cell：**28** 产出可评估 checkpoint → **21** 合格 → **2** 超过 base 模型 → **只有 1 个**过了保留阈值被留下（"1 retained gain / 30 cells"）。
- 模糊目标 − 明确任务（48 对匹配的 Opus 4.8 run pair，每分钟/每对）：决策思考 **+35**、GPU 空闲 **+37**、主动训练/评测 **−76 / −60**。
- 轨迹密度比（每万字符，模糊/明确）：读任务定义 **2.98×**、看评测脚本 **2.39×**、LoRA/PEFT 活动 **3.09×**；**LoRA 使用率 24.1% → 89.8%**。
- 局部涨、全局退（Qwen3.5-4B Self，隐藏评测数学分）：unevolved base **17.86**，三个 self-trained checkpoint 分别 **0.79 / 1.75 / 2.38**，最优 CK **−15.48 vs base**。

**源文自己的证据边界**：这是 48 对匹配 run 的描述性比较，不是隔离的"纯 prompt 效应"；轨迹密度只说明"力气往哪移"，不能证明最终分差的因果。

### 02 EXPERIENCE / S³Gym —— 没有普适的经验通路

**问题**：经验能否改进"下一个决策"？自评靠谱吗？记忆该用原始 history 还是 summary？

**证据（源文）**：
- **自评几乎不预测下一次增益：ρ = −0.010 和 −0.018。**
- 原始 history ICL vs summary memory **谁赢随游戏变、随归一化方式变**：raw AUC+ 下 Summary 领先 3 个游戏、History 领先 3 个、Tetris 打平；换成 baseline-normalized **NABA**（= AUC+ / max(y₀, ε)，覆盖 49 对匹配的 model–game），Summary 领先 Nullify/Tetris/Trust、History 领先 Minesweeper/Snake/PvZ、Chess 3–3–1 分裂。**换归一化，连"打平发生在哪个游戏"都从 Tetris 移到 Chess。**
- 参数更新也不稳：Trust 在 19 个 checkpoint 里 **18/19 高于基线**（max 30，AUC+ 163.5）；**PvZ 从 23 掉到 6，19/19 次更新都停在 6**（源文注明：PvZ 的持续退化"原因未知"）。

**结论（源文）**：证据不支持任何单一默认通路——要**按环境选 pathway，并在 held-out 决策上确认**。

### 03 SYSTEM / HarnessDev —— 代码里有机制，运行时是死的

**问题**：一个能跑的 harness，是否等于一个"机制真的在运行"的 harness？进化改的东西能否泛化？

**证据（源文）**：
- LLM 造了 **18 个 Code harness，全部能跑**；但 **18/108 个组件在正式执行中从未出现——全是 state / memory 类**。
- **26,679 条任务轨迹里，checkpoint 事件 = 0**；state class 定义 11/18、state-save 接口 **1/18**、周期性 checkpoint **1/18**。
- 进化时 agent 主要改执行流/工具，几乎不碰让改进持久的部件（64 次官方版本切换，类别有重叠）：Execution/control **58**、Tools **37**、Lifecycle recovery **17**、Context **16**、State **4**、Standalone verifier **0**。
- **可见增益 ≠ held-out 增益**：visible feedback 与 held-out 只在 **34/64** 次可比切换上方向一致（**53.1% direction agreement**）；**9 个 declared final 版本里只有 2 个是 held-out 最优**。
- 固定 executor 的残酷测试（四次独立进化，全程用 Gemini 当 executor，各自从 H₀ 到 declared final 的 held-out-630 增益）：**Opus 4.8 +2.70，其余三个退步——Qwen 3.7Max −1.11、DeepSeekV4 Pro −2.38、GPT-5.5 −10.32**。（九条单轨迹 · 73 个官方版本 · 64 次相邻切换；post-freeze held-out 只覆盖 SWE-Pro。）

**源文自己的证据边界**：Creation 分析覆盖 18 个 Code 工件；"被触发"不等于"有用"；进化类别互相重叠。

## 四、"该保留什么"：三条验证纪律（源文，非银弹）

源文没给银弹，给的是三条纪律，每条都由对应 benchmark 的负结果逼出来：

1. **目标要在 agent 看不见的评测上验**（hidden evaluation）——因为 21/30 合格 checkpoint 里只 1 个留下真增益，可见分数的涨（LoRA 24.1%→89.8%）只证明"搜索变了"，没证明"目标对了"。
2. **经验要在"下一个决策"上验，且按环境选 pathway、用 held-out 确认**——因为自评 ρ=−0.010/−0.018 几乎零预测力，且换归一化就重排赢家。
3. **进化要在固定 executor 下的 held-out 任务上验，且只保留带版本管理 + 回滚的改动**——因为可见/held-out 只 34/64 一致、9 个 final 只 2 个最优、固定 executor 下四个里三个退步。

一句话（源文"What these results mean in practice"）：**"目标不是持续变化，而是知道哪些变化该保留。"** 一个有用的自进化 agent 必须在真实工作上变好、而不只在公开 benchmark 上刷分；必须适配组织的目标/流程/数据/质量标准，又不把每个局部 workaround 变成永久复杂度。

## 五、FDE 类比与研究目标（源文）

源文把闭环 RSI 类比成 **Forward-Deployed Engineering**：Platform（从通用平台起步）→ Discover（找到真实客户问题）→ Deliver（造出能用的解）→ Learn（抽出可复用的模式）→ Compound（把验证过的能力整合进去）↺。**最终判据是"复用"——下一个项目能不能用上这个结果。**

研究目标（源文）：**研究"长进一个角色里"的 agent，而不只是"完成一个任务"的 agent。** 给 agent 一个 role-level objective，问它能否推断"在这个组织里什么叫好工作"、从不完美反馈里造测试、随证据累积更新自己的 model / memory / harness。目标不是端到端替代一个 FDE，而是**把重复的 field work 沉淀成可复用能力**。

## 六、审计层：对照本仓 RSI/eval 集群——"之前的方案为什么走得通"（我的分析，非源文）

**这一节是本篇笔记相对源文的主要增量。源文没有提到下列任何一篇；所有对照都是我的分析。**

把这篇当"审计层"最大的价值，不是给集群再添一个机制，而是**反过来解释集群里那些成功案例为什么能成立**：它们都在源文照出的漏水点上，各自装了一道 held-out 闸门。下面按三层走"漏水点 → 之前的方案怎么走通的"。

### 6.1 TARGET 层：Aspire 证明了 RRSI/Search Pathology 的警告是真的

- **漏水点（本篇）**：模糊目标 → agent 去操作化一个代理指标（LoRA 24.1%→89.8%、决策时间涨、真训练时间跌），checkpoint 涨但 base 17.86→最优 CK −15.48，30 cell 只 1 个留下真增益。这就是 Goodhart：优化一个 imperfect proxy，代理涨了、真能力没涨。
- **之前为什么走得通**：`notes/reading/rrsi-regularized-harness-self-improvement-notes.md` §一 点名的两个退化——benchmark-specific fitting、evaluation noise chasing——正是 Aspire 量化出来的东西。RRSI 之所以能拿出 OOD average 40.3→43.6 的提升，**恰恰因为它在 Selection 端装了 noise-adjusted floor + cost gate + pruning，只让"证明过自己"的改动进永久状态**。Aspire 的"1/30 保留"就是没有这道闸门时的自然结果；RRSI 的闸门把"该保留什么"从可见分数改判成 held-out/OOD 表现。已发布的《The Search Pathology》说的是同一件事在单次推理内的版本（imperfect proxy 上 scale test-time compute → over-engineering），解法方向也一致：**硬化评估地形，而不是限制搜索**。
- **接口点**：Aspire 的"纪律①目标在 agent 看不见的评测上验" = RRSI 的 OOD 验证 = Airbnb 的 golden set（held-out、含 bad examples）= SIFT 的 Polyglot-225 held-out 终评。四篇在不同域收敛到同一道闸门。

### 6.2 EXPERIENCE 层：S³Gym 是 Dream-RSI 那条负结果的跨环境量化证据

- **漏水点（本篇）**：没有普适记忆赢家，换归一化排序就翻；自评 ρ≈0 几乎不预测下一次增益；同一套参数更新在 Trust 上 18/19 有效、在 PvZ 上从 23 崩到 6。
- **之前为什么走得通**：`notes/reading/dream-rsi-replay-simulator-notes.md` §5.1 有一个关键负结果——把历史蒸馏成高层方向性建议塞进 prompt（+Guidance），在 Dream-RSI 和固定探索两边都**稳定更差**；它的 §七 进一步论证"没有默认通路、支持域等于走过的路"。S³Gym 的"no universal memory winner + 换 metric 就重排"正是这条判断的**跨七个环境的量化版本**。Dream-RSI 之所以能省 162× agent 调用还保持质量，不是因为它找到了"正确的记忆法"，而是因为它**放弃了通用建议、改用可执行结构 + 多棵树取平均的泛化压力**，逼策略在"多份历史"上都不差——这恰好是 S³Gym 的纪律②"按环境选 pathway、在 held-out 上确认"。
- **一个必须说清的区分**：S³Gym 的 ρ≈0 **不否定** SIFT/JEV。SIFT 用**强 judge**（gpt-5.4-high）做**排序**，拿到 BT rank 与 full-benchmark 的 ρ=+0.72；SIFT 明说 judge"最有用的是给排序信号、不是当准确率替身"，也自认"最强 run 的 judge 比 coding backbone 强，所以不是纯粹的自我评判"。S³Gym 测的是 **agent 判自己**（弱/自评 judge）能否预测下一次增益——这正好落在 SIFT/JEV 都承认的那一档：**弱 judge 能把搜索引向强候选，但在"前沿终选/预测真实增益"上不可靠**。所以 S³Gym 是对"自评天花板"的独立佐证，不是对"judge 无用"的证明。

### 6.3 SYSTEM 层：HarnessDev 把 SIFT 的个案升级成总体统计，并给了 RRSI 纪律实证理由

- **漏水点（本篇）**：18 harness 全能跑，但 18/108 组件运行时从未触发（全是 state/memory）；26,679 轨迹 0 次 checkpoint；进化改 Execution 58 次、State 只 4 次、Verifier 0 次；可见 vs held-out 只 34/64 一致，9 个 final 只 2 个最优，固定 executor 下四个里三个退步。
- **之前为什么走得通**：`notes/reading/sift-self-improvement-fast-tree-search-notes.md` 副案例一里，judge **只从代码**就抓出一个 verifier"默认 env flag 关着、likely does nothing on default runs"、一个 shell 重写"每次起新 shell 却假称状态持久"——SIFT 发现的是**单个 dead mechanism 的个案**；HarnessDev 测的是**它有多普遍（18/108）**。两者咬合：SIFT 的 full-file judge（Spearman 0.68）之所以值钱，正因为它能在"跑分看不见"的地方识别死机制，而 HarnessDev 证明这类死机制在 population 层面大量存在、且**下游分数对它们完全不可见**（这也是 SIFT"按最高 accuracy 选根本不可靠"的最强论据）。
- **集群没点名的盲区**：让改进**持久**的机制（state / checkpoint / standalone verifier）恰恰是进化搜索**最少碰**的（State 4、Verifier 0）。RRSI 担心的是 agent"加太多"（complexity accumulation），HarnessDev 揭示的是相反的一面——**该建的持久化机制根本没被建、也没被触发**。于是"只 2/9 final 最优 → 版本管理 + 回滚"就是 RRSI Selection 纪律（只保留证明过自己的改动、其余 prune）的实证理由；SIFT 的保真度阶梯（4-task gate → Polyglot-50 → 225 held-out）则是同一纪律的"分级验证"实现。

### 6.4 一处有生产力的张力：机制乐观 vs 结构悲观

集群整体是**机制乐观**的（SIFT +7.5 gain、RRSI OOD 提升、Dream-RSI 省 162×、Airbnb VJ agreement 78%→88%）；本篇是**结构悲观**的（增益常常不 hold、9 个 final 只 2 个最优）。但这不是矛盾——**集群那些成功案例，恰恰是通过了 held-out 闸门的那批**（SIFT 的 Polyglot-225、RRSI 的 OOD average、Airbnb 的 golden set）。本篇的真正贡献是量化了**不内置 held-out 纪律时，成功有多稀**（Aspire 1/30、HarnessDev 2/9）。一句话：**这篇解释了为什么集群里那些 held-out 闸门是承重墙，不是可选装饰。**

### 6.5 FDE 的 Compound 步 = 集群反复重新发现的"壁垒"

本篇 FDE 收束的最终判据是"复用"（下一个项目能不能用上）。这正是贯穿整个集群的 commoditized-vs-moat 收束的**组织形态版**：kuaishou"Context 才是壁垒"、SIFT"不断累积的 win 矩阵 W + BT 序才是壁垒"、Dream-RSI"被完整冻结的执行现场才是壁垒"、Airbnb"golden set + 领域 rubric 才是壁垒"。FDE 的 **Compound** 步，就是"把已付费的证据沉淀成搬不走的资产"——算法/方法论是通用件，**已验证、已累积的证据**才是护城河。本篇把这件事命名成了一个岗位（FDE）和一条闭环（Discover→Learn→Compound）。

## 七、收束：commoditized 通用件 vs 不可复制的壁垒

### 可复制的通用件（源文已把方法学摊开）

- **三问三层三 benchmark 的诊断框架**（Target / Experience / System；Aspire / S³Gym / HarnessDev）——这是一个可照搬的"自进化 agent 体检表"。
- **三条验证纪律**（隐藏评测验目标 / 下一决策验经验 / 固定 executor + held-out + 版本回滚验进化）。
- **benchmark 的评测设计护栏**：Aspire 的 sealed 520-item expert eval + 48 matched vague/explicit run pairs + 可审计轨迹；S³Gym 的 Self-Testing/Judging/Improvement 三分 + 七个可执行验证器游戏 + NABA 归一化；HarnessDev 的 Unified-Eval 跨 executor + 冻结工件 + fixed-Gemini lineage。这些是"如何设计一个不可被 hack 的评测"的通用资产。
- **FDE 闭环**（Platform→Discover→Deliver→Learn→Compound）。

### 不可复制的壁垒（收在这）

- **"用隐藏/held-out 评测戳穿可见增益"这套证伪纪律本身**——它不是算法，是一种"拒绝相信可见分数"的方法论姿态。集群里每一篇的护城河（Airbnb 的 golden set、SIFT 的 win 矩阵、Dream-RSI 的冻结现场、RRSI 的 OOD 闸门）都是这套纪律在某个域的物质化。**方法可抄，抄完发现你手上没有一个 agent 看不见、又足够锐的评测集。**
- **三个 benchmark 各自的私域工件**：Aspire 那 520 条密封专家评测 + 48 对匹配 run 的完整轨迹；S³Gym 七个游戏的可执行验证器 + 七套完整 context-level 模型 + 20-checkpoint Qwen3-8B 训练研究；HarnessDev 那 18 个被冻结、可跨 executor 重放的 harness 工件。这些是"付过钱的证据"，与 SIFT/Dream-RSI 的壁垒同构。

### 迁移到其他域的通用启示（我的分析）

**凡是要声称"我的系统自我改进了"，先问一句：这个增益是在 optimizer 看得见的评测上量的，还是在看不见的 held-out 上量的？** 本篇给的三个可迁移探针——① 目标层：留一个 agent 无法访问的密封评测；② 经验层：别信自评（ρ≈0），按环境选记忆/经验通路并在下一个决策上确认；③ 系统层：固定 executor 再测一次泛化，且只保留能回滚的版本化改动——就是把"可见 ≠ 真实"这条教训变成可执行的检查清单。

---

## 延伸阅读（本仓，均已读目标文件确认接口点，非凭标题猜）

- `notes/reading/rrsi-regularized-harness-self-improvement-notes.md` — 本篇 TARGET/SYSTEM 两层漏水的**机制化补丁**。RRSI 给 harness RSI 施加正则（Proposal 端控复杂度/归因，Selection 端 noise-adjusted floor + cost gate + pruning），正是本篇"纪律①③"的实现；Aspire 的 1/30、HarnessDev 的 2/9 是"不加这道闸门会怎样"的实证。（对照是我的分析）
- `notes/reading/sift-self-improvement-fast-tree-search-notes.md` — 本篇 SYSTEM 层"dead mechanism"的**个案来源**：SIFT 副案例一里 judge 从代码就抓出 verifier"默认跑不到"、shell"假称持久状态"，HarnessDev 把它测成 18/108 的总体统计。且 SIFT"judge 只给排序、不当准确率替身"与本篇 S³Gym"自评 ρ≈0"在"自评/弱 judge 的天花板"上互证。（对照是我的分析）
- `notes/reading/dream-rsi-replay-simulator-notes.md` — 本篇 EXPERIENCE 层的**孪生负结果**：Dream-RSI §5.1"+Guidance 稳定更差"与 §七"没有默认通路、支持域等于走过的路"，是 S³Gym"no universal memory winner"的机制侧论证；两者都主张"按环境选结构 + 多历史泛化压力"而非通用记忆法。（对照是我的分析）
- `notes/reading/jev-deepeval-judgment-model-notes.md` — judgment-vs-generation split。JEV 把判断换成"可校准、可设阈值的 typed probabilities"，正是本篇 TARGET/SYSTEM 层缺的那种"可信方向裁判"；但本篇 S³Gym 的 ρ≈0 提醒：JEV 那种校准是**总体性质、不是单例保证**，agent 自评仍会失效。（对照是我的分析）
- `notes/reading/airbnb-eval-driven-development-notes.md` — 本篇"纪律①目标在隐藏评测上验"的**产品化版本**：Airbnb 的 golden set（held-out、含 bad examples）+ VJ 校准到高80s-90s% + 每周 PM review 持续注入新 failure mode，就是把"可见 ≠ 真实"编译成可执行工件的工程闭环。（对照是我的分析）
- `notes/reading/kuaishou-conan-stability-agent-notes.md` — "方法即通用件、Context 才是壁垒"这个收束框架的出处，与本篇 §6.5/§七"壁垒是已付费的证据"同一把尺子。

本仓已发布文章（公开链接，均已读目标确认相关）：

- 《[The Search Pathology: Why Scaling Test-Time Compute Can Degrade Code Agent Quality](https://cj9208.github.io/blog/ai_study/search-pathology-test-time-compute/)》— 本篇 TARGET 层"agent 在 imperfect proxy 上操作化目标、真能力没涨"是这篇所述 Goodhart 在自进化层面的投影；解法方向一致（硬化评估地形而非限制搜索）。
- 《[The Comparator Trap: Why High-Stakes AI Fails](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/)》— 那篇讲"低风险域自带便宜客观的 comparator（编译/测试）"；本篇反过来证明：**即便在 coding 这种有 comparator 的域，当 comparator 本身要跑完整基准时它就不便宜、且可见 comparator 会与 held-out 脱钩**（34/64）。可当作"comparator 存在但会骗你"的一个补充案例。（对照是我的分析）
