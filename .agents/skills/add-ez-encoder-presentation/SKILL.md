---
name: add-ez-encoder-presentation
description: Extract a presentation post from the EZ.Encoder Academy Circle.so community (www.ez-encoder.com) using a logged-in Chrome profile and append it to content/blog/AI_study/presentations.md. Use when the user provides an ez-encoder.com post URL (e.g. https://www.ez-encoder.com/c/<space>/<post-slug>) and wants it recorded in the Presentations 分享记录 page.
---

# SKILL: Add EZ.Encoder Presentation

把 ez-encoder.com（EZ.Encoder Academy，基于 Circle.so 的社区）上的一次 presentation 帖子提取出来，追加到 `content/blog/AI_study/presentations.md`。

## 背景与前置条件

- 站点：`https://www.ez-encoder.com/`（EZ.Encoder Academy 社区，Circle.so 搭建）
- 帖子 URL 形如 `https://www.ez-encoder.com/c/<space>/<post-slug>`
- 目标页面：`content/blog/AI_study/presentations.md`（单文件栏目页，所有 presentation 依次追加）
- **关键难点**：站点有 Cloudflare 人机校验 + 帖子内容由 JS 渲染（Circle.so SPA），普通 `webfetch`/`curl` 拿不到正文，且登录态是 session cookie（不落盘，无法复制）。
- **解决方案**：用本机已登录的 Chrome profile 以 headless 模式渲染页面并 `--dump-dom`。

## 重要约束

- **使用 Chrome 的真实 profile（`--user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"`）**，才能带上登录态。
- 使用真实 profile 前必须**确认 Chrome 已完全退出**，否则 profile 被锁、cookie 文件无法访问。
- 若有上一次残留的 headless Chrome 进程，先杀掉再开始。
- 不用 `--headless=new`，用旧版 `--headless`（新模式下真实 profile 会超时）。
- 路径含空格（`User Data`），`Start-Process -ArgumentList` 必须用反引号转义的双引号包住 user-data-dir。

## 工作流

### 1. 确认 Chrome 已退出，清理残留进程

```powershell
(Get-Process chrome -ErrorAction SilentlyContinue | Measure-Object).Count
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
```

若用户 Chrome 正在运行，让用户先关闭 Chrome（或征得同意后杀进程）。

### 2. headless 渲染帖子页面，dump DOM

```powershell
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$ud = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$out = "<temp>\<slug>_render.html"
Remove-Item $out -ErrorAction SilentlyContinue
$args = "--headless --disable-gpu --no-first-run --disable-extensions --disable-background-networking --disable-component-update --no-default-browser-check --disable-sync --user-data-dir=`"$ud`" --dump-dom --virtual-time-budget=30000 https://www.ez-encoder.com/c/<space>/<post-slug>"
$p = Start-Process -FilePath $chrome -ArgumentList $args -RedirectStandardOutput $out -RedirectStandardError "<temp>\<slug>_err.txt" -NoNewWindow -PassThru
$done = $p.WaitForExit(90000)
if (-not $done) { $p.Kill(); "TIMEOUT" }
"OUT LEN: $((Get-Item $out -ErrorAction SilentlyContinue).Length)"
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
```

输出体积约 2.7 MB 即为成功（成功渲染的 DOM 中不应出现 `is-signed-out`、`post_login_redirect`）。如果出现 `is-signed-out` 或体积为 0，说明登录态没带上，回去确认 Chrome 已退出后重试。

将 DOM 用 UTF-8 写为文本便于后续搜索：`[System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($out))` → `[System.IO.File]::WriteAllText($txt, $t, (New-Object System.Text.UTF8Encoding($false)))`。

### 3. 从 DOM 提取各字段

| 字段 | 定位方式 |
|---|---|
| 帖子标题 | `<title>` 标签（`Agentic Post Training 分享总结 \| EZ.Encoder Academy`），也是 `<h1 class="post__title">` 的内容 |
| 时间 | 附件文件名前缀，如 `2026-8-9-Jack-Agentic Post Train...`（正则 `class="text-sm font-semibold[^"]*">([^<]+)</span>` 命中附件名，取其中日期） |
| 附件 URL | 正文首部 `react-renderer node-file` 内的 `href="https://assets-v2.circle.so/<id>"` |
| 附件大小 | 附件名旁边的 `class="text-xs font-regular[^"]*">181.64 KB</span>` |
| 正文大纲 | `data-testid="post-body-inside"` 之后的 `<ol>...</ol>` 块（ProseMirror 渲染），剥离 HTML 后得到结构化大纲 |
| 正文内的本站文章链接 | 大纲中 `https://cj9208.github.io/blog/...` 形式的内链 |

