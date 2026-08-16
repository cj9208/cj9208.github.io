#!/usr/bin/env python3
"""Find Hugo markdown files under content/ that lack YAML front matter.

A file is considered to have front matter if its first non-empty line
is exactly '---'.

Optional --scope <file>: a UTF-8 list of repo-relative paths (one per line).
When provided, only those files are checked; files outside the scope are
ignored. pipeline-blog-init passes the unpushed-work scope here.
"""

import argparse
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


def find_missing_front_matter(content_dir, scope=None):
    """Walk content_dir and yield paths of .md files lacking front matter.

    If scope (set of repo-relative forward-slash paths) is given, only files
    whose repo-relative path is inside the scope are considered.
    """
    missing = []
    for root, _dirs, files in os.walk(content_dir):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            if scope is not None:
                rel = os.path.relpath(fpath, os.path.dirname(content_dir))
                rel = rel.replace('\\', '/')
                if rel not in scope:
                    continue
            if not has_front_matter(fpath):
                missing.append(fpath)
    return missing


def load_scope(scope_file):
    """Read a UTF-8 scope file into a set of normalized repo-relative paths."""
    if not os.path.isfile(scope_file):
        print(f"Error: scope file not found: {scope_file}", file=sys.stderr)
        sys.exit(1)
    scope = set()
    with open(scope_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().replace('\\', '/')
            if line:
                scope.add(line)
    return scope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', default=None,
                        help='UTF-8 file listing repo-relative paths to restrict the scan to')
    args = parser.parse_args()

    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    )
    content_dir = os.path.join(repo_root, 'content')
    if not os.path.isdir(content_dir):
        print(f"Error: content directory not found at {content_dir}", file=sys.stderr)
        sys.exit(1)

    scope = load_scope(args.scope) if args.scope else None
    missing = find_missing_front_matter(content_dir, scope=scope)
    if missing:
        print(f"Found {len(missing)} file(s) without front matter:\n")
        for fpath in sorted(missing):
            relpath = os.path.relpath(fpath, repo_root)
            print(f"  {relpath}")
        print()
    else:
        if scope is not None:
            print("All files in scope already have front matter.")
        else:
            print("All markdown files under content/ have front matter.")


if __name__ == '__main__':
    main()
