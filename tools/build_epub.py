#!/usr/bin/env python3
"""Render the book's Markdown into a single EPUB with pandoc.

The site build (build_site.py) emits one HTML page per chapter, so a
cross-reference stays a link between files. An EPUB is one document, so
every chapter is concatenated into a single Markdown stream and every
`.md` link has to become an in-document anchor. That merge is where the
book's anchors stop being unique: 44 chapters each end in `## Exercises`,
and `#immutability`, `#generators`, `#lambdas` and six others appear in
two to four chapters apiece. Pandoc's own de-duplication would number
them in document order (`immutability`, `immutability-1`, ...), silently
sending `[Immutability](12_Data_Classes_as_Types.md#immutability)` to
chapter 3's heading instead of chapter 12's.

So this builder does not rely on that de-duplication. It gives every
heading an explicit id namespaced by chapter number, and rewrites every
link to match:

    ## Immutability                       ->  ## Immutability {#ch12-immutability}
    [x](12_Data_Classes.md#immutability)  ->  [x](#ch12-immutability)
    [x](#immutability)                    ->  [x](#ch12-immutability)
    [x](24_Singleton.md)                  ->  [x](#ch24)

The `ch` prefix is not decoration: an EPUB is XHTML, where an id may not
start with a digit.

The old ids come from `heading_links.pandoc_anchor()`, the same function
the `anchors` gate checks links with and the same one search_index.py
deep-links with, so a link the gate accepts is a link this build
resolves. Its per-file de-duplication is mirrored here too, so a chapter
with two identical headings keeps pandoc's `-1` suffix inside its own
namespace.

Part dividers come from `build_site.PARTS`, like the site's contents
page, and become level-1 headings so each opens its own EPUB section.

Usage:
    python tools/build_epub.py              # build/epub/ThinkingInPython.epub
    python tools/build_epub.py -o DIR       # build somewhere else
    python tools/build_epub.py --keep-source  # leave build/epub/src/ in place

Requires `pandoc` on PATH (`make check-tools-full` verifies it).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import build_site
from build_site import Chapter
from heading_links import ATTR_BLOCK, EXPLICIT_ID, LINK, pandoc_anchor
from tools_config import BUILD_EPUB_DIR as DEFAULT_OUT
from tools_config import ROOT
from tools_markdown import Document

COVER = ROOT / "resources" / "static" / "cover.png"
IMAGES_SRC = build_site.IMAGES_SRC
EPUB_NAME = "ThinkingInPython.epub"
LANG = "en-US"

HEADING_LINE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
CODE_SPAN = re.compile(r"(`[^`]*`)")
# Like heading_links.ANCHOR_TARGET, but the anchor also accepts a period.
# Pandoc keeps a period in an auto-generated id, so
# "## Dynamic Binding vs. Pattern Matching" is reachable as
# "#dynamic-binding-vs.-pattern-matching" and chapter 13 links to it.
ANCHOR_TARGET = re.compile(r"^(?:([\w./-]+)\.md)?#([\w.-]+)$")
FILE_TARGET = re.compile(r"^([\w./-]+)\.md$")
HAS_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Per-chapter anchor namespacing
# --------------------------------------------------------------------------- #
def chapter_prefix(ch: Chapter) -> str:
    """The id namespace for one chapter, e.g. "ch12" or "chA"."""
    return f"ch{ch.number}"


def heading_ids(doc: Document) -> list[tuple[int, str | None]]:
    """(line index, the id pandoc would assign) for each heading.

    Mirrors `heading_links.heading_anchors()`, including its per-file
    de-duplication counter, but keeps the line index so the heading can
    be rewritten in place. The id is None for a heading whose text has
    no letter in it, which pandoc leaves without an id.
    """
    ids: list[tuple[int, str | None]] = []
    counts: dict[str, int] = {}
    fenced = doc.in_fence()
    for index, line in enumerate(doc.lines):
        if fenced[index]:
            continue
        m = HEADING_LINE.match(line)
        if m is None:
            continue
        text = m.group(2)
        explicit = EXPLICIT_ID.search(text)
        if explicit:
            ids.append((index, explicit.group(1)))
            continue
        base = pandoc_anchor(ATTR_BLOCK.sub("", text))
        if not base:
            ids.append((index, None))
            continue
        n = counts.get(base, 0)
        counts[base] = n + 1
        ids.append((index, base if n == 0 else f"{base}-{n}"))
    return ids


def namespace_headings(lines: list[str], doc: Document,
                       prefix: str) -> set[str]:
    """Give each heading in `lines` an explicit `{#prefix-id}`.

    Returns the ids assigned, which the caller needs to resolve links.
    """
    assigned: set[str] = set()
    for index, old in heading_ids(doc):
        if old is None:
            continue
        m = HEADING_LINE.match(lines[index])
        if m is None:
            continue
        text = ATTR_BLOCK.sub("", m.group(2)).rstrip()
        new = f"{prefix}-{old}"
        lines[index] = f"{m.group(1)} {text} {{#{new}}}"
        assigned.add(new)
    return assigned


def title_anchor(title: str) -> str:
    """The anchor a chapter's own `#` heading would have carried.

    `load_chapter()` removes that heading, since its text becomes the
    chapter's title, so a link naming it would point at nothing. The
    caller aliases it to the chapter's root id instead.
    """
    explicit = EXPLICIT_ID.search(title)
    if explicit:
        return explicit.group(1)
    return pandoc_anchor(ATTR_BLOCK.sub("", title))


def outside_code(line: str, fn) -> str:
    """Apply `fn` to the parts of `line` that are not inline code spans.

    A split on a capturing pattern alternates text, delimiter, text, so
    the odd indices are the code spans and are passed through untouched.
    """
    parts = CODE_SPAN.split(line)
    return "".join(p if i % 2 else fn(p) for i, p in enumerate(parts))


class Ids:
    """The book's namespaced heading ids, and how a link reaches them."""

    def __init__(self, prefixes: dict[str, str], known: set[str],
                 aliases: dict[str, str]) -> None:
        self.prefixes = prefixes
        self.known = known
        self.aliases = aliases

    def resolve(self, stem: str | None, anchor: str,
                here: str) -> str | None:
        """The in-document id a link names, or None if it reaches nothing."""
        owner = here if stem is None else self.prefixes.get(stem)
        if owner is None:
            return None
        wanted = f"{owner}-{anchor}"
        if wanted in self.known:
            return wanted
        return self.aliases.get(wanted)


