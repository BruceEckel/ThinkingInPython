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

The argument is a path, the file's name (``.py`` optional), or pieces of
its path:

    python -m tools.run_one_example deque_timing
    python -m tools.run_one_example Examples/03_Foundations--Containers/deque_timing.py
    python -m tools.run_one_example Containers/deque      # pieces of the path
    python -m tools.run_one_example 18/exercise_1         # a Solutions answer
    python -m tools.run_one_example Solutions/47/research_by_hand

Each piece before the last is found, in order, inside a directory name,
the tree's included (``Solutions`` picks out ``Solutions/``,
``18`` the chapter directory). The last piece is the file: a name equal to
it beats one that only contains it. A spec matching several files lists
them and exits 2. Anything after the spec is passed to the example as its
own arguments.

The chapter listings and the Solutions answers are searched together, in
``Examples/`` and ``Solutions/``, the committed and always-synced trees
a reader browses. ``build/examples/`` and ``build/solutions/`` are searched
only if nothing there matches. No argument prints this help and exits 0:
this is a reader's helper, not a gate, so running it bare should teach
rather than fail.

Usage:
    python -m tools.run_one_example <spec> [args...]
"""

import fnmatch
import os
import subprocess
import sys
from pathlib import Path

from tools.config import (
    EXAMPLES_TREE, INLINE_NORUN_MARKER, NORUN_FILE, ROOT, SHARED_UTILS)
from tools.repo import load_glob_list

COMMITTED_EXAMPLES = ROOT / "Examples"
# Each tree, and the utils/ its listings import shared helpers from. A
# Solutions tree has no utils/ of its own and uses its chapter tree's.
TREES: dict[Path, Path] = {
    COMMITTED_EXAMPLES: COMMITTED_EXAMPLES / "utils",
    ROOT / "Solutions": COMMITTED_EXAMPLES / "utils",
    EXAMPLES_TREE: SHARED_UTILS,
    EXAMPLES_TREE.parent / "solutions": SHARED_UTILS,
}
# Searched a pass at a time: the build trees only when the committed
# ones hold no match.
PASSES: tuple[tuple[Path, ...], ...] = (
    tuple(list(TREES)[:2]), tuple(list(TREES)[2:]))


def pieces_match(pieces: list[str], dirs: list[str]) -> bool:
    """Whether each piece is inside one of `dirs`, in order."""
    at = 0
    for piece in pieces:
        while at < len(dirs) and piece not in dirs[at]:
            at += 1
        if at == len(dirs):
            return False
        at += 1
    return True


def search(spec: str) -> tuple[list[Path], list[Path]]:
    """The files `spec` names exactly, and those it names in part.

    A file named exactly has the last piece of `spec` as its stem; a file
    named in part has it inside its stem. Both need the earlier pieces
    inside its directories, in order.
    """
    pieces = [p for p in spec.removesuffix(".py").split("/") if p]
    if not pieces:
        return [], []
    *dirs_wanted, name = pieces
    for trees in PASSES:
        exact: list[Path] = []
        partial: list[Path] = []
        for tree in trees:
            if not tree.is_dir():
                continue
            for path in sorted(tree.rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                dirs = [tree.name, *path.relative_to(tree).parts[:-1]]
                if not pieces_match(dirs_wanted, dirs):
                    continue
                if path.stem == name:
                    exact.append(path)
                elif name in path.stem:
                    partial.append(path)
        if exact or partial:
            return exact, partial
    return [], []


def candidates(spec: str) -> list[Path]:
    """Every example `spec` could name. A path to a file wins; otherwise
    the exact matches beat the partial ones."""
    spec = spec.replace("\\", "/")
    for base in (Path(spec), ROOT / spec):
        if base.is_file():
            return [base.resolve()]
    exact, partial = search(spec)
    return exact or partial


def names_a_listing(word: str) -> bool:
    """Whether `word` names at least one listing exactly.

    `tip` asks this of a first word that is no task, so `tip maze_view`
    runs the listing while a mistyped task name still gets tip's own
    "no task named" message, not a search that half-matches a file.
    """
    word = word.replace("\\", "/")
    return (Path(word).is_file() or (ROOT / word).is_file()
            or bool(search(word)[0]))


def tree_root(path: Path) -> Path | None:
    """The tree `path` sits in, or None for a file outside all of them."""
    for tree in TREES:
        if path.is_relative_to(tree):
            return tree
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
        utils = os.path.relpath(TREES[tree], path.parent)
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
        trees = ", ".join(display_path(t) for t in TREES)
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
        utils = TREES[tree]
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
