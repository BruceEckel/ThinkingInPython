#!/usr/bin/env python3
"""Copy each exercise statement into its Solutions heading as a block quote.

`Solutions/NN_*.md` answers the exercises `Chapters/NN_*.md` sets, under
headings `## N. <short title>`. A solution with no exercise above it
sends the reader back to the chapter, and a solution that answers the
wrong exercise under the right number is hard to see.
`check_solutions.py` compares the numbers alone.

This tool puts the statement where the answer is. The chapter stays the
single source of truth; the copy is generated, and each run rewrites it:

    ## 3. A pool of connections

    > Write a pool that hands out at most three connections.
    > Return a connection to the pool when its block exits.

    (the section's own text follows, unchanged)

Finding a statement. Exercises are the top-level ordered-list items under
the chapter's last `## Exercises` heading, the same rule as
`check_solutions.exercise_numbers()`. A statement is its item line plus
every following line that is blank or starts with whitespace. It ends at
the next top-level item, at a heading, at a non-blank line in column 0
(chapters 11, 17, and 19 follow their last exercise with `[^label]:`
footnote definitions, which are not part of it), or at the end of the
file. Trailing blank lines are dropped. A statement can hold a blank line
and a nested list; the copy keeps that structure.

Rendering. For a heading that answers one exercise, each statement line
is dedented by the item's text column (the column is read from the item
line, since `1.  text` and `10. text` both put the text at column 4) and
prefixed with `> `. A blank line inside the statement becomes a bare `>`.
For a combined heading (`## 1 & 2.`, `## 1, 2.`, `## 1-3.`) every
statement the heading names goes into one block quote, each kept as the
ordered-list item the chapter writes (marker and indentation intact),
with a bare `>` line between items.

Two edits happen inside the copy, and no others:

- Links. `Solutions/` sits beside `Chapters/`, so a chapter-relative link
  needs a prefix. `](#anchor)` becomes `](../Chapters/<this chapter>#anchor)`
  and a bare book-file link, `](17_Techniques--Metaprogramming.md#x)` or
  `](A_Effect_Tracking.md)`, becomes `](../Chapters/17_...md#x)`. The
  rewrite matches the target's form, so a code span such as
  `last[T](items: list[T])` stays as written. `http` links and any target
  holding a `/` are left alone.
- Footnote references `[^label]` are removed, because a definition cannot
  follow the statement into `Solutions/`.

Which block the tool owns. The block quote that starts at the first
non-blank line after a numbered `## N.` heading (one matching
`check_solutions.ANSWER`) is the generated one, and a run replaces it in
full. If that line is not a `>` line, the run inserts a block there.
Headings that do not match `ANSWER` (`## Shared code: the bakery`) get
nothing, and neither does a heading whose number names no exercise. Fenced
code is ignored, so a `>` line or a heading inside a listing is never
touched. Every other line of the file stays byte for byte as it was,
including line endings and the final newline.

`generated_lines()` returns the line numbers of the generated blocks in a
Solutions document. `exercise_refs.py` skips them, since each statement
repeats the chapter's own references to other exercises and would double
every one in the baseline.

Usage:
    python -m tools.exercise_statements              # report drift
    python -m tools.exercise_statements --write      # rewrite Solutions/
    python -m tools.exercise_statements --write 25   # only chapter 25
"""

import argparse
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from tools.check_solutions import (
    ANSWER,
    EXERCISES_HEADING,
    HEADING,
    ITEM,
    SOLUTIONS_DIR,
    expand,
    selected,
)
from tools.markdown import Document
from tools.report import Finding, report

# A level-2 heading, the form a solution's heading takes.
SECTION = re.compile(r"^##\s+(.*?)\s*$")

# `](#anchor)`: a link into the chapter's own headings.
ANCHOR_LINK = re.compile(r"\]\(#")

# `](24_Patterns--Singleton.md#state)` or `](A_Effect_Tracking.md)`: a link
# to a book file with no directory in front. Requiring `.md` right after
# the name, and `)` right after the optional anchor, leaves code spans
# such as `last[T](items: list[T])` alone.
BOOK_LINK = re.compile(r"\]\(([\w-]+\.md)((?:#[^)\s]*)?)\)")

# `[^label]`, a footnote reference.
FOOTNOTE_REF = re.compile(r"\[\^[^\]\s]+\]")


@dataclass(frozen=True)
class Statement:
    """One exercise as the chapter writes it."""

    number: int
    column: int
    """Column at which the item's text starts, after the marker."""
    lines: tuple[str, ...]
    """The item line and its continuation lines, trailing blanks dropped."""


@dataclass(frozen=True)
class Section:
    """A numbered solution heading and the block quote under it."""

    heading: int
    """0-based index of the heading line."""
    numbers: tuple[int, ...]
    start: int
    """0-based index of the first non-blank line after the heading."""
    end: int
    """One past the last line of the `>` block; `start` when there is none."""


def clean(line: str) -> str:
    """`line` without a trailing carriage return."""
    return line.removesuffix("\r")


