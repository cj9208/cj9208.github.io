# rag-orchestration-architecture 质量分析报告

- 日期：2026-09-19
- 用途：发布前最终审阅
- 范围：`content/blog/AI_study/rag-orchestration-architecture/` 全部 13 个文件（CH00–CH04 + `_index.md`），外加 2 处站内引用页
- 当前状态（2026-09-19 晚）：3 处修正与发布准备已全部执行完毕（13 文件 `draft: false`、索引页条目就位、lastmod 刷新、Hugo 构建验证通过）；工作区未提交，等用户决定 commit/push

---

## 一、总体结论

1. 遗留事项：`notes/blog-todo.md` 中本批次仅剩「发布决策」一项未决，其余 4 项均已完成（见第二节）。发布所需的工程验证（golden sets、阈值校准、告警规则）已明确移出范围，无需发布前补齐。
2. 内容质量：按 blog 标准——设计故事线（CH00 起源 → CH01 控制路径 → CH02 运行时 → CH03 RAG 子系统 → CH04 可验证性）、决策表体系、边界声明三样齐备；参考栈与预算 schema 全树一致；"illustrative 非生产阈值"声明到位。
3. 待修正：3 处低风险一致性问题（计数措辞、枚举完整性），均为表述层，不涉及架构内容（见 3.2）。
4. 发布时机械事项：13 文件 draft 翻转、2 处索引页处理、lastmod 刷新（见第四节检查单）。

## 二、blog-todo 遗留事项核对

| # | 事项 | 状态 |
| --- | --- | --- |
| 1 | 重写 `CH03_04_Grounded-Answering-Layer.md`（叙事密度对齐 CH04） | ✅ 2026-08-27 完成（commit `7581fe7`） |
| 2 | CH03 选定推荐参考栈 | ✅ 2026-08-27 完成 |
| 3 | first-version 阈值标注 illustrative | ✅ 2026-08-27 完成 |
| 4 | 发布决策 | ⏸ 暂缓（2026-09-19 复查），未定日期 |
| 5 | `progress.md` 去留 | ✅ 已移入 `notes/`（2026-09-19） |

范围界定：golden sets / 阈值校准 / 告警规则已按 blog 标准明确移出范围，留给未来实际部署或 ops 向续篇。此项与本套 `_index.md` 的 "Not yet defined" 列表表述一致。

## 三、质量核查结果

### 3.1 已核查项（通过）

- **结构完整性**：13 文件 front matter 均含完整字段（title / date / lastmod / draft / slug / description / summary / categories / tags）；`draft: true` 全覆盖；slug 与文件名一致、无重复；lastmod 为真实时间戳，无 `09:00` 类占位值。
- **无 TODO / TBD / FIXME 残留。**
- **链接规则**：正文中的站内互链（CH01 L192、CH02_01/02/03 顶部 Related notes）均为公开链接，符合 AGENTS.md；`_index.md` 内部使用 relref（栏目页例外，合规）。
- **参考栈一致性**：MinerU → Elasticsearch（OpenSearch 列为 drop-in）+ Qdrant → BGE reranker → 直接 LLM API（Instructor / Guardrails）全树统一；pgvector（早期阶段）与 Vespa（统一方案）的定位说明在各章一致。
- **预算模型一致性**：CH02_01 envelope 为权威 schema（7 字段）；CH01（定性示例）、CH02_02（规则与回退表）、CH02_03（决策表）均正确引用，无冲突值。
- **决策表体系**：CH01 routing contract（9 行）→ CH02_03 execution / validation 决策表 → CH04 契约到测试类映射完整，每个契约都有对应测试类。
- **illustrative 声明**：CH01 工作案例（"not calibrated production thresholds"）、CH03_01 阈值说明、CH03_02 region-confidence 处均已标注。

### 3.2 发现的问题（3 处，低风险，均为表述层）— ✅ 已于 2026-09-19 全部修复

**问题 1 — CH02 主文边界计数两处不一致（附步数措辞）** ✅ 已修复

- `CH02_Request-Orchestration-Layer.md:38` 概述写作 "three hard controls"（三大类：cross-domain policy / governance / escalation budgets）
- `:180` 正文写作 "Four boundaries apply"，随后实际有 **5** 个小节：Governance Boundary（`:182`）、Cross-Domain Policy（`:193`）、Escalation Budgets（`:231`）、Latency UX（`:237`）、Human Handoff Contract（`:261`）
- 附带：`:104` 说 "Twelve steps"，而步骤表（`:129–143`）为 13 行（1–12 + 8A 插行）
- 修复成本：两处措辞。建议 L38 保留三分法但改称 "three boundary families" 之类，L180 按实际小节数统一；步数处改为泛指或把 8A 并入第 8 步

修复结果：L38 概述改为 "five boundaries around the flow"（列出五个边界）；L180 改为 "Five boundaries apply to every path through the flow"；L104 改为按阶段概括（"Steps 1–4 … and the clarification gate are inherited from CH01"），不再出现具体步数。

