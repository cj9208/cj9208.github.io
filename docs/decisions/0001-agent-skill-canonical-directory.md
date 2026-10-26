# 0001. Agent 技能正本迁到 `.agents/skills/`，Qoder 用目录联接装订

- 状态：已采纳
- 日期：2026-10-26
- 事实依据（五个 harness 的路径/字段/预算、Windows 联接、三条路线对比）：[../research/2026-10-26-agent-skill-harness-support.md](../research/2026-10-26-agent-skill-harness-support.md)
- 写作契约、遗留债务与优化顺序：[0002-skill-authoring-contract-and-backlog.md](./0002-skill-authoring-contract-and-backlog.md)

## 背景

本仓库的 19 份 agent 技能原先以 `.opencode/skills/` 为实体、`.qoder/skills` 是指向它的符号链接。跨 harness 的目录约定不一致：Codex CLI、OpenCode、DeepSeek Harness 原生读 `.agents/skills/`，而 Qoder 只读 `.qoder/skills/`，Claude Code 只读 `.claude/skills/`。目标是换成一个 harness 中立的中性正本目录，让切换工具不再需要改内容。

## 决定

1. **正本目录 = `.agents/skills/`，git 跟踪，唯一可编辑的位置。** 通过 `git mv .opencode/skills .agents/skills` 完成，历史保留。
2. **`.qoder/skills` 由脚本生成，是目录联接（junction），gitignore 忽略，禁止手改。** 命令：`python scripts/bind_skills.py bind`（幂等；另有 `check` / `unbind`）。
3. **Codex / OpenCode / DeepSeek Harness 不做任何装订动作**，它们原生扫 `.agents/skills/`。
4. **`.opencode/` 目录整体删除**（含 61MB 的 `@opencode-ai/plugin` bootstrap 产物，git 从未跟踪；OpenCode 下次在本仓库启动会自行重建）。其中唯一被跟踪的 `README.md` 先 `git mv` 成 `.agents/skills/README.md`，改写为 harness 中立的技能索引。
5. **`.gitignore` 删掉 `.opencode/node_modules` 一行**（目录已不存在，且 `node_modules/` 一行本就覆盖它）。

## 被否决的备选

- **`npx skills`（Vercel Labs，75+ agent 预设）**：它的价值在"从 GitHub 装别人的技能"，与本项目"一份自有技能、五个 harness"的需求不同；且默认 symlink 在本机需要提权（实测 `os.symlink` 返回 WinError 1314），而它不做 per-harness 的 frontmatter 处理。日后要引入外部技能包时再引入，与本方案不冲突。
- **rulesync**：会做真格式转换（rules/mcp/hooks），代价是引入一个构建步骤混进 Hugo 流程，且 19 份技能 × N 个 target 的拷贝进 git，diff 噪音大。
- **给 Claude Code 也建 `.claude/skills` 联接**：OpenCode 项目级会同时扫 `.opencode/skills`、`.claude/skills`、`.agents/skills` 三个根并要求技能名跨根唯一，多一个内容根就是重名源。接入 Claude Code 仍是未决项（0002 待办 P0-1）。
- **维护 per-harness 拷贝**：任何一份能被独立编辑的拷贝都会漂移，这是本方案要消除的对象。

## 后果

接受的代价：多了一个 `scripts/bind_skills.py` 需要维护；新克隆仓库后必须先跑一次 `bind`，否则 Qoder 无技能可用；`.qoder/skills` 变成重解析点后，`rm -rf .qoder/skills` 在 Git Bash/MSYS 下可能穿越联接删掉正本——**目前只用文档约束（AGENTS.md 与本文件）而非机制约束**，这是一笔显式欠账（0002 待办 P0-3）。

已验证：联接可被 harness 读取——用一次性探针技能做了双向观测（新建 `junction-probe/` 后下一轮出现在可用技能清单，删除后下一轮消失），顺带证明 Qoder 每轮重扫、新技能无需重启会话。`bind`/`check`/`unbind` 往返与幂等测试全绿。

未验证：没有任何 harness 真跑过一次"只说触发词、不提技能名"的自动触发；带脚本的技能未在新路径下执行过；OpenCode / Codex / dsh 三侧"能列出 19 条"仍是读文档得出的结论。

## 本次被推翻的两条判断（留证，避免重犯）

1. **"两份拷贝已经漂移"为假。** 我先前用目录级 diff 得出 `.qoder/skills` 与 `.opencode/skills` 中某技能内容不同，据此论证"手工维护多份拷贝必然漂移"。实际 `.qoder/skills` 自 2026-09-24 起就是指向后者的链接，一直是同一棵树，那条 DIFF 是比对方法的假阳性。原理仍成立，只是本仓库此前没踩这个坑。副产品是好的：它实证了 Qoder 跟随链接目录。
2. **技能体积把 UTF-8 字节当成了字符**（中文 3 字节/字）。按规范的 500 行 / 5000 token 红线，19 份技能全部在范围内；"落在 detailed→comprehensive 衰减区间"以及"description 过长会被 Claude 1536 / Codex 2% 预算截尾"两条结论一并撤回（实测最长描述 497 字符，无一超 500）。

教训是一条可复用的规则：**结论里的每个数字都要说明它是什么单位、怎么来的。** 上面两条错误都不是判断力问题，是把 `wc -c` 当成了字符数、把目录名比对当成了内容比对。
