---
name: search-blog-articles
description: Given a topic or idea, find existing blog articles that may already cover it, so the user can judge whether the idea is new. Searches a committed index of article metadata (tags, categories, titles, short excerpts) plus the cross-reference link graph, then does a small-LLM novelty gap analysis and suggests tags/category/section. Read-only; use when the user gives a topic and asks what related posts exist or whether an idea is novel (搜索相关文章, 是否已有覆盖, novelty check).
---

# SKILL: Search Blog Articles (Topic → Related Articles + Novelty Check)

给定一个 **topic / 想法**，找出站内已有的**可能相关文章**，并判断这个想法是否已被覆盖、增量在哪里。

与 `review-blog-content` §二 的区别：那个技能是**有 draft 之后**找关联并落互引；本技能是**只有 topic 时**做检索与新意评估，**只读、不改任何 `content/` 文件**。

## 核心设计：先便宜地搜，再少量地读

为控制 token：

1. **索引**（`index.json`，已提交）只存元数据 + 短摘要 + 交叉引用边，**不存全文**。
2. **检索脚本**在索引上打分（tags/categories/title/slug/excerpt）+ 交叉引用图扩展，输出一个小 shortlist。
3. **LLM 只读这个 shortlist**，且优先用输出里已带的 excerpt；仅当判断增量确有必要时，才打开 **top 3~5 篇**原文。**禁止通读 `content/`。**

## 工作流

### 1. 索引会自动保持最新

`search.py` 每次运行会比对 `content/blog` 的内容指纹（`source_fingerprint`）：**过期就自动重建**，无需手动刷新。若只想用现有索引、不触发重建，加 `--no-refresh`（会打印过期警告）。

需要**提交**索引时（例如内容改动后准备 commit），手动重建一次以保证仓库里的 `index.json` 新鲜：

```bash
python .opencode\skills\search-blog-articles\scripts\build-index.py
```

扫 `content/blog/**.md`（跳过 `_index.md` / `progress.md`），提取 front matter 元数据、公开 URL、短摘要、出链，写入 `index.json`。重建约 200ms，可放心常跑。`pipeline-blog-init` 与 `review-blog-content` 收尾也会自动重建。

### 2. 把 topic 拆成检索词

- 提炼 3~6 个**中英文关键词**（同一概念给出中英两版，提高召回）。
- 对照受控词表 `.opencode\skills\add-hugo-front-matter\tags-registry.md`，加入 1~2 个**已有的准确标签**作为检索词（标签命中权重最高）。
- 若主题落在某个 section，可用 `--section` 收窄。

### 3. 运行检索

```bash
# 关键词检索
python .opencode\skills\search-blog-articles\scripts\search.py --terms "reward hacking incentive design"

# 位置参数写法同样可用
python .opencode\skills\search-blog-articles\scripts\search.py "养老金" 社保

# 限定 section / 必须带某标签 / 控制返回量 / 机器可读
python .opencode\skills\search-blog-articles\scripts\search.py --terms "trust" --section systems_and_governance --limit 10
python .opencode\skills\search-blog-articles\scripts\search.py --terms "governance" --tag "Trust Collapse"
python .opencode\skills\search-blog-articles\scripts\search.py --terms "agent harness" --json
```

输出三段：
- **Direct matches**：按分数排序，含 `slug`、公开 URL、tags、命中信号（`tag=`/`tag~`/`cat=`/`title`/`phrase`）、短摘要。
- **Graph neighbors via cross-ref**：与命中文章有**一跳交叉引用**（出链或入链）的其他文章——用于发现关键词没命中、但主题相邻的文章。
- **Suggested tags / section**：命中文章的高频标签与所在 section，作为新文章 tags/category/section 的候选。

### 4. 判断相关性与新意（LLM 的唯一核心工作）

对 Direct matches + Graph neighbors 逐篇判断，必要时打开 top 3~5 篇原文核对。产出：

- **候选文章表**：相关度、文章标题、公开链接、命中信号、与主题的关系（同源 / 具体化 / 不同切面 / 仅背景）。
- **新颖度分析**：
  - **已被覆盖**：与 topic 重合的论点、机制、结论（指出具体是哪篇的哪部分）。
  - **增量**：新想法相对已有文章的差异——新机制 / 新数据 / 新场景 / 反向结论 / 更强的综合。
  - **重复风险**：是否与某篇实质重复，或已有文章其实已经给出该结论。
- **建议**：新建文章、还是并入某篇综述/已有文章；给出建议 `tags`（必须复用受控词表已有标签）、`category`、`section`。

### 5. 只读约束

- **不修改 `content/` 下任何文件**，不写 `_index.md`，不更新 `lastmod`。
- 允许写的只有本技能目录下的 `index.json`（由 `build-index.py` 生成）。
- 若用户接着要**互引落位**或**写文章**，转交 `review-blog-content` / `generate-article`。

## 输出模板

```markdown
## 候选文章
| 相关度 | 文章 | 命中信号 | 与主题关系 |
| --- | --- | --- | --- |
| 高 | [《标题》](https://cj9208.github.io/blog/<目录>/<slug>/) | tag=..., title | 同源 |

## 新颖度分析
- **已被覆盖**：...
- **增量**：...
- **重复风险**：...

## 建议
- 形态：新建文章 / 并入《某综述》
- tags：`...`、`...`（复用受控词表）
- category：`...`　section：`...`
```

## 脚本

| 脚本 | 作用 |
| --- | --- |
| `scripts/build-index.py` | 扫描 `content/blog`，生成 `index.json`（元数据 + 摘要 + 出链 + 内容指纹） |
| `scripts/search.py` | 在索引上打分 + 交叉引用图扩展，输出 shortlist / `--json`；过期自动重建 |
| `scripts/blogindex.py` | 共享模块：`content_files()` 与内容指纹 `compute_fingerprint()` |

`index.json` 字段：`title, shorttitle?, slug, url, path, dir, section, categories, tags, date, lastmod, excerpt, out_links[]`，顶层含 `generated_at` 与 `source_fingerprint`。`path` = URL 去掉域名（小写目录 + slug），用作交叉引用图的节点键。

## 注意事项

- **目录大小写**：公开 URL 目录为**小写**（`Chinese_government` → `chinese_government`，`AI_study` → `ai_study`），由脚本自动推导，不要手打。
- **评分口径**：tag 权重最高（复用受控词表是站内最重要的主题信号），其次 category/title，excerpt 最低；命中信号会一并打印，便于人工核对是否误命中。
- **Graph neighbors 只有一跳**，且方向无关（出链或入链都算）；它用于补召回，不代表一定相关，需人工确认。
- **摘要为截断文本**，仅供初筛；判断增量时对 top 候选读原文更可靠。
- **索引新鲜度**：`search.py` 用内容指纹自动判断并重建（`--no-refresh` 可关闭）。指纹基于文件内容而非 mtime，`git checkout` 不会误判。修改 `content/` 后若要提交索引，手动跑一次 `build-index.py` 即可。
- **编码安全**：脚本一律 `utf-8-sig` 读取、`utf-8` 写入；用 `edit`/`read` 工具处理原文，**禁止** PowerShell 默认编码读写含中文文件（见 AGENTS.md）。
- 新建/移动文章后记得重跑 `build-index.py`，否则检索会漏新文章。
