#!/usr/bin/env python3
"""Scan content/blog/ for .md files and propose normalized filenames.

Reads each file's H1 (or front matter title as fallback) and generates
a new filename following the skill's naming rules. Outputs a grouped
rename proposal.
"""
import os
import re

CONTENT_BLOG = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "content", "blog")
)


def get_title(filepath):
    """Extract the document title.

    Uses front matter title as primary source (it is the single source of
    truth in this repo). Falls back to first body H1 if no FM exists.
    """
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Find front matter boundaries
    fm_end = -1
    if content.startswith("---"):
        second = content.find("---", 3)
        if second > 0:
            fm_end = second

    # Use front matter title as primary source
    fm_match = re.search(
        r"title:\s*[\"'](.+?)[\"']",
        content[:fm_end] if fm_end > 0 else content,
    )
    if fm_match:
        return {"source": "frontmatter", "title": fm_match.group(1)}

    # Fall back to first body H1
    body = content[fm_end + 3 :] if fm_end > 0 else content
    h1s = re.findall(r"^#[ \t]+(.+)$", body, re.MULTILINE)
    for h in h1s:
        t = h.strip()
        if len(t) >= 5 and not t.startswith("=") and not t.startswith("-"):
            return {"source": "h1", "title": t}

    return {"source": "none"}


def extract_ordering_prefix(filename):
    """Extract ordering prefix like 00_, 01_, CH01_, CH03_02_ from filename."""
    m = re.match(r"^([A-Z]*\d+(?:_\d+)*_?)", filename)
    return m.group(1) if m else ""


def normalize_title(title):
    """Convert title to a filename following the naming rules."""
    # Step 1: Remove decorative quotes
    # Full-width quotes
    title = title.replace("\u201c", "").replace("\u201d", "")
    title = title.replace("\u300c", "").replace("\u300d", "")
    title = title.replace("\u300e", "").replace("\u300f", "")
    title = title.replace("\u300a", "").replace("\u300b", "")
    title = title.replace("\u2329", "").replace("\u232a", "")
    title = title.replace("\uff08", "-").replace("\uff09", "-")  # full-width parens -> -
    title = title.replace("\u3001", "-")  # 、-> -
    title = title.replace("\u3000", "")  # full-width space

    # Step 2: Convert colons to separator
    title = title.replace("\uff1a", " - ")  # ：-> -

    # Step 3: Handle other common punctuation
    title = title.replace("\u2014\u2014", " - ")  # —— -> -
    title = title.replace("\u2014", "-")  # — -> -
    title = title.replace("\u2026", "")  # … -> remove

    # Step 4: Remove meaningless spaces around Chinese
    # e.g. "AI 工程" -> "AI工程", "Spec 固定" -> "Spec固定"
    title = re.sub(r"(\w)\s+([\u4e00-\u9fff])", r"\1\2", title)
    title = re.sub(r"([\u4e00-\u9fff])\s+(\w)", r"\1\2", title)

    # Step 5: Collapse multiple spaces
    title = re.sub(r"\s+", " ", title).strip()

    # Step 6: Replace remaining spaces and special chars with -
    # But first: preserve acronyms with intended casing
    # Then: spaces -> -, other symbols -> -
    title = title.replace(" ", "-")
    title = re.sub(r"[^\w\-\u4e00-\u9fff]", "-", title)

    # Step 7: Collapse multiple dashes
    title = re.sub(r"-+", "-", title)

    # Step 8: Strip leading/trailing dashes
    title = title.strip("-")

    return title


def process():
    all_md = []

    for root, _dirs, files in os.walk(CONTENT_BLOG):
        for fname in files:
            if not fname.endswith(".md") or fname == "_index.md":
                continue
            fpath = os.path.join(root, fname)
            rel_dir = os.path.relpath(root, CONTENT_BLOG)

            title_info = get_title(fpath)

            if title_info["source"] == "none":
                all_md.append(
                    {
                        "dir": rel_dir,
                        "old": fname,
                        "status": "ERROR: no title found",
                    }
                )
                continue

            if title_info["source"] == "ambiguous":
                all_md.append(
                    {
                        "dir": rel_dir,
                        "old": fname,
                        "status": "AMBIGUOUS",
                        "fm_title": title_info["fm_title"],
                        "h1_title": title_info["h1_title"],
                    }
                )
                continue

            title = title_info["title"]
            prefix = extract_ordering_prefix(fname)
            base = normalize_title(title)
            new_name = f"{prefix}{base}.md" if prefix else f"{base}.md"

            # Check if already well-named
            # Normalize both for comparison: keep only Chinese chars, ASCII alnum
            old_stripped = re.sub(
                r"[^a-zA-Z0-9\u4e00-\u9fff]", "", fname.replace(".md", "")
            ).lower()
            new_stripped = re.sub(
                r"[^a-zA-Z0-9\u4e00-\u9fff]", "", new_name.replace(".md", "")
            ).lower()
            already_ok = old_stripped == new_stripped or new_stripped in old_stripped

            all_md.append(
                {
                    "dir": rel_dir,
                    "old": fname,
                    "new": new_name,
                    "status": "SAME" if already_ok else "RENAME",
                    "title": title,
                }
            )

    # Group by directory
    groups = {}
    for item in all_md:
        groups.setdefault(item["dir"], []).append(item)

    # Print proposal grouped by directory
    for dirname in sorted(groups.keys()):
        items = groups[dirname]
        print(f"\n{'='*60}")
        print(f"  {dirname}/")
        print(f"{'='*60}")

        renames = [i for i in items if i["status"] == "RENAME"]
        same = [i for i in items if i["status"] == "SAME"]
        errors = [i for i in items if i["status"] not in ("RENAME", "SAME")]

        if renames:
            print(f"\n  --- {len(renames)} to rename ---")
            for item in renames:
                print(f"  {item['old']}")
                print(f"  -> {item['new']}")
                print(f"     ({item['title']})")
                print()

        if same:
            print(f"  ({len(same)} already good)")
            for item in same:
                print(f"    {item['old']}")

        for item in errors:
            print(f"  ** {item['old']}: {item['status']}")
            if "fm_title" in item:
                print(f"     FM title: {item['fm_title']}")
                print(f"     H1 title: {item['h1_title']}")

    # Summary
    total_renames = sum(1 for i in all_md if i["status"] == "RENAME")
    total_ambiguous = sum(1 for i in all_md if i["status"] == "AMBIGUOUS")
    total_same = sum(1 for i in all_md if i["status"] == "SAME")
    print(f"\n{'='*60}")
    print(
        f"Summary: {total_renames} to rename, {total_ambiguous} ambiguous, {total_same} already good"
    )
    print(f"{'='*60}\n")


if __name__ == "__main__":
    process()
