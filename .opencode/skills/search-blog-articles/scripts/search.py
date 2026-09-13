#!/usr/bin/env python3
"""Search the committed blog index for articles related to a topic.

Token-cheap by design: it reads only `index.json` (titles + tags + categories +
short excerpts + cross-ref links), scores candidates, and prints a small
shortlist. The caller (LLM) then reads only the shortlisted articles to judge
whether the topic is already covered.

Usage:
    python search.py --terms "reward hacking incentive design"
    python search.py "reward hacking" governance
    python search.py --terms "养老金" --section systems_and_governance
    python search.py --terms "trust" --tag "Trust Collapse" --json

Options:
    --terms TEXT     topic keywords (space/comma separated); positional terms also accepted
    --limit N        max direct matches to print (default 15)
    --tag TAG        require the article to carry this tag (repeatable, case-insensitive substring)
    --section S      restrict to a top-level section (e.g. systems_and_governance)
    --no-refresh     do not auto-rebuild a stale index (default: auto-rebuild)
    --json           emit machine-readable JSON instead of the text report
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogindex import compute_fingerprint  # noqa: E402

INDEX = os.path.join(os.path.dirname(__file__), "..", "index.json")


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def load_index():
    if not os.path.isfile(INDEX):
        print("ERROR: index.json missing. Run build-index.py first.", file=sys.stderr)
        sys.exit(1)
    with open(INDEX, encoding="utf-8") as f:
        return json.load(f)


def ensure_fresh(allow_refresh):
    """Rebuild the index if content/blog changed since the last build."""
    idx = load_index()
    if idx.get("source_fingerprint") == compute_fingerprint():
        return idx
    if not allow_refresh:
        print("WARNING: index.json is stale (content/blog changed since last build); "
              "results may be incomplete. Run build-index.py.", file=sys.stderr)
        return idx
    print("index.json stale -> rebuilding...")
    subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "build-index.py")],
        check=True,
    )
    return load_index()


def score_article(a, terms, phrase):
    score = 0
    signals = []
    tags = a.get("tags", [])
    cats = a.get("categories", [])
    title = a.get("title", "")
    title_l = title.lower()
    slug_l = a.get("slug", "").lower()
    exc_l = a.get("excerpt", "").lower()
    for term in terms:
        tl = term.lower()
        tt = tokens(term)
        for tag in tags:
            tgl = tag.lower()
            if tl == tgl:
                score += 14
                signals.append("tag=" + tag)
                break
            if tl in tgl or tgl in tl or (tt & tokens(tag)):
                score += 9
                signals.append("tag~" + tag)
                break
        for cat in cats:
            cl = cat.lower()
            if tl == cl or tl in cl or cl in tl or (tt & tokens(cat)):
                score += 7
                signals.append("cat=" + cat)
                break
        if tl in title_l:
            score += 6
            signals.append("title")
        elif tt & tokens(title):
            score += 3
            signals.append("title")
        if tl in slug_l:
            score += 4
        if tl in exc_l:
            score += 2
    if phrase and (phrase in title_l or phrase in exc_l):
        score += 8
        signals.append("phrase")
    seen, uniq = set(), []
    for s in signals:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return score, uniq


def main():
    args = sys.argv[1:]
    terms, limit, tag_filter, section, as_json = [], 15, [], None, False
    no_refresh = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--json":
            as_json = True
        elif a == "--no-refresh":
            no_refresh = True
        elif a in ("--terms", "-t") and i + 1 < len(args):
            i += 1
            terms += re.split(r"[,\s]+", args[i].strip())
        elif a == "--limit" and i + 1 < len(args):
            i += 1
            limit = int(args[i])
        elif a == "--tag" and i + 1 < len(args):
            i += 1
            tag_filter.append(args[i].strip().lower())
        elif a == "--section" and i + 1 < len(args):
            i += 1
            section = args[i].strip()
        elif not a.startswith("-"):
            terms += re.split(r"[,\s]+", a.strip())
        i += 1
    terms = [t for t in terms if t]
    if not terms:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    idx = ensure_fresh(not no_refresh)
    articles = idx["articles"]
    phrase = " ".join(terms).lower()

    matches = []
    for a in articles:
        if section and a.get("section") != section:
            continue
        if tag_filter:
            atags = [t.lower() for t in a.get("tags", [])]
            if not all(any(f in t for t in atags) for f in tag_filter):
                continue
        sc, sig = score_article(a, terms, phrase)
        if sc > 0:
            matches.append((sc, a, sig))
    matches.sort(key=lambda x: (-x[0], x[1]["path"]))
    direct = matches[:limit]

    seed_paths = {a["path"] for _s, a, _g in direct}
    out_map = {a["path"]: set(a.get("out_links", [])) for a in articles}
    in_map = defaultdict(set)
    for src, outs in out_map.items():
        for o in outs:
            in_map[o].add(src)
    neighbors = []
    for a in articles:
        p = a["path"]
        if p in seed_paths:
            continue
        sources = set()
        for o in a.get("out_links", []):
            if o in seed_paths:
                sources.add(o)
        for s in in_map.get(p, ()):
            if s in seed_paths:
                sources.add(s)
        if sources:
            neighbors.append((len(sources), a, sorted(sources)))
    neighbors.sort(key=lambda x: (-x[0], x[1]["path"]))
    neighbors = neighbors[:limit]

    tag_counter = Counter()
    sec_counter = Counter()
    for _s, a, _g in direct:
        tag_counter.update(a.get("tags", []))
        sec_counter[a.get("section", "")] += 1
    suggested_tags = [t for t, _n in tag_counter.most_common(8)]
    suggested_section = sec_counter.most_common(1)[0][0] if sec_counter else None

    if as_json:
        out = {
            "terms": terms,
            "generated_at": idx.get("generated_at"),
            "matches": [
                {"score": s, "path": a["path"], "url": a["url"], "title": a["title"],
                 "section": a.get("section"), "tags": a.get("tags"),
                 "categories": a.get("categories"), "signals": g, "excerpt": a.get("excerpt")}
                for s, a, g in direct
            ],
            "neighbors": [
                {"connections": n, "path": a["path"], "url": a["url"], "title": a["title"],
                 "section": a.get("section"), "via": v}
                for n, a, v in neighbors
            ],
            "suggested_tags": suggested_tags,
            "suggested_section": suggested_section,
        }
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    print("# Topic search: %s" % " ".join(terms))
    print("index: %d articles, generated %s" % (idx.get("count"), idx.get("generated_at")))
    if section:
        print("section filter: %s" % section)
    if tag_filter:
        print("tag filter: %s" % ", ".join(tag_filter))
    print()

    print("## Direct matches (%d)" % len(direct))
    for s, a, g in direct:
        print("[%3d] %s  (%s)" % (s, a["title"], a.get("section", "")))
        print("      slug: %s" % a["path"])
        print("      url : %s" % a["url"])
        print("      tags: %s" % ", ".join(a.get("tags", [])))
        print("      hit : %s" % ", ".join(g))
        if a.get("excerpt"):
            print("      excerpt: %s" % a["excerpt"])
        print()

    print("## Graph neighbors via cross-ref (%d)" % len(neighbors))
    for n, a, v in neighbors:
        print("[x%d] %s" % (n, a["title"]))
        print("      slug: %s" % a["path"])
        print("      url : %s" % a["url"])
        print("      via : %s" % ", ".join(v))
    print()

    print("## Suggested tags (from direct matches)")
    print("  " + ", ".join(suggested_tags) if suggested_tags else "  (none)")
    print("## Suggested section")
    print("  " + (suggested_section or "(none)"))


if __name__ == "__main__":
    main()
