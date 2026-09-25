# ZhiMap 导图导出 —— 探索与解决记录

> 记录日期：2026-08-17
> 背景：zhimap.com（上海业有专网络科技有限公司运营的在线思维导图工具）即将关停，需要把账号下的思维导图全部导出备份。

## 一、站点结构分析

ZhiMap 是纯前端 Vue 单页应用（SPA），后端为 Spring Boot REST 风格 API，所有导图数据存于云端服务器，账号与微信深度绑定（扫码登录）。

### 关键技术点

- 页面 HTML 是空壳 `<div id="app">`，所有内容由 JS 渲染，抓 HTML 看不到任何数据
- JS 包按 webpack chunk 懒加载：`manifest.js` + 公共包（vj/md/zlib/vui/el）+ 页面包（pc_login/pc_gallery/pc_show 等）
- 前端代码里可定位到全部 REST 接口路径

### 已确认的 REST 接口

| 接口 | 说明 | 是否需登录 |
|------|------|-----------|
| `GET /restful/sec/usrdir/list` | 我的目录树（根"我的导图"+子目录） | 是 |
| `GET /restful/sec/dir_mindmap?directoryUuid=X&page=N&size=50` | 某目录下的导图分页列表 | 是 |
| `GET /restful/pub/mindmap/load_v?uuid=X` | 读取导图完整数据（节点 JSON） | 公开图免登录，私图需登录 |
| `GET /restful/sec/get_uuids?req_num=N` | 拉取 uuid 列表 | 是 |
| `GET /restful/sec/export?mindmapUuid=X&type=...` | 官方导出（png/pdf/mm/docx/zhimap） | 是 |
| `GET /show_mmap_as_img?uuid=X` | 导图渲染为图片 | - |

## 二、踩过的坑与结论

### 坑 1：`get_uuids` 返回全站列表，不是"我的导图"

初次脚本直接调 `get_uuids?req_num=100000`，返回了 100000 条 uuid（服务器上限），随后 `load_v` 逐个报"未授权"。

- 结论：**该接口不是"我的导图"列表**，不能用它确定归属
- 未登录时它返回 `code 2000`（登录已失效）

### 坑 2：登录态是成功导出的前提

- 未登录：`usrdir/list`、`dir_mindmap`、`get_uuids` 全部返回 `code 2000`（请刷新页面重新登录）
- 脚本 fetch 必须带 `credentials: 'include'` 才会携带微信登录 cookie

### 坑 3：`dir_mindmap` 的参数名是 `directoryUuid`

用 `dirUuid` 试返回 `code 1001`（错误信息提示"directoryUuid"），改对参数名后返回正常。

### 坑 4：文件名用 `mindMap.title` 会得到一堆"中心主题"

- `mindMap.title` 常是默认值（"中心主题"、"ZhiMap 在线思维导图"等）
- 真正有意义的标题在 `trees[0].title`（根节点标题），如"股票策略评价"、"RAG-based chatbot design"
- 解决：命名改为取根节点标题，且**必须保留 `__uuid` 后缀**——因为很多图根标题相同，去掉会互相覆盖

### 坑 5：`.mm` 用 `GM_download` 下载不成功

`GM_download` 连续两次下载 blob URL 时，第二个可能因 URL 生命周期问题失败。改为**原生 `<a download>` 标签点击下载**后稳定。

### 坑 6：标题含换行符导致文件命名非法

个别导图标题含 `\n`，转成文件名时报 `[Errno 22] Invalid argument`。处理：标题先去掉换行/制表符再作文件名。

### 关于图片的检查结论（2026-08-17 版，**已被推翻**）

对所有 38 张导出 json 检查：
- 节点字段无 `image` 字段（仅有 title/content/link/folded/children 等）
- `content` 中无 `<img>`、无 `data:image` base64

结论"这些导图本身没有插入图片"是**错的**。错因：检查只找了 ZhiMap 的 `image` 字段和 `data:image`，
而图片实际是以 `<img src="/res/...">` 混在节点的 `title` HTML 里；`strip_html` 又把标签整个剥掉，
所以转换出的 Markdown 里这些节点变成了空的 `- ` 条目，看起来像"本来就没内容"。

## 三、最终方案

### 导出流程（油猴脚本 `zhimap_export_all.user.js`）

1. 校验登录态（调 `usrdir/list`）
2. `usrdir/list` 拿目录树，递归收集所有目录 uuid
3. 每个目录调 `dir_mindmap?directoryUuid=X&page=N&size=50` 自动翻页（`totalPages` 控制循环）
4. 汇总 `content[].publicationInfo.uuid` → 去重
5. 逐张调 `load_v` 获取数据，用 `<a download>` 下载 `.json` + `.mm`
6. 命名：`根节点标题__uuid`

### 转换流程（`zhimap_convert.py`）

