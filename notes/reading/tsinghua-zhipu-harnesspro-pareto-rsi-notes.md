# 帕累托前沿上的 hill-climbing：HarnessPro 的 framing/生成两层，与"方法即通用件、mutation operator 才是壁垒"

> 源文：《智谱唐杰署名 RSI 新成果开源！Agent 自我进化成本还狂降 53%》，量子位（QbitAI）公众号，2026-10-23 19:30，作者梦晨。原始 URL <https://mp.weixin.qq.com/s/1nbncYhO5xZ7HAk6F3N0Dw>。
> 论文：HarnessPro，清华唐杰团队 + 智谱，arXiv:2610.26770，GitHub <https://github.com/pzs19/HarnessPro>。通讯作者唐杰（清华计算机系教授 / 智谱首席科学家）、赵虹 Hong (Vicky) Zhao（清华自动化系副教授）；共同一作盘卓实、冯志远（均清华）。盘卓实另一篇 ContextPilot（细粒度 RL 教 Agent 主动管理上下文）刚被 EMNLP 2026 接收。
> 这是一篇读后梳理，不是翻译。主线一句话：**HarnessPro 本质上是 hill-climbing with LLM as the mutation operator + 帕累托多目标筛选——它把 heuristic 优化闭环工程化，用四 Agent 流水线（诊断-规划-编辑-测试）+ Lite/Medium/Heavy 三档前沿代替单点最优；核心贡献不是发明新原理，而是让"越进化越贵"的 RSI 第一次同时把通过率和成本推向前沿，但 mutation operator 仍是 LLM，能力天花板就在那里。**
> 标注约定：§三（架构）、§四（困难↔方案咬合，源文事实为底）、§六（效果）中的所有数字、机制、术语、案例名均为**源文原样**；§一（framing/生成两层拆分）、§二（域背景：为什么"越进化越贵"是硬问题）、§五（标杆案例的流水线映射）、§四表后"层原则"小结、§七（commoditized vs moat 与集群对照）均为**我的分析，非源文**，已就地标注，不要当源文事实引用。

## 一、透镜：先把 framing 层与生成层拆开

源文的宣传口径是"首次将帕累托优化引入 Agent 底座进化"，容易读成一次理论突破。但把系统拆开会发现，它有两层性质完全不同的东西——**结构性 framing** 与 **heuristic 生成机制**。这个区分是本篇笔记的脊柱，后面全部结构都挂在它上面。

**结构性 framing（可抄的方法论骨架）**：

| 部件 | 干什么 | 为什么是 framing 而不是 heuristic |
|---|---|---|
| 帕累托多目标筛选（Lite/Medium/Heavy 三档） | 把 RSI 从"单点最优"改成"暴露整条前沿" | 是多目标优化的标准结构，不依赖具体底座/基准 |
| 测试合成器代替 LLM 裁判 | 判据层从"LLM 自评"换成"合成 10 个可执行 unittest" | 是评估机制的替换，可执行判据比 LLM 自评更可靠这条原则跨域成立 |
| 四 Agent 流水线 + 3-rollouts 稳定性诊断 | 分工骨架：诊断→规划→编辑→测试，每候选跑 3 次 | 是"什么信息进什么 Agent"的架构规定，不是具体补丁 |

**Heuristic 生成机制（换域要重标的经验性补丁）**：

| 部件 | 具体数值 / 形态 | 为什么是 heuristic |
|---|---|---|
| Runtime Hooks 分段预算 | 工具调用 **14 次**塞提醒（Economy phase）/ **26 次**升级警告（Convergence phase）/ **44 次**直接 Block 拦截 | 阈值来自 Terminal-Bench 2 Medium 模式的观察，不是从第一性原理推出来的 |
| 动态路由五档 | compact / lean / standard / deep / research | 档位划分与匹配规则是看到"上下文/推理强度一刀切"的浪费后打的补丁 |
| 日志折叠 | `[previous line repeated N more times]` + 头尾截断 | 类似 RTK (Rust Token Killer)，是应对命令行冗长日志的经验性方案 |
| Hooks 拼在工具返回结果末尾 | 保护 Prompt 前缀缓存（Cache Reuse） | 是"发现提醒消息会破 cache"后的巧妙工程细节，不是通用原则 |

**源文的消融实验恰好佐证 heuristic 那一层的性质**：单独把动态路由或预算钩子给 RHO，能省钱但通过率明显掉点——**heuristic patches 互相咬合、不可拆分，只有组合起来才 work**，这正是 heuristic 优化的典型特征。

