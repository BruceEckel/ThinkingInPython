#!/usr/bin/env python3
"""Extract tagged code examples from Solutions/<chapter>/README.md into a tree.

The counterpart of ``extract_examples.py``, pointed at ``Solutions/``
instead of ``Chapters/``. A fenced block is extractable when its first
content line is a path comment (``# exercise_1.py``); the file is written
under a directory named for the chapter (the name of the directory that
holds the README), as ``extract_examples.py`` does for the book chapters.
See that module's docstring for the full slug-naming rules; this module
reuses its functions directly rather than duplicating them.

The committed tree is ``Solutions/`` itself: each ``Solutions/<chapter>/``
holds the authored ``README.md`` (which GitHub renders under the file
list) beside the ``.py`` files extracted from it. Default mode is
``check``: compares against those committed files. Pass ``--write`` to
materialize a tree (default ``build/solutions``).

Both modes first verify that every ``Solutions/<stem>/README.md`` stem
matches a current ``Chapters/*.md`` stem, so a chapter renumbering cannot
silently leave the solutions carrying old chapter numbers.

Check mode also reports strays, the same way ``extract_examples.py`` does:
a file under ``Solutions/`` that no current block generates, left behind
by a rename or a renumbered exercise since the drift check only flags
missing/changed blocks, not extras. The authored ``README.md`` files are
the source, so they are not strays, and ``--prune`` refuses to delete
any Markdown file. Each stray is classified by grepping
the one ``README.md`` that generates its directory for its bare
filename: *orphaned* (the name appears nowhere there) fails the check;
*referenced* is reported for a human to judge. Grepping the solutions alone
is deliberate. A leftover named only by a chapter is still orphaned here,
because no solution block can be producing it, and the chapter's own copy
lives under ``Examples/``. Grepping one file rather than all of them is
deliberate too: every chapter has an ``exercise_2.py``, so a leftover from a
renumbering would otherwise read as referenced forever. Pass ``--prune``
to delete the orphaned files (never the referenced ones).

Usage:
    python -m tools.extract_solutions                # check vs Solutions/
    python -m tools.extract_solutions --prune         # also delete orphaned strays
    python -m tools.extract_solutions --write         # write build/solutions/
    python -m tools.extract_solutions --write -o DIR  # write somewhere else
"""

import argparse
import shutil
from pathlib import Path

from tools.extract_examples import extract, find_strays, is_derived, report_strays
from tools.config import BUILD_DIR, CHAPTERS_DIR, SOLUTIONS_DIR, SOLUTIONS_MD
from tools.extract import check_against, report_conflicts, write_tree
from tools.repo import chapter_stem, solutions_files

COMMITTED_DIR = SOLUTIONS_DIR
DEFAULT_OUT = BUILD_DIR / "solutions"


def naming_problems() -> list[str]:
    """Solutions stems that do not match a current Chapters stem.

    Matches by full stem first, then by title (the stem after the
    numeric prefix) to say which chapter number a stale file should
    carry now.
    """
    chapter_stems = {p.stem for p in CHAPTERS_DIR.glob("*.md")}
    by_title = {s.partition("_")[2]: s for s in chapter_stems}
    problems: list[str] = []
    for path in solutions_files(SOLUTIONS_DIR):
        stem = chapter_stem(path)
        if stem in chapter_stems:
            continue
        expected = by_title.get(stem.partition("_")[2])
        if expected:
            problems.append(
                f"{stem}/{SOLUTIONS_MD}: chapter is now {expected}.md")
        else:
            problems.append(f"{stem}/{SOLUTIONS_MD}: no matching chapter")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--write", action="store_true",
                    help="write the extracted tree (default: check only)")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output dir for --write (default: {DEFAULT_OUT.name})")
    ap.add_argument("--prune", action="store_true",
                    help="delete orphaned stray files under Solutions/ "
                         "(check mode only; never Markdown)")
    args = ap.parse_args(argv)

    stale = naming_problems()
    if stale:
        print(f"{len(stale)} Solutions file(s) out of step with "
              "Chapters/ numbering:")
        for problem in stale:
            print(f"  ! {problem}")
        return 1

    result = extract(markdown_dir=SOLUTIONS_DIR)
    print(f"Scanned {SOLUTIONS_DIR.name}: "
          f"{len(result.files)} file-blocks, {result.fragments} fragments.")

    report_conflicts(result)

    if args.write:
        print()
        if is_derived(args.out) and args.out.exists():
            shutil.rmtree(args.out)
            print(f"Cleaned {args.out}.")
        written = write_tree(result, args.out)
        print(f"Wrote {written} changed file(s) to {args.out}.")
        return 1 if result.conflicts else 0

    missing, changed = check_against(result, COMMITTED_DIR)
    # Worded "in Solutions" rather than report_drift's "in the book",
    # since this tool's source is Solutions/*/README.md, not the chapters.
    if missing:
        print(f"\n{len(missing)} example(s) in Solutions but not under "
              f"{COMMITTED_DIR.name}/:")
        for p in missing:
            print(f"  + {p}")
    if changed:
        print(f"\n{len(changed)} example(s) whose Solutions text differs "
              f"from {COMMITTED_DIR.name}/:")
        for p in changed:
            print(f"  ~ {p}")

    strays = find_strays(result, COMMITTED_DIR, source_md=SOLUTIONS_MD)
    orphaned, referenced = report_strays(strays, COMMITTED_DIR,
                                         search=[SOLUTIONS_DIR],
                                         prune=args.prune)

    if not (missing or changed or result.conflicts or orphaned):
        if referenced:
            print("\nIn sync otherwise: every solution matches the "
                  "committed tree.")
        else:
            print("\nIn sync: every solution matches the committed tree.")
        return 0
    print("\n(Run with --write to materialize build/solutions/ for running.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
