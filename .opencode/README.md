# OpenCode Guide

This folder contains repo-local OpenCode skills for maintaining this Hugo blog.

## Purpose

These skills capture repeatable repo-specific workflows so content changes stay consistent.

## Available Skills

### `add-hugo-front-matter`

Use this when a new content file under `content/` is missing Hugo front matter.

Main use cases:
- add `title`, `date`, `lastmod`, `draft`
- add `description`, `summary`
- add `categories`, `tags`, `slug`
- remove duplicate top-level H1 when front matter `title` is the single source of truth

Not for:
- rewriting files that already have front matter
- bulk normalization of old metadata

### `rename-blog-filenames`

Use this when filenames under `content/blog/` are not aligned with the document title.

Main use cases:
- rename bad filenames like numeric placeholders
- preserve ordering prefixes such as `01_` or `CH03_02_`
- keep semantic separators in Chinese titles
- update links after renaming

Title source rule:
- prefer H1 when present
- if H1 is missing, use front matter `title`
- if both exist and disagree, ask the user

### `sync-subfolder-links`

Use this when `_index.md` files under `content/blog/` need to reflect the files and subfolders beside them.

Main use cases:
- scan all `_index.md` files under `content/blog`
- add missing links to sibling markdown files
- link subfolders via `./subfolder/_index.md` when that file exists
- if a subfolder has no `_index.md`, ask the user to choose:
  - one file in that subfolder as the target, or
  - pure text with no link

## Recommended Sequence

For new or migrated content, the normal order is:

1. Add or normalize front matter with `add-hugo-front-matter`
2. Rename blog files if needed with `rename-blog-filenames`
3. Sync section links with `sync-subfolder-links`

Why this order:
- front matter may become the title source when H1 is missing
- renaming should happen before link syncing so section links point to final filenames
- `_index.md` updates are most reliable after filenames and metadata settle

## Scope Rules

- Content changes should stay under `content/` unless the user explicitly allows other files
- Hugo section link maintenance lives under `content/blog/`
- File renaming and front matter normalization are separate workflows and should stay separate

## Notes

- This repo uses Hugo with Docsy
- `slug` is recommended as part of standard front matter
- `toc` is not a default field here because Docsy usually handles TOC already
- `showBreadcrumbs` is not a default field here because this repo does not currently depend on it
