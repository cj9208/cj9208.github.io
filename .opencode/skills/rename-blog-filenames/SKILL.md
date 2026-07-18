---
name: rename-blog-filenames
description: Review and rename markdown files under content/blog using the document title from H1 or front matter, semantic separators, preserved ordering prefixes, and link updates with explicit user confirmation for convention changes.
---

# SKILL: Rename Blog Filenames

Normalize markdown filenames under `content/blog/` using the document title while preserving section structure and human readability.

## Scope

- Only operate on markdown files under `content/blog/`.
- Never rename `_index.md`.
- Update markdown references under `content/` after any rename.
- Ask the user for confirmation before applying a second-pass or convention-changing rename.

## Title Source

1. Use the first `# ` heading as the primary filename source when it exists.
2. If the file has no H1, use front matter `title` as the fallback source.
3. If the file has neither H1 nor front matter `title`, stop and ask the user.
4. If front matter title and H1 disagree, treat the file as ambiguous and ask the user before renaming.

## Naming Rules

1. Preserve ordering prefixes when they already exist or are clearly part of the folder structure.
   - Examples: `01_`, `00_`, `CH01_`, `CH03_02_`
2. Remove decorative punctuation instead of blindly converting everything to separators.
   - Examples: quotes, book-title marks, full-width punctuation used only for styling
3. Use `-` only for meaningful structure boundaries.
   - Good examples: title colon boundaries, clearly parallel concepts, major clause breaks
4. Preserve Chinese text naturally.
5. Preserve important acronyms and technical names with their intended casing.
   - Examples: `AI`, `LLM`, `RAG`, `AWS`, `Tit-for-Tat`
6. Remove meaningless spaces.
   - Especially around Chinese and acronym boundaries like `AI 工程` -> `AI工程`
7. Do not over-normalize filenames that are already readable.

## Chinese Punctuation Guidance

- `：` usually becomes `-` because it often separates title and subtitle.
- `，` or `、` should be judged semantically.
  - If they separate parallel concepts, convert them to `-`.
  - If removing them reads better and does not collapse important structure, remove them.
- Decorative quotes such as `“ ”`, `「 」`, `《 》`, `〈 〉` should usually be removed.

## Scripts

```bash
# Step 1: Analyze all files and propose renames
python .opencode\skills\rename-blog-filenames\scripts\propose-renames.py
```

```bash
# Step 2 (after user approval): Execute renames for numbered bare-name files
python .opencode\skills\rename-blog-filenames\scripts\execute-renames.py
```

## Process

1. Scan `content/blog/**/*.md` excluding `_index.md` using `propose-renames.py`.
2. Build a proposed rename list from document titles, using front matter `title` as primary source.
3. Split the results into:
   - high-confidence renames
   - ambiguous cases that need user confirmation
4. Present the proposal to the user before applying if the rename is a second-pass cleanup or changes an existing convention.
5. After approval:
   - rename the files using `execute-renames.py` (for numbered bare-name files) or manually
   - update affected links under `content/`
   - verify that no stale references remain

## Verification

- Search `content/` for references to the old filenames.
- Confirm every renamed path exists.
- Re-check `_index.md` files in affected folders because they usually contain explicit links.

## Repo-Specific Safety

- Do not manually type special Unicode filenames in scripts when an automated filesystem-based approach is available.
- When showing rename proposals to the user, group them by folder and keep the list concise.

## 编码安全（涉及文件读取时注意）

本技能涉及读取文件内容（提取 H1/front matter title）以生成新文件名，需注意：

1. **不要用 PowerShell `Get-Content` 的默认编码读取文件**——它会用 ANSI(GBK) 解码 UTF-8 文件，破坏中文。
2. **`rename` 操作本身不涉及文件内容修改**，但如果先前的操作已导致文件正文编码损坏，重命名不会修复它。
3. **读取正确 UTF-8 中文标题的可靠性排序：**
   - `edit` 工具（最可靠）
   - Python `open(path, 'r', encoding='utf-8')`（可靠）
   - PowerShell `Get-Content -Path $file -Raw -Encoding UTF8`（需显式指定）
4. **只读操作不影响文件内容**，但如果技能流程中包含写入（如修改 `_index.md`），写入也必须使用 UTF-8。
