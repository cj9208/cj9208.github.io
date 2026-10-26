---
name: sync-subfolder-links
description: Update markdown index files so they include links to markdown files in matching subfolders, using filesystem-derived names and safe handling of special Unicode filenames. Also reads the overview-articles registry and reports which new articles should be considered for linking into registered 综述类文章 (overview/survey articles).
---

# SKILL: Sync Subfolder Links

将 `content/blog` 下各层级目录中的 `_index.md` 作为目录入口页，并为同目录下的文件或子目录补充链接。
同时维护**综述类文章（总纲/综述）**：当新文章落入综述类文章的覆盖目录时，判断是否把它加入综述正文。

## 逻辑

1. 扫描 `content/blog` 及其子目录
2. 找到所有 `_index.md`，这些文件是当前应维护目录内容链接的位置
3. 对于每个 `_index.md` 所在目录，扫描同目录下的文件和子目录
4. 处理同目录下的普通文件：
   - 仅处理 `.md` 文件
   - 跳过当前 `_index.md`
   - 如果尚未在当前 `_index.md` 中被链接，则添加链接
   - 链接格式为 `* [文件名]({{< relref "./文件名.md" >}})`，显示文本使用不带后缀的文件名
5. 处理同目录下的子目录：
   - 查找该子目录下是否存在 `_index.md`
   - 若存在且尚未在当前 `_index.md` 中被链接，则直接链接到对应 `_index.md`
   - 默认链接格式为 `* [文件夹名]({{< relref "./子文件夹/_index.md" >}})`
   - 只有当该子目录中不存在 `_index.md` 时，才进入备用选择
   - 备用选择包括：让用户在该子目录中选择一个文件作为链接目标，例如 overview/introduction 页面；或改为纯文本，不添加链接
6. 处理**综述类文章候选**（见下方「综述类文章（总纲/综述）链接」章节）：读取 `overview-articles-registry.md`，若 scope 内文章位于某篇综述类文章的覆盖目录且综述正文尚未引用它，则报告为候选
7. 若链接是否应加入、加入到哪个位置或分组方式不明确，先询问用户

## 综述类文章（总纲/综述）链接

**综述类文章** = 以"总纲 / 综述 / 系统梳理"为形态的文章，正文通过链接汇总、串联本站其它文章。例如《威权治理系统总纲：从历史大分流到终局死锁》（`content/blog/systems_and_governance/Chinese_government/`）。

### 注册表

已识别的综述类文章维护在注册表文件 **`.opencode\skills\sync-subfolder-links\overview-articles-registry.md`**（仿照 `add-hugo-front-matter/tags-registry.md` 的维护方式）：

- 每个综述类文章一个 `### ` 小节，字段：
  - `- 目录:` 综述文章所在目录（仓库相对路径）
  - `- slug:` 综述文章 front matter 的 `slug`（脚本据此匹配文件，避免依赖中文文件名）
  - `- 覆盖目录:` 该综述覆盖的文章目录，可多行
  - `- 链接格式:` 正文内添加链接时的格式
- 发现新的综述类文章时，应追加到注册表对应分组，保持注册表同步。

### 逐篇判断：当前文章是否为新综述类文章

不需要单独的全站扫描。每次 `add-links-for-scope.py` 处理 scope 内的文章时，会逐篇判断**该文章自身**是否可能是综述类文章（依据：正文引用站内文章数量较多，或标题/slug 命中 总纲/综述/导论/概论/合集/Overview 等关键词），输出 [疑似综述类文章，待登记] 报告。

- 对每个疑似项，**通读文章确认**是否真是综述类文章（形态标准：以"总纲 / 综述 / 系统梳理"汇总串联其它文章）。
- 注意：站内链接多只是辅助信号，普通文章也可能引用很多站内文章（如《48小时周均工时悖论》有 9 个站内链接但并非综述）。
- 确认为综述类文章后，按上文「注册表」格式把该文章追加到 `overview-articles-registry.md`，并同步更新 `lastmod`（若修改了 `content/` 下文章）。
- 已登记在注册表中的综述类文章不会再出现在该报告中。

### 脚本行为

`add-links-for-scope.py` 每次运行会读取注册表并输出两类报告：

1. **[疑似综述类文章，待登记]** —— scope 内文章自身可能是综述类文章但尚未登记。通读确认后按「注册表」格式追加到 `overview-articles-registry.md`。
2. **[综述类文章候选]** —— scope 内文章位于某篇已登记综述的覆盖目录、但综述正文尚未引用。候选的**是否加入、放在哪个主题分节属于编辑判断**，脚本只报告、不自动写入；对每个候选给出其仓库相对路径、目标综述文章路径，以及注册表里配置的链接格式（通常为公开链接）。

