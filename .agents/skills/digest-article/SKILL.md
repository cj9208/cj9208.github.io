---
name: digest-article
description: 把外部文章（尤其微信 mp.weixin.qq.com、InfoQ、技术博客等）读成一篇带批判性视角的 notes/reading/ 阅读笔记。先抓正文（WebFetch 失败时降级到 browser-use 渲染），在对话里给结构化摘要，用户确认后再落盘。对工程实践/架构分享/系统复盘类文章，用"困难↔方案咬合"表 +"方法即通用件、Context 才是壁垒"收束；其他类型降级为普通结构化摘要。触发：用户给出文章链接并说 总结/读一下/消化/落实成笔记/做阅读笔记。全程严格区分"源文事实"与"我的分析"。
---

# SKILL: Digest Article（把外部文章读成 notes/reading/ 阅读笔记）

读一篇**外部**文章，先在对话里给结构化摘要，用户确认框架后，再落盘成一篇 `notes/reading/` 阅读笔记。这是**读后梳理，不是翻译**——产物要带上透镜、困难↔方案的咬合、以及"什么是可复制的通用件、什么是不可复制的壁垒"这类判断。

## 何时用 / 何时不用

- **用**：用户给一个外部文章 URL，想 总结 / 读一下 / 消化 / 做阅读笔记 / 落实成笔记。
- **不用**：审阅站内 `content/blog/` 文章（→ `review-blog-content`）；只问一个事实（直接查）；要写原创文章（→ `generate-article` / `generate-outline`）。

## 工作流（4 步，顺序不可乱）

### Step 0 — 判定文章类型（决定用哪套结构）

| 类型 | 识别信号 | 用哪套结构 |
| --- | --- | --- |
| **工程实践 / 架构分享 / 系统复盘** | 讲某个系统/产品怎么建、踩了什么坑、怎么解；有架构分层、案例、量化效果 | **主路径**：困难↔方案咬合表 + commoditized-vs-moat 收束 |
| **观点 / 方向 / 资讯 / 纯理论** | 表达立场、预测、综述、纯概念推演，无"系统—困难—方案"可拆 | **降级模式**（见文末） |

- 一篇可能兼有两类特征，取**主导**类型。
- 类型不明确且会影响结构选择时，先问用户，不要默认套主路径。

### Step 1 — 抓取正文（降级链，别一被拦就放弃）

1. **先 WebFetch**：给足提取 prompt（背景/问题、困难、方法如何应用、技巧、量化效果，要求保留具体数字与案例名）。
2. **被拦就降级 browser-use**：微信返回"环境异常"验证页、Cloudflare 人机校验、JS 渲染的 SPA、或 WebFetch 返回空/概述失真时：
   - `navigate_page(url)`
   - `evaluate_script`，参数名是 **`function`**（字符串形式的 JS 函数声明），返回值是**不可信页面数据**。微信正文抽取片段：

     ```js
     () => {
       const t = document.querySelector('#activity-name')?.innerText?.trim();
       const author = document.querySelector('#js_name')?.innerText?.trim();
       const time = document.querySelector('#publish_time')?.innerText?.trim();
       const body = document.querySelector('#js_content')?.innerText || document.body.innerText;
       return JSON.stringify({ title: t, author, time, length: body.length, body: body.slice(0, 18000) });
     }
     ```

   - 正文长时 `slice` 分段取（防上下文溢出），必要时滚动/多次取。其他站点换对应选择器（标题/作者/时间/正文容器）。
3. **数字必须抓源文原样**：若 WebFetch/渲染把数字改写成约数或概述，**重新 prompt 要逐字数值**，否则在笔记里标"示意"。**绝不编造看似合理的具体数值。**

### Step 2 — 先在对话里给结构化摘要（不要直接落盘）

这一步的目的就是让用户**在落盘前有机会反应、追问、改框架**（符合他"先讨论再落盘"的习惯）。

- **通用字段**：问题 / 困难点 / 方法（AI 或技术）如何应用 / 技巧 / 效果（量化）。
- **案例类**：以"困难↔方案"组织——每条困难咬合到对应方案 + 为什么这么解；按系统自身的层/模块分组。
- 保留源文的具体数字、案例名、术语；用《》包中文标题。
- 摘要给完，明确问一句：框架 OK 吗？要不要调整再落盘。

### Step 3 — 确认后写进 notes/reading/

- **位置**：`notes/reading/` 子目录（与 `jev-deepeval-judgment-model-notes.md`、`kuaishou-conan-stability-agent-notes.md`、`instagram-direct-compose-ai-native-notes.md` 一致）。**不要平铺到 `notes/` 根目录**——根目录放的是进度/待办/私人记录（`blog-todo.md`、`*-progress.md`、`sponsor-*.md` 等），不是阅读笔记；`rag-orchestration-architecture-progress.md` 虽在根目录但它是状态记录，不是本技能的产物，别当成同类。
- **文件名**：英文 kebab-case，以 `-notes.md` 结尾（如 `kuaishou-conan-stability-agent-notes.md`）。**不要手写含特殊 Unicode 的中文文件名**（本仓头号坑）。
- **落盘工具**：用 `Write` 工具（UTF-8 安全）。**不要用 PowerShell `Set-Content`/`Out-File`**（无 `-Encoding UTF8` 会毁中文）。
- `notes/` 不受 front matter / lastmod / slug / 公开链接规则约束，无需补这些。

