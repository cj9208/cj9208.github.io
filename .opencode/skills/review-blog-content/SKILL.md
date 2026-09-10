---
name: review-blog-content
description: Review blog articles under content/blog by first classifying the article type (argumentative, experiential, case post-mortem, survey/overview, technical), then applying type-specific quality standards; assess relevance to existing articles and needed cross-references; then fix front matter, filename, and index-link compliance and verify the Hugo build. Use when reviewing a new or draft article, or when asked to analyze a post's quality, logic, or relationship to other posts before publishing.
---

# SKILL: Review Blog Content

审阅 `content/blog/` 下的一篇（或多篇）文章：**先判定文章类型**，按类型选择对应的质量与证据标准（避免用论证型标准去衡量体感文，反之亦然），再评估与站内其他文章的关联与互引需求，最后修复合规问题（front matter、命名、索引链接），并验证 Hugo 渲染。

## 〇、先判定文章类型（决定后续标准）

审阅前先通读一遍，判定文章属于下列哪一类。类型决定**证据门槛**、**审阅重点**与**引用位置策略**；判错类型是本 skill 最常见的错误来源（例如拿「证据密度不足」去批评一篇本就不打算论证的体感文）。

| 类型 | 识别信号 | 证据门槛 | 审阅重点 |
| --- | --- | --- | --- |
| **论证/分析型** | 提出可检验的命题，用数据/精算/表格/案例/来源支撑；常见结构 现象→解构→后果→破局 | 高：应有具体数据、计算或来源 | 论证链是否闭环、有无偷换概念/循环论证、证据是否支撑断言 |
| **体感/方向型** | 第一人称亲历、作者手记、价值判断或方向倡议，通常无定量 | 低：不要求数据，但经验须具体、不自相矛盾 | 体感是否真切、方向是否立得住、有无空泛口号、经验与论点是否呼应 |
| **复盘/案例型** | 聚焦单一事件/公司/事故，常用 Post-Mortem、根因分析 | 中高：事件事实、时间线、数据 | 事实准确性、根因与表象是否区分、方法论是否自洽、有无过度归因 |
| **综述/总纲型** | 大量站内链接，标题含 总纲/综述/概论/合集/Overview | 不适用（以链接完整为准） | 覆盖面、分节归类是否合理、链接是否有效、阅读路径是否清晰 |
| **技术/方法型** | 步骤、代码块、命令、配置、可复现流程 | 以可运行/可验证为准 | 正确性、可复现性、环境/版本说明、步骤完整性 |

判定规则：

- 一篇文章可同时具备两类特征（如「案例复盘 + 方向倡议」），取**主导**类型，必要时在汇报中说明。
- 类型不明确且影响审阅结论时，先询问用户，不要默认套用论证型标准。
- **不要对非论证型文章套用「证据密度」批判**；同理，对论证型文章不应放过证据缺口。

## 一、质量与逻辑审阅（按类型取标准）

1. 通读文章，先对照上表确定类型，再按该类型的审阅重点逐项检查：
   - **结构**是否清晰（如 现象→逻辑解构→后果→破局 的递进），各部分是否服务于中心论点
   - **中心论点/方向**是否成立、是否自洽，有无偷换概念、循环论证
   - **证据/经验**是否达到该类型门槛（见上表）：论证型看数据、精算、案例、来源；体感型看经验是否具体、是否支撑所提方向；技术型看是否可复现
   - 有无**空泛口号式结论**、未展开的"目录式"要点（只给标题不给论证）——对所有类型都适用
2. 检查**正文杂物**：
   - 是否有遗留的 AI prompt / 编辑说明残留在正文开头（例如"精简并聚焦了…全文重构如下""以下是为您更新后的…"这类行）
   - 是否有未清理的重复分隔线、多余空行、占位文本、笔误

## 二、与已有内容的关联与互引

1. 定位同目录（尤其 `content/blog/<section>/<subsection>/`）以及全站中主题重叠的文章
2. 逐篇判断关联强度：
   - **强关联**：论点同源、同一框架的具体化、同一结论的不同切面 → 必须互引
   - **弱关联**：提供背景数据、支撑性计算 → 建议引用
