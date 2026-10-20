# 会过期的与会反号的：Auto-RecSys 的三路知识分流，与为什么它是一篇 infra 论文而不是 RSI 论文

> 源文：《Auto-RecSys: Harnessing Autonomous Research Agents for Industry-Scale Recommender Systems》，arXiv:2609.10922v1 [cs.CL]，2026-09-10，正文标注日期 September 11, 2026。Meta + University of Illinois Urbana-Champaign。作者 Ming Li、Dai Li、Xuying Ning、Bo Sun、Rui Li、Yi Zhang、Silvia Gong、Xuan Cao、Rui Li、Cornelia Carapcea、Qunshu Zhang、Zhigang Wang、Yinglong Xia、Xue Feng、Andy Wang。通讯 Andy Wang（xiaolongw@meta.com）、Ming Li（liming@meta.com）。本地 PDF：`C:\Users\cjdyx\我的云端硬盘\DS_ML\skills+harness\2609-Auto-RecSys.pdf`（16 页）。
> 这是一篇读后梳理，不是翻译。主线一句话：**并行本身不产生新能力，它只放大既有能力；真正产生新能力的唯一环节是「经验怎么分享」，而这篇论文把知识分成三路分流——运维知识写成自然语言、系统状态写成固定 schema、研究结论写成自由文本 lessons——前两路的分流判据是对的且有数字支撑，第三路违反了自己的判据且一个数字都没有。所以它是一篇很扎实的 infra 论文，套着一个 RSI 的叙事框架。**
> 标注约定：§三–§四、§六–§七 的机制、架构、存储布局、全部数字与英文原话均为**源文原样**。§二（域背景）、§五（MapReduce 类比辨析）、§八（infra vs RSI 判定）、§九 中的「我的判断」段落是**我的分析，非源文**，已就地标注，不要当源文事实引用。§八是本篇笔记相对源文的主要增量。

## 一、一句话主线

论文表面在讲「怎么让 auto-research agent 跑得起工业级推荐模型」，实际动的是一个更窄也更硬的问题：**当 N 个昂贵的长事务并行跑在多台服务器上，它们之间应该分享什么、以什么形式分享。**

三大 harness 设计（分布式异步执行、集中式跨服务器 memory、认知-程序分离）里，前两个是并行的**代价**——它们存在的全部理由是让并行不至于崩掉，不产生任何新能力，本质是防损失。只有第三个（认知-程序分离）触及「分享什么形式」，而它是这篇论文真正可迁移的内核。

先把核心判据钉精确（我的表述，源文分散在 §2.2、§6.1、§7.2 三处，没有合并成一条）：

> **能被安全地写成自然语言共享的知识，是消费者只需照做、不需再推理的知识；需要消费者据此重新推理方向的知识，必须以可查询、可重算的结构共享——否则一次错误归纳会静默污染所有下游。**

Auto-RecSys 在运维知识上严格遵守了这条（dead ends 是真实失败的记录，照做即可），在研究结论上违反了它（lessons learned 是三值标量加自由文本，消费者要据此决定下一个 idea 往哪走）。它自己的数据提供了违反的代价：第 21 次迭代基线切换后，**6 个连续的「切换前正向」结论在新基线上全部失败**。

## 二、域背景：并行之后，「分享什么」是唯一能产生新能力的环节（我的分析，非源文）

源文给了两个 challenge 和一张对照表，但没有解释为什么并行会把「分享什么」顶成核心问题。这一节是我的推理，用来交代后面所有分流的动机。

**串行的时候不需要分享，因为只有一个执行体。** 小尺度 auto-research（AI Scientist、AutoResearch、FARS）之所以能把经验共享这件事整个跳过，是因为它是一个 agent 在一个连续 session 里串行迭代：上一次的教训天然还在 context window 里。context 就是记忆，不需要外化，也不需要选形式。

**并行把 context 打碎了，于是「记忆必须外化」从可选变成强制。** N 个分支各在自己的 session、自己的服务器、自己的 context window 里。任何一个分支学到的东西，若不写出来，对其他分支就等于没发生。这是并行的第一笔账单，也是最容易被忽略的一笔：**并行不只是把工作量切开，它把「共享内存」这个原来免费的假设取消了。**

**外化就必须选形式，而形式选错的代价被并行放大 N 倍。** 串行时一条错误的经验只毒害后续时间线上的一串实验；并行时它被 N 个分支在各自 session start 时同时读入，同时中毒。所以「分享什么形式」不是一个工程品味问题，它的错误代价随并行度线性增长。

**这就解释了论文为什么在形式上如此固执。** 它两次专门论证「为什么是自然语言」：§2.2 说 LLM 推理灵活但不精确，而状态管理要求精确，「a single wrong field in a JSON state file can corrupt an entire experiment lifecycle」；§4.3 和 §7.2 说 LLM 消费程序性知识最有效的方式是「written in the same language they reason in」，并给了实证——审查 31 份 session transcript 发现「The agent seldom queries numerical metadata or scoring data」。它甚至举了具体对照：一条 dead end 写成「the runtime batch object exposes a feature under an internal field name that differs from its raw data-warehouse column name」是**直接可执行的**，而写成一个数值置信度分数则**需要额外一步解释**。

**但「operational」这个限定词被论文自己丢掉了。** §7.2 那句原话是 agent 偏好把 **operational** knowledge 当自然语言指令消费。到了 §4.3 的结论句里，它被推广成「LLM agents consume **procedural** knowledge effectively when it is written in the same language they reason in」。operational 是「照着做」，procedural 是「按流程做」，两者都不含「据此判断方向」。这个推广是全文最关键的一次滑动，§八 会回到它。

**这一节的结论**（它决定了后面所有分流的形状）：并行系统的知识层设计，本质是在回答「哪些知识可以容忍模糊、哪些不能」。判据不是知识的重要性，而是**消费者的解码方式**——照做、还是重新推理。

## 三、分享什么：三路知识分流，以及为什么是这种形式（核心）

论文没有把「分享了什么」集中讲过，它分散在 §2.2（三层知识架构）、§4.2（playbook 六类）、§4.3（蒸馏三类）、§6.1（存储布局）。合起来是三路，我按**消费者**重排：

| 分享物 | 形式 | 谁写 | 谁读 | 失效模式 |
| --- | --- | --- | --- | --- |
| **运维知识**：dead ends（疤痕组织）/ pipeline recipes / submission config（后两者合称肌肉记忆） | 自然语言 markdown，`playbooks/<model>.md`；dead ends 写成「DO NOT」指令，pipeline 写成编号步骤 | 迭代结束时 agent 分析**自己的** session trajectory 蒸馏 | LLM，在 session start 读入 | **过期**——基建或基线变了，这条知识作废，最坏结果是多撞一次坑 |
| **系统状态**：registry / per-idea state / baselines / experiment history / idea backlog / session index | 结构化 JSON/JSONL，固定 schema；**LLM 不许自由编辑**，由确定性脚本读写 | 确定性脚本 | 确定性脚本；同时可直接渲染成 dashboard 给**人** | **损坏**——一个字段写错毁掉整个实验生命周期，且让故障恢复远更难 |
| **研究结论**：verdict（positive / neutral / negative）+ structured lessons learned | append-only `experiment_history.jsonl` 里的三值标量 + 自由文本 | 分析阶段的 agent | 后续 ideation session 查询它 | **反号**——基线一变，正向结论可能变成有害结论 |

### 3.1 分流判据：三个消费者，三种解码成本

