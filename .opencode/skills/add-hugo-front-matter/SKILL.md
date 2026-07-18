---
name: add-hugo-front-matter
description: Add Hugo front matter to new content markdown files that do not already contain front matter, using this repo's standard fields such as title, date, lastmod, draft, categories, tags, and slug.
---

# SKILL: Add Hugo Front Matter

为 `content/` 下尚未包含 front matter 的新 Hugo markdown 文件补充标准 front matter。

## 适用范围

- 仅处理 `content/` 下的 markdown 文件
- 同时适用于普通文章 `.md` 与栏目页/入口页 `_index.md`
- 若用户未明确允许，不要修改 `content/` 以外的文件
- 仅在目标文件当前**没有** front matter 时执行；若文件已包含 front matter，则跳过，不负责覆盖或规范化

## 标准字段

`date` 和 `lastmod` 必须使用**创建/修改时的实际当前时间**，精确到分/秒（例如 `2026-07-15T14:30:00+08:00`），不要写死为固定值。

当标题较长时，可额外添加 `shorttitle` 字段用于网页显示（如列表、卡片等），模板会优先使用 `shorttitle`，若未设置则回退为 `title`。

普通文章建议使用：

```yaml
---
title: "完整文章标题"
date: <当前实际时间>
lastmod: <当前实际时间>
draft: false

categories:
  - "AI Study"
tags:
  - "Tag A"
  - "Tag B"

slug: "stable-url-slug"

# shorttitle: "精简标题"  # 可选，用于网页显示，省略时默认显示 title
---
```

栏目页或 `_index.md` 建议使用：

```yaml
---
title: "栏目标题"
date: <当前实际时间>
lastmod: <当前实际时间>
draft: false

categories:
  - "Section"
tags:
  - "Blog"

slug: "section-slug"
---
```

## 字段约定

1. `title`
   - front matter 中的 `title` 是标题的单一事实来源
2. `shorttitle`（可选）
   - 用于网页显示的简短标题，当完整标题过长时可设置此字段
   - 模板渲染优先级：`shorttitle` > `title`
   - 若未设置，网页默认使用 `title`
3. `date`
   - 表示创建时间，使用创建时的实际时间
3. `lastmod`
   - 表示最近一次重要修改时间，使用修改时的实际时间
4. `draft`
   - 发布控制，默认使用 `false`，除非用户明确要保留草稿
5. `categories`
   - 使用较稳定、较宽泛的分类，如 `AI Study`、`Communication`、`Organizational Behavior`
6. `tags`
   - 使用更细粒度主题词，如 `RAG`、`AWS`、`Architecture`
7. `slug`
   - 推荐添加，用于稳定、可控的 URL

## 内容结构规则

1. 若文章已经有 front matter，则直接跳过，不做补齐、覆盖或规范化
2. 若文章没有 front matter，则在文件顶部新增
3. 对普通文章，新增 front matter 后，通常应移除正文顶部重复的 `# 标题`，使 front matter `title` 成为单一事实来源
4. 若新增 front matter 后，正文中紧跟着存在多余的分隔线（例如标题后单独一个 `---`），应一并清理
5. 若需要新增的 `title` 与正文 H1 明显冲突，先询问用户

## 执行要求

1. 先读取目标文件，确认其当前没有 front matter
2. 仅对缺少 front matter 的文件新增标准字段
3. 若分类、标签或 slug 不明确，先给出建议并询问用户
4. 修改后确保 markdown 结构仍然合法，front matter 位于文件最顶部

## 注意事项

1. 该技能只负责为缺少 front matter 的新文件新增标准 front matter，不负责重命名文件，也不负责批量规范化已有 front matter
2. `toc` 不作为默认字段，因为当前 Docsy 主题通常已处理目录显示
3. `showBreadcrumbs` 不作为默认字段，因为当前仓库没有证据表明它已被使用或依赖

## 编码安全（重要历史教训）

**绝对禁止使用 PowerShell 的 `Get-Content` / `Set-Content` 读取或写入含中文的 markdown 文件，除非明确指定 `-Encoding UTF8`。**

### 事故复现路径（避免重犯）

1. 用 `Get-Content -Path $file -Raw`（无 `-Encoding UTF8`）读取 UTF-8 中文件
2. PowerShell 使用系统 ANSI 代码页（中文 Windows 下为 GBK）解码文件字节
3. 字节边界在 GBK 与 UTF-8 之间错位，产生乱码（mojibake）
4. 用 `Set-Content -Path $file -Value $data -Encoding UTF8` 写回
5. 乱码被持久化到磁盘，原始 UTF-8 字节永久丢失

### 为什么无法通过编码转换修复

- UTF-8 使用 1-4 字节变长编码，GBK 使用 1-2 字节变长编码
- 文件被误读为 GBK 后，3 字节的 UTF-8 序列被拆解为 2 字节的 GBK 字符序列
- 重新编码为 GBK 再解码为 UTF-8 时，字节边界无法对齐，产生无效 UTF-8 序列
- 部分乱码字符落入 GBK 未定义的私有使用区（PUA, U+E000-U+F8FF），根本无法编码回 GBK
- **结论：一旦乱码，不可逆修复。唯一恢复途径是从原始备份、读取记录或 git 历史还原。**

### 正确的操作方式

```powershell
# ✅ 正确：读取 UTF-8 文件
Get-Content -Path $file -Raw -Encoding UTF8

# ✅ 正确：写入 UTF-8 文件
Set-Content -Path $file -Value $data -Encoding UTF8

# ✅ 更安全的字节级操作
$bytes = [System.IO.File]::ReadAllBytes($path)
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($text))
```

```python
# ✅ Python 始终正确
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```

### 最佳实践

- **优先使用 `edit` 工具**修改含中文的 markdown 文件，它读写 UTF-8 正确
- **优先使用 Python**处理文件 I/O，`open(path, 'r', encoding='utf-8')` 始终可靠
- **如需使用 PowerShell**，每次读取和写入都显式指定 `-Encoding UTF8`
- **恢复乱码**的唯一可靠途径：从 conversation 中的读取记录（read tool output）重建正文
