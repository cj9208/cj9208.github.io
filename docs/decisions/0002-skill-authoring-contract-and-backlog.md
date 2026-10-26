# 0002. 技能设计的写作契约与欠账顺序（第一阶段不动内容）

- 状态：已采纳（待办部分持续更新，见文末"待办"）
- 日期：2026-10-26
- 关联：取代 `notes/skills-portability/`（两份文档已删除，内容并入本文件；原文在 git 历史 `4c5e752` 可查）；装订层的决定见 [0001-agent-skill-canonical-directory.md](./0001-agent-skill-canonical-directory.md)

## 背景

装订层落地后，正本 19 份 `SKILL.md` 跨 harness 可用了，但**内容本身没有经过设计审校**——它们是一路实践中逐条长出来的，从没按同一套标准回看过。

推动这次记录的不是"想整理"，是一组实测结论：**写得差的技能会掉到无技能基线以下**。SkillsBench 的消融实验里，详尽到全面的正文把增益从 +18.0pp 压到 +0.7pp；同一任务挂 4 个以上技能时增益从 +19.0pp 掉到 +10.1pp；用 skill-creator 批量自造的技能是**负收益**（−8.1 到 −11.5pp）。SWE-Skills-Bench 更直接：49 个公开技能里 **39 个通过率零改善**，均值 +1.2%，token 开销最高 +451%。也就是说"多写技能"本身不是资产，可能是负债——那么"哪些该改、按什么顺序改、改完怎么算成功"就变成需要冻结的项目级决定，而不是每次会话各凭手感。

## 决定

1. **两阶段路线：先可用，再优化。** 第一阶段只做装订（已完成，见 0001），不碰任何技能正文。
2. **写作契约 R1–R7 是唯一标准**，列在下面；新写或改技能都按它验收，不符合的记入文末待办，不即时修。
3. **优化顺序冻结**：P0-1 → P1-1 与 P1-2 → P2-1 → P1-3 与 P1-4 → P2-2/3/4 → 最后建判据回路。排序原则是"改动面小且直接影响触发准确率的先做"（`description` 字段一处改，风险最低）。
4. **判据回路建立之前，不合并、不删除任何技能。** `capstone-*` 六个与 `sync-*` 三个看起来像可以合并，但没测过的合并等于把有效部分一起扔掉。
5. **本文件只有"待办"一节可变**：完成一条在其后追加结果与日期，不删除条目正文，也不改写"决定"与"被否决的备选"。后续事实推翻本决定时新增 000N，不回来改这篇。

### 写作契约 R1–R7

- **R1 唯一真源**：真实文件只在 `.agents/skills/<name>/`，其余是链接或生成物。可检验形式：任何一份能被独立编辑的拷贝，半年后必然与正本不同。
- **R2 frontmatter 只用规范六字段**（`name`/`description`/`license`/`compatibility`/`metadata`/`allowed-tools`），harness 私有字段一律挂 `metadata:` 下。理由：Codex 不解析规范外顶层键（写了等于没写）；而打包上分发渠道时它是**硬报错**——本地能跑、分发那天才炸，是最坏的一类不一致。**已核：19 份文件当前零违规。**
- **R3 触发句前置，正文不复述触发条件**。描述模板固定为 `<做什么>. 触发：<用户会说的动词/短语 3-6 个>. 不用于：<最容易误选的相邻场景> → <相邻 skill 名>.`，控制在 500 字符内。因为 Codex 按上下文 2% 截目录、Claude 在 1536 字符截 `description + when_to_use`，都是**从尾部截**——触发关键词放尾部等于没有；而"何时不用"必须进描述而非只写正文，因为多数 harness 只把 name+description 注入目录，等正文加载时误选已经发生。
- **R4 工具用能力称谓，依赖显式声明**：正文写"取不到时用可用的浏览器渲染能力"，不写具名工具的具名调用；需要硬绑时声明 `metadata: requires: [...]`，让装订层能拒绝或降级，而不是换 harness 后静默变哑。反向成立：**仓库内的具名文件路径可以写**（`content/blog/` 等），那是跨 harness 稳定的约定。
- **R5 引用只走一层**，`references/*.md` 只由 `SKILL.md` 直接引用，不互相引用；引用写成条件式（"若 X 则读 references/Y"）。跨 skill 共享资料是反模式——别做 `references/common.md` 被多个技能引用，那会让 R5 静默失效；共享部分复制进各自目录。
- **R6 脚本窄入口宽出口**：只依赖标准库或 `metadata.requires` 声明过的依赖，显式传参，输出走 stdout 结构化文本；不使用 Claude 独占的 `` !`cmd` `` 内联执行。本仓库另叠一条红线：脚本读写中文一律 `encoding='utf-8'`（或 PowerShell 显式 `-Encoding UTF8`）。
- **R7 每个技能自带 Verification 段**：结尾写"什么算成功"，且必须是可观测、harness 无关的结果（文件落在哪、条数对得上、构建通过）。

