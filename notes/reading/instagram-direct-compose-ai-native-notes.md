# 把最省力的路修成正确的路：Instagram Direct 的 AI-native 架构迁移，与"33% token 到底省在哪一阶段"

> 源文：《How Instagram Direct engineers built AI-native UI architecture with Jetpack Compose and reduced token cost per agent session by 33%》，Android Developers Blog，2026-09-30。作者 Pavlo Stavytskyi（Software Engineer, Meta）、Rebecca Franks（Developer Relations Engineer, Google）。原文：<https://android-developers.googleblog.com/2026/09/jetpack-compose-ai-native-ui-instagram-direct.html>
> 这是一篇读后梳理，不是翻译。主线一句话：**AI agent 永远走阻力最小路径，所以架构质量的定义变了——不再是"好代码容易写"，而是"正确代码是最省力的那种、错误代码难以表达"；而衡量它的仪表，恰好是 agent 自己留下的 token 日志。**
> 标注约定：§三–§五 的困难、方案、代码模式、全部数字与 API 版本均为**源文原样**。§二（域背景）、§六（两阶段拆账）、§七（延伸洞见）整节是**我的分析，非源文**，已就地标注，不要当源文事实引用。§六是本篇笔记相对源文的主要增量。

## 一、一句话主线

源文表面在讲一次 View → Compose 的 UI 迁移，实际主张的是另一件事：**不要把 AI 工具指向现有代码（retrofit），而要重新设计代码库让它 AI-native by design**，理由是这种做法对 AI 效果的放大远超事后修补。

选 Compose 的动机也随之变了。不是"声明式更现代"，而是它副作用更少、隐式状态更少、组件边界更清晰，模型更容易推理。文章把这个动机落成两条可操作规则（源文）：

1. **最小化对自定义上下文的依赖**——AI 需要越多代码库专属知识才能改对，产出质量就越低；代码库越接近公认最佳实践，AI 结果越好。
2. **AI-first 代码库必须自我强制边界**——用 skill 补设计缺口不 scale，因为每个进 context 的 skill 都花 token 且会拉低 agent 表现；约束应由架构本身承载。

第 2 条的理由是全文最锋利的一句（源文）：**guardrails 和 skills 有帮助，但本身不够，因为 AI 遇到摩擦时往往会绕开它们来解锁自己**（"when AI hits friction it will often route around them to unblock itself"）。所以设计要让阻力最小的那条路正好通向正确代码，同时让糟糕的设计**难以表达、代价高昂**。

## 二、域背景：为什么这个 surface 特别难（我的分析，非源文）

源文给了规模数据，但没解释这些数字为什么构成困难。这一节是我的领域推理，用来交代后面困难集从哪来。

**规模（源文数据）**：每天数十亿条消息，数亿人发消息；单个 UI 组件可能有 **160 多种状态排列**；仅一个会话界面就要处理 **200 多种消息类型**。

**为什么"零扰动"是真约束而不是修辞（我的分析）**：消息是 Instagram 的核心 surface，且高频、常在会话早期被访问。这意味着任何回退都是全量用户立即可感的，没有"小众功能先试错"的空间。所以迁移必须能在生产环境按小批量独立灰度、随时用 feature flag 切回——**A/B 基建不是锦上添花，是迁移得以启动的前提**。这也解释了为什么后面所有方案都长成"两套并行 + 运行时可切换"的形状。

**为什么性能基线几乎不可能超过（我的分析）**：legacy View 实现经过多年微优化，已经贴近这套 UI 范式的能力上限。迁移方不是要跟一个平庸基线比，而是要跟一个被专门团队压榨多年的基线打平。这类迁移的典型失败模式不是"新框架更慢"，而是"新框架的理论上限更高，但你吃不到，因为要吃到的前提是整个 surface 端到端迁完"——源文后面正是这么说的（小规模试点的假阴性问题见 §三性能层）。

