#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bind the canonical skill tree into Qoder's skills directory.

Canonical source of truth:    .agents/skills/<name>/SKILL.md   (tracked in git)
Generated, never hand-edited: .qoder/skills                    (gitignored)

Why only .qoder gets bound:
  - Codex CLI, OpenCode and DeepSeek Harness read .agents/skills/ natively.
  - Qoder only scans .qoder/skills/, so it is the one harness needing a link.
    Verified empirically on this machine: .qoder/skills has been a symlink to
    .opencode/skills since 2026-09-24 and Qoder loaded the tree through it.
  - .claude/skills is deliberately NOT created here: OpenCode scans
    .opencode/skills, .claude/skills AND .agents/skills at project level and
    requires unique skill names across those roots, so a .claude copy would
    collide with the canonical tree. Binding Claude Code is an open decision
    (see docs/decisions/0002-skill-authoring-contract-and-backlog.md, P0-1).

Usage:
  python scripts/bind_skills.py bind     [--mode auto|junction|copy]
  python scripts/bind_skills.py check
  python scripts/bind_skills.py unbind

DELETION HAZARD: .qoder/skills is a link, not content. `rm -rf .qoder/skills`
from Git Bash/MSYS can follow the link and delete canonical files. Remove it
with `unbind` (this script) or `cmd /c rmdir .qoder\\skills`, never with
`shutil.rmtree` / `rm -rf`.
"""

import argparse
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, ".agents", "skills")
BIND = os.path.join(REPO, ".qoder", "skills")

SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata",
             "allowed-tools"}
DESC_MAX = 1024
NAME_MAX = 64

REPARSE = getattr(__import__("stat"), "FILE_ATTRIBUTE_REPARSE_POINT", 0)


def is_link(path):
    """True for a symlink or a Windows junction (reparse point)."""
    if os.path.islink(path):
        return True
    if not os.path.lexists(path):
        return False
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
    except OSError:
        return False
    return bool(attrs & REPARSE)


def skills():
    """Every directory holding a SKILL.md, in deterministic order."""
    found = []
    for root, dirs, files in os.walk(CANON):
        dirs.sort()
        if "SKILL.md" in files:
            found.append(root)
            dirs[:] = []  # a skill never nests another skill
    return sorted(found)


def parse_frontmatter(skill_md):
    """Return (top_level_keys, name, description); (None, None, None) if absent."""
    with open(skill_md, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, None
    body, closed = [], False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        body.append(line)
    if not closed:
        return None, None, None
    keys, cur = [], None
    name, desc = None, []
    for line in body:
        if line[:1] not in (" ", "\t", "-") and ":" in line:
            cur, val = line.split(":", 1)
            cur, val = cur.strip(), val.strip()
            keys.append(cur)
            if cur == "name":
                name = val
            elif cur == "description":
                desc = [val] if val else []
        elif cur == "description" and line.strip():
            desc.append(line.strip())  # folded / indented continuation
    return keys, name, " ".join(desc).strip()


def validate():
    """Return (fatal, warnings). `fatal` blocks binding; warnings do not.

    A non-spec frontmatter key or an over-long description is a debt to fix
    later, not a reason to leave the tree unbound - every harness tolerates
    it. A duplicate name or a name that disagrees with its directory is a
    fatal because the harness either errors out or silently picks one.
    """
    fatal, warn = [], []
    if not os.path.isdir(CANON):
        return ["canonical tree missing: %s" % CANON], warn
    seen = {}
    for d in skills():
        rel = os.path.relpath(d, CANON).replace("\\", "/")
        expected = os.path.basename(d)
        keys, name, desc = parse_frontmatter(os.path.join(d, "SKILL.md"))
        if keys is None:
            fatal.append("%s: no YAML frontmatter block" % rel)
            continue
        for k in keys:
            if k not in SPEC_KEYS:
                warn.append("%s: top-level key `%s` is outside the Agent "
                            "Skills spec; nest it under metadata:" %
                            (rel, k))
        if name != expected:
            fatal.append("%s: name `%s` != directory `%s`"
                         % (rel, name or "(missing)", expected))
        if len(expected) > NAME_MAX:
            fatal.append("%s: name longer than %d chars" % (rel, NAME_MAX))
        if not desc:
            warn.append("%s: empty description - it can never trigger" % rel)
        elif len(desc) > DESC_MAX:
            fatal.append("%s: description %d chars > %d limit"
                         % (rel, len(desc), DESC_MAX))
        elif len(desc) > 500:
            warn.append("%s: description %d chars - long enough to be "
                        "truncated by Claude Code's 1536 budget or Codex's "
                        "2%% catalog; put the trigger words first"
                        % (rel, len(desc)))
        if name in seen:
            fatal.append("%s: duplicate skill name `%s` (also under %s)"
                         % (rel, name, seen[name]))
        seen[name] = rel
    return fatal, warn


def remove_binding():
    if not os.path.lexists(BIND):
        return False
    if is_link(BIND):
        os.rmdir(BIND) if os.path.isdir(BIND) else os.remove(BIND)
    else:
        shutil.rmtree(BIND)
    return True


def make_link(mode):
    if mode == "junction":
        subprocess.run(["cmd", "/c", "mklink", "/J", BIND, CANON],
                       check=True, capture_output=True, text=True)
        return "junction"
    try:
        os.symlink(CANON, BIND, target_is_directory=True)
        return "symlink"
    except OSError as exc:
        print("symlink unavailable (%s) - falling back to junction" % exc)
        subprocess.run(["cmd", "/c", "mklink", "/J", BIND, CANON],
                       check=True, capture_output=True, text=True)
        return "junction"


def bind(mode):
    fatal, warn = validate()
    for w in warn:
        print("warning: " + w)
    if fatal:
        print("REFUSING to bind; %d fatal problem(s) in the canonical tree:"
              % len(fatal))
        for p in fatal:
            print("  - " + p)
        return 1
    rel_bind = os.path.relpath(BIND, REPO)
    if os.path.lexists(BIND):
        if is_link(BIND) and os.path.realpath(BIND) == os.path.realpath(CANON):
            print("already bound: %s -> .agents/skills" % rel_bind)
            return 0
        what = "link" if is_link(BIND) else "stale copy"
        remove_binding()
        print("removed %s %s (canonical tree untouched)" % (what, rel_bind))
    if mode == "copy":
        shutil.copytree(CANON, BIND,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print("copied %d skill(s) into %s" % (len(skills()), rel_bind))
    else:
        kind = make_link("junction" if mode == "junction" else "auto")
        print("%s  %s  ->  %s" % (kind, rel_bind,
                                 os.path.relpath(CANON, REPO)))
    return 0


def unbind():
    if remove_binding():
        print("unbound %s" % os.path.relpath(BIND, REPO))
        return 0
    print("nothing bound")
    return 0


def check():
    fatal, warn = validate()
    rc = 1 if fatal else 0
    if fatal:
        print("canonical tree has %d fatal problem(s):" % len(fatal))
        for p in fatal:
            print("  - " + p)
    else:
        print("canonical OK: %d skill(s) under %s"
              % (len(skills()), os.path.relpath(CANON, REPO)))
    for w in warn:
        print("warning: " + w)

    if not os.path.lexists(BIND):
        print("NOT BOUND: %s missing - run `bind`"
              % os.path.relpath(BIND, REPO))
        return 1
    if is_link(BIND):
        if os.path.realpath(BIND) == os.path.realpath(CANON):
            print("binding OK: link -> %s" % os.path.relpath(CANON, REPO))
        else:
            rc = 1
            print("WRONG TARGET: %s -> %s (expected .agents/skills)"
                  % (os.path.relpath(BIND, REPO), os.path.realpath(BIND)))
        return rc
    live = {os.path.basename(d) for d in skills()}
    copies = {d for d in os.listdir(BIND) if os.path.isdir(os.path.join(BIND, d))}
    if live ^ copies:
        rc = 1
        print("DRIFT between canonical and the %s copy: %s"
              % (os.path.relpath(BIND, REPO), ", ".join(sorted(live ^ copies))))
        print("re-run `bind`")
    else:
        print("binding OK: %d copied skill(s) in sync" % len(copies))
    for stray in (".opencode/skills", ".claude/skills"):
        if os.path.lexists(os.path.join(REPO, stray.replace("/", os.sep))):
            rc = 1
            print("DUPLICATE ROOT: %s also holds skills - OpenCode/Qoder "
                  "name collisions are possible" % stray)
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["bind", "check", "unbind"])
    ap.add_argument("--mode", choices=["auto", "junction", "copy"],
                    default="auto",
                    help="auto = symlink, fall back to junction; copy is the "
                         "last resort for a harness that ignores links")
    args = ap.parse_args()
    return {"bind": lambda: bind(args.mode),
            "unbind": unbind,
            "check": check}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