**问题 2 — CH02_01 的 routing decision 枚举缺少 `switch_capability`** ✅ 已修复

- `CH02_01_Runtime-Objects.md:298–307` 列出 8 个决策值（proceed / proceed_conservative / clarify / stronger_model / execute_capability / retry / handoff_human / reject），并声明与 CH01 routing contract 对齐
- 但 `switch_capability` 在 `CH02_03`（`:165`、`:349`、`:387`、`:478`、`:497`）、`CH02_02`（`:214`）、`CH04`（`:139`）中均作为合法动作 / 期望结果出现
- 附带：`CH02_02:208–214` 的「LLM 可提议动作」用词（`reinterpret`、`retry_execution`）与 CH02_01 决策值（`retry` 等）不完全对齐，建议补一行映射说明或统一命名
- 修复成本：枚举补一行 + 一句映射说明

修复结果：CH02_01 枚举补入 `switch_capability`（共 9 值）；CH02_02 在「harness is the final authority」句后补一句映射说明（`reinterpret` / `retry_execution` 记录为 `retry`，由 `decision_reason.primary` 区分）。

**问题 3 — CH02_02 caps 汇总遗漏 `max_tool_calls: 4`** ✅ 已修复

- `CH02_02_State-Machine-and-Control-Loop.md:301–307` 的 "First-Version Default Caps" 列 6 个值；CH02_01 `:116` envelope 共 7 字段（多 `max_tool_calls: 4`）
- 修复成本：补一行

修复结果：caps 列表补入 `max_tool_calls: 4`（共 7 值，与 CH02_01 envelope 对齐）。

修复后核验：全树 grep 无 `Twelve` / `hard controls` / `Four boundaries` 残留；CH02 全量 diff 逐行核对无内容损伤；Hugo 构建（无 `--buildDrafts`）exit 0，relref 全部解析。

### 3.3 交叉引用风格（已统一 — 方案 C 于 2026-09-19 执行完毕）

原状：全树正文 59 处反引号文件名提及中，45 处为纯文件名（线上不可点击），14 处已在 commit `31e203f` 转为公开链接；`_index.md` 另有 2 处纯提及（该页其余 12 处为 relref）。

用户选定方案 C（全部转链接），已执行：

- 12 个章节文件：45 处 → 公开链接 `https://cj9208.github.io/blog/ai_study/rag-orchestration-architecture/<slug>/`，各文件 lastmod 已刷新
- `_index.md`：2 处 → relref 链接（沿用该页栏目页惯例），lastmod 已刷新
- 有意保留 1 处：CH02_01 代码块内 YAML 注释提及（非链接语境）

转换后核验：0 处纯反引号残留；59 处公开链接 URL 与 slug 逐一比对无错；14 处 relref 目标文件全部存在；未破坏任何既有链接（负向断言防误伤）。

### 3.4 发布时的外部影响点（2 处）— ✅ 均已处理

- `content/blog/AI_study/_index.md:46`：原为 `* rag-orchestration-architecture（整理中，未发布）` 纯文本占位 — ✅ 已改为独立板块 `## RAG Orchestration Architecture`（标题 + relref 合集链接 + 中文摘要）；原 `## 参考资料` 板块已无成员，随之移除（**此项为执行时的判断选择，已在对话中向用户说明待确认**）
- `content/blog/AI_study/harness-engineering/_index.md:44`：已有公开链接指向本套 overview，当前 404；发布后自动生效（无需改动，仅需部署后确认）

## 四、发布检查单（恢复发布时执行）

机械步骤（blog-todo 原有约定）：

1. ✅ 13 个文件 `draft: true` → `false`（2026-09-19 执行）
2. ✅ lastmod 刷新为 `2026-09-19T10:49:38+08:00`（统一时间戳）
3. ✅ 更新 `AI_study/_index.md:46` 条目为正式链接（见 3.4）
4. ⏳ 部署后核对：overview 线上可访问、harness-engineering 引用链接生效、各章相互跳转正常（待用户 push 后执行）
5. ✅ 修复 3.2 的 3 处一致性问题（2026-09-19 执行）
6. ✅ ~~转化反引号引用~~ 已完成（2026-09-19，方案 C；见 3.3）

本地验证：Hugo v0.164.0 extended 构建（不含 `--buildDrafts`）exit 0，1056 pages；`blog/ai_study/rag-orchestration-architecture/` 下 12 章 + overview 全部生成；AI_study 索引页新板块链接渲染正确；修正内容渲染核对通过（Five boundaries / `switch_capability` / `max_tool_calls` / ch01 公开链接）。

## 五、审阅建议

按 blog 标准（设计故事线、决策表、边界声明），本套已达发布条件；3 处表述层问题已全部修复，发布准备（draft 翻转、索引条目、lastmod）已完成并通过本地构建验证。剩余动作：用户在确认 `AI_study/_index.md` 板块调整后自行 commit + push，部署后完成检查单第 4 项线上核对即可。