def relink(text: str, prefix: str, ids: Ids, unresolved: set[str]) -> str:
    """Rewrite one line's book links into in-document anchors.

    Inline code is left alone: chapter 8 writes `[x](#anchor)` inside
    backticks to show the link syntax, which is text, not a link.
    """
    def repl(m: re.Match[str]) -> str:
        target = m.group(1).strip()
        if HAS_SCHEME.match(target):  # external link, left alone
            return m.group(0)
        anchor = ANCHOR_TARGET.match(target)
        if anchor is not None:
            found = ids.resolve(anchor.group(1), anchor.group(2), prefix)
            if found is None:
                unresolved.add(target)
                return m.group(0)
            return f"](#{found})"
        whole = FILE_TARGET.match(target)
        if whole is not None:
            owner = ids.prefixes.get(whole.group(1))
            if owner is None:
                unresolved.add(target)
                return m.group(0)
            return f"](#{owner})"
        return m.group(0)

    return outside_code(text, lambda part: LINK.sub(repl, part))


def rewrite_images(text: str, img_map: dict[str, str],
                   missing: set[str]) -> str:
    """`_images/<name>` to the bare filename pandoc resolves via --resource-path."""
    def repl(m: re.Match[str]) -> str:
        name = m.group(2)
        filename = img_map.get(name)
        if not filename:
            missing.add(name)
            filename = f"{name}.png"
        return f"{m.group(1)}{filename}{m.group(3)}"

    return build_site.IMG_REF.sub(repl, text)


