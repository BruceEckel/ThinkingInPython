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
from pathlib import Path

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r"\{#([\w-]+)[^}]*\}\s*$")
ATTR_BLOCK = re.compile(r"\s*\{[^}]*\}\s*$")
INLINE_CODE = re.compile(r"`[^`]*`")
INLINE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
LINK = re.compile(r"\]\(([^)]+)\)")
ANCHOR_TARGET = re.compile(r"^(?:([\w./-]+)\.md)?#([\w-]+)$")


def pandoc_anchor(text: str) -> str:
    """Reproduce pandoc's auto identifier for a heading's visible text."""
    text = INLINE_CODE.sub(lambda m: m.group(0).strip("`"), text)
    text = INLINE_LINK.sub(r"\1", text)  # [text](url) -> text
    return _slug(text)


def _slug(text: str) -> str:
    # Keep letters, digits, underscores, hyphens, periods, and spaces.
    kept = "".join(c for c in text if c.isalnum() or c in " _-.")
    kept = re.sub(r"\s+", "-", kept).lower()
    m = re.search(r"[a-z]", kept)  # identifiers start at the first letter
    return kept[m.start():] if m else ""


def heading_anchors(lines: list[str]) -> set[str]:
    """Every anchor pandoc would assign to the headings in `lines`."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if not m:
            continue
        text = m.group(1)
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


def anchor_links(lines: list[str]):
    """Yield (lineno, target_stem_or_None, anchor) for #-anchor links."""
    in_fence = False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        masked = INLINE_CODE.sub("", line)
        for target in LINK.findall(masked):
            m = ANCHOR_TARGET.match(target.strip())
            if m:
                yield i, m.group(1), m.group(2)


def iter_files(paths: list[str]) -> list[Path]:
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
                    help="Markdown files or directories (default: Markdown/)")
    args = ap.parse_args(argv)
    files = iter_files(args.paths or ["Markdown"])

    cache: dict[Path, set[str] | None] = {}

    def anchors_of(path: Path) -> set[str] | None:
        key = path.resolve()
        if key not in cache:
            cache[key] = (heading_anchors(
                path.read_text(encoding="utf-8").splitlines())
                if path.exists() else None)
        return cache[key]

    total = 0
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        for lineno, stem, anchor in anchor_links(lines):
            if stem is None:
                where, valid = "this file", anchors_of(f)
            else:
                target = f.parent / f"{stem}.md"
                valid = anchors_of(target)
                where = f"{stem}.md"
                if valid is None:
                    print(f"{f}:{lineno}: link target not found: {stem}.md")
                    total += 1
                    continue
            if anchor not in (valid or set()):
                print(f"{f}:{lineno}: no heading matches anchor "
                      f"\"#{anchor}\" in {where}")
                total += 1

    if total:
        print(f"\n{total} broken anchor link(s). Fix the anchor, or give the "
              "target heading an explicit {#id}.")
        return 1
    print("Anchor links OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
