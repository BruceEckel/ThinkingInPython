#!/usr/bin/env python3
"""Build a gallery of every figure in the book, to check them by eye.

Writes `build/figures/index.html`: every figure the prose references, in
book order and numbered, each under its file name, chapter, line, and
caption, so "figure 12" or "observer_broadcast" names one without
ambiguity. The page shows the SVG the site and the PDF draw (read live
from `resources/images/`, so an edit shows on reload) and can switch to
the PNG the EPUB draws, rasterized here at the EPUB's width with the
first of `build_epub.SVG_TOOLS` on PATH; a PNG is redrawn only when its
SVG is newer, so a rebuild costs nothing when nothing changed.

Under each figure is a style line: the distinct colors, stroke widths,
dash patterns, font families and sizes, and arrowhead markers the SVG
uses, with anything outside the cover palette or the book's monospace
font marked. The figures are hand-authored and nothing else compares
them with each other, so this is where an odd arrowhead or a stray
color shows.

Usage:
    uv run python -m tools.figure_gallery           # build/figures/
    uv run python -m tools.figure_gallery --open    # and open it
    uv run python -m tools.figure_gallery --no-png  # skip rasterizing

`make figures` is the one-command form and `make verify` runs it, so the
gallery tracks the working tree. A figure the prose references with no
file under `resources/images/` fails the build, since the book would
render nothing there; a file no chapter references is listed at the end
of the gallery and reported, not failed.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from tools import build_epub, build_site
from tools.build_site import IMAGES_SRC
from tools.config import BUILD_DIR, CHAPTERS_DIR, ROOT

SOLUTIONS_DIR = ROOT / "Solutions"


def site_column_width() -> int:
    """The site's content column in px, read from its stylesheet.

    A figure is an `<img>` with `max-width: 100%` inside `.page`, whose
    width is the `--max-width` custom property, so this is the width
    the site draws every figure at.
    """
    m = re.search(r"--max-width:\s*(\d+)px", build_site.render_css())
    if m is None:
        raise ValueError("build_site.render_css() sets no --max-width")
    return int(m.group(1))


SITE_WIDTH = site_column_width()
READER_WIDTH = 420
OUT_DIR = BUILD_DIR / "figures"
PNG_DIR = OUT_DIR / "png"

# The same shape build_site.IMG_REF matches; a caption reflowed onto
# two lines (chapter 19's) is still one reference.
FIG_REF = re.compile(r"!\[(?P<caption>[^\]]*)\]\(_images/(?P<name>[^)\s]+)\)")
IMAGE_SUFFIXES = {".svg", ".png", ".gif", ".jpg", ".jpeg"}

# The cover palette (tools/make_cover.py) plus the box stroke the
# coupling panels use; a color outside this set is marked, not wrong.
PALETTE: dict[str, str] = {
    "#1a1612": "ink",
    "#c8bfb0": "box",
    "#7a6e62": "muted",
    "#8b1a1a": "mark",
    "#f5f0e8": "paper",
}
NEUTRAL = {"none", "white", "#fff", "#ffffff", "transparent", "currentcolor"}
BOOK_FONT = "JetBrains Mono"

COLOR_RE = re.compile(r"(?:fill|stroke|stop-color)\s*[:=]\s*[\"']?\s*([^;\"'\s)]+)")
WIDTH_RE = re.compile(r"stroke-width\s*[:=]\s*[\"']?\s*([\d.]+)")
DASH_RE = re.compile(r"stroke-dasharray\s*[:=]\s*[\"']?\s*([\d., ]+)")
FAMILY_RE = re.compile(r"font-family\s*[:=]\s*\"?([^;\">]+)")
SIZE_RE = re.compile(r"font-size\s*[:=]\s*[\"']?\s*([\d.]+)")
MARKER_DEF_RE = re.compile(r"<marker\b[^>]*\bid=\"([^\"]+)\"")
MARKER_USE_RE = re.compile(r"marker-(?:end|start|mid)\s*[:=]\s*[\"']?url\(#([^)]+)\)")
VIEWBOX_RE = re.compile(r"<svg\b[^>]*\bviewBox=\"([^\"]+)\"")
ROOT_SIZE_RE = re.compile(r"<svg\b[^>]*\b(width|height)=\"")
TITLE_RE = re.compile(r"<title>")


@dataclass
class Reference:
    """One `![caption](_images/name)` in the prose."""
    doc: Path
    line: int
    caption: str

    @property
    def chapter(self) -> str:
        return self.doc.stem.split("_", 1)[0]

    @property
    def tree(self) -> str:
        return self.doc.parent.name


@dataclass
class Style:
    """What one SVG draws with, for comparing figures with each other."""
    view_box: str = ""
    sized_root: bool = False
    titled: bool = False
    colors: list[str] = field(default_factory=list)
    widths: list[str] = field(default_factory=list)
    dashes: list[str] = field(default_factory=list)
    families: list[str] = field(default_factory=list)
    sizes: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)
    marker_uses: dict[str, int] = field(default_factory=dict)

    @property
    def odd_colors(self) -> list[str]:
        return [c for c in self.colors
                if c not in PALETTE and c.lower() not in NEUTRAL]

    @property
    def odd_families(self) -> list[str]:
        return [f for f in self.families if BOOK_FONT not in f]

    @property
    def flags(self) -> list[str]:
        out = []
        if not self.view_box:
            out.append("no viewBox")
        if self.sized_root:
            out.append("width/height on <svg>")
        if not self.titled:
            out.append("no <title>")
        if self.odd_colors:
            out.append("color outside the palette")
        if self.odd_families:
            out.append("font other than " + BOOK_FONT)
        if not self.families:
            out.append("no font-family")
        return out


@dataclass
class Figure:
    name: str
    path: Path | None
    refs: list[Reference]
    style: Style | None = None
    png: Path | None = None

    @property
    def sort_key(self) -> tuple[int, int, int]:
        if not self.refs:
            return (10_000, 0, 0)
        r = self.refs[0]
        head = r.chapter
        num = int(head) if head.isdigit() else 1_000 + ord(head[0])
        return (num, 0 if r.tree == "Chapters" else 1, r.line)


def _uniq(items: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for it in items:
        seen.setdefault(it.strip(), None)
    return [s for s in seen if s]


def read_style(text: str) -> Style:
    """The distinct drawing attributes in an SVG's source."""
    m = VIEWBOX_RE.search(text)
    uses: dict[str, int] = {}
    for u in MARKER_USE_RE.findall(text):
        uses[u] = uses.get(u, 0) + 1
    return Style(
        view_box=m.group(1) if m else "",
        sized_root=bool(ROOT_SIZE_RE.search(text)),
        titled=bool(TITLE_RE.search(text)),
        colors=_uniq([c.lower() for c in COLOR_RE.findall(text)]),
        widths=sorted(_uniq(WIDTH_RE.findall(text)), key=float),
        dashes=_uniq(DASH_RE.findall(text)),
        families=_uniq(FAMILY_RE.findall(text)),
        sizes=sorted(_uniq(SIZE_RE.findall(text)), key=float),
        markers=_uniq(MARKER_DEF_RE.findall(text)),
        marker_uses=uses,
    )


