# AWS 笔记深度抽验报告

- 日期：2026-09-19
- 用途：`notes/blog-todo.md` 批次二「快速抽验 3~5 个服务页与 S3 页的深度差」的执行记录
- 范围：`content/blog/study-notes/aws-solution-architect-notes/` 全部 47 个文件

---

## 一、结论

抽验发现**三档结构**（S3 作为 worked example/模板基准为 10 节）：

| 档位 | 数量 | 结构 | 代表 |
|---|---|---|---|
| 完整档（超出模板） | 12 文件 | 17 节（10 个服务页 + KMS/IAM 等），含 Constraint Matrix / Cost Shape / Security Governance / Multi-Account / Evolution Path / Anti-Patterns | `vpc.md`、`iam.md`、`kms.md`、`cloudwatch.md`、`sqs.md`、`eventbridge.md`、`api-gateway.md`、`cloudfront.md`、`aurora.md`、`dynamodb.md` 等 |
| 模板标准档 | 1 文件 | 10 节，与 S3 同构 | `lambda.md` |
| 精简档 | 26 服务页 + `ecr.md`/`aws-backup.md` | 5~6 节（Identity → Fit/Non-Fit → 关键设计驱动/High-Impact Settings → Failure & Cost → Expert Warnings） | `ec2.md`、`rds.md`、`glue.md`、`step-functions.md` 等 |

另 `cloudtrail.md`（60 行）为 5 节精简档。

## 二、判定

1. 精简档属**有意设计的轻量格式**（页首自述 "fast expert note"），内容具备 Identity / 选择边界 / 失败面 / 成本 / 反模式五要素，无模板套壳感；缺的是决策表、场景矩阵、对比快照等**展开分析层次**。
2. 按 blog 标准（快照型学习笔记，非教程），精简档可发布；深度方差是真实存在的，但方向是"完整档高于基准、精简档低于基准"，不存在明显凑数内容。
3. 可选的后续增强（不阻塞发布）：若想消除深度方差，优先级为 `ec2.md`/`rds.md`（旗舰服务）> 其余精简档；增量方式是补 High-Impact Settings 表与 Comparison Snapshot。

## 三、发布决定（2026-09-19，已执行）

- 立即发布：整树 draft 翻转 + lastmod 刷新（见 blog-todo 批次二）。
- `progress.md` 沿用 rag 批次先例移入 `notes/`（内部进度文档不进公网），发布树从 47 文件减为 46 文件。

## 四、发布执行记录（2026-09-19）

机械步骤（全部完成）：

1. 全树 46 个发布文件 `draft: true` → `false`；lastmod 刷为 2026-09-19T10:12–10:35 各批次真实时间戳，无占位值。
2. `progress.md` → `notes/aws-solution-architect-notes-progress.md`（发布树 47 → 46 文件）。
3. **slug 统一为 kebab-case（用户选定）**：15 个文件——11 个家族页 + `lambda` / `s3` / `iam` 三个服务页 + 模板 + study map；同步修复 study map 中 4 处旧 slug 硬编码 URL。起因：Hugo 会把含大写的 slug 输出目录转小写，原「编号_Slug」式与首字母大写式混用存在大小写不一致隐患。
4. 链接与显示文本清理：正文显示文本统一去除目录前缀与 `.md` 后缀（如 `compute/lambda.md` → `lambda`、`compute/_index.md` → `compute`）。
5. 搜索索引重建：`.opencode/skills/search-blog-articles/index.json`（222 篇）。
6. 根索引：`content/blog/study-notes/_index.md` 的 AWS 条目由纯文本改为 relref 链接。

验证（本地构建全绿）：

- 全树进入构建产物；正文内 41 个绝对站内 URL 逐一映射到已构建页面，0 缺失。
- 本地服务器实测：相对链接 47 条全部 200。
- 无旧 slug / 裸 `_index.md` / 带路径前缀显示文本残留。

部署：随本次提交推送 main，由 `.github/workflows/hugo.yml` 部署至 GitHub Pages。

## 五、发布后结构调整（2026-09-19，当日完成）

起因：用户复查线上页面后指出 study map 两处问题——(a) 越到 service 层：28 个旗舰链接与家族页 Flagship Service Plan 重复，10 项 next-dives 属作者 backlog 非读者内容；(b) 与 collection landing 功能重叠：同一份 11 家族列表、同一套「怎么读」指引，landing 首句即「去看 study map」，读者实际要跳两跳。用户选定方案：合并成单页。

执行：

1. `AWS-Solution-Architect-Study-Map.md` 删除（发布树 46 → 45 文件）；读者向内容全部并入 `_index.md`（collection 页），层级收敛为三层：collection 页 → 家族页 → 服务页。
2. collection 页重组：家族表按建议学习顺序排列（吸收原「Suggested Study Order」，改为家族名显示）；删 28 服务旗舰清单（家族页已有带状态的 Flagship Service Plan）；删「Study Workflow」（与模板页「Practical Study Loop」逐条重复）；「Expert Note Standard」压缩去重。
3. 内部内容移入 `aws-solution-architect-notes-progress.md` §5：next-dives backlog、目录命名说明。
4. 旧 URL 保留：`_index.md` 加 alias，`/blog/study-notes/aws-solution-architect-notes/study-map/` 重定向到 collection 根。
5. 搜索索引重建：222 → 221 篇。
