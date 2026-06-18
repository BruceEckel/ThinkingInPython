#!/usr/bin/env python
"""Reflow Markdown prose to one sentence per line.

Prose paragraphs in `Markdown/*.md` are hard-wrapped at a fixed column. That
makes editing awkward: changing a word reflows a whole paragraph and produces a
noisy git diff. This tool rewrites each prose paragraph so every sentence sits
on its own line. Editing then touches only the sentences that change, and diffs
read sentence by sentence.

A sentence longer than `--width` is broken further, at top-level clause
punctuation (",", ";", ":"), so no line is wide enough to wrap in an editor. A
greedy fill inserts the fewest breaks needed: short sentences are left on one
line. Breaks are never made inside parentheses, brackets, inline code, or
footnotes.

Only plain prose paragraphs are touched. Everything else is preserved verbatim:
fenced code, indented code, tables, headings, list items, blockquotes, HTML
blocks, horizontal rules, and YAML front matter. Inline code spans and footnotes
are masked before splitting so their internal punctuation never causes a break.

Safety: a file is rewritten only if its whitespace-normalized text is unchanged.
The tool only moves newlines; it never adds, drops, or alters a word. If that
invariant ever fails the file is left untouched and reported.

Usage:
    uv run python tools/reflow_prose.py                  # check all Markdown/, no write
    uv run python tools/reflow_prose.py --write           # rewrite all Markdown/
    uv run python tools/reflow_prose.py --write 02        # rewrite one chapter by number
    uv run python tools/reflow_prose.py --diff Tour       # diff a chapter by name part
    uv run python tools/reflow_prose.py --write FILE...   # rewrite specific files
    uv run python tools/reflow_prose.py --width 100       # change the wrap width

A positional argument may be a file path or a chapter selector matched against
Markdown/: a number or stem prefix ("02", "02_A_Python") or a substring ("Tour").
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

# Sentences wider than this are broken at clause punctuation. Roughly the
# column at which an editor would otherwise soft-wrap the line.
_DEFAULT_WIDTH = 80

# Top-level punctuation a long sentence may be broken after.
_BREAK_PUNCT = ",;:"

# Closing quotes and brackets that may trail the break punctuation and belong
# with the clause, as in `means "raw," which ...`. Masked spans (inline code,
# footnotes) also count, and are recognized separately by their PUA range.
_CLOSERS_SET = {'"', "'", ")", "]", "’", "”", "»"}

# A clause break is suppressed only while the current line is shorter than this,
# which keeps a tiny lead-in ("Initially,", "That is,") from being stranded on
# its own line. Kept small so a substantial lead-in clause still breaks.
_MIN_LEAD = 20

# Abbreviations whose trailing period must not end a sentence. Stored without
# the final period and lowercased; "e.g." is stored as "e.g" (its internal dot
# is part of the token scanned back to whitespace).
ABBREV = {
    "e.g", "i.e", "etc", "vs", "cf", "al", "ie", "eg", "mr", "mrs", "ms", "dr",
    "prof", "st", "fig", "no", "vol", "pp", "ch", "sec", "approx", "inc", "ltd",
    "co", "jr", "sr", "esp", "ca", "viz", "resp",
}

# Private-use characters stand in for masked spans (inline code, footnotes) so
# their internal punctuation is invisible to the splitter.
_PUA_START = 0xE000
_PUA_END = 0xF8FF

_FOOTNOTE = re.compile(r"\^\[[^\]]*\]")
_INLINE_CODE = re.compile(r"``[^`]*``|`[^`]*`")

# Character-class bodies, built with chr()/\u escapes so no literal smart quote
# or private-use character appears in this source file. A sentence may end with
# trailing closers (quotes, brackets, masked spans) and the next may begin with
# an opener, a capital, a digit, or a masked span.
_PUA_RANGE = chr(_PUA_START) + "-" + chr(_PUA_END)
_CLOSER_BODY = "\"'’”)»*\\]" + _PUA_RANGE
_OPENER_BODY = "\"'“«([*A-Z0-9" + _PUA_RANGE

_BOUNDARY = re.compile(
    r"[.!?]+[" + _CLOSER_BODY + r"]*(\s+)(?=[" + _OPENER_BODY + r"])"
)


def _mask(text: str) -> tuple[str, list[str]]:
    store: list[str] = []

    def repl(m: re.Match[str]) -> str:
        store.append(m.group(0))
        return chr(_PUA_START + len(store) - 1)

    text = _FOOTNOTE.sub(repl, text)
    text = _INLINE_CODE.sub(repl, text)
    return text, store


def _unmask(text: str, store: list[str]) -> str:
    for i, original in enumerate(store):
        text = text.replace(chr(_PUA_START + i), original)
    return text


def _disp_len(masked: str, store: list[str]) -> int:
    """Length of `masked` as it renders, with masked spans expanded."""
    return len(_unmask(masked, store))


def _token_before(text: str, dot_index: int) -> str:
    """The run of word characters and dots immediately before `dot_index`."""
    j = dot_index
    while j > 0 and (text[j - 1].isalnum() or text[j - 1] == "."):
        j -= 1
    return text[j:dot_index]


def _split_masked(masked: str) -> list[str]:
    """Split masked paragraph text into masked sentence strings."""
    out: list[str] = []
    start = 0
    for m in _BOUNDARY.finditer(masked):
        first_punct = m.start()
        # Walk to the final consecutive .!? char in this terminator run.
        p = first_punct
        while p + 1 < len(masked) and masked[p + 1] in ".!?":
            p += 1
        is_single_dot = masked[first_punct] == "." and p == first_punct

        if is_single_dot:
            token = _token_before(masked, first_punct)
            stripped = token.rstrip(".").lower()
            next_char = masked[m.end():m.end() + 1]
            prev_char = masked[first_punct - 1] if first_punct > 0 else ""
            # Abbreviation, single initial (e.g. "B."), or a decimal like
            # "3. 14": do not treat as a sentence boundary.
            if stripped in ABBREV:
                continue
            if len(token) == 1 and token.isupper():
                continue
            if prev_char.isdigit() and next_char.isdigit():
                continue

        out.append(masked[start:m.end()].rstrip())
        start = m.end()

    tail = masked[start:].rstrip()
    if tail:
        out.append(tail)
    return out


def split_sentences(paragraph: str) -> list[str]:
    """Split one logical paragraph (already single-spaced) into sentences."""
    masked, store = _mask(paragraph)
    return [_unmask(s, store) for s in _split_masked(masked)]


def _clause_segments(masked: str) -> list[str]:
    """Split a masked sentence at top-level ",", ";", ":" followed by a space.

    Each segment keeps its trailing punctuation. Punctuation inside parentheses,
    brackets, or masked spans is ignored, so the segments are clause-sized.
    """
    depth = 0
    segs: list[str] = []
    start = 0
    i = 0
    n = len(masked)
    while i < n:
        c = masked[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth = max(0, depth - 1)
        elif c in _BREAK_PUNCT and depth == 0:
            # Absorb closing quotes/brackets that trail the punctuation, so the
            # break falls after them: `means "raw,"` | `which ...`.
            j = i + 1
            while j < n and (masked[j] in _CLOSERS_SET
                             or _PUA_START <= ord(masked[j]) <= _PUA_END):
                j += 1
            if j < n and masked[j] == " ":
                k = j
                while k < n and masked[k] == " ":
                    k += 1
                if k < n:  # never break on trailing punctuation
                    segs.append(masked[start:j])
                    start = k
                    i = k
                    continue
        i += 1
    tail = masked[start:].rstrip()
    if tail:
        segs.append(tail)
    return segs


def _wrap_clause(masked_sentence: str, store: list[str], width: int) -> list[str]:
    """Break one masked sentence onto clause lines no wider than `width`."""
    if _disp_len(masked_sentence, store) <= width:
        return [masked_sentence]
    segs = _clause_segments(masked_sentence)
    if len(segs) <= 1:
        return [masked_sentence]

    # Greedy fill: pack clauses up to `width`, breaking at clause punctuation.
    # The only exception is a lead-in shorter than `_MIN_LEAD`, which is held
    # back so a tiny first clause is not stranded alone.
    lines: list[str] = []
    cur = ""
    for seg in segs:
        if not cur:
            cur = seg
            continue
        fits = _disp_len(cur, store) + 1 + _disp_len(seg, store) <= width
        if fits or _disp_len(cur, store) < _MIN_LEAD:
            cur = f"{cur} {seg}"
        else:
            lines.append(cur)
            cur = seg
    if cur:
        lines.append(cur)
    return lines


def _reflow_text(joined: str, width: int) -> list[str]:
    """Reflow one logical block of text into sentence/clause lines."""
    masked, store = _mask(joined)
    result: list[str] = []
    for sentence in _split_masked(masked):
        for clause in _wrap_clause(sentence, store, width):
            result.append(_unmask(clause, store))
    return result


# --- Block classification ---------------------------------------------------

_FENCE = re.compile(r"^\s*(```+|~~~+)")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
_HR = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
_LIST = re.compile(r"^\s*([-*+]|\d+[.)])\s")
# Full match for a list item: leading indent, marker, gap, then the text.
_LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)(.*)$")
_BLOCKQUOTE = re.compile(r"^\s*>")
_TABLE = re.compile(r"^\s*\|")
_HTML = re.compile(r"^\s*<")
_INDENTED_CODE = re.compile(r"^(\t| {4,})")


def _is_prose_line(line: str) -> bool:
    if not line.strip():
        return False
    return not (
        _HEADING.match(line)
        or _HR.match(line)
        or _LIST.match(line)
        or _BLOCKQUOTE.match(line)
        or _TABLE.match(line)
        or _HTML.match(line)
        or _INDENTED_CODE.match(line)
    )


def reflow(text: str, width: int = _DEFAULT_WIDTH) -> tuple[str, int]:
    """Return (reflowed_text, paragraphs_reflowed)."""
    lines = text.splitlines(keepends=False)
    out: list[str] = []
    i = 0
    n = len(lines)
    in_fence = False
    fence_marker = ""
    reflowed = 0

    # YAML front matter: a leading '---' line opens it.
    if lines and lines[0].strip() == "---":
        out.append(lines[0])
        i = 1
        while i < n:
            out.append(lines[i])
            closed = lines[i].strip() in ("---", "...")
            i += 1
            if closed:
                break

    while i < n:
        line = lines[i]

        if in_fence:
            out.append(line)
            if _FENCE.match(line) and line.strip().startswith(fence_marker):
                in_fence = False
            i += 1
            continue

        fence = _FENCE.match(line)
        if fence:
            in_fence = True
            fence_marker = fence.group(1)[0] * 3
            out.append(line)
            i += 1
            continue

        # A list item: gather the marker line and its continuation lines, then
        # reflow the combined text with a hanging indent. Without this, a
        # wrapped continuation line is treated as a separate paragraph and
        # de-dented away from its bullet.
        list_item = _LIST_ITEM.match(line)
        if list_item:
            indent, bullet, gap, first_text = list_item.groups()
            content_col = len(indent) + len(bullet) + len(gap)
            cont: list[str] = []
            i += 1
            while i < n:
                nxt = lines[i]
                if (not nxt.strip()
                        or _FENCE.match(nxt)
                        or _LIST.match(nxt)
                        or _HEADING.match(nxt)
                        or _HR.match(nxt)
                        or _BLOCKQUOTE.match(nxt)
                        or _TABLE.match(nxt)
                        or _HTML.match(nxt)):
                    break
                cont.append(nxt)
                i += 1

            block = [line, *cont]
            # Leave items with a hard line break, or with no text, untouched.
            if first_text.strip() and not any(b.endswith("  ") for b in block):
                joined = " ".join(s.strip() for s in [first_text, *cont] if s.strip())
                text_lines = _reflow_text(joined, max(20, width - content_col))
                if text_lines:
                    prefix = indent + bullet + gap
                    pad = " " * content_col
                    block = [prefix + text_lines[0]] + [pad + t for t in text_lines[1:]]
            if block != [line, *cont]:
                reflowed += 1
            out.extend(block)
            continue

        if not _is_prose_line(line):
            out.append(line)
            i += 1
            continue

        # Gather a prose paragraph: consecutive prose lines.
        para_lines = [line]
        i += 1
        while i < n and _is_prose_line(lines[i]) and not _FENCE.match(lines[i]):
            para_lines.append(lines[i])
            i += 1

        # A trailing double-space is a hard line break; leave such a paragraph
        # untouched rather than risk dropping the break.
        if any(pl.endswith("  ") for pl in para_lines):
            out.extend(para_lines)
            continue

        joined = " ".join(pl.strip() for pl in para_lines)
        new_lines = _reflow_text(joined, width) or para_lines
        if new_lines != para_lines:
            reflowed += 1
        out.extend(new_lines)

    result = "\n".join(out)
    if text.endswith("\n"):
        result += "\n"
    return result, reflowed


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def process(path: Path, write: bool, show_diff: bool, width: int) -> tuple[bool, int, bool]:
    """Returns (changed, paragraphs_reflowed, roundtrip_ok)."""
    original = path.read_text(encoding="utf-8")
    reflowed, count = reflow(original, width)
    roundtrip_ok = _normalize(original) == _normalize(reflowed)
    changed = reflowed != original

    if show_diff and changed:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            reflowed.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path) + " (reflowed)",
        )
        sys.stdout.writelines(diff)

    if write and changed and roundtrip_ok:
        path.write_text(reflowed, encoding="utf-8")

    return changed, count, roundtrip_ok


def _resolve(selector: str) -> list[Path]:
    """Resolve one selector to Markdown files.

    A selector may be a path to a file, or a chapter selector matched against
    `Markdown/`: a number or stem prefix ("02", "02_A_Python") or a substring
    ("Tour"). Matching is case-insensitive.
    """
    path = Path(selector)
    if path.is_file():
        return [path]
    md = Path("Markdown")
    matches = sorted(md.glob(f"{selector}*.md"))
    if not matches:
        low = selector.lower()
        matches = sorted(p for p in md.glob("*.md") if low in p.stem.lower())
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*",
                        help="files or chapter selectors like '02' or 'Tour' "
                             "(default: all of Markdown/)")
    parser.add_argument("--write", action="store_true", help="rewrite files in place")
    parser.add_argument("--diff", action="store_true", help="print a unified diff")
    parser.add_argument("--width", type=int, default=_DEFAULT_WIDTH,
                        help=f"clause-break sentences wider than this (default {_DEFAULT_WIDTH})")
    args = parser.parse_args()

    if args.paths:
        files = []
        for selector in args.paths:
            matched = _resolve(selector)
            if not matched:
                print(f"no Markdown file matches: {selector}")
                return 2
            files.extend(matched)
    else:
        files = sorted(Path("Markdown").glob("*.md"))

    total_changed = 0
    total_paras = 0
    failures: list[Path] = []
    for path in files:
        changed, count, ok = process(path, args.write, args.diff, args.width)
        if not ok:
            failures.append(path)
            print(f"SKIP (round-trip failed): {path}")
            continue
        if changed:
            total_changed += 1
            total_paras += count
            verb = "rewrote" if args.write else "would reflow"
            print(f"{verb}: {path.name} ({count} paragraph(s))")

    print(f"\n{total_changed} file(s), {total_paras} paragraph(s).")
    if failures:
        print(f"{len(failures)} file(s) skipped on round-trip failure.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
