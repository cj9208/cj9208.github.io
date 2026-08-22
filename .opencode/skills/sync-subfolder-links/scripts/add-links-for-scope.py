#!/usr/bin/env python3
"""Ensure the section _index.md of each scoped file links to it.

Also reads the 综述类文章注册表 (overview-articles-registry.md) and reports:
  - scoped articles that themselves look like 综述类文章 but are not yet registered
    (register them to keep the registry in sync), and
  - scoped articles that fall inside a registered overview article's coverage but are
    not yet referenced by it (manual editorial decision, report-only).

Used by pipeline-blog-init to wire newly added (unpushed) articles into
their section index WITHOUT re-scanning / touching already-published files.

Usage:
  python .opencode\\skills\\sync-subfolder-links\\scripts\\add-links-for-scope.py --scope <file>
  python .opencode\\skills\\sync-subfolder-links\\scripts\\add-links-for-scope.py --scope <file> --apply
  python .opencode\\skills\\sync-subfolder-links\\scripts\\add-links-for-scope.py --file content/blog/.../x.md [--apply]

Default: report-only (prints the link lines that are missing).
With --apply: insert the missing link into the section _index.md.
Both overview-article reports are always report-only; registration and placement are editorial.
"""

import argparse
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REGISTRY = os.path.join(os.path.dirname(__file__), "..", "overview-articles-registry.md")


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


def front_matter_slug(abs_path):
    """Return the slug from an article's front matter, or None."""
    try:
        text = open(abs_path, "r", encoding="utf-8-sig").read()
    except (OSError, UnicodeDecodeError):
        return None
    m = re.search(r"^slug:\s*[\"']?([^\"'\s#]+)", text, re.MULTILINE)
    return m.group(1) if m else None


def front_matter_text(abs_path):
    """Return (title, slug, body) from an article, tolerating read errors."""
    try:
        text = open(abs_path, "r", encoding="utf-8-sig").read()
    except (OSError, UnicodeDecodeError):
        return None, None, None
    title, slug = None, None
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            for line in parts[1].splitlines():
                m = re.match(r"^(title|slug):\s*(.*)$", line)
                if m:
                    val = m.group(2).strip().strip("\"'")
                    if m.group(1) == "title":
                        title = val
                    else:
                        slug = val
    return title, slug, body


OVERVIEW_KEYWORDS = ["总纲", "综述", "导论", "概论", "合集", "Overview", "总览", "系统梳理", "阅读路径", "map"]
BLOG_URL_RE = re.compile(r"https://cj9208\.github\.io/blog/[^\s)）》、]+")


def is_overview_article(abs_path, min_links=4):
    """Judge whether an article itself is a 综述类文章 (overview/survey).

    Signals: title/slug hits overview keywords, or body references many in-site
    articles. Returns (is_overview, n_links, keyword_hit).
    """
    title, slug, body = front_matter_text(abs_path)
    n_links = len(set(BLOG_URL_RE.findall(body or "")))
    keyword_hit = any(k in ((title or "") + " " + (slug or "")) for k in OVERVIEW_KEYWORDS)
    return (n_links >= min_links or keyword_hit), n_links, keyword_hit


def load_overview_registry(path):
    """Parse overview-articles-registry.md into a list of entries.

    Entry keys: title, directory, slug, covers (list), linkfmt.
    """
    entries = []
    if not os.path.isfile(path):
        return entries
    try:
        lines = open(path, "r", encoding="utf-8-sig").read().splitlines()
    except (OSError, UnicodeDecodeError):
        return entries
    cur = None
    in_covers = False
    for line in lines:
        s = line.strip()
        if s.startswith("### "):
            if cur:
                entries.append(cur)
            cur = {"title": s[4:].strip(), "directory": None, "slug": None,
                   "covers": [], "linkfmt": ""}
            in_covers = False
            continue
        if cur is None:
            continue
        if s.startswith("- 目录:"):
            cur["directory"] = s[len("- 目录:"):].strip()
            in_covers = False
        elif s.startswith("- slug:"):
            cur["slug"] = s[len("- slug:"):].strip()
            in_covers = False
        elif s.startswith("- 覆盖目录:"):
            in_covers = True
            val = s[len("- 覆盖目录:"):].strip()
            if val:
                cur["covers"].append(val)
        elif s.startswith("- 链接格式:"):
            cur["linkfmt"] = s[len("- 链接格式:"):].strip()
            in_covers = False
        elif in_covers and s.startswith("- "):
            cur["covers"].append(s[len("- "):].strip())
        elif s.startswith("- "):
            in_covers = False
    if cur:
        entries.append(cur)
    return [e for e in entries if e["directory"] and e["slug"]]


