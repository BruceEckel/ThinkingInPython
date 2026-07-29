#!/usr/bin/env python3
"""Extract Rust/PyO3 examples from the book's Markdown into rust/.

Extends extract_examples.py's marker convention to a second language. A
```rust fenced block is extracted when its first content line is a Rust
line comment naming the file, relative to rust/::

    ```rust
    // fastcount/src/lib.rs
    ...
    ```

A ```python fenced block whose slug starts with ``rust/`` (e.g.
``# rust/fastcount/demo.py``) is a Python caller for a Rust module, not a
normal book example: extract_examples.py excludes it (see that module's
docstring), and this tool picks it up instead, writing it under ``rust/``
next to the crate it demonstrates.

``rust/`` also holds real, hand-maintained project files this tool never
touches: ``Cargo.toml``, ``pyproject.toml``, ``.python-version``,
``.gitignore``, whatever ``maturin new`` scaffolds. Only the specific
paths a book block names are read, checked, or written; nothing else
under ``rust/`` is inspected. There is no destructive "clean and
regenerate" mode the way ``extract_examples.py --write`` has for
``build/``, since everything under ``rust/`` is real, committed project
state, not a throwaway tree, and no orphan detection yet either (unlike
``extract_examples.py``'s stray-file check): a renamed or deleted book
slug leaves its old file behind under ``rust/`` until removed by hand.

Building and running the extracted crates needs cargo/rustc and is never
done here, nor by the main build: see ``rust/README.md`` and
``rust/Makefile`` (run ``make`` from inside ``rust/``).

Default mode is ``check``: nothing is written, drift against the
committed ``rust/`` tree is reported, and a non-zero exit signals
trouble. Pass ``--write`` to update the tracked files.

Usage:
    python tools/extract_rust.py            # check vs rust/
    python tools/extract_rust.py --write     # update rust/
"""

import argparse
from pathlib import Path

from tools_config import CHAPTERS_DIR, ROOT
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

RUST_DIR = ROOT / "rust"


def route_rust(doc: Document, block: Block) -> str | None:
    """A ```rust block naming its file with a `// path` first line."""
    if block.lang != "rust":
        return None
    slug = block.rust_slug
    return f"rust/{slug}" if slug else None


def route_caller(doc: Document, block: Block) -> str | None:
    """A ```python block whose `# rust/...` slug makes it a crate's caller.

    extract_examples.py passes over exactly these, since the compiled
    module they import does not exist in the main build's environment.
    """
    if not block.is_python:
        return None
    slug = block.slug
    return slug if slug and slug.startswith("rust/") else None


def extract(markdown_dir: Path = CHAPTERS_DIR) -> ExtractResult:
    docs = (Document.parse(md) for md in md_files([markdown_dir]))
    return extract_blocks(docs, [route_rust, route_caller])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="update the tracked rust/ files (default: check only)")
    args = ap.parse_args(argv)

    result = extract()
    print(f"Scanned {CHAPTERS_DIR.name}: {len(result.files)} rust/ file(s).")

    report_conflicts(result)

    if args.write:
        written = write_tree(result, ROOT)
        print(f"\nWrote {written} changed file(s) under {RUST_DIR.name}/.")
        return 1 if result.conflicts else 0

    missing, changed = check_against(result, ROOT)
    report_drift(missing, changed, noun="file", where=RUST_DIR.name)

    if not (missing or changed or result.conflicts):
        print(f"\nIn sync: every {RUST_DIR.name}/ file matches the book.")
        return 0
    print(f"\n(Run with --write to update {RUST_DIR.name}/.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
