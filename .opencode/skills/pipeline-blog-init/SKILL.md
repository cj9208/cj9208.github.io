---
name: pipeline-blog-init
description: Run add-hugo-front-matter, rename-blog-filenames, and sync-subfolder-links in sequence, with a git stash as rollback backup.
---

# SKILL: Pipeline Blog Init

Run the three existing content-init skills sequentially on blog content.
Before any modification, create a git stash as a recoverable snapshot so the
user can restore the original state at any time.

## Process

### 1. Stash backup

Save the current working tree (including untracked files) as a named stash:

```bash
git stash push -u -m "pipeline-blog-init: pre-init snapshot"
```

Immediately restore the files so the pipeline can work on them:

```bash
git stash apply
```

The stash entry remains as a backup. If something goes wrong, run:

```bash
git checkout .
git stash apply
```

to restore the original state from scratch.

### 2. Dynamic skill invocation

For each sub-skill **in the following order**, use the `skill` tool to load
the skill, then execute it:

1. `add-hugo-front-matter`
2. `rename-blog-filenames`
3. `sync-subfolder-links`

**Do NOT inline or copy instructions from the sub-skills into this document.**
Always `skill`-load them dynamically so each runs with its own latest
instructions.

### 3. Error handling

If a sub-skill fails (user cancels, script error, etc.), stop the pipeline
and report the failure. Do not continue to the next sub-skill.

If the user asks questions during a sub-skill, resolve them within that
sub-skill before proceeding.

### 4. Completion

After the pipeline finishes, run `git status --short` and show the result
so the user knows what changed.

Remind the user that the pre-init snapshot is still in the stash and can be
restored with:

```bash
git checkout .
git stash apply
```
