# Skill 索引

这里（`.agents/skills/`）是本仓库全部 agent 技能的**唯一真源**，由 git 跟踪。跨 harness 的目录约定、装订命令与删除风险见仓库根目录 `AGENTS.md` 的"Skill 的唯一真源"一节；本文只补充每个 `SKILL.md` 都**不拥有**的跨技能知识。

本索引**故意不复述**各技能的用途、触发词或步骤。那些的唯一真源是各自 `SKILL.md` 的 `description` 与正文；在索引里抄一份，就是给同一条规则制造第二份拷贝，从此开始漂移。想知道某个技能做什么，读它自己的 `SKILL.md`。

（迁移说明：本文前身是 `.opencode/README.md`，那份文件里逐条列出了三个技能的 use cases 与 not-for，与它们的 `SKILL.md` 重复，本次删去了重复部分，保留了下述跨技能内容。）

## 清单

只按目录名列出，不做描述。

| 组 | 技能 |
|---|---|
| 发布流水线 | `add-hugo-front-matter`、`rename-blog-filenames`、`sync-subfolder-links`、`pipeline-blog-init` |
| 内容审阅与迁移 | `review-blog-content`、`restore-missing-links`、`sync-zhihu-migration-status`、`search-blog-articles` |
| 写作与阅读 | `generate-outline`、`generate-article`、`digest-article`、`add-ez-encoder-presentation` |
| 思考陪练 | `stress-test-reasoning` |
| Capstone（容器目录，内嵌 6 个技能 + `reference/`） | `capstone-thinking-partner/` |

## 发布流水线的推荐顺序

新迁入或新建的内容，正常顺序是：

1. `add-hugo-front-matter` —— 补齐或规范化 front matter
2. `rename-blog-filenames` —— 文件名对齐文档标题
3. `sync-subfolder-links` —— 同步栏目页链接

这个顺序的因果：H1 缺失时 front matter 的 `title` 会成为标题来源，所以它必须先定；重命名要早于链接同步，否则栏目页链接指向即将失效的文件名；`_index.md` 在文件名与元数据都稳定之后才最可靠。

`pipeline-blog-init` 是这三步的编排入口（默认只处理未推送的内容，并以 `git stash` 作为回滚备份）。编排技能只管顺序与范围，各步的纪律留在被编排者自己那里——不要把步骤复述进编排技能。

## 范围规则

- 内容改动留在 `content/` 下，除非用户明确允许动其他目录。
- Hugo 栏目页链接维护在 `content/blog/` 下。
- 重命名与 front matter 规范化是两个独立工作流，保持独立——它们的风险面不同（一个改文件名并需要联动更新链接，一个只改文件头）。
- 业务取舍、风险例外和不可逆决策不写进技能；技能只固化"动作明确、结果可验证"的部分。

## Hugo 字段事实

- 本站主题是 Docsy（`hugo.toml` 的 module 指向 `github.com/google/docsy`）。
- `slug` 对文章页有效，推荐作为标准 front matter 的一部分；但**对 `_index.md`（栏目页）无效**，栏目页 URL 取目录名。全仓 23 个 `_index.md` 的对照证据见 `notes/game-theory-series/01-验证与总纲写作计划.md`。
- `toc` 不是本站默认字段，Docs 主题通常已处理。
- `showBreadcrumbs` 不是本站默认字段，当前布局不依赖它。
