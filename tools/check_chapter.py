#!/usr/bin/env python
"""Run the code-example gates for one chapter, and nothing else.

`make gate` checks the whole book and takes tens of seconds, most of it
spent executing every listing in all 44 chapters. When you are editing the
listings in a single chapter, almost none of that work is about your edit.
This runs the same checks a code example must pass, scoped to one chapter:

    make check-ch CH=12          # or CH=12_Techniques--Data_Classes_as_Types

The steps, in order:

1. ``extract_examples.py --write`` rebuilds ``build/examples/`` from the
   Markdown. This is whole-book (and cheap), because a chapter's listings
   import their siblings and the tree has to be consistent.
2. ``validate_output.py --update`` on this chapter alone, refreshing
   its ``#:`` markers. This is the step the full gate spends its time on,
   and the one worth narrowing.
3. The Markdown-level listing gates: blank-line density, comment periods,
   comment spacing, comment capitalization. Hand-editing a listing is what
   trips these, so they belong in an edit-loop check.
4. ``ty``, ``ruff``, and ``pytest`` over this chapter's extracted directory.

Only ``capitalize_comments.py`` still reads the whole book, since it takes
no path argument; it is fast enough not to matter.

Step 1 is fail-fast: nothing downstream means anything against a tree that
would not build. The rest all run even after one fails, so a single pass
reports every problem instead of making you rediscover them one at a time.

A prose-only chapter (no extracted directory) skips steps 4 and reports so.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from tools_config import CHAPTERS_DIR, EXAMPLES_TREE, ROOT
from tools_repo import run_capture

PY = [sys.executable]
NO_TESTS_COLLECTED = 5  # pytest's exit code for an empty directory
# Generous: a chapter of asyncio examples takes seconds, not the 30 that
# run_capture defaults to for a version probe.
MARKER_TIMEOUT = 300


def resolve(selector: str) -> Path:
    """The one chapter a number or stem prefix names."""
    matches = sorted(CHAPTERS_DIR.glob(f"{selector}*.md"))
    if not matches:
        low = selector.lower()
        matches = sorted(
            p for p in CHAPTERS_DIR.glob("*.md") if low in p.stem.lower())
    if not matches:
        raise SystemExit(f"error: no chapter matches {selector!r}")
    if len(matches) > 1:
        names = ", ".join(p.stem for p in matches)
        raise SystemExit(f"error: {selector!r} matches several: {names}")
    return matches[0]


def run(label: str, command: list[str], ok: tuple[int, ...] = (0,)) -> bool:
    proc = subprocess.run(command, cwd=ROOT)
    passed = proc.returncode in ok
    print(f"{'ok  ' if passed else 'FAIL'}  {label}")
    return passed


def run_markers(md: Path) -> bool:
    """Refresh this chapter's `#:` markers, the way `gate` does.

    `gate` runs validate_output.py with --update, so a stale marker
    self-heals rather than failing the build. This must match it: a
    preview of the gate that fails on something the gate would quietly
    fix is worse than no preview, because it sends you off to hand-edit
    output that a tool generates. An exception raised where none was
    expected still fails here, exactly as it fails there.

    Whether a marker actually moved is decided by comparing the file,
    not by reading the report. In --update mode validate_output.py
    counts every file it processed as "updated" whether or not it
    rewrote anything, so trusting that word would print the warning on
    every run and teach you to ignore it.
    """
    before = md.read_bytes()
    result = run_capture(
        [*PY, "tools/validate_output.py", "--update", str(md)],
        timeout=MARKER_TIMEOUT)
    if result is None:
        print("FAIL  output markers (validate_output.py would not start)")
        return False
    report, code = result
    passed = code == 0
    print(f"{'ok  ' if passed else 'FAIL'}  output markers")
    if not passed:
        print(report.strip())
    elif md.read_bytes() != before:
        print("      Markers were rewritten. Check `git diff Chapters/`,")
        print("      especially any marker that depends on timing.")
    return passed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chapter",
                    help="chapter number or stem prefix, e.g. 12")
    args = ap.parse_args(argv)

    md = resolve(args.chapter)
    chapter_dir = EXAMPLES_TREE / md.stem
    print(f"Checking {md.name}\n")

    if not run("extract", [*PY, "tools/extract_examples.py", "--write"]):
        return 1
    # Also refresh the committed Examples/ tree. Without this an editing
    # session leaves it behind the Markdown, and the drift shows up much
    # later as a `gate` failure about a file you no longer remember.
    if not run("sync",
               [*PY, "tools/extract_examples.py", "--write", "-o",
                "Examples"]):
        return 1

    results = [
        True, True,  # extract and sync, already known to have passed
        run_markers(md),
        run("listing format", [*PY, "tools/listing_format.py", str(md)]),
        run("comment periods", [*PY, "tools/comment_periods.py", str(md)]),
        run("comment spacing", [*PY, "tools/comment_spacing.py", str(md)]),
        run("comment caps", [*PY, "tools/capitalize_comments.py"]),
    ]

    if chapter_dir.is_dir():
        target = str(chapter_dir)
        results += [
            run("ty", ["uv", "run", "ty", "check", target]),
            run("ruff", ["uv", "run", "ruff", "check", target]),
            run("pytest",
                ["uv", "run", "pytest", "-q", target],
                ok=(0, NO_TESTS_COLLECTED)),
        ]
    else:
        print(f"skip  ty/ruff/pytest ({md.stem} extracts no examples)")

    failed = results.count(False)
    print(f"\n{len(results) - failed} passed, {failed} failed")
    if failed:
        print("Run `make gate` before committing: this checks one chapter,"
              " not the book.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
