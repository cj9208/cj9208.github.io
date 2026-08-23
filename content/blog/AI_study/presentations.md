---
title: "Presentations 分享记录"
date: 2026-08-23T09:16:26+08:00
lastmod: 2026-08-23T09:30:00+08:00
draft: false

description: "在外部 AI 社区做过的一些 presentation 的记录。"
summary: "在外部 AI 社区做过的一些 presentation 的记录。"

categories:
  - "AI Study"
tags:
  - "Presentation"

slug: "presentations"
---

这里记录我在外部 AI 社区做过的分享（presentation），包含每次分享的主题、时间、场合、内容大纲、slides/原文链接，以及相关的博客文章。

## Agentic Post Training 分享总结

* **时间**：2026-08-09
* **场合**：[EZ.Encoder Academy](https://www.ez-encoder.com/) 社区 · 自我介绍（say-hello）板块
* **原文链接**：https://www.ez-encoder.com/c/say-hello/agentic-post-training
* **内容大纲**：

1. 为什么要 agentic post training？
   * prompt engineering 作为 open loop control 的天然不稳定性 + 人为编写 workflow 太复杂、不可遍历所有情况，容易 miss 各种 edge case（承接上次 harness engineering 分享）
   * claude code 第一次被大众所知的 closed loop control：大模型负责根据情况做决定，而训练大模型做决定的过程就需要 agentic post training
   * 数据到了上限、结果超越人类后，再往前走就需要自我学习（RL，强化学习）来进化
2. 算法层面：RLVR（reinforcement learning with verified rewards）
   * 与 AlphaGo 的区别：go 是确定的游戏、reward 清晰，但实际任务并不清晰，验证是一件非常困难的事（见 [The Comparator Trap](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/)）
   * 衍生出 process reward model：一般任务搜索空间太大，稀疏奖励基本不可训练，需要研究如何给 partial reward
   * 衍生出 anti reward hacking：防止 LLM 走捷径（参考 SWE-bench 例子，附录 B of [From Board Games to Reasoning Agents](https://cj9208.github.io/blog/ai_study/rl-evolution-llm-reasoning-agents/)，也顺带解释了 GPRO 思路）
3. 商业层面：pro 和 flash 模型的双轮驱动
   * pro 模型负责探索（test time compute / MCTS），解决更多问题、创造更多数据，商业上作为公司的实力担当
   * flash 模型负责商业（on policy distillation）：蒸馏常见，但必须 on policy，解决 make decision 时走错路能回来的问题；只用 happy path 训练，遇到 OOD 路径容易崩溃
4. 更多 topic：confidence calibration、state-faithful training、generate harness（harness + flash model 堪比 pro mode）、self evolving
5. 关于创业：pre-training 十万卡级别只有大公司能做；agentic post training 几千张卡门槛较低，可用行业/私有数据调优，是成本低且不易被巨头颠覆的领域；harness 传统公司和个人可做，不涉及训练
6. 关于 Jeff Dean 离开 Google 的观点（见 [科学家退场与工程收权](https://cj9208.github.io/blog/systems_and_governance/corporate/google-scientist-exit-org-decoupling/)）：AI 时代 Google 商业模型受颠覆、投资重导致内部工业化、scientist 与 engineer 对抗，大佬走人说明 Google 已放下身段、安心做 AI 时代的 Amazon
7. 关于研究与执行：平衡探索和执行，执行中带问题回来探索，探索多了需要一个方向去执行（见 [The State Machine of Technical Research](https://cj9208.github.io/blog/ai_era_engineering_careers/state-machine-technical-research/)）

* **相关博客文章**：
  * [The Death of the Wrapper: How Agentic Post-Training Is Reshaping AI Architecture](https://cj9208.github.io/blog/ai_study/death-of-the-wrapper/)
  * [The Comparator Trap: Why High-Stakes AI Fails](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/)
  * [From Board Games to Reasoning Agents: The Evolution of Reinforcement Learning in Large Language Models](https://cj9208.github.io/blog/ai_study/rl-evolution-llm-reasoning-agents/)
  * [科学家退场与工程收权：Google 路线明朗化与 AI 产业的组织解耦](https://cj9208.github.io/blog/systems_and_governance/corporate/google-scientist-exit-org-decoupling/)
  * [The State Machine of Technical Research: Balancing Exploration and Bounded Execution](https://cj9208.github.io/blog/ai_era_engineering_careers/state-machine-technical-research/)

## Agent Harness 框架介绍，工程实践以及传统领域的商业分析

* **时间**：2026-06-28
* **场合**：[EZ.Encoder Academy](https://www.ez-encoder.com/) 社区 · resources（资源）板块
* **原文链接**：https://www.ez-encoder.com/c/resources/agent-harness
* **slides**：[2026-6-28-Jack-The Agent Harness...](https://assets-v2.circle.so/19jxn1s537k4u17ihd7ma95122sa)（181.64 KB）
* **内容大纲**：

1. prompt engineering vs context engineering vs harness engineering：本质是 open loop control 到 closed loop control 的演进，通过增加反馈机制增强表现。通过信息论和系统设计的对比，探讨为何 harness 是必然逻辑
2. Agent Harness 的七大模块（见论文 [LLM-Harness](https://picrew.github.io/LLM-Harness/)）和优化技巧
   * **控制流与编排（Orchestration & Control）**：摒弃过去复杂的图（Graph）工作流，直接把 Context 给大模型让其自主决定下一步（While True 循环）
   * **评估器分离（Comparator）**：为克服大模型的"确认偏差"（认为自己生成的代码都是完美的），必须将生成器与评估器分离，修改后的状态交由全新的大模型独立评判
   * **防止语义偏离（Semantic Drift）**：长时运行任务中，大模型容易"胡扯"并误以为任务已结束；第一步先生成任务说明书（Specification）和验收标准，让评估器严格卡死标准
   * **环境隔离与沙箱（Environmental & Sandbox）**：智能体修复错误时可能破坏已有代码，所有操作先在隔离沙箱执行，通过所有验证后再写入 codebase
   * **上下文管理（Context Management）**：最核心的降本增效手段——按需读取（几十个 task 写入临时 md/json，只读当前部分）、工具与子智能体隔离（上下文剪切 + 只返回精简 json）、确定性过滤（Denoiser 过滤无用日志噪音）、工具分类与动态检索（按阶段分类或 Embedding 相似度动态加载）
3. Reasonix 的具体实践（五层过滤设计：保证效果的前提下尽可能节省 token 费用）
   * 第一层：确定性识别（AST 工具自动补全）
   * 第二层：局部编译器/Linter 检查（静态 linter 或编译工具，确保无语义问题）
   * 第三层：廉价模型（如 Flash Model）微调重试（只修改最后一轮对话 Prompt，最大化命中缓存）
   * 第四层：模型升级（Cluster Failover，Flash 多次失败后升级到 Pro 或推理模型，如 R1/o1）
   * 第五层：人工介入（Human-in-the-loop，Pro 也不行时总结问题征询人工意见）
4. 传统领域（金融/法律/医药）的应用
   * 现状：局限于 Read-Only（只读区域），银行真正上线的只有 IT Chatbot、OCR 文档解析、客服支持等边缘辅助环节；涉及"买股票""投资"等执行权场景因反馈周期长、无法像代码一样即时报错而难以通过合规
   * 痛点：强合规与高错误代价——银行的"幻觉"和"似是而非的错误"可能导致几十亿巨额罚款，且懂技术的合规官极少
   * Harness 的破局点（经济账）：通过闭环控制把失误率从 10% 降到 1%，从概率和经济学角度证明"潜在损失可控、期望收益为正"，推动项目通过合规上线
   * 未来的黄金机会（应用与蒸馏）：顶级 Coding Agent 厉害不仅在于 Harness 框架，更在于与底层大模型（Post-training/SFT/RL）的强绑定；银行等大机构因数据不出境和合规要求必然选择本地私有化部署，harness + 小模型实现大模型效果的技术路线前景广阔；未来 3~5 年算力和大模型成本降低 100 倍，利用 Harness Engineering 做降本增效的"AI 应用岗位"将是未来 5~10 年的黄金赛道
5. 补充：最近的 AI coding 心得（从利用本体 + harness + 多智能体来编写具有业务逻辑的应用代码出发，公众号"工程师的本体论"）

* **相关博客文章**：
  * [The Comparator Trap: Why High-Stakes AI Fails](https://cj9208.github.io/blog/ai_study/harness-engineering/the-comparator-trap-why-high-stakes-ai-fails/)（评估器分离/Comparator）
  * [Harness as an OS: Architectural Musings on Reasonix](https://cj9208.github.io/blog/ai_study/harness-engineering/harness-as-os-reasonix/)（Reasonix 五层过滤）
  * [生态式架构：AI 时代的 EMD 演进逻辑](https://cj9208.github.io/blog/ai_study/eco-architecture-ai-emd-evolution/)（本体/harness/多智能体的编码思路）
  * [AI-Coding 的防御性进化：平台化、业务解耦与结构的自然生长](https://cj9208.github.io/blog/ai_study/ai-coding-evolution/)
  * [算力经济学：从历史沙盘推演 AI 的百倍通缩终局](https://cj9208.github.io/blog/ai_study/compute-economics-deflation/)（算力成本 100 倍降低）
