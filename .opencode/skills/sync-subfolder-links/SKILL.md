---
name: sync-subfolder-links
description: Update markdown index files so they include links to markdown files in matching subfolders, using filesystem-derived names and safe handling of special Unicode filenames.
---

# SKILL: Sync Subfolder Links

将 `content/blog` 下各层级目录中的 `_index.md` 作为目录入口页，并为同目录下的文件或子目录补充链接。

## 逻辑

1. 扫描 `content/blog` 及其子目录
2. 找到所有 `_index.md`，这些文件是当前应维护目录内容链接的位置
3. 对于每个 `_index.md` 所在目录，扫描同目录下的文件和子目录
4. 处理同目录下的普通文件：
   - 仅处理 `.md` 文件
   - 跳过当前 `_index.md`
   - 如果尚未在当前 `_index.md` 中被链接，则添加链接
   - 链接格式为 `* [文件名](./文件名.md)`，显示文本使用不带后缀的文件名
5. 处理同目录下的子目录：
   - 查找该子目录下是否存在 `_index.md`
   - 若存在且尚未在当前 `_index.md` 中被链接，则直接链接到对应 `_index.md`
   - 默认链接格式为 `* [文件夹名](./子文件夹/_index.md)`
   - 只有当该子目录中不存在 `_index.md` 时，才进入备用选择
   - 备用选择包括：让用户在该子目录中选择一个文件作为链接目标，例如 overview/introduction 页面；或改为纯文本，不添加链接
6. 若链接是否应加入、加入到哪个位置或分组方式不明确，先询问用户

## 注意事项

### 核心原则：始终从文件系统读取文件名，切勿手动输入或字符串匹配

文件名中若包含特殊 Unicode 字符时，即使肉眼看起来一样，手动输入的字符与文件系统实际存储的字符在字节层面可能不同。

**关键经验：**
1. 禁止手动输入含特殊字符的路径，始终从文件系统获取
2. 显示文本使用不含扩展名的文件名，或文件夹名本身
3. 目录链接优先基于子目录下的 `_index.md`
4. 只有当子目录不存在 `_index.md` 时，才向用户确认应链接到哪个文件，或是否改为纯文本

## 执行要求

1. 先扫描 `content/blog` 并读取所有现有 `_index.md`
2. 仅在缺失链接时补充，不要重复添加
3. 不再负责文件名清洗、规范化或重命名，这部分由独立技能处理
4. 如果链接位置、分组、归类不明确，或子目录缺少 `_index.md` 需要备用目标时，先向用户确认再修改
5. 修改后验证所有新增链接都指向真实文件或真实子目录入口
