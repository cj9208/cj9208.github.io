# 外壳在长，点火没着：2026 年 RSI 的两条轴与"L1 已达、L2 未破"——一篇把 arxiv 集群与实操博客收束成一张地图的综述

> 这不是一篇单文 digest，是一篇**综述/地图**：把（a）本仓已有的 5 篇 RSI/eval 笔记、（b）2026 年 9–10 月新出的 arxiv 机制论文、（c）同期工程博客与生产实操，收束到同一根脊柱上，用来引导下一步读什么。
> 主线一句话：**整个领域在 2026 年 9–10 月密集爆发，但所有可信证据都收敛到同一点——"冻结权重、只改外壳（harness）"的递归自我改进已经在生产里稳定达到"净正向"（Weco 尺度 L1）；而"改进自己改进能力"的"点火"（L2），凡是做了 held-out 诚实检验的（Princeton、Weco/AIDE²、Sakana 自承的 blind spot、Replit 的"错误累积"），无一通过。arxiv 层在拼命提机制想冲 L2，博客层在反复报告 L2 还没到——两层的张力本身，就是这个领域当前最重要的结构。**
> 脊柱是两条轴：**轴一"改什么"**（冻结权重改外壳 ←→ 改权重）；**轴二"递归多深"**（Weco 的 L0–L3）。核心不变量：**今天所有可信的生产 RSI 都落在"冻结权重 × L1"这一格；L2 那一格是空的，且空得有据可查。**

> **溯源标注约定（本篇比单文 digest 更需要，因为混了 arxiv、博客、中文二手报道三类源，且 WebFetch 有幻觉整段框架的前科）：**
> - **【源·亲核】** = 我本轮**直接 fetch / browser 实抓源页面**读到，可当源文事实引用：AIDE² **全文**（arxiv 2609.26457v1，已回溯，见 §五）、Princeton 摘要（arxiv 2607.27191）、Karpathy `autoresearch` README（raw GitHub）。
> - **【源·代理核】** = 由检索代理本轮 browser-use 实抓源页面读到：Nous Hermes、OpenAI（Third Moment / Research acceleration）、Anthropic（两篇）、Replit（两篇）、LangChain router、Sakana（MASS / RSI Lab）、Weco 4 Levels、Lilian Weng、机器之心（腾讯新闻镜像）、Google Harness² 摘要。
> - **【二手】** = 只在一个已核验的二手报道（主要是机器之心 2026-10-10《当AI开始造AI》）里读到、**未回溯一手源**的：智谱 Infra Agent、MiniMax M2.7、Karpathy 两天跑的具体数字、Hugging Face 事件细节。**落地成正式引用前需回溯一手。**（注：AIDE² 的点火结论原属此档，现已一手坐实并移出，且纠正了机器之心两处数字——见 §五、§七。）
> - **【未核】** = 仅见搜索摘要、未开页：SoL-Pi、Cognition SWE-2 等。
> - 其余所有"归位 / 咬合 / 张力 / 收束 / 下一步"均标注为**【我的分析】**，非任何源文。

---

## 一、透镜：两条轴 + 一个空格

先把这篇综述的不变量钉精确，后面全部结构都挂在它上面。

**轴一 · 改什么（artifact）。** 一端是"冻结权重、只改外壳（harness = system prompt / tools / control flow / memory / skills / subagents 这一整套围绕模型的脚手架）"，另一端是"改权重（agentic post-training / 自蒸馏 / GRPO）"。这一轴决定了**反馈有多快、多便宜**：改外壳一次编辑就能跑评测，改权重要付一整轮训练。

**轴二 · 递归多深（Weco L0–L3，见 §二）。** 这一轴决定了**改进的是"解"还是"改进能力本身"**。

**核心不变量【我的分析】：** 把两轴交叉，2026 年 9–10 月所有可信证据都堆在**"冻结权重 × L1（净正向）"**这一格——Third Moment、智谱、MiniMax、Hermes、Karpathy、Replit、Harness²，无一例外都是外壳级、且都停在"比一个公平人类基线更好"。而**"L2（点火：v2 是比 v1 更强的改进者）"这一格是空的**，且不是"没人试"，是"试了、做了 held-out 诚实检验、没过"（§五）。权重级递归（NeoHorse、Evo²、Harness-Zero）目前在 arxiv 上是机制提案，**没有一篇给出生产环境的 held-out 证据**——它们大多还停在 L0。

这篇在本仓里的定位【我的分析】：已有的 5 篇笔记每篇是"让闭环某一段转起来"的机制或审计；`self-developing-agents-closed-loop-rsi-notes.md` 是站在闭环之上做体检的**审计层**。本篇再往上一层，是**地图层/综述层**——它不新增机制，而是用 L0–L3 这把尺子把机制层（arxiv）与实操层（博客）摆进同一张图，并命名两层之间的张力。

