# AGENTS.md

## Repo purpose
Personal GitHub Pages site (resume + long-form writing). No build step, no CI, no tests, no dev server.

## Content structure
- `README.md` — resume (entrypoint for gh-pages).
- Topic areas follow a paired convention: `Topic.md` (table-of-contents) + `Topic/` subfolder (full articles).
  - `中国政府行为分析/` — the only populated section (8 articles + `analyze_birth.py`).
  - `AI_study/`, `communication/`, `organizational_behavior/` — empty placeholders (root `.md` files are also empty).
- Root `.md` files use `## H2` headings grouping bullet links: `* [title](./Topic/filename.md)`.

## Key rule: Chinese filenames with special Unicode
Never type literal Chinese filenames (especially those containing `"`, `'`, `「`, `」`) in code or scripts. Always read from filesystem via `Get-ChildItem` / `os.listdir` and use keyword matching (`-match` / regex) instead of exact string comparison.

This is the **single most common mistake** to avoid in this repo.

