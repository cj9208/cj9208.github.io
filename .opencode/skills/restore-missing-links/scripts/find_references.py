#!/usr/bin/env python3
"""Find unlinked references to other blog articles by reverse-searching titles.

Approach (no LLM needed):
  1. Build an inventory of canonical article pages from the *built* site
     (`public/blog/**/index.html`), excluding section landing pages.
  2. For every article body, look for full-title fragments (and main-title
     fragments when wrapped in 「《》」/bold) that are NOT inside a link.
  3. Emit `references_report.json` (machine readable) and
     `references_report.txt` (grouped by file, for human review).

Prereq: run `hugo --gc --minify` first so `public/` is up to date.

Usage: python .opencode/skills/restore-missing-links/scripts/find_references.py
Output: references_report.json / references_report.txt in the CWD
"""
import os
import re
import json
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PUB = os.path.join(ROOT, "public", "blog")
BLOG = os.path.join(ROOT, "content", "blog")

QUOTE_CH = "\u201c\u201d\"\u00ab\u00bb'\u2018\u2019\u300c\u300d"
COLON_CH = "\uff1a:\u2014"  # ： : —

QUOTE_RE = re.compile(r'["\'\u201c\u201d\u2018\u2019\u300c\u300d\u300a\u300b《》\u3001]')


def norm(s):
    return re.sub(r"\s+", "", re.sub(QUOTE_RE, "", s))


def body_only(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def src_title_norm(text):
    if not text.startswith("---"):
        return ""
    fm = text.split("---", 2)[1]
    m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
    return norm(m.group(1)) if m else ""


def build_inventory():
    section_urls = set()
    for dp, _dn, fns in os.walk(BLOG):
        if "_index.md" in fns:
            rel = os.path.relpath(dp, BLOG).replace("\\", "/")
            section_urls.add("https://cj9208.github.io/blog/" + rel.lower() + "/")
            section_urls.add("https://cj9208.github.io/blog/")
    inventory = {}
    if not os.path.isdir(PUB):
        print("ERROR: public/blog missing. Run `hugo --gc --minify` first.")
        raise SystemExit(1)
    for dirpath, _dn, filenames in os.walk(PUB):
        if os.path.basename(dirpath) == "page" or "index.html" not in filenames:
            continue
        content = open(os.path.join(dirpath, "index.html"), encoding="utf-8", errors="replace").read()
        m = re.search(r'<meta name=robots content="([^"]+)"', content)
        if not m or "index" not in m.group(1):
            continue
        t = re.search(r"<title>(.*?)</title>", content)
        if not t:
            continue
        title = t.group(1).strip().replace(" | Jack&#39;s Blog", "").replace(" | Jack's Blog", "")
        url = "https://cj9208.github.io/blog" + dirpath.replace(PUB, "").replace("\\", "/") + "/"
        if url in section_urls:
            continue
        main = title.split("：")[0] if "：" in title else title.split(":")[0]
        inventory[url] = {"title": title, "url": url, "norm_full": norm(title), "norm_main": norm(main)}
    return inventory


LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
RELREF_RE = re.compile(r"\{\{<\s*relref[^}]*>\}\}")
CODE_RE = re.compile(r"`[^`]*`")


def pattern_for(title):
    out = []
    for ch in title:
        if ch in QUOTE_CH:
            out.append("[%s]*" % "".join(re.escape(c) for c in QUOTE_CH))
        elif ch in COLON_CH:
            out.append("[%s]" % "".join(re.escape(c) for c in COLON_CH))
        elif ch.isspace():
            out.append(r"\s*")
        else:
            out.append(re.escape(ch))
    return "".join(out)


def main():
    inventory = build_inventory()
    targets = [inv for inv in inventory.values() if len(inv["norm_full"]) >= 5]
    hits = []
    for dp, _dn, fns in os.walk(BLOG):
        for fn in fns:
            if not fn.endswith(".md") or fn in ("_index.md", "progress.md"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, ROOT)
            text = open(full, encoding="utf-8-sig").read()
            body = body_only(text)
            src_norm = src_title_norm(text)
            for lineno, raw in enumerate(body.splitlines(), 1):
                links = [(lt, lu) for lt, lu in LINK_RE.findall(raw)]
                stripped = CODE_RE.sub(" ", LINK_RE.sub(" ", RELREF_RE.sub(" ", raw)))
                plain = norm(stripped)
                if not plain:
                    continue
                for t in targets:
                    if src_norm == t["norm_full"]:
                        continue
                    if t["norm_full"] in plain:
                        already = any(norm(lu) == t["url"] for lt, lu in links)
                        linked_else = any(t["norm_full"] in norm(lt) and norm(lu) != t["url"] for lt, lu in links)
                        has_wrap = bool(re.search(r"[《》\u300a\u300b]", stripped))
                        hits.append({
                            "source": rel, "line": lineno, "url": t["url"], "title": t["title"],
                            "conf": "HIGH" if t["norm_full"] in plain else "MED",
                            "kind": "ALREADY-LINKED" if already else ("LINKED-WRONG" if linked_else else "UNLINKED"),
                            "has_wrap": has_wrap,
                            "context": stripped.strip()[:140],
                        })
                        break
    json.dump(hits, open("references_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    groups = defaultdict(list)
    for h in hits:
        groups[(h["source"], h["url"])].append(h)
    out = []
    for (src, url), hs in sorted(groups.items()):
        real = [h for h in hs if h["kind"] == "UNLINKED"]
        if not real:
            continue
        confs = {h["conf"] for h in real}
        conf = "HIGH" if "HIGH" in confs else "MED"
        out.append("### [%s] %s  L%s  (x%d)" % (conf, hs[0]["title"], ",".join(str(h["line"]) for h in real), len(real)))
        out.append("    url : %s" % url)
        for h in real[:2]:
            out.append("    ctx : %s" % h["context"])
    open("references_report.txt", "w", encoding="utf-8").write("\n".join(out))
    print("inventory targets:", len(targets))
    print("raw hits:", len(hits))
    print("unlinked groups:", len(groups))
    print("wrote references_report.json / references_report.txt")


if __name__ == "__main__":
    main()