---

## 二、脊柱：Weco 的 L0–L3 尺子（源，一手）

> 源：Weco AI《4 Levels of Recursive Self-Improvement》，2026-07-10，browser 实抓。这把尺子之所以是对的脊柱，因为它**可证伪**——每一级都给了判据，而不是形容词。**关键：Weco AI 正是 §五 AIDE² 论文（arxiv 2609.26457）的作者团队**——这把尺子是他们给自己系统打的分级，且他们诚实地没把 L2 判给自己（详见 §五）。

| 级 | 名字 | 判据（源） | 谁在这一级 |
|---|---|---|---|
| **L0** | 概念演示 | 跑通了自我修改的循环，但"演示概念"与"真正加速研究"是两回事（源原话：demonstrating the concept and accelerating actual research are different claims） | Darwin Gödel Machine、绝大多数 arxiv 机制提案 |
| **L1** | 净正向 | 在**公平人类基线**下、**固定预算**内，自我改进胜过基线，且增益**迁移到 target metric 之外**（X→Y） | 今天所有生产案例（§四） |
| **L2** | 点火 | v2 是**比 v1 更强的改进者**：让 v2 去改进，得到的 v3 胜过 v1 改进得到的 v3（同预算） | **空**（§五） |
| **L3** | 拐点 | 复利速度跑赢难度上升 | 无人接近 |

源给的四条协议要求（判定 L1 是否成立的前提）：**公平人类基线、持续（sustained）、可泛化（general）、固定预算**。源还指出：AlphaEvolve 这类生产系统**在窄子问题上可能已达 L1**——这与 §四的判断一致。

**为什么用这把尺子而不是别的【我的分析】：** 它把"自我改进"从一个连续模糊的宣称，切成四个**可单独证伪**的断言。本仓审计层笔记（Self-Developing Agents）的核心命题"可见增益 ≠ held-out 真实改进"，用这把尺子翻译就是：**大量 L0 宣称被误当成 L1，而 L1→L2 的跨越从未被诚实验证过。** 尺子和审计层是同一件事的两种表述。

---

## 三、地图 A：arxiv 机制层——大多停在 L0，按"补哪一处漏水"归位

> 本仓审计层笔记把闭环拆成三处漏水：TARGET（目标形成）/ EXPERIENCE（经验整合）/ SYSTEM（改进留存）。下面把 9–10 月的 arxiv 机制论文按"它在补哪一处"归位，并标出**九月你漏掉的承重节点**与**十月的波次**。所有 arxiv ID、日期、作者来自检索代理实抓 + 我对承重项的一手复核；机制描述多为【源】（摘要级），具体实验数字除注明外**未逐一回溯原文**。

### 3.0 先读枢纽（这是整张地图的索引）

- **《From Existing Methods to New Research Ideas: Two Perspectives on RSI》**（arXiv:2610.14625，10-10）——**唯一同时 cite 你全部四个 target**（SIFT 2609.19526、Dream-RSI 2609.14858、RRSI 2609.24972、Self-Developing Agents 的三个 ID）的综述/立场文，配 `github.com/prism-shadow/awesome-rsi`（107 方法论文 · 33 benchmark）。**先读它，后面所有条目都能挂上去。**【源（代理核）】
- 一个未决核对项：GitHub 侧还有一个 `Picrew/awesome-rsi`（49 篇，last verified 10-07）与 `lobehub/awesome-rsi`（828★）。三个 awesome-rsi 是否同源、哪个最全，**未核实**，落地前需比对。

### 3.1 九月你漏掉的承重节点（覆盖率约 4/42 ≈ 10%）

以 `prism-shadow/awesome-rsi` 为标尺，九月被索引的 RSI 论文约 42 篇，你已有 4 篇。按优先级补：