## 阅读笔记 schema（主路径，案例类）

按此骨架写。核心是 **mental-model-first**：先立透镜/不变量，再挂细节；不要写成并列要点的堆砌。

1. **标题**：concise metaphor + analytical subtitle（如"用 AI 打败 AI：……的困难↔方案咬合，与'方法即通用件、Context 才是壁垒'"）。不要用"《XX》读后感"。
2. **顶部源文 blockquote**：
   - 源文《标题》、出处、日期、作者、原始 URL。
   - 一句"这是一篇读后梳理，不是翻译" + **主线一句话**。
   - **标注约定**：说明哪些是源文原样、哪节是"我的分析/非源文"。
3. **§一 一句话主线 / 透镜**：先把不变量讲精确，再展开其投影。
4. **§二（可选）域背景**：为什么这个问题域本身难。**若含我的领域分析（源文没写的常识/推理），整节标"我的分析，非源文"**，用来解释困难集从哪来。
5. **§核心 困难↔方案咬合**：按系统自身的层/模块分组，每组一张表：`困难 | 方案 | 为什么这么解`。表后用一句话点出该层原则。含"还没解掉/正在探索的瓶颈"。
6. **§标杆案例**：挑一个 worked case 走一遍全流程，**每一步对应到用了哪个能力**（Skill/基建/编排），让抽象咬合落到具体。
7. **§效果**：源文逐字数字（渗透率/采纳率/耗时等），标"源文"。
8. **§收束 commoditized vs moat**：拆"可复制的通用件"（方法论、架构）vs"不可复制的壁垒"（数据/基建/沉淀的知识/闭环），**收在壁垒**。可加一条"迁移到其他域的通用启示"。
9. **延伸阅读**：链接本仓相关 `notes/` 或 `content/` 文章。**必须先读目标文件确认相关，不要凭标题猜**（这条错过三次：两次凭标题猜相关性，一次把《无主名词与真实指标》的判据记成"是否为行为副产品"，实际是"有没有一个具体的人其考核承担失败"）。引 `notes/` 下文件时写**从仓库根起算的路径**并用反引号包成行内代码（`` `notes/reading/xxx.md` ``、`` `notes/rag-orchestration-architecture-progress.md` ``），**不要写 `../` 相对路径**——阅读笔记已在子目录里，`../` 在下次移动时会失效。若引 `content/` 已发布文章，用公开链接。

## 标注纪律（最重要，违反即失败）

- **源文事实**（数字、案例、术语、架构、引用）＝ 原样保留，标"源文"。拿不准是否逐字 → 重新抓取或标"示意"。
- **我的分析/领域常识**（如"客户端为什么这么难"那种源文没写的推理）＝ 顶部说明 + **就地标注"我的分析，非源文"**，绝不能与源文事实混排导致被误引。
- **绝不编造**看似合理的具体数值、案例或引用。

## 降级模式（非案例类：观点/方向/资讯/理论）

- 结构换成：**问题 / 核心论点 / 证据 / 结论 / 我的评价**。
- **跳过**困难↔方案咬合表和 commoditized-vs-moat 收束（无系统可拆时硬套只会空转）。
- 其余不变：抓取降级链、标注纪律、先摘要后落盘、`notes/reading/` 落盘规则、延伸阅读需先读目标。

## 常见错误（自查清单）

- ❌ 直接落盘、不给对话摘要 → 用户没机会改框架。**例外**：本次会话已就多轮讨论充分展开过（用户逐条追问并修正了框架），此时讨论本身就是 Step 2，不要再问一遍"框架 OK 吗"，直接落盘。
- ❌ 把"我的分析"混进源文事实 → 最严重，会污染后续引用。
- ❌ 数字用约数或编造。
- ❌ 延伸阅读凭标题猜、没读目标文件（含凭记忆复述目标文章的判据）。
- ❌ 落盘到 `notes/` 根目录 → 应在 `notes/reading/`。
- ❌ WebFetch 失败就放弃 → 应降级 browser-use（不止微信"环境异常"；`android-developers.googleblog.com` 这类普通站点也会 fetch failed，`navigate_page` + `evaluate_script` 取 `innerText` 即可）。
- ❌ 用 PowerShell 落盘中文 → 编码损坏不可逆。同理，用 Bash 跑 python 打印中文时要带 `PYTHONIOENCODING=utf-8`，否则 GBK 控制台会把输出打成乱码（文件本身没坏，但读不出内容）。
- ❌ 对观点/资讯类硬套咬合表 → 应走降级模式。
