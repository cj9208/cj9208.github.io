---
name: pipeline-blog-init
description: Run add-hugo-front-matter, rename-blog-filenames, and sync-subfolder-links in sequence, restricted to unpushed content (uncommitted + committed-but-unpushed) by default, with a git stash as rollback backup.
---

# SKILL: Pipeline Blog Init

把三个内容初始化子 skill 按顺序跑在**未 push 的工作**上（新文章、新改动），默认**不再全量扫描**整个 `content/`。

"未 push 的工作" = 两类：

1. **已提交但未推送到远端**（`git log origin/main..HEAD` 涉及的 `content/` 文件）
2. **工作区未提交**（`git status` 中的修改/未跟踪的 `content/` 文件）

## Process

### 0. 计算未 push 范围（Scope）

先算出本次要处理的文件清单并写入 scope 文件：

```bash
python .opencode\skills\pipeline-blog-init\scripts\compute-scope.py
```

- 脚本基于 `@{u}`（即 `origin/main`）计算未 push 提交 + 工作区改动，过滤出 `content/**/*.md` 且**磁盘上仍存在**的文件
- 输出 scope 文件路径（默认 `<temp>\opencode\pipeline-scope.txt`）并列出清单
- **把清单展示给用户确认**：默认只处理这些文件。若用户要求全量处理或补充文件，据实修改/重建 scope 文件
- 若脚本输出 `Nothing to do`（没有未 push 的 content 改动），直接结束，不执行后续步骤
- scope 文件在后续步骤通过 `--scope <文件>` 传给三个子 skill

### 1. Stash backup

保存当前工作区（含未跟踪文件）作为可回滚快照：

```bash
git stash push -u -m "pipeline-blog-init: pre-init snapshot"
```

立即恢复，让 pipeline 能继续操作这些文件：

```bash
git stash apply
```

stash 条目保留作为备份。出错时：

```bash
git checkout .
git stash apply
```

> 注：stash 只覆盖**工作区改动**。对**已提交但未 push** 的文件，若 pipeline 修改了它们，回滚方式为 `git checkout .`（撤销对工作区的改动）配合上面的 stash；若要彻底丢弃这些本地提交，用 `git reset <origin/main>`（谨慎，会改写本地历史）。

### 2. Dynamic skill invocation

按顺序使用 `skill` 工具加载并执行，每个子 skill 都**传入 scope**，只处理未 push 的文件：

1. `add-hugo-front-matter`
   - 脚本：`python .opencode\skills\add-hugo-front-matter\scripts\find-no-frontmatter.py --scope <scope文件>`
2. `rename-blog-filenames`
   - 脚本：`python .opencode\skills\rename-blog-filenames\scripts\propose-renames.py --scope <scope文件>`
3. `sync-subfolder-links`
   - 脚本：`python .opencode\skills\sync-subfolder-links\scripts\add-links-for-scope.py --scope <scope文件>`（可加 `--apply` 实际写入）

**Do NOT inline or copy instructions from the sub-skills into this document.**
Always `skill`-load them dynamically so each runs with its own latest instructions.

### 3. Error handling

若某个子 skill 失败（用户取消、脚本报错等），停止 pipeline 并报告失败，不继续下一个。

若用户在子 skill 过程中提问，在该子 skill 内解决后再继续。

### 4. Completion

pipeline 结束后运行 `git status --short` 展示结果。

提醒用户：

- 预置快照仍在 stash 中，可用 `git checkout .` + `git stash apply` 恢复
- 若本批改动中包含**已提交未 push**的文件且需要彻底丢弃，用 `git reset <origin/main>`（会改写本地历史）