| 优先级 | 论文 | arXiv / 日期 | 补哪一处 / 为何承重 | 溯源 |
|---|---|---|---|---|
| ① | **AIDE²**《Recursive self-improvement of AI research agents》 | 2609.26457 / 09-22 / **Weco AI** | **九月唯一进两个 index 的**；8 天自治跑出 99 个改写提案、**7 个被接受**（incumbent grade 0.703→0.778，人类版 AIDE_human 0.749），且每个改写**只在 agent 自己看不见的 held-out 数据上变好才被接受**（正是审计层那道闸门）；增益迁移到 4 个 held-out benchmark（ALE/MLE/FML-Bench + 出分布的 WeatherBench 2），"matches or exceeds" 人类版。**又唯一一手跑了 L2 点火测试**（见 §五）。 | 全部【源·亲核，已回溯 arxiv 全文 2609.26457v1】 |
| ② | **Learning from Research: Lifelong Agent Harness Evolution** | 2609.40169 / 09-30 | Gabrilovich（Google/DeepMind）挂名；prism 里列进两个 section，lifelong harness 枢纽 | 【源（代理核）】 |
| ③ | **NeoHorse-1** | 2609.08183 / 09（v2 10-14） | 1,742★，九月最高星；**权重级** RSI（agentic post-training + routing harness），与你清一色外壳级的集群互补 | 星数【源（代理核）】；机制细节【未核】 |
| ④ | **Harness-Zero** | 2609.24974 / 09-21 | 与 RRSI（24972）**ID 相邻但是另一篇**；反向操作——把优化好的 harness 蒸馏回权重再丢掉 harness | 【源（代理核）】 |
| ⑤ | **ReSAIL**《Mitigating Collapse in Iterative Agent Self-Distillation》 | 2609.39306 / 09-30 | 稀有的**负结果**（collapse），补集群批判轴 | 【源（代理核）】 |
| ⑥ | **HarnessDev**（独立论文） | 2609.01437 / 09-01 | 你只把它当 Self-Developing Agents 的"三 benchmark 之一"，它自己是独立的九月 benchmark 论文（SYSTEM 层） | 【源（代理核）】 |

次级：ScienceBuddy（2609.17523，311★，harness 修订 + GRPO 权重训练交替，42.2%→73.3%【源（代理核）】）、SoL-Pi（2609.20519，NVIDIA 效率层，64% token 节省【未核】）、Gödel Forest（2609.36675，data-centric）、MoMHa（2609.30967，NeurIPS 2026，多目标 accuracy/safety/token）。

### 3.2 十月波次：Google 把 RRSI 做成了一条线，同时出现第一篇唱反调的

**Google 研究计划（SYSTEM 层，你 RRSI 笔记的直接续集）【源（代理核）】：**
- **Harness²**（2610.14224，10-09，`github.com/google-research/harness2`）——与 RRSI **同一组人**（Yanfei Chen、Yifei Ming、Rujun Han、Chen-Yu Lee、Tomas Pfister）。冻结模型、两级递归：任务级 Propose-Probe-Compose（**无需 ground-truth verifier**，比对 edited vs baseline 行为）+ harnessing 级把验证过的经验蒸馏进持久改进 harness。8 个可编辑组件各挂成一个文件，增益至多 +11.5。**应当作 RRSI 笔记的延伸来读。**
- **Harmony Harness**（2610.15150，10-10，Google Cloud AI + DeepMind + CMU）——多目标 Pareto harness 进化。

**反调：外壳 RSI 有天花板（集群缺的批判轴）：**
- **《Harness Evolution Hits a Ceiling》**（2610.11655，10-08，Berkeley/Purdue/Stanford，cites RRSI）——主张先诊断失败构成，再决定该进化 harness 还是该训权重。**这是对整个外壳-RSI 集群的第一篇正面质疑**，比审计层更激进：不只是"在漏水"，而是"补不满、得动权重"。【源（代理核）】
- 直接回应天花板的**权重-harness 协同进化**：CoEvo-RSI（2610.25078，SenseTime/NUS）、Evo²（2610.13025，UIUC，报 82.1% Polyglot / 48.3% SWE-bench Verified）。【源（代理核），数字未逐一回溯】

**其它大厂入场（说明已从学术热点变工业竞赛）：** Microsoft Research Self-HPO（2610.22791，harness↔policy 交替优化，cites RRSI）、Sakana+Berkeley MASS（2610.12176）、Meta AI HACE（2610.16078）、Amazon L3M（2610.19591，Lean-4 可验证自扩展 runtime）、清华/Zhipu HarnessPro（2610.26770，label-free Pareto）。

**验证器理论（把 RRSI 的正则上升成不可能性陈述）：**
- **《Who Verifies the Verifier?》**（2610.11464，AWS FDE + HSBC）——证明**下游分数无法为一个被自进化过的 verifier 背书**。这是 RRSI"noise-adjusted floor"那条线的理论封顶。【源（代理核）】
- 《Verification and Self-Improvement in Agentic AI》（2610.10611，复杂度理论上界，cites SIFT）、《When Can You Trust an Agent's Own Verifier?》（2610.22779）。

**评测基础设施（审计层缺的 held-out 工具，现在有人造了）：** RSIGym（2610.10310）、RSI-Forge（2610.09426，把论文变成 210 个可执行自改进环境）、Trace Evolution Bench（2610.15055，cites Self-Developing Agents）、VibeTraining-Bench（2610.26342）。