def scan(docs_dirs: list[Path] | None = None,
         images: Path = IMAGES_SRC) -> list[Figure]:
    """Every figure the prose references, plus every image file it does not."""
    dirs = docs_dirs or [CHAPTERS_DIR, SOLUTIONS_DIR]
    refs: dict[str, list[Reference]] = {}
    for d in dirs:
        if not d.is_dir():
            continue
        for doc in sorted(d.glob("*.md")):
            text = doc.read_text(encoding="utf-8")
            for m in FIG_REF.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                caption = " ".join(m["caption"].split())
                refs.setdefault(m["name"], []).append(
                    Reference(doc, line, caption))
    files: dict[str, Path] = {}
    if images.is_dir():
        for f in sorted(images.iterdir()):
            if f.suffix.lower() in IMAGE_SUFFIXES:
                files[f.stem] = f
    figures = [Figure(name, files.get(name), rs) for name, rs in refs.items()]
    figures += [Figure(name, path, []) for name, path in files.items()
                if name not in refs]
    for fig in figures:
        if fig.path and fig.path.suffix.lower() == ".svg":
            fig.style = read_style(fig.path.read_text(encoding="utf-8"))
    figures.sort(key=lambda f: f.sort_key)
    return figures


def rasterize(figures: list[Figure], out: Path = PNG_DIR) -> str | None:
    """Rasterize each SVG whose PNG is missing or older; the tool used, or None."""
    tool = build_epub.find_svg_tool()
    if tool is None:
        return None
    out.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[Path, Path]] = []
    for fig in figures:
        if fig.path is None or fig.path.suffix.lower() != ".svg":
            continue
        dst = out / f"{fig.name}.png"
        fig.png = dst
        if not dst.exists() or dst.stat().st_mtime < fig.path.stat().st_mtime:
            jobs.append((fig.path, dst))

    def run(job: tuple[Path, Path]) -> None:
        src, dst = job
        subprocess.run(build_epub.svg_command(tool, src, dst), check=True,
                       capture_output=True)

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        list(pool.map(run, jobs))
    return tool


