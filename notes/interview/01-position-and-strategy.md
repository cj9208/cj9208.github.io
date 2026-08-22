# 01 — Position & Strategy（定位与策略）

> 回答任何问题前，先想清楚：你是谁、面什么岗位、面试官想要什么。
> 本文件解决「怎么想」，`02`/`03` 解决「怎么答」，`05` 解决「现场说什么」。
> 核心新增：「活体反例」定位、反对 hype 的人格证据、以及「为什么是你」的真实故事素材。

## 人设一句话

不是「我懂很多 AI」，而是「我比大多数候选人更懂银行部署的真实问题」。

面试要证明四件事：独立观点 / 把问题框对 / 约束下有明确立场 / 把 AI 架构接回银行现实（合规、审计、成本、运营）。

## 岗位画像（先锁定自己在面什么）

- **目标岗位 = Solution Lead / Architect**（银行 Director，Band 5 / GCB4 档）。
- 这类岗位 = **横切面技术影响力**（跨团队技术方向、架构决策）+ **小团队/技术领导** + **hands-on**。
- 这是技术过配的理想落点：三桶框架（架构判断/可落地/带小团队）正好就是这类岗位的考察点。
- 面试时开口就清楚自己在面什么，所有话术都往"横切面影响力 + 落地"收。

### 职级语境（先记住自己的形状）

- Google 体系里自我定位 = **Staff（L6）**：技术影响力的巅峰，不要求带团队。
- Google 的 Director（Staff+）≈ **要带大组/更大组织**，那层对应银行 MD（GCB3）级别——不是目标。
- 银行 Director（渣打 Band 5 / HSBC GCB4）= **领域技术负责人 + 小团队管理**的混合体。
- 映射钉死：**Google Staff（L6）= 银行 Director**，目标岗位就是自己这档。
- 关键认知：**你的能力形状恰好是银行 Director 的形状**——技术判断力够，团队刚好是"小团队互信、≤10 人"，既不缺技术也不缺带小组的能力，只是没到大规模组织/预算那层。
- **技术富余定位（结构性优势）**：个人技术判断已达 Google Director 水平。在银行 Director 岗位上，这份技术富余正好用来**把组织逻辑融入技术**——有余力处理人/流程/干系人维度，而不是被技术难题和复杂政治（强预算、投靠山）消耗。这就是你在同档候选人里的结构性优势。
- **活体反例定位（直击面试官痛点）**：面试官亲口吐槽过"面试过很多完美简历但空洞的人"，HR 也来请教过我筛选逻辑。这正是我最大的结构性差异化——**我是"简历不完美但有想法"的活体反例**。开场可以直接点破："You mentioned you've interviewed people with perfect resumes but no ideas. I think I'm the opposite shape." 一句话建立识别度，让他从"又来了一个候选人"切换到"这个人自己就是我在找的那种人"。
- **话术反转（防止被读成逃避管理）**：不说"我不做管理"，说"我理解 Director 的管理责任边界，且我有一个清晰的团队运行模型（网关 + 主备 + 规格驱动）"。把组织层从"短板"重新框成"有边界感的团队运行模型"。

## 面试官想要什么

> 他最可能的一句话是「简历完美但没有想法」（Perfect Resume but No Idea or Opinion）。

他指的可能是一类候选人：

- 能描述项目，但说不清自己在想什么
- 知道工具和 buzzword，但讲不出 tradeoff
- 复述市场共识，而不是形成自己的观点
- 只谈模型能力，忽略控制、风险、成本
- 答案安全、漂亮，但空洞

他可能真正在测：

- 这个人能不能独立思考？
- 面对模糊问题时能不能形成观点？
- 能不能区分 demo 和生产级银行系统？
- 能不能把技术设计连接到合规、审计、成本、运营模型？
- 这个人放进严肃的 leadership 讨论里有没有用？

### 最稀缺的东西：反对 hype 的独立批判（人格证据，不是技巧）

"反对 hype"不该只是话术立场，它是我真实的人格证据。我深恶痛绝 buzzword——不是表演，是写了三百篇文章、连很多优秀 paper 的 abstract 都批过的真实审美：**"一个概念如果只能用新词才能显得高级，那它很可能还没被想清楚；真正的本质，是可以被朴素地讲出来的。"** 这恰好是"Perfect Resume but No Idea"的对立面。当他听到我说 "I would not do that yet" / "That works for a demo but not for a bank-grade system" 时，他要听到的不是技巧，是一个长期独立思考、拒绝随大流的人。

## 核心策略

**不要以「我懂很多 AI」开场。** 要让他产生这种感觉：

> "This person understands the real deployment problem better than most candidates."

实现方式：

1. 从他的约束出发，而不是从你的理论出发
2. 直接回答
3. 把问题往深一层重新框（reframe）
4. 表明立场（take a position）
5. 展示 tradeoff 意识
6. 保持具体

核心提醒：