**推到底的表述（我的分析）**：这套方法本质上是 **hill-climbing with LLM as the mutation operator**——帕累托筛选把它从单目标变成多目标，测试合成器把评估判据从 LLM 自评换成可执行 unittest。但 **mutation 本身的质量还是取决于 LLM 能不能看诊断报告想出合理补丁**，这就是能力的天花板。所以论文的核心贡献不是"发明了新原理"，是**把 heuristic 优化闭环工程化，并用帕累托筛选暴露多档方案**。是工程贡献，不是理论贡献。

**在本仓 RSI 集群里的定位（我的分析，非源文）**：`notes/reading/rsi-2026-landscape-harness-l1-ignition-l2-notes.md` §3.2 已把 HarnessPro 挂在"其它大厂入场"的位置，标签是"label-free Pareto"。按那篇地图的 L0–L3 尺子，HarnessPro 是**冻结权重改外壳的 L0 机制提案**，还没有一手 L2 点火证据；它的独特角度是**首次把帕累托多目标引入 RSI**——从"单点最优"到"暴露整条前沿"，是这个集群里少见的多目标视角。

## 二、域背景：为什么"越进化越贵"是硬问题（我的分析，非源文）

源文给了痛点陈述（"以往的 RSI 方法往往通过更广泛的探索和更繁琐的验证来换取高分，Token 消耗量和延迟原地爆炸"），但没展开它为什么在物理上这么硬。这一节是我的领域推理，用来交代后面困难集从哪来。

**RSI 的评估函数本身就是主要成本。** 这一点在 `notes/reading/sift-self-improvement-fast-tree-search-notes.md` §二里已经论证过：普通 MCTS/A\* 在任务状态空间里搜，评估一个节点＝读一个状态、算一个 `h(n)`，便宜；RSI 搜的是 agent harness 的设计空间——每个节点是一份会去调度 coding model 的**源码**，评估一个节点＝把改过的 agent 拿去**跑一整套基准**。于是"评估函数"从一次前向变成一次完整的 agent×benchmark 运行，成本抬了几个数量级。

**"越进化越贵"是这条成本的复合效应。** 以往方法（如 RHO）用"更广泛的探索 + 更繁琐的验证"换高分，本质是**在评估函数已经很贵的前提下，继续加码评估次数与评估深度**。分是高了，但 Token 消耗和延迟跟着原地爆炸。这不是工程细节问题，是搜索策略与评估成本耦合的结构性问题。

**HarnessPro 的破法方向因此很清楚**：不动 mutation operator（还是 LLM 出补丁），而是动**筛选机制**（帕累托多目标代替单点最优）与**判据形态**（合成 unittest 代替 LLM 自评）。前者让搜索不再只朝一个方向爬，后者让每次评估更便宜也更可靠。

**同一域背景下的三条平行路线（我的分析，非源文）**：

- **SIFT**（`notes/reading/sift-self-improvement-fast-tree-search-notes.md`）：让 judge 便宜——成对比较 + BT 排序，把评估做成"排序信号"，让搜索与慢评估解耦。
- **RRSI**（`notes/reading/rrsi-regularized-harness-self-improvement-notes.md`）：让进化不过拟合——Proposal 端控复杂度、Selection 端 noise-adjusted floor + cost gate + pruning。
- **HarnessPro**：让筛选多目标化 + 让判据可执行——帕累托前沿 + 测试合成器。

三条都在处理"评估层"的问题，但方向正交：SIFT 走"便宜排序"，RRSI 走"正则化筛选"，HarnessPro 走"多目标前沿 + 可执行判据"。

## 三、架构：四 Agent 流水线（源文原样）

每一轮进化（Epoch）中，四个专门的 Agent 像流水线一样，对候选 Harness 进行"诊断-开方-动刀-体检"：