**边界**：技能适合固化"动作明确、结果可验证"的部分（构建命令、修改范围、命名规范、review 维度、发布前检查）；业务取舍、风险例外、不可逆决策不塞进去。长期生效的项目规则属于 `AGENTS.md` 的 always-on 层，不属于按需加载的技能层——两个机制混用会表现为"有时候记得有时候不记得"。

## 被否决的备选

- **一次性重写全部 19 份**：没有判据时的批量改写等于把 19 份手感换成另一种手感，而且自造技能批量低于基线这条证据正好适用于批量重写。
- **先建判据回路再动其它**：判据要求每个技能约 20 条触发查询集 + 8 正 8 近似反例 × 3 次运行，成本前置会把已经完成的装订层一起拖住。它排在最后，但它是前面所有改动的**验收前提**，不是可选项。
- **债务清单继续留在 `notes/`**：否决理由就是本文件的由来——一份会改变未来 agent 行为的待办，放在私人笔记里等于下次会话必须重新诊断一遍。`notes/` 只留过程记录与选题。
- **每条债务单独写一篇记录**：那会把 `docs/decisions/` 变成第二份 changelog，违反 0001 之后写进 `AGENTS.md` 的写入门槛（要同时满足"改变了别人会依赖的结构"和"存在被否决的备选"）。
- **给 Claude Code 也建 `.claude/skills` 联接**：0001 曾计划这一步，被 OpenCode 的三根扫描否决（见 P0-1）。

## 依据（执行待办时需要的事实）

发现路径与预算，五个 harness 里三个原生读 `.agents/skills/`，只有 Qoder 与 Claude Code 需要链接动作：

| | Qoder | OpenCode | Codex CLI | Claude Code | DeepSeek Harness |
|---|---|---|---|---|---|
| 项目级路径 | `.qoder/skills/` | **三根同扫**：`.opencode/`、`.claude/`、`.agents/skills/`，向上走到 git worktree | `.agents/skills/` | `.claude/skills/` | `.agents/`、`.dsh/` |
| 解析的 frontmatter | `name`/`description`，其余未验证 | 规范六字段，未知字段忽略 | **仅** `name`/`description`/`metadata.short-description` | 一长串私有字段（`when_to_use`、`paths`、`disable-model-invocation` 等） | 至少 `name`/`description` |
| 描述预算 | ≤1024 | 1–1024 | 目录预算 = **上下文窗口 2%** | `description + when_to_use` 拼接后**截断于 1536 字符** | 未验证 |
| 调用方式 | 自动 + `/name` | 模型经 `skill` 工具选中，**无斜杠接线** | 自动 + `$name` + `/skills` | 自动 + `/name` | 自动 + 斜杠 |
| 执行 `scripts/` | 支持 | 只读，agent 自己用 shell 跑 | 执行 | 执行（内联语法可关） | **未验证** |

来源：agentskills.io 规范、Qoder/OpenCode/Claude Code 官方文档、Codex 文档与源码解析器（二手，标注待一手复核）、DeepSeek Harness 用户指南。未验证项见 0001 的后果一节。

三条写法结论（有一手对照实验）：

- **描述里不要有流程摘要**。superpowers 的实测记录：描述写了 "code review between tasks"，流程图规定两次 review，实际只跑一次；修法是删掉流程，机制是"描述一旦概括流程，agent 照摘要走、不读正文"。
- **产物形状类失败用正面配方，不用禁令**。superpowers 的"Match the Form to the Failure"：规则被跳过→禁令+合理化对照表；产物形状错→**正面配方**（禁令那一组实测反而产出更多不想要的内容）；要素遗漏→必填模板槽位；条件性→可观测谓词。
- **过程而非散文**：步骤、检查点、退出条件；同时给可选步骤标"可选"并提供快路径——307 例技能致因失败里**最大单一原因是过度验证（67 例）**，第二是重型流水线（30 例）。

Windows 事实：真符号链接需开发者模式或提权（本机 `os.symlink` 返回 WinError 1314），**目录联接 `mklink /J` 不需要**，且 Node `lstat` 对二者返回值一致，对扫描器不可区分。这是自建路线零摩擦的前提。

## 待办（唯一可变部分）

### 实测快照（2026-10-26）

`禁令` = 正文"不要/不得/禁止/别/不可/不应"次数；`反触发` = "何时不用/不适用/NOT for/When NOT"次数；`H2` = 二级标题数；`scr` = 是否带 `scripts/`。

