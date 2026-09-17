#!/usr/bin/env python3
"""List the comments in book listings that are new since a git ref.

A comment in a listing earns its place by saying something the code does
not. The failure mode is the comment that restates the line it sits on:

    class Contact:  # A Contact has a Name and an Address

Nothing mechanical can tell that comment from a useful one, so this tool
judges nothing. It narrows the reading instead: after an editing session
you want the comments you just wrote, not the nine hundred already in the
book. Run it, read the list, and delete what restates its own line.

It is report-only: it gates nothing, fixes nothing, and exits nonzero
only on a usage error (an unknown ref, a path that is not there).

    python -m tools.comment_report                  # new since HEAD
    python -m tools.comment_report --since HEAD~5   # new since five commits back
    python -m tools.comment_report --since v0.5.9 Chapters/20_Patterns--Rethinking_Objects.md
    python -m tools.comment_report --all            # every comment, no git

What counts as a comment
------------------------
Each ```python block is tokenized as a whole with the `tokenize` module,
and only COMMENT tokens count. That matters because a `#` inside a
string is not a comment: chapter 38 draws a maze out of `#` characters
inside a triple-quoted string, and chapter 35 does something similar, so
a line-by-line scan reports about forty-five wall segments as comments.

Three kinds of comment are skipped, none of them prose you would edit:
the block's own `# slug.py` file marker on its first line, a `#:` output
marker, and a tool directive (`# type: ignore`, `# noqa`, `# ty:`,
`# pyright:`, `# pragma`, `# fmt:`).

What counts as new
------------------
Comparison is per listing within one Markdown file. Each comment is keyed
by the listing it sits in (the slug from the block's `# name.py` first
line, or `<fragment N>` for the Nth unmarked block in that file) and its
own text, and the two versions of the file are counted as multisets of
those keys. A key whose count went up is new, and the *last* occurrences
of that key are the ones reported.

So editing a comment's wording reports it as new, which is what you
want: the reworded comment has not been read yet. Moving a comment
within its listing is not new, and neither is moving a whole listing
within its chapter, since no line number enters the key.

Limits
------
The multiset comparison is per file, so moving a listing from one chapter
to another reports every comment in it as new in the receiving file. The
`<fragment N>` numbering counts unmarked blocks in file order, so
inserting a fragment renumbers the fragments after it and their comments
read as new. A block that does not tokenize as a whole (a fragment
starting mid-indentation, an intentionally broken listing) is retokenized
one line at a time, and a line that still fails is dropped, so a comment
on such a line goes unreported.
"""

import argparse
import io
import re
import subprocess
import sys
import tokenize
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.config import CHAPTERS_DIR, PATH_LINE_RE, ROOT
from tools.markdown import Block, Document
from tools.repo import md_files

SOLUTIONS_DIR = ROOT / "Solutions"

# Comments that are instructions to a tool rather than prose to a reader.
DIRECTIVE = re.compile(r"^#\s*(type:|ty:|noqa|pyright:|pragma|fmt:)")

GIT_TIMEOUT = 60


@dataclass(frozen=True)
class CommentRecord:
    """One comment in one listing, located in the Markdown file."""

    listing: str
    """The block's slug ("composition.py") or "<fragment N>"."""

    line: int
    """1-based line number in the Markdown file, for jumping to it."""

    comment: str
    """The comment token's own text, starting with "#"."""

    source: str
    """The whole source line the comment sits on, stripped."""

    @property
    def key(self) -> tuple[str, str]:
        """What makes two comments the same one: listing and text."""
        return self.listing, self.comment


def _comment_tokens(source: str) -> list[tuple[int, str]]:
    """(0-based line index, comment text) for each COMMENT token.

    Raises whatever `tokenize` raises on source it cannot read, which
    `block_comments` below turns into its line-by-line fallback.
    """
    reader = io.StringIO(source).readline
    return [
        (token.start[0] - 1, token.string)
        for token in tokenize.generate_tokens(reader)
        if token.type == tokenize.COMMENT
    ]


def block_comments(lines: Sequence[str]) -> list[tuple[int, str]]:
    """(0-based line index, comment text) for a listing's lines.

    The whole block is tokenized first, so a `#` inside a string is not
    a comment. Many blocks are illustrative fragments that no tokenizer
    can read as a unit, and those fall back to tokenizing one line at a
    time; a line that fails on its own is skipped.
    """
    source = "".join(f"{line}\n" for line in lines)
    try:
        return _comment_tokens(source)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    found: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        try:
            found.extend((index, text) for _, text in
                         _comment_tokens(f"{line}\n"))
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue
    return found


def _first_content_index(lines: Sequence[str]) -> int:
    """0-based index of the first non-blank line, or -1 if all blank."""
    for index, line in enumerate(lines):
        if line.strip():
            return index
    return -1


def _skipped(comment: str, *, is_slug_line: bool) -> bool:
    """Whether this comment is a marker or a directive, not prose.

    The `# name.py` test applies to the block's first content line
    alone, so a comment elsewhere that happens to name a file is kept.
    """
    if comment.startswith("#:") or DIRECTIVE.match(comment):
        return True
    return is_slug_line and PATH_LINE_RE.match(comment.strip()) is not None


