# ZhiMap 导图备份

zhimap.com 即将关停，这里是账号下 **38 张思维导图**的完整本地备份，以及生成它们的全部代码。
一个目录管到底：源数据、产物、脚本、方案记录都在这。

```
notes/zhimap/                 合计约 8.6 MB
├── README.md      本说明（入口）
├── code/          脚本 + EXPLORATION.md（探索与踩坑日志）
├── json/          38 份源数据 —— 唯一事实来源，关停后不可再生
├── md/            38 份 Markdown 大纲
└── assets/        35 张节点内嵌图片
```

## 命名规则

所有产物文件都是 `根节点标题__uuid.扩展名`，例如 `EBP__829664278779475fa55d80c85916eff1.md`。

- `uuid` 是网站上的导图 ID，**唯一且不变**；标题取**根节点**（`trees[0].title`）而不是 `mindMap.title`，
  后者常是"中心主题"这类默认值，没有区分度。
- 标题可以改，改完文件名前缀跟着变，但 `uuid` 不变；同一目录里出现同名标题也不冲突。
- 同一张导图在 `json/` 和 `md/` 里前缀完全相同，按名字就能对上。
- **跨目录比对时用 uuid，别用整个文件名**：`md/` 由 `safe_name` 生成，会把标题里的连续空格压成一个。
  `covariance  estimation`（两个空格）的 json 一度看起来"缺其他格式"，其实就是同一个 uuid 的两种写法。

## 目录里有什么

| 路径 | 数量 | 是什么 | 什么时候用它 |
|------|------|--------|--------------|
| `json/` | 38 份，2.8 MB | **源数据**。`load_v` 接口返回的原始存档，`data.mindMap.trees` 是完整节点树（富文本 HTML、颜色、公式、图片引用、折叠标记都在） | 唯一不可再生的东西，重转换、重渲染都从它出发 |
| `md/` | 38 份 | **大纲**。根节点是唯一一行 `# 标题`，其余各层是缩进的 `-` 列表；公式还原成 LaTeX 原文（`$tex$`），图片走相对路径 `../assets/` | 日常阅读、搜索、复制进笔记；也是校对内容有没有丢的基准 |
| `assets/` | 35 张，5.4 MB | 节点里**内嵌的图片**（原站 `/res/...`，已本地化）。basename 是原始数字 ID，全局唯一，所以平铺一层 | `md/` 的图片引用指向这里，别单独移动 |

规则很简单：**只有不可再生的东西才留在仓库里**。三样派生产物因此被删掉了：

- `.txt` 纯文本大纲——完全由 `.md` 派生，零新增信息。
- `.mm`（FreeMind/XMind）——`.json` 的有损重编码，丢图片和公式排版；要喂给别的工具随时 `convert -f mm` 重新派生。
- `png/` 38 张整图——32 MB，接近其余全部内容（8.6 MB）的四倍，而一条命令就能重画（见下）。

## 重新生成

命令都在仓库根目录跑。前两步的产物在版本库里，第三条按需出图：

```bash
# 1) 下载源 JSON（网站关停前已抓完，不用再跑，也别再覆盖 json/）
python notes/zhimap/code/zhimap_convert.py download --cookie '<登录后浏览器里的完整 Cookie>' -o notes/zhimap/json

# 2) JSON -> Markdown。--assets-dir 决定 md 里图片引用的相对路径（md 在子目录，所以写 ../assets）；
#    加 --fetch-assets 会先把内嵌图片下载到 -o 与 --assets-dir 拼出的目录，也就是这里的 assets/
python notes/zhimap/code/zhimap_convert.py convert notes/zhimap/json \
    -o notes/zhimap/md --assets-dir ../assets
```

转换脚本另有 `-f md,mm` 控制格式、`--remote` 让 md 直接引用原站图片 URL（关停后失效，不建议）。

### 想要整图时（一次性产物，不进仓库）

```bash
python notes/zhimap/code/zhimap_render.py notes/zhimap/json -o <临时输出目录>
```

需要本机 Chrome；图片目录自动取 `json/` 的同级 `assets/`。
常用参数：`--scale`（倍率，默认 2）、`--max-px`（长边上限，默认 9000，最低降到 1:1）、
`--only 关键字`（只渲某几张）、`--keep-html`（留中间 HTML 便于排查）。

## code/ 里的东西

| 文件 | 作用 |
|------|------|
| `zhimap_export_all.user.js` | 油猴脚本，登录网站后一键导出全部导图 JSON |
| `zhimap_convert.py` | JSON → Markdown / FreeMind，顺带下载节点内嵌图片；也能带 Cookie 直接下载 JSON |
| `zhimap_render.py` | JSON → 自包含 HTML（页内量尺寸 → tidy-tree 排版 → SVG 连线）→ 无头 Chrome 截图 → PIL 按背景色裁边 |
| `EXPLORATION.md` | 五轮探索的记录：接口结论、踩过的坑、每次改格式和删产物的理由 |

PNG 之所以要自己排版渲染：官网的 `/restful/sec/export?type=png` 按存档的**折叠状态**出图（收起的分支只剩 `...`），
画布还锁死 1600×1130，`scale/width/dpi/hd` 一律无效——拿不到"完全展开 + 高清"。

## 当初怎么把数据弄出来的

两种办法，都还需要登录态（图片路径 `/res/...` 例外，公开可取）：

1. **油猴脚本**（推荐）：装 Tampermonkey → 粘 `zhimap_export_all.user.js` → 登录 zhimap.com → 任意页面右下角「一键导出全部导图」。
   脚本先校验登录，再用 `/restful/sec/usrdir/list` 读目录树、`/restful/sec/dir_mindmap?directoryUuid=X&page=N&size=50` 翻页汇总你名下全部 uuid，逐个 `load_v` 下载。
2. **命令行**：F12 复制 Cookie，`zhimap_convert.py download --cookie "..." --convert`。

## 自检结论

留在库里的内容：

- 节点数：38 张共 **4274 个节点**，逐张比对 `json/` 与 `md/` 条目数，38/38 一致（折叠分支也全展开，没丢内容）。
- 图片：`md/` 里 35 处引用，本地缺失 0；残留 `/res/` 远程路径 0。

渲染脚本（2026-09-25 全量跑过一次 38 张，产物已删，结论仍然有效）：

- 38/38 成功，每张渲染后回读页面自检，`data-badmath`（未排版公式数）与 `data-overlaps`（节点两两重叠数）合计均为 0。
- 成图尺寸：长边中位数约 3000 px，28 张在 2000~9000 px，8 张小图不足 2000 px；
  两张巨型图 RAG 2738×30788、FRM 2920×25038（`--max-px` 最低只能降到 1:1，再压就糊）。

## 已知限制与注意

- 重画出来的 PNG 是**排版重建**：配色、字体与官网不完全一样，分支左右位置按存档的 `side` 字段还原，个别图视觉布局有出入（内容一致）。
- 超大图（RAG、FRM）单张超过 2 万像素，查看器会缩放显示，也未做分页/分块；看细节仍应回 `md/`。
- `json/` 里的 `theme` 字段本身还是个 JSON 字符串（网站的结构），别直接当对象用。
- `.zhimap` 原生格式只有 ZhiMap 自己能打开，关停后无效，所以归档以 `json/` 为准。
- `notes/` 在本仓库是 git 跟踪的公开内容：只放不可再生的产物和代码，临时文件（含重画出的 PNG）别往这里丢。
