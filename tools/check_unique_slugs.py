#!/usr/bin/env python3
"""Check that no two book listings share a filename.

Every extractable block carries a path comment on its first line
(`# module_singleton.py`), and `extract_examples.py` writes it under a
directory named for its chapter. Two chapters can therefore both define
`import_once.py` without any existing gate objecting: the files land in
different directories, so the trees stay in sync and the drift check
passes.

The collision still costs the reader. Searching the repository for a
listing named in the prose returns two unrelated files, and neither the
chapter nor the filename says which one the sentence meant. It costs the
build too, in a way that is easy to hit and hard to diagnose: one pytest
run covers every chapter, so two test modules with one basename collide
in `sys.modules`, and a test that imports `config` gets whichever
chapter's `config.py` was imported first.

So this check enforces one basename per listing across `Chapters/` and
`Solutions/`, reporting every place a name is reused.

Three kinds of reuse are legitimate and are not reported:

- A `shared:` listing lives in `utils/` and is imported by name from
  several chapters. It is one file, declared once.
- A chapter and its own solutions may reuse a name, since
  `Solutions/NN_x.md` answers `Chapters/NN_x.md` and the pairing is the
  point. Only cross-chapter reuse is a collision.
- `Solutions/` names its listings positionally, so every solutions file
  has an `exercise_1.py`. That is the convention rather than a clash,
  and pytest never collects those names.

Usage:
    python tools/check_unique_slugs.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from tools_config import ROOT
from tools_markdown import Document
from tools_report import Finding, report

CHAPTERS_DIR = ROOT / "Chapters"
SOLUTIONS_DIR = ROOT / "Solutions"

# Solutions/ names its listings by exercise number, so the same name
# appears in nearly every solutions file. That is the convention.
POSITIONAL = re.compile(r"^exercise_\d+[a-z]?\.py$")


def chapter_key(path: Path) -> str:
    """The chapter number a file belongs to, e.g. "24" or "A"."""
    return path.stem.split("_", 1)[0]


def collisions() -> list[Finding]:
    """One finding per listing whose basename another chapter also uses."""
    # basename -> [(chapter key, path, line, slug)]
    seen: defaultdict[str, list[tuple[str, Path, int, str]]] = (
        defaultdict(list)
    )
    sources = sorted(CHAPTERS_DIR.glob("*.md")) + sorted(
        SOLUTIONS_DIR.glob("*.md")
    )
    for md in sources:
        doc = Document.parse(md)
        for block in doc.python_blocks():
            slug = block.slug
            if slug is None:
                continue
            # A shared listing is one file by design.
            if slug.startswith("utils/"):
                continue
            base = Path(slug).name
            if POSITIONAL.match(base):
                continue
            seen[base].append(
                (chapter_key(md), md, block.line_number(0), slug)
            )

    findings: list[Finding] = []
    for base, uses in sorted(seen.items()):
        chapters = {key for key, _, _, _ in uses}
        if len(chapters) < 2:
            continue  # One chapter, or a chapter and its own solutions.
        for _, md, line, slug in uses:
            others = ", ".join(
                sorted(
                    f"{other.name}:{other_line}"
                    for _, other, other_line, _ in uses
                    if other != md
                )
            )
            findings.append(
                Finding(
                    md.relative_to(ROOT),
                    line,
                    f"`{slug}` reuses the filename `{base}`, "
                    f"also used by {others}",
                )
            )
    return findings


def main() -> int:
    return report(
        collisions(),
        clean="Listing filenames are unique across chapters.",
        problem=(
            "{n} listing filename collision(s). Rename one side to "
            "something distinctive, then run `make sync` and delete the "
            "stale file under Examples/ (a name still used elsewhere is "
            "reported as 'referenced', so prune-examples leaves it)."
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