- `convert <json目录> -o <输出目录>`：json → `.mm` / `.md` / `.txt`，命名沿用 `根节点标题__uuid`
- `download --cookie "..." --convert`：命令行直连下载（不装油猴），需浏览器复制登录 Cookie

## 四、结果

- 成功导出 **38 张**导图，共 152 个文件（json/mm/md/txt 各 38）
- 保存在 `notes/zhimap-export/`
- 每张图 4 种格式，命名有意义且不覆盖

## 五、遗留提醒

- 若账号下有导图在"回收站"或特殊目录，`dir_mindmap` 可能未列出
- ~~若确认某张图有图片但没导出，需用 `load_e` 接口重导验证~~ —— 已查明：图片确实在 `load_v` 的数据里（`<img>` 混在节点 HTML 中），不需要 `load_e`，见第六节
- 网站即将关停，**备份要趁早**，关停后 `.zhimap` 原生格式也无法再使用

## 六、第二轮：图片本地化 + 完全展开（2026-09-25）

### 重新核查的事实

| 项目 | 实测结果 |
|------|----------|
| 内嵌图片 | 38 张导图里 **35 个 `<img>`**，分布在 9 张图中，路径形如 `/res/e/9/<数字>.png` |
| 图片可达性 | `https://zhimap.com/res/...` **免登录即可下载**，35 张全部 200，共 5.4 MB |
| 文件名冲突 | 35 个 basename 全局唯一，可平铺进单个 assets 目录 |
| 折叠状态 | 存档 JSON 里有 **78 个节点 folded=true** |
| 折叠是否丢内容 | **不丢**。`load_v` 返回完整子树，转换脚本也无条件递归 children，md 一直是全展开的 |
| KaTeX 公式 | 187 处。旧版被 `strip_html` 压成 `dnl=dnlRaw−μlσld_{nl}...` 这类三重复读垃圾，是"展示不好"的另一主因 |
| 官方 PNG | `/restful/sec/export?mindmapUuid=X&type=png` 免登录可用（38 张 `private` 均为 false），内嵌图片在图里；但**按存档的折叠状态渲染**（折叠分支只剩 `...`），且画布锁死 **1600×1130**，`scale/width/dpi/hd/expand` 参数一律无效 —— 即官方导出既拿不到"完全展开"也拿不到高清 |

### 做法

`zhimap_convert.py` 新增：
- `render_node()`：先摘出 `<img>` 备用，再把 KaTeX span 换成 `$tex$`（读 `<annotation encoding="application/x-tex">`），最后剥其余标签
- `assets` 子命令：扫描 JSON 里全部图片引用并下载到本地目录
- `convert` 增加 `--fetch-assets` / `--assets-dir` / `--remote`

### 结果

- `notes/zhimap-export/assets/`：35 张图，0 失败
- 38 张 md/mm 原地重生成：**4274 个节点全部在册**（逐张比对 JSON 节点数与 md 条目数，38/38 一致）
- 校验：md 图片引用 35 处、本地缺失 0；`/res/` 残留 0；`katex` 标记残留 0；空条目 1 个（源数据本身即空节点）
- `.txt` 与 md 内容重复，已删除（`zhimap_convert.py` 也不再输出 txt）

## 七、第三轮：自建排版出高清整图（2026-09-25）

官方导出既不能"完全展开"也不能放大（见第六节表末行），驱动网站前端的 viewer DOM 又不稳定，
因此改为 **本地重排版**：新增 `zhimap_render.py`。

### 做法

1. 读 JSON，把节点标题的富文本原样搬进 HTML（图片改指本地 `assets/`，KaTeX 标注换成 `<span class="km">`）
2. 页面内先建隐藏测量容器 → 等图片/字体/公式就绪 → 读每个节点真实宽高
3. tidy-tree 排版（按 `node.side` 分左右两侧），SVG 画贝塞尔连线，量出画布尺寸写进 `data-canvas`
4. `--dump-dom` 读出画布尺寸决定倍率 → `--screenshot` 出图 → PIL 按主题背景色裁掉多余边

### 踩到的坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 画布只有 172×256 | 量尺寸早于图片/字体加载 | 拆成 buildBoxes → waitReady → readSizes → layout 四阶段 |
| 节点宽高全为 0 | `el(html)` 返回的是外层 wrapper | 取 `.firstChild` |
| 排版后公式仍是 `$...$` 原文 | 只给隐藏测量盒做了排版，可见节点又用原始 HTML 重建 | 缓存排版结果 `n.html` 复用 |
| **美元金额被当公式** | `$...$` 规则无法区分：RAG 等 3 张图共 45 个节点正文里本来就有 `$5,000`、`$200 cashback` | 公式改用 `span.km` 显式标记，正文里的 `$` 原样保留 |
| `png/` 目录是空的 | Chrome 的 `--screenshot` 相对路径按它自己的 CWD 解析 | 传绝对路径 |
| 个别公式排版失败 | TeX 源里带 `&lt;` 等 HTML 实体 | 标注先 unescape 再塞进 `span.km` |
| 图片上方凭空多一行空白，像被截断 | ZhiMap 把 `<img>` 包在 `<p>\u200b<img></p>` 里，零宽空格撑出一个幽灵行盒（节点高 68 → 46 px） | `node_html()` 里先 `replace('\u200b','')` |
| 自检报"86~900 个节点溢出" | 那指标本身算错了；用真浏览器复核，重叠数为 0，只有一个节点比测量值高 2 px | 删掉假指标，改留 `data-overlaps`（真实两两重叠计数） |