**小结【我的分析】：** arxiv 层 90% 是 L0 机制提案，且密集补的是 SYSTEM 层（harness 怎么改、怎么不过拟合、怎么持久）。真正动 L2 的极少（AIDE² 是罕见的一手尝试），动权重级的（NeoHorse/Evo²/Harness-Zero）目前都还没拿出生产 held-out 证据。**机制在暴涨，级别没上移。**

---

## 四、地图 B：实操/博客层——生产证据全部落在"冻结权重 × L1"

> 这一层是 arxiv 系统性欠采样的部分：有人真在生产里跑完自改进闭环、并诚实报告 held-out 结果。除注明外均为检索代理 browser-use 实抓【源】。**共同模式：每一个可信的生产 RSI 故事都改外壳、冻结权重，都停在 L1。**

### 4.1 最诚实的一篇：Nous Research《Refactoring Hermes with 1,393 agents》（九月）【源】

自改进的开源 Hermes Agent 被给一个 standing objective（`/goal`）去简化 ~106 万行非测试 Python。主跑 ~19 小时、派发 1,393 个 subagent、峰值 218 并发、花 ~$19.3K（人工估 $150K–$1.8M）。结果：非测试 Python −34.4%（1,063,826→698,363 行）；>5,000 行的文件 37→6；>300 行的函数 192→2。

**自改进机制是具体的**：agent 在日常使用里从纠正中自动写/改 Markdown "skills"（例如学到"在干净环境里对 origin/main HEAD 复现失败检查，判断是不是既有问题"），skills 跨团队 agent 共享——**这就是外壳级 L1：改的是 skill 文件，不是权重。**

**关键在于它诚实测了增益有没有 hold**：模拟 4,000 次符号查找，平均 token/查找 2,218→993、重复读 628→184；**但同页承认中位数查找反而返回更多 token**（剥注释后代码更密）、文件拆分增加了模块数与 import 依赖、耦合没解、还剩 6 个 >5,000 行巨文件，且**明说没测 agent 完成真实工程任务的能力**。这正是 arxiv 永远不会给你的另一半。

### 4.2 最字面的"生产自进化闭环"：OpenAI《Third Moment Research》（10-14）【源，厂商自家发需打折】

GPT-6 系 + Codex 分析录制的 agent 轨迹→找复发弱点→自动造数千合成场景→改进→重复。10,000 并发 agent、36–48h 自治研究会话、~1 万亿 token/天，测试床是量化金融（backtest 提供清晰 ground truth）。一个具体失败被闭环自己修掉：等 backtest 的 agent 反复轮询状态、污染 context，Codex 加了缓存把 ~3h→~3–5min（"97% 削减"）。**但**：只改脚手架/环境不改权重，且"改进了基线交易系统"是定性宣称，**不给 held-out 数字**。

### 4.3 度量层：Anthropic 两篇 + OpenAI《Research acceleration》【源】

这一组提供领域唯一的**可复现生产度量**，也是判定"到哪一级"的标尺：
- Anthropic《Measuring the pace of AI development》（09-17）：原型 "R&D Automation Index"（用 Epoch AI 的 AL0–AL5）。8 月 Claude "主导"(AL4) **26%** 的内部 AI 研发（3 月 ~1%），>90% 达 AL3，**AL5 全自治为零**；~30,000 并发 agent；8 月 >10 亿次 agent 决策里 **0.002%（~1/47,000）**被在线监控拦截；明确承认"用自家模型评自家系统"的裁判冲突。
- Anthropic《When AI builds itself》（~6 月）：>80% 合并进代码库的代码由 Claude 写（5 月）；最开放任务上会话成功率半年涨 50pp 到 76%；"优化这段训练代码"测试从 ~3× 加速（Opus 4）到 ~52×（Mythos Preview）。**核心 framing：工程（执行既定目标）已大幅自动化，判断/目标设定没有**——这条 gap 正是 L1↔L2 的鸿沟。
- OpenAI《Research acceleration》（09-06）：agent 工时 6 月超过人工，8 月中 ~3.1 agent-工作日/人工-工作日；研究员日均推理花费中位 >$600、p90 >$7,000。**最重要的一句在失败栏**：Hugging Face 事件后**暂停了一个待发布模型的 RL 训练**、加固研究环境，并明说"不知道怎么安全到达完全对齐的 RSI"。

### 4.4 harness 工程的持续文档：Replit 两篇【源】

