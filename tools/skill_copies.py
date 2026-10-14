#!/usr/bin/env python3
"""Fail if the two copies of the Python coding-style skill differ.

The book's coding-style skill exists twice: `thinking-in-python-skill.md`
at the repo root and `.claude/skills/thinking-in-python/SKILL.md`, where
Claude Code loads it. The repo sets `core.symlinks = false`, so one file
cannot link to the other, and the two are plain copies. Until this check
existed, nothing enforced that they match; the sync was a manual copy,
and an edit to one copy could sit unnoticed while the other went stale.

This check reads both files as bytes and compares them. It is not a
per-document `Check` from `tools/report.py`: those run over one Markdown
document at a time, and this compares two whole files. On a difference it
names both paths and the first line at which they diverge (where one file
is a prefix of the other, the line at which the longer file continues),
then exits 1. A missing file also fails, naming the path.

The pairs to compare live in the module-level `PAIRS` constant, so a
future second pair of copies is one more line.

Usage:
    python -m tools.skill_copies
"""

import sys
from pathlib import Path
from typing import Final
from tools.config import ROOT

PAIRS: Final[tuple[tuple[Path, Path], ...]] = (
    (
        ROOT / "thinking-in-python-skill.md",
        ROOT / ".claude" / "skills" / "thinking-in-python" / "SKILL.md",
    ),
)

ADVICE: Final = (
    "Copy one over the other; see CLAUDE.md's Pointers entry on the "
    "two skill copies."
)


def _display(path: Path) -> str:
    """The path relative to the repo root when it sits under it."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def compare(a: Path, b: Path) -> str | None:
    """A message describing how `a` and `b` differ, or None if equal."""
    for path in (a, b):
        if not path.is_file():
            return f"Skill copy is missing: {_display(path)}. {ADVICE}"
    data_a = a.read_bytes()
    data_b = b.read_bytes()
    if data_a == data_b:
        return None
    lines_a = data_a.split(b"\n")
    lines_b = data_b.split(b"\n")
    line = min(len(lines_a), len(lines_b)) + 1
    for number, (x, y) in enumerate(zip(lines_a, lines_b), start=1):
        if x != y:
            line = number
            break
    return (
        f"Skill copies differ: {_display(a)} and {_display(b)} first "
        f"differ at line {line}. {ADVICE}"
    )


def main(argv: list[str] | None = None) -> int:
    del argv  # The check takes no arguments.
    failed = False
    for a, b in PAIRS:
        message = compare(a, b)
        if message is not None:
            print(message)
            failed = True
    if failed:
        return 1
    print("Skill copies match.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