推荐用 Python 脚本提取正文（参考仓库内 `.opencode/skills/` 下其他技能的脚本风格）：定位 `file-wrapper` 后的 `<ol>`，正则剥离 `<li>`/`<p>`/`<a>` 标签，把 `<a href="...">text</a>` 替换成 URL 本身，`html.unescape` 后再规整空行。

本技能自带提取脚本，可直接复用：

```bash
python .opencode/skills/add-ez-encoder-presentation/scripts/extract_post.py "<DOM txt 路径>" "<输出 txt 路径>"
```

脚本输出：`TITLE`、`ATTACHMENT_NAME`（含日期前缀，如 `2026-6-28-Jack-The Agent Harness...`）、`ATTACHMENT_SIZE`、`ATTACHMENT_URL`、`BODY`（剥离 HTML 的正文大纲，自动截断到评论区之前）。

> 注意：PowerShell 控制台会乱码显示中文，把提取结果写入 UTF-8 文件后用 `read` 工具查看，不要直接看控制台输出。

### 4. 核对关联博客文章的 slug

演示大纲里引用的 `https://cj9208.github.io/blog/ai_study/<slug>/` 等链接，逐个确认对应的本地文章 front matter 的 `slug` 一致：

```bash
# 用 grep 在 content/blog 下按 slug 确认目标文章存在
```

若帖子正文引用的站内链接 slug 与本地不一致，以本地为准修正。

### 5. 追加到 presentations.md

在 `content/blog/AI_study/presentations.md` 中新增一个 `## <标题>` 小节，**插入到已有条目的最上方（最新在前）**，位于简介段落之后、第一个 `##` 之前，结构（与现有条目保持一致）：

```markdown
## <帖子标题>

* **时间**：YYYY-MM-DD
* **场合**：[EZ.Encoder Academy](https://www.ez-encoder.com/) 社区 · <space 中文名>（<space slug>）板块
* **原文链接**：https://www.ez-encoder.com/c/<space>/<post-slug>
* **slides**：[<附件名>](<附件 URL>)（<大小>）
* **内容大纲**：
  <从正文大纲整理，用有序列表 + 子列表>
* **相关博客文章**：
  * [<文章标题>](<公开链接>)
```

- **排序规则**：默认最新的 presentation 排在最前（按时间倒序）。插入后检查全文各条目时间顺序为从新到旧。
- 相关博客文章用**公开链接**（`https://cj9208.github.io/blog/...`），遵循 AGENTS.md 链接规则。
- 正文里有而站内没有对应文章的（如知乎外链、公众号链接），可放在大纲里作为普通外链，不必强挂「相关博客文章」。
- 时间取附件文件名里的日期；若帖子标题本身含日期，优先用附件日期。

### 6. 更新 lastmod 并验证构建

- `presentations.md` front matter 的 `lastmod` 改为当前实际时间（遵循 AGENTS.md 规则）。
- 若 `content/blog/AI_study/_index.md` 被改动，同步更新其 `lastmod`。
- 验证 Hugo 构建：

```powershell
hugo --source <repo> --destination <temp_build_dir> --quiet; $LASTEXITCODE
```

确认生成的 `blog/ai_study/presentations/index.html` 存在且包含新标题。

## 常见坑

- **真实 profile 渲染超时**：headless 启动真实 profile 首次会慢（可达 90s），`WaitForExit(90000)` 不足时可能误杀进程导致输出为 0；可重试一次，或在 `.NET` 里用更长超时。第 3 步的 `virtual-time-budget` 与 `WaitForExit` 是两回事，前者控制页面 JS 虚拟时间。
- **登录态丢失**：若渲染结果含 `is-signed-out`，帖子内容不会渲染。此时应确认 Chrome 已完全退出（包括后台进程），再重试；不要尝试复制 cookie 文件（session cookie 不落盘，复制无效）。
- **中文乱码**：DOM 文件本身是 UTF-8，不要用 PowerShell 控制台直接打印中文；写入 UTF-8 文件后用 `read` 工具读取。写文件务必 `(New-Object System.Text.UTF8Encoding($false))`（无 BOM）或带 BOM 均可，但禁止默认 ANSI。
- **不要动其他文件**：只改 `content/blog/AI_study/presentations.md`（和必要的 `_index.md`），不涉及 `static/`、`.github/` 等（除非用户明确要求）。
