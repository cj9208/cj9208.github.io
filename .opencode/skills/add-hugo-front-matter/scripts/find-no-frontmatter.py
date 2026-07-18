#!/usr/bin/env python3
"""Find Hugo markdown files under content/ that lack YAML front matter.

A file is considered to have front matter if its first non-empty line
is exactly '---'.
"""

import os
import sys


def has_front_matter(filepath):
    """Check if the first non-empty line of a file is '---'.

    Strips UTF-8 BOM (\ufeff) if present, since Hugo accepts BOM-prefixed
    front matter as valid.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip().lstrip('\ufeff')
            if stripped:
                return stripped == '---'
    return False


def find_missing_front_matter(content_dir):
    """Walk content_dir and yield paths of .md files lacking front matter."""
    missing = []
    for root, _dirs, files in os.walk(content_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            if not has_front_matter(fpath):
                missing.append(fpath)
    return missing


def main():
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    )
    content_dir = os.path.join(repo_root, 'content')
    if not os.path.isdir(content_dir):
        print(f"Error: content directory not found at {content_dir}", file=sys.stderr)
        sys.exit(1)

    missing = find_missing_front_matter(content_dir)
    if missing:
        print(f"Found {len(missing)} file(s) without front matter:\n")
        for fpath in sorted(missing):
            relpath = os.path.relpath(fpath, repo_root)
            print(f"  {relpath}")
        print()
    else:
        print("All markdown files under content/ have front matter.")


if __name__ == '__main__':
    main()
