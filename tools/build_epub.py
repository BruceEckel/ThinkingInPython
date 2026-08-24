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

The book's diagrams are SVG, which the site serves as-is. Kindle's SVG
support is unreliable, so this build rasterizes each one to PNG and
points the EPUB at that instead. The conversion needs one of `resvg`
(preferred: the renderer typst uses, so the EPUB's diagrams match the
PDF's; `scoop install resvg`), `rsvg-convert`, `magick`, or
`inkscape`; with none of them installed the build still succeeds and
keeps the SVGs, printing a note.

The build produces two EPUBs from one assembly, differing only in
stylesheet. Listings carry the same token `<span>`s in both (keyword,
string, comment, number, tokenized by the pinned CPython's own
`tokenize` module, so 3.15-only syntax needs no third-party lexer):

- `ThinkingInPython-color.epub` colors the tokens, for backlit
  readers (phone/tablet Kindle apps). Kindle's dark mode keeps a
  declared color as given, so every color is a mid-tone chosen to
  stay readable on both white and black.
- `ThinkingInPython-eink.epub` bolds keywords and italicizes
  comments instead, the styling that survives a grayscale e-ink
  screen.

Usage:
    python tools/build_epub.py              # build/epub/ThinkingInPython-{color,eink}.epub
    python tools/build_epub.py -o DIR       # build somewhere else
    python tools/build_epub.py --keep-source  # leave build/epub/src/ in place
    python tools/build_epub.py --keep-svg     # skip the PNG conversion

Requires `pandoc` on PATH (`make tools-check-full` verifies it).
"""

import argparse
import datetime
import io
import json
import keyword
import os
import re
import shutil
import subprocess
import sys
import tokenize
from html import escape
from pathlib import Path

import build_site
from build_site import Chapter
from heading_links import ATTR_BLOCK, EXPLICIT_ID, LINK, pandoc_anchor
from tools_config import BUILD_EPUB_DIR as DEFAULT_OUT
from tools_config import ROOT
from tools_markdown import Document

# A JPEG on purpose: the cover is painted art with smooth gradients,
# which PNG stores at ~6.4 MB against JPEG's ~700 KB with no visible
# difference on a reader. Half the old EPUB's weight was this file.
COVER = ROOT / "resources" / "static" / "cover.jpg"
IMAGES_SRC = build_site.IMAGES_SRC
EPUB_STEM = "ThinkingInPython"
# The two EPUBs this build produces. Same markup, different stylesheet:
# every Python listing carries the same token spans, and the variant's
# CSS decides whether they show as color (backlit readers) or as
# bolding (e-ink, where color is invisible). HIGHLIGHT_CSS below holds
# each variant's rules.
VARIANTS = ("color", "eink")
LANG = "en-US"
# Wide enough to stay crisp on a Kindle Scribe (1860px) without paying
# for it: the diagrams are flat line art, so a 256-color PNG at this
# width is visually identical to 24-bit and about a tenth the size.
SVG_PNG_WIDTH = 1600
# First found wins. resvg leads: it is the same renderer typst uses,
# so the EPUB's rasterized diagrams match the PDF's, and it is the one
# with a packaged Windows install (scoop install resvg; rsvg-convert
# has no winget/scoop package on Windows).
SVG_TOOLS = ("resvg", "rsvg-convert", "magick", "inkscape")
# Code-listing font size, relative to the surrounding prose.
CODE_FONT_SCALE = 0.75
# How far past its own start a wrapped code line hangs, in characters.
CODE_HANG_CHARS = 2
# A monospace character's advance width as a fraction of the em. Only
# the hang depends on this, never a listing's own indentation, which
# stays literal spaces the `pre` lays out on the real character grid.
# So a font whose advance is not quite 0.6em moves a continuation a
# fraction of a character, and never puts code off its grid.
CHAR_EM = 0.6
# Indents deeper than this share the deepest hang rule. The book's
# listings reach 27, and a rule per column past that buys nothing.
MAX_HANG_INDENT = 28

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


# --------------------------------------------------------------------------- #
# SVG diagrams to PNG, for readers that cannot draw SVG
# --------------------------------------------------------------------------- #
def svg_command(tool: str, src: Path, dst: Path) -> list[str]:
    """The command line that rasterizes `src` to `dst` with `tool`.

    Each one flattens onto white. The diagrams have no background of
    their own and draw in near-black, so a transparent PNG would vanish
    against a dark theme.
    """
    match tool:
        case "resvg":
            # Width alone preserves the aspect ratio.
            return [tool, "--width", str(SVG_PNG_WIDTH),
                    "--background", "white", str(src), str(dst)]
        case "rsvg-convert":
            return [tool, "--width", str(SVG_PNG_WIDTH),
                    "--keep-aspect-ratio", "--background-color", "white",
                    "-o", str(dst), str(src)]
        case "magick":
            return [tool, "-density", "200", "-background", "white",
                    str(src), "-flatten",
                    "-resize", f"{SVG_PNG_WIDTH}x>", "-strip",
                    f"PNG8:{dst}"]
        case "inkscape":
            return [tool, "--export-type=png",
                    f"--export-width={SVG_PNG_WIDTH}",
                    "--export-background=white", "--export-background-opacity=1",
                    f"--export-filename={dst}", str(src)]
        case _:
            raise ValueError(f"unknown SVG tool: {tool}")


def find_svg_tool() -> str | None:
    """The first usable rasterizer on PATH, or None."""
    for tool in SVG_TOOLS:
        if shutil.which(tool):
            return tool
    return None


def rasterize_svgs(img_map: dict[str, str],
                   stage: Path) -> tuple[dict[str, str], list[str]]:
    """Convert every SVG in `img_map` to a PNG under `stage`.

    Returns the map with those entries repointed at the PNGs, plus any
    notes for the caller to print. An SVG that cannot be converted stays
    an SVG, so the build never fails over a diagram.
    """
    svgs = {stem: name for stem, name in img_map.items()
            if name.lower().endswith(".svg")}
    if not svgs:
        return img_map, []
    tool = find_svg_tool()
    if tool is None:
        return img_map, [
            f"NOTE: {len(svgs)} diagram(s) stay SVG, which some readers "
            "(Kindle among them) will not draw.",
            f"      Install one of {', '.join(SVG_TOOLS)} to convert them.",
        ]

    stage.mkdir(parents=True, exist_ok=True)
    out = dict(img_map)
    failed: list[str] = []
    for stem, name in sorted(svgs.items()):
        dst = stage / f"{stem}.png"
        proc = subprocess.run(svg_command(tool, IMAGES_SRC / name, dst),
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if proc.returncode != 0 or not dst.is_file():
            failed.append(name)
            continue
        out[stem] = dst.name

    notes = [f"Rasterized {len(svgs) - len(failed)} SVG diagram(s) to PNG "
             f"with {tool}."]
    if failed:
        notes.append(f"WARNING: {len(failed)} SVG(s) could not be "
                     f"converted and stay SVG: {', '.join(sorted(failed))}")
    return out, notes


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
# Syntax highlighting: token spans shared by both variants
# --------------------------------------------------------------------------- #
def token_class(tok: tokenize.TokenInfo) -> str | None:
    """The span class for one token, or None for plain text.

    Four classes only: keyword (`kw`), string (`st`), comment (`co`),
    number (`nu`). Operators and names stay plain, which keeps the
    markup small and the listings quiet. A soft keyword (`match`,
    `case`, `type`, ...) counts as a keyword only when it opens its
    line, so `type(e).__name__` and a variable named `match` stay
    plain while `match command:` and `type Bins = ...` highlight.
    """
    kind = tokenize.tok_name[tok.type]
    if kind == "COMMENT":
        return "co"
    if kind == "STRING" or kind.startswith(("FSTRING", "TSTRING")):
        return "st"
    if kind == "NUMBER":
        return "nu"
    if kind == "NAME":
        text = tok.string
        if keyword.iskeyword(text):
            return "kw"
        if (keyword.issoftkeyword(text) and text != "_"
                and tok.start[1] == len(tok.line) - len(tok.line.lstrip())):
            return "kw"
    return None


def highlight_ranges(
        lines: list[str]) -> dict[int, list[tuple[int, int, str]]]:
    """Per 0-based line index, the (start, end, class) column ranges.

    Tokenized by the running CPython's own `tokenize`, so whatever
    syntax the pinned interpreter accepts highlights correctly with no
    third-party lexer to lag behind it. A multi-line token (a triple-
    quoted string) is split into one range per line. Adjacent ranges of
    the same class merge (an f-string arrives as several FSTRING
    pieces), so the markup stays one span. A block that stops
    tokenizing (an illustrative fragment with, say, an unterminated
    string) keeps the ranges found before the error; everything after
    it stays plain.
    """
    code = "\n".join(lines) + "\n"
    ranges: dict[int, list[tuple[int, int, str]]] = {}

    def add(row: int, start: int, end: int, cls: str) -> None:
        if end <= start:
            return
        line = ranges.setdefault(row, [])
        if line and line[-1][2] == cls and line[-1][1] == start:
            line[-1] = (line[-1][0], end, cls)
        else:
            line.append((start, end, cls))

    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            cls = token_class(tok)
            if cls is None:
                continue
            (srow, scol), (erow, ecol) = tok.start, tok.end
            for row in range(srow, erow + 1):
                start = scol if row == srow else 0
                end = ecol if row == erow else len(lines[row - 1])
                add(row - 1, start, end, cls)
    except (tokenize.TokenError, SyntaxError):
        pass
    return ranges


def marked_up(line: str, spans: list[tuple[int, int, str]]) -> str:
    """The line escaped, with a `<span class>` around each range.

    `listing_html()` rstrips the line after the ranges were computed
    against the raw one, so an end past the stripped length clamps.
    """
    out: list[str] = []
    pos = 0
    for start, end, cls in spans:
        start, end = min(start, len(line)), min(end, len(line))
        if end <= start:
            continue
        out.append(escape(line[pos:start], quote=False))
        out.append(f'<span class="{cls}">'
                   f'{escape(line[start:end], quote=False)}</span>')
        pos = end
    out.append(escape(line[pos:], quote=False))
    return "".join(out)


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


def listing_html(lines: list[str], python: bool = False) -> str:
    """One fenced listing as a `<pre>` whose every line is its own block.

    With `python=True` the lines carry the token spans from
    `highlight_ranges()`, the markup both EPUB variants share; a
    ```text block holding program output stays plain.

    A code line too wide for the page wraps, and a wrapped line has to
    read as the continuation of the line above rather than as the next
    statement. That wants a hanging indent, and a hanging indent wants
    each logical line to be its own block box: CSS `text-indent` applies
    to the first line of a block, and the newlines inside a `<pre>` do
    not start new ones. So `text-indent: -2em` on the `<pre>` would
    outdent the listing's opening line and indent all 40 lines below it,
    which is not a hanging indent at all. (`text-indent: ... each-line`
    describes the wanted behavior, but no reader implements it.)

    Hence a `<span>` per line. Its class carries that line's own indent,
    so the continuation hangs past where its line starts instead of at a
    fixed column: without that, a continuation of a line indented four
    levels would begin to the *left* of the code it continues, reading
    as a dedent. A third of the book's over-wide lines sit at indent 8
    or deeper, so this is the common case, not the corner.

    The spans are emitted with no newline between them. Each is already
    `display: block`, and under `pre-wrap` a newline between two of them
    would be a second line break, double-spacing every listing.
    """
    ranges = highlight_ranges(lines) if python else {}
    out = ["<pre>"]
    for index, raw in enumerate(lines):
        line = raw.rstrip()
        if not line.strip():
            # An empty block box has no height; a space gives it one.
            out.append('<span class="h0">&#160;</span>')
            continue
        indent = min(len(line) - len(line.lstrip()), MAX_HANG_INDENT)
        text = marked_up(line, ranges.get(index, []))
        out.append(f'<span class="h{indent}">{text}</span>')
    out.append("</pre>")
    return "".join(out)


def hang_listings(text: str) -> str:
    """Rewrite every fenced block in `text` as a hanging-indent `<pre>`.

    Pandoc passes a raw HTML block through to EPUB's XHTML untouched, so
    this runs on the Markdown stream rather than on pandoc's output. The
    whole `<pre>` goes on one line: a blank line inside it would end the
    HTML block early and hand the rest back to the Markdown reader.

    Every fence is rewritten, not only the Python ones. A ```text block
    holding a program's output has the same wrapping problem.
    """
    doc = Document.from_text(text)
    if not doc.blocks:
        return text
    out: list[str] = []
    index = 0
    for block in doc.blocks:
        out.extend(doc.lines[index:block.open_at])
        out.append(listing_html(block.lines, python=block.is_python))
        index = block.end + 1
    out.extend(doc.lines[index:])
    return "\n".join(out)


def book_markdown(chapters: list[Chapter], missing: set[str],
                  unresolved: set[str],
                  img_map: dict[str, str] | None = None,
                  hang_code: bool = True) -> str:
    """Every chapter as one Markdown stream, ids namespaced and links rewritten.

    Two passes: the first namespaces the headings and so learns every id
    the book has, which the second needs before it can tell a link that
    resolves from one that does not.

    `hang_code=False` keeps every listing a fenced block instead of the
    raw-HTML `<pre>` from `hang_listings()`. build_pdf.py needs that:
    pandoc's typst writer drops raw HTML, so the EPUB's hanging-indent
    markup would erase every listing from the PDF.
    """
    prefixes = {ch.md.stem: chapter_prefix(ch) for ch in chapters}
    if img_map is None:
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
        if hang_code:
            text = hang_listings(text)
        head = f"# {chapter_heading(ch)} {{#{prefix}}}"
        parts.append(f"{head}\n\n{text.strip()}\n")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Metadata and stylesheet
# --------------------------------------------------------------------------- #
def release_line(version: str,
                 today: datetime.date | None = None) -> str:
    """The reader-facing release stamp, e.g. "Release 1.0 · August 23, 2026".

    This lands on the title page of both the EPUB and the PDF (via
    `metadata_yaml()`'s date field), so a reader can tell which release
    they hold and how old it is. The middle dot matches the Part
    headings' separator.
    """
    if today is None:
        today = datetime.date.today()
    return f"Release {version} · {today:%B} {today.day}, {today.year}"


def metadata_yaml(release: str | None = None) -> str:
    """Pandoc metadata for the EPUB and PDF builds. Values are
    JSON-quoted, which YAML accepts, so a title or license line never
    has to be escaped by hand.

    With `release`, the date field becomes the full release stamp
    ("Release 1.0 · August 23, 2026"), which pandoc renders on both
    title pages. Without it (an ad-hoc `make epub`/`make pdf`), the
    date stays the bare copyright year, so a casual build never
    masquerades as a numbered release.
    """
    fields = {
        "title": build_site.BOOK_TITLE,
        "subtitle": build_site.BOOK_SUBTITLE,
        "author": build_site.BOOK_AUTHOR,
        "lang": LANG,
        "date": (release_line(release) if release
                 else build_site.COPYRIGHT_YEAR),
        "rights": (f"© {build_site.COPYRIGHT_YEAR} "
                   f"{build_site.BOOK_AUTHOR}. Licensed CC BY-NC-ND 4.0 "
                   f"({build_site.LICENSE_URL}). Freely readable online. "
                   "No reproduction without permission."),
        "identifier": build_site.REPO_URL,
    }
    lines = [f"{k}: {json.dumps(v)}" for k, v in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def hang_css() -> str:
    """One hanging-indent rule per indent column a listing can start at.

    `listing_html()` tags each line with its own indent, so `h8` hangs a
    line indented eight columns two characters past column eight. The
    rules are generated rather than written out because they are one
    arithmetic series, and they live in the single shared stylesheet,
    not inlined per chapter the way pandoc's highlighting CSS was.

    `display: block` sits in each rule rather than on a bare
    `pre span`: a line's span now contains inline token spans from
    `marked_up()`, which a `pre span` block rule would stack one
    token per line. Scoping by the `h*` classes needs no child
    combinator, which not every Kindle renderer honors.
    """
    rules: list[str] = []
    for column in range(MAX_HANG_INDENT + 1):
        em = round((column + CODE_HANG_CHARS) * CHAR_EM, 2)
        rules.append(f"pre .h{column} {{ display: block; "
                     f"padding-left: {em}em; "
                     f"text-indent: -{em}em; }}")
    return "\n".join(rules)


# Per-variant listing styles over the same token spans. The color
# palette is constrained by Kindle's dark mode, which keeps a declared
# color as given against black, and by e-readers having no media
# queries to swap palettes: every color must read on both white and
# black, so each is a mid-tone with roughly balanced contrast against
# both (the same reason #767676 is the classic "legible on anything"
# gray). The eink variant styles with weight and slant only, which is
# all a grayscale screen can show.
HIGHLIGHT_CSS = {
    "color": """pre .kw { color: #3f78c8; }
pre .st { color: #2e8b57; }
pre .co { color: #767676; }
pre .nu { color: #b07219; }
""",
    "eink": """pre .kw { font-weight: bold; }
pre .co { font-style: italic; }
""",
}


def epub_name(variant: str) -> str:
    """One variant's filename, e.g. "ThinkingInPython-color.epub"."""
    return f"{EPUB_STEM}-{variant}.epub"


def epub_css(variant: str) -> str:
    """The bare minimum CSS, so the reader's own defaults do the rest.

    Every rule here fixes something that breaks without it, not
    something that looks nicer with it. No line height or margin is
    set anywhere: a Kindle's line-spacing control and its default type
    ramp for `h1`-`h4` already do that, and a value set here does not
    track a per-element override consistently, which reads as spacing
    that drifts from paragraph to paragraph. The one font size this
    sets, `CODE_FONT_SCALE` for listings, is set once here and inherited
    by `pre code` rather than repeated, so a nested `<code>` inside a
    `<pre>` does not compound the scale. `pre`'s `white-space: pre-wrap`
    stays load-bearing: without it, a long code line runs off the page
    instead of wrapping. No fixed colors either: a Kindle in dark mode
    keeps a declared color as given, so a light fill would become a
    glaring panel against black.

    The per-indent rules from `hang_css()` are the hanging indent for
    wrapped code lines. They need a `<span>` per listing line, which
    `listing_html()` emits; the reasoning for paying that markup is in
    its docstring. They are inert for a reader wide enough that no
    line wraps. `HIGHLIGHT_CSS[variant]` is the only difference
    between the two EPUBs: color for backlit readers, weight and
    slant for e-ink.

    `#toc ol` is the one list-style rule here, and it is also a fix,
    not a look: `chapter_heading()` already spells each chapter's
    number into its title text ("3. Containers"), but pandoc's nav
    document is still a plain `<ol>`, which every reader numbers on
    its own. Left alone, the two numbers stack ("4. 3. Containers",
    the "4." being the reader's count of nav entries so far, Parts
    included, not the chapter number). Suppressing the list's own
    marker leaves the chapter's real number as the only one shown.
    """
    return f"""pre {{
  white-space: pre-wrap; overflow-wrap: break-word;
  page-break-inside: avoid;
}}
pre, code {{ font-size: {CODE_FONT_SCALE}em; }}
pre code {{ font-size: inherit; }}
{hang_css()}
{HIGHLIGHT_CSS[variant]}h1, h2, h3, h4 {{ page-break-after: avoid; }}
figure {{ page-break-inside: avoid; }}
figure img {{ max-width: 100%; height: auto; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid currentColor; padding: 0.3em 0.5em; }}
#toc ol {{ list-style: none; padding-left: 1em; }}
"""


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run_pandoc(src: Path, css: Path, meta: Path, epub: Path,
               images: Path | None = None,
               dc: Path | None = None) -> None:
    resources = [str(IMAGES_SRC)]
    if images is not None and images.is_dir():
        # First on the path, so a rasterized diagram wins over its SVG.
        resources.insert(0, str(images))
    command = [
        "pandoc",
        "--from", "markdown+smart",
        "--to", "epub3",
        "--output", str(epub),
        "--metadata-file", str(meta),
        "--css", str(css),
        "--resource-path", os.pathsep.join(resources),
        # Pandoc's own highlighting stays off; the listings are already
        # raw `<pre>` HTML carrying this build's token spans, styled per
        # variant by HIGHLIGHT_CSS. Pandoc's version also pays in markup
        # a Kindle handles badly: 73 lines of CSS inlined in every
        # chapter file, one `<span id>` plus an empty `<a href>` anchor
        # around every line of every listing, and a
        # `pre > code.sourceCode { white-space: pre }` rule that outranks
        # this build's `pre-wrap` and so stops code from wrapping.
        "--syntax-highlighting=none",
        "--toc", "--toc-depth=2",
        "--split-level=1",
    ]
    if COVER.exists():
        command += ["--epub-cover-image", str(COVER)]
    if dc is not None:
        command += ["--epub-metadata", str(dc)]
    command.append(str(src))
    proc = subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8")
    if proc.returncode != 0:
        sys.exit(f"pandoc failed:\n{proc.stderr}")
    if proc.stderr.strip():
        print(proc.stderr.strip())


def build(out_dir: Path, keep_source: bool = False,
          keep_svg: bool = False, release: str | None = None) -> int:
    build_site.check_pandoc()
    chapters = build_site.discover()
    if not chapters:
        sys.exit("error: no chapters found in Chapters/")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    src_dir = out_dir / "src"
    src_dir.mkdir(parents=True)
    images = src_dir / "images"

    img_map = build_site.build_image_map()
    if not keep_svg:
        img_map, notes = rasterize_svgs(img_map, images)
        for note in notes:
            print(note)

    missing: set[str] = set()
    unresolved: set[str] = set()
    text = book_markdown(chapters, missing, unresolved, img_map)

    src = src_dir / "book.md"
    meta = src_dir / "metadata.yaml"
    src.write_text(text, encoding="utf-8")
    meta.write_text(metadata_yaml(release), encoding="utf-8")

    # The release stamp in `date` is prose ("Release 1.0 · ..."), which
    # pandoc cannot parse as a date, so it would leave the OPF's
    # machine-readable dc:date empty. --epub-metadata supplies a real
    # ISO date alongside the prose one on the title page.
    dc: Path | None = None
    if release is not None:
        dc = src_dir / "dc.xml"
        dc.write_text(f"<dc:date>{datetime.date.today():%Y-%m-%d}"
                      "</dc:date>\n", encoding="utf-8")

    for variant in VARIANTS:
        css = src_dir / f"epub-{variant}.css"
        css.write_text(epub_css(variant), encoding="utf-8")
        epub = out_dir / epub_name(variant)
        run_pandoc(src, css, meta, epub, images, dc)
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
    ap.add_argument("--keep-svg", action="store_true",
                    help="skip converting SVG diagrams to PNG")
    ap.add_argument("--release", metavar="VERSION",
                    help="stamp the title page with this release number "
                         "and today's date (used by `make release`)")
    args = ap.parse_args(argv)
    return build(args.out, args.keep_source, args.keep_svg, args.release)


if __name__ == "__main__":
    raise SystemExit(main())
