# AGENTS.md

## Repo purpose
Personal blog site rendered with Hugo and deployed to GitHub Pages.

## Site structure
- Hugo content lives under `content/`.
- Supplemental static assets and standalone files live under `static/`.
- Non-blog working notes and drafts live under `notes/` (not rendered by Hugo).
- Hugo configuration is in `hugo.toml`.
- Deployment is handled by `.github/workflows/hugo.yml`.
- Do not modify files outside `content/`, `static/` and `notes/` unless the user explicitly gives permission.
- 例外：`.agents/skills/` 与 `scripts/` 是 agent 工具层（见下"Skill 的唯一真源"），维护它们属于本文件授权范围内的日常工作。

## Skill 的唯一真源：`.agents/skills/`
本仓库的 agent 技能只有一份真实文件，位于 `.agents/skills/<skill-name>/SKILL.md`（含各自的 `scripts/`、`references/`）。这是 git 跟踪的正本。

- **新增或修改 skill，只在 `.agents/skills/` 下做。** 其他 harness 目录都是生成物，不是内容。
- `.qoder/skills` 是一个**目录联接**（junction），指向 `.agents/skills/`，且已被 `.gitignore` 忽略。它由脚本生成，**不要手工编辑里面的文件**——编辑等于编辑正本，但你会以为自己在改副本。
- 装订命令：`python scripts/bind_skills.py bind`（幂等，可重复执行）；`check` 校验正本与绑定状态；`unbind` 安全解除。新克隆仓库后先跑一次 `bind`，Qoder 才有技能可用。
- Codex CLI、OpenCode、DeepSeek Harness 原生读取 `.agents/skills/`，**不需要**任何装订动作。
- **禁止手工创建 `.claude/skills/` 或 `.opencode/skills/`。** OpenCode 项目级会同时扫描 `.opencode/skills`、`.claude/skills` 和 `.agents/skills` 三个根，且要求 skill 名跨根唯一；多一个根就是重名冲突。Claude Code 的接入方式仍是未决项，见 `docs/decisions/0002-skill-authoring-contract-and-backlog.md`（P0-1）。
- ⚠️ **删除风险**：`.qoder/skills` 是链接而非目录内容。在 Git Bash / MSYS 里执行 `rm -rf .qoder/skills` 可能穿越联接**删掉正本**。解除绑定只走 `python scripts/bind_skills.py unbind`（内部用 `os.rmdir` 删重解析点）或 `cmd /c rmdir .qoder\skills`。

## Content structure
- The main site sections live under `content/`, especially `content/blog/`.
- Section landing pages are stored as `_index.md` inside the corresponding folder.
- Section folders are the canonical location for both article collections and their landing-page content.
- `_index.md` is not just a table of contents. It may also contain introductions, notes, navigation guidance, section structure, or other editorial content that improves the section page.
- Article markdown files live alongside or below the section `_index.md` inside the matching folder.

## Editing guidance
- When working on blog content, assume the authoritative source is under `content/`, not the repo root.
- When moving or adding non-rendered support files, place them under `static/` unless there is a Hugo-specific reason to put them elsewhere.
- When editing `_index.md`, preserve any introductory or structural content; do not assume it should be reduced to a pure link list.

## 非 blog 内容的默认位置：`notes/`
凡是**不属于站点发布内容**的文件，默认放到 `notes/`，不要散落在仓库根目录。这样便于集中管理，也避免污染 Hugo 构建。

判断标准：

- 会被 Hugo 渲染、对外发布 → `content/`
- 站点要用到的静态资源（图片、附件、独立 HTML/JS 等，会随站点一起部署）→ `static/`
- 其余一切私人工作产物 → `notes/`
- 但**会改变未来决策的项目级结构决定** → `docs/decisions/`（判据与门槛见下）

`notes/` 下典型的文件包括：选题与大纲草稿、todo 清单（如 `blog-todo.md`）、学习进度与认证笔记、面试与 coffee chat 准备、组织与职业判断的私人记录、以及只在会话间传递、不需要发布的中间分析。

补充约定：

- `notes/` 不参与 Hugo 构建，因此**不受** front matter、`lastmod`、slug 与站内公开链接等发布规则约束。
- 在 `notes/` 下可以用子目录归类（现有的如 `interview/`、`zhimap/`、`archive/`）；新主题文件多时，优先建子目录而不是继续平铺。
- `notes/archive/` 专门记录**讨论过但决定不写**的选题：判断依据、残差清单（哪些组件站内已写过、哪几块是真新的）与重开触发条件。格式见 `notes/archive/README.md`，产生这类结论的流程在 `search-blog-articles` 技能 §4。与 `blog-todo.md` 互补——那里放要写的，这里放决定不写的，避免同一话题几个月后被当成新想法重讨论。
- 文件名仍遵循仓库既有习惯：英文 kebab-case，或中文标题直接使用；含中文或特殊 Unicode 的文件名必须从文件系统读取，不要手写（见下文 Key rule）。
- 当一篇 `notes/` 草稿成熟到要发布时，再迁移到 `content/` 对应栏目，并按发布规则补齐 front matter 与站内链接。

## 项目决策记录：`docs/decisions/`
一句话判据：**这份东西会不会被未来的 agent 或未来的自己拿来支撑决策？** 会 → `docs/decisions/`；其中短到可以 always-on 的部分直接写进本文件。不会、只是过程记录 → `notes/`。

