#!/usr/bin/env python3
"""Extract tagged code/data examples from the book's Markdown into a tree.

A fenced block in any ``Chapters/*.md`` file is treated as an extractable
*file* when its first non-blank content line is a path comment naming the file
relative to its chapter, e.g.::

    ```python
    # trace.py
    ...
    ```

The file is written under a directory named for the chapter it appears in (the
Markdown file's stem). A ``# trace.py`` slug in
``14_Techniques--Decorators.md`` is written to
``14_Techniques--Decorators/trace.py``, verbatim block contents and all. Slugs may
include sub-paths (``# mouse/MouseAction.py``) to group files within a chapter.

A slug starting with ``utils/`` is written to the tree root's ``utils/``
directory instead of a chapter dir, so any chapter can import it, e.g.
``# utils/display.py`` becomes ``utils/display.py`` at the root. The example
tooling puts that directory on the import path, so this is how a helper like
``result.py`` or ``safe.py`` gets reused across chapters. Use it only for
something genuinely shared; everything else stays chapter-scoped.

A slug starting with ``rust/`` (e.g. ``# rust/fastcount/demo.py``) is
excluded entirely, counted as a fragment rather than extracted: it is a
Python caller for a compiled Rust/PyO3 module, extracted separately by
``tools/extract_rust.py`` into ``rust/``, not ``Examples/``. That module
does not exist in this build's Python environment, so running the caller
here would fail; see ``rust/README.md``.

Blocks without such a first line, or with a ``rust/``-prefixed slug, are
illustrative fragments and are skipped.

Default mode is ``check``: nothing is written, drift between the Markdown and
the committed ``Examples/`` tree is reported, and a non-zero exit signals
trouble (useful in CI). Pass ``--write`` to materialize the tree.

Writing to the default ``build/examples`` (or any path under ``build/``) wipes
the directory first, so a regenerated tree never carries orphaned files left by
a renamed or deleted example. Writing to any other ``-o`` target keeps the
non-destructive incremental write, since trees like the committed ``Examples/``
hold files that are not generated from the book.

Check mode also looks the other way: a file under ``Examples/`` (besides
``__pycache__`` and ``.idea``) that no current block generates, left behind by
a rename or deletion since the drift check above only flags missing/changed
blocks, not extras. Each stray is further classified by grepping every chapter
for its bare filename: *orphaned* (the name appears nowhere) fails the check
the same as a missing or changed block; *referenced* (the name still appears
in some chapter's prose, e.g. a hand-written helper mentioned but not
extracted) is reported but does not fail the check, since deleting it needs a
human to confirm it is truly unused. Pass ``--prune`` to delete the orphaned
files (never the referenced ones).

Usage:
    python tools/extract_examples.py                # check vs Examples/
    python tools/extract_examples.py --prune        # also delete orphaned strays
    python tools/extract_examples.py --write        # write build/examples/
    python tools/extract_examples.py --write -o DIR  # write somewhere else
"""

import argparse
import re
import shutil
from pathlib import Path

from tools_config import BUILD_DIR, CHAPTERS_DIR, EXAMPLES_TREE, ROOT
from tools_extract import (
    ExtractResult,
    check_against,
    extract as extract_blocks,
    report_conflicts,
    report_drift,
    write_tree,
)
from tools_markdown import Block, Document
from tools_repo import md_files

COMMITTED_DIR = ROOT / "Examples"
DEFAULT_OUT = EXAMPLES_TREE

# Directories under Examples/ that are never book-generated and never stray:
# JetBrains project settings and Python's own bytecode cache.
NOISE_DIR_NAMES = {"__pycache__", ".idea"}


def route(doc: Document, block: Block) -> str | None:
    """Where a book block extracts to, or None if it is a fragment.

    A "utils/" slug keeps its path so it lands at the tree root and every
    chapter can import it. A "rust/" slug is passed over entirely: it is a
    caller for a compiled module extract_rust.py handles, and the module
    does not exist in this build's environment.
    """
    slug = block.slug
    if slug is None or slug.startswith("rust/"):
        return None
    return slug if slug.startswith("utils/") else f"{doc.path.stem}/{slug}"


def extract(markdown_dir: Path = CHAPTERS_DIR) -> ExtractResult:
    docs = (Document.parse(md) for md in md_files([markdown_dir]))
    return extract_blocks(docs, [route])