**为什么 AI 让这件事的性质变了（我的分析）**：在 AI 之前，"代码库好不好改"靠人的手感衡量——新人多久上手、老人改一个功能要碰几个文件。这些指标无法量化，因为没人记录人类工程师往脑子里加载了多少上下文。AI agent 进场后，同一件事突然有了自动日志。这个变化是本篇笔记 §七 的落点。

## 三、困难 ↔ 方案 咬合（核心，按三层）

### 架构表达层：解决"范式混合让 AI 走捷径走出 bug"

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 把 Compose 组件嵌进现有 View 层级是增量迁移的合理做法，但长期混用声明式与命令式代码，**AI 会走阻力最小路径把两者错误糅合**，引入隐蔽 bug、技术债与性能回退（源文） | 不靠规范文档约束，而是**改造抽象本身**，让 Compose 代码在语言层面拿不到命令式状态 | AI 的捷径是由"什么可表达"决定的；改文档不改可表达空间，等于没改 |
| 老式 `RecyclerViewItem` + `onBind`：feature flag 在命令式代码读取后又被 Compose lambda 捕获，形成跨范式耦合（源文 Example 1） | 见下 Example 3 | 耦合点在于命令式上下文对声明式代码可见 |
| `var isPinned` 挂在 item 对象上而非 `ChatUiState` 中，于是它**熬过 RecyclerView 的 re-binding 与回收，在多行之间泄漏**，产生极难复现的 bug（源文 Example 1） | 状态一律读 `uiState`，变更走 `onPin(...)` 回调 | item 对象的生命周期与行的生命周期不一致，可变字段必然串味 |
| 即使清理成给 item 一个专属 `@Composable` 函数（源文 Example 2），**同样的问题原样存在** | 同上 | 只要类成员对 Compose 代码可见且可变，换个写法不解决可见性 |
| 需要保留既有架构的抽象形式（list item 仍要有自己的类），又要切断上述可见性 | **把所有 Compose 代码放进 `ComposeItem` 的构造函数参数** `content = { uiState -> ... }`（源文 Example 3） | 这段代码因此无法访问类成员或类状态，唯一入参来源就是构造函数，**等价于一个纯 `@Composable` 函数**，同时符合既有架构 |

原则（源文）：**给 AI 的边界越少，它长期产出的代码质量越低。** Example 3 是"让错误设计难以表达"的字面实现——不是禁止，是让那个错误在这个位置根本写不出来。

### 迁移工程层：解决"数百组件与 legacy 长期并行，还不能停下来"

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 数百个 UI 组件必须与 legacy 版本长期并存、两套并行维护 | **多名工程师各跑自己的 AI agent，共享一个迁移过程中沉淀的可复用 skills 与 conventions 知识库** | 让工作流和最佳实践在团队内保持同步，而不是每人重新发现一遍 |
| 迁移要快，又不能打断其余工程师日常发功能 | **每个界面拆两阶段**：① 用 AI 把所有 Compose 代码写出来；② 打磨——处理边界情况、补性能缺口——直到灰度给真实用户 | 让一个工程师快速扫完整个 surface，先把架构和棘手边界定下来；随后其他人只需专注推到生产可用，不必自己停下来做技术决策 |
| 所有 item 迁完后，核心架构仍重度依赖 legacy View（RecyclerView） | 下一步换核心：**RecyclerView → LazyColumn**；Compose item 与所处框架解耦，**同时兼容两者，并能通过 feature flag 运行时切换** | 只有运行时可切，两套方案才能并行 A/B，才能在不打断其他人的前提下打磨性能 |
| 原生适配 LazyColumn 的 Compose item 塞不进 RecyclerView | **专门写一个 interop API** 把它们反向插进 RecyclerView | 复用同一批 Compose item，让 LazyColumn 版本能与 RecyclerView 版本并排灰度 |

### 性能层：解决"基线极高，而小规模试点会骗人"

