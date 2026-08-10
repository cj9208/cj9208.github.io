---
name: sync-zhihu-migration-status
description: Sync the migration status of blog articles against the Zhihu column record file (zhihu-column-c_132070558-articles.md). Use after migrating a new article into content/blog that originally came from the Zhihu column c_132070558: it finds newly-migrated articles, sets their front-matter date to the original Zhihu created time, and updates the record file to mark them as migrated (unbolds the title, flips 未迁移 to 已迁移).
---

# SKILL: Sync Zhihu Migration Status

当把知乎专栏 c_132070558 的新文章迁移到 `content/blog/` 后，用本技能把本地文章的发布时间恢复为知乎上的原始 created 时间，并同步更新记录文件。

## 背景

- 记录文件：仓库根目录 `zhihu-column-c_132070558-articles.md`
- 该文件是一个 Markdown 表格，每行一篇文章，含「迁移状态」列（`已迁移` / `未迁移`）
- 未迁移的文章标题用 `**加粗**` 标记，方便一眼识别
- 本技能负责在完成一篇文章的迁移后，将该行从「未迁移+加粗」改为「已迁移+不加粗」

## 工作流

### 1. 运行同步脚本（dry-run，先看报告）

```bash
python .opencode\skills\sync-zhihu-migration-status\scripts\sync_migration.py
```

脚本会：
- 解析记录文件表格，统计总行数、已迁移/未迁移数
- 扫描 `content/blog/` 下所有文章 front matter 的 `title`
- 按归一化标题（忽略标点、空格、引号变体）与「未迁移」行匹配，支持模糊匹配（相似度 ≥ 0.92）
- 输出计划：匹配到的文章、将设置的 `date`、将要更新的行

### 2. 人工核对报告

- 检查匹配到的标题是否确实对应（尤其模糊匹配项）
- 确认 `new_date` 与知乎 created 时间一致

### 3. 应用变更

```bash
python .opencode\skills\sync-zhihu-migration-status\scripts\sync_migration.py --apply
```

应用时脚本会：
1. **改本地 front matter `date`**：设为知乎 created 时间（`+08:00` 格式）
2. **更新 `lastmod`**：设为当前实际时间（遵循 AGENTS.md 的 lastmod 维护规则）
3. **更新记录文件**：
   - 该行「迁移状态」由 `未迁移` 改为 `已迁移`
   - 去掉标题的 `**` 加粗

### 4. 验证

- 重跑 dry-run，确认 0 条待更新
- `git status --short` 查看改动

## 脚本参数

- `--record <path>`：记录文件路径，默认仓库根 `zhihu-column-c_132070558-articles.md`
- `--base <dir>`：扫描的本地文章目录，默认 `content/blog`
- `--apply`：实际写回文件；不加则只输出 dry-run 报告

## 注意事项

### 编码安全（关键）

- 一律用 Python `open(..., encoding='utf-8-sig')` 读取 `content/` 下的 `.md`（`utf-8-sig` 剥掉 BOM；用 `utf-8` 读 BOM 文件会导致 front matter 正则不匹配）
- 写文件用 `encoding='utf-8'` 或 `utf-8-sig`（保留原 BOM 状态），保持 LF 行尾
- **禁止**用 PowerShell `Get-Content`/`Set-Content` 默认编码（ANSI/GBK 会破坏 UTF-8 中文，不可逆）
- 优先用 `edit` 工具处理少量文件

### 标题匹配的坑

- **引号变体**：来源 `「干净交易」` vs 文中 `"干净交易"`，需归一化后再匹配
- **数量词差异**：如「四大底层逻辑」vs「五大底层逻辑」，模糊匹配（≥0.92）可命中
- **LaTeX/符号差异**：`$\neq$` vs `!=`，归一化无法消除，模糊匹配可命中
- 若多个本地文章命中同一行（不应发生），脚本按行去重，只更新一次；若一行命中多篇（重复迁移），提示核对

### lastmod 维护规则

每次实质修改 `content/` 下文章（含改 date）后，必须把 front matter 的 `lastmod` 更新为当前实际时间。脚本自动处理。

### 特殊 Unicode 文件名

- 从不手打中文文件名，脚本用 `os.walk` 从文件系统读取，天然安全
- 手动 `edit` 时用 `glob`/`os.listdir` + 关键词匹配获取真实路径

## 执行要求

1. 先跑 dry-run 拿全量事实，再动手改
2. 模糊匹配项必须人工核对，避免错配
3. `--apply` 后再跑一次 dry-run 确认 0 待更新
4. 若记录文件结构变化（列增减、表头改名），先向用户确认再执行
