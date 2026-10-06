#!/usr/bin/env python
"""Run the verify loop for one chapter and its Solutions file.

`tip verify` fixes line endings, refreshes every `#:` marker, syncs both
generated trees, and runs the whole gate: tens of seconds, nearly all of
it spent on chapters you did not touch. After editing one chapter this
runs the same loop scoped to that chapter and its Solutions file:

    tip verify-ch CH=28        # or CH=28_Patterns--Function_Objects

The steps, in order, mirror `verify` (fixers first, markers before sync):

1. ``check_line_endings --fix`` over the tree (whole-repo, cheap).
2. ``reflow_prose --write`` on the chapter. Not on the Solutions file:
   the gate reflows ``Chapters/`` only, and Solutions prose is wrapped
   at a column, so reflowing it here would rewrite a hundred lines the
   gate never asked for.
3. ``exercise_statements --write`` on the chapter, so the exercise
   statements copied under the Solutions headings match the reflowed
   chapter, then ``solution_steps --write``, so each hinted solution's
   step ladder and shape blocks match its listings.
4. ``extract_examples --write`` and ``extract_solutions --write`` rebuild
   both build trees (``build/examples`` and ``build/solutions``, or the
   two under ``--build-dir``). Whole-book, because listings import siblings.
   Fail-fast: nothing below means anything against a tree that would not
   build.
5. ``validate_output --update`` on the chapter and on its Solutions file,
   refreshing their ``#:`` markers. This is the step the full gate spends
   its time on, and the one worth narrowing. A rewritten marker triggers
   a second extract so the build trees carry the new text.
   ``marker_placement`` then checks that each run sits directly after
   the statement that printed it, in both files.
6. Sync ``Examples/`` and the code beside ``Solutions/<chapter>/README.md``
   from the Markdown, then the drift and orphan checks over both.
7. The Markdown gates: ``check_all`` on the chapter (every gate check, or
   the ``--checks`` list tools/tasks.py passes from ``GATE_CHECKS``),
   ``anchors`` and ``widths`` on the Solutions file, quoted ``ty``
   diagnostics in both, prose references to numbered exercises in
   both (the ones these two files make; a reference another chapter
   makes to this chapter's exercises needs the whole-book run),
   exercise/solution numbering, unique slugs.
8. ``ty``, ``ruff``, ``run_examples``, and ``pytest`` over the chapter's
   directory in each build tree (the private ones under ``--build-dir``).

Everything after step 4 runs even when an earlier step fails, so one pass
reports every problem. It does not write the gate stamp: it checks one
chapter, not the book, and `tip verify` is still the pre-commit run
after a change that could reach other chapters (a renamed listing, a
shared ``utils/`` helper, a heading another chapter links to).

Parallel runs: step 4 wipes and rebuilds the shared ``build/examples``
and ``build/solutions``, so two runs at once delete each other's trees
mid-run (``WinError 32``/``145``, ``ModuleNotFoundError`` for
``record``). ``--build-dir DIR`` points this run at its own trees,
``DIR/examples`` and ``DIR/solutions``, and every step that reads a
build tree reads those; the shared pair is neither read nor written.
``--isolated`` is shorthand for ``--build-dir build/verify-ch-<NN>``
with ``<NN>`` the chapter's number prefix (``28``, ``B``);
``tip verify-ch CH=28 ISOLATED=1`` passes it. The directories sit under
``build/``, which is gitignored, and a run leaves its directory behind
(the next run on that chapter reuses the name and rebuilds it), so
deleting ``build/verify-ch-*`` is safe at any time. With neither flag
the run is the shared-tree run described above.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

from tools.check_chapter import resolve, run, run_markers
from tools.config import BUILD_DIR, ROOT, SOLUTIONS_MD
from tools.repo import chapter_stem, solutions_file

PY: Final = [sys.executable]
NO_TESTS_COLLECTED: Final = 5  # pytest's exit code for an empty directory
SOLUTIONS_DIR: Final = ROOT / "Solutions"
# pyproject's [tool.ty.environment] extra-paths, minus the build/examples
# prefix: the directories (under the examples tree) that ty must see.
TY_EXTRA_DIRS: Final = ("utils", "06_Foundations--Modules_and_Packages")
# The Solutions checks the gate runs through check_all (its `banned` and
# listing checks stay off Solutions/ for the reasons tools/tasks.py gives).
SOLUTIONS_CHECKS = ["anchors", "widths", "records"]


def ty_overrides(build_dir: Path) -> list[str]:
    """`ty` options that point its extra-paths at a private examples tree.

    pyproject names ``build/examples/...``, which a private build
    directory does not populate. ``-c environment.extra-paths=[...]``
    would not do: ty merges it with the pyproject list and still
    fails on the missing shared directory. ``--config-file`` makes ty
    ignore pyproject's ``[tool.ty]`` (which holds only extra-paths),
    so this writes ``DIR/ty.toml`` and points ty at it. Forward
    slashes keep Windows backslashes out of the TOML string.
    """
    examples = build_dir / "examples"
    paths = ", ".join(f'"{(examples / d).resolve().as_posix()}"'
                      for d in TY_EXTRA_DIRS)
    config = build_dir / "ty.toml"
    lines = ["[environment]", f"extra-paths = [{paths}]"]
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ["--config-file", str(config.resolve())]


def pytest_overrides(examples: Path) -> list[str]:
    """`pytest` options that replace pyproject's ``pythonpath``."""
    return ["-o", f"pythonpath={(examples / 'utils').resolve().as_posix()}"]