前两路的分流是有原则的，而且原则被论文完整论证了。**完整判据不是我上一轮说的「精确归代码、灵活归自然语言」——那只讲了一半。** §6.1 给了另一半，方向是反的：状态之所以必须走确定性脚本 + 固定 schema，是因为**它要被人聚合观测**。源文原话：如果同样的状态「散落在自由格式日志里或嵌在自然语言 memory 里」，那个 centralized dashboard「would be far harder to build」。dashboard 把「监督一个大型、分布式、多天的实验组合」变成「a straightforward monitoring task」。

所以边界不是按精确/灵活划的，是按**消费者有几个、各自解码成本结构如何**划的：

- 消费者是**确定性脚本** → 结构化 schema。零解码成本，要求精确，不容忍模糊。
- 消费者是**LLM** → 自然语言。零解码成本，容忍模糊，但要求「照做即可执行」。
- 消费者是**人（聚合观测）** → 结构化 schema。自由文本无法被聚合成表格。

playbook 和 model knowledge base 被刻意留在自然语言，恰恰因为它们**只需要被 agent 读懂，不需要被聚合成视图**。这不是工程洁癖，是并行组合下「人怎么监督 N 个分支」这个约束倒推出来的。

### 3.2 第三路违反了自己的判据

第三路（研究结论）的消费者是 LLM，形式是自然语言，看起来合规。但**它的用途不是照做，是重新推理方向**。源文 §5.3 明写后续 ideation session 查询 history 来做四件事：对已试 idea 去重、把部分成功组合成更强的复合 idea（例：把两个各自独立有效的特征配对）、剪掉在该模型上持续失败的 idea 类别、瞄准 idea space 里未探索的区域。

这四件事全是归纳推理，没有一件是照做。而它拿到的输入是三值标量加一段自由文本。按 §3.1 的判据，这应该走结构化那一路——至少要带上「这个 verdict 是相对哪个基线纪元得到的」这一维。论文的 `experiment_history.jsonl` 是扁平日志，schema 里看不到这一维（源文没有列出 history 的字段，这是我从 §6.1 的存储布局和 §5.3 的描述推断的空缺，属**我的分析**）。

### 3.3 三层知识架构与 one-shot transfer

分流之外还有一层纵向结构（§2.2），三层特异性递增：

1. **model-agnostic orchestrator skill**：核心实验循环写一次、全模型共用——状态转换、idea 选择、基线管理、分析方法论。
2. **per-model playbook**：一份紧凑的自然语言 skill artifact，记录随架构变化的域知识——关键文件、配置约定、硬件要求、dead ends、proven strategies。六类内容（§4.2）：关键 config/model/trainer 文件及其重要类与函数；配置 flag 纪律（命名约定、guard 模式、插入点）；确切验证命令及其期望输出；submission recipe（硬件型号、resource entitlements、scheduling tags、package layer 版本、warm-start checkpoint 配置）；dead ends（历次错误 + 根因 + 修复）；proven strategies。
3. **per-iteration state file**：当前任务的短暂细节——commit hash、job id、验证结果、分析裁决。

**one-shot transfer playbook creation**（§4.4）：迁移的是**结构**（六类知识的分类与组织方式），不是内容。第一个模型的 playbook 通过若干次交互式迭代蒸馏成成熟模板；后续模型的首次跑仍是交互式的，但不再重新发现「一个好 playbook 该怎么组织」，而是复用模板、只往槽里填新模型自己的指针（关键文件、配置约定、验证命令、submission recipe、可能的 dead ends）。源文说这是「让 Auto-RecSys 能跨多模型 scale 的机制」。每个迁移来的 playbook 此后独立演化。

**这里有一个论文没有说的限定**（我的分析）：结构可迁移，但结构的**槽位本身就是 Meta 基建的形状**——package layer 版本、resource entitlements、scheduling tags、warm-start checkpoint 这些都是特定基建的产物。换一套基建，六类里至少两类会消失、另几类会换名。所以 one-shot transfer 的适用域是「同一套基建下的多个模型」，不是「任意组织」。

### 3.4 借用 SkillOpt 的词：rejected-edit buffer 与 accepted edits

论文把自己的 dead-end catalog 明确对应到 SkillOpt（Yang et al., 2026）的 **rejected-edit buffer**（记录失败过的、不该重复的方法），把 pipeline recipes 和 submission configs 对应到 **accepted edits**（经成功迭代验证过的）。它引 SkillOpt 对 skill 的定义：「portable natural-language artifacts that package procedures, domain heuristics, tool policies, output constraints, and failure modes, letting a frozen agent adapt through external text」——注意 **frozen agent**：底座模型不动，靠外部文本适配。

**但这个借用只借了一半，而且论文自己承认了**（§9）：SkillOpt 的消融显示去掉 validation gate 会退化，而「Auto-RecSys currently accepts playbook updates unconditionally based on agent judgment」。它的辩护是「dead ends record actual failures (they are correct by construction)」。**这条辩护对 rejected-edit buffer 成立，对 accepted edits 不成立**——proven strategy 不是一次失败的记录，是一次归纳，而样本量常常是 1。§八 会展开。

## 四、困难 ↔ 方案 咬合

### 4.1 一阶困难（源文自述结构，压缩）

| 困难 | 方案 | 为什么这么解 |
| --- | --- | --- |
| **长反馈环**：单次训练几天，串行迭代不可行（源文：一个完整研究周期含 ideation、实现、验证、训练、故障恢复、结果分析，通常 **3 到 7 天**） | 分布式异步执行 + distributed experiment portfolio | 保持研究速度需要多个 idea 在分布式资源上并发实现、训练、监控，结果「asynchronously as they become available」 |
| **系统复杂度**：几千行配置、跨代码与基建的依赖、专用硬件、作业会因抢占/checkpoint 损坏/数据过期/兼容性问题失败；session 会在实现中途终止，server 会在训练中重启 | 集中式跨服务器 memory + 持久状态机 | 「Because every run is computationally expensive, execution must remain recoverable across sessions, servers, and failures」 |
| **LLM 灵活但不精确，而状态管理要求精确** | 认知-程序分离：自然语言 skill 引导推理/规划/诊断，确定性脚本执行状态转换、API 交互、校验、文件操作 | 「a single wrong field in a JSON state file can corrupt an entire experiment lifecycle and make failure recovery far harder」 |

五条设计原则（§2.1）：① **composes rather than reinvents**——建立在既有的分布式训练、作业提交、版本控制、指标监控之上，每个 specialist agent 只是这些成熟工具上的薄编排层；② 决策点保留 human in the loop；③ **asynchronous by design**——「It never assumes that the same agent session, or even the same server, will remain available when a multi-day training job completes」；④ self-evolving——执行流程与研究方向都通过结构化反馈改进，而非手工写规则，使运维知识成为「an appreciating asset rather than a static configuration」；⑤ **failure as expected and recoverable**——atomic writes 防状态损坏、append-only logs 保留历史、trajectory logs 支持上下文恢复、dead-end catalog 避免重复昂贵错误。

> **源文内部不一致（原样记录，不替它圆）**：§2.1 说 interactive 模式停在**四个** checkpoint——idea selection、code review、training submission、results review；§7.1 说 human-in-the-loop 模式下研究员只在**两个** review checkpoint 保留控制——idea selection 和 implementation review，其余（验证、提交、监控、故障恢复、分析）委托给系统。两处对不上，我无法判断哪个是当前实现。

### 4.2 二阶困难：并行制造的新问题（这张表是本节的主体）

论文把并行的代价拆散在三个章节里各讲一半：portfolio 在 §5.2（挂在 Idea Loop 底下）、playbook 在 §4（挂在 Execution Loop 底下）、持久化在 §6，三处各自成立但没有串成因果。合并后是这样：

