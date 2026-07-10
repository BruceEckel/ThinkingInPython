#!/usr/bin/env python3
"""Extract tagged code examples from Solutions/*.md into a tree.

The exact counterpart of ``extract_examples.py``, pointed at ``Solutions/``
instead of ``Chapters/``. A fenced block is extractable when its first
content line is a path comment (``# exercise_1.py``); the file is written
under a directory named for the chapter (the Solutions file's stem), exactly
as ``extract_examples.py`` does for the book chapters. See that module's
docstring for the full slug-naming rules; this module reuses its functions
directly rather than duplicating them.

Default mode is ``check``: compares against the committed ``SolutionsCode/``
tree. Pass ``--write`` to materialize a tree (default ``build/solutions``).

Usage:
    python tools/extract_solutions.py                # check vs SolutionsCode/
    python tools/extract_solutions.py --write         # write build/solutions/
    python tools/extract_solutions.py --write -o DIR  # write somewhere else
"""

import argparse
import shutil
from pathlib import Path

from extract_examples import check_against, extract, is_derived, write_tree
from tools_config import BUILD_DIR, ROOT

SOLUTIONS_DIR = ROOT / "Solutions"
COMMITTED_DIR = ROOT / "SolutionsCode"
DEFAULT_OUT = BUILD_DIR / "solutions"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--write", action="store_true",
                    help="write the extracted tree (default: check only)")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output dir for --write (default: {DEFAULT_OUT.name})")
    args = ap.parse_args(argv)

    result = extract(markdown_dir=SOLUTIONS_DIR)
    print(f"Scanned {SOLUTIONS_DIR.name}: "
          f"{len(result.examples)} file-blocks, {result.fragments} fragments.")

    if result.conflicts:
        print(f"\n{len(result.conflicts)} conflicting duplicate path(s) "
              "(same path, differing content):")
        for path, a, b in result.conflicts:
            print(f"  ! {path}  ({a} vs {b})")

    if args.write:
        print()
        if is_derived(args.out) and args.out.exists():
            shutil.rmtree(args.out)
            print(f"Cleaned {args.out}.")
        written = write_tree(result, args.out)
        print(f"Wrote {written} changed file(s) to {args.out}.")
        return 1 if result.conflicts else 0

    missing, changed = check_against(result, COMMITTED_DIR)
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
    if not (missing or changed or result.conflicts):
        print("\nIn sync: every solution matches the committed tree.")
        return 0
    print("\n(Run with --write to materialize build/solutions/ for running.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
