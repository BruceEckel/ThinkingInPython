#!/usr/bin/env python
"""Print categorized help for the Makefile, replacing `grep | awk`.

Every target line that ends with a `## text` comment becomes one help
entry; a line starting with `##@ Name` starts a new category, printed as a
heading above the entries that follow it. A target with no `## text`
comment is left out of the listing (most are internal or self-explanatory).

This exists so `make help` has no dependency on `grep`/`awk` being on PATH.
Every other target already requires Python (via `uv run`), so routing help
through it too means one less way for `make help` to fail on a machine
that has GNU Make but not a POSIX toolchain.

Usage:
    python tools/make_help.py            # read ./Makefile
    python tools/make_help.py path/to/Makefile
"""
import argparse
import re
from pathlib import Path

from tools_config import ROOT

MAKEFILE = ROOT / "Makefile"

_TARGET = re.compile(r"^([a-zA-Z_-]+):.*?##\s?(.*)$")
_CATEGORY = re.compile(r"^##@\s?(.*)$")


def entries(text: str) -> list[tuple[str, str] | tuple[None, str]]:
    """(target, doc) pairs, or (None, category) for a `##@` heading."""
    found: list[tuple[str, str] | tuple[None, str]] = []
    for line in text.splitlines():
        category = _CATEGORY.match(line)
        if category:
            found.append((None, category.group(1)))
            continue
        target = _TARGET.match(line)
        if target:
            found.append((target.group(1), target.group(2)))
    return found


def render(found: list[tuple[str, str] | tuple[None, str]]) -> str:
    width = max((len(name) for name, _ in found if name), default=0)
    lines: list[str] = []
    for name, doc in found:
        if name is None:
            lines.append(f"\n{doc}")
        else:
            lines.append(f"  {name:<{width}}  {doc}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "makefile", nargs="?", type=Path, default=MAKEFILE,
        help=f"Makefile to read (default: {MAKEFILE.name})")
    args = ap.parse_args(argv)

    print(render(entries(args.makefile.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