确认后使用 `edit` 工具手工在综述正文对应分节添加链接（正文内引用本站文章**必须使用公开链接**，见 AGENTS.md 链接规则，不要用 `{{< relref >}}`）。

### 注意事项

- 覆盖目录命中仅代表"所在位置匹配"，真正是否加入需结合主题与综述正文的分节结构判断，必要时询问用户。
- 综述类文章本身不参与自身的候选报告。

## 脚本

```bash
# 验证所有 _index.md 中的 relref 链接是否指向真实文件
python .opencode\skills\sync-subfolder-links\scripts\verify-links.py
```

**由 `pipeline-blog-init` 调用时**，使用 `add-links-for-scope.py` 只处理未 push 的新文件，不重扫全站：

```bash
# 报告：哪些 scope 内文件还没被所在目录的 _index.md 链接
python .opencode\skills\sync-subfolder-links\scripts\add-links-for-scope.py --scope <scope文件>

# 确认后实际写入缺失链接
python .opencode\skills\sync-subfolder-links\scripts\add-links-for-scope.py --scope <scope文件> --apply
```

`--scope` 接收一个 UTF-8 文件，每行一个仓库相对路径（由 `pipeline-blog-init/scripts/compute-scope.py` 生成）。该脚本对每个 scope 内的普通文章，找到同目录的 `_index.md`，若尚未包含对该文件的 relref 链接则补上（默认插到第一个 `## ` 标题前）。

**单文件模式**：逐个审阅文章时，用 `--file` 只为指定文章补链：

```bash
# 报告：该文章是否已被所在目录 _index.md 链接
python .opencode\skills\sync-subfolder-links\scripts\add-links-for-scope.py --file content/blog/<目录>/<文件名>.md

# 确认后实际写入缺失链接
python .opencode\skills\sync-subfolder-links\scripts\add-links-for-scope.py --file content/blog/<目录>/<文件名>.md --apply
```

`--file` 接收一个仓库相对路径，内部等价于单元素 scope。

> **注意**：`--apply` 是机械插入，插入位置可能不理想（例如应放进特定分组）。执行后务必检查对应 `_index.md` 的分组归属，必要时用 `edit` 工具手工调整。若文章所在的目录没有 `_index.md`，该文件会被跳过并在报告中体现。

## 注意事项

### 核心原则：始终从文件系统读取文件名，切勿手动输入或字符串匹配

### 编码安全：所有文件读写必须使用 UTF-8

本技能需要读取和写入 `_index.md` 文件（含中文），必须正确使用 UTF-8 编码：

- **不要用 PowerShell `Get-Content` 的默认编码**——默认使用 ANSI(GBK)，会破坏 UTF-8 中文。
- **始终使用** `Get-Content -Path $file -Raw -Encoding UTF8` 和 `Set-Content -Path $file -Value $data -Encoding UTF8`。
- **Python 始终正确**——使用 `open(path, 'r', encoding='utf-8')` / `open(path, 'w', encoding='utf-8')`。
- **`edit` 工具最可靠**——读写 UTF-8 始终正确，优先使用。

### 核心原则：始终从文件系统读取文件名，切勿手动输入或字符串匹配

文件名中若包含特殊 Unicode 字符时，即使肉眼看起来一样，手动输入的字符与文件系统实际存储的字符在字节层面可能不同。

**关键经验：**
1. 禁止手动输入含特殊字符的路径，始终从文件系统获取
2. 显示文本使用不含扩展名的文件名，或文件夹名本身
3. 目录链接优先基于子目录下的 `_index.md`
4. 只有当子目录不存在 `_index.md` 时，才向用户确认应链接到哪个文件，或是否改为纯文本

## 执行要求

1. 先扫描 `content/blog` 并读取所有现有 `_index.md`
2. 仅在缺失链接时补充，不要重复添加
3. 不再负责文件名清洗、规范化或重命名，这部分由独立技能处理
4. 如果链接位置、分组、归类不明确，或子目录缺少 `_index.md` 需要备用目标时，先向用户确认再修改
5. 修改后验证所有新增链接都指向真实文件或真实子目录入口
6. 每次运行 `add-links-for-scope.py` 后，检查输出的**综述类文章候选**：对每个候选，结合主题与综述正文分节结构判断是否加入，必要时询问用户；确认后手工用 `edit` 工具添加公开链接
7. 若发现新的综述类文章，将其追加到 `overview-articles-registry.md`，保持注册表同步

## 待处理清单（上次遗留）

以下子目录因缺少 `_index.md` 被跳过，下次执行时需确认是否补齐：

- `AI_study/aws-solution-architect-notes/`（13 篇 AWS 笔记，无 `_index.md`）
- `AI_study/rag-orchestration-architecture/`（11 篇 RAG 架构文章，无 `_index.md`）
