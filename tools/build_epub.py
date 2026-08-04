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
points the EPUB at that instead. The conversion needs one of
`rsvg-convert`, `magick`, or `inkscape`; with none of them installed the
build still succeeds and keeps the SVGs, printing a note.

Usage:
    python tools/build_epub.py              # build/epub/ThinkingInPython.epub
    python tools/build_epub.py -o DIR       # build somewhere else
    python tools/build_epub.py --keep-source  # leave build/epub/src/ in place
    python tools/build_epub.py --keep-svg     # skip the PNG conversion

Requires `pandoc` on PATH (`make check-tools-full` verifies it).
"""

import argparse
import json
import os
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
# Wide enough to stay crisp on a Kindle Scribe (1860px) without paying
# for it: the diagrams are flat line art, so a 256-color PNG at this
# width is visually identical to 24-bit and about a tenth the size.
SVG_PNG_WIDTH = 1600
SVG_TOOLS = ("rsvg-convert", "magick", "inkscape")
# Code-listing font size, relative to the surrounding prose.
CODE_FONT_SCALE = 0.75

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
                  unresolved: set[str],
                  img_map: dict[str, str] | None = None) -> str:
    """Every chapter as one Markdown stream, ids namespaced and links rewritten.

    Two passes: the first namespaces the headings and so learns every id
    the book has, which the second needs before it can tell a link that
    resolves from one that does not.
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
h1, h2, h3, h4 {{ page-break-after: avoid; }}
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
               images: Path | None = None) -> None:
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
        # Highlighting off. It is invisible on e-ink, and pandoc pays for
        # it in markup a Kindle handles badly: 73 lines of CSS inlined in
        # every chapter file, one `<span id>` plus an empty `<a href>`
        # anchor around every line of every listing, and a
        # `pre > code.sourceCode { white-space: pre }` rule that outranks
        # this build's `pre-wrap` and so stops code from wrapping.
        # Turning it off halves the EPUB.
        "--syntax-highlighting=none",
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


def build(out_dir: Path, keep_source: bool = False,
          keep_svg: bool = False) -> int:
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
    css = src_dir / "epub.css"
    meta = src_dir / "metadata.yaml"
    src.write_text(text, encoding="utf-8")
    css.write_text(epub_css(), encoding="utf-8")
    meta.write_text(metadata_yaml(), encoding="utf-8")

    epub = out_dir / EPUB_NAME
    run_pandoc(src, css, meta, epub, images)

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
    args = ap.parse_args(argv)
    return build(args.out, args.keep_source, args.keep_svg)


if __name__ == "__main__":
    raise SystemExit(main())
