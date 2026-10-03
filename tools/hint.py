#!/usr/bin/env python3
"""Reveal one exercise's solution a step at a time, at the command line.

The web forms of a solution (GitHub's rendering of the README and the
site's page) fold each solution into steps a reader opens one at a
time; `solution_steps.py` has the format. A reader who cloned the repo
and works in a terminal gets the same steps here:

    tip hint CH=30 N=3          # the first step: where to look
    tip hint CH=30 N=3          # the next: the shape of the listing
    tip hint CH=30 N=3          # the next: the solution
    tip hint CH=30 N=3 ARGS=--reset   # start over
    tip hint CH=30 N=3 ARGS=--all     # every step at once

Each run prints the next step and remembers where it got to, in
`build/hints.json` (derived, gitignored), keyed by chapter and
exercise. An exercise with no `Hint:` paragraph has one step, the
solution itself. The exercise statement prints every time, above the
step, so the question is always in view.

Usage:
    python -m tools.hint 30 3
    python -m tools.hint 30 3 --reset
    python -m tools.hint 30 3 --all
"""

import argparse
import json
from pathlib import Path

from tools.check_solutions import SOLUTIONS_DIR, selected
from tools.config import BUILD_DIR
from tools.exercise_statements import sections
from tools.markdown import Document
from tools.repo import solutions_file
from tools.solution_steps import Flat, Step, flat_sections, steps

PROGRESS = BUILD_DIR / "hints.json"


def load_progress() -> dict[str, int]:
    if not PROGRESS.exists():
        return {}
    try:
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_progress(progress: dict[str, int]) -> None:
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps(progress, indent=1, sort_keys=True),
                        encoding="utf-8")


def find(doc: Document, number: int) -> tuple[list[str], Flat] | None:
    """(the exercise's quoted statement, its flat form), or None."""
    flats = flat_sections(doc)
    for section in sections(doc):
        if number in section.numbers:
            quote = doc.lines[section.start:section.end]
            return quote, flats[section.numbers]
    return None


def show(step: Step, index: int, total: int) -> None:
    print(f"--- Step {index} of {total}: {step.label} ---")
    print("\n".join(step.lines))
    print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapter", help="chapter number, e.g. 30")
    ap.add_argument("exercise", type=int, help="exercise number, e.g. 3")
    ap.add_argument("--reset", action="store_true",
                    help="forget this exercise's progress and show nothing")
    ap.add_argument("--all", action="store_true",
                    help="print every step at once")
    args = ap.parse_args(argv)

    chapters = selected([args.chapter])
    if len(chapters) != 1:
        print(f"no single chapter matches {args.chapter!r}")
        return 2
    path: Path = solutions_file(chapters[0], SOLUTIONS_DIR)
    if not path.exists():
        print(f"{chapters[0].stem} has no solutions file")
        return 2
    found = find(Document.parse(path), args.exercise)
    if found is None:
        print(f"{path.parent.name} has no exercise {args.exercise}")
        return 2
    quote, flat = found
    ladder = steps(flat)
    key = f"{chapters[0].stem.split('_', 1)[0]}/{args.exercise}"
    progress = load_progress()
    if args.reset:
        progress.pop(key, None)
        save_progress(progress)
        print(f"Progress on {key} forgotten.")
        return 0

    print("\n".join(quote))
    print()
    if args.all:
        for i, step in enumerate(ladder, 1):
            show(step, i, len(ladder))
        return 0
    shown = min(progress.get(key, 0), len(ladder))
    if shown >= len(ladder):
        print("Every step is revealed. `--reset` starts over, "
              "`--all` prints them together.")
        return 0
    show(ladder[shown], shown + 1, len(ladder))
    shown += 1
    progress[key] = shown
    save_progress(progress)
    if shown < len(ladder):
        print(f"Run again for step {shown + 1}: {ladder[shown].label}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
