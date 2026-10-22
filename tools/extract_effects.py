#!/usr/bin/env python3
"""Extract chapter 44's Koka, Flix, Scala, and TypeScript programs into effects/.

The Effect Management chapter shows one greeting program in four other
languages, two with native Effects (Koka, Flix) and two library Effect
systems (ZIO for Scala, Effect for TypeScript). Each is a complete
program, and this tool keeps a buildable copy of each under ``effects/``
the way ``extract_rust.py`` keeps chapter 18's crates under ``rust/``.
A fenced block whose language is one of ``EFFECT_LANGS`` and whose first
content line is a ``//`` comment naming the file, relative to
``effects/``, extracts there::

    ```koka
    // koka/greet.kk
    ...
    ```

All four languages share the ``//`` comment form, so one marker
convention covers them (``Block.slash_slug``). A block of one of these
languages with no such first line is a fragment and extracts nothing.

``effects/`` also holds real, hand-maintained project files this tool
never touches: ``ts/package.json`` and its lockfile, ``ts/tsconfig.json``,
``zio/project.scala``, ``expected.txt``, the READMEs. Only the specific
paths a book block names are read, checked, or written, so there is no
"clean and regenerate" mode and no orphan detection: a renamed or deleted
book slug leaves its old file behind until removed by hand.

Building and running the programs needs the four toolchains and is never
done here, nor by the main build: ``tools/effects_run.py`` and the
``effects-*`` tasks in ``tools/tasks.py`` (``tip effects-all``) do that,
and skip any toolchain that is not installed. See ``effects/README.md``.

Default mode is ``check``: nothing is written, drift against the
committed ``effects/`` tree is reported, and a non-zero exit signals
trouble. ``tip check`` and the gate run it, so a chapter 44 edit that
leaves ``effects/`` stale fails the build; ``tip effects-sync`` is the
fix. Pass ``--write`` to update the tracked files.

Usage:
    python -m tools.extract_effects            # check vs effects/
    python -m tools.extract_effects --write    # update effects/
"""

import argparse
from pathlib import Path

from tools.config import CHAPTERS_DIR, ROOT
from tools.extract import (
    ExtractResult,
    check_or_write,
    extract as extract_blocks,
)
from tools.markdown import Block, Document
from tools.repo import md_files

EFFECTS_DIR = ROOT / "effects"

EFFECT_LANGS = frozenset({"koka", "flix", "scala", "typescript"})
"""The fence languages this tool claims. Rust has its own extractor."""


def route_effects(doc: Document, block: Block) -> str | None:
    """A block in one of `EFFECT_LANGS` naming its file with `// path`."""
    if block.lang not in EFFECT_LANGS:
        return None
    slug = block.slash_slug
    return f"effects/{slug}" if slug else None


def extract(markdown_dir: Path = CHAPTERS_DIR) -> ExtractResult:
    docs = (Document.parse(md) for md in md_files([markdown_dir]))
    return extract_blocks(docs, [route_effects])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="update the tracked effects/ files (default: check only)")
    args = ap.parse_args(argv)
    result = extract()
    print(f"Scanned {CHAPTERS_DIR.name}: {len(result.files)} effects/ file(s).")
    return check_or_write(result, ROOT, EFFECTS_DIR.name, write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
