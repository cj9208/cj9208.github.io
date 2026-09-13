#!/usr/bin/env python3
"""Shared helpers for the search-blog-articles index.

Kept in a hyphen-free module name so sibling scripts (`build-index.py`,
`search.py`) can import it.
"""
import hashlib
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BLOG = os.path.join(ROOT, "content", "blog")
SKIP = {"_index.md", "progress.md"}


def content_files():
    """Return sorted absolute paths of article markdown files (excludes _index.md / progress.md)."""
    files = []
    for dirpath, _dirs, names in os.walk(BLOG):
        for fn in names:
            if fn.endswith(".md") and fn not in SKIP:
                files.append(os.path.join(dirpath, fn))
    files.sort()
    return files


def compute_fingerprint():
    """Hash of (repo-relative path + raw bytes) over every article file.

    Content-based (not mtime), so `git checkout` does not cause false staleness.
    """
    h = hashlib.sha1()
    for full in content_files():
        rel = os.path.relpath(full, ROOT).replace("\\", "/")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        with open(full, "rb") as f:
            h.update(f.read())
        h.update(b"\0")
    return h.hexdigest()
