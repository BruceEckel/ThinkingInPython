#!/usr/bin/env python3
"""Capitalize the first letter of prose comments in ```python blocks.

Walks every ``Chapters/*.md`` file, and within fenced ``python`` blocks only,
finds real ``#`` comments (string-aware, so ``#`` inside a literal is ignored).
A comment's first word is capitalized only when it looks like prose: a run of
two or more ASCII letters (or the lone article "a") that is NOT immediately
followed by a code character (``.([_=/\\:`` or a digit) and is not a known
code keyword. Path-marker slugs like ``# trace.py`` are left alone because the
``.`` disqualifies them. Mid-sentence continuation lines of a multi-line
comment are skipped so words are not capitalized mid-thought.

The prose-vs-code call is a heuristic, so it has false positives: literal
program output (`# total = 7`), an identifier reference (`# n is the counter`),
schematic notation (`# name -> subclass`). Those are listed by their comment
text in tools/data/comment_caps_allow.txt and skipped. Add a line there when the
checker is wrong; capitalize the comment when it is right.

Default is a check that lists comments needing capitalization and exits non-zero
(it is part of the `make ci` gate). Pass --write to apply the changes. After
applying, regenerate the Examples/ mirror:
    python tools/extract_examples.py --write -o Examples
"""

import argparse
import re
from collections.abc import Iterator
from functools import cache
from pathlib import Path

from tools_config import DATA_DIR
from tools_config import FENCE_RE as FENCE
from tools_markdown import Document
from tools_pycode import scan_line as find_comment_hash
from tools_repo import md_files, write_text_lf
from tools_report import Check, Finding, report

ALLOWLIST = DATA_DIR / "comment_caps_allow.txt"

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


def load_allowlist(path: Path) -> set[str]:
    """Comment texts (the part after `#`, stripped) to leave lowercase."""
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            out.add(stripped)
    return out


def is_full_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def ends_sentence(comment_text: str) -> bool:
    t = comment_text.rstrip().rstrip("\"')")
    return bool(t) and t[-1] in TERMINAL


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


def find_changes(
    lines: list[str], allow: set[str],
) -> tuple[list[tuple[int, str, str]], list[str]]:
    """(changes, rewritten lines) for one file's lines.

    Pure, so both the reporting path and the rewriting path derive from
    one walk. That walk threads triple-quote state and a "the previous
    comment left a sentence open" flag across the whole file, which is
    why this is line-based rather than built on `doc.python_blocks()`:
    both would have to be re-derived at every block boundary.
    """
    changes: list[tuple[int, str, str]] = []
    in_python = False
    triple: str | None = None
    # True when the previous line was a full-line comment that left a sentence
    # open, so the current full-line comment is a mid-sentence continuation.
    prev_comment_open = False
    out = []
    for idx, line in enumerate(lines, 1):
        fence = FENCE.match(line)
        if fence:
            lang = fence.group(1) or ""
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
                allowed = line[hash_i + 1:].strip() in allow
                if not continuation and not allowed:
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
    return changes, out


def process_file(path: Path, write: bool,
                 allow: set[str]) -> list[tuple[int, str, str]]:
    """Report (and optionally apply) one file's capitalization changes."""
    original = path.read_text(encoding="utf-8")
    changes, out = find_changes(original.splitlines(keepends=False), allow)
    if write and changes:
        text = "\n".join(out)
        if original.endswith("\n"):
            text += "\n"
        write_text_lf(path, text)
    return changes


@cache
def default_allowlist() -> frozenset[str]:
    """The configured allowlist, read once per process."""
    return frozenset(load_allowlist(ALLOWLIST))


def find(doc: Document) -> Iterator[Finding]:
    """Comments needing capitalization, one Finding each.

    Reads `doc.lines` rather than reopening `doc.path`, so the check is a
    function of the document it is handed and works on one built in
    memory. The message carries the replacement, so the one-line report
    says as much as this tool's own grouped diff does.
    """
    changes, _ = find_changes(doc.lines, set(default_allowlist()))
    for lineno, old, new in changes:
        yield Finding(
            doc.path, lineno,
            f"comment needs capitalizing: {old.strip()} -> {new.strip()}",
        )


def fixed(doc: Document) -> str | None:
    """The file with those comments capitalized, or None if none need it."""
    changes, out = find_changes(doc.lines, set(default_allowlist()))
    return doc.rendered(out) if changes else None


CHECK = Check(
    name="comment-caps",
    doc="prose comments in listings start with a capital",
    run=find,
    clean="Comment capitalization OK.",
    problem="{n} comment(s) need capitalizing. Capitalize them, "
            "or add the text to tools/data/comment_caps_allow.txt.",
    fixer=fixed,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply changes")
    ap.add_argument("--allow", type=Path, default=ALLOWLIST,
                    help=f"comment texts to skip (default: {ALLOWLIST.name})")
    args = ap.parse_args(argv)

    allow = load_allowlist(args.allow)
    total = 0
    for md in md_files():
        changes = process_file(md, args.write, allow)
        if changes:
            print(f"\n{md.name}: {len(changes)} change(s)")
            for ln, old, new in changes:
                print(f"  {ln}: {old.strip()}")
                print(f"      -> {new.strip()}")
            total += len(changes)

    if args.write:
        print(f"\nApplied {total} change(s).")
        return 0
    if total:
        print(f"\n{CHECK.problem.format(n=total)}")
        return 1
    print(f"\n{CHECK.clean}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
