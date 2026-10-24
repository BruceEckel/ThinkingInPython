#!/usr/bin/env python3
"""Fail if a module or package in `tools/` goes unnamed in `tools/README.md`.

`tools/README.md` gives each tool an entry. Nothing compared the file
with the directory, so by 2026-10-24 more than fifty modules had no
entry, some of them gated checks. The entries for all of them went in
that day (commits 8d216dc6 and 1bd13f17), and this check keeps the
file complete.

A module counts as named when the README holds its filename
(`archive_contents.py`) or its dotted name (`tools.archive_contents`).
A package (a directory under `tools/` holding Python files, such as
`story_figures/`) counts as named when the README holds its name with a
trailing slash. `__init__.py` and `__main__.py` belong to their package,
so they need no entry of their own. The check reads names alone: it
cannot tell an entry from a passing mention, so a module named only in
another tool's entry passes. It runs in `tip check`, so the gate
catches a new module whose author left the README alone.

Usage:
    python -m tools.readme_coverage
"""

import re
import sys
from pathlib import Path
from typing import Final
from tools.config import ROOT

TOOLS: Final = ROOT / "tools"
README: Final = TOOLS / "README.md"
# Files that belong to a package, not entries of their own.
PACKAGE_FILES: Final = frozenset({"__init__.py", "__main__.py"})


def modules(directory: Path) -> list[str]:
    """Module filenames directly in `directory`."""
    return sorted(p.name for p in directory.glob("*.py")
                  if p.name not in PACKAGE_FILES)


def packages(directory: Path) -> list[str]:
    """Subdirectories of `directory` that hold Python files."""
    return sorted(p.name for p in directory.iterdir()
                  if p.is_dir() and any(p.glob("*.py")))


def named(module: str, text: str) -> bool:
    """Does `text` name the module by filename or dotted name?"""
    dotted = re.escape(f"tools.{module.removesuffix('.py')}")
    return module in text or re.search(rf"{dotted}\b", text) is not None


def problems(directory: Path, readme: Path) -> list[str]:
    """One message per module or package the README never names."""
    text = readme.read_text(encoding="utf-8")
    return (
        [f"tools/{name}: not named in tools/README.md"
         for name in modules(directory) if not named(name, text)]
        + [f"tools/{name}/: not named in tools/README.md"
           for name in packages(directory) if f"{name}/" not in text]
    )


def main(argv: list[str] | None = None) -> int:
    del argv  # The check takes no arguments.
    found = problems(TOOLS, README)
    for message in found:
        print(message)
    if found:
        print("Give each one an entry in tools/README.md: what it does, "
              "which tip task runs it, and whether a gate does.")
        return 1
    print("tools/README.md names every module in tools/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
