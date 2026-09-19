#!/usr/bin/env python3
"""Fail on a pattern in norun.txt or timing.txt that matches no file.

``tools/data/norun.txt`` names the listings `make run` must skip, and
``tools/data/timing.txt`` names the listings whose `#:` markers are
wall-clock claims that `validate_output.py` must never rewrite. Both are
lists of `fnmatch` patterns over a listing's path inside its tree, and
both go stale the same way: a listing is renamed, moved, or deleted, or a
chapter is renumbered, and its pattern is left behind matching nothing.

A stale pattern fails quietly, and in the wrong direction. A stale
norun entry means the renamed GUI listing is no longer skipped, which
`make run` does catch, as a timeout. A stale timing entry means the
renamed listing's timing boolean is no longer a claim: the next flip is
rewritten into the chapter with the gate green, which is the failure
timing.txt exists to prevent. Nothing reports either until it bites.

Each pattern is matched against the committed trees, ``Examples/`` and
``SolutionsCode/``. One file serves both trees, so a pattern passes when
it matches in either. The gate runs this after the drift check, so the
committed trees are known to equal what the Markdown generates.

Usage:
    python -m tools.check_skip_lists
"""

import fnmatch
import sys
from pathlib import Path

from tools.config import NORUN_FILE, ROOT, TIMING_FILE
from tools.report import Finding, report

LISTS = (NORUN_FILE, TIMING_FILE)
TREES = (ROOT / "Examples", ROOT / "SolutionsCode")


def numbered_patterns(path: Path) -> list[tuple[int, str]]:
    """(line number, pattern) pairs, read the way `load_glob_list()` does."""
    if not path.exists():
        return []
    found: list[tuple[int, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, raw in enumerate(lines, start=1):
        line = raw.split("#", 1)[0].strip()
        if line:
            found.append((number, line.replace("\\", "/")))
    return found


def tree_paths(tree: Path) -> list[str]:
    """Every file under `tree`, as the forward-slash path patterns match."""
    if not tree.is_dir():
        return []
    return [path.relative_to(tree).as_posix()
            for path in tree.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts]


def stale(lists: tuple[Path, ...] = LISTS,
          trees: tuple[Path, ...] = TREES) -> list[Finding]:
    paths = [rel for tree in trees for rel in tree_paths(tree)]
    where = " or ".join(f"{tree.name}/" for tree in trees)
    return [
        Finding(path, number,
                f"`{pattern}` matches no file in {where}")
        for path in lists
        for number, pattern in numbered_patterns(path)
        if not any(fnmatch.fnmatch(rel, pattern) for rel in paths)
    ]


def main() -> int:
    return report(
        stale(),
        clean="Every norun.txt and timing.txt pattern matches a listing.",
        problem=(
            "{n} stale pattern(s). A listing was renamed, moved, or "
            "deleted, or its chapter renumbered. Update the pattern to "
            "the listing's new path, or delete the line if the listing "
            "is gone."
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