3. 按关联强度给出引用建议清单（文章标题 + slug），再按下述**引用位置策略**落位
4. **引用位置策略（按类型）**：
   - **论证/分析型、复盘/案例型**：在正文对应位置**内联**引用，让引用服务于论证
   - **体感/方向型**：**优先放在文末「更多阅读」**，避免打断叙述。按主题分组，每条附**一句与本文的逻辑关联**：

     ```
     ## 更多阅读

     **<分组标题>**

     - [《标题》](https://cj9208.github.io/blog/<目录>/<slug>/)：一句话说明它与本文的逻辑关联。
     ```

     若用户明确要求内联，才内联；默认遵循「不打断话题论述」的原则。
   - **综述/总纲型**：在正文对应分节内串联引用
5. 引用规则（遵循 AGENTS.md）：
   - 正文引用必须用公开链接：`https://cj9208.github.io/blog/<目录>/<slug>/`
   - `<目录>` 用 **URL 小写**层级（如 `systems_and_governance/chinese_government`），与 `content/` 文件夹名不一定一致
   - `<slug>` 从目标文章 front matter 的 `slug` 字段取，用 `grep '^slug:'` 批量核对
   - 例外：仅 `_index.md` 栏目页内部用 `{{< relref >}}` 相对链接
6. 检查文中已有链接是否与目标 slug 一致，失效/不一致则修正

## 三、合规修复（依次调用三个子技能，单文件模式）

合规问题修复不需要走 pipeline，**按序加载并执行三个子技能**即可。三个子技能都支持 `--file <仓库相对路径>` 单文件模式：每次只针对当前审阅的一篇文章处理（含其相关改动），避免全站扫描。

1. **front matter**：执行 `add-hugo-front-matter`。用 `find-no-frontmatter.py --file <路径>` 检查目标文件；已有 front matter 时人工核对 title/date/lastmod/draft/categories/tags/slug 是否齐全合法、tags 是否复用受控词表
2. **命名**：执行 `rename-blog-filenames`。用 `propose-renames.py --file <路径>` 生成建议名，用户确认后通过文件系统重命名该文件并同步更新 `content/` 引用
3. **索引链接**：执行 `sync-subfolder-links`。用 `add-links-for-scope.py --file <路径> --apply` 把该文章链入所在目录 `_index.md`；已有链接则核对显示标题与分组是否合理

> 路径统一用仓库相对路径，例如 `content/blog/systems_and_governance/chinese_government/文章.md`。
>
> `sync-subfolder-links` 的 `--apply` 是机械插入，插入位置可能不理想；写完后务必检查 `_index.md` 的分组归属，必要时用 `edit` 手工调整。

4. **lastmod**：任何对 `content/` 下文章的实质性修改，必须把其 front matter `lastmod` 更新到当前实际时间（精确到分钟/秒）

## 四、编码与格式注意（重要）

- 涉及含中文文件时，优先用 `edit` 工具；用 Python 时 `open(..., encoding='utf-8')`；用 PowerShell 必须显式 `-Encoding UTF8`（详见 `add-hugo-front-matter` 的「编码安全」章节）
- **引号字符**：站内文章可能混用弯引号（“ ”）与直引号（"）。编辑前先确认目标文件用哪种，编辑时保持一致。若 `edit` 工具报 "oldString not found"，多半是引号或换行符不符，用字节级检查定位：

  ```python
  pathlib.Path(p).read_bytes().decode('utf-8')
  ```

- **换行符**：文件可能是 LF 或 CRLF。用 Python 修改时保留原换行符（先 `read_bytes` 解码、替换后再 `write_bytes` 写回）
- 文件名含特殊 Unicode 时，不要手动输入路径，用 `Get-ChildItem` / `os.listdir` 从文件系统取并关键词匹配（见 AGENTS.md）

## 五、验证

1. 检查无残留旧文件名引用：`grep "旧文件名" content/`
2. Hugo 构建验证渲染无错误：

   ```bash
   hugo --source <repo根目录> --destination <临时目录> --quiet
   ```

3. 确认页面按预期 URL（`/blog/<目录>/<slug>/`）生成，文中引用链接存在于渲染 HTML
4. 完成后向用户简要汇报：
   - **文章类型**判定及所采用的标准
   - 质量评估结论
   - 关联/互引建议清单（区分已落位与待定）
   - 已做的修复
