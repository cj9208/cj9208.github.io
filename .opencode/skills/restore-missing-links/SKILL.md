---
name: restore-missing-links
description: Restore references that lost their links during content migration. Replaces broken placeholder links (google.com/search?q=%23, bare [bracket]) and finds unlinked article-title mentions across blog content via title reverse-search. Use when reference links are dead, when an article's Reference section lost its links, or after migrating content into content/blog.
---

# SKILL: Restore Missing Links

在内容迁移后，引用链接经常丢失：有的变成 `https://www.google.com/search?q=%23` 占位符，有的只保留标题文字而链接被丢弃，还有的变成 `[标题]` 没有 URL。本技能用于系统性地找回并补齐这些链接。

## 背景：链接方案

- 站点 URL 结构：`https://cj9208.github.io/blog/<section>/<slug>/`，slug 已固定，绝对 URL 稳定不变。
- 引用链接统一使用**绝对 URL**（VSCode 中可点击跳转，构建期不解析）。
- section 落地页（`_index.md` 渲染页，标题短如"投资"）会污染标题搜索，必须排除。
- 每处引用匹配的判定：文章完整标题的归一化片段（引号 `「」`/`""`/`《》`、空白差异全部归一），主标题片段作为兜底。

## 扫描范围参数（scope）

所有扫描脚本（`scan_broken_links.py`、`find_references.py`、`find_missing_references.py`）都接受 `--scope` 参数：

- **`--scope auto`（默认）**：只扫描"还没有 push 到 origin 的本地改动"，范围 = 三类的并集：
  - `stash`：stash 里暂存的改动（`git stash list` + `git stash show`）。
  - `commits`：已 commit 但未 push 的提交（`git log origin/<branch>..HEAD`）。
  - `worktree`：工作区/暂存区的未提交改动（`git status --porcelain`）。
- **`--scope full`（全量）**：扫描 `content/blog` 下全部文章，无视 git 状态。
- 也可精确指定某一类来源：`--scope stash`、`--scope commits`、`--scope worktree`。

行为约定：
- **除非用户明确说"全量"**（`--scope full`），一律用默认 `auto`，只处理本地未 push 的改动，避免把已上线文章的存量问题拖进本次改动。
- 已存在文章的标题清单（标题反查的 inventory、已知标题集合）始终从全量内容构建，这样改动文件引用到任何文章（含未改动的）都能被找到。
- 过滤依据是 `git_scope.changed_files(ROOT, scope)` 返回的仓库相对路径（POSIX `/` 分隔）。Git 输出已通过 `-c core.quotepath=false` 保留原始 UTF-8 中文路径。
- 扫描脚本对 `content/`、`static/` 之外的文件（如 `zhihu-column-*.md`、`_index.md`、`progress.md`）自然无感。

## 工作流

1. **扫描失效链接**：找出所有 `google.com/search` 占位、空链接、裸 `[标题]` 无 URL 等（默认只扫本地未 push 改动）。
2. **构建站点**：先 `hugo --gc --minify` 生成 `public/`（标题反查依赖已构建产物）。
3. **标题反查**：找出正文/Reference 里以纯文本出现的其他文章标题（无链接的潜在引用），输出候选报告（默认只扫本地未 push 改动）。
4. **缺失文章清单**：找出"被引用但站内无对应文章"的标题（漏迁移），生成 `missing-references.md` 供排查（默认只扫本地未 push 改动）。
5. **人工审阅**：检查候选报告，剔除误报（泛化短语、section 标题、自身章节标题撞名），生成 `candidates.json`。
6. **批量加链**：对审阅后的候选批量包裹链接并更新 `lastmod`。
7. **手动兜底**：批量脚本无法处理的（bold 分拆标题、连字符标题、行号漂移）用 `edit` 工具逐个处理。
8. **验证**：重跑扫描脚本 + `hugo` 构建，确认无残留。

## 脚本

```bash
# 扫描范围：默认 auto（只扫未 push 到 origin 的本地改动）；全量用 --scope full
# 也可以精确指定来源：--scope stash / --scope commits / --scope worktree

# 1. 扫描失效/占位链接
python .opencode\skills\restore-missing-links\scripts\scan_broken_links.py

# 2. 先构建站点（必须）
hugo --gc --minify

# 3. 标题反查，输出 references_report.json / references_report.txt 到当前目录
python .opencode\skills\restore-missing-links\scripts\find_references.py

# 4. 缺失文章清单（漏迁移排查），输出 missing-references.md 到仓库根目录
python .opencode\skills\restore-missing-links\scripts\find_missing_references.py

# 5. 人工审阅 references_report.txt，生成 candidates.json：
#    [{"source": "content/blog/xxx.md", "line": 12, "title": "<完整标题>", "url": "https://cj9208.github.io/blog/..."}]
#    line 为 body 相对行号（front matter 之后），仅作提示，匹配失败时脚本会全文件回退搜索

# 6. 批量加链 + 更新 lastmod
python .opencode\skills\restore-missing-links\scripts\apply_links.py candidates.json

# 7. 验证：重跑 1、3 和 4，确认 0 残留；再 hugo 构建确认成功
```

