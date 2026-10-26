#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regenerate the skill-design snapshot that docs/decisions/0002's backlog cites.

Every debt item in 0002 is a measurement (line counts, description length, how
many prohibitions a body leans on), so each carries an as-of tag: date + commit.
Change a skill's description or body and that tag goes stale. This script is
what makes re-measuring cheap enough that the tag stays honest.

Definitions (fixed here so numbers are reproducible; see 0002 rule 6):
  lines        total lines of SKILL.md, front matter included (all 19 files
               have a 4-line front matter, so subtract 4 to compare with the
               pre-script hand-measured table, which counted body only)
  desc_chars   len() of the front matter `description` value, Unicode chars
  h2           lines in the body starting with "## "
  bans         prohibition-word occurrences in the body (pattern below)
  verify       verification-load words in the body (P2-2's metric; excludes 确认)
  nf_desc      explicit "when NOT to use" marker inside `description` (R3 wants
               it there, because most harnesses inject only name+description)
  nf_body      same marker inside the body
  scripts      whether a sibling scripts/ directory exists and is non-empty

`bans` deliberately excludes bare 别 unless it is a real prohibition: 特别 /
识别 / 个别 / 别的 would otherwise inflate the count, which is exactly the
"numbers without a stated unit" failure 0002 records. `nf_*` matches only
marker phrasings, not prose hedges like 除非 / 不涉及 - the hand-measured
pre-script table counted those and overstated how many skills declare an
applicability boundary.

Usage:
  python scripts/skill_snapshot.py            # markdown table to stdout
  python scripts/skill_snapshot.py --json
"""
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, ".agents", "skills")

BAN = re.compile(
    r"不要|不得|不可|不应|不准|禁止|勿|千万别|"
    r"(?<![特别识个那这哪另内级差中区分本它各])别(?![人字样名])"
)
NOTFOR = re.compile(r"何时不用|When NOT|NOT for|Not for|不用于")
# Narrow on purpose: bare 确认 is ordinary prose in these files, so counting it
# would rank skills by their writing style rather than by verification load.
VERIFY = re.compile(r"验证|校验|复核|verify|Verify|\bchecks?\b|\bChecks?\b")
DESC = re.compile(r"^description:\s*(.*)$", re.M)


def front_matter(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    block = text[3:end + 1]
    return block, text[end + 1:]


def rows():
    for entry in sorted(os.listdir(CANON)):
        root = os.path.join(CANON, entry)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if "SKILL.md" not in filenames:
                continue
            path = os.path.join(dirpath, "SKILL.md")
            with io.open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
            fm, body = front_matter(text)
            desc = ""
            if fm:
                m = DESC.search(fm)
                if m:
                    desc = m.group(1).strip().strip("\"'")
            scripts = os.path.isdir(os.path.join(dirpath, "scripts")) and bool(
                os.listdir(os.path.join(dirpath, "scripts")))
            yield {
                "skill": entry if dirpath == root else os.path.basename(dirpath),
                "path": os.path.relpath(path, REPO).replace("\\", "/"),
                "lines": text.count("\n") + 1,
                "desc_chars": len(desc),
                "h2": len(re.findall(r"^## ", body, re.M)),
                "bans": len(BAN.findall(body)),
                "verify": len(VERIFY.findall(body)),
                "nf_desc": len(NOTFOR.findall(desc)),
                "nf_body": len(NOTFOR.findall(body)),
                "scripts": "S" if scripts else "-",
            }


def main():
    data = list(rows())
    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print("| skill | 行 | desc 字符 | H2 | 禁令 | 验证 | 反触发(desc/body) | scr |")
    print("|---|---|---|---|---|---|---|---|")
    for r in sorted(data, key=lambda x: (-x["bans"], -x["desc_chars"])):
        print("| %s | %d | %d | %d | %d | %d | %d / %d | %s |" % (
            r["skill"], r["lines"], r["desc_chars"], r["h2"],
            r["bans"], r["verify"], r["nf_desc"], r["nf_body"], r["scripts"]))
    print()
    print("count=%d  max_desc=%d  over_500_lines=%s  bans_total=%d  verify_total=%d  "
          "no_boundary_anywhere=%d/%d" % (
        len(data), max(r["desc_chars"] for r in data),
        [r["skill"] for r in data if r["lines"] > 500] or "none",
        sum(r["bans"] for r in data), sum(r["verify"] for r in data),
        sum(1 for r in data if not r["nf_desc"] and not r["nf_body"]),
        len(data)))


if __name__ == "__main__":
    main()
