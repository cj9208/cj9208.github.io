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

### 关于图片的检查结论

对所有 38 张导出 json 检查：
- 节点字段无 `image` 字段（仅有 title/content/link/folded/children 等）
- `content` 中无 `<img>`、无 `data:image` base64
- 38 张中仅 1 张有 1 个非空 content（备注）

结论：**这些导图本身没有插入图片**，不存在图片丢失。若确有带图导图，可能需改用 `load_e`（编辑接口，需登录）验证。

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
- 若确认某张图有图片但没导出，需用 `load_e` 接口重导验证
- 网站即将关停，**备份要趁早**，关停后 `.zhimap` 原生格式也无法再使用