| 困难 | 方案 | 为什么这么解 |
|---|---|---|
| 三个必须打平的指标（源文）：**time to interact**（打开到可交互）、**time to fully load**（打开到含图片全部加载）、**scroll performance**（无掉帧）；均在线上运行时追踪以支持 A/B | 整块 surface 端到端迁移，而非零散组件 | 见下一行——小规模试点的读数不可外推 |
| **从小处着手会给出假阴性**（源文），两个原因：① 不具代表性——不同组件行为差异出于无法泛化的原因；② **interop 成本**——小 Compose 片段待在大 View 代码库里要付不可预测的桥接开销，扭曲测量 | 迁得越端到端、桥接中断越少，性能画面才越真实 | 这条直接推出 §七 的经验："aim to migrate bigger surfaces over individual small components" |
| 昂贵的懒列表项单趟组合会超帧预算，造成滚动卡顿 | **Pausable composition**（Compose 1.10 默认开启）：跨帧增量组合 | 把一次大开销摊到多帧 |
| 快速滑动时离屏内容来不及准备 | **LazyLayoutCacheWindow**（Compose 1.9 引入）：在视口周围按像素保留已组合的离屏项 | 用内存换滑动的连续性 |
| 大规模 Compose surface 需要一致地知道某个 composable 是否真的显示在屏幕上，过去各家手写 | **`onVisibilityChanged`**（Compose 1.9.0），支撑曝光相关的产品质量指标 | 仅 Instagram Direct 内部就有数百个文件依赖它 |
| Compose runtime 有一次性预热成本，影响首启 | **Baseline Profiles** 在安装期预编译热路径 | 首启即快；且因消息是高频早期 surface，预热只付一次，**其他用 Compose 的界面跟着变快**（源文称这是意外收益） |

### 边界与代价（我的分析，非源文）

源文没有"还没解掉"的自认清单，但有两处代价值得记下：一是 interop API 本身是纯迁移期资产，LazyColumn 全量后就该删，源文没说是否已清理；二是"两阶段流程"把架构决策权集中在第一阶段那个人身上，这对那个人的判断力要求很高，源文把它当纯优点讲，但它同时是单点。

## 四、标杆案例：`ChatItem` 的三段演进（源文代码，逐段走一遍）

这是全文唯一的 worked case，正好把"边界如何一步步收窄"落到具体代码上。

**Example 1 — 老写法**：`ChatItem : RecyclerViewItem<ComposeViewHolder, ChatUiState>`，`onBind` 里读 `features.isEnabled("pinned_chats_feature")`，再在 `holder.composeView.setContent { }` 里用；同时类上有 `var isPinned: Boolean = false`，按钮 `onClick = { isPinned = !isPinned }`。两处病灶：flag 在命令式上下文读取后被 Compose lambda 捕获（跨范式耦合）；`isPinned` 是 item 上的可变字段而非 `ChatUiState` 的一部分，因此熬过 re-binding 与回收、在多行间泄漏。源文注释直言这类 bug "unexpected, hard-to-reproduce"。

**Example 2 — 第一次清理**：改成 `ComposeRecyclerViewItem<ChatUiState>`，给它一个 `@Composable override fun Content(uiState: ChatUiState)`。看起来干净了，但 `val isPinnedChatsEnabled` 和 `var isPinned` 仍是类成员，`Content` 里照样直接读写。**源文结论：同样的问题原样存在。** 换写法没有改变可见性。

**Example 3 — 真正的解法**：`ChatItem(val features: FeatureFlagProvider, val onPin: (Boolean) -> Unit) : ComposeItem<ChatUiState>(content = { uiState: ChatUiState -> ... })`。所有 Compose 代码作为构造函数参数传入，因此：① 它拿不到类成员，也拿不到类状态；② 唯一入参来源是构造函数；③ 开关判断移进 lambda 内部（`val isPinnedChatsEnabled = features.isEnabled(...)` 通过构造参数闭包捕获，而非类字段）；④ 状态读 `uiState.isPinned`，变更调 `onPin(!uiState.isPinned)`。源文说这使它"等价于一个纯 `@Composable` 函数，同时符合既有架构"。