def code_checks(label: str, chapter_dir: Path, tree: Path,
                build_dir: Path = BUILD_DIR) -> list[bool]:
    """ty, ruff, run, pytest over one chapter directory of one tree.

    A ``build_dir`` other than ``build/`` is a private one, so ``ty``
    and ``pytest`` get its ``examples/`` paths in place of pyproject's.
    The chapter's tree must exist, so ``build_dir`` does too.
    """
    if not chapter_dir.is_dir():
        print(f"skip  {label} ty/ruff/run/pytest (no extracted directory)")
        return []
    target = str(chapter_dir)
    private = build_dir != BUILD_DIR
    ty_extra = ty_overrides(build_dir) if private else []
    pytest_extra = (pytest_overrides(build_dir / "examples")
                    if private else [])
    return [
        run(f"{label} ty", ["uv", "run", "ty", "check", *ty_extra, target]),
        run(f"{label} ruff", ["uv", "run", "ruff", "check", target]),
        run(f"{label} run",
            [*PY, "-m", "tools.run_examples", "--tree", str(tree),
             chapter_dir.name]),
        run(f"{label} pytest",
            ["uv", "run", "pytest", "-q", *pytest_extra, target],
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
    where = ap.add_mutually_exclusive_group()
    where.add_argument("--build-dir", type=Path, default=BUILD_DIR,
                       metavar="DIR",
                       help="extract into DIR/examples and DIR/solutions "
                            "instead of build/, so parallel runs do not "
                            "wipe each other (default: build/)")
    where.add_argument("--isolated", action="store_true",
                       help="shorthand for --build-dir "
                            "build/verify-ch-<NN>")
    args = ap.parse_args(argv)

    md = resolve(args.chapter)
    sol = solutions_file(md, SOLUTIONS_DIR)
    prose = [md, sol] if sol.exists() else [md]
    number = md.stem.split("_", 1)[0]
    build_dir = (BUILD_DIR / f"verify-ch-{number}" if args.isolated
                 else args.build_dir)
    examples_tree = build_dir / "examples"
    solutions_tree = build_dir / "solutions"
    print(f"Verifying {md.name}"
          + (f" and Solutions/{chapter_stem(md)}/{SOLUTIONS_MD}"
             if sol.exists() else "")
          + "\n")

    results = [
        run("fix-eol", [*PY, "-m", "tools.check_line_endings", "--fix"]),
        run("reflow", [*PY, "-m", "tools.reflow_prose", "--write",
                       str(md)]),
        run("statements", [*PY, "-m", "tools.exercise_statements",
                           "--write", number]),
        run("steps", [*PY, "-m", "tools.solution_steps",
                      "--write", number]),
    ]
    extract = [*PY, "-m", "tools.extract_examples", "--write",
               "-o", str(examples_tree)]
    extract_sol = [*PY, "-m", "tools.extract_solutions", "--write",
                   "-o", str(solutions_tree)]
    if not run("extract", extract) or not run("solutions-extract",
                                              extract_sol):
        return 1

    before = [p.read_bytes() for p in prose]
    results.append(run_markers(md, tree=examples_tree,
                               label="examples markers"))
    if sol.exists():
        results.append(run_markers(sol, tree=solutions_tree,
                                   label="solutions markers"))
    if [p.read_bytes() for p in prose] != before:
        # A rewritten marker lives in the Markdown; the build trees were
        # extracted from the old text.
        results += [run("re-extract", extract),
                    run("solutions-re-extract", extract_sol)]
    results.append(run("marker placement",
                       [*PY, "-m", "tools.marker_placement",
                        "--build-dir", str(build_dir), *map(str, prose)]))

    sync = [*PY, "-m", "tools.extract_examples", "--write"]
    sync_sol = [*PY, "-m", "tools.extract_solutions", "--write"]
    results += [
        run("sync", [*sync, "-o", "Examples"]),
        run("solutions-sync", [*sync_sol, "-o", "Solutions"]),
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
            [*PY, "-m", "tools.check_quoted_diagnostics",
             "--build-dir", str(build_dir), *map(str, prose)]),
        run("exercise-refs",
            [*PY, "-m", "tools.exercise_refs", *map(str, prose)]),
        run("solutions-numbering",
            [*PY, "-m", "tools.check_solutions", number]),
        run("unique-slugs", [*PY, "-m", "tools.check_unique_slugs"]),
        run("coupling-panels",
            [*PY, "-m", "tools.coupling_panels", "--check"]),
        run("story-figures",
            [*PY, "-m", "tools.story_figures", "--check"]),
    ]
    results += code_checks("examples", examples_tree / md.stem,
                           examples_tree, build_dir)
    results += code_checks("solutions", solutions_tree / md.stem,
                           solutions_tree, build_dir)

    failed = results.count(False)
    print(f"\n{len(results) - failed} passed, {failed} failed")
    if failed:
        print("Run `tip verify` before committing: this checks one"
              " chapter, not the book.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
