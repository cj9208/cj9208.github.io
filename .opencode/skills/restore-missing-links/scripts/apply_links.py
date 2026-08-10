#!/usr/bin/env python3
"""Apply links from a reviewed candidates list.

Input JSON (list of dicts):
  [
    {"source": "content/blog/xxx.md", "line": 12, "title": "<exact article title>", "url": "https://cj9208.github.io/blog/..."},
    ...
  ]
`line` is the body-relative line where the title appears; it is a HINT only.
If the title is not found on that line, the whole file is searched as fallback
(this tolerates BOM / front-matter line-number drift).

Wrapping rules:
  - Normal:  title -> [title](url), keeping adjacent 《》 outside.
  - `[title]` bare-bracket: append (url) after the closing bracket.
Each modified file's `lastmod` is updated to the current time (+08:00).

Usage: python .opencode/skills/restore-missing-links/scripts/apply_links.py candidates.json
"""
import os
import re
import json
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
QUOTE_CH = "\u201c\u201d\"\u00ab\u00bb'\u2018\u2019\u300c\u300d"
COLON_CH = "\uff1a:\u2014"


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


def apply_link(line, pattern, url):
    m = re.search(pattern, line)
    if not m:
        return line, "nomatch"
    s, e = m.span()
    if s > 0 and line[s - 1] == "[" and e < len(line) and line[e] == "]":
        if e + 1 < len(line) and line[e + 1] == "(":
            return line, "already"
        new = line[: e + 1] + "(" + url + ")" + line[e + 1 :]
    else:
        new = line[:s] + "[" + m.group(0) + "](" + url + ")" + line[e:]
    return new, "ok"


def body_only(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def find_match_line(body_lines, pattern, hint_line):
    """Return (line_index, content) preferring hint_line, else first match."""
    if hint_line and 1 <= hint_line <= len(body_lines):
        if re.search(pattern, body_lines[hint_line - 1]):
            return hint_line - 1, body_lines[hint_line - 1]
    for i, ln in enumerate(body_lines):
        if re.search(pattern, ln):
            return i, ln
    return None, None


def main():
    if len(sys.argv) < 2:
        print("usage: apply_links.py candidates.json")
        sys.exit(1)
    cands = json.load(open(sys.argv[1], encoding="utf-8"))
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")

    by_file = defaultdict(list)
    for c in cands:
        by_file[c["source"]].append(c)

    modified, fails = [], []
    for src in sorted(by_file):
        full = os.path.join(ROOT, src.replace("/", os.sep))
        if not os.path.exists(full):
            fails.append((src, "FILE-MISSING"))
            continue
        text = open(full, encoding="utf-8-sig").read()
        parts = text.split("---", 2)
        body = parts[2] if len(parts) == 3 else text
        blines = body.splitlines(keepends=True)
        changed = False
        for c in by_file[src]:
            pat = pattern_for(c["title"])
            idx, content = find_match_line(blines, pat, c.get("line"))
            if idx is None:
                fails.append((src, c["title"][:40] + "  NO-MATCH"))
                continue
            raw = content[:-1] if content.endswith("\n") else content
            nl = "\n" if content.endswith("\n") else ""
            new_raw, status = apply_link(raw, pat, c["url"])
            if status == "already":
                continue
            if status == "nomatch" or new_raw == raw:
                fails.append((src, c["title"][:40] + "  NO-MATCH"))
                continue
            blines[idx] = new_raw + nl
            changed = True
        if changed:
            parts[2] = "".join(blines)
            new_text = "---".join(parts)
            new_text = re.sub(
                r"^(lastmod:\s*).*?(\s*)$",
                lambda m: m.group(1) + now + m.group(2),
                new_text, count=1, flags=re.M,
            )
            open(full, "w", encoding="utf-8", newline="").write(new_text)
            modified.append(src)
            print("MODIFIED:", src)

    print("\nmodified files:", len(modified))
    print("fails:", len(fails))
    for f in fails:
        print("  FAIL", f)


if __name__ == "__main__":
    main()