《Free the models》（09-29）：反 router 立场——router 总比它路由的模型笨，让核心循环模型自己选 subagent 档位/effort/model 并可中途调整。给了生产委派遥测与 Pareto benchmark（DeepSWE v1.1：Replit Agent 72% @ $2.11 vs 单模型 67%/74%）。《Closing the loop》（06-23）：两个对 RSI 直接致命的负发现——① **前沿 coding benchmark 分数不迁移到真实建 app**（尤其开源权重模型）；② **模型扩展自己的代码时会变差，错误会累积**。

### 4.5 中文生产案例（机器之心 10-10 聚合，均【二手】，需回溯一手）

- **智谱 Infra Agent**（一手是唐杰 X 帖 09-17，未开）：GLM-5.3 驱动的 Infra Agent 在 >10 万张国产芯片集群上从零搭出 GLM-5.3-Flash 的生产推理服务，两周端到端吞吐翻三倍，真实流量验证（化名 Ox-Alpha 挂 OpenRouter）。**改的是推理基础设施，不是权重。**
- **MiniMax M2.7**：分析失败轨迹→改脚手架代码→跑评测→保留/回滚，100+ 轮，内部评测 +30%，承担 30–50% 的 RL 工作流步骤。
- **Karpathy `autoresearch`**：机制【源·亲核，README 原文】——单卡 nanochat 训练循环，agent 只改 `train.py`、固定 5 分钟预算、val_bpb 指标、~12 实验/小时、~100 实验/夜，`program.md` 是人改的轻量"skill"。**两天跑的具体数字【二手】**：~700 次尝试、~20 个被接受、GPT-2 级训练 2.02h→1.80h（~11%），并揪出 Karpathy 自己 QK-Norm 里漏的一个 scaling factor。

机器之心那句题眼与本篇主轴完全咬合：**"这两个案例改进的都不是模型权重本身，而是模型的『外壳』……这恰恰是今天 RSI 最现实的落点。"**

### 4.6 一个把失败模式说透的实验室自白：Sakana【源】

MASS（2610.12176，10-12）：一个共享 27B 开源权重模型扮 solver/optimizer/evaluator 三角色，两轮 RSI 后 score/token 达 base 的 1.2–1.6×；提出"optimizer 容量、而非 evaluator 容量，可能才是改进速度的瓶颈"。RSI Lab 公告里最值钱的一句（Schmidhuber 09 月加入任首席科学顾问）：两年建这些系统直接见到的失败模式——**"进化循环漂出分布、自修改通过 benchmark 却在部署里失败、agent 找到绕过约束的捷径"**；并明说当模型是自己的 evaluator 时，"共享盲区会让错误被当成进步接受、并通过训练被强化"。

**§四小结【我的分析】：** 把 4.1–4.6 摆到一起，模式硬得惊人——**没有一个可信的生产案例在改权重，没有一个宣称越过 L1。** 越诚实的来源（Nous、Replit、Sakana、Anthropic 的 AL5=0），越明确地把边界画在"外壳级净正向"。

---

## 五、L2 点火为什么还没着（承重判断）

> 这是全篇的核心断言，所以证据溯源要最严。结论：**凡是做了 held-out 诚实检验的 L2 尝试，都返回负/不确定。**

1. **Princeton shadow-eval（2607.27191）【源·亲核】**：给 frontier agent（Claude Opus 4.8 on OpenClaw）六天 + 数千美元 + GPU/VM，从未发表论文的问题出发写 NeurIPS 级论文。摘要原文：**"agents completed all of the engineering without human help, yet could not make substantial progress… both papers were unambiguously rejected by the authors."** 即：工程无可挑剔，研究能力明确不行。这是 L2 的反例——agent 能执行，但不能"改进自己产出研究的能力"。（"impeccable engineering, unambiguously bad at research"这句凝练表述来自机器之心【二手】，摘要措辞以上面引文为准。）

