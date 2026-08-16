#!/usr/bin/env python3
"""Ensure the section _index.md of each scoped file links to it.

Used by pipeline-blog-init to wire newly added (unpushed) articles into
their section index WITHOUT re-scanning / touching already-published files.

Usage:
  python .opencode\\skills\\sync-subfolder-links\\scripts\\add-links-for-scope.py --scope <file>
  python .opencode\\skills\\sync-subfolder-links\\scripts\\add-links-for-scope.py --scope <file> --apply

Default: report-only (prints the link lines that are missing).
With --apply: insert the missing link into the section _index.md.
"""

import argparse
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def load_scope(scope_file):
    scope = set()
    with open(scope_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().replace("\\", "/")
            if line:
                scope.add(line)
    return scope


def normalize(path):
    return path.replace("\\", "/")


def find_parent_index(repo_path):
    """Return the _index.md in the same directory as the file, if any."""
    d = os.path.dirname(repo_path)
    candidate = os.path.join(d, "_index.md")
    return candidate if os.path.isfile(candidate) else None


def link_line(filename):
    name = filename[:-3] if filename.endswith(".md") else filename
    return f'* [{name}]({{{{< relref "./{filename}" >}}}})'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, help="UTF-8 scope file (repo-relative paths)")
    parser.add_argument("--apply", action="store_true", help="insert missing links (default: report only)")
    args = parser.parse_args()

    scope = load_scope(args.scope)
    by_index = {}

    for rel in sorted(scope):
        if not rel.startswith("content/"):
            continue
        if not rel.endswith(".md") or os.path.basename(rel) == "_index.md":
            continue
        abs_path = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        parent_index = find_parent_index(abs_path)
        if parent_index is None:
            continue
        try:
            content = open(parent_index, "r", encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"  !! cannot read {normalize(os.path.relpath(parent_index, REPO))}: {e}")
            continue
        fname = os.path.basename(abs_path)
        if fname in content:
            continue  # already linked
        by_index.setdefault(parent_index, []).append(fname)

    if not by_index:
        print("All scoped articles are already linked in their section _index.md (or have no parent index).")
        return

    print(f"{sum(len(v) for v in by_index.values())} missing link(s):\n")
    for index_path, fnames in sorted(by_index.items()):
        rel_index = normalize(os.path.relpath(index_path, REPO))
        print(f"  {rel_index}")
        for fname in fnames:
            print(f"    + {link_line(fname)}")
        print()

    if not args.apply:
        print("Report-only (no files changed). Re-run with --apply to insert these links.")
        return

    for index_path, fnames in sorted(by_index.items()):
        raw = open(index_path, "rb").read()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        content = raw.decode("utf-8-sig")
        additions = [link_line(fname) for fname in fnames]
        block = "\n" + "\n".join(additions) + "\n"
        # Insert before the first '## ' heading; otherwise append at the end.
        lines = content.splitlines(keepends=True)
        insert_at = None
        for i, line in enumerate(lines):
            if line.lstrip().startswith("## "):
                insert_at = i
                break
        if insert_at is not None:
            lines.insert(insert_at, block.lstrip("\n"))
            new_content = "".join(lines)
        else:
            if not content.endswith("\n"):
                content += "\n"
            new_content = content + block.lstrip("\n") + "\n"
        enc = new_content.encode("utf-8")
        open(index_path, "wb").write((b"\xef\xbb\xbf" + enc) if has_bom else enc)
        print(f"  updated {normalize(os.path.relpath(index_path, REPO))}")


if __name__ == "__main__":
    main()
