#!/usr/bin/env python3
"""Check quoted `ty` diagnostics against the listings they point at.

The book quotes `ty` output in fenced blocks (```text, or a bare fence)
that begin `error[...]` or `warning[...]`. Each quote carries a
location line, ` --> file.py:LINE:COL`, and gutter lines, `LINE | source`,
that reproduce the listing's source. Nothing gates those: a `#:`
marker is validated against a run, but a quoted diagnostic is prose,
so a listing edit that shifts a line, or a `ty` upgrade that changes
the message, leaves the quote stale with every gate green. The
2026-09-14 claims sweep found such quotes in chapters 08, 13, 20, and
46 and in several Solutions files.

This check reads every quoted block, follows each ` --> file:LINE`
line, and compares every gutter line that follows it with that line
of the extracted listing (`build/examples/<chapter>/` for Chapters/,
`build/solutions/<chapter>/` for Solutions/). A gutter line matches
when it equals the file's line, or equals it with a trailing
`# type: ignore` comment removed (the prose usually says the comment
was stripped to produce the diagnostic), or equals the file's line
with its leading `# ` removed (the book's convention is a
commented-out probe line). Anything else is reported, and so is a
location naming a file the tree does not hold, which usually means a
scratch name the prose explains.

Report-only: the exit code is 0 unless `--strict` is given, because
some quotes are deliberately against an edited copy of the listing
(a `match` block removed, a line uncommented) and the shifted line
numbers are right for that copy. Read each hit against its prose.

Usage:
    python -m tools.check_quoted_diagnostics            # Chapters/ and Solutions/
    python -m tools.check_quoted_diagnostics Chapters/46_*.md
    python -m tools.check_quoted_diagnostics --strict   # exit 1 on any hit
"""
import argparse
import re
import sys
from collections.abc import Iterator
from pathlib import Path

from tools.config import BUILD_DIR, ROOT
from tools.markdown import Block, Document
from tools.report import Finding, report

DIAGNOSTIC_START = re.compile(r"^(error|warning)\[[\w-]+\]")
LOCATION = re.compile(r"^\s*-->\s*(\S+?):(\d+):(\d+)\s*$")
GUTTER = re.compile(r"^\s*(\d+)\s\|(?: (.*))?$")
TYPE_IGNORE = re.compile(r"\s*#\s*type:\s*ignore(\[[\w,-]+\])?\s*$")
# The bar ty prints at the left of a multi-line span's continuation lines.
SPAN_BAR = re.compile(r"^\s*\|\s")

TREES = {"Chapters": BUILD_DIR / "examples", "Solutions": BUILD_DIR / "solutions"}


def quoted_blocks(doc: Document) -> Iterator[Block]:
    """Fenced blocks whose first content line is a `ty` diagnostic."""
    for block in doc.blocks:
        first = next((line for line in block.lines if line.strip()), "")
        if DIAGNOSTIC_START.match(first):
            yield block


def listing_dirs(md: Path) -> list[Path]:
    """Where a quoted file may live, for a chapter or solutions file.

    A solutions file often quotes a diagnostic against the chapter's own
    listing, so its chapter directory under build/examples is searched
    after its own, and the shared helpers in build/examples/utils last.
    """
    tree = TREES.get(md.parent.name)
    if tree is None:
        return []
    dirs = [tree / md.stem]
    if tree is not TREES["Chapters"]:
        dirs.append(TREES["Chapters"] / md.stem)
    dirs.append(TREES["Chapters"] / "utils")
    return dirs


def locate(name: str, dirs: list[Path]) -> Path | None:
    for d in dirs:
        candidate = d / name
        if candidate.exists():
            return candidate
    return None


def gutter_matches(quoted: str, actual: str) -> bool:
    """Whether a quoted gutter line reproduces the listing's line.

    Both sides are compared stripped, since ty indents the source of a
    multi-line span and prefixes its continuation lines with a `|` bar.
    """
    quoted = SPAN_BAR.sub("", quoted).strip()
    actual = actual.strip()
    if quoted == actual:
        return True
    if TYPE_IGNORE.sub("", actual) == quoted:
        return True
    if actual.startswith("# ") and actual[2:] == quoted:
        return True
    return False


def find(doc: Document) -> Iterator[Finding]:
    """Every gutter line in a quoted diagnostic that disagrees with its file."""
    dirs = listing_dirs(doc.path)
    if not dirs:
        return
    for block in quoted_blocks(doc):
        name = ""
        lines: list[str] | None = None
        for index, raw in enumerate(block.lines):
            line = raw.rstrip("\n\r")
            loc = LOCATION.match(line)
            if loc:
                name = loc.group(1).replace("\\", "/")
                found = locate(name, dirs)
                if found is None:
                    lines = None
                    yield Finding(
                        doc.path, block.line_number(index),
                        f"quoted location names {name}, which "
                        f"{dirs[0].relative_to(ROOT)} does not hold",
                    )
                else:
                    lines = found.read_text(encoding="utf-8").split("\n")
                continue
            gut = GUTTER.match(line)
            if not gut or lines is None:
                continue
            n = int(gut.group(1))
            quoted = gut.group(2) or ""
            if not (0 < n <= len(lines)):
                yield Finding(
                    doc.path, block.line_number(index),
                    f"{name} has no line {n} (quoted: {quoted!r})",
                )
                continue
            actual = lines[n - 1].rstrip("\r")
            if not gutter_matches(quoted, actual):
                yield Finding(
                    doc.path, block.line_number(index),
                    f"{name}:{n} reads {actual.strip()!r}, "
                    f"quote shows {quoted.strip()!r}",
                )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files to check (default: Chapters/ and "
                         "Solutions/)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when anything is reported")
    args = ap.parse_args(argv)
    paths = [Path(p) for p in args.paths] or sorted(
        list((ROOT / "Chapters").glob("*.md"))
        + list((ROOT / "Solutions").glob("*.md")))
    findings = [f for p in paths for f in find(Document.parse(p))]
    code = report(
        findings,
        clean="Quoted diagnostics match their listings.",
        problem="{n} quoted diagnostic line(s) disagree with the extracted "
                "listing. Read each against its prose: a quote against an "
                "edited copy is expected, a stale line number is not.",
    )
    return code if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