## 加链规则（apply_links.py）

- 常规：`标题` → `[标题](绝对URL)`，相邻 `《》` 保留在外侧。
- 裸括号：`详见：[标题]`（有 `[` 无 `(url)`）→ 在 `]` 后追加 `(url)`。
- 同一行多处引用（如"本篇是《A》、《B》及《C》的后续"）→ 逐个包裹。
- 匹配采用**柔性正则**：引号类字符可替换、`：`/`:`/`—` 可互换、空白可变。

## 注意事项

### 标题匹配的坑

- **引号变体**：来源 `「工单驱动」` vs 文中 `"工单驱动"`，需归一化后再匹配。
- **部分标题（历史遗留）**：文中可能用 `《神话的黄昏》`、`《深度解构》` 这类缩写，主标题片段兜底可部分命中，但仍有漏网，需要人工配合。
- **泛化短语误报**："深度解构""从第一性原理出发""投资"等作为主标题片段时到处都是，必须用完整标题片段优先（HIGH），主标题片段仅在有 `《》`/加粗包裹时采用（MED）。
- **bold 分拆标题**：`**主标题：** 副标题（注解）` 结构（如 48小时 文章"相关阅读"），正则跨不过 `**`，需人工用 `edit` 处理：`**[完整标题](url)**（注解）`。
- **连字符代替冒号**：如 `《混沌中的信任重构-从拜占庭将军...》`，可把 `：`/`-` 归为一类。
- **标题前有前缀**：如 `《人口老龄化与养老金问题缩水的血包...》` 实际标题是"缩水的血包..."，用柔性正则包裹标题子串即可，前缀留在外面。

### 编码安全（关键）

- 一律用 Python `open(..., encoding='utf-8-sig')` 读取 content 下的 `.md`（`utf-8-sig` 会剥掉 UTF-8 BOM，BOM 文件用 `utf-8` 读会导致 `startswith('---')` 失败、front matter 不剥离、标题自匹配误报）。
- 写文件用 `open(full, 'w', encoding='utf-8', newline='')`，保持 LF 行尾（会顺带去除 BOM，可接受）。
- **禁止**用 PowerShell `Get-Content`/`Set-Content` 默认编码（ANSI/GBK 会破坏 UTF-8 中文，不可逆）。
- 优先用 `edit` 工具做手动修改（读写 UTF-8 始终正确）。

### BOM 的坑（历史踩过）

部分迁移文件带 UTF-8 BOM。读取时若用普通 `utf-8`：
- `text.startswith('---')` 判断失效 → front matter 不被剥离 → 文章标题在自己 front matter 的 `title:` 行自匹配，产生大量"L2"误报。
- 自排除（`src_norm == norm_full`）也失效。
修复：统一 `utf-8-sig` 读取。`apply_links.py` 的 `line` 只是提示，全文件回退搜索天然免疫行号漂移（含 BOM 偏移）。

### 特殊 Unicode 文件名

- 从不手打中文文件名，用 `glob`/`os.listdir` + 关键词匹配从文件系统读取路径。
- 本技能脚本的 `source` 字段用 `os.path.relpath` 生成，天然安全。

### lastmod 维护规则

每次实质修改 `content/` 下文章（含加链接）后，必须把 front matter 的 `lastmod` 更新为当前实际时间，格式 `2026-08-09T09:43:17+08:00`。脚本自动处理；手动 `edit` 时同步更新。

## 执行要求

1. **默认 scope=auto**：只扫描还没有 push 到 origin 的本地改动（stash + 未 push 提交 + 工作区改动）。除非用户明确说"全量"（`--scope full`），否则不要全量扫描。
2. 先跑 `scan_broken_links.py` 和 `find_references.py` 拿到全量事实，再动手改。
3. 候选清单必须人工/受控审阅，剔除误报后再批量应用，禁止无审阅全自动改写。
4. 批量脚本的 FAIL 逐条处理，不要遗漏。
5. 改完后验证：扫描 0 残留 + `hugo` 构建成功。
6. 被引用但站内已无对应文章（迁移丢失）的标题，保留文字并询问用户是否加缺失标注，不要编造链接。
