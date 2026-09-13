#!/usr/bin/env python3
"""Build a compact, committed search index of blog articles.

Scans `content/blog/**.md` (excluding `_index.md` / `progress.md`) and extracts,
for each article:
  - front-matter metadata (title, shorttitle, slug, categories, tags, date,
    lastmod, description/summary)
  - the derived public URL (`https://cj9208.github.io/blog/<dir>/<slug>/`)
  - a short plain-text body excerpt (no full body stored -> low token cost)
  - outgoing cross-reference links to other site articles (`out_links`)

Writes `index.json` next to the skill directory. Re-run after adding, moving or
editing articles so the index stays fresh.

Usage:
    python .opencode/skills/search-blog-articles/scripts/build-index.py
"""
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogindex import ROOT, BLOG, SKIP, compute_fingerprint  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "index.json")
BASE = "https://cj9208.github.io/blog/"
EXCERPT_LEN = 200

LINK_URL_RE = re.compile(r"https?://cj9208\.github\.io/blog/([A-Za-z0-9_./-]+)/")
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
KV_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def parse_front_matter(text):
    """Minimal YAML front-matter parser (scalars + simple string lists)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_raw, body = parts[1], parts[2]
    data = {}
    cur_list = None
    for line in fm_raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m_item = LIST_ITEM_RE.match(line)
        if m_item and cur_list is not None:
            item = unquote(m_item.group(1))
            if item:
                data[cur_list].append(item)
            continue
        m = KV_RE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            cur_list = key
            data[key] = []
        else:
            cur_list = None
            data[key] = unquote(val)
    return data, body


def slugify(name):
    s = name.lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff\-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def make_excerpt(body, limit=EXCERPT_LEN):
    text = CODE_FENCE_RE.sub(" ", body)
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith(("#", ">", "|", "!", "---", "{{<", "$$")):
            continue
        lines.append(s)
        if len(" ".join(lines)) >= limit:
            break
    joined = " ".join(lines)
    joined = MD_LINK_RE.sub(r"\1", joined)
    joined = re.sub(r"[*_`~]", "", joined)
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined[:limit]


def extract_links(body):
    out, seen = [], set()
    for m in LINK_URL_RE.finditer(body):
        p = m.group(1).strip("/").lower()
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def build():
    if not os.path.isdir(BLOG):
        print("ERROR: content/blog not found at %s" % BLOG, file=sys.stderr)
        sys.exit(1)
    articles = []
    for dirpath, _dirs, files in os.walk(BLOG):
        rel_dir = os.path.relpath(dirpath, BLOG).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        for fn in files:
            if not fn.endswith(".md") or fn in SKIP:
                continue
            full = os.path.join(dirpath, fn)
            text = open(full, "rb").read().decode("utf-8-sig")
            fm, body = parse_front_matter(text)
            title = fm.get("title", "").strip() or os.path.splitext(fn)[0]
            slug = fm.get("slug", "").strip() or slugify(os.path.splitext(fn)[0])
            url_dir = rel_dir.lower()
            path = (url_dir + "/" + slug).strip("/").lower()
            url = BASE + path + "/"
            cats = fm.get("categories", [])
            tags = fm.get("tags", [])
            if isinstance(cats, str):
                cats = [cats]
            if isinstance(tags, str):
                tags = [tags]
            excerpt = make_excerpt(body)
            desc = fm.get("description") or fm.get("summary") or ""
            if desc and len(desc) > len(excerpt):
                excerpt = make_excerpt(desc) or excerpt
            entry = {
                "title": title,
                "slug": slug,
                "url": url,
                "path": path,
                "dir": ("content/blog/" + rel_dir).rstrip("/"),
                "section": rel_dir.split("/")[0] if rel_dir else "",
                "categories": cats,
                "tags": tags,
                "date": fm.get("date", ""),
                "lastmod": fm.get("lastmod", ""),
                "excerpt": excerpt,
                "out_links": extract_links(body),
            }
            if fm.get("shorttitle"):
                entry["shorttitle"] = fm["shorttitle"]
            articles.append(entry)
    articles.sort(key=lambda a: a["path"])
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    index = {
        "generated_at": now,
        "base_url": BASE,
        "source_fingerprint": compute_fingerprint(),
        "count": len(articles),
        "articles": articles,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("articles: %d" % len(articles))


if __name__ == "__main__":
    build()
