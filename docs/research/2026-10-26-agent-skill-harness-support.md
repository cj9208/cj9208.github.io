# Agent Skills 跨 harness 支持现状调研

- as-of：**2026-10-26**，测量时的仓库状态 = 提交 `dcd572e`（正本 19 份 `SKILL.md` 位于 `.agents/skills/`）
- 结论被引用于：`0001-agent-skill-canonical-directory.md`（装订层决定）、`0002-skill-authoring-contract-and-backlog.md`（写作契约与待办）
- 失效条件（复核触发）：**任何一个 harness 的路径约定、字段解析集或截断预算发生变化**。这份文档的价值全在日期——它描述的是别家软件，不是本仓库，过期了不会自己报错。半年一次的事实审计（0002 待办最后一条）应连本文件一起过。

## 一、结论：物理形态已经统一

2025-12 起 Agent Skills 是开放标准（源自 Anthropic 2025-10 的机制，规范托管在 [agentskills.io](https://agentskills.io/specification)）：一个目录 + 一份带 YAML frontmatter 的 `SKILL.md`，可选 `scripts/`、`references/`、`assets/`。规范字段：`name`（≤64，小写连字符，须等于目录名）、`description`（1–1024）、`license`、`compatibility`（≤500）、`metadata`、`allowed-tools`；正文建议 **<500 行 / <5000 token**；三层渐进披露（目录只注入 name+description → 选中后加载正文 → 按需加载 references）。

所以"格式"不需要设计。没统一的是三件事，且性质不同：**在哪被发现**（装订）、**用什么预算被触发**（触发）、**能不能真跑起来**（能力）。借编译器的形状看，是四层：

| 层 | 内容 | 可移植性 | 应对方式 |
|---|---|---|---|
| 装订层 | 目录位置、发现顺序、命名冲突规则 | 无（各家路径约定不同） | **生成**，绝不手写、绝不进 git |
| 触发层 | `name` + `description` 及其注入预算 | 有最严公共分母 | 按公共分母**约束写法** |
| 指令层 | `SKILL.md` 正文 | 完全可移植 | 唯一真正的资产，人写 |
| 能力层 | `scripts/` 执行、工具名、权限模型 | 半可移植（能跑 ≠ 认得同名工具） | **能力称谓 + 显式声明**，装订层校验 |

> 一个 skill 的可移植性 = 它四个层里**最不可移植那一层**的可移植性。

推论：手工维护多份拷贝之所以必然漂移，是因为它把这四层当成一层在抄。而工作量比想象小——**五个目标 harness 里三个原生读 `.agents/skills/`**，只有 Qoder 与 Claude Code 需要链接动作。通用版 = 一个 canonical 目录 + 两条链接规则 + 一份作者规范。

## 二、现状矩阵（范围内五个，字段以官方文档为准）

| | Qoder | OpenCode | Codex CLI | Claude Code | DeepSeek Harness |
|---|---|---|---|---|---|
| 项目级路径 | `.qoder/skills/` | **三根同扫**：`.opencode/skills/`、`.claude/skills/`、`.agents/skills/`，从 cwd 向上走到 git worktree | `.agents/skills/`（cwd 向上到仓库根） | `.claude/skills/`（支持父目录/嵌套） | `.agents/`、`.dsh/` 下 |
| 用户级路径 | `~/.qoder-cn/skills/` | `~/.config/opencode/skills/`，也读 `~/.claude/`、`~/.agents/` | `~/.agents/skills/`、`~/.codex/skills` | `~/.claude/skills/` | UNVERIFIED |
| 读 `.agents/skills/` | **不读**（文档只见 `.qoder/skills`） | 读 | 读（主路径） | UNVERIFIED（文档只写 `.claude/skills`） | 读 |
| 解析的 frontmatter | `name`/`description`，其余 UNVERIFIED | 规范六字段，未知顶层键忽略 | **仅** `name`/`description`/`metadata.short-description`；`license`/`compatibility`/`allowed-tools` 不解析 | 一长串私有字段：`when_to_use`、`paths`、`allowed-tools`、`disallowed-tools`、`disable-model-invocation`、`user-invocable`、`model`、`effort`、`context`、`agent`、`hooks`、`shell`、`argument-hint` | 至少 `name`/`description` |
| 执行 `scripts/` | 支持 | 只读，由 agent 自己用 shell 跑 | 执行 | 执行（`` !`cmd` `` 内联也执行，可关） | **UNVERIFIED** |
| 调用方式 | 自动 + `/name` | 模型经 `skill` 工具选中，**无斜杠接线** | 自动 + `$name` + `/skills` 选择器 | 自动 + `/name` | 自动 + 斜杠 |
| 截断/预算 | `description` ≤1024 | 1–1024 | 技能目录预算 = **上下文窗口的 2%** | `description` + `when_to_use` 拼接后截断于 **1536 字符** | 采用渐进披露，预算数字 UNVERIFIED |
| 跨根重名行为 | — | 名必须唯一（后果 UNVERIFIED：报错 or 择一，需读源码） | 两个都进选择器，**不合并** | 前缀区分；`synced`/`anthropic-skills` 保留 | — |
| 优先级 | 项目 > 用户（推测） | 多根，名唯一 | 仓库 > 用户 > 系统 | 企业 > 个人 > 项目 > 内置 | — |

来源：[agentskills.io 规范](https://agentskills.io/specification)、[Qoder Skills](https://docs.qoder.com/zh/cli/Skills)、[OpenCode skills](https://opencode.ai/docs/skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[DeepSeek Harness 用户指南](https://dsh.hicyou.com/zh/docs/user-guide)、[Codex Agent Skills](https://test.runoob.com/codex/codex-agent-skills.html)（**二手**，其字段解析结论与 [Codex 源码解析器](https://github.com/openai/codex/blob/main/codex-rs/skills/src/parser.rs) 一致，标记待一手复核）。

两处来源不一致或未定，均已降级：

1. OpenCode 的三根扫描**已一手核实**（官方文档原文列出三个项目级位置及各自全局等价物，并说明向上走到 git worktree）；跨根重名的**后果**先前写"会直接报错"，现降级为 UNVERIFIED。结论不变：**只能有一个根真的装着内容**。
2. dsh 发布日期两个来源不一致（官网 2026-08-13，中文对比文 2026-08-27 开发者预览）。项目级技能走 `.agents/` 这点各方一致；打包成分发插件是另一条路（`dsh.bundle` / Cordis 市场），不在本调研范围。

## 三、Windows 事实（决定装订路线的那条）

真正的符号链接需要开发者模式或管理员权限；**目录联接（junction，`mklink /J`）不需要**，且对"只有目录"的 skill 完全够用。已在本机实测：`python os.symlink()` 建目录链接返回 WinError 1314（客户端没有所需特权），自动降级为 junction 成功；Node `lstat` 对 junction 的返回值与符号链接一致（`isSymbolicLink=true`），故对 harness 的扫描器而言二者不可区分。

另一条必须记住的反向风险：联接是重解析点，Git Bash/MSYS 下 `rm -rf .qoder/skills` 可能**穿越联接删掉正本**。解除只走 `bind_skills.py unbind`（内部 `os.rmdir`）或 `cmd /c rmdir`。

## 四、写法效果的实测证据

这些数字决定了 0002 的契约与待办优先级——**技能写得差是负资产**：

- **长度消融（SkillsBench）**：compact 正文 +18.0pp，standard +21.5，detailed +14.5，**comprehensive +0.7**。
- **数量消融**：单技能 +18.0，2–3 个 +19.0，**≥4 个只 +10.1**。
- **自造技能**：用 skill-creator 批量生成的落在**无技能基线以下**（−8.1 到 −11.5pp），87 个任务中 13 个负 delta。三个成因之一是"自信但错误的 gotcha 会变成承重结构"。
- **公开技能库**：SWE-Skills-Bench 中 49 个公开技能 **39 个通过率零改善**，均值 +1.2%，token 开销最高 **+451%**；退化最高的 3 个技能（−10%）原因写的是"版本不匹配的指引与项目上下文冲突"。对照：curated 技能可从 33.9% 提到 50.5%。
- **失败归因**：307 例技能致因失败里**最大单一原因是过度验证（67 例）**，第二是重型实现流水线（30 例）。

三条一手对照结论（来自 superpowers 的 writing-skills 记录）：

1. **描述里不要有流程摘要**。实测：描述写了 "code review between tasks"，流程图规定两次 review，实际只跑一次。机制是"描述一旦概括流程，agent 照摘要走、不读正文"——渐进披露陷阱。修法是删掉流程，不是补说明。
2. **产物形状类失败用正面配方，不用禁令**（"Match the Form to the Failure"）：规则被跳过 → 禁令 + 合理化对照表；产物形状错 → **正面配方**（禁令那一组实测反而产出更多不想要的内容）；要素遗漏 → 必填模板槽位；条件性 → 可观测谓词。
3. **过程而非散文**：步骤、检查点、退出条件；给可选步骤标"可选"并提供快路径（SkillsBench 对策原话 *mark optional steps and supply a fast path*）；适用边界要写进描述而非只写偏好流程（*include applicability boundaries, not just preferred procedures*）。

分工规则（mattpocock）：user-invoked 技能负责编排，model-invoked 技能持有纪律；**编排技能不得调用另一个编排技能**，也不得复述被调用技能的内部步骤。

反向也存在：**不写技能也是一种选择**。规范本身给的拆分触发条件是 "When SKILL.md becomes unwieldy, split into separate files"，参考内容按变体切（`references/aws.md` 那种）让 agent 只读到需要的一份。

## 五、装订的三条路线

| | 自建薄脚本（**已采用**） | `npx skills`（Vercel Labs） | rulesync |
|---|---|---|---|
| 机制 | 读 `.agents/skills/`，对声明需要的 target 建 junction | 75+ agent 预设（含 `qoder`/`qoder-cn`/`opencode`），**默认 symlink**，`--copy` 可选，写 `skills-lock.json` | `.rulesync/` 为正本，**materialize 拷贝**到 70+ target，做真格式转换 |
| 是否转换 frontmatter | 会（自己写降级规则） | **不转**，共享同一份 `SKILL.md`，私有字段各 harness 自行忽略 | 转的是 rules/mcp/hooks，**skill 本体不转** |
| Windows | junction 无权限摩擦 | symlink 默认，需开发者模式；失败需 `--copy` | 拷贝，无摩擦 |
| git | 链接不进 git，脚本进；一行 `bind` 重建 | lock 可提交、可复现 | 拷贝可提交，但 N 技能 × M target 进 git，diff 噪音大 |
| 成本与风险 | 一个脚本 + 自己维护它对路径的假设 | 依赖外部项目节奏；不解决 R2/R4 的作者约束 | 最重，引入构建步骤混进 Hugo 流程 |

选自建的依据是需求形状匹配：五个 harness、一个仓库、junction 够用。`npx skills` 的价值在"从 GitHub 装别人的技能"——那是另一个需求，日后真要引入外部技能包时可与本方案并存（它的 lock 与我们的 canonical 目录不冲突）。

## 六、验收方法：每个 harness 三个观测点

不能只看"文件在不在"。三档强度不同，**第 2、3 条本仓库至今未跑过**：

| 观测点 | 方法 | 已知风险 |
|---|---|---|
| **出现** | `/skills` 列表或 `@`/`/` 面板；OpenCode 直接问"你有哪些 skill 可用"。Qoder 侧用**探针法**：临时建一个技能看下一轮是否出现在清单里，验完删除 | 联接是否可穿越 → 已验证可（2026-10-26 双向观测，且证明 Qoder 每轮重扫、无需重启会话） |
| **触发** | 只说 3 个触发关键词、不提 skill 名，看是否自动选中 | 描述尾部被截；正文写了"何时用"但没进 description |
| **执行** | 跑一个带脚本的（`rename-blog-filenames`），确认脚本被真执行且中文文件名未被破坏 | OpenCode 只读不执行（agent 用 shell 跑）；dsh 未知；PowerShell 默认编码会毁掉 UTF-8 中文 |

另两条结构性风险：**渐进披露不是免费的**——Claude Code 一旦选中技能，正文会留在上下文里，多个技能叠加后长正文比长描述更贵；**跨 skill 共享资料是反模式**——别为了 DRY 做 `references/common.md` 被多个技能引用（社区里已有只装单个技能就缺共享资料的真实报错），共享部分复制进各自目录。

## 七、范围外

不认 `SKILL.md` 的工具（Aider 靠 `CONVENTIONS.md` + `--read` 注入，Continue 用 `rules/` + `.prompt.md`）：在"写一次 IR"的约束下，它们的成本是**一个输出格式**而不是重写——把 `description` + 正文内联成扁平 rule 文本，丢掉 `scripts/` 并注明需手动执行。只要 R3（触发句进 description）不破坏，这个后端是纯机械的。当前不实现，只作为该约束存在的理由。