def is_derived(out_dir: Path) -> bool:
    """True if out_dir lives under build/, so it is safe to wipe and rebuild.

    The default output (build/examples) is gitignored and fully regenerated
    from the Markdown, so cleaning it each run is safe and avoids leaving
    orphaned files behind after a rename or deletion. Any other target (such as
    the committed Examples/ tree, which holds files not generated from the book)
    keeps the non-destructive incremental write.
    """
    try:
        out_dir.resolve().relative_to(BUILD_DIR.resolve())
        return True
    except ValueError:
        return False


def find_strays(result: ExtractResult, committed: Path) -> list[str]:
    """Files under `committed` that no book block generates.

    Excludes NOISE_DIR_NAMES (__pycache__, .idea), which are expected to sit
    there without ever having a matching block.
    """
    if not committed.exists():
        return []
    expected = set(result.files)
    strays = []
    for path in committed.rglob("*"):
        if not path.is_file():
            continue
        if NOISE_DIR_NAMES & set(path.relative_to(committed).parts):
            continue
        rel = path.relative_to(committed).as_posix()
        if rel not in expected:
            strays.append(rel)
    return sorted(strays)


def classify_strays(
    strays: list[str], search: list[str | Path] | None = None
) -> tuple[list[str], list[str]]:
    """Split strays into (orphaned, referenced).

    Referenced means the bare filename still appears somewhere in the
    Markdown under `search` (Chapters/ by default), e.g. a hand-written
    helper mentioned in prose but not extracted; that needs a human to
    confirm it is truly unused, so it is reported but not treated as a
    failure. Orphaned means the name appears nowhere, so it is safe to
    delete outright.

    `search` is the tree that generates the committed files being
    classified, so extract_solutions.py passes Solutions/. A stray there
    named only by a chapter is still orphaned as far as the solutions are
    concerned, since no solution block can be producing it.

    The name must match whole, not as a substring. Renaming
    ``locked_settings.py`` to ``singleton_locked_settings.py`` leaves a
    stray whose name reads as "mentioned" inside the new one, and a
    substring test reports that leftover as referenced forever, so the
    most common source of strays would never be prunable.
    """
    book_text = "\n".join(
        md.read_text(encoding="utf-8") for md in md_files(search))
    orphaned, referenced = [], []
    for rel in strays:
        name = re.escape(Path(rel).name)
        mentioned = re.search(rf"\b{name}\b", book_text) is not None
        (referenced if mentioned else orphaned).append(rel)
    return orphaned, referenced


def report_strays(strays: list[str], committed: Path,
                  search: list[str | Path] | None = None,
                  prune: bool = False) -> tuple[list[str], list[str]]:
    """Classify, optionally delete, and report strays.

    Returns (orphaned, referenced) as they stand after any pruning. The
    caller folds the orphans into its exit status and words its "in sync"
    line against the referenced ones. Pruning empties the orphan list, so
    a --prune run reports what it deleted and then succeeds.
    """
    orphaned, referenced = classify_strays(strays, search)
    if prune and orphaned:
        for p in orphaned:
            (committed / p).unlink()
        print(f"\nPruned {len(orphaned)} orphaned stray file(s) "
              f"from {committed.name}/:")
        for p in orphaned:
            print(f"  - {p}")
        orphaned = []
    elif orphaned:
        print(f"\n{len(orphaned)} orphaned stray file(s) under "
              f"{committed.name}/ (no block generates it, and the name "
              "appears in no source Markdown; run with --prune to delete):")
        for p in orphaned:
            print(f"  x {p}")
    if referenced:
        print(f"\n{len(referenced)} stray file(s) under {committed.name}/ "
              "with no block, but the filename is still mentioned in the "
              "source Markdown (review by hand):")
        for p in referenced:
            print(f"  ? {p}")
    return orphaned, referenced


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="write the extracted tree (default: check only)")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output dir for --write (default: {DEFAULT_OUT.name})")
    ap.add_argument("--prune", action="store_true",
                    help="delete orphaned stray files under Examples/ "
                         "(check mode only)")
    args = ap.parse_args(argv)

    result = extract()
    print(f"Scanned {CHAPTERS_DIR.name}: "
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

    # Default: check mode against the committed Examples/ tree.
    missing, changed = check_against(result, COMMITTED_DIR)
    report_drift(missing, changed, noun="example",
                 where=COMMITTED_DIR.name)

    strays = find_strays(result, COMMITTED_DIR)
    orphaned, referenced = report_strays(strays, COMMITTED_DIR,
                                         prune=args.prune)

    if not (missing or changed or result.conflicts or orphaned):
        if referenced:
            print("\nIn sync otherwise: every book example matches the "
                  "committed tree.")
        else:
            print("\nIn sync: every book example matches the committed tree.")
        return 0
    print("\n(Run with --write to materialize build/examples/ for running.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