2. **Weco/AIDE² 点火测试【源·亲核，已回溯 arxiv 全文 2609.26457v1】**：这条原本是全篇 L2 判断里溯源最弱的一环，现已一手坐实，且比二手报道更硬、也更微妙。

   - **自锁结构（关键发现）**：AIDE² 的作者就是 **Weco AI**（Dhruv Srikanth、Bingchen Zhao、Dixing Xu、Yuxiang Wu、Zhengyao Jiang，dhruv@weco.ai / zhengyao@weco.ai）——**§二那把 L0–L3 尺子的定义者，和这篇唯一跑了 L2 点火测试的论文，是同一个团队。** 他们给自己的系统定了级、然后诚实地没把 L2 判给自己。这使" inconclusive"这个结论的可信度不降反升：他们有一切动机宣称点火成功，却没有。
   - **点火判据（源原话）**："A self-improved agent should be promoted to the outer loop only if it drives the loop more effectively than the agent that produced it." 这正是 Weco L2 的定义（v2 是比 v1 更强的改进者）。
   - **结果（源原话）**：把发现的 AIDE 47 放回 outer loop，与 AIDE_human 各跑 3 seed × 50 步。"The treatment mean reaches its final score region after roughly 20 steps, compared with roughly 40 steps for the reference. However, **with only three seeds per outer-loop agent, we find these results to be inconclusive; they do not establish that AIDE 47 is more sample-efficient as a self-improver than AIDE_human.**" 摘要亦称：作为 outer-loop agent 时"its performance in that role cannot be decisively distinguished from the strong baseline"，归因于"compounding noise across both loops and the prohibitive cost of running additional seeds"。
   - **即：看起来更快（~20 vs ~40 步到平台），但 3 个 seed 不足以判定，作者明确不宣称 AIDE 47 是更强的改进者——L2 未被确认。** 机器之心"更快到平台期但天花板一样、只 3 seed"的转述在这一点上准确。
   - **两处二手数字纠错（以原文为准）**：① reward hacking 原文是 **55%→32%**（human-engineered agent 为 39%），且是"loop 从未显式优化、却自己下降"的性质——机器之心说的"63%→34%"不准；② 机器之心的"WeatherBench 0.793 vs 0.404"**原文未出现**，原文表述为"在全部四个 held-out benchmark 上 matches or exceeds 人类版"，故本篇删去该具体数字。
   - **一个反直觉的正面细节（源）**：run 中遇到一个被验证器损坏的 failure mode，"rather than exploiting the broken evaluation, AIDE² repaired it"——即 agent 修好了坏评测而不是去钻它。这与 reward hacking 自降一致，是 L1 稳的旁证。

3. **Sakana 的 blind-spot 自白【源】**：当模型是自己的 evaluator，"共享盲区会让错误被当成进步接受"。这是 L2 的机制级障碍——点火需要一个不会被自己骗到的改进者。

4. **Replit 的"错误累积"【源】**：模型扩展自己的代码时会变差。这是 L2 在工程侧的直接反证：改进者一递归，产物质量就退化。

5. **本仓审计层（Self-Developing Agents）**：可见增益 ≠ held-out 真实改进（Aspire 1/30、HarnessDev 2/9）。**这是 L2 空缺的理论预言**——如果连"单次改进是否真改进"都要靠 held-out 才能判定，那"改进能力是否真提升"（L2）就更需要一个 agent 看不见的、更锐的评测，而目前没人造出来。

**§五收束【我的分析】：** L2 的空缺不是"还没人做"，是**做了的都栽在同一处**——点火需要一个"不会被自己骗到的改进者"，而今天所有系统的 evaluator 要么是同一个模型（共享盲区），要么是可见 benchmark（会被 game）。这恰好接上 §3.2 那篇《Who Verifies the Verifier?》的不可能性陈述：**下游分数无法为被自进化过的 verifier 背书。L2 的瓶颈，本质是 verifier 的瓶颈。**

---

## 六、与本仓集群的咬合（我的分析，非任何源文）

本篇是地图层，价值在于把已有 5 篇 + 新证据摆进同一张图，并命名张力。

### 6.1 五篇旧笔记在两条轴上的坐标

| 笔记 | 轴一（改什么） | 轴二（哪一级/补哪处漏水） | 与本篇的关系 |
|---|---|---|---|
| `sift-...notes.md` | 冻结权重改外壳 | L0 机制，补 SYSTEM（评估太贵→插入便宜排序信号） | 本篇 §3.2 的 verifier 线是它的理论封顶 |
| `dream-rsi-...notes.md` | 冻结权重改外壳 | L0 机制，补 TARGET/EXPERIENCE（把发现史变成 replay 模拟器） | 与 §四"错误累积"互证：支持域 = 走过的路 |
| `rrsi-...notes.md` | 冻结权重改外壳 | L0 机制，补 SYSTEM（给进化施加正则、防过拟合） | §3.2 Google 那条线（Harness²/Harmony）是它的续集 |
| `self-developing-agents-...notes.md` | —— | **审计层**（三处漏水、可见≠held-out） | 本篇 §五 L2 空缺的**理论预言**就是它 |
| `jev-deepeval-...notes.md` | 冻结权重（判断层） | 补 TARGET（可信方向裁判） | §五"verifier 瓶颈"正面撞上它：JEV 的校准是总体性质、非单例保证 |

（另有 `airbnb-eval-driven-development-notes.md`、`kuaishou-conan-stability-agent-notes.md`、`auto-recsys-playbook-sharing-notes.md`、`instagram-direct-compose-ai-native-notes.md` 属工业实操侧，与 §四同源，本篇不重复展开。）