写入门槛（两条**同时**满足才写）：

1. 改变了别人（或未来的你）会依赖的结构或约定；
2. 存在被否决的备选方案。

只"改动很大"不够。批量格式迁移之类的动作写进 commit message 即可，不要每改一次就写一篇记录，否则 `docs/` 会退化成第二份 changelog。

格式：`docs/decisions/NNNN-短横线标题.md`（四位递增编号），固定五段——背景 / 决定 / 被否决的备选 / 后果（含接受的代价与未验证项）/ 被推翻的判断。采纳后不重写正文；被后续事实推翻时新增一篇，在新篇写"取代 000N"，旧篇只加一行状态行。

两条边界：**变更事实不进 `docs/`**——动了哪些文件、怎么回滚，归宿是 commit message（一次提交对应一个逻辑工作项），手工维护一份变更记录等于给 git 已有的信息做第二份拷贝；**决策记录正文不要写进本文件**——本文件每轮注入，把长文塞进来会稀释真正的指令（与官方文档点名的 "bloated CLAUDE.md 会让模型忽略你实际指令" 同一个失效模式），这里只保留判据与指路。

`docs/` 是根目录，Hugo 不渲染（`hugo.toml` 未覆盖 `contentDir`/`staticDir`，workflow 只发布 `./public`；2026-10-26 实测 `hugo --destination public_test` 构建通过、退出码 0，输出目录中无 `docs` 页面），但它在公开仓库里，写的时候按"公开可读"处理。现有两篇：`0001-agent-skill-canonical-directory.md`（正本目录与装订层）、`0002-skill-authoring-contract-and-backlog.md`（技能写作契约 R1–R7 与未完成的优化顺序——**新增或修改 skill 前先读它的"待办"一节**）。

## 链接规则（文章正文用公开链接）
- 文章正文（非 `_index.md` 栏目页）内引用本站文章时，**必须使用公开链接**（`https://cj9208.github.io/blog/<目录>/<slug>/`），不要使用 `{{< relref >}}` 相对路径。
- 公开链接的 `<slug>` 取自目标文章 front matter 的 `slug` 字段；目录层级与 `content/` 下的文件夹一致（如 `systems_and_governance`、`systems_and_governance/chinese_government`、`ai_era_engineering_careers`）。
- **同一篇文章每次提到都加链接，不是只在首次提到时加。** 理由：读者从任意小节进入都应该能直接跳转，不必回滚去找第一次出现的位置；加链接的边际成本接近零，而“首次链接”规则要求读者记住前文、也要求作者在调整段落顺序后重新判断哪一次才算首次。
- 标题过长时可以截短作链接文字（如把《编程语言的终局：从“人肉码农”到“意图流片”》写作《编程语言的终局》），但**截短不等于免链接**。
- 只有本站文章需要这样处理。外部书名、法规与条例名（如《劳动合同法》《雇佣条例》《1984》）不加站内链接，指向官方或权威来源的普通外链即可。
- 例外：仅 `_index.md` 等栏目页内部继续使用 `{{< relref >}}` 相对链接。
- 修改了文章内容后，同步检查文中引用链接是否与目标 slug 保持一致。
- 批量排查漏链接用 `restore-missing-links` 技能（按标题反查未加链接的提及）。

## lastmod 维护规则
每次修改 `content/` 下的文章内容时（包括正文、front matter、标签、分类等实质性变更），**必须同步更新 front matter 中的 `lastmod` 字段**到当前实际时间（精确到分钟/秒），例如 `2026-07-15T14:30:00+08:00`。不要沿用旧的 `09:00:00` 占位时间。

## Key rule: Chinese filenames with special Unicode
Never type literal Chinese filenames (especially those containing `"`, `'`, `「`, `」`) in code or scripts. Always read from filesystem via `Get-ChildItem` / `os.listdir` and use keyword matching (`-match` / regex) instead of exact string comparison.

This is the **single most common mistake** to avoid in this repo.

## CRITICAL: Encoding safety for Chinese content

**PowerShell file I/O destroys UTF-8 Chinese text if `-Encoding UTF8` is omitted.**

- `Get-Content -Path $file` (without `-Encoding UTF8`) uses the system ANSI code page (GBK on Chinese Windows). Reading a UTF-8 file this way corrupts all non-ASCII characters irreversibly.
- `Set-Content / Out-File` without `-Encoding UTF8` also defaults to ANSI, causing data loss.
- **Always use** `Get-Content -Path $file -Raw -Encoding UTF8` and `Set-Content -Path $file -Value $data -Encoding UTF8`.
- For byte-level safety, use `[System.IO.File]::ReadAllBytes($path)` + `[System.Text.Encoding]::UTF8.GetString($bytes)`.

**Python file I/O is safe for Chinese text:**
- `open(path, 'r', encoding='utf-8')` / `open(path, 'w', encoding='utf-8')` works correctly.

**Encoding corruption cannot be reversed.**
- Once UTF-8 bytes are misread as GBK/ANSI and re-saved, the original byte alignment is destroyed. GBK ↔ UTF-8 round-trip fixes fail because byte boundaries differ between the two encodings.
- Recovery is only possible from the original source (backup, read records, git before corruption).

**Prefer the `edit` tool over PowerShell for modifying files with Chinese content.** The `edit` tool reads and writes UTF-8 correctly.