| 并行带来的新问题 | 解法 | 源文依据 |
| --- | --- | --- |
| **状态争用**：N 个 idea 同时在一个模型上跑，共享一份 mutable state 会互相覆盖 | per-idea state file 隔离（`state/<model>/active/<idea>.json`），而非 per-model 单一状态 | 「there is no contention between parallel ideas」 |
| **故障传染**：一个分支烧了几小时 GPU 后失败，可能拖垮旁边的分支 | 同一套隔离顺带做故障容纳 | 「an idea whose training job fails after hours of GPU time affects only its own state file and never blocks or corrupts the ideas running alongside it」 |
| **结果不可比**：并行的全部意义是横向择优，但各分支若用不同基线或不同训练日期区间，比较无效 | 同模型所有 idea 共享一个 common baseline，且**训练日期区间对齐**；`baselines.json` 带 lifecycle | 「ensuring fair A/B comparison」 |
| **谁在做哪个**：多 session、多服务器，两个 agent 可能抓同一个 idea | global registry（`state/registry.json`，注释即「Global: active ideas across servers」）+ `sessions/index.json`（「Session -> model/idea lookup」） | 「preventing conflicts」 |
| **人的监督崩溃**：十几个 idea 跨十多台服务器处在不同阶段，人根本看不见 | centralized dashboard 直接渲染结构化状态 | 「turns oversight of a large, distributed, multi-day experiment portfolio into a straightforward monitoring task」；若状态散在自由文本日志里则「far harder to build」 |
| **会话与服务器寿命断裂** | 集中 memory store + session trajectory 日志 + 启动时 recovery protocol：读 global registry 发现所有服务器上的 active idea → 读目标模型每个 active idea 的 state file → 若当前 session id 与记录不同则读上一会话轨迹重建上下文 → 对 training 态立即轮询远端作业 → 给摘要并路由 | §6.2 全节 |
| **代码只活在本地 checkout**：各服务器独立 checkout，上个会话的 commit 在新机器上不存在 | 每个改动都发布成 **draft diff** 到共享 code-review 系统；恢复时 `get_diff_num(idea)` 从结构化 state file 取回 diff 号直接 apply | 「avoids the token cost of regenerating work」 |
| **昂贵失败被放大**：并行下丢一个失败实验的上下文、或重复一个已知坏配置，浪费的是本可用于探索的资源 | atomic writes + append-only JSONL（每行独立可解析，坏一条不连坐）+ dead-end catalog | 第五条设计原则；§6 开头「Robustness is not optional at industry scale; it is a hard requirement」 |
| **运维失败被复制 N 份**：每个并行分支都要独立跑通那套几千行配置 + 硬件 + entitlement + package layer 的提交路径 | playbook——per-model、被该模型上所有并行分支在 session start 共同读取的共享知识层 | §4.1「At industry scale, operational knowledge is itself the bottleneck」 |
| **想法层撞车与重复**：N 个分支探索同一 idea space，可能试同一个特征或重走已失败方向 | 所有候选 idea 过同一条下游流水线：对 append-only `experiment_history.jsonl` 去重、按预期指标影响/实现复杂度/回归风险/相对新颖度排序进 `idea_backlog.json`（ranked queue）；自主模式从 backlog 链式取 | §5.1、§5.3 |

### 4.3 存储布局（源文 §6.1，逐字）

```
state/
  registry.json              # Global: active ideas across servers
  <model>/
    active/<idea>.json       # In-flight idea state (mutable)
    completed/<idea>.json    # Archived (read-only)
    baselines.json           # Shared baselines with lifecycle
    experiment_history.jsonl # Append-only log
    idea_backlog.json        # Ranked queue
    playbooks/
      <model>.md             # Human-readable recipe
      <model>_meta.json      # Iteration metadata
    ideas/
      <model>/<idea>.md      # Per-idea details
    knowledge_base/
      <model>/feature.md
      <model>/arch.md        # Model-specific knowledge
    sessions/
      index.json             # Session -> model/idea lookup
      <session_id>.jsonl     # Trajectory backup
```

这个布局本身就是 §3.1 那张分流表的物理形态：`playbooks/*.md`、`ideas/*.md`、`knowledge_base/*.md` 是自然语言那一路；`registry.json`、`active/*.json`、`baselines.json`、`*.jsonl` 是结构化那一路。**分流不是修辞，是目录结构。**

### 4.4 playbook 演化的生命周期（源文 §4.4）

一次性 bootstrap，然后持续演化，三阶段，源文说它「mirrors how a human researcher becomes proficient with a new model」：

1. 首次交互式迭代：人指代码、notebook、训练配置，系统把它们总结成初始 playbook，错误恢复仍需人指导。
2. 接下来若干次迭代：系统在 session start 加载 playbook 并沿用其 proven patterns；dead ends 累积，失败率下降，人在关键 checkpoint 审查但介入越来越少。
3. playbook 成熟：pipeline recipes 稳定、submission config 结晶、dead-end catalog 完备 → 自主模式变可靠，系统无人干预跑完整循环，「pausing only for the unavoidable asynchronous wait during training」。

关键数字（§4.1）：这套运维知识「A human researcher accumulates ... over weeks. Auto-RecSys captures it in the playbook after **one or two interactive iterations**」。**这句话是全文最重要的自我定位，§八 会回到它——它描述的是知识获取加速，不是能力持续上升。**

### 4.5 想法层：三个来源，一条流水线

ideation grounded in model architecture：集中 memory 维护一份 model context，捕获模型架构、task heads、feature inventory、enabled modules 等。源文给了一个很实际的动机——工业级模型跨几千行代码与配置，每次 session 重新读取并重新推导架构会消耗大量 token；复用记忆化的 context、只刷新变化部分，就把 token 预算花在 ideation 而不是重新学习已知 things 上。

三个候选来源（§5.1）：① 研究员直接提案（如描述一个想被评估的改动的 design document）；② 挖掘外部文献，把近期论文的技术适配到当前模型；③ 从 model knowledge base 自主 brainstorm——分析架构缺口，把常见改进模式（embedding 策略、gating 机制、auxiliary loss）应用到「数据里存在但模型尚未捕获的信号」「组件间缺失的交互」「未被充分利用的模块」上。

无论来源，统一过同一条下游流水线：对 experiment history 过滤（哪类 idea 成功过、哪类失败过、如何避免重复同时在部分成功上叠加）→ 按**预期指标影响、实现复杂度、回归风险、相对既有实验的新颖度**排序。

每个 idea 都被具体化：可测假设、知识库引用、要修改的目标文件。源文说这种具体性有两个用途——作为质量保障使 idea 交给执行 agent 后直接可动；支持人类监督，因为工业尺度实验资源密集，每个 idea 都记成有组织的、人类可读的 markdown，「so that a domain expert can review it and judge whether it makes sense before any training resources are committed」。

### 4.6 还没解掉的瓶颈（源文 §9 自认）

- **proxy models**：训练时长仍是瓶颈。未来用小尺度副本做快速筛选，若小尺度结果能可靠迁移到全尺度，系统可快速筛几十个 idea、只对最有希望的做全尺度训练。
- **跨模型知识迁移**：目前每个模型维护独立 playbook 和 history。「gating mechanisms help multi-task models」「embedding dimension sweeps have diminishing returns above 128」这类洞见本可在相似架构间迁移。
- **playbook 更新缺验证闸门**：见 §3.4。建议的轻量机制是「verifying that a new dead-end entry does not conflict with existing proven strategies」。
- **human-in-the-loop 只是二元开关**：应按校准置信度选择性求助——高置信低成本决策自主进行，新的或高影响决策（新模型首个实验、高回归风险 idea）触发人类审查。
- **只面向单研究员**：团队级要解共享 backlog、协作 history、多用户冲突解决；per-model 隔离架构是自然起点。