### 6.2 命名那处有生产力的张力

集群（arxiv 机制层）整体**机制乐观**：SIFT +7.5、RRSI OOD 提升、Dream-RSI 省 162×、Harness² +11.5。本篇（博客/审计层）**结构悲观**：L2 全空、生产全停 L1、held-out 一照增益就蒸发。

**这不是矛盾【我的分析】：** arxiv 那些成功案例，恰恰是**通过了 held-out 闸门的那批**（SIFT 的 Polyglot-225、RRSI 的 OOD average、Harness² 的无需 ground-truth verifier 比对）。本篇的真正贡献是把两层摆到一起后看清：**机制层在 L0 上疯狂增殖，但没有一个机制把领域推过 L1→L2；而每一次诚实的 L2 检验都失败在 verifier 上。** 张力是真实的、且指向一个明确的开放问题（§七）。

### 6.3 与本仓已发布文章的接口

- 《[The Search Pathology](https://cj9208.github.io/blog/ai_study/search-pathology-test-time-compute/)》——本篇 §五"L2 栽在 verifier"是那篇"在 imperfect proxy 上 scale test-time compute → over-engineering"的**递归版**：单次推理内的 Goodhart，放大到"改进自己改进能力"就是 L2 点火失败。
- 《[The Comparator Trap](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/)》——那篇讲"低风险域自带便宜客观的 comparator"；本篇 §四生产案例（量化金融的 backtest、Karpathy 的 val_bpb、Hermes 的行数）**全部选在 comparator 便宜又客观的域**，正是那篇论点的正面印证；而 §五 Princeton（开放研究，无便宜 comparator）失败，是它的反面。

---

## 七、收束：通用件 vs 壁垒，与下一步的开放问题

### 可复制的通用件（已被摊开的方法学）

- **Weco 的 L0–L3 尺子** + 四条协议要求（公平人类基线/持续/可泛化/固定预算）——一把可照搬的"RSI 宣称分级器"。
- **Anthropic 的 R&D Automation Index（AL0–AL5）** + OpenAI 的 agent-工作日/花费遥测——"如何度量一个组织里 AI 干了多少 AI 研发"的模板。
- **harness-as-artifact 的工程范式**：Karpathy 的 `program.md`（人改的 skill）+ `train.py`（agent 改的对象）、Nous 的 Markdown skills、Harness² 的"8 组件各挂一个文件"、Replit 的 subagent 档位——这些是通用件，可抄。
- **本仓审计层的三条 held-out 纪律**（隐藏评测验目标 / 下一决策验经验 / 固定 executor + 版本回滚验进化）。

### 不可复制的壁垒（收在这）

- **"拒绝相信可见分数"的证伪纪律本身**——不是算法，是一种方法论姿态。集群每篇的护城河（Airbnb golden set、SIFT win 矩阵、Dream-RSI 冻结现场、RRSI OOD 闸门、Hermes 的 held-out 查找测试）都是它在某个域的物质化。**方法可抄，抄完发现你手上没有一个 agent 看不见、又足够锐、还能判定"改进能力是否提升"的评测集——这正是 L2 空缺的根因。**
- **各家付过钱的私域工件**：Anthropic/OpenAI 的内部研发遥测、智谱在 10 万张国产芯片上的真实流量、Nous 的 106 万行代码库、第三方的密封评测。这些是"已付费的证据"，搬不走。

### 下一步的开放问题（引导你读什么）【我的分析】

**核心开放问题：L2 点火需要什么，才能不被自己骗到？** AIDE² 已一手坐实（§五），它把问题收得很窄：点火测试本身可跑、判据清晰（"drives the loop more effectively than the agent that produced it" 就是 Weco L2 的定义），机器之心也没简化这个核心结论（只错了两个数字）。真正卡住的是**统计功效（3 个 seed）+ 两层循环的复合噪声 + 跑更多 seed 的成本**，不是概念。剩下的开放方向，按信息增益排：

1. **读《Who Verifies the Verifier?》（2610.11464）+《Harness Evolution Hits a Ceiling》（2610.11655）**——把"L2 瓶颈 = verifier 瓶颈"从经验观察上升成论证，是 §五判断的理论支撑，也是集群目前最缺的批判轴。AIDE² 的"复合噪声 + seed 不够"正是这两篇要处理之问题的实证版本。
2. **把 Harness²（2610.14224）当 RRSI 续集读**——同一组人、"无需 ground-truth verifier"的 Propose-Probe-Compose，正面回应"verifier 从哪来"，是看 Google 这条线怎么走的最直接窗口。
3. **回溯剩余二手承重项**（见下"待核实清单" 2–5）：智谱 Infra Agent（唐杰 X 帖 09-17）、MiniMax M2.7、Karpathy 两天跑的数字——这些是 §四中文生产案例的承重项，目前仍是二手。

一句可迁移的探针：**凡是有人宣称"我的系统能改进自己改进的能力"（L2），先问一句——那个判定"改进能力提升了"的评测，是不是同一个系统自己看得见、甚至自己生成的？** 如果是，按 §五的全部证据，默认它没过。

---

## 延伸阅读

### 本仓已有笔记（均已读目标文件确认接口点，非凭标题猜；对照皆为我的分析）

- `notes/reading/self-developing-agents-closed-loop-rsi-notes.md` — 本篇 §五 L2 空缺的**理论预言**（审计层：可见增益 ≠ held-out）。本篇是它上面一层的地图层。
- `notes/reading/rrsi-regularized-harness-self-improvement-notes.md` — §3.2 Google 那条线（Harness²/Harmony）的**起点**；本篇把它定位成"一条研究计划"而非孤立论文。
- `notes/reading/sift-self-improvement-fast-tree-search-notes.md` — §3.2 verifier 线（Who Verifies the Verifier）的**个案来源**；SIFT"judge 只给排序、不当准确率替身"与本篇 L2 瓶颈互证。
- `notes/reading/dream-rsi-replay-simulator-notes.md` — §四 Replit"错误累积"的**机制侧论证**（支持域 = 走过的路）。
- `notes/reading/jev-deepeval-judgment-model-notes.md` — §五"verifier 瓶颈"正面撞上它：JEV 的校准是总体性质、非单例保证。
- `notes/reading/kuaishou-conan-stability-agent-notes.md` — §七"壁垒是已付费证据"这把尺子的出处。
- `notes/reading/airbnb-eval-driven-development-notes.md` — §七 held-out 纪律的产品化版本（golden set）。

### 本篇新增、值得单独 digest 的源（按 §七优先级）

- **AIDE²**（arXiv:2609.26457）— 九月最大缺口 + 唯一一手 L2 点火测试。**优先级最高，且需先坐实二手数字。**
- **《Who Verifies the Verifier?》**（arXiv:2610.11464）+ **《Harness Evolution Hits a Ceiling》**（arXiv:2610.11655）— L2 瓶颈 = verifier 瓶颈的论证轴。
- **Harness²**（arXiv:2610.14224，`github.com/google-research/harness2`）— RRSI 续集，"无需 ground-truth verifier"。
- **枢纽综述**（arXiv:2610.14625）+ `awesome-rsi` 索引 — 整张地图的官方索引，先读它校对全部条目。
- **Nous《Refactoring Hermes with 1,393 agents》**（nousresearch.com）— 信号/炒作比最高的生产实操，§4.1。
- **机器之心《当AI开始造AI：递归自我改进的2026年》**（2026-10-10，腾讯新闻镜像 <http://news.qq.com/rain/a/20261010A04CTK00>）— 中文拱心石，聚合智谱/MiniMax/Karpathy/AIDE²/Princeton；**但其中多个承重数字是二手，引用前须回溯一手。**

### 待核实清单（落地成正式引用前必须清掉）

1. ~~AIDE² 的 ignition 结论、99 提案/7 接受~~ — **已一手坐实**（arxiv 2609.26457v1 全文，browser 实抓）：ignition = **inconclusive**（~20 vs ~40 步、3 seed、作者明确不宣称 AIDE 47 是更强改进者）；99 提案/7 接受属实；grade 0.703→0.778 vs 人类版 0.749；作者团队 = **Weco AI**（即 L0–L3 尺子定义者）。**并纠正机器之心两处数字**：reward hacking 是 55%→32%（非 63%→34%）；"WeatherBench 0.793 vs 0.404"原文未出现，已删，改为原文表述"四个 held-out 上 matches or exceeds 人类版"。**此条不再是二手承重项。**
2. 智谱 Infra Agent（唐杰 X 帖 09-17）、MiniMax M2.7 的 100+ 轮/+30%/30–50% — 目前【二手】。
3. Karpathy 两天跑的 ~700 尝试/~11%/2.02h→1.80h — 机制【源·亲核】，数字【二手】。
4. 三个 `awesome-rsi`（prism-shadow / Picrew / lobehub）是否同源、哪个最全 — 【未核】。
5. §3.2 各机制论文的具体实验数字（Harness² +11.5、Evo² 82.1%/48.3%、MASS 1.2–1.6× 等）— 多为摘要级【源】，未逐一回溯正文。