| Agent | 干什么 | 关键细节（源文） |
|---|---|---|
| **轨迹诊断师** Trajectory Analyzer | 每个候选 Harness 在训练集上独立跑 **3 次 rollouts**，同时调取 3 次完整执行轨迹，找出任务为什么失败 + 哪些操作在纯纯浪费 Token | 附录案例：AI 虽然配好了邮件服务器，但诊断师一眼看出它在无关的配置文件上反复倾倒日志，导致单次任务狂吞 **251 万个输入 Token** |
| **进化规划师** Evolution Planner | 拿到诊断报告和成本指标后出改造方案，用 Diff 工具对比当前候选池里不同 Harness 的代码差异，看看别人的好机制能不能借鉴 | 针对每个候选者，同时开出 **3 张不同侧重点的方案**：成本优先（I₁）、平衡模式（I₂）、性能优先（I₃） |
| **代码编辑器** Harness Editor | 拿到方案后，在独立的工作空间里直接修改 Harness 的底层代码和配置文件，生成新的可执行 Harness | 自动提交到 Git，方便随时追溯和回滚 |
| **测试合成器** Test Synthesizer | 在没有官方测试题的"无标签"环境下，根据任务描述直接编写 **10 个固定的可执行单元测试（unittest）** | 取代 LLM 裁判——LLM 裁判有严重的"盲目乐观"，经常把有缺陷的代码判为成功，对失败案例的召回率只有惨淡的 **41.7%**；合成器把召回率拉到 **83.3%**（+41.7 pp） |

**帕累托筛选与就近选拔（源文）**：生成的一大批新 Harness 经过测试集验证后，系统先无情淘汰掉性能低于初始底线、或者处于"帕累托劣势"（即花钱更多、分还更低）的废案。随后，利用**归一化加权平方距离**准则，分别选出最符合 Lite（省钱）、Medium（均衡）、Heavy（高性能）三个档位的代表，送入下一轮继续迭代进化。

## 四、困难↔方案咬合

按系统自身的层分组：A 判分层（无标签怎么判）、B 进化层（怎么让改造有方向、有多样性、可回滚）、C 运行时层（Agent 自进化出的省钱组合拳）。表中"困难/方案/为什么"均为源文原样（含源文自述的设计理由）；层后"原则一句话"是我的概括。

### A 层 · 判分：无标签环境怎么判

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 没有官方测试用例和标准答案（Label-free） | 测试合成器根据任务描述直接编写 **10 个固定可执行 unittest** | 取代 LLM 裁判——LLM 裁判"盲目乐观"，经常把有缺陷的代码判为成功，对失败案例的召回率只有 **41.7%**；合成器达到 **83.3%**（+41.7 pp） |
| 单次 rollout 偶然性大 | 每候选 Harness 在训练集上独立跑 **3 次 rollouts**，诊断师同时调取 3 次完整轨迹 | 稳定性 + 能对比不同 rollout 找共性浪费（如那个 251 万 token 的邮件服务器案例） |

**A 层原则一句话（我的分析）**：判据形态从"LLM 自评"换成"可执行 unittest"，是评估机制的替换——可执行判据比 LLM 自评更可靠这条原则跨域成立，与 `notes/reading/airbnb-eval-driven-development-notes.md` "把'什么叫好'编译成可执行工件"同一思路，只是 Airbnb 编译成 rubric + golden set + VJ，HarnessPro 编译成 unittest。

### B 层 · 进化：怎么让改造有方向、有多样性、可回滚

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 单一改造方案容易失衡、陷入局部最优 | 规划师一次开 **3 张不同侧重方案**（I₁ 成本优先 / I₂ 平衡 / I₃ 性能优先） | 保留多样性，暴露整条帕累托前沿而非单点 |
| 各方案优劣不可比（多目标） | 帕累托劣势淘汰（花钱更多、分还更低的废案）+ **归一化加权平方距离**准则选拔 Lite/Medium/Heavy 三档代表 | 多目标（性能 vs 成本）下的可比性；一次生成三档让用户按预算选 |
| Harness 改坏无法回滚 | 编辑器在**独立 workspace** 改代码 + **自动 Git 提交** | 追溯性、可回滚 |
| 各 Agent 之间信息不通 | 规划师用 **Diff 工具**对比当前候选池里不同 Harness 的代码差异 | 借鉴别人的好机制，避免重复发明 |

**B 层原则一句话（我的分析）**：从"单点最优"到"暴露整条前沿"是 framing 层的结构性改动——帕累托筛选不依赖具体底座/基准，是多目标优化的标准结构。这一层是 HarnessPro 相对 RHO 等前辈最本质的区别。