## 五、它看起来像 MapReduce，难的地方都不在像的部分（我的分析，非源文）

拓扑层面这个类比是对的，而且「worker 回传经验」这半句抓到了论文没有明说的东西：经验回流是 worker 的义务而不是 master 的采集——trajectory log 由每个 session 自动写，蒸馏发生在迭代结束时，master 不主动去问。一个协调者（orchestrator + global registry + idea backlog + 集中 memory store）、N 个执行者（不同开发服务器上的 agent session）从队列取 idea、共享状态、把经验写回。

但 MapReduce 的设计目标恰好是把并行的那十类困难**全部消掉**：同质可互换的 map、同步 barrier、无状态幂等所以容错等于重算、确定性 reduce。用它当透镜，§4.2 那张表正好落在盲区里。三处不成立：

**一、MR 的 reduce 是函数，这里的 reduce 是归纳推理。** MR 的 combiner/reducer 是确定性的，N 个 map 输出合成一个确定结果，语义上等价于逐个处理。这里是 46 个 session 的轨迹被 agent「分析后提取知识」写成自然语言 dead end 和 pipeline recipe——摘要函数，必然有损，丢什么由 LLM 判断，且论文自认无验证闸门。MR 里 reduce 错了是 bug，会被测试抓到；这里 reduce 错了会静默写进所有未来 worker 的输入。

**二、MR 的 map 无状态幂等，所以容错是重算；这里的 map 是有状态长事务，所以容错只能是恢复。** 这条最硬。MR 里 worker 挂了就把同一个 split 重跑，输出一样。这里 worker 挂掉后，新 worker 必须读 registry、读 state file、发现 session id 不同、读上一会话轨迹重建上下文、再用 `get_diff_num(idea)` 取回 draft diff 才能接着干。**如果这是 MR，论文整个 §6.2 不需要存在。** 而三大 harness 设计里有两个（集中式跨服务器 memory、认知-程序分离）存在的唯一理由就是「不能重算只能恢复」——重放代价是几百 GPU-hours，所以状态必须精确到一个 JSON 字段。

**三、MR 有 barrier、是 DAG、一轮就完成；这里刻意没有 barrier，而且带反馈回路。** 源文写的是 asynchronous by design，每个 idea 独立处在 ideating→implementing→validating→training→analyzing（训练失败则 branch 到 debugging）→回到 ideating 的不同阶段。没有 shuffle，没有全局同步点，没有「job 完成」这个状态。而且 reduce 的输出被喂回 map 的输入：playbook 改变后续每个 worker 的行为，experiment history 改变后续 idea 的生成。

更贴的类比是 **work-stealing 任务队列 + 一块批量刷新的黑板 + 一个会被 worker 改写的调度器**。但连 blackboard 这个类比也要打个折：经典 blackboard architecture 是机会主义、增量写入的——任何知识源一有贡献就写黑板，其他知识源立刻看见。Auto-RecSys 的黑板要等分支自己迭代结束、轨迹被蒸馏进 playbook，别的分支才可能在**下一次 session start** 读到。经验共享延迟 = 一整个迭代周期（几天）。它更像每几天同步一次的分布式缓存。这个区别有实际后果（§八 第五条）。

**类比好坏的判据是预测力。** MR 框架会预测「加机器 → 吞吐线性上升」。实际不会：同模型所有 idea 必须共享对齐训练日期区间的 baseline，并行度受 baseline 生命周期约束；GPU 配额和 entitlement 才是真瓶颈，不是 worker 数；playbook 内容 per-model 不共享，加一个新模型不是加一个 map split，而是要重新交互式 bootstrap 一次。MR 还会预测「某个 worker 慢不拖累别人」，而基线切换是同时作废所有在飞分支的 submission config。

**还有一处 master 并不只在生成 idea：它被 worker 改写过。** 见 §6.2 第二个案例。MR 里 worker 不会重写 JobTracker。

## 六、标杆案例：一个证明 infra 闭环，一个暴露 RSI 的危险模式

### 6.1 跨服务器恢复（源文 §7.3，infra 那一路的完整走通）

一个 agent 在做某个 idea，实现完改动，**还没来得及验证或提交训练**，开发服务器的 lease 到期，会话几乎立刻崩溃。另一台服务器上的 agent 后来接手同一个 idea。

因为每台服务器独立 checkout，上个会话的代码不在新 checkout 里。接手的 agent 从本地 commit 历史察觉到这点——源文引了它的原话：「the commit from the previous session doesn't exist in this checkout; it was working on a different server」——然后读轨迹日志重建「上个会话做了什么」的上下文，用 `get_diff_num(idea)` 从结构化 state file 取回上个会话已提交到共享 code-review 系统的 draft diff 号，直接 apply，接着验证、提交训练、收尾整个迭代，**全程无人指导**。

支撑它的设计是：每个代码改动都发布成 draft diff，而不只留在本地 checkout。源文的结论：「any agent on any server can resume an in-flight idea directly from the shared state」，这使跨服务器 handoff 无缝，并避免了重新生成工作的 token 成本。

另两个恢复证据（源文 §7.3）：
- **自主执行深度**：观测到的最自主会话连续执行 **970 条日志（110 次工具调用）零人工干预**——诊断失败的训练作业、把根因定位到共享 operator 库里一个 fused-kernel import、重建 package layer、重提交实验。
- **自适应改流程**：一个 feature-gating 实验在 publish 步骤连败 **4 次**（共享 ranking 模块的 ahead-of-time compilation 失败），系统改用跳过该 publish 步骤的训练流，下一次一遍过。源文强调这显示系统改的不只是参数，而是执行流程本身。

### 6.2 五个自我演化机制（源文 §7.2，审查 46 个 session、跨十多台开发服务器的原始轨迹）

- **dead-end 回避**：bootstrap 期间通过**三次失败作业**学到某一代 GPU 会造成反复的硬件作业失败，记为 dead end，此后自动选稳定的一代；后续某次迭代明确加载了「flash attention 在该硬件上是坏的、应使用手动 fallback」这条教训。
- **pipeline config 结晶**：submission config 累积了硬件型号、package layer 版本、resource entitlements、scheduling tags、resource-partition flags、ownership metadata、build target、model type 等，每一项都从一次具体失败中学到，此后被每个后续迭代消费。
- **validation-skip 模式**：当某台开发服务器没有 GPU 时，playbook 引导系统跳过本地 toy-train 验证、直接远程提交训练，每次省掉一次失败的验证尝试和不必要的人工介入。
- **自我诊断的基建改造**：多天监控中，系统发现后台 monitor agent 会在**约 3 到 5 小时**后静默死掉，原因是每个轮询周期都追加工具结果直到 LLM context window 溢出。它**自主设计**了一个基于 cron 的替代方案——每个 tick 都是全新 prompt、无上下文累积——实现它，并提交了一个升级 orchestrator 本身的代码改动。源文：「improving its own infrastructure rather than just the model」。
- **涌现的元模式识别**：在**第六个**连续的「切换前正向、在新基线上失败」之后，agent **未被提示地**自己综合出：新基线已经捕获了这些特征提供的信号，使它们冗余甚至有害。这个观察被记为一条 learning，并「directly drove the pivot toward experiments native to the new baseline」。

**这两个案例的份量完全不同**（我的分析）。前四个是 infra 层的知识积累，机制清楚、有数字、可验证。第四个（改 orchestrator）是全文唯一一个真正的递归自我改进证据——worker 重写了调度器——却埋在 bullet 里、没有附任何数字。第五个是唯一一个 idea 层的自我归纳，而它恰好是 §八 要重点处理的那个危险模式：一个未经验证的归纳，直接改变了整个后续搜索方向。

