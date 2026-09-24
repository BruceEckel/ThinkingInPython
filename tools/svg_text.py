"""Find a figure's text that runs off the canvas or into other text.

Every figure sets its text in JetBrains Mono, a monospace font whose
characters all advance 0.6 em, so a `<text>` element's extent follows
from its position, `font-size`, `text-anchor`, and character count
without rendering anything. `text_boxes()` estimates each box;
`clipped()` names the text that crosses the `viewBox` edge, which a
browser and the EPUB's rasterizer both cut off; `collisions()` names
pairs of text whose boxes overlap. `make figures`
(`tools/figure_gallery.py`) fails on either.

The estimate is deliberately plain: the box runs from 0.75 em above the
baseline to 0.2 em below it, and whitespace collapses the way SVG's
default `xml:space` handling collapses it, so the `<tspan>` runs of one
line join into one string. No figure uses `transform` or `<g>`, and a
figure that starts to will need them handled here, or the boxes land in
the wrong place. Text does not collide with lines or shapes as far as
this module knows; a label lying across its own curve is still for the
eye, in the gallery's PNG view.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass

ADVANCE = 0.6
ASCENT = 0.75
DESCENT = 0.2
# Boxes may touch by this much before they count as overlapping, so a
# glyph's side bearing does not turn two adjacent labels into a finding.
SLACK = 1.0

TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
VIEWBOX_RE = re.compile(r"<svg\b[^>]*\bviewBox=\"([^\"]+)\"")


def _attr(attrs: str, name: str, default: str) -> str:
    m = re.search(rf'\b{name}="([^"]*)"', attrs)
    return m.group(1) if m else default


@dataclass(frozen=True)
class Box:
    text: str
    left: float
    top: float
    right: float
    bottom: float

    def overlaps(self, other: Box) -> bool:
        return (self.left < other.right - SLACK
                and other.left < self.right - SLACK
                and self.top < other.bottom - SLACK
                and other.top < self.bottom - SLACK)


def text_boxes(svg: str) -> list[Box]:
    """The estimated extent of every `<text>` element, in document order."""
    out = []
    for m in TEXT_RE.finditer(svg):
        attrs = m.group(1)
        text = html.unescape(" ".join(TAG_RE.sub("", m.group(2)).split()))
        if not text:
            continue
        x = float(_attr(attrs, "x", "0"))
        y = float(_attr(attrs, "y", "0"))
        size = float(_attr(attrs, "font-size", "16"))
        width = len(text) * ADVANCE * size
        left = {"middle": x - width / 2, "end": x - width}.get(
            _attr(attrs, "text-anchor", "start"), x)
        out.append(Box(text, left, y - ASCENT * size, left + width,
                       y + DESCENT * size))
    return out


def clipped(svg: str) -> list[str]:
    """The text whose box crosses an edge of the `viewBox`."""
    m = VIEWBOX_RE.search(svg)
    if m is None:
        return []
    x0, y0, w, h = (float(v) for v in m.group(1).replace(",", " ").split())
    return [b.text for b in text_boxes(svg)
            if b.left < x0 or b.right > x0 + w
            or b.top < y0 or b.bottom > y0 + h]


def collisions(svg: str) -> list[tuple[str, str]]:
    """Each pair of text elements whose boxes overlap."""
    boxes = text_boxes(svg)
    return [(a.text, b.text) for i, a in enumerate(boxes)
            for b in boxes[i + 1:] if a.overlaps(b)]
