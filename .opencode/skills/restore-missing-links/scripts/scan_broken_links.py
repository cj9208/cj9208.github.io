#!/usr/bin/env python3
"""Scan blog content for broken/placeholder links that survived migration.

Detects: google.com/search wrappers, empty anchors, TODO placeholders,
example.com, and bare `[title]` brackets with no URL.

Usage:  python .opencode/skills/restore-missing-links/scripts/scan_broken_links.py [--scope auto|full]
  --scope auto (default): only scan files with local-only changes (stash /
    unpushed commits / working tree); --scope full: scan all content.
"""
import os
import re
import glob
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BLOG = os.path.join(ROOT, "content", "blog")

from git_scope import changed_files  # noqa: E402

# (name, regex on the URL portion of [text](url))
PATTERNS = [
    ("google_search", re.compile(r"https?://(?:www\.)?google\.com/search")),
    ("empty_anchor", re.compile(r"^#\s*$")),
    ("empty_url", re.compile(r"^\s*$")),
    ("todo", re.compile(r"^(TODO|todo|XXX|placeholder|your-link-here)")),
    ("example", re.compile(r"https?://example\.com")),
]

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def scan(scope="auto"):
    changed = changed_files(ROOT, scope)
    md_files = [
        f
        for f in glob.glob(os.path.join(BLOG, "**", "*.md"), recursive=True)
        if os.path.basename(f) not in ("_index.md", "progress.md")
    ]
    if changed is not None:
        md_files = [f for f in md_files if os.path.relpath(f, ROOT).replace("\\", "/") in changed]
    issues = []
    for f in md_files:
        text = open(f, encoding="utf-8-sig").read()
        rel = os.path.relpath(f, ROOT)
        # strip front matter
        if text.startswith("---"):
            parts = text.split("---", 2)
            body = parts[2] if len(parts) == 3 else text
        else:
            body = text
        for lineno, line in enumerate(body.splitlines(), 1):
            for name, pat in PATTERNS:
                for m in LINK_RE.finditer(line):
                    url = m.group(2)
                    if pat.search(url):
                        issues.append((name, rel, lineno, line.strip()[:110]))
    return issues


def main():
    args = sys.argv[1:]
    scope = "auto"
    for a in args:
        if a.startswith("--scope="):
            scope = a.split("=", 1)[1]
        elif a in ("--scope", "-s"):
            scope = args[args.index(a) + 1]
    issues = scan(scope)
    if not issues:
        print(f"No broken links found (scope={scope}).")
        return
    print(f"Found {len(issues)} broken/placeholder link issues (scope={scope}):")
    for kind, rel, lineno, ctx in issues:
        print(f"  [{kind}] {rel} L{lineno}: {ctx}")


if __name__ == "__main__":
    main()