### C 层 · 运行时：Agent 自进化出的省钱组合拳（heuristic 生成机制）

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 探索停不下来（"雷霆大思考"） | Runtime Hooks：Terminal-Bench 2 Medium 下，工具调用 **14 次**塞提醒（"进入经济阶段 Economy phase，请合并检查，停止复读机行为"）/ **26 次**升级警告（"进入收敛阶段 Convergence phase，立刻停止广泛探索，专注收尾验证"）/ **44 次**直接 Block 拦截（"工具预算已耗尽！保留当前文件，立刻根据现有证据交卷"） | 硬性预算约束；阈值来自具体观察 |
| 提醒消息破坏 Prompt 前缀缓存 | 把提醒**拼在工具返回结果的末尾** | 保护 Cache Reuse，把省钱细节抠到极致 |
| 上下文/推理强度一刀切 | 动态路由：先看一眼任务描述，从 **compact / lean / standard / deep / research 五档**配置单里挑一个最匹配的，动态分配 Reasoning Effort 和工具调用预算 | 按任务复杂度分配，避免"杀鸡用牛刀" |
| 命令行经常吐出几万行冗长日志 | 自动引入类似 **RTK (Rust Token Killer)** 的工具输出压缩机制：连续重复的报错或编译日志折叠成 `[previous line repeated N more times]`，超长输出截断只留头尾关键信息 | 减少无效 token 消耗 |

**C 层原则一句话（我的分析）**：这一层全部是 heuristic patches——阈值（14/26/44）、档位（五档）、折叠规则、拼接位置，都是看到具体浪费模式后打的补丁，换底座/换基准大概率要重标。源文的消融实验恰好佐证：**单独把动态路由或预算钩子给 RHO，能省钱但通过率明显掉点**——patches 互相咬合、不可拆分，只有组合起来才 work，这正是 heuristic 优化的典型特征。

## 五、标杆案例：251 万 token 的邮件服务器任务（源文 + 我的流水线映射）

源文附录给了一个真实案例，但只展示了诊断师那一段。这里基于源文事实把整条流水线映射上去，**映射部分是我的推断，非源文**，用来让抽象咬合落到具体。

**源文事实**：AI 虽然配好了邮件服务器，但诊断师一眼看出它在无关的配置文件上反复倾倒日志，导致单次任务狂吞了 **251 万个输入 Token**。

**流水线映射（我的推断，非源文）**：

1. **轨迹诊断师**：同时调取 3 次 rollouts 的完整轨迹，发现共性浪费——"在无关配置文件上反复倾倒日志"。这一步是源文事实。
2. **进化规划师**：拿到诊断报告 + 成本指标（251 万 token 是异常值），用 Diff 工具对比候选池，看其他 Harness 有没有处理日志的机制可借鉴；然后开 3 张方案——I₁（成本优先）可能直接引入日志折叠；I₂（平衡）可能折叠 + 动态路由降档；I₃（性能优先）可能只折叠不降档。
3. **代码编辑器**：在独立 workspace 改 Harness 代码——引入类似 RTK 的折叠机制（`[previous line repeated N more times]`）、可能加 Runtime Hooks 在工具调用 N 次后提醒"停止复读机行为"、可能把任务路由到 compact/lean 档。自动 Git 提交。
4. **测试合成器**：根据"配邮件服务器"这个任务描述，写 10 个 unittest——比如"能否发送邮件"、"配置文件是否正确"、"日志是否包含关键事件"等。新 Harness 跑这 10 个 test，通过才算候选合格。
5. **帕累托筛选**：新 Harness 的（通过率, 成本）二元组进入候选池，淘汰帕累托劣势者，按归一化加权平方距离选入 Lite/Medium/Heavy 三档之一，送入下一轮。

**这个案例展示的关键（我的分析）**：诊断师抓到的"251 万 token"不是抽象的"成本高"，是**具体的浪费模式**（在无关配置文件上反复倾倒日志）。规划师出的方案也不是抽象的"降低成本"，是**针对这个具体模式的补丁**（日志折叠 + 可能的 Hooks + 可能的降档）。这正是 heuristic 优化的本质——**基于当下测试出来的问题来提出改造手段**，而不是从第一性原理推导。

## 六、效果（源文逐字数字）

**测试底座**：GPT-5.5 + Codex、GLM-5.2 + Claude Code（智谱自家）。

**三大基准**：Terminal-Bench 2（终端操作）、SWE-Bench Pro（仓库级代码修复）、ProgramBench（从零重构程序）。

**核心数字**：

