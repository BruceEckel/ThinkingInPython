"""The pattern chapters' opening figures, one module per chapter.

Each pattern chapter opens with a figure that tells the pattern's story:
what happens, in what order, and who knows what. Chapter 30's Observer
storyboard came first (2026-09-29). Bruce found it told "a much more
accessible story" than the coupling-notation panels, and asked for the
same for every pattern chapter, with no notation or precedent to follow:
whatever picture best helps the reader, a variation of the coupling panel
included when that works for a pattern.

A figure is a module here named `chNN_<pattern>.py` that defines:

    STEM     the SVG's name in resources/images/, without `.svg`
    render() the SVG source, as a string

`python -m tools.story_figures` discovers every such module and writes
the SVGs it draws; `--check` exits nonzero when a committed SVG differs
from what its module draws, or when a figure fails one of `tip figures`'
per-figure checks (`lint()`). `--only NN` limits either to one chapter,
and `--png DIR` rasterizes with the EPUB's rasterizer so you can look at
the result, since text that fits in a browser can collide once
rasterized. Never edit one of these SVGs by hand.

The helpers below are the vocabulary the figures share: the cover
palette, the book font, text and boxes, and arrows whose heads come from
`tools/arrowheads.py` with each tip `TIP_GAP` short of its target. An
outer shape that encloses the target of an arrow (a class box holding a
list, a shaded region holding the responders) is drawn with `region()`,
a path, because `arrowheads.tight_tips()` measures a tip against every
rect around it and would read a tip on an inner box as buried in the
outer one.
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path

from tools.arrowheads import HEADS, marker_def, shorten_line
from tools.config import ROOT

IMAGES = ROOT / "resources" / "images"
INK, BOX, MUTED, RED = "#1a1612", "#c8bfb0", "#7a6e62", "#8b1a1a"
# The fill for a shaded region. The EPUB's PNG8 conversion cuts each
# channel to a multiple of 17, which turned a translucent BOX over white,
# and every pale warm tint tried, yellow or pink; a neutral 0xEE survives.
SHADE = "#eeeeee"
TIP_GAP = 4
FONT = "font-family=\"'JetBrains Mono', Consolas, monospace\""

type Point = tuple[float, float]


def esc(s: str) -> str:
    """Text content for SVG: `<`, `>`, and `&` escaped."""
    return html.escape(s, quote=False)


def text(x: float, y: float, s: str, size: float = 11, fill: str = INK,
         anchor: str = "start", bold: bool = False,
         italic: bool = False) -> str:
    b = ' font-weight="bold"' if bold else ""
    i = ' font-style="italic"' if italic else ""
    return (f'  <text x="{x:g}" y="{y:g}" font-size="{size:g}" '
            f'fill="{fill}"{b}{i} text-anchor="{anchor}">{esc(s)}</text>\n')


def rect(x: float, y: float, w: float, h: float, stroke: str = BOX,
         width: float = 1.3, dash: bool = False, rx: float = 4,
         fill: str = "none") -> str:
    """A box an arrow may point at."""
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width:g}" '
            f'rx="{rx:g}"{d}/>\n')


def outline(x: float, y: float, w: float, h: float, r: float = 4) -> str:
    """Path data for a rectangle with corners of radius `r`."""
    if not r:
        return f"M{x:g},{y:g} H{x + w:g} V{y + h:g} H{x:g} Z"
    return (f"M{x + r:g},{y:g} H{x + w - r:g} Q{x + w:g},{y:g} "
            f"{x + w:g},{y + r:g} V{y + h - r:g} Q{x + w:g},{y + h:g} "
            f"{x + w - r:g},{y + h:g} H{x + r:g} Q{x:g},{y + h:g} "
            f"{x:g},{y + h - r:g} V{y + r:g} Q{x:g},{y:g} {x + r:g},{y:g} Z")


def region(x: float, y: float, w: float, h: float, stroke: str = "none",
           width: float = 1.6, fill: str = "none", opacity: float = 1,
           r: float = 4, dash: bool = False) -> str:
    """A box that encloses other boxes arrows point at (see the docstring)."""
    o = f' fill-opacity="{opacity:g}"' if opacity != 1 else ""
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <path d="{outline(x, y, w, h, r)}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{width:g}"{d}/>\n')


def line(a: Point, b: Point, color: str = BOX, width: float = 0.8,
         dash: bool = False) -> str:
    """A line with no head: a separator, a timeline, a link."""
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <line x1="{a[0]:g}" y1="{a[1]:g}" x2="{b[0]:g}" '
            f'y2="{b[1]:g}" stroke="{color}" stroke-width="{width:g}"{d}/>\n')


def arrow(a: Point, b: Point, color: str, marker: str,
          kind: str = "filled", dash: bool = False,
          width: float = 1.3) -> str:
    """An edge from `a` toward `b`, `b` being a point on the target's border.

    The line stops `TIP_GAP` plus the head's trim short of `b`, so the tip
    lands `TIP_GAP` from the border. `marker` names a marker from
    `markers()` whose color matches `color`.
    """
    ex, ey = shorten_line(a, b, TIP_GAP + HEADS[kind].trim)
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <line x1="{a[0]:g}" y1="{a[1]:g}" x2="{ex:.1f}" '
            f'y2="{ey:.1f}" stroke="{color}" stroke-width="{width:g}"{d} '
            f'marker-end="url(#{marker})"/>\n')


def cross(x: float, y: float, size: float = 6, color: str = RED) -> str:
    """An X, for a call or a reply that does not happen."""
    return (f'  <path d="M{x - size:g},{y - size:g} L{x + size:g},'
            f'{y + size:g} M{x - size:g},{y + size:g} L{x + size:g},'
            f'{y - size:g}" stroke="{color}" stroke-width="2" '
            f'fill="none"/>\n')


def markers(**defs: tuple[str, str]) -> str:
    """`<defs>` holding one marker per id: `ink=("filled", INK)`."""
    return ("  <defs>\n"
            + "".join(marker_def(mid, kind, color)
                      for mid, (kind, color) in defs.items())
            + "  </defs>\n")


def svg(width: float, height: float, title: str, defs: str,
        body: str) -> str:
    """The whole document: a viewBox with no size, the font, a <title>."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width:g} {height:g}"\n     {FONT}>\n'
            f"  <title>{esc(title)}</title>\n{defs}{body}</svg>\n")


def lint(source: str, stem: str) -> list[str]:
    """What `tip figures` would flag in this figure, or [] when clean."""
    from tools.figure_gallery import read_style
    return read_style(source, stem).flags


def png(source: Path, dest: Path) -> Path:
    """Rasterize `source` the way the EPUB does; the PNG's path."""
    from tools import build_epub
    tool = build_epub.find_svg_tool()
    if tool is None:
        raise SystemExit("no SVG rasterizer on PATH (see build_epub)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_epub.svg_command(tool, source, dest), check=True,
                   capture_output=True)
    return dest
