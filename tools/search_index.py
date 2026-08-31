#!/usr/bin/env python
"""Build the client-side search index for the static site.

`build_site.py` renders one HTML page per chapter. This module turns the same
Markdown into `search-index.json`, a flat list of *sections* that the site's
`search.js` fetches and searches in the browser. There is no server, so the
whole index ships to the reader; it is fetched lazily, the first time someone
opens the search box.

A section is the text under one `##` or `###` heading, plus the chapter's
opening text (which sits under no heading and links to the page itself). Each
record carries the URL and anchor needed to deep-link to it:

    {"u": "12_Techniques--Data_Classes_as_Types.html",  # page
     "a": "immutability",                   # heading anchor, "" for the intro
     "l": "Chapter 12",                     # label, as on the index page
     "c": "Data Classes as Types",          # chapter title
     "s": "Immutability",                   # section heading
     "t": "passing frozen=True makes ..."}  # searchable text

Anchors come from `heading_links.pandoc_anchor()`, so a link the gate accepts in
the Markdown and a link the search results produce resolve to the same heading.

Code inside fenced blocks is indexed along with the prose: in a programming
book, `__post_init__` or `NamedTuple` is exactly what a reader searches for, and
those names often appear only in listings. Markdown decoration (backticks,
emphasis, link URLs, heading marks) is stripped so it cannot match or clutter a
result snippet.

Usage:
    python tools/search_index.py            # write to build/site/
    python tools/search_index.py -o DIR     # write somewhere else
    python tools/search_index.py --stats    # report size, write nothing
"""

import argparse
import json
import re
from pathlib import Path
from typing import NamedTuple

from heading_links import ATTR_BLOCK, EXPLICIT_ID, pandoc_anchor
from tools_config import BUILD_SITE_DIR as DEFAULT_OUT
from tools_config import FENCE_ANY_RE as FENCE
from tools_repo import md_files

INDEX_NAME = "search-index.json"

HEADING = re.compile(r"^(#{2,3})\s+(.*?)\s*$")
ANY_HEADING = re.compile(r"^#{1,6}\s+")
MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
FOOTNOTE = re.compile(r"\[\^[^\]]*\]")
HTML_TAG = re.compile(r"<[^>]+>")
# Underscores survive: `__post_init__` and `snake_case` names are exactly what
# a reader searches for. The book writes emphasis with `*`, not `_`.
DECORATION = re.compile(r"[`*>|]+")
LIST_MARK = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+", re.MULTILINE)
SPACES = re.compile(r"\s+")


class Source(NamedTuple):
    """One chapter's Markdown plus the page `build_site.py` renders it to."""
    md: Path
    url: str
    title: str
    label: str


class Section(NamedTuple):
    url: str
    anchor: str
    label: str
    chapter: str
    heading: str
    text: str

    def as_record(self) -> dict[str, str]:
        return {"u": self.url, "a": self.anchor, "l": self.label,
                "c": self.chapter, "s": self.heading, "t": self.text}


def clean(lines: list[str]) -> str:
    """Strip Markdown decoration, leaving text worth matching against."""
    text = "\n".join(lines)
    text = MD_IMAGE.sub(" ", text)
    text = MD_LINK.sub(r"\1", text)
    text = FOOTNOTE.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = LIST_MARK.sub("", text)
    text = DECORATION.sub("", text)
    return SPACES.sub(" ", text).strip()


def anchor_for(raw: str, counts: dict[str, int]) -> str:
    """The id pandoc gives this heading, duplicates numbered as pandoc does."""
    explicit = EXPLICIT_ID.search(raw)
    if explicit:
        return explicit.group(1)
    base = pandoc_anchor(ATTR_BLOCK.sub("", raw))
    if not base:
        return ""
    n = counts.get(base, 0)
    counts[base] = n + 1
    return base if n == 0 else f"{base}-{n}"


def heading_text(raw: str) -> str:
    return clean([ATTR_BLOCK.sub("", raw)])


def split_sections(source: Source) -> list[Section]:
    """One record per `##`/`###` heading, plus the text above the first one."""
    lines = source.md.read_text(encoding="utf-8").split("\n")
    counts: dict[str, int] = {}
    sections: list[Section] = []
    heading, anchor = source.title, ""
    body: list[str] = []
    in_fence = False

    def flush() -> None:
        text = clean(body)
        if text:
            sections.append(Section(source.url, anchor, source.label,
                                    source.title, heading, text))

    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            body.append(line)
            continue
        if in_fence:
            body.append(line)
            continue
        m = HEADING.match(line)
        if not m:
            # The chapter's own `#` title is already the record's chapter name.
            if not ANY_HEADING.match(line):
                body.append(line)
            continue
        flush()
        raw = m.group(2)
        heading, anchor, body = heading_text(raw), anchor_for(raw, counts), []
    flush()
    return sections


def build(sources: list[Source]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for source in sources:
        records += [s.as_record() for s in split_sections(source)]
    return records


def write(sources: list[Source], out_dir: Path) -> int:
    """Write the index; return the number of sections it holds."""
    records = build(sources)
    (out_dir / INDEX_NAME).write_text(
        json.dumps(records, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    return len(records)


def default_sources() -> list[Source]:
    """Every chapter, labeled the way `build_site.py` labels it."""
    sources: list[Source] = []
    for md in md_files():
        number = md.stem.split("_", 1)[0]
        title = re.sub(r"^\d+_", "", md.stem).replace("_", " ")
        for line in md.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"^#\s+(.*?)\s*#*\s*$", line)
            if m:
                title = m.group(1)
                break
        if number == "00":
            label = "Front Matter"
        elif number.isdigit():
            label = f"Chapter {int(number)}"
        else:
            label = f"Appendix {number}"
        sources.append(Source(md, f"{md.stem}.html", title, label))
    return sources


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT})")
    ap.add_argument("--stats", action="store_true",
                    help="report the index size without writing it")
    args = ap.parse_args(argv)
    sources = default_sources()
    if args.stats:
        records = build(sources)
        raw = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
        chars = sum(len(r["t"]) for r in records)
        print(f"{len(records)} sections from {len(sources)} chapters")
        print(f"{chars:,} characters of text, "
              f"{len(raw.encode('utf-8')) / 1024:.0f} KB of JSON")
        return 0
    if not args.out.is_dir():
        raise SystemExit(f"error: no such directory: {args.out}")
    count = write(sources, args.out)
    print(f"Wrote {INDEX_NAME}: {count} sections "
          f"({(args.out / INDEX_NAME).stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
