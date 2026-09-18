#!/usr/bin/env python3
"""Start every example that needs a human, all at once (`make by-hand`).

`make run` skips the examples in ``tools/data/norun.txt``: they open a
window, and nothing unattended can close it. No gate ever executes those
files, so a view that raises an exception on startup, or on the first
click, fails without anyone seeing it. This tool is the check a human
runs instead. It starts each one as its own process, from its own
chapter directory with the tree's ``utils/`` on ``PYTHONPATH`` (the
setup `make run-one` builds), and waits. Try each window, close it, and
the tool prints a line as each process ends. When the last one closes it
prints the traceback of every example that exited nonzero, and exits 1
if any did.

Which entries start is decided inside ``norun.txt``. Only the patterns
under a ``# [by-hand]`` comment header are started; the section ends at
the next ``# [name]`` header or at the end of the file. The header is a
comment, so `run_examples.py` and `run_one_example.py`, which read the
file through `repo.load_glob_list()`, skip every pattern in the file as
before. The entries above the header stay out: chapter 6's package
submodules are listed because running one as a script is the failure
that chapter documents, and there is nothing to watch.

Everything starts at once because a window reads nothing from the
terminal. An example that waits on ``input()`` could not share a
terminal with another one; none is listed today, and one that is added
belongs under a header of its own with a launcher that runs them one at
a time.

A pattern under the header that matches no file is stale (a renamed or
deleted listing), and is reported; ``--list`` exits 1 on one, so it can
serve as a check.

Usage:
    python -m tools.by_hand           # start them all and wait
    python -m tools.by_hand --list    # print what would start; opens nothing
"""

import argparse
import fnmatch
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import IO

from tools.config import NORUN_FILE, ROOT

TREE = ROOT / "Examples"
HEADER = "# [by-hand]"
POLL_SECONDS = 0.2


def by_hand_patterns(text: str) -> list[str]:
    """The glob patterns under the `# [by-hand]` header of a norun file."""
    patterns: list[str] = []
    inside = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("# [") and stripped.endswith("]"):
            inside = stripped == HEADER
            continue
        line = raw.split("#", 1)[0].strip()
        if inside and line:
            patterns.append(line.replace("\\", "/"))
    return patterns


def resolve(patterns: list[str],
            tree: Path) -> tuple[list[Path], list[str]]:
    """The files the patterns match under `tree`, and the stale patterns."""
    files = sorted(tree.rglob("*.py")) if tree.is_dir() else []
    found: list[Path] = []
    stale: list[str] = []
    for pattern in patterns:
        hits = [path for path in files
                if fnmatch.fnmatch(path.relative_to(tree).as_posix(),
                                   pattern)]
        if not hits:
            stale.append(pattern)
        found += [path for path in hits if path not in found]
    return found, stale


@dataclass
class Running:
    path: Path
    proc: subprocess.Popen[bytes]
    errors: IO[bytes]


@dataclass(frozen=True)
class Outcome:
    path: Path
    returncode: int
    errors: str


def start(path: Path, tree: Path) -> Running:
    env = dict(os.environ)
    utils = tree / "utils"
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (str(utils) if not existing
                         else f"{utils}{os.pathsep}{existing}")
    errors = tempfile.TemporaryFile()
    proc = subprocess.Popen([sys.executable, path.name], cwd=path.parent,
                            env=env, stderr=errors)
    return Running(path, proc, errors)


def finish(running: Running, returncode: int) -> Outcome:
    running.errors.seek(0)
    text = running.errors.read().decode("utf-8", errors="replace")
    running.errors.close()
    return Outcome(running.path, returncode, text.strip())


def run_all(paths: list[Path], tree: Path) -> list[Outcome]:
    """Start every path, wait for all of them, report each as it ends."""
    waiting = [start(path, tree) for path in paths]
    done: list[Outcome] = []
    try:
        while waiting:
            for running in list(waiting):
                returncode = running.proc.poll()
                if returncode is None:
                    continue
                waiting.remove(running)
                done.append(finish(running, returncode))
                print(f"  closed  {running.path.name}  "
                      f"(exit {returncode}, {len(waiting)} still open)")
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nInterrupted: stopping what is still open.")
        for running in waiting:
            running.proc.terminate()
            done.append(finish(running, running.proc.wait()))
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Start every example that needs a human, all at once.")
    parser.add_argument("--list", action="store_true",
                        help="print what would start, and start nothing")
    args = parser.parse_args(argv)

    patterns = by_hand_patterns(NORUN_FILE.read_text(encoding="utf-8"))
    paths, stale = resolve(patterns, TREE)
    for pattern in stale:
        print(f"Stale pattern under {HEADER} in {NORUN_FILE.name}: "
              f"{pattern} matches nothing in {TREE.name}/")
    if args.list:
        for path in paths:
            print(path.relative_to(ROOT).as_posix())
        return 1 if stale else 0
    if not paths:
        print(f"Nothing is listed under {HEADER} in {NORUN_FILE.name}.")
        return 1 if stale else 0

    print(f"Starting {len(paths)} examples. Try each window, then close "
          "it; Ctrl+C here stops whatever is still open.")
    for path in paths:
        print(f"  {path.relative_to(ROOT).as_posix()}")
    outcomes = run_all(paths, TREE)
    failed = [outcome for outcome in outcomes if outcome.returncode != 0]
    for outcome in failed:
        print(f"\n{outcome.path.relative_to(ROOT).as_posix()} "
              f"exited {outcome.returncode}:")
        print(outcome.errors or "  (nothing on stderr)")
    print(f"\n{len(outcomes) - len(failed)} of {len(outcomes)} "
          "closed cleanly.")
    return 1 if failed or stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
