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
from dataclasses import dataclass, field
from pathlib import Path

from tools_config import CHAPTERS_DIR, ROOT, RUST_FENCE_RE, RUST_PATH_LINE_RE
from tools_pycode import iter_python_blocks, walk_fenced
from tools_repo import block_slug, md_files, write_text_lf

RUST_DIR = ROOT / "rust"


@dataclass
class RustFile:
    path: str  # relative to ROOT (starts with "rust/"), forward slashes
    content: str  # verbatim block text, including the trailing newline
    source_md: str  # chapter file the block came from
    kind: str  # "rust" or "python"


@dataclass
class ExtractResult:
    files: dict[str, RustFile] = field(default_factory=dict)
    conflicts: list[tuple[str, str, str]] = field(default_factory=list)


def _rust_slug(block: list[str]) -> str | None:
    """The path a ```rust block's first content line names, if any."""
    for line in block:
        if line.strip():
            m = RUST_PATH_LINE_RE.match(line.rstrip("\n\r"))
            return m.group(1).replace("\\", "/") if m else None
    return None


def _iter_rust_blocks(lines: list[str]):
    for ev in walk_fenced(lines, open_re=RUST_FENCE_RE):
        if ev.match is not None:
            yield lines[ev.open_at + 1:ev.end]


def extract(markdown_dir: Path = CHAPTERS_DIR) -> ExtractResult:
    result = ExtractResult()

    def add(rel: str, content: str, md_name: str, kind: str) -> None:
        existing = result.files.get(rel)
        if existing and existing.content != content:
            result.conflicts.append((rel, existing.source_md, md_name))
            return
        result.files[rel] = RustFile(rel, content, md_name, kind)

    for md in md_files([markdown_dir]):
        text = md.read_text(encoding="utf-8")
        lines = text.splitlines()

        for block in _iter_rust_blocks(lines):
            slug = _rust_slug(block)
            if slug is None:
                continue
            content = "\n".join(block).rstrip("\n") + "\n"
            add(f"rust/{slug}", content, md.name, "rust")

        for _, block in iter_python_blocks(lines):
            slug = block_slug(block)
            if slug is None or not slug.startswith("rust/"):
                continue
            content = "\n".join(block).rstrip("\n") + "\n"
            add(slug, content, md.name, "python")

    return result


def write_files(result: ExtractResult) -> int:
    written = 0
    for f in result.files.values():
        dest = ROOT / f.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_text(encoding="utf-8") != f.content:
            write_text_lf(dest, f.content)
            written += 1
    return written


def check_against_tree(result: ExtractResult) -> tuple[list[str], list[str]]:
    """Compare extracted files to what is currently under rust/."""
    missing, changed = [], []
    for f in result.files.values():
        dest = ROOT / f.path
        if not dest.exists():
            missing.append(f.path)
        elif dest.read_text(encoding="utf-8") != f.content:
            changed.append(f.path)
    return missing, changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="update the tracked rust/ files (default: check only)")
    args = ap.parse_args(argv)

    result = extract()
    print(f"Scanned {CHAPTERS_DIR.name}: {len(result.files)} rust/ file(s).")

    if result.conflicts:
        print(f"\n{len(result.conflicts)} conflicting duplicate path(s) "
              "(same path, differing content):")
        for path, a, b in result.conflicts:
            print(f"  ! {path}  ({a} vs {b})")

    if args.write:
        written = write_files(result)
        print(f"\nWrote {written} changed file(s) under {RUST_DIR.name}/.")
        return 1 if result.conflicts else 0

    missing, changed = check_against_tree(result)
    if missing:
        print(f"\n{len(missing)} file(s) in the book but not under "
              f"{RUST_DIR.name}/:")
        for p in missing:
            print(f"  + {p}")
    if changed:
        print(f"\n{len(changed)} file(s) whose book text differs from "
              f"{RUST_DIR.name}/:")
        for p in changed:
            print(f"  ~ {p}")

    if not (missing or changed or result.conflicts):
        print(f"\nIn sync: every {RUST_DIR.name}/ file matches the book.")
        return 0
    print(f"\n(Run with --write to update {RUST_DIR.name}/.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
