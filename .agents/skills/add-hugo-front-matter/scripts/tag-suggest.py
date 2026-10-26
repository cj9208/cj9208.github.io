#!/usr/bin/env python3
"""Tag lookup / suggestion tool for the blog's Hugo front matter.

Keeps tags consistent by always reusing tags that already exist in content/.
Use BEFORE writing front matter for a new article:

    python .opencode\\skills\\add-hugo-front-matter\\scripts\\tag-suggest.py list
    python .opencode\\skills\\add-hugo-front-matter\\scripts\\tag-suggest.py search game theory
    python .opencode\\skills\\add-hugo-front-matter\\scripts\\tag-suggest.py check "Trust Collapse"

Modes:
  list                 print every existing tag with a usage count
  search <term>...     fuzzy-match terms against existing tags (reuse these!)
  check <tag>          is this exact tag already used? show closest matches
"""

import os
import re
import sys
from collections import Counter, defaultdict


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def load_tags(content_dir):
    """Return Counter of tag -> usage count by scanning content/ front matter."""
    counter = Counter()
    for root, _dirs, files in os.walk(content_dir):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            path = os.path.join(root, fname)
            raw = open(path, "rb").read()
            text = raw.decode("utf-8-sig")
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            fm = parts[1]
            in_tags = False
            for line in fm.splitlines():
                s = line.strip()
                if s == "tags:":
                    in_tags = True
                    continue
                if in_tags:
                    if s.startswith("- "):
                        val = s[2:].strip().strip("\"'")
                        if val:
                            counter[val] += 1
                    elif s:
                        in_tags = False
    return counter


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_tag(tag, terms):
    """Return (best_score, detail) for a tag against a list of query terms."""
    tag_l = tag.lower()
    tag_tokens = tokenize(tag)
    best = 0
    for term in terms:
        term_l = term.lower()
        term_tokens = tokenize(term)
        if term_l == tag_l:
            s = 100
        elif term_l in tag_l:
            s = 85
        elif tag_l in term_l:
            s = 75
        else:
            shared = tag_tokens & term_tokens
            if shared:
                s = 60 + 10 * len(shared)
            else:
                s = 0
        best = max(best, s)
    return best


def main():
    args = sys.argv[1:]
    content_dir = os.path.join(repo_root(), "content")
    if not os.path.isdir(content_dir):
        print(f"Error: content directory not found at {content_dir}", file=sys.stderr)
        sys.exit(1)

    tags = load_tags(content_dir)
    if not args or args[0] == "list":
        print(f"{len(tags)} existing tags:\n")
        for tag, n in sorted(tags.items(), key=lambda kv: (-kv[1], kv[0].lower())):
            print(f"  {n:3d} | {tag}")
        print("\nFor a new article, run:  tag-suggest.py search <keyword1> <keyword2> ...")
        return

    mode = args[0]
    rest = args[1:]

    if mode == "search":
        if not rest:
            print("Usage: tag-suggest.py search <term>...")
            sys.exit(1)
        scored = [(score_tag(t, rest), t, n) for t, n in tags.items()]
        scored.sort(key=lambda x: (-x[0], x[2], x[1].lower()))
        hits = [x for x in scored if x[0] >= 50][:12]
        if hits:
            print(f"Existing tags related to '{' '.join(rest)}' (reuse one of these verbatim):\n")
            for s, t, n in hits:
                flag = "  <-- exact" if s >= 100 else ("  <-- strong" if s >= 80 else "")
                print(f"  [{s:3d}] {t}  (used {n}x){flag}")
            print("\nPrefer the closest existing tag. Do NOT invent a near-synonym.")
        else:
            print(f"No existing tag closely matches '{' '.join(rest)}'.")
            print("You may create a NEW tag. Follow the naming rules in SKILL.md and append it")
            print("to .opencode\\skills\\add-hugo-front-matter\\tags-registry.md.")

    elif mode == "check":
        if not rest:
            print("Usage: tag-suggest.py check \"<tag>\"")
            sys.exit(1)
        q = " ".join(rest).strip()
        exact = tags.get(q)
        if exact is not None:
            print(f"Tag '{q}' already exists (used {exact}x). REUSE it verbatim.")
            return
        print(f"Tag '{q}' does not exist yet. Closest existing tags:")
        scored = [(score_tag(t, [q]), t, n) for t, n in tags.items()]
        scored.sort(key=lambda x: (-x[0], x[2], x[1].lower()))
        for s, t, n in [x for x in scored if x[0] >= 50][:6]:
            print(f"  [{s:3d}] {t}  (used {n}x)")
        print("\nIf one of these is close enough, REUSE it. Otherwise create the new tag")

    else:
        print(f"Unknown mode '{mode}'. Use: list | search <term>... | check <tag>")


if __name__ == "__main__":
    main()