# --------------------------------------------------------------------------- #
# The page
# --------------------------------------------------------------------------- #
CSS = """
:root { --ink: #1a1612; --muted: #7a6e62; --box: #c8bfb0; --mark: #8b1a1a;
        --paper: #f5f0e8; }
body { margin: 0; padding: 24px 32px; background: var(--paper);
       color: var(--ink); font: 15px/1.45 system-ui, sans-serif; }
h1 { font-size: 22px; margin: 0 0 4px; }
.meta { color: var(--muted); font-size: 13px; margin-bottom: 14px; }
.controls { display: flex; gap: 24px; flex-wrap: wrap; align-items: center;
            padding: 10px 14px; background: #fff; border: 1px solid var(--box);
            border-radius: 6px; margin-bottom: 18px; position: sticky; top: 8px;
            z-index: 2; }
.controls label { margin-right: 6px; }
table.index { border-collapse: collapse; font-size: 13px; margin-bottom: 28px;
              background: #fff; border: 1px solid var(--box); }
table.index th, table.index td { text-align: left; padding: 4px 10px;
                                 border-bottom: 1px solid var(--box);
                                 vertical-align: top; }
table.index th { background: #f0ebe2; }
code { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12.5px; }
.card { background: #fff; border: 1px solid var(--box); border-radius: 6px;
        padding: 14px 18px 12px; margin-bottom: 22px; }
.card h2 { font-size: 16px; margin: 0 0 2px; }
.card h2 .num { color: var(--mark); margin-right: 8px; }
.card .where { color: var(--muted); font-size: 13px; }
.card .caption { margin: 6px 0 10px; font-size: 14px; }
.card .fig { padding: 8px; background: #fff; border: 1px dashed var(--box);
             display: inline-block; max-width: 100%; }
.card img { display: block; max-width: 100%; height: auto; }
main.book .card .fig { width: __SITE__px; }
main.reader .card .fig { width: __READER__px; }
main.full .card .fig { width: 100%; box-sizing: border-box; }
.style { font-size: 12.5px; color: var(--muted); margin-top: 8px;
         /* Widths above are substituted by render_html. */
         display: grid; grid-template-columns: max-content 1fr; gap: 2px 12px; }
.style b { color: var(--ink); font-weight: 600; }
.sw { display: inline-block; width: 11px; height: 11px; border: 1px solid
      var(--box); vertical-align: -1px; margin-right: 3px; }
.odd { color: var(--mark); }
.flags { color: var(--mark); font-size: 13px; margin-top: 6px; }
.missing { color: var(--mark); }
.unref { color: var(--muted); }
"""

JS = """
const main = document.querySelector('main');
function setRender(kind) {
  for (const img of document.querySelectorAll('img[data-svg]')) {
    const src = kind === 'png' ? img.dataset.png : img.dataset.svg;
    if (src) img.src = src;
  }
  for (const b of document.querySelectorAll('[data-render]'))
    b.classList.toggle('on', b.dataset.render === kind);
}
function setWidth(kind) {
  main.className = kind;
  for (const b of document.querySelectorAll('[data-width]'))
    b.classList.toggle('on', b.dataset.width === kind);
}
document.querySelectorAll('[data-render]').forEach(b =>
  b.addEventListener('click', () => setRender(b.dataset.render)));
document.querySelectorAll('[data-width]').forEach(b =>
  b.addEventListener('click', () => setWidth(b.dataset.width)));
setWidth('book');
"""


def _swatch(color: str) -> str:
    label = PALETTE.get(color)
    odd = color not in PALETTE and color.lower() not in NEUTRAL
    text = f"{color} ({label})" if label else color
    cls = ' class="odd"' if odd else ""
    box = (f'<span class="sw" style="background:{html.escape(color)}"></span>'
           if color.lower() not in {"none", "transparent", "currentcolor"}
           else "")
    return f"<span{cls}>{box}<code>{html.escape(text)}</code></span>"


def _style_rows(s: Style) -> str:
    def row(label: str, value: str) -> str:
        return f"<b>{label}</b><span>{value or '<i>none</i>'}</span>"
    markers = ", ".join(
        f"<code>{html.escape(m)}</code>"
        + (f" ×{s.marker_uses[m]}" if m in s.marker_uses else " (unused)")
        for m in s.markers)
    families = ", ".join(
        f'<span class="{"odd" if BOOK_FONT not in f else ""}"><code>'
        f"{html.escape(f)}</code></span>" for f in s.families)
    return "".join([
        row("viewBox", f"<code>{html.escape(s.view_box)}</code>"
            if s.view_box else ""),
        row("colors", " ".join(_swatch(c) for c in s.colors)),
        row("stroke widths", ", ".join(f"<code>{w}</code>" for w in s.widths)),
        row("dashes", ", ".join(f"<code>{html.escape(d)}</code>"
                                for d in s.dashes)),
        row("fonts", families),
        row("font sizes", ", ".join(f"<code>{z}</code>" for z in s.sizes)),
        row("arrowheads", markers),
    ])