def resolve_overview_file(entry):
    """Find the overview article file in its directory by matching front matter slug."""
    d = os.path.join(REPO, entry["directory"].replace("/", os.sep))
    if not os.path.isdir(d):
        return None
    for fname in os.listdir(d):
        if not fname.endswith(".md"):
            continue
        p = os.path.join(d, fname)
        if front_matter_slug(p) == entry["slug"]:
            return p
    return None


def article_dir_in_coverage(repo_rel, covers):
    """True if the scoped article's directory is under any registered cover dir."""
    d = normalize(os.path.dirname(repo_rel))
    for c in covers:
        c = normalize(c).rstrip("/")
        if d == c or d.startswith(c + "/"):
            return True
    return False


def registered_slugs(entries):
    return {e["slug"] for e in entries if e.get("slug")}


def report_new_overview_articles(scoped_files, entries):
    """Report scoped articles that themselves look like 综述类文章 but are not yet registered."""
    known = registered_slugs(entries)
    hits = []
    for rel in sorted(scoped_files):
        abs_path = os.path.join(REPO, rel.replace("/", os.sep))
        is_ov, n_links, kw = is_overview_article(abs_path)
        if not is_ov:
            continue
        slug = front_matter_slug(abs_path)
        if slug in known:
            continue  # already registered
        hits.append((rel, n_links, kw))
    if not hits:
        return
    print("\n[疑似综述类文章，待登记] 以下 scope 内文章自身可能是综述类文章，尚未登记到注册表：")
    print("  确认后按格式追加到 overview-articles-registry.md。\n")
    for rel, n_links, kw in hits:
        print(f"  - {rel}")
        print(f"      依据: {'关键词命中' if kw else ''}{'站内链接 x%d' % n_links if n_links else ''}")
        print()


def report_overview_candidates(scoped_files, entries):
    """Report scoped articles that belong in a registered overview article but aren't linked there."""
    if not entries:
        return
    lines = []
    for rel in sorted(scoped_files):
        for entry in entries:
            if not article_dir_in_coverage(rel, entry["covers"]):
                continue
            ov = resolve_overview_file(entry)
            if ov is None:
                continue
            abs_path = os.path.join(REPO, rel.replace("/", os.sep))
            if os.path.normcase(os.path.abspath(ov)) == os.path.normcase(os.path.abspath(abs_path)):
                continue  # the scoped article IS the overview article
            slug = front_matter_slug(abs_path)
            fname = os.path.basename(abs_path)
            try:
                ov_text = open(ov, "r", encoding="utf-8-sig").read()
            except (OSError, UnicodeDecodeError):
                continue
            if slug and slug in ov_text:
                continue  # already referenced by slug
            if fname in ov_text:
                continue  # already referenced by filename/relref
            lines.append((rel, entry, slug, fname, ov))
    if not lines:
        return
    print("\n[综述类文章候选] 以下 scope 内文章位于综述类文章的覆盖目录，但综述正文尚未引用：")
    print("  是否加入、放在哪个主题分节属于编辑判断，确认后再手动编辑综述正文。\n")
    for rel, entry, slug, fname, ov in lines:
        print(f"  - {rel}")
        print(f"      -> 综述：《{entry['title']}》（{normalize(os.path.relpath(ov, REPO))}）")
        if entry["linkfmt"]:
            fmt = entry["linkfmt"].replace("<slug>", slug or fname[:-3])
            print(f"      链接格式: {fmt}")
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", default=None, help="UTF-8 scope file (repo-relative paths)")
    parser.add_argument("--file", default=None,
                        help="single repo-relative path to add index links for only that file")
    parser.add_argument("--apply", action="store_true", help="insert missing links (default: report only)")
    args = parser.parse_args()

    scope = None
    if args.file:
        scope = {args.file.strip().replace("\\", "/")}
    elif args.scope:
        scope = load_scope(args.scope)
    else:
        print("Error: provide either --scope <file> or --file <path>", file=sys.stderr)
        sys.exit(1)
    scoped_files = []
    by_index = {}

    for rel in sorted(scope):
        if not rel.startswith("content/"):
            continue
        if not rel.endswith(".md") or os.path.basename(rel) == "_index.md":
            continue
        abs_path = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        scoped_files.append(rel)
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

    if by_index:
        print(f"{sum(len(v) for v in by_index.values())} missing link(s):\n")
        for index_path, fnames in sorted(by_index.items()):
            rel_index = normalize(os.path.relpath(index_path, REPO))
            print(f"  {rel_index}")
            for fname in fnames:
                print(f"    + {link_line(fname)}")
            print()
    else:
        print("All scoped articles are already linked in their section _index.md (or have no parent index).")

    overview_entries = load_overview_registry(REGISTRY)
    report_new_overview_articles(scoped_files, overview_entries)
    report_overview_candidates(scoped_files, overview_entries)

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