# --------------------------------------------------------------------------- #
# Assembling the single Markdown stream
# --------------------------------------------------------------------------- #
def chapter_heading(ch: Chapter) -> str:
    """The level-1 heading text, numbered so the EPUB's contents reads like
    the site's."""
    title = ATTR_BLOCK.sub("", ch.title).rstrip()
    if ch.number.isdigit():
        return f"{int(ch.number)}. {title}"
    return f"Appendix {ch.number}. {title}"


def part_markdown(roman: str, title: str) -> str:
    return f"# Part {roman} · {title} {{#part-{roman.lower()}}}\n"


def book_markdown(chapters: list[Chapter], missing: set[str],
                  unresolved: set[str]) -> str:
    """Every chapter as one Markdown stream, ids namespaced and links rewritten.

    Two passes: the first namespaces the headings and so learns every id
    the book has, which the second needs before it can tell a link that
    resolves from one that does not.
    """
    prefixes = {ch.md.stem: chapter_prefix(ch) for ch in chapters}
    img_map = build_site.build_image_map()

    prepared: list[tuple[Chapter, Document, list[str]]] = []
    known: set[str] = set()
    for ch in chapters:
        _, body = build_site.load_chapter(ch.md)
        doc = Document.from_text(body, ch.md)
        lines = list(doc.lines)
        prefix = prefixes[ch.md.stem]
        known.add(prefix)
        known |= namespace_headings(lines, doc, prefix)
        prepared.append((ch, doc, lines))

    # A link naming a chapter's own title heading reaches the chapter
    # itself, unless a real section already claimed that id.
    aliases: dict[str, str] = {}
    for ch in chapters:
        anchor = title_anchor(ch.title)
        prefix = prefixes[ch.md.stem]
        if anchor and f"{prefix}-{anchor}" not in known:
            aliases[f"{prefix}-{anchor}"] = prefix
    ids = Ids(prefixes, known, aliases)

    parts: list[str] = []
    for ch, doc, lines in prepared:
        divider = build_site.PARTS.get(ch.number)
        if divider is not None:
            parts.append(part_markdown(*divider))
        prefix = prefixes[ch.md.stem]
        fenced = doc.in_fence()
        for index, line in enumerate(lines):
            if not fenced[index]:
                lines[index] = relink(line, prefix, ids, unresolved)
        text = rewrite_images("\n".join(lines), img_map, missing)
        head = f"# {chapter_heading(ch)} {{#{prefix}}}"
        parts.append(f"{head}\n\n{text.strip()}\n")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Metadata and stylesheet
