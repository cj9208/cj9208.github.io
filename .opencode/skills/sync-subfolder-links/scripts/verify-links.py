#!/usr/bin/env python3
"""Verify all relref links in _index.md files point to real files."""
import os
import re

CONTENT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "content")
)
errors = 0

for root, _dirs, files in os.walk(CONTENT):
    for fname in files:
        if fname != "_index.md":
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, "r", encoding="utf-8-sig") as f:
            content = f.read()
        for m in re.finditer(r'\{\{<\s*relref\s+"(.+?)"\s*>\}\}', content):
            ref = m.group(1)
            target = os.path.normpath(os.path.join(root, ref))
            if not os.path.exists(target):
                print(f"  BROKEN: {os.path.relpath(fpath, CONTENT)} -> {ref}")
                errors += 1

if errors == 0:
    print("All relref links verified OK.")
else:
    print(f"Found {errors} broken links.")
