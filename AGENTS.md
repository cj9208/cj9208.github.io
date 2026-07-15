# AGENTS.md

## Repo purpose
Personal blog site rendered with Hugo and deployed to GitHub Pages.

## Site structure
- Hugo content lives under `content/`.
- Supplemental static assets and standalone files live under `static/`.
- Hugo configuration is in `hugo.toml`.
- Deployment is handled by `.github/workflows/hugo.yml`.
- Do not modify files outside `content/` and `static/` unless the user explicitly gives permission.

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

## Key rule: Chinese filenames with special Unicode
Never type literal Chinese filenames (especially those containing `"`, `'`, `「`, `」`) in code or scripts. Always read from filesystem via `Get-ChildItem` / `os.listdir` and use keyword matching (`-match` / regex) instead of exact string comparison.

This is the **single most common mistake** to avoid in this repo.
