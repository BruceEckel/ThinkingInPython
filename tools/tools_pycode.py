#!/usr/bin/env python3
"""Shared Python-source scanning: quote tracking and fenced-block walking.

Several tools/*.py scripts need the same two low-level scans over a
```python listing: tracking single/double/triple-quote state to find a
line's real (non-string) '#', and walking a Markdown file's fenced blocks.
Both were reimplemented per file with the same core algorithm; this module
gives them one home.

Named tools_pycode (not the shorter "pycode") for the same reason as
tools_config/tools_repo: it must never collide with a book listing's own
filename via Python's sys.modules cache. See tools_repo.py's docstring for
the failure that caused those two renames.
"""

import re
from collections.abc import Callable, Iterator
from typing import NamedTuple

from tools_config import FENCE_ANY_RE, FENCE_RE, PY_FENCE_RE


def scan_line(line: str, triple: str | None) -> tuple[int, str | None]:
    """Scan one line of Python source, tracking quote state.

    `triple` is the triple-quote delimiter (three single or three double
    quotes) still open from a previous line, or None. Returns
    (hash_index, triple_after): hash_index is the index of the line's
    first real (non-string) '#', or -1 if none; triple_after is the
    delimiter still open at the line's end, or None.
    """
    i, n = 0, len(line)
    quote = triple
    sq = dq = False
    while i < n:
        c = line[i]
        if quote:
            if line.startswith(quote, i):
                i += 3
                quote = None
                continue
            i += 1
            continue
        if sq:
            i += 2 if c == "\\" else 1
            if c == "'":
                sq = False
            continue
        if dq:
            i += 2 if c == "\\" else 1
            if c == '"':
                dq = False
            continue
        if line.startswith("'''", i) or line.startswith('"""', i):
            quote = line[i:i + 3]
            i += 3
            continue
        if c == "'":
            sq = True
            i += 1
            continue
        if c == '"':
            dq = True
            i += 1
            continue
        if c == "#":
            return i, quote
        i += 1
    return -1, quote


class FenceEvent(NamedTuple):
    """One step of a `walk_fenced` walk over a Markdown file's lines.

    A wanted block: `match` is the open line's re.Match (so callers can read
    its language from `match.group(1)`); the block's content is
    `lines[open_at + 1:end]`, both fence lines excluded; `lines[open_at]` is
    the open fence and `lines[end]` the close fence, if `end` is in range.

    A passthrough line (not a fence open, or a fence open that `wanted`
    rejected): `match` is None, `open_at` is the line's own index, and
    `end == open_at + 1`.
    """

    match: re.Match[str] | None
    open_at: int
    end: int


def walk_fenced(
    lines: list[str],
    *,
    open_re: re.Pattern[str] = FENCE_RE,
    is_close: Callable[[str], bool] | None = None,
    wanted: Callable[[re.Match[str]], bool] = lambda m: True,
) -> Iterator[FenceEvent]:
    """Walk `lines` top to bottom, yielding a FenceEvent per line or block.

    A line matching `open_re` and satisfying `wanted` opens a block: the
    walk then skips ahead to the next line satisfying `is_close` (default:
    starts with three backticks), treats everything between as that block's
    content, and resumes after the close (or at end of input, if no close is
    found). Any other line -- prose, or a fence `wanted` rejects -- is
    yielded as its own passthrough event, one line at a time, and the walk
    resumes at the very next line.

    That per-line fallback (rather than skipping a whole rejected fence as
    one opaque span) matches how the loops this replaces always worked: none
    of them tracked fence nesting, so a line that merely looks like a fence
    inside an unwanted block was always re-examined on its own. Trailing
    "\\r\\n" is stripped from each line before matching, so this works
    whether `lines` came from splitlines() or splitlines(keepends=True).
    """
    close = is_close or (lambda ln: ln.startswith("```"))

    i, n = 0, len(lines)
    while i < n:
        m = open_re.match(lines[i].rstrip("\r\n"))
        if m and wanted(m):
            j = i + 1
            while j < n and not close(lines[j].rstrip("\r\n")):
                j += 1
            yield FenceEvent(m, i, j)
            i = j + 1
        else:
            yield FenceEvent(None, i, i + 1)
            i += 1


def iter_python_blocks(lines: list[str]) -> Iterator[tuple[int, list[str]]]:
    """Yield (content_start_index, block_lines) for each ```python block.

    A convenience wrapper over `walk_fenced` for callers that only care
    about python-labeled blocks' content and don't need to reconstruct the
    surrounding document (comment_periods.py, listing_format.py): the open
    fence must match PY_FENCE_RE (indent-tolerant, "python" only, not "py"),
    and the block closes at the next line matching FENCE_ANY_RE.
    """
    for ev in walk_fenced(
        lines, open_re=PY_FENCE_RE,
        is_close=lambda ln: FENCE_ANY_RE.match(ln) is not None,
    ):
        if ev.match is not None:
            yield ev.open_at + 1, lines[ev.open_at + 1:ev.end]
