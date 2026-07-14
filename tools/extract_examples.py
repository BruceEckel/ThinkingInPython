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
Markdown file's stem). A ``# trace.py`` slug in ``08_Decorators.md`` is written
to ``08_Decorators/trace.py``, verbatim block contents and all. Slugs may
include sub-paths (``# mouse/MouseAction.py``) to group files within a chapter.

A ``# shared: name.py`` slug (the ``shared:`` marker, not a path segment,
since no ``Examples/shared/`` directory exists) is written to the tree root
instead of a chapter dir, so any chapter can import it, e.g.
``# shared: display.py`` becomes ``display.py`` at the root. The example
tooling puts the tree root on the import path, so this is how a helper like
``result.py`` or ``safe.py`` gets reused across chapters. Use it only for
something genuinely shared; everything else stays chapter-scoped.

Blocks without such a first line are illustrative fragments and are skipped.

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
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from tools_config import BUILD_DIR, CHAPTERS_DIR, EXAMPLES_TREE, ROOT
from tools_pycode import walk_fenced
from tools_repo import block_slug, md_files, write_text_lf

COMMITTED_DIR = ROOT / "Examples"
DEFAULT_OUT = EXAMPLES_TREE

# Directories under Examples/ that are never book-generated and never stray:
# JetBrains project settings and Python's own bytecode cache.
NOISE_DIR_NAMES = {"__pycache__", ".idea"}


@dataclass
class Example:
    path: str  # relative path, forward slashes
    content: str  # verbatim block text, including the trailing newline
    source_md: str  # chapter file the block came from
    language: str  # fence language, e.g. "python" or "" if none


@dataclass
class ExtractResult:
    examples: dict[str, Example] = field(default_factory=dict)
    conflicts: list[tuple[str, str, str]] = field(default_factory=list)
    fragments: int = 0


def iter_blocks(lines: list[str]):
    """Yield (language, block_lines) for each fenced block."""
    for ev in walk_fenced(lines):
        if ev.match is not None:
            yield ev.match.group(1) or "", lines[ev.open_at + 1:ev.end]


def extract(markdown_dir: Path = CHAPTERS_DIR) -> ExtractResult:
    result = ExtractResult()
    for md in md_files([markdown_dir]):
        text = md.read_text(encoding="utf-8")
        for lang, block in iter_blocks(text.splitlines()):
            parsed = block_slug(block)
            if parsed is None:
                result.fragments += 1
                continue
            shared, slug = parsed
            if shared:
                rel = slug
                # The written file's header comment should match where it
                # actually lands (the tree root), not the shared: marker.
                first = next(b for b in block if b.strip())
                block[block.index(first)] = f"# {rel}"
            else:
                rel = f"{md.stem}/{slug}"
            content = "\n".join(block).rstrip("\n") + "\n"
            existing = result.examples.get(rel)
            if existing and existing.content != content:
                result.conflicts.append((rel, existing.source_md, md.name))
                continue
            result.examples[rel] = Example(rel, content, md.name, lang)
    return result


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


def write_tree(result: ExtractResult, out_dir: Path) -> int:
    written = 0
    for ex in result.examples.values():
        dest = out_dir / ex.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_text(encoding="utf-8") != ex.content:
            write_text_lf(dest, ex.content)
            written += 1
    return written


def check_against(result: ExtractResult, committed: Path):
    """Compare extracted examples to the committed tree. Returns drift lists."""
    missing, changed = [], []
    for ex in result.examples.values():
        target = committed / ex.path
        if not target.exists():
            missing.append(ex.path)
        elif target.read_text(encoding="utf-8") != ex.content:
            changed.append(ex.path)
    return missing, changed


def find_strays(result: ExtractResult, committed: Path) -> list[str]:
    """Files under `committed` that no book block generates.

    Excludes NOISE_DIR_NAMES (__pycache__, .idea), which are expected to sit
    there without ever having a matching block.
    """
    if not committed.exists():
        return []
    expected = set(result.examples)
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


def classify_strays(strays: list[str]) -> tuple[list[str], list[str]]:
    """Split strays into (orphaned, referenced).

    Referenced means the bare filename still appears somewhere in
    Chapters/*.md, e.g. a hand-written helper mentioned in prose but not
    extracted; that needs a human to confirm it is truly unused, so it is
    reported but not treated as a failure. Orphaned means the name appears
    nowhere, so it is safe to delete outright.
    """
    book_text = "\n".join(
        md.read_text(encoding="utf-8") for md in md_files())
    orphaned, referenced = [], []
    for rel in strays:
        name = Path(rel).name
        (referenced if name in book_text else orphaned).append(rel)
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

    # Default: check mode against the committed Examples/ tree.
    missing, changed = check_against(result, COMMITTED_DIR)
    if missing:
        print(f"\n{len(missing)} example(s) in the book but not under "
              f"{COMMITTED_DIR.name}/:")
        for p in missing:
            print(f"  + {p}")
    if changed:
        print(f"\n{len(changed)} example(s) whose book text differs from "
              f"{COMMITTED_DIR.name}/:")
        for p in changed:
            print(f"  ~ {p}")

    strays = find_strays(result, COMMITTED_DIR)
    orphaned, referenced = classify_strays(strays)
    if args.prune and orphaned:
        for p in orphaned:
            (COMMITTED_DIR / p).unlink()
        print(f"\nPruned {len(orphaned)} orphaned stray file(s) "
              f"from {COMMITTED_DIR.name}/:")
        for p in orphaned:
            print(f"  - {p}")
        orphaned = []
    elif orphaned:
        print(f"\n{len(orphaned)} orphaned stray file(s) under "
              f"{COMMITTED_DIR.name}/ (no book block, no reference anywhere; "
              "run with --prune to delete):")
        for p in orphaned:
            print(f"  x {p}")
    if referenced:
        print(f"\n{len(referenced)} stray file(s) under {COMMITTED_DIR.name}/ "
              "with no book block, but the filename is still mentioned in "
              "the book (review by hand):")
        for p in referenced:
            print(f"  ? {p}")

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
