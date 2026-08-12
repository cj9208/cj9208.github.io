#!/usr/bin/env python3
"""Compute the set of repo files with local-only changes (not yet pushed to origin).

Scope sources:
  - worktree : working-tree / index changes (git status --porcelain)
  - commits  : commits on the current branch not present on origin (git log origin/<branch>..HEAD)
  - stash    : stashed changes (git stash list + git stash show)
  - auto     : union of worktree + commits only (default; stash NOT included)

Returned paths are repo-relative with POSIX separators (e.g. "content/blog/xxx.md")
so they compare cleanly with the relpath values the scanning scripts already emit.

Usage:
    from git_scope import changed_files
    changed = changed_files(ROOT, scope="auto")   # set of paths, or None for "full scan"
"""
import os
import re
import ast
import subprocess

_GIT = ["git", "-c", "core.quotepath=false"]


def _run(root, args):
    try:
        out = subprocess.run(
            _GIT + args,
            cwd=root,
            capture_output=True,
        )
    except Exception:
        return ""
    if out.returncode != 0:
        return ""
    return out.stdout.decode("utf-8", errors="replace")


def _branch(root):
    b = _run(root, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    return b or "main"


def _unquote(p):
    if p.startswith('"') and p.endswith('"'):
        try:
            return ast.literal_eval(p)
        except Exception:
            return p[1:-1]
    return p


def _parse_paths(text):
    paths = set()
    for raw in text.splitlines():
        p = raw.strip()
        if not p:
            continue
        # git status --porcelain prefixes "XY path" or "?? path"
        p = re.sub(r"^[ MADRCU?!]{1,2}\s+", "", p)
        p = _unquote(p)
        if not p:
            continue
        # porcelain v1 rename entries: "R  old -> new" -> keep the destination
        if " -> " in p:
            p = p.rsplit(" -> ", 1)[-1]
        paths.add(p.replace("\\", "/"))
    return paths


def _worktree_files(root):
    return _parse_paths(_run(root, ["status", "--porcelain", "-uall"]))


def _unpushed_files(root, branch):
    return _parse_paths(_run(root, ["log", "origin/%s..HEAD" % branch, "--name-only", "--pretty=format:"]))


def _stash_files(root):
    files = set()
    listing = _run(root, ["stash", "list"]).strip()
    if not listing:
        return files
    for i in range(len(listing.splitlines())):
        ref = "stash@{%d}" % i
        files |= _parse_paths(_run(root, ["stash", "show", "--name-only", ref]))
    return files


def changed_files(root, scope="auto"):
    """Return set of repo-relative paths (POSIX) with local-only changes.

    scope:
      auto      - union of worktree + unpushed commits only (default; stash excluded)
      worktree  - uncommitted working-tree / index changes only
      commits   - committed but not pushed to origin only
      stash     - stashed changes only
      full / all - None, meaning: scan everything (全量)
    """
    scope = (scope or "auto").lower()
    if scope in ("full", "all", "all_scan"):
        return None
    files = set()
    if scope in ("auto", "worktree"):
        files |= _worktree_files(root)
    if scope in ("auto", "commits"):
        files |= _unpushed_files(root, _branch(root))
    if scope in ("stash",):
        files |= _stash_files(root)
    return files


if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    scope = sys.argv[1] if len(sys.argv) > 1 else "auto"
    res = changed_files(ROOT, scope)
    if res is None:
        print("scope=full: scanning everything")
    elif not res:
        print("scope=%s: no local-only changed files" % scope)
    else:
        print("scope=%s: %d changed files" % (scope, len(res)))
        for p in sorted(res):
            print("  " + p)
