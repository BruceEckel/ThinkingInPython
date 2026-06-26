#!/usr/bin/env python3
"""Extract tagged code/data examples from the book's Markdown into a tree.

A fenced block in any ``Markdown/*.md`` file is treated as an extractable
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
Blocks without such a first line are illustrative fragments and are skipped.

Default mode is ``check``: nothing is written, drift between the Markdown and
the committed ``Examples/`` tree is reported, and a non-zero exit signals
trouble (useful in CI). Pass ``--write`` to materialize the tree.

Usage:
    python tools/extract_examples.py                # check vs Examples/
    python tools/extract_examples.py --write        # write build/examples/
    python tools/extract_examples.py --write -o DIR  # write somewhere else
"""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_DIR = ROOT / "Markdown"
COMMITTED_DIR = ROOT / "Examples"
DEFAULT_OUT = ROOT / "build" / "examples"

FENCE = re.compile(r"^```(\w+)?\s*$")
# First content line names a relative path with an extension.
PATH_LINE = re.compile(r"^#\s*([\w./\\-]+\.\w+)\s*$")

# Helpers shared across chapters are written to the tree root rather than a
# chapter dir, so any example can import them (the example tooling puts the
# root on the path). Add future shared modules to this set.
SHARED = {"display.py"}


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
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE.match(lines[i])
        if m:
            lang = m.group(1) or ""
            i += 1
            start = i
            while i < n and not lines[i].startswith("```"):
                i += 1
            yield lang, lines[start:i]
            i += 1  # skip the closing fence
        else:
            i += 1


def extract(markdown_dir: Path = MARKDOWN_DIR) -> ExtractResult:
    result = ExtractResult()
    for md in sorted(markdown_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        for lang, block in iter_blocks(text.splitlines()):
            first = next((b for b in block if b.strip()), "")
            pm = PATH_LINE.match(first)
            if not pm:
                result.fragments += 1
                continue
            slug = pm.group(1).replace("\\", "/")
            rel = slug if slug in SHARED else f"{md.stem}/{slug}"
            content = "\n".join(block).rstrip("\n") + "\n"
            existing = result.examples.get(rel)
            if existing and existing.content != content:
                result.conflicts.append((rel, existing.source_md, md.name))
                continue
            result.examples[rel] = Example(rel, content, md.name, lang)
    return result


def write_tree(result: ExtractResult, out_dir: Path) -> int:
    written = 0
    for ex in result.examples.values():
        dest = out_dir / ex.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_text(encoding="utf-8") != ex.content:
            # newline="\n" forces LF even on Windows, so regenerating the tree
            # never introduces CRLF (which .gitattributes would warn about).
            dest.write_text(ex.content, encoding="utf-8", newline="\n")
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="write the extracted tree (default: check only)")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output dir for --write (default: {DEFAULT_OUT.name})")
    args = ap.parse_args(argv)

    result = extract()
    print(f"Scanned {MARKDOWN_DIR.name}: "
          f"{len(result.examples)} file-blocks, {result.fragments} fragments.")

    if result.conflicts:
        print(f"\n{len(result.conflicts)} conflicting duplicate path(s) "
              "(same path, differing content):")
        for path, a, b in result.conflicts:
            print(f"  ! {path}  ({a} vs {b})")

    if args.write:
        written = write_tree(result, args.out)
        print(f"\nWrote {written} changed file(s) to {args.out}.")
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
    if not (missing or changed or result.conflicts):
        print("\nIn sync: every book example matches the committed tree.")
        return 0
    print("\n(Run with --write to materialize build/examples/ for running.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