| 配置 | 基准 | 通过率 | 成本 | 对比 |
|---|---|---|---|---|
| **HarnessPro-Medium** | SWE-Bench Pro | **79.0%** | **$1.26**/任务 | vs RHO 80.0% / $2.68，成本 **-53.0%** |
| **HarnessPro-Heavy** | Terminal-Bench 2 | **80.8%** | — | vs RHO **+4.5 pp**，成本 **-33.9%** |
| **HarnessPro-Lite** | 三大基准 | 全线超越 Vanilla | 节省 **17.7%–57.4%** | — |
| **RHO**（前辈 SOTA） | SWE-Bench Pro | — | $1.88 → **$2.68** | 成本 **+42.6%** |

**附带效果（源文）**：论文没把时间延迟作为优化目标，但由于砍掉了大量废话和无效探索，在 SWE-Bench Pro 上 Heavy 模式平均任务耗时 **520s → 412s**。

**消融实验（源文）**：单独把动态路由或预算钩子给 RHO，能省钱但通过率明显掉点。**只有依靠 HarnessPro 的多智能体多轮递归进化，让各个机制产生协同效应（Synergy），才能真正把"性能-成本"的帕累托前沿往前推。**

**GLM-5.2 + Claude Code 上的复现（源文）**：同样的碾压态势在智谱自家底座上也得到了完美复现。

## 七、收束：commoditized 通用件 vs 不可复制的壁垒

### 可复制的通用件（结构性 framing，已被摊开的方法学）

- **帕累托多目标筛选 + Lite/Medium/Heavy 三档前沿**——把 RSI 从单点最优改成多目标前沿生成，这个 framing 不依赖具体底座/基准，可直接抄。
- **测试合成器代替 LLM 裁判**——无标签环境下用合成 unittest 做判据，召回率 41.7%→83.3% 的提升是判据形态替换的直接效果，跨域成立。
- **四 Agent 流水线（诊断-规划-编辑-测试）+ 3-rollouts 稳定性诊断**——分工骨架，是"什么信息进什么 Agent"的架构规定。
- **Runtime Hooks 分段预算 + 动态路由 + 日志折叠的"组合拳"思路**——具体阈值要重标，但"用硬性预算约束 + 按任务分配推理强度 + 压缩无效输出"这个组合方向是通用件。

### Heuristic 生成机制（换域要重标的经验性补丁）

- **14/26/44 的 Hook 阈值**——来自 Terminal-Bench 2 Medium 模式的观察，换底座/换基准大概率要重标。
- **compact/lean/standard/deep/research 五档的划分与匹配规则**——是看到"一刀切"浪费后打的补丁。
- **`[previous line repeated N more times]` 的折叠规则与头尾截断策略**——类似 RTK，是应对命令行冗长日志的经验性方案。
- **Hooks 拼在工具返回结果末尾**——是"发现提醒消息会破 cache"后的巧妙工程细节，依赖具体 Prompt 缓存机制。

### 不可复制的壁垒（收在这）

- **能自动出好补丁的 LLM 底座本身**——mutation operator 的质量决定了整套系统的天花板。源文用了 GPT-5.5 + Codex 和 GLM-5.2 + Claude Code 两套底座，智谱自家 GLM 的协同复现能力是壁垒之一。
- **3-rollouts 训练集的算力沉淀**——每候选跑 3 次的算力成本是"已付费的证据"。
- **帕累托选拔的具体准则参数**（归一化加权平方距离的权重设定）——这些是在具体底座+基准上标定出来的。
- **与 Git/Workspace 基建的深度集成**——编辑器的独立 workspace + 自动 Git 提交，依赖具体工程基建。

**与集群收束的同构（我的分析）**：这个"方法即通用件、mutation operator 才是壁垒"的收束，与 `notes/reading/kuaishou-conan-stability-agent-notes.md` "方法即通用件、Context 才是壁垒"同一把尺子，也与 `notes/reading/self-developing-agents-closed-loop-rsi-notes.md` §6.5 "壁垒是已付费的证据"同构——**算法/方法论是通用件，能持续产出好补丁的底座 + 已累积的算力/数据/基建才是护城河**。

### 迁移到其他域的通用启示（我的分析）

**任何"越优化越贵"的自动化闭环（不止 Agent），帕累托前沿 + 一次生成多档方案是可以借的通用模式**——从单点最优改成暴露整条前沿，让用户按预算选档位，这个 framing 跨域成立。

