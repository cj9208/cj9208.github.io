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