def statements(doc: Document) -> dict[int, Statement]:
    """The exercise statements under the document's last Exercises heading."""
    fenced = doc.in_fence()
    lines = [clean(line) for line in doc.lines]
    opened = [
        i for i, line in enumerate(lines)
        if not fenced[i] and EXERCISES_HEADING.match(line)
    ]
    if not opened:
        return {}
    found: dict[int, Statement] = {}
    current: tuple[int, int, list[str]] | None = None

    def close() -> None:
        if current is None:
            return
        number, column, body = current
        while body and not body[-1].strip():
            body.pop()
        found[number] = Statement(number, column, tuple(body))

    for i in range(opened[-1] + 1, len(lines)):
        line = lines[i]
        if not fenced[i] and HEADING.match(line):
            break
        item = ITEM.match(line)
        if item and not fenced[i]:
            close()
            current = (int(item.group(1)), item.end() - 1, [line])
        elif current is not None:
            if line.strip() and not line[0].isspace():
                break
            current[2].append(line)
    close()
    return found


def rewrite_links(text: str, chapter: str) -> str:
    """`text` with chapter-relative links made valid from Solutions/."""
    text = ANCHOR_LINK.sub(f"](../Chapters/{chapter}#", text)
    text = BOOK_LINK.sub(r"](../Chapters/\1\2)", text)
    return FOOTNOTE_REF.sub("", text)


def dedent(line: str, column: int) -> str:
    """`line` less up to `column` leading spaces; a blank line is empty."""
    if not line.strip():
        return ""
    lead = len(line) - len(line.lstrip(" "))
    return line[min(lead, column):]


def quote(line: str) -> str:
    """`line` as a block quote line; a blank line is a bare `>`."""
    return f"> {line}" if line else ">"


def render(chosen: list[Statement], chapter: str) -> list[str]:
    """The block quote lines (no line endings) for one heading."""
    single = len(chosen) == 1
    lines: list[str] = []
    for statement in chosen:
        if lines:
            lines.append("")
        if single:
            body = [dedent(line, statement.column)
                    for line in statement.lines]
            body[0] = statement.lines[0][statement.column:]
        else:
            body = [line if line.strip() else ""
                    for line in statement.lines]
        lines.extend(body)
    return [quote(rewrite_links(line, chapter)) for line in lines]


def sections(doc: Document) -> Iterator[Section]:
    """Every numbered `## N.` heading, with the block quote it owns."""
    lines = doc.lines
    for lineno, text in doc.headings():
        index = lineno - 1
        if not SECTION.match(lines[index]):
            continue
        answer = ANSWER.match(text)
        if not answer:
            continue
        start = index + 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        end = start
        while end < len(lines) and lines[end].startswith(">"):
            end += 1
        yield Section(index, tuple(expand(answer.group(1))), start, end)


def generated_lines(doc: Document) -> set[int]:
    """1-based line numbers of the generated blocks in a Solutions file."""
    owned: set[int] = set()
    for section in sections(doc):
        owned.update(range(section.start + 1, section.end + 1))
    return owned


def apply(
    doc: Document, chapter: Document, name: str,
) -> tuple[list[str], list[tuple[int, bool]]]:
    """(new lines, [(heading line, was inserted)] for each changed section)."""
    available = statements(chapter)
    cr = "\r" if doc.lines and doc.lines[0].endswith("\r") else ""
    lines = list(doc.lines)
    changed: list[tuple[int, bool]] = []
    for section in reversed(list(sections(doc))):
        chosen = [available[n] for n in section.numbers if n in available]
        if not chosen:
            continue
        block = [line + cr for line in render(chosen, name)]
        existing = section.end > section.start
        after = lines[section.end] if section.end < len(lines) else None
        tail = [""] if after is not None and after.strip() else []
        if existing:
            if lines[section.start:section.end] == block and not tail:
                continue
            lines[section.start:section.end] = block + [x + cr for x in tail]
        else:
            lead = [cr] if section.start == section.heading + 1 else []
            lines[section.start:section.start] = (
                lead + block + [cr] if after is not None
                else lead + block)
        changed.append((section.heading + 1, not existing))
    changed.reverse()
    return lines, changed


def process(chapter: Path, write: bool) -> tuple[list[Finding], int, int]:
    """(drift findings, statements inserted, statements replaced)."""
    solutions = SOLUTIONS_DIR / chapter.name
    if not solutions.exists():
        return [], 0, 0
    source = Document.parse(chapter)
    raw = solutions.read_bytes().decode("utf-8")
    doc = Document.from_text(raw, solutions)
    lines, changed = apply(doc, source, chapter.name)
    if not changed:
        return [], 0, 0
    findings = [
        Finding(solutions, line,
                "exercise statement is " + ("missing" if new
                                            else "out of date")
                + "; run `tip statements`")
        for line, new in changed
    ]
    if write:
        solutions.write_bytes("\n".join(lines).encode("utf-8"))
    inserted = sum(1 for _, new in changed if new)
    return findings, inserted, len(changed) - inserted


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapters", nargs="*",
                    help="chapter numbers to process (default: all)")
    ap.add_argument("--write", action="store_true",
                    help="rewrite Solutions/ instead of reporting drift")
    args = ap.parse_args(argv)

    findings: list[Finding] = []
    files = inserted = replaced = 0
    for chapter in selected(args.chapters):
        found, new, old = process(chapter, args.write)
        findings.extend(found)
        files += bool(found)
        inserted += new
        replaced += old
        if args.write and found:
            print(f"Solutions/{chapter.name}: {new} inserted, "
                  f"{old} replaced")
    if args.write:
        print(f"{files} file(s) changed: {inserted} statement(s) "
              f"inserted, {replaced} replaced.")
        return 0
    return report(
        findings,
        clean="Every solution carries its exercise statement.",
        problem="{n} statement(s) in Solutions/ differ from their "
                "chapter. Run `tip statements` to rewrite them.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