> **Same principles, situational expression.**

底层观点不需要逐题变化。变化的是：

- 你选哪个观点
- 你如何针对他的具体问题去框
- 你为 HSBC / HKMA / 银行部署现实得出什么推论

### 控场锚点（防止顺着对方思路走丢主线）

> 复盘教训：不是所有回答都走丢——整体控场没问题，但**偶尔遇到问得很具体的题，一时间没跳出来**，陷进细节里接招，而不是先归到自己的框架。

做法：**具体题更要在开口前先跳出来归层。** 越具体的题，越容易被细节带走，越需要先定位。三件套锚点——

1. **三桶框架定位**：开口先告诉对方"这个问题在我框架里的哪一层"（控制架构 / ROI / 工程方法）。
2. **三层次弧线定位**：回答具体题时点出"这是我在哪一层做的事"（个体工具 / 编排 / 治理·审计），让他看到你走过整条线。
3. **回拉收尾**：答完把话题拉回你的主线——harness 边界、上游条件化、可预测账单。

对方抛的具体问题只是**入口**，你的回答要把它**带回自己的地图**，而不是陷在细节里跟着对方的地图走。

## 最佳开场入口

最强的切入点是 **HKMA 和银行控制要求**（详见 `05-scripts-and-qa.md`）。理由：从对方的现实出发、展示商业与监管意识、避免像泛泛的 AI 爱好者、自然引到你的架构观点。

## 怎么证明你「好」（How To Demonstrate You Are Good）

不要试图显得更博学。持续做四件事：

1. 把问题说清楚（make the problem clearer）
2. 做出别人混为一谈的区分（make distinctions others blur together）
3. 给出结构化观点（give a structured opinion）
4. 把技术选择连接到真实后果（connect technical choices to real consequences）

最常用的形状（反复使用）：

1. 听出问题（listen for the issue）
2. 精炼复述（restate it crisply）
3. 拆成 2–3 部分（separate it into 2 or 3 parts）
4. 给观点（give your view）
5. 说清含义（explain the implication）

示例：

> So if I understand correctly, the real issue is not whether the model can perform the task, but whether the workflow is governable under HKMA and internal controls. I would probably separate that into three problems: data boundary, execution authority, and auditability. My bias is that these need different control mechanisms rather than a single general AI layer.

## 为什么是你（Why You，最强的话术素材）

框架再完整，也不如"你自己就活成了答案"有说服力。真实故事：**我不是靠简历来的——我是靠写了三百多篇文章，被 Head of AI 在 LinkedIn 私信找到、二十分钟对齐、fast track 到 VP 的。** 我之前投 HSBC 被 HR 秒拒/Ghost，后来 Head of AI 读了我的思考，主动发起面试。这不是炫耀，而是对"他想要什么"的现场演示：

- 他要的是"有想法的人"，而我的 blog 就是几百份不可作假的判断力样本。
- 他要的是"Perfect Resume but No Idea"的对立面，而我的简历恰好不完美、但有想法。
- 他吐槽过"面试过很多完美简历的人但一个都不想要"——我恰好是那个"简历系统差点筛掉、但读懂我的人一眼认出"的人。

被问"为什么是你"时，直接讲这个故事。它的形式本身就是答案：**一个靠深度思考、而非靠格式过关的人。**

## 强候选 vs 弱候选听起来怎样

**强候选的短语**（详见 `05` 判断力短语库）：

- My short answer is...
- The real issue underneath that is...
- I would separate this into three cases...
- My bias is that...
- I think the common mistake is...
- This is really a governance problem disguised as a model problem.
- In a bank, I would optimize for control before capability.
- I would not use one trust model for all AI workflows.

**弱候选的雷区**：

- 长独白
- 过早堆术语
- 泛泛的 "AI is transformative"
- 复述行业标准观点
- 答非所问
- 只谈能力不谈部署现实
- 用力过猛显得聪明

## 他可能关心的 5 个暗测点

1. **能不能排序**（prioritize）：Senior 更在意你知道先做什么，而不是什么都懂。
2. **能不能区分 prototype 与 production**：这是你最强的角度，要用足。
3. **能不能说工程以外的话**：把答案绑到 liability / audit / predictability / governance / operating model / ROI。
4. **能不能反对 hype**：敢说 "I would not do that yet." / "That works for a demo but not for a bank-grade system."
5. **能不能给出迁移路径**（migration path）：内部只读用例 → analyst copilot → 有界 workflow 辅助 → 窄领域可控自动化。

## 组织层（可聊，但诚实限界）

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

## 需要诚实声明的风险清单（Risk Profile）

- confidence calibration 仍需正式规则
- 测试深度仍需加固
- alert 阈值与运行时 triage 仍需打磨
- 当前实现最强的是 intention 层，orchestration 层是方向
- 组织层仅限小团队（≤10 人，互信型）
- 经济层只有框架，无落地数字（组织未给 rollout runway）