从 1 到 3，改动量很小，但**性质变了**：Example 2 靠纪律（记得别用类字段），Example 3 靠作用域（用不到类字段）。前者 AI 会绕开，后者绕不开。

## 五、效果（源文数字，逐字）

**代码量**：迁移后的 Instagram Direct surface，总 UI 代码减少 **50%**。源文的因果表述是"要生成的代码更少，与产出质量更高、单任务 token 成本更低相关联"。

**AI 效率，分两个口径报告**（源文明确解释为何两个都要给）：

- **按落地代码每字符计**：相比 Android Views，Compose 少 **32%** 的工程师-agent 交互轮次，少 **35%** 的 agent 执行时间（定义为"从 agent 开始处理工程师的请求到返回结果的耗时"）。这组衡量的是**单位产出的资源消耗**。
- **按 agent session 计**：整体 token 成本下降 **33%**。这组衡量的是**一次典型 session 的总成本**。

**衰减斜率**（源文，全文最有分析价值的一组）：Meta 用一个 risk score 追踪代码变更的整体质量与引发线上事故的概率；agent 资源效率是 token 消耗、执行时间、工程师交互次数的复合指标。当文件的累计 risk score **翻倍**时：

- Android Views 实现的 agent 资源效率（按落地字符计）下降 **30%**
- Jetpack Compose 实现的下降 **9%**

**滚动性能**（源文，Meta 内部测试，基线为 vanilla Compose，指标 LFDs/m = 每分钟明显卡顿次数，Meta 内部指标）：Pausable composition 配一个视口大小的 LazyLayoutCacheWindow，LFDs/m 降低约 **13%**；仅用 cache window 降低约 **8%**。

配置写法（源文，需 Compose 1.13.0-alpha03）：`LazyLayoutCacheWindow(ahead = 150.dp, behind = 100.dp)` 是固定绝对长度；`LazyLayoutCacheWindow(aheadFraction = 0.5f, behindFraction = 0.3f)` 是视口比例，绝对量随屏幕高度缩放（平板/折叠屏展开时留更多）。Instagram 团队针对 Direct 的内容结构与 item 尺寸专门调了 float 比例，源文强调最优值取决于具体 UI 参数，需要实验。

## 六、两阶段拆账：标题那个 33% 属于第二阶段（我的分析，非源文）

这是本篇笔记相对源文的主要增量。源文把两件事混在一个叙事里，账本因此只有一半。

### 6.1 两个问题，不是一个

- **第一阶段：一次性迁移项目。** 验收标准是功能一致 + 性能不退化。源文这部分用的确实是性能指标——time to interact / time to fully load / scroll performance，配 A/B，加上 pausable composition 与 cache window 的 LFDs/m 收益。这部分跟 AI 没关系，就是传统迁移验收。
- **第二阶段：之后的日常迭代。** token 成本、agent 执行时间、工程师-agent 交互轮次这组指标衡量的是它。它测的不是 app 跑得快不快，而是**改这个代码库贵不贵**——工程生产系统自身的性能。

**标题的 33% 完全属于第二阶段。** 证据在测量方式里：源文说的是拿"跑在 Compose UI 上的 AI agent session"与"同样任务跑在 Android Views 上的"做对比——这是同一时期的**截面比较**，不是迁移前后的纵向比较。更能说明问题的是 risk score 那组，它明确讲"文件累计风险分翻倍时"的效率衰减，而累计风险只有被反复修改的老文件才会有。这已经完全是稳态开发期的现象。

### 6.2 缺的是 capex 那一栏

按两阶段摆开，源文只给了运营支出（opex）的收益：

