# 综述类文章注册表（Overview Article Registry）

综述类文章 = 以"总纲 / 综述 / 系统梳理"为形态的文章，正文中通过链接汇总、串联本站其它文章
（示例：《威权治理系统总纲：从历史大分流到终局死锁》）。

新增文章时，`add-links-for-scope.py` 会读取本表：若文章所在目录命中某篇综述文章的
「覆盖目录」，且正文尚未引用该文章，则把它报告为"综述类文章候选"。是否加入、
放在哪个主题分节属于编辑判断，需与用户确认后手工编辑正文。

## 注册条目格式

每个综述类文章一个 `### ` 小节，字段：

- `- 目录:` 综述文章所在目录（**仓库相对路径**，如 `content/blog/systems_and_governance/Chinese_government`）
- `- slug:` 综述文章的 front matter `slug`（脚本据此在目录内匹配文件，避免依赖中文文件名）
- `- 覆盖目录:` 该综述覆盖的文章目录（仓库相对路径），可多行；新文章所在目录命中任意一行即为候选
- `- 链接格式:` 正文内添加链接时使用的格式

## 注册表

### 威权治理系统总纲
- 目录: content/blog/systems_and_governance/Chinese_government
- slug: authoritarian-governance-overview
- 覆盖目录:
  - content/blog/systems_and_governance/Chinese_government
  - content/blog/systems_and_governance
- 链接格式: 公开链接 `[《标题》](https://cj9208.github.io/blog/systems_and_governance/chinese_government/<slug>/)`

> 注：`content/blog/systems_and_governance` 根目录命中时覆盖面较广，是否真正加入需按主题与综述正文的分节结构逐一确认。

### 极简组织行为学与管理学概论
- 目录: content/blog/systems_and_governance
- slug: ob-management-overview
- 覆盖目录:
  - content/blog/systems_and_governance
- 链接格式: 公开链接 `[《标题》](https://cj9208.github.io/blog/systems_and_governance/<slug>/)`

> 注：该综述以"阅读路径"方式指引，正文不逐篇列链接；加入新文章需以正文叙述语境判断，命中候选时人工确认。
