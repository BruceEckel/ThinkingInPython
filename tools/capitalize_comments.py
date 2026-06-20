#!/usr/bin/env python3
"""Capitalize the first letter of prose comments in ```python blocks.

Walks every ``Markdown/*.md`` file, and within fenced ``python`` blocks only,
finds real ``#`` comments (string-aware, so ``#`` inside a literal is ignored).
A comment's first word is capitalized only when it looks like prose: a run of
two or more ASCII letters (or the lone article "a") that is NOT immediately
followed by a code character (``.([_=/\\:`` or a digit) and is not a known
code keyword. Path-marker slugs like ``# trace.py`` are left alone because the
``.`` disqualifies them. Mid-sentence continuation lines of a multi-line
comment are skipped so words are not capitalized mid-thought.

NOT a Makefile target by design: the prose-vs-code call is a heuristic, so a
run still needs a human to review the diff and revert false positives (literal
program output, schematic key->value notation, etc.). Use it as an assist, not
an automated gate.

Default is a dry run that prints proposed changes. Pass --write to apply.
After applying, regenerate the Examples/ mirror:
    python tools/extract_examples.py --write -o Examples
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_DIR = ROOT / "Markdown"

FENCE = re.compile(r"^```(\w+)?\s*$")
# Word = leading run of ASCII letters in the comment text.
WORD = re.compile(r"^[A-Za-z]+")
# A path-marker slug like "# trace.py" or "# mouse/Action.py".
PATH_MARKER = re.compile(r"^#\s*[\w./\\-]+\.\w+\s*$")
TERMINAL = {".", "!", "?", ":"}

# Tokens that are code references far more often than prose; leave untouched.
CODE_KEYWORDS = {
    "def", "class", "import", "from", "return", "self", "cls", "lambda",
    "elif", "else", "for", "while", "with", "try", "except", "finally",
    "yield", "async", "await", "global", "nonlocal", "assert", "del",
    "pass", "raise", "and", "or", "not", "in", "is", "if",
}


def is_full_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def ends_sentence(comment_text: str) -> bool:
    t = comment_text.rstrip().rstrip("\"')")
    return bool(t) and t[-1] in TERMINAL


def find_comment_hash(line: str, in_triple: str | None):
    """Return (hash_index or -1, triple_state_after_line)."""
    i, n = 0, len(line)
    quote = in_triple
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


def transform_comment(line: str, hash_i: int) -> str | None:
    """Return a new line with the comment's first prose word capitalized, or None."""
    prefix = line[:hash_i]            # code before the comment (or indentation)
    after = line[hash_i + 1:]         # text after '#'
    stripped = after.lstrip(" ")
    pad = after[: len(after) - len(stripped)]
    if not stripped:
        return None
    m = WORD.match(stripped)
    if not m:
        return None
    word = m.group(0)
    # Single letters are usually variable names; "a" is the lone prose article.
    if len(word) < 2 and word != "a":
        return None
    if not word[0].islower():
        return None
    if word.lower() in CODE_KEYWORDS:
        return None
    nxt = stripped[len(word): len(word) + 1]
    if nxt in {".", "(", "[", "_", "=", "/", "\\", ":", "'"} or nxt.isdigit():
        return None
    new_after = pad + word[0].upper() + stripped[1:]
    return prefix + "#" + new_after


def process_file(path: Path, write: bool) -> list[tuple[int, str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=False)
    changes: list[tuple[int, str, str]] = []
    in_python = False
    triple: str | None = None
    # True when the previous line was a full-line comment that left a sentence
    # open, so the current full-line comment is a mid-sentence continuation.
    prev_comment_open = False
    out = []
    for idx, line in enumerate(lines, 1):
        if FENCE.match(line):
            lang = FENCE.match(line).group(1) or ""
            in_python = (lang == "python") if not in_python else False
            triple = None
            prev_comment_open = False
            out.append(line)
            continue
        if in_python:
            hash_i, triple = find_comment_hash(line, triple)
            if hash_i != -1 and triple is None:
                full = is_full_comment(line)
                continuation = full and prev_comment_open
                if not continuation:
                    new = transform_comment(line, hash_i)
                    if new and new != line:
                        changes.append((idx, line, new))
                        line = new
                if full:
                    text = line.lstrip()[1:]
                    prev_comment_open = not (
                        PATH_MARKER.match(line.lstrip()) or ends_sentence(text)
                    )
                else:
                    prev_comment_open = False
                out.append(line)
                continue
            prev_comment_open = False
        else:
            prev_comment_open = False
        out.append(line)
    if write and changes:
        text = "\n".join(out)
        if path.read_text(encoding="utf-8").endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8", newline="\n")
    return changes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply changes")
    args = ap.parse_args(argv)

    total = 0
    for md in sorted(MARKDOWN_DIR.glob("*.md")):
        changes = process_file(md, args.write)
        if changes:
            print(f"\n{md.name}: {len(changes)} change(s)")
            for ln, old, new in changes:
                print(f"  {ln}: {old.strip()}")
                print(f"      -> {new.strip()}")
            total += len(changes)
    print(f"\n{'Applied' if args.write else 'Proposed'} {total} change(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
