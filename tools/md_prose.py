#!/usr/bin/env python
"""Shared Markdown classification helpers.

Tools that work on the book's prose (``reflow_prose.py`` and the prose linter)
need the same two distinctions: which *lines* are prose rather than code,
headings, lists, tables, and so on; and which *inline* spans (code spans,
footnotes) are not prose and must be ignored. Keeping both here means the rules
stay identical across tools.

``is_prose_line`` classifies a single line. It is stateless, so a caller that
must skip fenced code blocks tracks the fence itself: a line matching ``FENCE``
opens or closes a block.

``mask``/``unmask`` replace inline code spans and footnotes with private-use
characters, so their internal punctuation is invisible to text processing.
"""

from __future__ import annotations

import re

# --- Inline masking ---------------------------------------------------------

# Private-use characters stand in for masked spans (inline code, footnotes) so
# their internal punctuation is invisible to callers.
PUA_START = 0xE000
PUA_END = 0xF8FF

_FOOTNOTE = re.compile(r"\^\[[^\]]*\]")
_INLINE_CODE = re.compile(r"``[^`]*``|`[^`]*`")


def mask(text: str) -> tuple[str, list[str]]:
    """Replace footnotes and inline code spans with private-use placeholders."""
    store: list[str] = []

    def repl(m: re.Match[str]) -> str:
        store.append(m.group(0))
        return chr(PUA_START + len(store) - 1)

    text = _FOOTNOTE.sub(repl, text)
    text = _INLINE_CODE.sub(repl, text)
    return text, store


def unmask(text: str, store: list[str]) -> str:
    """Restore the spans replaced by `mask`."""
    for i, original in enumerate(store):
        text = text.replace(chr(PUA_START + i), original)
    return text


def code_spans(text: str) -> list[tuple[int, int]]:
    """(start, end) ranges of inline code spans and footnotes in `text`.

    Lets a caller ignore those regions without shifting column positions, the
    way `mask` would.
    """
    spans: list[tuple[int, int]] = []
    for pattern in (_FOOTNOTE, _INLINE_CODE):
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    return spans


# --- Block classification ---------------------------------------------------

FENCE = re.compile(r"^\s*(```+|~~~+)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
HR = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
LIST = re.compile(r"^\s*([-*+]|\d+[.)])\s")
# Full match for a list item: leading indent, marker, gap, then the text.
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(.*)$")
BLOCKQUOTE = re.compile(r"^\s*>")
TABLE = re.compile(r"^\s*\|")
HTML = re.compile(r"^\s*<")
INDENTED_CODE = re.compile(r"^(\t| {4,})")


def is_prose_line(line: str) -> bool:
    """True if `line` is ordinary prose: not code, a heading, a list, etc.

    Stateless: it does not know whether `line` sits inside a fenced code block.
    A caller that must skip fences tracks that itself using `FENCE`.
    """
    if not line.strip():
        return False
    return not (
        HEADING.match(line)
        or HR.match(line)
        or LIST.match(line)
        or BLOCKQUOTE.match(line)
        or TABLE.match(line)
        or HTML.match(line)
        or INDENTED_CODE.match(line)
    )