def listing_comments(block: Block, listing: str) -> Iterator[CommentRecord]:
    """Every reportable comment in one block, in file order."""
    slug_line = _first_content_index(block.lines)
    for index, comment in block_comments(block.lines):
        if _skipped(comment, is_slug_line=index == slug_line):
            continue
        yield CommentRecord(
            listing=listing,
            line=block.line_number(index),
            comment=comment.strip(),
            source=block.lines[index].strip(),
        )


def comments_in(text: str) -> list[CommentRecord]:
    """Every reportable comment in a Markdown file's ```python blocks.

    Takes the file's text rather than its path, so both versions of a
    file compare through one function and a test needs no filesystem.
    """
    records: list[CommentRecord] = []
    fragments = 0
    for block in Document.from_text(text).python_blocks():
        slug = block.slug
        if slug is None:
            fragments += 1
            listing = f"<fragment {fragments}>"
        else:
            listing = slug
        records.extend(listing_comments(block, listing))
    return records


def added(old: Iterable[CommentRecord],
          new: Iterable[CommentRecord]) -> list[CommentRecord]:
    """The records in `new` whose key appears more often than in `old`.

    Where a key gained occurrences, the last ones are the ones reported.
    Any consistent choice would do, and the last reads better: a comment
    appended to a listing is more often the new one than the comment
    already at the top.
    """
    new_records = list(new)
    before = Counter(record.key for record in old)
    after = Counter(record.key for record in new_records)
    seen: Counter[tuple[str, str]] = Counter()
    picked: list[CommentRecord] = []
    for record in reversed(new_records):
        seen[record.key] += 1
        if seen[record.key] <= after[record.key] - before[record.key]:
            picked.append(record)
    picked.reverse()
    return picked


def display_path(path: Path) -> str:
    """The path as the report prints it, and as git names it.

    Relative to the repo root with forward slashes, so an editor can
    jump to `path:line` and `git show REF:path` finds the same file.
    """
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _git(*args: str) -> tuple[str, int]:
    """One git command's (stdout, exit code), run at the repo root."""
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT,
    )
    return proc.stdout, proc.returncode


def ref_exists(ref: str) -> bool:
    _, code = _git("rev-parse", "--verify", f"{ref}^{{commit}}")
    return code == 0


def changed_since(ref: str, paths: Sequence[Path]) -> set[str]:
    """The display paths that differ from `ref`, plus untracked ones.

    A file git does not track has no version at `ref` to compare with,
    so it counts as changed and every comment in it is new.
    """
    names = [display_path(p) for p in paths]
    tracked, _ = _git("diff", "--name-only", ref, "--", *names)
    untracked, _ = _git(
        "ls-files", "--others", "--exclude-standard", "--", *names)
    listed = set(tracked.splitlines()) | set(untracked.splitlines())
    return {name for name in names if name in listed}


def text_at(ref: str, name: str) -> str:
    """A file's text at `ref`, or "" when it does not exist there."""
    out, code = _git("show", f"{ref}:{name}")
    return out if code == 0 else ""


def collect(paths: Sequence[Path], *, ref: str | None,
            ) -> list[tuple[Path, list[CommentRecord]]]:
    """Per file, the comments to report, in file order.

    With `ref` None, that is every comment in the file. Otherwise it is
    the comments new since `ref`, and a file git reports unchanged is
    never read.
    """
    changed = changed_since(ref, paths) if ref is not None else set()
    out: list[tuple[Path, list[CommentRecord]]] = []
    for path in paths:
        name = display_path(path)
        if ref is not None and name not in changed:
            out.append((path, []))
            continue
        now = comments_in(path.read_text(encoding="utf-8"))
        out.append((path, now if ref is None
                    else added(comments_in(text_at(ref, name)), now)))
    return out


def format_lines(path: Path,
                 records: Iterable[CommentRecord]) -> Iterator[str]:
    """`path:line: [listing] source` for each record, in file order."""
    name = display_path(path)
    for record in records:
        yield f"{name}:{record.line}: [{record.listing}] {record.source}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files (default: Chapters/ and Solutions/)")
    ap.add_argument("--since", default="HEAD", metavar="REF",
                    help="compare the working tree against this git ref "
                         "(default: HEAD)")
    ap.add_argument("--all", action="store_true",
                    help="ignore git and list every comment")
    args = ap.parse_args(argv)

    files = md_files(args.paths or [CHAPTERS_DIR, SOLUTIONS_DIR])
    missing = [p for p in files if not p.is_file()]
    if missing:
        print("error: no such file: "
              + ", ".join(display_path(p) for p in missing), file=sys.stderr)
        return 2
    if not args.all and not ref_exists(args.since):
        print(f"error: {args.since} is not a git ref this repository "
              "knows. Name a commit, tag, or branch.", file=sys.stderr)
        return 2

    total = 0
    counted = 0
    for path, records in collect(files, ref=None if args.all else args.since):
        if not records:
            continue
        counted += 1
        for line in format_lines(path, records):
            print(line)
        total += len(records)

    if not total:
        print("No comments in listings." if args.all else
              f"No new comments in listings since {args.since}.")
    elif args.all:
        print(f"\n{total} comment(s) in {counted} file(s).")
    else:
        print(f"\n{total} new comment(s) in {counted} file(s) "
              f"since {args.since}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