**测试合成器代替 LLM 裁判也是无标签评估的通用解法**——当没有官方测试用例时，用 LLM 根据任务描述合成可执行 unittest，比让 LLM 自评更可靠（召回率 41.7%→83.3% 是直接证据）。这条与 `notes/reading/airbnb-eval-driven-development-notes.md` "把'什么叫好'编译成可执行工件"同一思路。

**但要警惕 heuristic patches 的不可拆分性**——源文消融实验证明单独抽一个 patch 会掉点，说明这些补丁互相咬合、只有组合起来才 work。换域时不能只抄一个机制，要整套重标。

## 延伸阅读（本仓，均已读目标文件确认接口点，非凭标题猜）

- `notes/reading/rsi-2026-landscape-harness-l1-ignition-l2-notes.md` — 地图综述层。§3.2 已把 HarnessPro 挂在"其它大厂入场：清华/Zhipu HarnessPro（2610.26770，label-free Pareto）"的位置；按那篇的 L0–L3 尺子，HarnessPro 是**冻结权重改外壳的 L0 机制提案**，还没有一手 L2 点火证据。本篇是那篇地图里一个具体坐标的展开。（对照是我的分析）
- `notes/reading/rrsi-regularized-harness-self-improvement-notes.md` — 同族但方向正交。RRSI 处理"自进化会过拟合"（Proposal 端控复杂度 + Selection 端 noise-adjusted floor / cost gate / pruning），HarnessPro 处理"越进化越贵"（帕累托多目标 + 测试合成器）。两者都在 harness 层做文章，但 RRSI 关心"该保留什么"，HarnessPro 关心"怎么同时推进性能和成本"。RRSI §3.2 提到的 Google Harness²（2610.14224，同一组人）是 RRSI 的直接续集，与 HarnessPro 平行。（对照是我的分析）
- `notes/reading/sift-self-improvement-fast-tree-search-notes.md` — 评估层的另一条路线。SIFT 让 judge 便宜（成对比较 + BT 排序，把评估做成"排序信号"），HarnessPro 让 judge 变成可执行 unittest（测试合成器）。两者都在处理"评估太贵"，但 SIFT 走"便宜排序"，HarnessPro 走"可执行判据"。SIFT §二"评估函数就是主要成本"的域背景论证直接适用于本篇。（对照是我的分析）
- `notes/reading/self-developing-agents-closed-loop-rsi-notes.md` — 审计层。那篇的三处漏水（TARGET/EXPERIENCE/SYSTEM）里，HarnessPro 主要补 **SYSTEM 层**（harness 怎么改、怎么筛），测试合成器部分沾到 **EXPERIENCE 层**的判据问题（用可执行 unittest 代替 LLM 自评——S³Gym 的 ρ≈0 就是 LLM 自评失败的量化证据）。但 HarnessPro **没有触及 TARGET 层**（模糊目标怎么变成具体行动）。审计层 §6.5 "壁垒是已付费的证据"与本篇 §七收束同构。（对照是我的分析）
- `notes/reading/airbnb-eval-driven-development-notes.md` — "把'什么叫好'编译成可执行工件"的产品化版本。Airbnb 编译成 rubric + golden set + VJ，HarnessPro 编译成 unittest——同一思路在 RSI 域的具体实现。Airbnb 的 VJ 校准到高80s-90s% agreement，与 HarnessPro 测试合成器把召回率从 41.7% 拉到 83.3% 是同一类"判据形态替换"的直接效果。（对照是我的分析）
- `notes/reading/kuaishou-conan-stability-agent-notes.md` — "方法即通用件、Context 才是壁垒"这个收束框架的出处，与本篇 §七"能自动出好补丁的 LLM 底座才是壁垒"同一把尺子。（对照是我的分析）

本仓已发布文章（公开链接，均已读目标确认相关）：

- 《[The Search Pathology: Why Scaling Test-Time Compute Can Degrade Code Agent Quality](https://cj9208.github.io/blog/ai_study/search-pathology-test-time-compute/)》— 那篇讲"在 imperfect proxy 上 scale test-time compute → over-engineering"；HarnessPro 的 Runtime Hooks（14/26/44 次分段提醒→拦截）正是对"探索停不下来"的硬性预算约束，是同一问题在 harness 层的解法。（对照是我的分析）
- 《[Harness Engineering 合集](https://cj9208.github.io/blog/ai_study/harness-engineering/)》— 定义了什么是 Agent Harness、为什么它是可靠性的关键层。HarnessPro 操作的正是这一层。（对照是我的分析）