| skill | 行 | desc 字符 | H2 | 禁令 | 反触发 | scr |
|---|---|---|---|---|---|---|
| stress-test-reasoning | 96 | 369 | 0 | 0 | 0 | – |
| add-hugo-front-matter | 259 | 192 | 9 | 12 | 0 | S |
| capstone-coaching-core | 43 | 448 | 0 | 0 | 0 | – |
| review-blog-content | 130 | 497 | 6 | 12 | 2 | S |
| add-ez-encoder-presentation | 125 | 350 | 5 | 6 | 1 | S |
| search-blog-articles | 119 | 468 | 8 | 4 | 0 | S |
| restore-missing-links | 118 | 363 | 7 | 6 | 0 | S |
| sync-subfolder-links | 136 | 326 | 6 | 5 | 2 | S |
| rename-blog-filenames | 108 | 224 | 9 | 2 | 1 | S |
| capstone-build-expertise | 28 | 376 | 0 | 0 | 0 | – |
| digest-article | 98 | 256 | 6 | 19 | 3 | – |
| capstone-fieldwork | 42 | 379 | 10 | 0 | 0 | – |
| capstone-project-framing | 26 | 318 | 0 | 0 | 0 | – |
| capstone-deepen-opportunity | 29 | 363 | 0 | 0 | 1 | – |
| sync-zhihu-migration-status | 88 | 418 | 5 | 4 | 0 | S |
| pipeline-blog-init | 88 | 206 | 1 | 0 | 0 | S |
| generate-article | 22 | 359 | 0 | 0 | 0 | – |
| capstone-compare-opportunities | 27 | 336 | 0 | 0 | 0 | – |
| generate-outline | 26 | 326 | 1 | 0 | 0 | – |

按行数全部在规范红线（500 行）内；描述最长 497 字符，无一接近截断预算。所以下面的条目不是"太长"，是形状与触发问题。

### P0：会静默失效

- [ ] **P0-1 Claude Code 的接入路径未定。** 它只读 `.claude/skills`，而 OpenCode 项目级同时扫三根并要求技能名跨根唯一，所以不能简单建一个 `.claude/skills` 目录联接。三条待选：①确认 OpenCode 的跨根重名行为究竟是报错还是按优先级择一（读源码或实测）；②改成 per-skill 联接并验证去重；③接受"用 Claude Code 时它只看得到 `.claude` 里显式挑出的子集"。**当前处置**：`AGENTS.md` 已下"禁止手工创建 `.claude/skills`"硬约束，`bind_skills.py check` 会把该目录报成 DUPLICATE ROOT。
- [ ] **P0-3 联接的删除风险只有文档约束。** `.qoder/skills` 是重解析点，Git Bash/MSYS 下 `rm -rf .qoder/skills` 可能穿越联接删掉正本。现约束为 `AGENTS.md` 与脚本 docstring；机制化方案（如 bind 后给 `.agents/skills` 设只读属性、或脚本里加删除守卫）**本轮故意没做**。
- [x] ~~P0-2 联接的实际可用性~~ **已验证通过（2026-10-26）**：一次性探针技能放入后下一轮出现在可用技能清单、删除后下一轮消失，双向观测；顺带证明 Qoder 每轮重扫、新技能无需重启会话。

### P1：触发与产物形状（有一手依据）

- [ ] **P1-1 描述里不该有流程摘要**（违反依据第一条）。命中：`digest-article`（描述含"先抓正文→降级 browser-use→对话给摘要→确认后落盘"完整链路，另有一句属正文的元规则）、`review-blog-content`（497 字符里塞了类型分类逻辑）、`search-blog-articles`、`sync-zhihu-migration-status`。目标形状见 R3 模板。
- [ ] **P1-2 11/19 个技能没有"何时不用"**：`stress-test-reasoning`、`add-hugo-front-matter`、`search-blog-articles`、`restore-missing-links`、`sync-zhihu-migration-status`、`pipeline-blog-init` 与 5 个 `capstone-*`。依据：Claude Code 与 Codex 官方写法都把"何时不使用"列为描述必备成分；SkillsBench 归纳的第二种伤害是"技能覆盖掉模型本来更强的策略"，对策原话是 *include applicability boundaries, not just preferred procedures*。六个 `capstone-*` 相互边界只写在各自描述开头一句，近似反例缺位——同族技能最容易互相误选的形状。
- [ ] **P1-3 判断型技能用禁令而非正面配方**。计数前三：`digest-article` 19、`add-hugo-front-matter` 12、`review-blog-content` 12。依据是"禁令组反而产出更多不想要内容"那条对照结论。修法是把每条禁令**翻译成一个形状描述**，而不是删掉——本仓库作者偏好禁令式表达，这条特别对症。
- [ ] **P1-4 编排技能可能复述了被编排者的纪律**。待核对 `pipeline-blog-init`（88 行 / 1 个 H2 / 0 反触发）是否把三步技能的内部步骤抄了一遍。依据：user-invoked 只管编排、model-invoked 才持有纪律，编排技能不得调用另一个编排技能，复述即同一规则两份拷贝。