| | 内容 | 源文是否给了数字 |
|---|---|---|
| **capex（第一阶段投入）** | 重写数百组件；与 legacy 版本长期并行维护两套；建共享 skills/conventions 知识库；做 Example 3 那种架构设计；搭 A/B 基建；写 RecyclerView↔LazyColumn 的 interop API；与 Google 结对推进 Compose 上游改动 | **一个都没有** |
| **opex（第二阶段收益）** | 每次改动省 33% token、35% 时间、32% 轮次；代码少 50% | 给了 |

诚实的问法不是"整个迁移花了多少"，而是**"按 AI-native 方式做"减去"按常规方式做"的差额**——因为迁移反正要做（技术债、声明式趋势、AI 助手已经进场），差额才是真正的决策变量。这个差额源文也没给。

它只暗示了一个有意思的方向：AI workflows "helped make this parallel migration possible by speeding up the process of writing massive amounts of code"，让团队"in record time"完成迁移且不打断其他人。**也就是说 AI 反过来资助了一部分自己的建设成本。** 这条如果能量化，比 33% 有说服力得多，因为它直接回答"为什么现在做"。

### 6.3 第二阶段内部还得再切一刀：体量效应 vs 衰减速率效应

"新架构更好所以 token 更少"混了两个机制：

- **体量效应**：代码少 50% → 要生成的少 → token 少。这近乎恒等式，是**一次性的水平位移，不会复利**。
- **衰减速率效应**：risk score 翻倍时 Views 掉 30%、Compose 只掉 9%。这个**随时间和修改次数复利**。

对一个有 200+ 消息类型、单组件 160+ 状态排列、且要连续迭代多年的 surface 来说，几乎全部价值在后者。而源文把它压在一个段落里，把恒等式的那半放在了标题。

由此可以推出一条源文没写的**决策规则**：如果驱动因素是衰减速率而非体量，那么**迁移优先级应该按未来的变更频率排，而不是按当前的性能痛点或代码规模排**。这跟常规迁移的排序逻辑完全不同——常规逻辑会先迁最烂或最慢的，而衰减速率逻辑会先迁最常改的。一个又烂又没人动的模块，迁过去省不了多少 token。

### 6.4 归因有个循环

"我们用 AI 写 Compose 代码，然后测出 Compose 的 AI 效率高"——但迁移期间团队专门建了共享 skills/conventions 知识库、采用两阶段流程、还做了 Example 3 那种针对性的架构改造。**这些都是额外投入，不是 Compose 自带的。**

关键问题：对照组（同样任务用 Android Views）是否配了同等强度的 skills 库、同等认真的架构改造？源文没说。如果 Views 组是"原样代码丢给 AI"，那 33% 里有多少来自 Compose、多少来自"专门为 AI 重新设计过架构"，就分不开。

源文自己露了一句：他们做的是 *redesigned the codebase and its architecture to be AI-native by design*。**起作用的可能主要是后半句**，Compose 只是让这种设计更容易表达的载体。Example 3 的本质是收窄作用域——这个手法在 View 体系里理论上也能实现，只是别扭得多（没有 `@Composable` lambda 这种天然的构造函数参数位）。

所以我会这样读这篇文章：**结论是硬的，归因是软的。** 硬的那半是"架构应该让正确路径成为最省力的路径，而不是靠 skill 和 guardrail 去堵"；软的那半是"所以要上 Compose"。

### 6.5 口径：优先信 per-character 那组

token 的 33% 是 **per agent session**，而 session 不是等量的工作单元。源文一处说比较的是"同样任务"（the same tasks），另一处说比的是"一次典型 agent session 的总成本"（total cost for a typical agent session）——**两者之间有滑动**：前者是配对样本，后者是典型样本，不是同一个统计对象。

相比之下，per character of landed code 那两个数字（32% / 35%）做了产出归一化，口径更硬。我会优先信这组，把 33% 当参考值。

## 七、延伸洞见：AI agent 是架构质量的测量仪表（我的分析，非源文）

