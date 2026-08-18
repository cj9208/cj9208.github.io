---
name: review-blog-content
description: Review blog articles under content/blog for quality, logical coherence, and evidence density; assess relevance to existing articles and which cross-reference citations are needed; then fix front matter, filename, and index-link compliance and verify the Hugo build. Use when reviewing a new or draft article, or when asked to analyze a post's quality, logic, or relationship to other posts before publishing.
---

# SKILL: Review Blog Content

审阅 `content/blog/` 下的一篇（或多篇）文章：先评估质量与逻辑，再评估与站内其他文章的关联与互引需求，最后修复合规问题（front matter、命名、索引链接），并验证 Hugo 渲染。

## 一、质量与逻辑审阅

1. 通读文章，判断：
   - **结构**是否清晰（如 现象→逻辑解构→后果→破局 的递进），各部分是否服务于中心论点
   - **中心论点**是否成立、论证链是否闭环，有无偷换概念、循环论证
   - **证据密度**：是否用具体数据、精算表、案例或来源支撑断言。对照站内同类文章（涉及社保/债务/财政主题的文章普遍有定量计算与对比表格），若通篇只有断言而无证据，需明确指出
   - 有无**空泛口号式结论**、未展开的"目录式"要点（只给标题不给论证）
2. 检查**正文杂物**：
   - 是否有遗留的 AI prompt / 编辑说明残留在正文开头（例如"精简并聚焦了…全文重构如下"这类行）
   - 是否有未清理的重复分隔线、多余空行、占位文本

## 二、与已有内容的关联与互引

1. 定位同目录（尤其 `content/blog/<section>/<subsection>/`）以及全站中主题重叠的文章
2. 逐篇判断关联强度：
   - **强关联**：论点同源、同一框架的具体化、同一结论的不同切面 → 必须互引
   - **弱关联**：提供背景数据、支撑性计算 → 建议引用
3. 按关联强度给出引用建议清单（文章标题 + slug），并在正文对应位置补引用
4. 引用规则（遵循 AGENTS.md）：
   - 正文引用必须用公开链接：`https://cj9208.github.io/blog/<目录>/<slug>/`
   - `<目录>` 用 **URL 小写**层级（如 `systems_and_governance/chinese_government`），与 `content/` 文件夹名不一定一致
   - `<slug>` 从目标文章 front matter 的 `slug` 字段取，用 `grep '^slug:'` 批量核对
   - 例外：仅 `_index.md` 栏目页内部用 `{{< relref >}}` 相对链接
5. 检查文中已有链接是否与目标 slug 一致，失效/不一致则修正

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
4. 完成后向用户简要汇报：质量评估结论、关联/互引建议清单、已做的修复
