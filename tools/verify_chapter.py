#!/usr/bin/env python
"""Run the verify loop for one chapter and its Solutions file.

`make verify` fixes line endings, refreshes every `#:` marker, syncs both
generated trees, and runs the whole gate: tens of seconds, nearly all of
it spent on chapters you did not touch. After editing one chapter this
runs the same loop scoped to that chapter and its Solutions file:

    make verify-ch CH=28        # or CH=28_Patterns--Function_Objects

The steps, in order, mirror `verify` (fixers first, markers before sync):

1. ``check_line_endings --fix`` over the tree (whole-repo, cheap).
2. ``reflow_prose --write`` on the chapter. Not on the Solutions file:
   the gate reflows ``Chapters/`` only, and Solutions prose is wrapped
   at a column, so reflowing it here would rewrite a hundred lines the
   gate never asked for.
3. ``extract_examples --write`` and ``extract_solutions --write`` rebuild
   both ``build/`` trees. Whole-book, because listings import siblings.
   Fail-fast: nothing below means anything against a tree that would not
   build.
4. ``validate_output --update`` on the chapter and on its Solutions file,
   refreshing their ``#:`` markers. This is the step the full gate spends
   its time on, and the one worth narrowing. A rewritten marker triggers
   a second extract so the build trees carry the new text.
5. Sync ``Examples/`` and ``SolutionsCode/`` from the Markdown, then the
   drift and orphan checks over both.
6. The Markdown gates: ``check_all`` on the chapter (every gate check, or
   the ``--checks`` list the Makefile passes from ``GATE_CHECKS``),
   ``anchors`` and ``widths`` on the Solutions file, quoted ``ty``
   diagnostics in both, prose references to numbered exercises in
   both (the ones these two files make; a reference another chapter
   makes to this chapter's exercises needs the whole-book run),
   exercise/solution numbering, unique slugs.
7. ``ty``, ``ruff``, ``run_examples``, and ``pytest`` over the chapter's
   directory in each build tree.

Everything after step 3 runs even when an earlier step fails, so one pass
reports every problem. It does not write the gate stamp: it checks one
chapter, not the book, and `make verify` is still the pre-commit run
after a change that could reach other chapters (a renamed listing, a
shared ``utils/`` helper, a heading another chapter links to).
"""

import argparse
import sys
from pathlib import Path

from tools.check_chapter import resolve, run, run_markers
from tools.config import BUILD_DIR, EXAMPLES_TREE, ROOT

PY = [sys.executable]
NO_TESTS_COLLECTED = 5  # pytest's exit code for an empty directory
SOLUTIONS_DIR = ROOT / "Solutions"
SOLUTIONS_TREE = BUILD_DIR / "solutions"
# The Solutions checks the gate runs through check_all (its `banned` and
# listing checks stay off Solutions/ for the reasons the Makefile gives).
SOLUTIONS_CHECKS = ["anchors", "widths", "records"]


def code_checks(label: str, chapter_dir: Path, tree: Path) -> list[bool]:
    """ty, ruff, run, pytest over one chapter directory of one tree."""
    if not chapter_dir.is_dir():
        print(f"skip  {label} ty/ruff/run/pytest (no extracted directory)")
        return []
    target = str(chapter_dir)
    return [
        run(f"{label} ty", ["uv", "run", "ty", "check", target]),
        run(f"{label} ruff", ["uv", "run", "ruff", "check", target]),
        run(f"{label} run",
            [*PY, "-m", "tools.run_examples", "--tree", str(tree),
             chapter_dir.name]),
        run(f"{label} pytest",
            ["uv", "run", "pytest", "-q", target],
            ok=(0, NO_TESTS_COLLECTED)),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapter",
                    help="chapter number or stem prefix, e.g. 28")
    ap.add_argument("--checks", nargs="*", default=None, metavar="CHECK",
                    help="check_all checks to run on the chapter "
                         "(default: all of them)")
    args = ap.parse_args(argv)

    md = resolve(args.chapter)
    sol = SOLUTIONS_DIR / md.name
    prose = [md, sol] if sol.exists() else [md]
    number = md.stem.split("_", 1)[0]
    print(f"Verifying {md.name}"
          + (f" and Solutions/{sol.name}" if sol.exists() else "")
          + "\n")

    results = [
        run("fix-eol", [*PY, "-m", "tools.check_line_endings", "--fix"]),
        run("reflow", [*PY, "-m", "tools.reflow_prose", "--write",
                       str(md)]),
    ]
    extract = [*PY, "-m", "tools.extract_examples", "--write"]
    extract_sol = [*PY, "-m", "tools.extract_solutions", "--write"]
    if not run("extract", extract) or not run("solutions-extract",
                                              extract_sol):
        return 1

    before = [p.read_bytes() for p in prose]
    results.append(run_markers(md, label="examples markers"))
    if sol.exists():
        results.append(run_markers(sol, tree=SOLUTIONS_TREE,
                                   label="solutions markers"))
    if [p.read_bytes() for p in prose] != before:
        # A rewritten marker lives in the Markdown; the build trees were
        # extracted from the old text.
        results += [run("re-extract", extract),
                    run("solutions-re-extract", extract_sol)]

    results += [
        run("sync", [*extract, "-o", "Examples"]),
        run("solutions-sync", [*extract_sol, "-o", "SolutionsCode"]),
        run("drift", [*PY, "-m", "tools.extract_examples"]),
        run("solutions-drift", [*PY, "-m", "tools.extract_solutions"]),
        run("checks",
            [*PY, "-m", "tools.check_all", *(args.checks or []),
             "--paths", str(md)]),
    ]
    if sol.exists():
        results.append(run("solutions-checks",
                           [*PY, "-m", "tools.check_all", *SOLUTIONS_CHECKS,
                            "--paths", str(sol)]))
    results += [
        run("quoted-diagnostics",
            [*PY, "-m", "tools.check_quoted_diagnostics", *map(str, prose)]),
        run("exercise-refs",
            [*PY, "-m", "tools.exercise_refs", *map(str, prose)]),
        run("solutions-numbering",
            [*PY, "-m", "tools.check_solutions", number]),
        run("unique-slugs", [*PY, "-m", "tools.check_unique_slugs"]),
        run("coupling-panels",
            [*PY, "-m", "tools.coupling_panels", "--check"]),
    ]
    results += code_checks("examples", EXAMPLES_TREE / md.stem,
                           EXAMPLES_TREE)
    results += code_checks("solutions", SOLUTIONS_TREE / md.stem,
                           SOLUTIONS_TREE)

    failed = results.count(False)
    print(f"\n{len(results) - failed} passed, {failed} failed")
    if failed:
        print("Run `make verify` before committing: this checks one"
              " chapter, not the book.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
