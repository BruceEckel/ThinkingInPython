#!/usr/bin/env python3
"""Tidy imports in the book's python listings, writing back to Markdown.

ruff's import rules are part of the lint gate, but the gate runs on the
extracted tree (``build/examples/``), which is regenerated from the Markdown.
So an automatic fix has to land in the Markdown source.

Running ruff on the real extracted files (rather than each block in isolation)
matters: ruff's isort classifies a listing's sibling imports as first-party only
when it can see those files on disk, so an in-place fix on the tree sorts the way
the gate expects. This extracts nothing itself; run it after the tree is built
(``make fix-imports`` depends on ``extract``). For each ```python block that
names an extractable file, it runs ``ruff check --fix-only --select I,F401``
over the tree (sort the import block and drop unused imports, leaving
deliberately-unused ones that per-file-ignores exempt), then splices each fixed
file back into the block it came from.

Usage:
    python tools/fix_imports.py          # report listings to organize (exit 1)
    python tools/fix_imports.py --fix     # rewrite them in place
    python tools/fix_imports.py --fix Chapters/05_Modules_and_Packages.md
"""

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = ROOT / "Chapters"
DEFAULT_TREE = ROOT / "build" / "examples"
# A python fenced block, e.g. ```python or ```py.
FENCE_RE = re.compile(r'^```(\w+)?\s*$')
# First content line of a block naming its relative path, e.g. "# trace.py".
PATH_LINE_RE = re.compile(r'^#\s*([\w./\\-]+\.\w+)\s*$')


def block_slug(block: list[str]) -> str | None:
    """The relative path a block names on its first content line, if any."""
    for line in block:
        if line.strip():
            m = PATH_LINE_RE.match(line.rstrip('\n\r'))
            return m.group(1).replace('\\', '/') if m else None
    return None


def find_ruff() -> list[str]:
    """The ruff command: the venv binary if present, else ``uv run ruff``."""
    for rel in ('.venv/Scripts/ruff.exe', '.venv/bin/ruff'):
        binary = ROOT / rel
        if binary.exists():
            return [str(binary)]
    return ['uv', 'run', 'ruff']


def ruff_fix_tree(tree: Path, ruff: list[str]) -> None:
    """Tidy imports in place across the extracted tree.

    I organizes the import block; F401 drops unused imports. ruff's autofix
    honors per-file-ignores, so a deliberately unused import (such as the one
    in import_module.py) is left alone.
    """
    subprocess.run(
        ruff + ['check', '--fix-only', '--select', 'I,F401', str(tree)],
        check=False,
    )


def splice_markdown(
    text: str, fixed_for
) -> tuple[str, list[str]]:
    """Replace each slugged python block with its organized version.

    ``fixed_for(slug)`` returns the organized file text, or None to leave the
    block untouched. Returns ``(new_text, changed_slugs)``.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changed: list[str] = []
    i, n = 0, len(lines)

    while i < n:
        m = FENCE_RE.match(lines[i].rstrip('\n\r'))
        if not (m and (m.group(1) or '') in ('python', 'py')):
            out.append(lines[i])
            i += 1
            continue

        out.append(lines[i])  # opening fence
        i += 1
        start = i
        while i < n and not lines[i].startswith('```'):
            i += 1
        block = lines[start:i]
        fence_close = lines[i] if i < n else None
        if i < n:
            i += 1

        slug = block_slug(block)
        fixed = fixed_for(slug) if slug is not None else None
        if (slug is not None and fixed is not None
                and fixed != ''.join(block)):
            out.extend(fixed.splitlines(keepends=True))
            changed.append(slug)
        else:
            out.extend(block)
        if fence_close is not None:
            out.append(fence_close)

    return ''.join(out), changed


def collect_markdown(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        if t.is_dir():
            files.extend(sorted(t.glob('*.md')))
        elif t.suffix == '.md':
            files.append(t)
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        'targets', nargs='*', type=Path, default=[CHAPTERS_DIR],
        help='Markdown files or directories (default: Chapters/)',
    )
    ap.add_argument(
        '--fix', action='store_true',
        help='rewrite listings in place (default: report only)',
    )
    ap.add_argument(
        '--tree', type=Path, default=DEFAULT_TREE,
        help=f'extracted-examples tree to sort (default: {DEFAULT_TREE})',
    )
    args = ap.parse_args(argv)

    if not args.tree.exists():
        print(
            f"No extracted tree at {args.tree}. "
            "Run `python tools/extract_examples.py --write` first."
        )
        return 1

    ruff_fix_tree(args.tree, find_ruff())

    files = collect_markdown(args.targets)
    total = 0
    for md in files:
        chapter = md.stem

        def fixed_for(slug: str | None) -> str | None:
            if slug is None:
                return None
            fp = args.tree / chapter / slug
            return fp.read_text(encoding='utf-8') if fp.exists() else None

        new_text, changed = splice_markdown(
            md.read_text(encoding='utf-8'), fixed_for
        )
        if not changed:
            continue
        total += len(changed)
        if args.fix:
            md.write_text(new_text, encoding='utf-8', newline='\n')
            print(f"organized {md.name}: {', '.join(changed)}")
        else:
            print(f"{md.name}: would organize {', '.join(changed)}")

    if total == 0:
        print("Imports OK: every listing is organized.")
        return 0
    if args.fix:
        print(f"\nOrganized imports in {total} listing(s).")
        return 0
    print(f"\n{total} listing(s) need organizing. Run `make fix-imports`.")
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
