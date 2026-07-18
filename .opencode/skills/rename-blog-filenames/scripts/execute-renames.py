#!/usr/bin/env python3
"""Rename numbered bare-name files under content/blog/ using their
front-matter title, then update all references under content/.

Target files match the pattern \d+.md (e.g. 1.md, 42.md).
The numeric prefix is dropped from the new name.
"""
import os
import re
import sys


def repo_root():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )


def normalize_title(title):
    title = title.replace("\u201c", "").replace("\u201d", "")
    title = title.replace("\u300c", "").replace("\u300d", "")
    title = title.replace("\u300e", "").replace("\u300f", "")
    title = title.replace("\u300a", "").replace("\u300b", "")
    title = title.replace("\uff08", "").replace("\uff09", "")
    title = title.replace("\u3001", "")
    title = title.replace("\uff1a", "-")
    title = title.replace("\u2014\u2014", "-")
    title = title.replace("\u2014", "-")
    title = re.sub(r"(\w)\s+([\u4e00-\u9fff])", r"\1\2", title)
    title = re.sub(r"([\u4e00-\u9fff])\s+(\w)", r"\1\2", title)
    title = re.sub(r"\s+", " ", title).strip()
    title = title.replace(" ", "-")
    title = re.sub(r"[^\w\-\u4e00-\u9fff]", "-", title)
    title = re.sub(r"-+", "-", title)
    return title.strip("-") + ".md"


def get_title(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()
    m = re.search(r"title:\s*[\"'](.+?)[\"']", content)
    return m.group(1) if m else None


def main():
    root = repo_root()
    blog = os.path.join(root, "content", "blog")
    content_dir = os.path.join(root, "content")

    renames = []
    for dirpath, _dirs, files in os.walk(blog):
        for fname in files:
            if not re.match(r"^\d+\.md$", fname):
                continue
            fpath = os.path.join(dirpath, fname)
            title = get_title(fpath)
            if not title:
                print(f"  SKIP (no title): {os.path.relpath(fpath, content_dir)}")
                continue
            new_name = normalize_title(title)
            new_path = os.path.join(dirpath, new_name)
            if os.path.exists(new_path):
                print(f"  SKIP (exists): {os.path.relpath(new_path, content_dir)}")
                continue
            renames.append((fpath, new_path, fname, new_name))

    if not renames:
        print("No numbered files to rename.")
        return

    print(f"Renaming {len(renames)} files:")
    for old_path, new_path, old_name, new_name in renames:
        rel_dir = os.path.relpath(os.path.dirname(old_path), content_dir)
        print(f"  {rel_dir}/{old_name}")
        print(f"  -> {rel_dir}/{new_name}")

    confirm = input("\nProceed with rename? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    renamed = []
    for old_path, new_path, old_name, new_name in renames:
        os.rename(old_path, new_path)
        renamed.append((old_name, new_name))
        print(f"  OK: {old_name} -> {new_name}")

    # Update references
    update_count = 0
    for dirpath, _dirs, files in os.walk(content_dir):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(dirpath, fname)
            with open(fpath, "r", encoding="utf-8-sig") as f:
                content = f.read()
            modified = False
            for old_name, new_name in renamed:
                if old_name in content:
                    content = content.replace(old_name, new_name)
                    modified = True
            if modified:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  References updated: {os.path.relpath(fpath, content_dir)}")
                update_count += 1

    print(f"\nDone: {len(renamed)} renamed, {update_count} files with link updates.")


if __name__ == "__main__":
    main()