### P2：结构与体量（依据较弱，但便宜）

- [ ] **P2-1 7/19 正文零个二级标题**：`stress-test-reasoning`（96 行 / 9389 字符纯段落流）、`capstone-coaching-core`、`capstone-build-expertise`、`capstone-project-framing`、`capstone-deepen-opportunity`、`capstone-compare-opportunities`、`generate-article`。目标形态是"祈使句过程 + 可勾选清单 + 检查点"。`stress-test-reasoning` 优先——它是最常在对话里手动调用的那个。
- [ ] **P2-2 验证步骤要设上限并标快路径**：`sync-subfolder-links` 验证类词 12 次、`review-blog-content` 11、`add-ez-encoder-presentation` 10。依据：过度验证是技能致因失败的最大单一原因（67/307）。注意这条不是说验证习惯错，而是**写进技能后它会变成强制工作**，代价不同。
- [ ] **P2-3 `add-hugo-front-matter` 是唯一接近体量线的（259 行）**。拆分触发条件与做法：把按变体切的参考资料移入 `references/`，让 agent 只读到需要的那份；它里面 12 条禁令（P1-3）和命名细则多数属"被选中后才需要"。
- [ ] **P2-4 两处文件位置**：`add-hugo-front-matter/tags-registry.md` 在技能根而非 `references/` 下；`search-blog-articles/index.json` 是 299KB 生成物也在根目录。规范归位是参考→`references/`、模板与资源→`assets/`；生成物放技能根还会随目录被复制、打包和 diff。

### 判据回路（排在最后，但是验收前提）

- [ ] 带技能/不带技能成对跑（`evals/evals.json`，先 2–3 个用例，断言在第一轮跑完之后再补）；触发用约 20 条查询、8 正 8 近似反例、每条 3 次、阈值 0.5、60/40 训练/验证切分。看**通过率与 token/时间的双 delta**——高 2 个点但 token 翻倍未必值得。反直觉判据：**加规则后通过率持平 = 技能过约束，该删而不是该补。**
- [ ] 基准预期：curated 技能在 SkillsBench 里把 33.9% 提到 50.5%，但 87 个任务中仍有 13 个负 delta——别指望一键变好。
- [ ] **半年一次事实审计**：把 19 个技能里的"事实断言"逐条对源码或官方文档过一遍，而不是只改文案。机制是"自信但错误的 gotcha 会变成承重结构"，模型会照着它坚决地做错且难以察觉；SWE-Skills-Bench 里退化最高的 3 个技能，原因写的是"版本不匹配的指引与项目上下文冲突"。

## 后果

接受的代价：多了一份需要维护的契约（R1–R7 若与规范演进冲突，以 agentskills.io 为准并回来更新本文件）；19 份技能在判据建立前保持"能用但未经设计"的状态；P0-1 与 P0-3 是显式欠账，不是已解决。

收益不只是"省切换麻烦"：**它让技能第一次成为可版本化的资产**。"困难↔方案咬合"这类读法原本只活在肌肉记忆里，固化成一份符合规范、五个 harness 都能加载、且能被脚本校验的目录之后，它才可审计、可回滚、可迁移。

未验证：没有任何 harness 真跑过一次"只说触发词、不提技能名"的自动触发；带脚本的技能未在新路径下执行过；OpenCode / Codex / dsh 三侧"能列出 19 条"仍是读文档得出的结论。这三项属于上面的判据回路。

## 本次被推翻的判断

1. **原计划给 Claude Code 建 `.claude/skills` 联接**——被 OpenCode 的三根扫描否决，降级为 P0-1 未决项。
2. **"文档级 diff 能证明两份拷贝漂移"**——`.qoder/skills` 一直是符号链接，那条 DIFF 是方法假阳性（同一 inode）。
3. **技能体积超线**——把 `wc -c` 的 UTF-8 字节数当成了字符数（中文 3 字节/字）；按行与字符重算后全部在规范内，"落在衰减区间""描述会被截尾"两条结论撤回。
4. **这类待办该放 `notes/`**——本文件的由来。

教训是一条可复用规则：**结论里的每个数字都要说明它是什么单位、怎么来的。** 上面第 2、3 条都不是判断力问题，是把目录名比对当成了内容比对、把字节当成了字符。
