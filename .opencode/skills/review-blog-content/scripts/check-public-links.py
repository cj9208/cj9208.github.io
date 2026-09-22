#!/usr/bin/env python3
"""校验审阅文章中的公开链接能否在 Hugo 构建输出中找到落点（防大小写/失效）.

背景: Hugo 默认把输出路径全转小写, 即使目标 front matter 的 slug 是大写
(如 CH00_Preface 也会渲染成 ch00_preface/) 也是如此; 而 GitHub Pages (Linux)
对大小写敏感, 手写公开链接时目录或 slug 大小写写错就会 404。
Windows 文件系统本身不区分大小写, 所以本脚本逐段用 os.listdir 做精确匹配,
在 Windows 上也能抓出大小写错误。

用法 (仓库根目录下运行):
  hugo --source <repo根目录> --destination <临时目录> --quiet
  python .opencode\\skills\\review-blog-content\\scripts\\check-public-links.py --file <仓库相对路径> --build-dir <临时目录>
"""

import argparse
import os
import re
import sys
import urllib.parse

SITE = "https://cj9208.github.io"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")


def extract_links(md_text):
    """按行抽取 markdown 内联链接与 autolink, 返回 [(行号, url)]."""
    found = []
    for lineno, line in enumerate(md_text.splitlines(), start=1):
        for m in LINK_RE.finditer(line):
            found.append((lineno, m.group(1).strip()))
        for m in AUTOLINK_RE.finditer(line):
            found.append((lineno, m.group(1).strip()))
    return found


def to_site_path(url):
    """公开链接/根相对链接 -> 站点路径; 站外链接与 relref 等返回 None."""
    url = url.split("#")[0].split("?")[0].strip()
    if not url:
        return None
    if url.startswith(SITE):
        path = url[len(SITE):]
    elif url.startswith("/") and not url.startswith("//"):
        path = url
    else:
        return None
    if not path.startswith("/"):
        path = "/" + path
    return urllib.parse.unquote(path)


def resolve_case_sensitive(root, site_path):
    """逐段精确匹配, 大小写不符即判为不存在。目录要求含 index.html。"""
    parts = [p for p in site_path.split("/") if p not in ("",)]
    cur = os.path.abspath(root)
    for seg in parts:
        try:
            entries = os.listdir(cur)
        except OSError:
            return False
        if seg not in entries:  # 精确匹配: Windows 上也能抓出大小写错误
            return False
        cur = os.path.join(cur, seg)
    if os.path.isdir(cur):
        try:
            entries = os.listdir(cur)
        except OSError:
            return False
        return "index.html" in entries
    return os.path.isfile(cur)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="仓库相对路径或绝对路径")
    ap.add_argument("--build-dir", required=True, help="Hugo 构建输出目录")
    ap.add_argument("--root", default=".", help="仓库根目录 (默认当前目录)")
    args = ap.parse_args()

    md_path = args.file if os.path.isabs(args.file) else os.path.join(args.root, args.file)
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    results = {}  # site_path -> {"ok": bool, "lines": [...], "raw": url}
    for lineno, url in extract_links(md_text):
        path = to_site_path(url)
        if path is None:
            continue
        entry = results.setdefault(path, {"lines": [], "raw": url, "ok": None})
        entry["lines"].append(lineno)

    for path, entry in results.items():
        entry["ok"] = resolve_case_sensitive(args.build_dir, path)

    missing = {p: e for p, e in results.items() if not e["ok"]}
    for path, entry in sorted(missing.items()):
        lines = ",".join(str(n) for n in entry["lines"])
        print(f"MISSING (lines {lines}): {entry['raw']}")

    print(f"checked {len(results)} links, {len(missing)} missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