# --------------------------------------------------------------------------- #
def metadata_yaml() -> str:
    """Pandoc EPUB metadata. Values are JSON-quoted, which YAML accepts,
    so a title or license line never has to be escaped by hand."""
    fields = {
        "title": build_site.BOOK_TITLE,
        "subtitle": build_site.BOOK_SUBTITLE,
        "author": build_site.BOOK_AUTHOR,
        "lang": LANG,
        "date": build_site.COPYRIGHT_YEAR,
        "rights": (f"© {build_site.COPYRIGHT_YEAR} "
                   f"{build_site.BOOK_AUTHOR}. Licensed CC BY-NC-ND 4.0 "
                   f"({build_site.LICENSE_URL}). Freely readable online. "
                   "No reproduction without permission."),
        "identifier": build_site.REPO_URL,
    }
    lines = [f"{k}: {json.dumps(v)}" for k, v in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def epub_css() -> str:
    """A restrained stylesheet: readers override fonts and margins, so this
    sets only what the book's structure needs."""
    return """body { line-height: 1.5; }
h1, h2, h3, h4 { line-height: 1.25; page-break-after: avoid; }
h1 { font-size: 1.6em; margin: 1em 0 0.75em; }
h2 { font-size: 1.3em; margin: 1.5em 0 0.5em; }
h3 { font-size: 1.1em; margin: 1.25em 0 0.5em; }
pre {
  font-size: 0.8em; line-height: 1.35; white-space: pre-wrap;
  overflow-wrap: break-word; padding: 0.5em 0.6em;
  background: #f4f2ee; border-left: 3px solid #c8bfb0;
  page-break-inside: avoid;
}
code { font-size: 0.9em; overflow-wrap: break-word; }
pre code { font-size: inherit; }
figure { margin: 1.5em 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; height: auto; }
figcaption { font-size: 0.85em; font-style: italic; margin-top: 0.5em; }
blockquote {
  margin: 1em 1.5em; font-style: italic; color: #444;
}
table { border-collapse: collapse; font-size: 0.9em; }
th, td { border: 1px solid #c8bfb0; padding: 0.3em 0.5em; }
"""


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run_pandoc(src: Path, css: Path, meta: Path, epub: Path) -> None:
    command = [
        "pandoc",
        "--from", "markdown+smart",
        "--to", "epub3",
        "--output", str(epub),
        "--metadata-file", str(meta),
        "--css", str(css),
        "--resource-path", str(IMAGES_SRC),
        # No --highlight-style: pygments is pandoc's default, and naming it
        # explicitly draws a deprecation warning from pandoc 3.10 on.
        "--toc", "--toc-depth=2",
        "--split-level=1",
    ]
    if COVER.exists():
        command += ["--epub-cover-image", str(COVER)]
    command.append(str(src))
    proc = subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8")
    if proc.returncode != 0:
        sys.exit(f"pandoc failed:\n{proc.stderr}")
    if proc.stderr.strip():
        print(proc.stderr.strip())


def build(out_dir: Path, keep_source: bool = False) -> int:
    build_site.check_pandoc()
    chapters = build_site.discover()
    if not chapters:
        sys.exit("error: no chapters found in Chapters/")

    missing: set[str] = set()
    unresolved: set[str] = set()
    text = book_markdown(chapters, missing, unresolved)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    src_dir = out_dir / "src"
    src_dir.mkdir(parents=True)

    src = src_dir / "book.md"
    css = src_dir / "epub.css"
    meta = src_dir / "metadata.yaml"
    src.write_text(text, encoding="utf-8")
    css.write_text(epub_css(), encoding="utf-8")
    meta.write_text(metadata_yaml(), encoding="utf-8")

    epub = out_dir / EPUB_NAME
    run_pandoc(src, css, meta, epub)

    size = epub.stat().st_size / 1024
    print(f"Built {epub.relative_to(ROOT)} "
          f"({len(chapters)} chapters, {size:.0f} KB).")
    if not COVER.exists():
        print(f"NOTE: no cover image at {COVER.relative_to(ROOT)}.")

    if not keep_source:
        shutil.rmtree(src_dir)
    else:
        print(f"Kept the pandoc input in {src_dir.relative_to(ROOT)}.")

    status = 0
    if missing:
        print(f"\nWARNING: {len(missing)} referenced image(s) not found in "
              f"{IMAGES_SRC.relative_to(ROOT)}:")
        for name in sorted(missing):
            print(f"  ? _images/{name}")
        status = 1
    if unresolved:
        print(f"\nWARNING: {len(unresolved)} link(s) name no book chapter "
              "and stay unlinked in the EPUB:")
        for target in sorted(unresolved):
            print(f"  ? {target}")
        status = 1
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT})")
    ap.add_argument("--keep-source", action="store_true",
                    help="leave the generated pandoc input under <out>/src/")
    args = ap.parse_args(argv)
    return build(args.out, args.keep_source)


if __name__ == "__main__":
    raise SystemExit(main())
