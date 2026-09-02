#!/usr/bin/env python3
"""Run one book example by hand, with the working directory and import path
the book assumes.

An example expects to run from inside its own chapter directory, so the
sibling modules and data files it opens (``../mouse/Moves.txt``) resolve.
Seventy-one of them also import a shared helper from the tree's ``utils/``
directory (``from benchmark import report``). The gate supplies both by
itself: pytest reads ``utils`` from ``pythonpath``, ty from
``extra-paths``, and run_examples.py sets PYTHONPATH on every subprocess
it starts. A reader running a file straight from the repo root gets
neither, and sees ``ModuleNotFoundError: No module named 'benchmark'``.

This script does for one file what the gate does for all of them, and
streams the output instead of capturing it. It prints the equivalent
by-hand commands first, so the mechanism stays visible rather than hiding
behind a wrapper.

The argument is a path, or just the file's name:

    python tools/run_one_example.py deque_timing
    python tools/run_one_example.py Examples/03_Foundations--Containers/deque_timing.py
    python tools/run_one_example.py Containers/deque      # any substring

A name matching several files lists them and exits 2. Anything after the
name is passed to the example as its own arguments.

``Examples/`` is searched first, since that is the committed, always-synced
tree a reader browses; ``build/examples/`` is searched only if nothing
there matches. No argument prints this help and exits 0: this is a reader's
helper, not a gate, so running it bare should teach rather than fail.

Usage:
    python tools/run_one_example.py <name-or-path> [args...]
"""

import fnmatch
import os
import subprocess
import sys
from pathlib import Path

from tools_config import EXAMPLES_TREE, INLINE_NORUN_MARKER, NORUN_FILE, ROOT
from tools_repo import load_glob_list

COMMITTED_TREE = ROOT / "Examples"
SEARCH_TREES = (COMMITTED_TREE, EXAMPLES_TREE)


def candidates(spec: str) -> list[Path]:
    """Every example `spec` could name. A path wins; otherwise the stem
    matches beat the substring matches, and Examples/ beats build/examples/.
    """
    for base in (Path(spec), ROOT / spec):
        if base.is_file():
            return [base.resolve()]
    wanted = spec.removesuffix(".py")
    for tree in SEARCH_TREES:
        if not tree.is_dir():
            continue
        exact: list[Path] = []
        partial: list[Path] = []
        for path in sorted(tree.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            if path.stem == wanted:
                exact.append(path)
            elif wanted in path.relative_to(tree).as_posix():
                partial.append(path)
        if exact or partial:
            return exact or partial
    return []


def tree_root(path: Path) -> Path | None:
    """The example tree `path` sits in: the nearest parent holding utils/."""
    for parent in path.parents:
        if (parent / "utils").is_dir():
            return parent
    return None


def is_unattended(path: Path, tree: Path | None) -> bool:
    """True if this example opens a window, reads input, or never ends."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if INLINE_NORUN_MARKER in text:
        return True
    if tree is None:
        return False
    rel = path.relative_to(tree).as_posix()
    return any(fnmatch.fnmatch(rel, pat)
               for pat in load_glob_list(NORUN_FILE))


def display_path(path: Path) -> str:
    """`path` relative to the repo root, or absolute if it lies outside."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def show_manual_form(path: Path, tree: Path | None,
                     extra: list[str]) -> None:
    """Print the two or three commands this run is standing in for."""
    run = " ".join(["uv run python", path.name, *extra])
    lines = [f"cd {display_path(path.parent)}"]
    if tree is not None:
        utils = os.path.relpath(tree / "utils", path.parent)
        utils = Path(utils).as_posix()
        if os.name == "nt":
            lines.append(f'$env:PYTHONPATH = "{utils}"')
        else:
            run = f"PYTHONPATH={utils} {run}"
    lines.append(run)
    for line in lines:
        print(f"  {line}", file=sys.stderr)
    print(file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print((__doc__ or "").strip())
        return 0

    spec, extra = argv[0], argv[1:]
    found = candidates(spec)
    if not found:
        trees = ", ".join(display_path(t) for t in SEARCH_TREES)
        print(f"No example matches {spec!r} under {trees}.")
        return 2
    if len(found) > 1:
        print(f"{spec!r} matches several examples:")
        for path in found:
            print(f"  {display_path(path)}")
        print("Give more of the path to pick one.")
        return 2

    path = found[0]
    tree = tree_root(path)
    env = dict(os.environ)
    if tree is not None:
        utils = tree / "utils"
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = (str(utils) if not existing
                             else f"{utils}{os.pathsep}{existing}")
    show_manual_form(path, tree, extra)
    if is_unattended(path, tree):
        print("This example opens a window, waits for input, or runs "
              "until you stop it.\n", file=sys.stderr)
    proc = subprocess.run([sys.executable, path.name, *extra],
                          cwd=path.parent, env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
