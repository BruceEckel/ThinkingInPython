#!/usr/bin/env python3
"""Upgrade the project's Python and resync the environment.

With no argument, fetch the latest patch of the minor pinned in
``.python-version`` (e.g. the newest 3.14.x). With a minor argument
such as ``3.15``, first repin: rewrite ``.python-version`` and the
``requires-python`` floor in ``pyproject.toml``, then sync.

Run via ``make upgrade-python``, which executes it outside the project
venv. ``uv sync`` rebuilds that venv, so the running interpreter must
not be it. ruff infers its target from ``requires-python``, so there
is no separate version to bump.

Usage:
    python tools/upgrade_python.py        # latest patch of the minor
    python tools/upgrade_python.py 3.15   # move to the 3.15 minor
"""

import re
import sys

from tools_config import PYVER, ROOT
from tools_repo import run_echoed, write_text_lf

PYPROJECT = ROOT / "pyproject.toml"
MINOR_RE = re.compile(r"(\d+\.\d+)(.*)")


def pinned() -> tuple[str, str]:
    """Return (minor, suffix), e.g. ('3.14', '+gil')."""
    m = MINOR_RE.match(PYVER.read_text(encoding="utf-8").strip())
    if not m:
        sys.exit(f"Cannot parse a minor version from {PYVER}")
    return m.group(1), m.group(2)


def repin(old_minor: str, suffix: str, new_minor: str) -> None:
    """Move the minor pin and requires-python floor to new_minor."""
    write_text_lf(PYVER, f"{new_minor}{suffix}\n")
    text = PYPROJECT.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r'(requires-python\s*=\s*">=)\d+\.\d+(")',
        rf"\g<1>{new_minor}\g<2>", text, count=1,
    )
    if n != 1:
        sys.exit("No requires-python floor found in pyproject.toml")
    write_text_lf(PYPROJECT, new_text)
    print(
        f"Repinned {old_minor} -> {new_minor} "
        "in .python-version and requires-python."
    )


def main(argv: list[str]) -> int:
    minor, suffix = pinned()
    target = argv[0] if argv else minor
    if not re.fullmatch(r"\d+\.\d+", target):
        sys.exit(f"Target must be a minor like 3.15, got {target!r}")

    if target != minor:
        repin(minor, suffix, target)

    # install handles a brand-new minor; upgrade pulls the latest
    # patch of an existing one. Both are idempotent. sync follows.
    run_echoed(["uv", "python", "install", target], check=True)
    run_echoed(["uv", "python", "upgrade", target], check=True)
    run_echoed(["uv", "sync"], check=True)
    print("Now using: ", end="", flush=True)
    run_echoed(["uv", "run", "python", "--version"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
