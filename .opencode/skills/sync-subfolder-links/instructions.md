# Sync Subfolder Links

将子文件夹中的 `.md` 文件链接更新到根目录对应的 `.md` 文件中，并根据文件名推断所属标题。

## 逻辑

1. 扫描根目录下所有子文件夹，查找包含 `.md` 文件的子文件夹
2. 对于每个有 `.md` 文件的子文件夹，找到同名的根目录 `.md` 文件（如 `中国政府行为分析/` → `中国政府行为分析.md`）
3. 读取根目录 `.md` 文件中的所有 `## 标题`
4. 遍历子文件夹中的每个 `.md` 文件：
   - 如果已在根目录 `.md` 中被链接，则跳过
   - 否则根据**文件名关键词**推断应归入哪个标题：
     - 例如：社保、社保夯实 → `## 社保体系`
   - 若匹配不到时询问用户或新建标题
5. 在对应标题下添加 `* [文件名](./子文件夹/文件名.md)` 格式的链接

## 注意事项

### ⚠️ 核心原则：始终从文件系统读取文件名，切勿手动输入或字符串匹配

文件名中若包含**特殊 Unicode 字符**（如中文弯引号 `""` U+201C/U+201D），最大的陷阱是：即使肉眼看起来一样，手动输入的字符与文件系统实际存储的字符在字节层面可能不同。

**错误做法（极易出错）：**
```powershell
# ❌ 手动构造字符串与文件名匹配 — 引号字符可能不匹配！
$fn = '税费枷锁下的劳动力重构：社保夯实与"零工时代"的必然终局.md'
$f = Get-ChildItem "*.md" | Where-Object { $_.Name -eq $fn }
```

**正确做法：**
```powershell
# ✅ 使用 -match 关键字匹配（不依赖精确字符）
$files = Get-ChildItem "*.md"
foreach ($f in $files) {
    if ($f.Name -match '社保|社保夯实') { ... }
}

# ✅ 链接路径直接使用 $f.Name 和 $f.BaseName
Write-Host "* [$($f.BaseName)](./子文件夹/$($f.Name))"
```

**关键经验：**
1. **禁止手动输入含特殊字符的路径** — 始终通过 `$f.Name` 从文件系统获取
2. **使用 `-match` 按关键词分类**，而不是按完整文件名匹配
3. **`$f.BaseName` 用于显示文本**（不含扩展名），**`$f.Name` 用于链接路径**（含扩展名）
4. 使用 `[System.IO.File]::WriteAllText(path, content, [System.Text.Encoding]::UTF8)` 写入，避免多次写入引入双 BOM

**PowerShell 验证方法：**
```powershell
# 验证所有链接路径是否指向真实文件
$base = "项目根目录"
$content = Get-Content "$base\根文件.md" -Encoding UTF8
foreach ($line in $content) {
    if ($line -match '\.\(\.\/') {
        $start = $line.IndexOf('('); $end = $line.LastIndexOf(')')
        $relPath = $line.Substring($start+1, $end-$start-1)
        $fullPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($base, $relPath))
        if (-not (Test-Path $fullPath)) { Write-Host "MISSING: $relPath" }
    }
}
```