## 七、效果（源文数字，逐个标注属于哪一路）

### 7.1 人力口径

源文明确拒绝用端到端周期时间衡量：wall-clock 由训练主导，而 Auto-RecSys 不缩短训练（「an industry-scale run still takes days no matter how it is launched」），且周期时间还受集群排队、基线可用性等系统外因素影响。它主张的指标是**每个 idea 消耗的人力带宽**——把一个 idea 从提案带到已分析结果所需的动手研究员注意力。

- 手工流程：同等复杂度的单个 idea 需要 **hours to days** 的主动人力投入，分散在实现、验证、提交、监控、故障恢复、分析。
- human-in-the-loop 模式：研究员在两个 review checkpoint 保留控制，其余委托系统，同等复杂度 idea 的动手投入降到 **minutes**。
- 全自主模式：跳过 checkpoint，人力降到最低，仅限选 idea 和响应系统无法自行解决的升级。源文原话：这「minimizes human time but **risks pursuing weaker ideas and spending training resources on them**」，所以只在 playbook 成熟且候选 idea 低风险时才用。
- 合并效果：「on the same hands-on allotment, the attention that once covered a single idea now covers **more than a dozen**」。

### 7.2 执行可靠性演化（infra 那一路，唯一的量化证据）

**31 次唯一实验迭代，一个模型**。选这个模型因为它是代表性模型，且**在评估期内经历了一次基线切换**——这让我们能在两个 regime 下观察学习与演化：playbook 在稳定基线上首次成熟，以及在底层模型变化后恢复。

四个从 session trajectory log 导出的指标（源文定义）：
- **session log step**：一次自主迭代在轨迹日志里记录的一串带时间戳动作（实现决策、观察、作业提交、错误恢复、分析结果），每一条是一个离散的 agent 动作。
- **major fix step**：花在从**运维**失败中恢复的日志步——训练作业失败或重提交、硬件或 entitlement 设置错、package layer 版本不匹配、metadata 修正、基线刷新。**刻意排除**实现 idea 时的推理与调试，因为那部分努力取决于 idea 复杂度和底座模型能力而非 playbook 成熟度，算作 productive work。「Restricting the metric to operational failures lets it reflect what the playbook actually controls, namely the failures that a more knowledgeable playbook could have avoided.」
- **zero-fix rate**：零 major fix step 完成的迭代占比。
- **error category**：共享同一根因的一类运维失败（如「GPU hardware instability」「build date parameter conventions」）。playbook 把单个错误记为 dead ends，论文把它们归成类别以分析整类失败是否跨阶段被消除。

四阶段与数字：

| 阶段 | 迭代 | 关键数字 |
| --- | --- | --- |
| Bootstrap | 1–4 | 交互式蒸馏出初始 playbook |
| Stabilized | 5–20 | playbook 吸收硬件选择、提交参数、build 约定、input-naming 规则，major fixes 从 **4.0 降到 1.3** 每次迭代 |
| MC3 Reval. | 21–25 | 第 21 次迭代基线从标准架构切换为整合了 **graph-mode compilation + 一个新 embedding module + task adapters** 的组合配置，改动了提交基建（不同硬件、entitlements、package layer 版本、upstream revisions）。**连续 5 次迭代都需要运维恢复**，原因是新配置的硬件与 entitlements 错误、adapter 注入失败、package layer 版本不匹配、upstream revision 冲突。两个指标被打回 bootstrap 水平 |
| MC3 Native | 26–31 | **0.5 major fixes 每次迭代，6 次里 5 次完全不需要运维修复**，超过切换前的稳定期水平 |

结论里合并成一句：「from 4.0 to 0.5 fixes per iteration across 31 unique iterations」。

**错误是分类的而非随机的**：每一类（GPU 硬件不稳、缺 resource tag、build date 参数错、input-naming 约定、package layer 版本不匹配）只在一两个阶段出现，被记为 dead end，然后在吸收了修复的阶段消失。过渡重验证阶段引入两个新类别——package layer 不匹配和 publish 基建失败——两者在后过渡阶段都不存在。**后过渡阶段唯一的错误是一个真正新颖的代码 bug：graph compilation 里的 type-inference 失败，任何先验经验都无法预防。**

**playbook 如何影响 agent 行为**（审查全部 31 份 transcript）：影响主要通过自然语言运作。agent 在 session start 读 playbook markdown 并遵循其指令——dead-ends 表（**19 条**带明确「DO NOT」指令）防止已知错误，proven-strategies 表指导实现模式，pipeline recipes 指定确切工具序列。**agent 很少查询数值 metadata 或打分数据。** 论文据此下结论：一条 dead-end 描述如「the runtime batch object exposes a feature under an internal field name that differs from its raw data-warehouse column name」对 agent 是直接可执行的，而一个数值置信度分数需要额外一步解释——「The playbook's effectiveness comes from writing errors and fixes in the same language the agent reasons in.」

**结晶出的分阶段流水线**：实现期对 **6 个**关键文件的 read 调用；验证用 toy-train 命令；训练用带 **9 个**钉死参数的 build-based submission；分析是一次取指标调用加一次比基线调用。这条流水线是从 playbook 里累积的 **49 个 dead ends 和 17 个 error-fix 模式**演化出来的。

### 7.3 想法层的效果：零个数字

**全文没有任何关于 idea 质量的量化结果**（我的核查，非源文陈述）：没有正向/中性/负向裁决的分布，没有 idea 存活率，没有单位 GPU-hours 产出的有效改动数，没有 history 去重实际拦掉了多少次重复，没有复合 idea（把两个各自有效的特征配对）成功过几次，没有「剪掉持续失败类别」这个动作的准确率。§5.3 描述的四条用途全部是机制描述，一条都没有配数字。

唯一带 idea 层信息的量化事实是那个负面的：**6 个连续的切换前正向结论在新基线上全部失败。**

## 八、为什么这是一篇 infra 论文而不是 RSI 论文（我的分析，非源文）

用户的判据很准：并行之后，经验分享的**内容和形式**才是核心；抽掉它，剩下的全是 infra。这一节把这个判据做成可检验的。

### 8.1 一个分类器：删掉哪一半，数字会消失

把所有与 idea 质量相关的内容删掉，论文的所有数字**一个都不会变**——4.0→1.3→0.5、19 条 DO NOT、49 dead ends、17 error-fix 模式、6 个文件读、9 个钉死参数、970 条日志、110 次工具调用、4 次 publish 失败、3–5 小时 monitor 死亡，全部是运维口径。反过来，把所有 infra 内容删掉，论文就没有数字了。

这不是修辞。它说明论文的**证据、判据、验证全部只在 infra 那一层闭合**。Idea Evolution Loop 在论文里是一个有骨架、有叙事、无测量的部件。

### 8.2 那条曲线会平，而 RSI 的曲线不该平

论文自己写下了天花板，而且没意识到那是天花板：后过渡阶段唯一的错误是「a genuinely novel code bug ... **that no prior experience could have prevented**」。翻译成一句话——**所有能被经验防止的失败都已被防止了。** 0.5 fixes/iteration、6 次里 5 次零修复，是收敛，不是持续上升。

再叠加 §4.4 那句自我定位：人类研究员要几周积累的运维知识，Auto-RecSys「after **one or two interactive iterations**」就captured 进 playbook。**这描述的是知识获取的一次性加速，不是能力的持续复利。** 把专家暗知识显性化、让所有并行分支共享——这个贡献很实在，站内快手柯南那篇的落点是同一件事（「持续把私域知识搬进 Agent 能消费的地方」），而快手那篇从没声称这是 RSI。

### 8.3 机制版：会过期的和会反号的