顺着 §6.3 往上抽一层，我认为这个案例最有价值的地方不在省 token，而在于它示范了一种新的测量能力。

传统上衡量架构好坏用"新人多久能上手"、"改一个功能要碰几个文件"、"bug 有多难复现"。这些都极难量化，**因为没人会记录人类工程师改一个功能时往脑子里加载了多少上下文**——那个成本发生在 skull 内部，不留日志。

AI agent 把这件事外化了：每次改动自动留下 token、轮次、耗时的完整记录。同一个概念突然有了便宜、连续、大样本的测法。Meta 那个 risk score × agent 资源效率的分析，本质上就是**用 agent 的消耗曲线给"代码腐烂"画了一条可测的斜率**——过去"这个文件越来越难改"只能靠老人的抱怨，现在它是一个有单位的数。

这条还有一个组织层面的含义（我的分析）：agent 日志天然带归属——每个 session 都挂在发起它的那个具体工程师身上，无法推给"能力建设"这类无人担责的名词。这意味着它比大多数自报式工程指标更难被玩坏。

顺带修正我自己之前的一个说法：我原以为这条符合《无主名词与真实指标》里的判据，读了原文后发现那篇的判据是"**有没有一个具体的人其考核承担它的失败**"，不是"是否为行为副产品"。两者不是一回事。准确的连接是上面这句——agent 指标恰好**同时**满足"自动产生"和"天然带 owner"，这是它比人工填报指标更硬的原因，但不是同一篇里的同一条判据。

## 八、收束：方法即通用件，测量仪器与上游议价权才是壁垒

**可复制的通用件**（源文给出的方法，任何 Android 团队都能照搬，且大半是 Google 官方 API）：

1. 两条规则——最小化自定义上下文依赖 / 架构自我强制边界。
2. Example 3 的手法——把 UI 代码放进构造函数 lambda 以切断对外层类状态的访问。本质就是收窄作用域，不限于 Compose。
3. 两阶段迁移流程 + 共享 skills/conventions 知识库。
4. 整块 surface 迁移优于零散组件（避开 interop 成本造成的假阴性）。
5. Pausable composition 与 LazyLayoutCacheWindow **配对使用**——源文明确说只用 cache window 时，重 item 仍可能试图单趟组合完，超出帧预算。
6. Baseline Profiles 处理首启预热。

**不可复制的壁垒**：

- **测量仪器**：数百上千个线上性能指标的 A/B 能力、risk score、agent 资源效率复合指标、LFDs/m。没有这套东西，"架构让 AI 更高效"只能停在体感和 PPT 上——你连 30% vs 9% 这种斜率都算不出来。
- **上游议价权**：Pausable composition、LazyLayoutCacheWindow、`onVisibilityChanged` 三项能力都是这次 Meta–Google 合作的产物。源文最后一条经验直接写"Contribute to Compose itself"，并点名致谢双方的工程师。**能把自己的性能需求推进框架上游，是供应链位置，不是方法论。**
- **组织习惯**：数百工程师共用并持续沉淀同一套 skills/conventions；以及能把一个界面拆成"一人定架构与边界、其余人推生产"的分工信任。
- **现金流**：两套实现长期并行维护的 capex 极重。这一条源文没提，但对照《编码向左，工程向右》附注里那句"如果你没有 Google 的命，却得了 Google 的病"——Meta 同样有能承受这种浪费的印钞机。普通团队照搬"并行双轨 + 整块迁移"可能先被 capex 压死。

**所以真正值得盯的不是那三条百分比，而是那道磨人的坎**：方法论（让正确路径成为最省力的路径）几句话说得完，难的是①有仪器把它测出来、②有位置把缺的能力推进上游、③有组织纪律日复一日维护那套 skills 与 conventions。这跟快手柯南那篇的落点是同一个结论的不同投影——那边说"Context 才是真正的壁垒，也是享受模型升级红利的前提"，这边说的是**能把 Context 的效果测出来并持续调的那套装置才是壁垒**。方法论早就熟了。

