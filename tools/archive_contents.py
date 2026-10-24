#!/usr/bin/env python3
"""Fail if `archive/README.md`'s Contents list and `archive/` disagree.

`archive/README.md` describes each finished working document in the
directory, one bullet per file, opening with the file's name in a code
span: "- `~exercise_review.md`: the decision queue from...". Nothing
compared that list with the directory, so on 2026-10-24 two archived
reviews, `~adversarial_review.md` and `~exercise_review.md`, turned out
never to have had an entry.

This check reads the bullets, takes the code span that opens each one as
a filename, and compares the names with the files in `archive/` other
than the README. A file with no bullet fails, and so does a bullet that
names no file (left behind when a file is renamed or deleted). It runs
in `tip check`, so the gate catches both.

Usage:
    python -m tools.archive_contents
"""

import re
import sys
from pathlib import Path
from typing import Final
from tools.config import ROOT

ARCHIVE: Final = ROOT / "archive"
README: Final = ARCHIVE / "README.md"
# A Contents bullet: a dash at column 0, then the filename in backticks.
BULLET: Final = re.compile(r"^- `([^`]+)`", re.MULTILINE)


def listed_names(readme_text: str) -> set[str]:
    """The filenames the README's bullets open with."""
    return set(BULLET.findall(readme_text))


def problems(directory: Path, readme: Path) -> list[str]:
    """One message per file missing from the list or bullet naming none."""
    files = {p.name for p in directory.iterdir()
             if p.is_file() and p != readme}
    listed = listed_names(readme.read_text(encoding="utf-8"))
    return (
        [f"archive/{name}: no bullet in archive/README.md"
         for name in sorted(files - listed)]
        + [f"archive/README.md lists `{name}`, which is not in archive/"
           for name in sorted(listed - files)]
    )


def main(argv: list[str] | None = None) -> int:
    del argv  # The check takes no arguments.
    found = problems(ARCHIVE, README)
    for message in found:
        print(message)
    if found:
        print("Add or remove the bullet in archive/README.md's Contents.")
        return 1
    print("archive/README.md lists every archived file.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