上一轮我说的「双环折旧率不同」太含糊。精确的机制是**分享物的语义是否基线相对**：

- **dead end 是「这个配置在这套基建上会以这个方式失败，修复是这个」。** 基建变了它就**过期**。过期的 dead end 最坏结果是让你多撞一次坑——撞了就会重新记录，系统自愈。这是可自愈的失效。
- **verdict 是「这个特征相对某个 baseline 有增益」。** baseline 变了它可能**反号**。反号的 verdict 不会自我暴露：它仍然躺在 `experiment_history.jsonl` 里，仍然被后续 ideation 查询，仍然被当成「这类 idea 成功过」的证据。它让你**放弃一个本来有效的方向，或重做一个已经失效的方向**，而系统没有任何机制察觉。

论文提供了反号的铁证却没把它当成失效模式讨论：6 个连续 positive 在新基线上全灭，agent 自己综合出「新基线已捕获这些信号，这些特征冗余甚至有害」。**注意这个归纳的内容本身就是在说「history 里的 positive 标签已失效」**——系统在自己的数据里撞见了第三路知识的失效模式，把它记成一条 learning（也就是又一条自由文本），然后 pivot。没有回头去清理那 6 条已经反号的记录。

两种失效的代价不对称：**过期是自限的，反号是自我强化的。** 论文对前者有完整机制（dead-end 记录 + 自愈），对后者没有任何机制。

### 8.4 与 Dream-RSI 的正面互证：同一个判据的两半

这是本篇笔记最硬的一块，而且它不是我从单篇推的，是站内阅读语料内部互证出来的。

`notes/reading/dream-rsi-replay-simulator-notes.md` 那篇（Google，arXiv:2609.14858，同期）有一个 §5.1 的负结果：**把发现历史蒸馏成 prompt 里的语义指导是有害的**，所以历史必须以**可执行的结构**（把每个节点的执行现场完整冻结成 replay simulator）而非**可读的建议**被消费。那篇的域背景节把这条当作整个设计的出发点：「既然蒸馏成语义指导有害，那历史就必须以可执行的结构而非可读的建议的形式被消费。」

Auto-RecSys 的结论正好相反：运维知识必须写成自然语言指令，因为 agent 就在它推理的那种语言里消费程序性知识最有效，数值分数反而需要额外解释步骤。

**两篇独立论文给出了相反的答案，因为它们分享的是不同类的知识——而这恰好证明了 §一 那条判据。**

| | Auto-RecSys | Dream-RSI |
| --- | --- | --- |
| 分享什么 | 运维知识：哪个配置会失败、怎么修、提交参数是什么 | 探索策略：往哪生成解、开几条分支、什么时候停 |
| 消费者要做什么 | **照做**（读 DO NOT，避开；读 recipe，执行） | **重新推理**（据此改一段作用域全局的策略代码） |
| 选的形式 | 自然语言 markdown | 可执行、可查询的冻结历史结构 |
| 结果 | 有效，且是全文唯一有数字支撑的部分 | 有效；而自然语言那条路被它实验证明有害 |

判据由此得到双向验证：**照做 → 自然语言；重新推理 → 可执行结构。**

而 Auto-RecSys 的第三路（研究结论）恰好是「让 LLM 拿自然语言 lessons 去重新推理方向」——**它在这一路上违反了自己的判据，也违反了 Dream-RSI 用实验证出来的那条负结果。** 它把该结构化的东西写成了散文。这不是事后诸葛：Dream-RSI 的 §5.1 是一个做了对照实验的负结果，Auto-RecSys 的 §5.3 是一段没有数字的机制描述。

一个必要的公道话（我的分析）：Dream-RSI 的负结果是关于**策略层**的语义指导，Auto-RecSys 的第三路是**idea 层**的结论复用，两者对象不完全同一。但差别不足以挽救——两者的共同点正是判据关心的那点：消费者要据此决定往哪走，而不是照一条已知指令执行。

### 8.5 黑板是批量刷新的，所以并行会重复撞同一个坑

§五 已经指出：dead end 要等分支自己迭代结束、轨迹被蒸馏进 playbook，别的分支才可能在**下一次 session start** 读到。经验共享延迟 = 一整个迭代周期（几天）。

后果（我的推论，源文没讨论）：在并行组合里，N 个分支可能同时撞同一个坑 N 次，各自独立付一次恢复成本，最后产出 N 条几乎相同的 dead end。论文那个「通过三次失败作业学到某代 GPU 不稳」的例子本身就是这个模式的化石——**三次**，而不是一次。它被当成 bootstrap 期的正常学习成本讲，但在一周处理多个实验的组合里，这类重复的代价随并行度上升。

缺的部件很清楚：一个 in-flight 的横向广播机制（某分支撞到未知错误时立刻写黑板，其他分支下次工具调用前就能看到），而不是只在迭代边界批量蒸馏。论文没有任何这类机制，也没有讨论这个代价。

### 8.6 分享与污染是同一个动作，而它违反了自己站内已写下的原则

§3.4 已经引了论文的自认：playbook 更新无条件接受 agent 判断，缺 SkillOpt 那个 validation gate。它的辩护（dead ends correct by construction）只覆盖 rejected-edit buffer，不覆盖 accepted edits——**proven strategy 是从一次成功轨迹归纳出来的，样本量常常是 1。**

更要紧的是结构问题：**跑迭代的 agent 就是从自己轨迹蒸馏 playbook 的 agent，而且是在自己的 active session 里做。** 站内 harness-engineering 系列第 02 篇把这条写成了一个明确原则——「Forcing a main agent to inspect its own work within its active conversation loop introduces heavy confirmation bias and inflates token costs」，所以现代 harness 把 Generator（有状态 worker）和 Evaluator（无状态 contract-checker）严格分离，让评估者「zero knowledge of the agent's historical brainstorming」。

Auto-RecSys 在状态层严格遵守了这个分离（确定性脚本写、LLM 不许自由编辑），但在知识层完全没有：生成者和评估者是同一个 agent、同一个 context。论文自认的「缺验证闸门」不是疏忽，是这个结构的必然结果。

而 §6.2 第五个机制正是这个缺陷的最坏实例：一个未被提示的自我归纳（「新基线已捕获这些信号」）被记为 learning 并「directly drove the pivot」。论文把它当亮点讲。它是 RSI 系统最危险的模式——**自我生成的假设被当成自我验证的知识写回记忆，然后改变了整个后续搜索方向。**

### 8.7 毕业闸门只检查了三根柱子里的第三根

站内《The State Machine of Technical Research》给出一个研究项目的毕业判据：从探索期进入有界执行期，必须显式验证三根柱子——① 技术问题是否锋利、② 差异点是否被证明、③ 数据基建是否就绪；缺任何一根，项目「remains in the playground」。

Auto-RecSys 的 interactive → autonomous 切换条件是什么？源文 §3.2 和 §4.4：「as the playbook matures and accumulates dead-end knowledge, autonomous mode becomes increasingly reliable」；playbook 成熟意味着 pipeline recipes 稳定、submission config 结晶、dead-end catalog 完备。**这全是第三根柱子（基建就绪）。**

而论文自己承认自主模式的风险是「risks pursuing weaker ideas」——那正是第一、二根柱子（问题锋利、差异点被证明）没被检查。所以自主模式的 graduation 是**只凭基建就绪就把项目从 playground 放出来**。

论文提的改进方向（adaptive human-in-the-loop，按校准置信度选择性求助）在概念上就是想把前两根柱子纳入闸门。但它需要一个 idea 级的校准置信度，而系统没有任何 idea 质量测量可供校准（§7.3）——**这是循环依赖：要测量 idea 质量才能安全地自主选 idea，而要安全地自主选 idea 才有便宜的 idea 质量数据。**

