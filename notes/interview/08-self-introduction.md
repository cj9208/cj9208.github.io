# 08 — Self-Introduction（自我介绍 / Tell me about yourself）

> 面试第一问,第一个印象,决定后续话题走向。
> 把定位(`01`)+ 主线脊柱(`03`)+ 组织层(`01`)串成一段 90–120 秒口语。
> 别背简历——用价值弧线定调,让面试官顺着你的主线问。

## 结构（90–120 秒）

| 阶段 | 时间 | 做什么 |
|---|---|---|
| 1. 一句话定位 | 5–10 秒 | 我是谁 + 一句话价值主张（人设一句话） |
| 2. 价值主线 | 40–60 秒 | 三层次递进弧线：个体工具 → 编排 → 治理/架构/审计 |
| 3. 岗位契合 | 15–20 秒 | 为什么这形状就是银行 Director：横切影响力 + 小团队 + hands-on |
| 4. 差异化 + 抛回 | 10–15 秒 | 技术富余 + 团队运行模型；收尾把话题抛给面试官 |

## 完整版（约 2 分钟）

> I am an AI architecture engineer, and my work has followed one clear progression line: from building individual AI tools, to wiring multiple tools into governed orchestration, to working on the governance, architecture, and audit layer that makes the whole thing safe to operate in a bank.
>
> On the individual-tool side, I built RAG retrieval, an intention-recognition layer, and document parsing with strict acceptance gates. On the orchestration side, I moved from one tool to a tool set: a central tool registry, domain routing, and a reusable control plane. On the governance side, my focus was the deterministic control boundary — the model proposes, but the harness decides. Permissions, policy, risk, and execution control live outside the model, which is exactly what a regulated environment needs.
>
> That is why I think in three layers: control architecture, ROI, and the engineering operating model around AI. The real deployment problem in a bank is not model capability; it is placing a probabilistic system inside deterministic institutional boundaries — compliance, audit, cost, and operating risk.
>
> For the role itself, I bring the shape of a Solution Lead or Architect: cross-cutting technical influence, small-team leadership, and hands-on capability. My team model is small and high-trust, spec-driven, with clear gateways and ownership boundaries.
>
> I would be happy to go deeper into any of these. I am especially curious which part has actually been the biggest bottleneck in your environment.

## 压缩版（约 45 秒）

> My work follows one line: I built individual AI tools — RAG, intention recognition, document parsing — then wired them into governed orchestration with a central tool registry and a reusable control plane, and finally worked on the governance layer that makes it safe to operate. My core principle is that the model proposes, but the harness decides: permissions, policy, risk, and execution stay outside the model. That is what bank-grade AI deployment needs. I bring the shape of a Solution Lead or Architect — cross-cutting influence, small high-trust teams, and hands-on work — and I think in three layers: control architecture, ROI, and the engineering operating model. I would love to hear which of those is the real bottleneck where you are.

## 每段意图（讲的时候心里知道在干嘛）

1. **一句话定位**：不是"我懂很多 AI"，而是"我走过整条价值线、比大多数人更懂银行部署现实"。
2. **价值主线**：三层次弧线（`03`）——让他看到你从单点工具一路做到治理层，不是一个故事。
3. **岗位契合**：直接点出 Solution Lead / Architect 的形状 = Google Staff L6 = 银行 Director 档（`01` 职级映射），横切影响力 + 小团队 + hands-on。
4. **差异化 + 抛回**：技术富余用来把组织逻辑融入技术；团队运行模型（网关 + 主备 + 规格驱动）；以问题收尾，把控制权交回面试官。

## 常见错误

- 背简历 / 流水账式讲项目名
- 一开口就堆术语（agent platform / orchestration / governance）
- 只谈模型能力，不谈治理、审计、成本
- 讲得太长（>2 分钟）或没有落点
- 结尾没把话题抛回面试官（冷场）
- 诚实边界没埋好：组织层 ≤10 人互信、经济层只有框架（被追问时直说，见 `01`）

## 指针

- 人设一句话 / 岗位画像 / 职级映射 → `01`
- 三层次弧线 + 60 秒脊柱 → `03`
- 组织层（分布式系统 / TFT / 诚实边界）→ `01`
- 三桶框架深度 → `02`