def _doc_label(doc: Path) -> str:
    """The document's path from the repo root, or its name from elsewhere."""
    try:
        return doc.relative_to(ROOT).as_posix()
    except ValueError:
        return doc.name


def _where(fig: Figure) -> str:
    if not fig.refs:
        return '<span class="unref">referenced by no chapter</span>'
    return "; ".join(f"<code>{html.escape(_doc_label(r.doc))}</code>:{r.line}"
                     for r in fig.refs)


def _rel(path: Path) -> str:
    return os.path.relpath(path, OUT_DIR).replace(os.sep, "/")


def render_html(figures: list[Figure], tool: str | None) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M")
    unref = sum(1 for f in figures if not f.refs)
    missing = sum(1 for f in figures if f.path is None)
    png_note = (f"PNGs rasterized with <code>{tool}</code> at "
                f"{build_epub.SVG_PNG_WIDTH}px, as the EPUB draws them"
                if tool else "no SVG rasterizer on PATH, so no PNG view")
    rows = []
    cards = []
    for i, fig in enumerate(figures, 1):
        anchor = html.escape(fig.name)
        cap = html.escape(fig.refs[0].caption) if fig.refs else ""
        flags = fig.style.flags if fig.style else []
        if fig.path is None:
            flags = ["NO FILE under resources/images/"] + flags
        rows.append(
            f'<tr><td>{i}</td><td><a href="#{anchor}"><code>{anchor}</code>'
            f"</a></td><td>{_where(fig)}</td><td>{cap}</td>"
            f'<td class="flags">{html.escape("; ".join(flags))}</td></tr>')
        if fig.path is None:
            img = ('<p class="missing">The prose references this figure and '
                   'no file under <code>resources/images/</code> has this '
                   "name.</p>")
        else:
            src = _rel(fig.path)
            png = f' data-png="{_rel(fig.png)}"' if fig.png else ""
            img = (f'<div class="fig"><img src="{src}" data-svg="{src}"{png} '
                   f'alt="{anchor}"></div>')
        style = (f'<div class="style">{_style_rows(fig.style)}</div>'
                 if fig.style else "")
        flag_line = (f'<div class="flags">{html.escape("; ".join(flags))}</div>'
                     if flags else "")
        cards.append(
            f'<section class="card" id="{anchor}">'
            f'<h2><span class="num">{i}</span><code>{anchor}'
            f"{html.escape(fig.path.suffix) if fig.path else ''}</code></h2>"
            f'<div class="where">{_where(fig)}</div>'
            f'<p class="caption">{cap}</p>{img}{flag_line}{style}</section>')
    css = (CSS.replace("__SITE__", str(SITE_WIDTH))
              .replace("__READER__", str(READER_WIDTH)))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Thinking in Python: figures</title>
<style>{css}</style></head>
<body>
<h1>Thinking in Python: figures</h1>
<div class="meta">{len(figures)} figures, {unref} referenced by no chapter,
{missing} with no file. Built {stamp}. {png_note}.
The SVG view reads <code>resources/images/</code> live; reload after an edit.
Refer to a figure by its number or its file name.</div>
<div class="controls">
<span><label>Render:</label>
<button data-render="svg" class="on">SVG (site, PDF)</button>
<button data-render="png"{"" if tool else " disabled"}>PNG (EPUB)</button></span>
<span><label>Width:</label>
<button data-width="reader">e-reader ({READER_WIDTH}px)</button>
<button data-width="book">site column ({SITE_WIDTH}px)</button>
<button data-width="full">full</button></span>
</div>
<table class="index"><tr><th>#</th><th>file</th><th>referenced at</th>
<th>caption</th><th>flags</th></tr>
{"".join(rows)}
</table>
<main class="book">
{"".join(cards)}
</main>
<script>{JS}</script>
<style>button.on {{ background: var(--ink); color: var(--paper); }}</style>
</body></html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--no-png", action="store_true",
                    help="do not rasterize; the page shows SVGs only")
    ap.add_argument("--open", action="store_true",
                    help="open the gallery in the default browser")
    args = ap.parse_args(argv)
    figures = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tool = None if args.no_png else rasterize(figures)
    index = OUT_DIR / "index.html"
    index.write_text(render_html(figures, tool), encoding="utf-8")
    missing = [f for f in figures if f.path is None]
    unref = [f for f in figures if not f.refs]
    print(f"{len(figures)} figures -> {index.relative_to(ROOT)}"
          + (f" (PNGs via {tool})" if tool
             else " (no PNGs: no rasterizer on PATH)" if not args.no_png
             else ""))
    for f in unref:
        print(f"  referenced by no chapter: {f.name}")
    for f in missing:
        r = f.refs[0]
        print(f"  NO FILE: _images/{f.name} at {_doc_label(r.doc)}:{r.line}")
    if args.open:
        webbrowser.open(index.as_uri())
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
