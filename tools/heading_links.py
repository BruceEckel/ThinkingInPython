#!/usr/bin/env python
"""Verify that every Markdown heading-anchor link resolves to a real heading.

Markdown can link to a heading, not only a whole file:

    [text](#anchor)                       a heading in the same file
    [text](07_Static_Typing.md#anchor)    a heading in another chapter

The site is built with pandoc, which derives a heading's anchor from its text:
strip formatting and backticks, drop punctuation, lowercase, turn spaces into
hyphens, and remove everything up to the first letter. A heading may instead set
an explicit id with a trailing `{#id}`. This tool reproduces that rule, collects
every heading id, and checks that each `#anchor` link points at one.

A broken anchor renders as a dead in-page link with no other warning, so this is
a gate. It reports `path:line` and exits non-zero. There is nothing to auto-fix:
correct the anchor, or give the target heading an explicit `{#id}`.
"""
import argparse
import re
from collections.abc import Iterator
from functools import cache
from pathlib import Path

from tools_markdown import Document
from tools_repo import add_paths_arg, md_files
from tools_report import Check, Finding, report

EXPLICIT_ID = re.compile(r"\{#([\w-]+)[^}]*\}\s*$")
ATTR_BLOCK = re.compile(r"\s*\{[^}]*\}\s*$")
INLINE_CODE = re.compile(r"`[^`]*`")
INLINE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_TAG = re.compile(r"<[^>]+>")
LINK = re.compile(r"\]\(([^)]+)\)")
ANCHOR_TARGET = re.compile(r"^(?:([\w./-]+)\.md)?#([\w-]+)$")


def pandoc_anchor(text: str) -> str:
    """Reproduce pandoc's auto identifier for a heading's visible text."""
    text = INLINE_CODE.sub(lambda m: m.group(0).strip("`"), text)
    text = INLINE_LINK.sub(r"\1", text)  # [text](url) -> text
    text = HTML_TAG.sub("", text)  # raw <a href=...>text</a> -> text
    return _slug(text)


def _slug(text: str) -> str:
    # Keep letters, digits, underscores, hyphens, periods, and spaces.
    kept = "".join(c for c in text if c.isalnum() or c in " _-.")
    kept = re.sub(r"\s+", "-", kept).lower()
    m = re.search(r"[a-z]", kept)  # identifiers start at the first letter
    return kept[m.start():] if m else ""


def heading_anchors(doc: Document) -> set[str]:
    """Every anchor pandoc would assign to this document's headings."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for _, text in doc.headings():
        explicit = EXPLICIT_ID.search(text)
        if explicit:
            anchors.add(explicit.group(1))
            continue
        base = pandoc_anchor(ATTR_BLOCK.sub("", text))
        if not base:
            continue
        n = counts.get(base, 0)
        anchors.add(base if n == 0 else f"{base}-{n}")
        counts[base] = n + 1
    return anchors


def anchor_links(doc: Document) -> Iterator[tuple[int, str | None, str]]:
    """(lineno, target_stem_or_None, anchor) for each #-anchor link."""
    for lineno, line in doc.outside_fences():
        masked = INLINE_CODE.sub("", line)
        for target in LINK.findall(masked):
            m = ANCHOR_TARGET.match(target.strip())
            if m:
                yield lineno, m.group(1), m.group(2)


@cache
def anchors_of(path: Path) -> frozenset[str] | None:
    """A file's anchors, or None if the file does not exist.

    Cached because a chapter linking into another chapter would otherwise
    reparse the target once per link. The cache is keyed by the resolved
    path and lives for the process, which is right for a checker run but
    is why a test that rewrites a file must clear it.
    """
    if not path.exists():
        return None
    return frozenset(heading_anchors(Document.parse(path)))


def find(doc: Document) -> Iterator[Finding]:
    """Every anchor link in `doc` that resolves to no heading.

    A same-file anchor is resolved against `doc` itself rather than by
    reopening its path, so the check works on a document built in memory
    and never disagrees with the text it was handed. Only cross-file
    links go to disk, through the cache.
    """
    own = frozenset(heading_anchors(doc))
    for lineno, stem, anchor in anchor_links(doc):
        if stem is None:
            where, valid = "this file", own
        else:
            target = doc.path.parent / f"{stem}.md"
            valid = anchors_of(target.resolve())
            where = f"{stem}.md"
            if valid is None:
                yield Finding(
                    doc.path, lineno, f"link target not found: {stem}.md"
                )
                continue
        if anchor not in (valid or frozenset()):
            yield Finding(
                doc.path, lineno,
                f'no heading matches anchor "#{anchor}" in {where}',
            )


CHECK = Check(
    name="anchors",
    doc="every heading-anchor link points at a real heading",
    run=find,
    clean="Anchor links OK.",
    problem="{n} broken anchor link(s). Fix the anchor, or give the "
            "target heading an explicit {{#id}}.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    args = ap.parse_args(argv)

    findings = (
        f for p in md_files(args.paths) for f in find(Document.parse(p))
    )
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