### 8.8 打破循环的那个部件，被论文误标成了加速器

§4.6 第一条 future work（proxy models）被论文写成「解决训练时长瓶颈」。按上面 §7.3 和 §8.7，它同时是**唯一能让 Idea Loop 变得可测量的办法**：如果筛一个 idea 只要几分钟而不是几天，你才跑得起统计——idea 命中率、类别存活率、正向裁决在不同基线纪元之间的可迁移性、复合 idea 的成功率。

所以 proxy model 不是加速器，**它是 Idea Loop 的测量仪器**。没有它，§7.3 那个空洞永远填不上，§8.7 那个循环依赖永远解不开。这是我对论文 future work 的重新解读（我的分析，非源文）：论文把一个测量问题当成了性能问题。

顺带，这也是全篇最可惜的一处：论文已经有一个天然的对照实验——第 21 次基线切换。它用这个对照测出了 Execution Loop 的恢复能力（很漂亮），却没有用它测 Idea Loop 的可迁移性（那 6 个反号的 positive 就是现成的数据）。**同一件事件，一路测了，一路只当故事讲了。**

### 8.9 一个不能忽略的评测单元错配

论文卖的是跨服务器、跨模型的分布式并行组合，但可靠性数据是**一个模型上的 31 次迭代，按迭代号排成一条时间线**——那是串行叙事。全文没有一个组合层的数字：同时在飞多少个 idea、跨多少个模型、组合级吞吐（每周完成多少个实验）、分支之间撞车或 registry 冲突发生过几次、基线切换时有多少个在飞分支同时作废。

970 条日志 / 110 次工具调用是**单会话深度**，不是组合宽度。46 sessions across more than ten development servers 是审查语料的规模，不是系统吞吐。§4.2 那张表里一半的解法（registry 防冲突、baseline 对齐、dashboard、跨服务器 handoff）在评测里根本没有对应的观测。

最尖的一处落在第 21 次基线切换：在串行叙事里这是「5 次迭代受影响」；在并行组合里，基线切换是**同时作废所有在飞分支的 submission config**。这个 N 倍放大效应论文没有观测到，因为它的评测单元里没有 N。

### 8.10 组合层是空的

portfolio 这个词借自金融，但只借了「多个持仓并行」，没借仓位管理：没有预算约束，没有 early stopping，没有「这个分支已经烧了 400 GPU-hours 且看起来不行，砍掉」，没有分支间的资源再平衡。`idea_backlog.json` 是一个按预期指标影响/复杂度/回归风险/新颖度排序的队列，排序发生在**入队时**，之后不随实验结果更新（源文没有描述任何重排序机制）。

论文对全自主模式的缓解只有一句纪律性的话（等 playbook 成熟、只挑低风险 idea），不是机制。而按 §8.2，playbook 成熟是**基建**成熟，不是**选题判断**成熟——所以这个缓解措施针对的恰好不是它想防的风险。（我的分析）

## 九、收束：可复制的是分流判据，不可复制的是那 49 个 dead ends——以及壁垒里哪一部分其实是摩擦补偿

### 可复制的通用件

1. **三路知识分流 + §3.1 那个消费者判据**（确定性脚本 / LLM / 人，按解码成本选形式）。这是全篇最可迁移的一条，而且它比论文自己讲的「认知-程序分离」更完整——论文只讲了前两个消费者，dashboard 那条（人的聚合观测反向决定哪些状态必须结构化）是我从 §6.1 读出来的。
2. **三层知识架构**：model-agnostic orchestrator skill / per-model playbook / per-iteration state file，以及「结构可迁移、内容不可迁移」的 one-shot transfer 模式。
3. **playbook 六类**：关键文件、配置 flag 纪律、验证命令 + 期望输出、submission recipe、dead ends、proven strategies。这个分类几乎可以直接抄。
4. **per-idea state 隔离**（而非 per-model 单一状态）同时解决争用与故障传染。
5. **draft diff 而非本地 checkout** 作为跨机器恢复的锚点；append-only JSONL 每行独立可解析；atomic writes。
6. **recovery protocol 的五步**（读 registry → 读 active state → session id 不同则读轨迹 → training 态立即轮询 → 摘要并路由）。
7. **major fix step 这个指标构造**：把「实现期推理与调试」排除在外，只计运维失败，理由是后者才是 playbook 能控制的。这个口径设计本身值得抄——即使 §8.1 指出它的定义域恰好等于被测部件的控制域。
8. **§5.1 那条负结果的镜像**：运维知识不要写成打分，要写成「DO NOT」加编号步骤；而（据 Dream-RSI 互证）方向性结论不要写成散文建议。

### 不可复制的壁垒（收在这里）

- **49 个 dead ends、17 个 error-fix 模式、19 条 DO NOT 指令、9 个钉死的提交参数**，以及它们背后跨十多台服务器、46 个 session 的原始轨迹语料。方法论可以照抄，抄完发现手上没有这些。
- **基建的形状**：集中式 memory store、共享 code-review 系统的 draft diff 语义、lease 语义、package layer 与 entitlement 体系、warm-start checkpoint 的有效性查询。跨服务器无缝 handoff 之所以可能，是因为每个改动都被强制发布成 draft diff——这是一条**组织纪律**，不是技术。
- **对齐训练日期区间的共享 baseline** 及其 lifecycle 管理。没有它，并行的全部意义（横向择优）就不存在。
- **能让研究员接受「一次交互式 bootstrap 换几周暗知识显性化」的组织信任**，以及 interactive/autonomous 双模式提供的渐进授权路径。

### 但壁垒里有一大部分不是护城河，是内部摩擦的度量（我的分析）

这一条要拆开讲，否则会和站内快手那篇的「Context 才是真正的壁垒」错误地合并。

那 49 个 dead ends 的主体是什么？哪代 GPU 稳、哪些 package layer 版本兼容、哪些 entitlement 和 scheduling tag、build date 参数约定、input-naming 约定、publish 基建失败、warm-start checkpoint 是否过期、upstream revision 冲突。**这些知识之所以存在，是因为内部基建不透明且频繁变动。** 在一套干净、文档良好、接口稳定、版本兼容矩阵公开的基建上，playbook 的大半内容根本不需要存在。

所以这里的 Context 有两种，必须分开：

- **域知识型 Context**（快手那 2 万行 Skill、Instagram 那套 conventions）：它编码的是「这个业务/这个平台本质上是怎么回事」，基建变好了它仍然有价值。这是真壁垒。
- **摩擦补偿型 Context**（Auto-RecSys 的大部分 dead ends 和全部 submission config）：它编码的是「我们这套基建有哪些没写下来的坑」。基建修好了它就归零。这是**负债的镜像**，不是资产。

判别方法很便宜：问一句「如果上游把这个坑修了、把这条约定写进文档，这条知识还有价值吗」。dead end 里那条「runtime batch object 用一个内部字段名暴露特征，与它在数据仓库里的原始列名不同」——这是数据基建的接口债，修了就归零。而「gating 机制对多任务模型有帮助」——这是域知识，修什么都不会让它归零（但它恰好在第三路，那个没有验证、会反号的那一路）。

**这个拆分的实际含义**：Auto-RecSys 的 Execution Loop 在把组织的摩擦成本从「每个研究员几周」压到「一次性 bootstrap + 每次迭代 0.5 次修复」。这是真实的、可量化的收益，值得做。但它同时**降低了修复上游基建的动机**——坑被 playbook 吸收之后就不再痛了，而 §2.1 第一条设计原则明写「composes rather than reinvents」，即接受既有基建的形状。所以这套系统是一个摩擦的**缓冲器**，不是一个摩擦的**消除器**，并且它会让摩擦变得不可见。（我的判断，源文没有这层自觉）

