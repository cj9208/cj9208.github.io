#!/usr/bin/env python3
"""Compute the set of "unpushed" content files for pipeline-blog-init.

The pipeline should only touch work that has NOT been pushed to the remote:
  * files changed in local commits that are not on the upstream branch
  * files with uncommitted working-tree changes (modified / untracked)

Usage:
  python .opencode\\skills\\pipeline-blog-init\\scripts\\compute-scope.py [--out <scope-file>]

Writes a UTF-8 (no BOM) scope file, one repo-relative path per line, and
prints a summary. If the scope is empty, no file is written and the script
reports "nothing to do".
"""

import argparse
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def git(*args, check=True):
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    ).stdout


def upstream_ref():
    """Return the upstream ref (e.g. origin/main), or origin/HEAD as fallback."""
    for cmd in (
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "origin/HEAD"],
    ):
        try:
            out = git(*cmd).strip()
            if out:
                return out
        except subprocess.CalledProcessError:
            continue
    return None


def parse_porcelain_paths(status_out):
    """Parse `git status --porcelain` lines into (kind, path) with proper quote handling.

    kinds: M (modified/added/renamed), U (untracked). Deleted (D) entries are
    dropped because the file no longer exists and cannot be processed.
    Rename lines 'R  old -> new' track the new path.
    """
    paths = []
    for line in status_out.splitlines():
        if not line:
            continue
        xy = line[:2]
        if "D" in xy:
            continue  # deleted -> no longer on disk
        rest = line[3:]
        kind = "U" if xy == "??" else "M"
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        # porcelain already unquoted thanks to core.quotePath=false
        paths.append((kind, rest.strip()))
    return paths


def normalize(path):
    return path.replace("\\", "/").lstrip("./")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None, help="scope file path")
    args = parser.parse_args()

    ref = upstream_ref()
    if ref is None:
        print("Error: no upstream or origin/HEAD found; cannot compute unpushed scope.")
        sys.exit(1)

    unpushed = set()
    try:
        for line in git("diff", "--name-only", ref, "HEAD").splitlines():
            line = normalize(line)
            if line:
                unpushed.add(line)
    except subprocess.CalledProcessError:
        # ref..HEAD may fail if ref is not an ancestor; fall back to name-only vs HEAD^
        for line in git("diff", "--name-only", "HEAD^", "HEAD").splitlines():
            line = normalize(line)
            if line:
                unpushed.add(line)

    working = set()
    for _kind, path in parse_porcelain_paths(git("status", "--porcelain")):
        path = normalize(path)
        if path:
            working.add(path)

    # Only content markdown files that still exist on disk
    scope = set()
    for p in (unpushed | working):
        if p.startswith("content/") and p.endswith(".md"):
            disk = os.path.join(REPO, p.replace("/", os.sep))
            if os.path.isfile(disk):
                scope.add(p)

    out_path = args.out or os.path.join(
        tempfile_gettempdir_opencode(), "pipeline-scope.txt"
    )

    if not scope:
        print("Nothing to do: no unpushed content/ .md changes.")
        print("(No scope file written.)")
        return

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sorted(scope)) + "\n")

    print(f"Scope file written: {out_path}")
    print(f"{len(scope)} unpushed content file(s):\n")
    for p in sorted(scope):
        tag = "committed-unpushed" if p in unpushed and p not in working else "working-tree"
        print(f"  [{tag:9s}] {p}")


def tempfile_gettempdir_opencode():
    import tempfile

    return os.path.join(tempfile.gettempdir(), "opencode")


if __name__ == "__main__":
    main()
