#!/usr/bin/env python
"""Check the numbered tags that let prose point at a line.

A listing can mark a line with a numbered tag: a trailing
comment `# [1]`, `# [2]`, and so on. The prose below the
listing then cites that line by writing the tag as a code
span, `[1]`. A line too long to carry its tag within the
60-column limit gets an own-line tag instead: the same
comment alone on its own line, marking the line below it.
Any fenced block can carry tags, a ```text block as well as
a ```python one.

A listing's citations sit in its prose region: the lines
after its closing fence, up to the next fenced block or the
next heading, whichever comes first. This check enforces
four rules:

1. A block's tags run 1, 2, ..., n in order, with no gaps
   and no repeats.
2. The block's prose region cites every one of its tags at
   least once.
3. Every `[n]` code span in prose names a tag in the block
   whose region holds it. A citation in a region with no
   block above it, such as one under a heading before any
   listing, is a finding.
4. A bare [n] in prose, outside a code span and followed by
   neither `(` nor `:`, is a finding. The EPUB and PDF
   concatenate every chapter into one document, where a
   single stray `[n]:` reference definition turns every
   bare [n] in the book into a link, so a citation is
   always a code span.

A citation is a code span whose whole content is `[n]`,
with n from 1 up, since tags start at 1. A footnote marker
`[^1]`, a longer span such as `x[1]`, and the list literal
`[0]` cite no tag. An untagged block whose region cites
nothing draws no finding, so the check costs the untagged
chapters nothing.

Usage:
    python -m tools.listing_tags         # all of Chapters/
    python -m tools.listing_tags Chapters Solutions
"""

import argparse
import re
from collections.abc import Iterator
from tools.markdown import Block, Document
from tools.repo import add_paths_arg, md_files
from tools.report import Check, Finding, report

# A tag closing a code line, or an own-line tag alone on its
# line. Either way the comment ends the line.
TAG = re.compile(r"(?:^|\s)# \[(\d+)\]\s*$")

# An inline code span: a run of backticks, its content, and
# a closing run of the same length.
SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")

# A code span's whole content when it cites a tag.
CITATION = re.compile(r"\[([1-9]\d*)\]")

# A bracketed number in prose. A following `(` makes it a
# link and a following `:` makes it a reference definition,
# so neither counts as bare.
BARE = re.compile(r"\[(\d+)\](?![(:])")

WHY = ("the EPUB and PDF concatenate the chapters, where "
       "one stray reference definition would turn it into "
       "a link")


def tags(block: Block) -> Iterator[tuple[int, int]]:
    """(line, number) for each tag in `block`, in order."""
    for index, line in enumerate(block.lines):
        m = TAG.search(line)
        if m:
            yield block.line_number(index), int(m.group(1))


def order_findings(doc: Document,
                   found: list[tuple[int, int]]
                   ) -> Iterator[Finding]:
    """Findings for tags that break the 1, 2, ..., n run."""
    seen: set[int] = set()
    expected = 1
    for lineno, n in found:
        if n in seen:
            yield Finding(
                doc.path, lineno,
                f"tag [{n}] repeats; a listing numbers its "
                "tags 1, 2, 3, ... with each number once")
        elif n != expected:
            yield Finding(
                doc.path, lineno,
                f"tag [{n}] where [{expected}] comes next; "
                "a listing numbers its tags 1, 2, 3, ... "
                "in order")
        seen.add(n)
        expected = max(expected, n + 1)


def line_findings(doc: Document, lineno: int, line: str,
                  owner: Block | None, numbers: set[int],
                  cited: set[int]) -> Iterator[Finding]:
    """Citation and bare-tag findings for one prose line.

    `owner` is the block whose region holds the line,
    `numbers` holds its tags, and `cited` collects the
    numbers this line cites.
    """
    masked = list(line)
    for span in SPAN.finditer(line):
        start, end = span.span()
        masked[start:end] = " " * (end - start)
        ref = CITATION.fullmatch(span.group(2))
        if ref is None:
            continue
        n = int(ref.group(1))
        if owner is None:
            yield Finding(
                doc.path, lineno,
                f"`[{n}]` has no listing above it in its "
                "region; a citation follows the tagged "
                "listing it names, before the next heading",
                col=start + 1)
        elif n not in numbers:
            yield Finding(
                doc.path, lineno,
                f"`[{n}]` names no tag in the listing "
                "above it (opening at line "
                f"{owner.open_at + 1})",
                col=start + 1)
        else:
            cited.add(n)
    for bare in BARE.finditer("".join(masked)):
        n = bare.group(1)
        yield Finding(
            doc.path, lineno,
            f"bare [{n}]: write it as the code span "
            f"`[{n}]`, since {WHY}",
            col=bare.start() + 1)


def find(doc: Document) -> Iterator[Finding]:
    """Every tag and citation finding in `doc`, in order."""
    found: list[Finding] = []
    by_end = {block.end: block for block in doc.blocks}
    numbers: dict[int, set[int]] = {}
    cited: dict[int, set[int]] = {}
    for block in doc.blocks:
        block_tags = list(tags(block))
        numbers[block.open_at] = {n for _, n in block_tags}
        cited[block.open_at] = set()
        found.extend(order_findings(doc, block_tags))
    fenced = doc.in_fence()
    owner: Block | None = None
    for index, line in enumerate(doc.lines):
        if index in by_end:
            owner = by_end[index]
            continue
        if fenced[index]:
            continue
        if line.startswith("#"):
            owner = None
        key = -1 if owner is None else owner.open_at
        found.extend(line_findings(
            doc, index + 1, line, owner,
            numbers.get(key, set()),
            cited.setdefault(key, set())))
    for block in doc.blocks:
        for lineno, n in tags(block):
            if n not in cited[block.open_at]:
                found.append(Finding(
                    doc.path, lineno,
                    f"tag [{n}] is never cited; the prose "
                    f"after the listing names it as "
                    f"`[{n}]`, before the next listing or "
                    "heading"))
    found.sort(key=lambda f: (f.line, f.col or 0))
    yield from found


CHECK = Check(
    name="listing-tags",
    doc="listing tags # [n] run 1..n and are cited as "
        "`[n]` in the prose below; no bare [n] in prose",
    run=find,
    clean="Listing tags and their citations agree.",
    problem="{n} listing tag problem(s). Renumber the "
            "tags, cite each one below its listing, and "
            "write every citation as a code span.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_paths_arg(ap)
    args = ap.parse_args(argv)
    findings = [
        f for p in md_files(args.paths)
        for f in find(Document.parse(p))
    ]
    return report(findings, clean=CHECK.clean,
                  problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