### 结果

- 38/38 出图，共 32 MB，命名与 md 一致（`根节点标题__uuid.png`）
- 自检：每张图渲染后回读页面，38 张的 `data-badmath`（未排版公式）与 `data-overlaps`（节点重叠）合计均为 0
- 尺寸分布：长边中位数约 3000 px，28 张在 2000~9000 px（默认 2 倍率），8 张小图不足 2000 px；
  RAG 2738×30788、FRM 2920×25038（1:1 已是下限，再缩就糊），
  Design of Intention Recognition Layer / 面试 / Nike AI Overview / scikit-learn 均在 8800~8900 px 附近

### 仍有限制

- `--max-px` 只能降倍率，最低 1:1，超大图仍是一整张超长图（未做分页/分块）
- 排版是自动 tidy-tree，与 ZhiMap 原站的视觉布局不逐像素一致（内容一致，位置不同）
- 公式渲染依赖 jsdelivr 上的 KaTeX，离线时退化为显示 `$tex$` 原文并被 `data-badmath` 计数

## 八、第四轮：格式收敛（2026-09-25）

备份已经齐了，这一轮只做减法，让目录里每种文件都有不可替代的理由。

- **删 `.txt`（38 个）**：完全由 `.md` 派生（去掉标题符号、图片引用换成 `[图片: 路径]`），零新增信息。
- **删 `.mm`（38 个）**：FreeMind 是 `.json` 的**有损**重编码——内嵌图片和公式排版都丢了；
  需要喂给 XMind 之类工具时随时能用 `zhimap_convert.py convert -f mm` 重新派生，不必常驻。
- **查重复**：用户怀疑"多出来的 json 是改名的副本"。按 uuid 逐一比对，**38 个 uuid 全唯一、无相同内容**，
  怀疑不成立；真正的原因是 `covariance  estimation`（标题里两个空格）：`.json` 用网站原始文件名，
  `.md` 经 `safe_name` 压成单空格，看起来就像 json 单身。已把该 json 重命名成单空格，三种格式前缀统一。
- **改默认**：`zhimap_convert.py` 的 `convert` 不再输出 `.txt`，`-f` 默认 `md`（要 FreeMind 显式 `-f mm`）。
- **按格式分文件夹**：根目录平铺 77 个文件看不出结构，改为 `json/` + `md/` + `assets/` + `png/`，README 留在最外层。
  `md` 里图片是相对路径，下移一层必须改成 `../assets/`——用 `--assets-dir ../assets` **重新生成**而不是文本替换，
  并与改前备份逐行 diff：只有 9 张含图导图的 35 行图片引用变了，其余内容零差异。
  `zhimap_render.py` 的图片目录自动检测同时支持 `<json目录>/assets` 和同级 `assets/`，重渲一张与批次产物**哈希相同**。
- **新增 `notes/zhimap-export/README.md`**：说明命名规则、四类产物各自用途、生成命令、自检结论和已知限制。
- **收进一个目录**：脚本从 `static/zhimap-backup/` 挪出来，最终整棵树收敛为
  `notes/zhimap/{README.md, code/, json/, md/, assets/}`——源数据、产物、代码、方案记录是一个项目的四份材料，
  分在 `static/` 和 `notes/` 两处反而没人能找到。两份 README 合并成 `notes/zhimap/README.md` 作唯一入口，本日志留在 `code/`。
  **本文前面几节写的 `notes/zhimap-export/`、`static/zhimap-backup/` 是当时的路径，不再存在。**

校验：改默认前把 md/mm 重新生成到临时目录，与仓库里现存的 38 份**逐字节相同**，确认这次收敛没有动过 Markdown 内容。

## 九、第五轮：整图不入版本库（2026-09-25）

`png/` 38 张共 **32 MB**，而 `json/` + `md/` + `assets/` + `code/` 合计只有 8.6 MB——图接近它描绘的内容的四倍大，
且**一条命令就能重画**（`zhimap_render.py`），属于典型的可再生派生物。删。

删之前先证明"真能重画"：在新路径下把 38 份 md 重新生成到临时目录，与库内文件**逐字节相同**；
再渲一张 EBP，与批次产物 **SHA-256 相同**。两条都过了才动手删。

留下的判据一句话：**只有不可再生的东西才进仓库**。`.json` 是网站关停后就没了的那一份，其余全都能从它派生。