**迁移到其他域的通用启示**：在引入 AI 编码时，先别问"哪个框架对 AI 更友好"，先问"我的架构里，阻力最小的那条路通向哪里"。如果通向错误代码，加多少 skill 和 review 都是在堵，而 AI 会绕。把可表达空间本身改掉，比写规范便宜。

---

延伸阅读（本仓，均已读正文确认相关）：

- 《[AI Coding 的防御性进化：平台化、业务解耦与结构的自然生长](https://cj9208.github.io/blog/ai_study/ai-coding-evolution/)》——**本篇最直接的上游论点，且有一处真实分歧值得记下**。它的"Token 泄露症候群（Context Bleeding）"给出了 33% 的机制解释（AI 为修一个跨模块 bug 会把数十个文件塞进上下文，形成乘法效应）；"人类恐惧重复，但 AI 恐惧耦合"与 Instagram 的选择同构。**分歧在边界的实现层级**：那篇主张在 `agent.md` 里声明 `src/platform/` 绝对只读——这是**指令级软边界**；而 Instagram 明确说 guardrails/skills 不够，因为 AI 遇摩擦会绕开，Example 3 用的是**语言级硬边界**（代码根本访问不到类成员）。Instagram 的案例可以读成对那篇的一个 refinement：软边界拦得住守规矩的 agent，硬边界才拦得住走捷径的 agent。
- 《[破除"单测无用论"：代码不可测，是架构烂，不是单测错](https://cj9208.github.io/blog/ai_era_engineering_careers/unit-testing-testable-architecture/)》——结构完全平行的姊妹命题："代码不可测，人写容易出 Bug；架构不解耦，AI 写必定会崩溃"。它那句"把'AI 输出是否破坏系统不变量'从不可验证的信任问题，转变成可自动执行的机械问题"，正是 Example 2 → Example 3 那一步在做的事：从靠纪律变成靠作用域。
- 《[编码向左，工程向右：AI 时代程序员的生存突围](https://cj9208.github.io/blog/ai_era_engineering_careers/coding-left-engineering-right-ai-survival/)》附注 1——**反面案例**。Google Monorepo 里 AI"为了追求局部最优绝不重复造轮子"，跨部门精准 import 三年前的底层函数，"在文本层面消灭了重复代码，却在拓扑层面织出极度耦合的超级大面条网"，爆炸半径指数扩散。这与 Example 1 里 `var isPinned` 跨行泄漏是同一个失效模式的不同尺度：AI 的最小阻力路径在没有物理边界时必然通向耦合。
- 《[重力回归：企业 ROI 约束与 AI"确定性账单"的控盘人](https://cj9208.github.io/blog/ai_era_engineering_careers/gravity-roi-ai-deterministic-billing/)》——§六 capex/opex 拆账的企业侧对照。那篇讲"无产出即消耗"的财务黑洞（盲目重试把算力预算火化掉），Instagram 的 risk score × agent 效率曲线可以理解成给这类账单装了一个可预测函数：代码老化到什么程度，AI 账单涨多少。
- 《[无主名词与真实指标：次优演化系统中的个体检测器](https://cj9208.github.io/blog/ai_era_engineering_careers/ownerless-nouns-real-metrics-detector/)》——§七 那条组织层面含义的判据来源（注意：判据是"有没有 owner"，不是"是否为副产品"，我在 §七 已就地修正）。
- `notes/reading/kuaishou-conan-stability-agent-notes.md`——**独立来源的同一主张**。快手那篇说"缺乏全局上下文的 AI 会沿最小阻力路径消除表面现象"，且"前置约束（SDD、Coding Harness、Review）能拦一部分，但消灭不了全部"。两家公司、两个不同问题域，撞到同一句结论上，这比任何单篇的百分比都值得信。
