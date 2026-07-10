#!/usr/bin/env python
"""Lint Markdown prose for small mechanical slips a spell checker misses.

Checks the prose in `Chapters/*.md` for:

  MULTI-SPACE    more than one space between words
  SPACE-BEFORE   a space before . , ; ! or ?
  BLANK-RUN      more than one blank line in a row
  QUOTE-PUNCT    a period or comma after a closing " (it belongs inside)
  TRAILING-WS    trailing whitespace (a two-space hard break is allowed)

Code is skipped through the shared classifier in `md_prose`: fenced code,
indented code, tables, blockquotes, HTML, and rules are ignored, and inline code
spans and footnotes are ignored within a prose line. Headings and list-item text
are checked, but their markers are not.

Exit status is non-zero if any issue is found, so it works as a gate. It is run
as part of `make spell`.

Usage:
    python tools/prose_lint.py                 # all of Chapters/
    python tools/prose_lint.py Chapters/06_Classes.md
    python tools/prose_lint.py Chapters        # a directory: every *.md in it
"""

import argparse
import re
from pathlib import Path

from md_prose import FENCE, HEADING, LIST_ITEM, code_spans, is_prose_line

_MULTI_SPACE = re.compile(r"(?<=\S) {2,}(?=\S)")
_SPACE_BEFORE = re.compile(r" +([.,;!?])")
_QUOTE_PUNCT = re.compile(r'"([.,])')
_TRAILING_WS = re.compile(r"[ \t]+$")

Finding = tuple[int, int, str, str]  # line, column, code, message


def _in_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def _prose_text(line: str) -> tuple[str, int] | None:
    """Return (text, offset) for the prose part of a line, or None to skip it.

    A heading or list marker is stripped so its own spacing is not flagged;
    `offset` is where the returned text starts, for column reporting.
    """
    heading = HEADING.match(line)
    if heading:
        return line[heading.end():], heading.end()
    item = LIST_ITEM.match(line)
    if item:
        indent, bullet, gap, text = item.groups()
        return text, len(indent) + len(bullet) + len(gap)
    if is_prose_line(line):
        return line, 0
    return None


def lint_text(text: str) -> list[Finding]:
    """Return every prose issue in one Markdown document."""
    findings: list[Finding] = []
    lines = text.splitlines()
    n = len(lines)
    in_fence = False
    fence_marker = ""
    blank_run = 0

    # Skip YAML front matter.
    start = 0
    if lines and lines[0].strip() == "---":
        start = 1
        while start < n and lines[start].strip() not in ("---", "..."):
            start += 1
        start += 1

    for idx in range(start, n):
        line = lines[idx]
        lineno = idx + 1

        if in_fence:
            if FENCE.match(line) and line.strip().startswith(fence_marker):
                in_fence = False
            blank_run = 0
            continue
        fence = FENCE.match(line)
        if fence:
            in_fence = True
            fence_marker = fence.group(1)[0] * 3
            blank_run = 0
            continue

        if not line.strip():
            blank_run += 1
            if blank_run > 1:
                findings.append((lineno, 1, "BLANK-RUN",
                                 "more than one blank line in a row"))
            if line:
                findings.append((lineno, 1, "TRAILING-WS",
                                 "whitespace on a blank line"))
            continue
        blank_run = 0

        # Trailing whitespace; a Markdown hard break is exactly two spaces.
        trailing = _TRAILING_WS.search(line)
        if trailing and trailing.group(0) != "  ":
            findings.append((lineno, trailing.start() + 1, "TRAILING-WS",
                             "trailing whitespace"))

        prose = _prose_text(line)
        if prose is None:
            continue
        body, offset = prose
        spans = code_spans(body)

        for m in _MULTI_SPACE.finditer(body):
            if not _in_span(m.start(), spans):
                findings.append((lineno, offset + m.start() + 1, "MULTI-SPACE",
                                 "more than one space between words"))

        for m in _SPACE_BEFORE.finditer(body):
            punct = m.group(1)
            if punct == "." and body[m.end():m.end() + 1] == ".":
                continue  # ellipsis, not a misplaced period
            if not _in_span(m.start(1), spans):
                findings.append((lineno, offset + m.start() + 1, "SPACE-BEFORE",
                                 f"space before '{punct}'"))

        for m in _QUOTE_PUNCT.finditer(body):
            if not _in_span(m.start(), spans):
                findings.append((lineno, offset + m.start() + 1, "QUOTE-PUNCT",
                                 f"'{m.group(1)}' after a closing quote; "
                                 "put it inside"))

    findings.sort()
    return findings


def _iter_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        files.extend(sorted(path.glob("*.md")) if path.is_dir() else [path])
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files or directories (default: Chapters/)")
    args = ap.parse_args(argv)

    files = _iter_files(args.paths or ["Chapters"])
    total = 0
    for path in files:
        for lineno, col, code, message in lint_text(
                path.read_text(encoding="utf-8")):
            print(f"{path}:{lineno}:{col}: {code} {message}")
            total += 1

    if total:
        print(f"\n{total} prose issue(s).")
        return 1
    print("No prose issues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