### 迁移到其他域的通用启示

三句话：

1. **先分消费者，再选形式。** 问「这条知识是给确定性代码读、给 LLM 读、还是给人聚合观测」，答案唯一决定它该是 schema 还是散文。混用是大多数 agent 记忆系统变糊的原因。
2. **区分「照做型」与「重新推理型」知识，后者绝不要写成散文。** 照做型（已知失败 + 已知修复）写自然语言是对的，而且比打分好。重新推理型（从有限样本归纳出的方向性结论）必须带上下文索引（相对哪个基线/哪个版本/哪个时期得到的）并且可查询、可重算，否则它会在环境变化时静默反号。Auto-RecSys 和 Dream-RSI 各自证明了这条的一半。
3. **区分真壁垒和摩擦补偿。** 沉淀知识之前先问：这条知识在上游修好之后还有价值吗？没有价值的那部分应该被记成一张**待修清单**而不是 playbook——playbook 会让它永久隐形。

---

延伸阅读（本仓，均已读目标正文确认相关）：

- `notes/reading/dream-rsi-replay-simulator-notes.md` —— **本篇最强的一条，两篇在「分享什么形式」上给出相反答案，因而在判据上互证**。那篇 §5.1 是一个做了对照实验的负结果：把发现历史蒸馏成 prompt 里的语义指导**有害**，所以历史必须以可执行的结构（冻结每个节点执行现场的 replay simulator）而非可读的建议被消费；那篇 §二 甚至把这条当成整个设计的出发点。Auto-RecSys 的结论正好相反（运维知识必须写成自然语言，数值分数需要额外解释步骤）。两者不矛盾：那篇分享的是**探索策略**（消费者要重新推理），本篇分享的是**运维知识**（消费者只需照做）。合起来给出 §8.4 那条判据。另外那篇 §7.2「采样分布被优化器自己锁死」与本篇 §8.5「黑板批量刷新」是同一类失效的两个形态——**闭环里没有外力打破它**；那篇的壁垒是「一份把每个节点执行现场完整冻结下来的历史」，本篇的壁垒是「49 个 dead ends + 46 个 session 的轨迹语料」，同一种东西的两个方向：一个要冻结得足以**重放**，一个要积累得足以**回避**。
- `notes/reading/kuaishou-conan-stability-agent-notes.md` —— **同一落点，不同证据强度**。那篇的收束是「五层架构与'确定性归代码/概率性归模型'都是可照搬的通用件，不可复制的是三端 Core Dump 采集基建、预聚合源码服务、30+ Skill / 2 万行私域知识与 Bad Case 闭环」，引源文原话「Context 才是真正的壁垒，也是享受模型升级红利的前提」；它给的真壁垒判别标准是「持续把私域知识搬进 Agent 能消费的地方」这道磨人的坎。本篇 §九 对此做了一个必要的拆分：Context 分**域知识型**（基建修好仍有价值）与**摩擦补偿型**（基建修好即归零），快手那 2 万行 Skill 绝大部分属前者，Auto-RecSys 的 submission config 与大部分 dead ends 属后者。两篇合读可以得到一个更准的说法：**「Context 是壁垒」成立，但要先问这个 Context 编码的是域还是债。** 另外那篇的「专家从'前线救火员'变成'消防系统设计师'」与本篇 §7.1「研究员从一次执行一个 idea 变成管一个组合」是同一个角色位移，一个在稳定性域、一个在模型研究域。
- 《[The Algorithm of Compute: Why Modern Agent Harnesses Focus 80% of Their Design on Context Management](https://cj9208.github.io/blog/ai_study/harness-engineering/the-algorithm-of-compute-why-modern-agent-harnesses-focus-80-of-their-design-on-context-management/)》—— **两处精确咬合，其中一处是 Auto-RecSys 的违规证据**。① 那篇 §2 主张 Generator（有状态 worker）与 Evaluator（无状态 contract-checker）严格分离，理由是「Forcing a main agent to inspect its own work within its active conversation loop introduces heavy confirmation bias」，且评估者要「zero knowledge of the agent's historical brainstorming」。Auto-RecSys 在状态层遵守了这条（确定性脚本写、LLM 不许自由编辑），在知识层完全没有——跑迭代的 agent 就是从自己轨迹蒸馏 playbook 的 agent，且在自己的 active session 里做；论文自认的「缺验证闸门」是这个结构的必然结果（详见本篇 §8.6）。② 那篇 §3 讲 Context Rot：context window 是 RAM，会快速腐烂，随轮次累积成千上万 token 的脏执行日志，触发注意力退化、任务漂移与幻觉，所以 harness 的真正工程里程碑是做一个「memory garbage collector」。本篇 §6.2 那个「后台 monitor agent 在约 3 到 5 小时后静默死掉、因为每个轮询周期追加工具结果直到 context window 溢出」是这个机制的一个**实测实例**——而 agent 自己给出的修复（cron 化、每个 tick 全新 prompt、无上下文累积）正是那篇所说的「保持活跃状态空间洁净」，只不过它是用**无状态化**而不是**垃圾回收**实现的。那篇讲原理，这篇提供了一个野外案例。
- `notes/reading/instagram-direct-compose-ai-native-notes.md` —— **正面冲突，且冲突点正好在 playbook 这条路线上**。那篇引源文最锋利的一句：「guardrails 和 skills 有帮助，但本身不够，因为 AI 遇到摩擦时往往会绕开它们来解锁自己」，所以约束应由**架构本身**承载（Example 3 用构造函数 lambda 切断对外层类状态的访问，是语言级硬边界），而不是写成 skill。Auto-RecSys 走的正是那篇判定为「不 scale」的路线：它的约束是 markdown 里的「DO NOT」指令，是纯指令级软边界。两篇谁对？我的判断是**取决于失败的代价形状**（我的分析）：Instagram 那个域里 agent 绕过约束的产物是**能跑但耦合错的代码**，会静默通过测试、代价延迟爆发，所以必须用硬边界让它根本表达不出来；Auto-RecSys 这个域里 agent 绕过 DO NOT 的产物是**一次失败的训练作业**，几小时内就炸、代价立刻可见、而且炸完就会变成一条新的 dead end。软边界在「失败会自己报错」的域里够用，在「失败会静默通过」的域里不够用。那篇 §八 的壁垒是「能把 Context 的效果测出来并持续调的那套装置」（A/B 能力、risk score、agent 资源效率复合指标），本篇 §7.3 恰好缺的就是这个——**两篇的差距不在方法论，在有没有仪器**。
- 《[The State Machine of Technical Research: Balancing Exploration and Bounded Execution](https://cj9208.github.io/blog/ai_era_engineering_careers/state-machine-technical-research/)》—— **毕业闸门的判据来源，见本篇 §8.7**。那篇 §2 主张项目从探索期进入有界执行期必须显式验证三根柱子（技术问题是否锋利 / 差异点是否被证明 / 数据基建是否就绪），缺任何一根就「remains in the playground」，且「must never transition to production simply because a deadline arrives」。Auto-RecSys 的 interactive → autonomous 切换条件全部落在第三根柱子上（playbook 成熟 = pipeline recipes 稳定 + submission config 结晶 + dead-end catalog 完备），而论文自认的自主模式风险「risks pursuing weaker ideas」正是前两根柱子未被检查。那篇的三柱判据因此可以直接当审计清单用：**一个 agent 系统从「有监督」升到「自主」的门槛，应该按它验证了几根柱子来定，而不是按它的执行可靠性来定。** Auto-RecSys 是用第三根柱子的成熟度去授权前两根柱子的免检。
