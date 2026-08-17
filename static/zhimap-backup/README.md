# ZhiMap 导图备份说明

> 背景：zhimap.com 即将关停，此目录存放从该站导出思维导图的工具脚本。

## 脚本说明

| 文件 | 作用 |
|------|------|
| `zhimap_export_all.user.js` | 油猴(Tampermonkey)脚本，登录网站后一键导出全部导图 |
| `zhimap_convert.py` | 把导出的 JSON 转成 Markdown / FreeMind(.mm) / 纯文本 |

每张导图会产出两种格式：
- `.json`：ZhiMap 原始数据结构，最完整，可二次转换
- `.mm`：FreeMind 通用格式，XMind / 知犀 / FreeMind 可直接打开

## 方法一：油猴脚本导出（推荐）

1. 浏览器安装 **Tampermonkey** 扩展
2. 新建用户脚本，把 `zhimap_export_all.user.js` 全部内容粘进去并保存
3. 用微信登录 https://zhimap.com
4. 打开任意 ZhiMap 页面（如 https://zhimap.com/home）
5. 页面右下角出现绿色按钮「一键导出全部导图」，点击
6. 脚本会：
   - 先校验登录态（未登录会提示刷新页面）
   - 调用 `/restful/sec/usrdir/list` 读取你的**目录树**（根目录"我的导图"+所有子目录）
   - 对每个目录调用 `/restful/sec/dir_mindmap` 自动翻页，汇总**仅限你名下**的所有导图 uuid
   - 逐个调用 `load_v` 下载 `.json` + `.mm` 到浏览器下载目录
7. 浏览器若弹「允许多次下载」，选择**允许**；中途失败会在浮层标出，可再点一次重试（已成功的会跳过下载重复文件）

> 已确认接口：`dir_mindmap?directoryUuid=X&page=N&size=50` 返回 Spring 分页结构，`data.content[]` 每元素含 `publicationInfo.uuid`（导图 uuid）与 `totalPages`（翻页依据）。

## 方法二：命令行导出（不装油猴）

先登录 zhimap.com，按 F12 → Network → 任意请求里复制 Cookie：

```powershell
# 下载全部导图 JSON 并同时转换
python zhimap_convert.py download --cookie "粘贴完整Cookie" --convert
```

## 转换已下载的 JSON

```powershell
python zhimap_convert.py convert <json所在目录> -o <输出目录>
```

可用参数：`-f mm,md,txt` 控制输出格式（默认三种都输出）。

## 注意

- `.zhimap` 原生格式只有 ZhiMap 自己能打开，**关停后无效**，不要依赖它，务必导出 `.mm` 或 `.json`
- 建议导出后随手用 XMind 打开一张 `.mm` 抽查内容是否完整
- 趁网站还活着立刻备份，不要拖到关停
