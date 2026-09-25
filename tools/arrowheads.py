"""The book's arrowheads: four standard SVG markers and the geometry they need.

Every figure draws its arrowheads from this set, so they match across the
book, and each head is drawn in the color of the line that carries it,
so a figure with gray and red edges defines one marker per color.
`make figures` (`tools/figure_gallery.py`) fails on a `<marker>` that is
not one of the set (`marker_kinds()`) or that sits on a line of another
color (`mismatched_heads()`); `tools/coupling_panels.py` and
`tools/state_machine_figure.py` write their markers with `marker_def()`.

    filled   a swept head with a notched back: a call, a reference, a
             transition, anything that points
    hollow   an open triangle: inherits or satisfies (UML
             generalization and realization)
    open     a V with no back: a return, or a dashed "produces" edge
    diamond  an open diamond at the owning end: aggregation

Each head has a fixed size in user units (`markerUnits="userSpaceOnUse"`),
so a heavy edge and a thin one carry the same head. The two open shapes,
`hollow` and `diamond`, have no fill: a head filled with the paper color
to hide the line under it shows as a patch on the white page of the EPUB.
Instead the edge stops short of its target by the head's `trim`, and the
head reaches forward from the line's end to the target. That is why
`filled` and `hollow` anchor at their back (`refX` at the notch or the
base) instead of at the tip: the anchor sits where the line ends. The
same holds at the start of an edge for the diamond.

So an edge drawn to its target's border needs shortening by `trim` at
the marked end. `shorten_line()` does it for a `<line>`, and
`shorten_path_end()` and `shorten_path_start()` for path data of `M`,
`L`, `Q`, and `C` segments (a `<polyline>`'s points are `M` then `L`s),
cutting a curve at the arc length so the head stays on the curve.
Shortening by `trim` alone puts the tip on the border, so aim the edge a
few units short of it first: `tight_tips()` fails a tip closer than
`MIN_GAP` to the box or circle it points at.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Head:
    """One marker shape. `{c}` in `path` is the color."""
    width: float
    height: float
    ref_x: float
    path: str
    trim: float


HEADS: dict[str, Head] = {
    "filled": Head(18, 12, 5, (
        '<path d="M0.5,0.5 L17.4,6 L0.5,11.5 L5,6 Z" fill="{c}" '
        'stroke="{c}" stroke-width="0.8" stroke-linejoin="round"/>'), 12.4),
    "hollow": Head(18, 12, 1, (
        '<path d="M1,1 L17.4,6 L1,11 Z" fill="none" stroke="{c}" '
        'stroke-width="1.2" stroke-linejoin="round"/>'), 16.4),
    "open": Head(18, 12, 17, (
        '<path d="M1.5,1.5 L17,6 L1.5,10.5" fill="none" stroke="{c}" '
        'stroke-width="1.4" stroke-linecap="round" '
        'stroke-linejoin="round"/>'), 0),
    "diamond": Head(22, 12, 21, (
        '<path d="M1,6 L11,1 L21,6 L11,11 Z" fill="none" stroke="{c}" '
        'stroke-width="1.2" stroke-linejoin="round"/>'), 20),
}


def marker_def(marker_id: str, kind: str, color: str,
               indent: str = "    ") -> str:
    """The `<marker>` element for `kind`, drawn in `color`."""
    h = HEADS[kind]
    return (
        f'{indent}<marker id="{marker_id}" viewBox="0 0 {h.width:g} '
        f'{h.height:g}" refX="{h.ref_x:g}" refY="{h.height / 2:g}"\n'
        f'{indent}        markerWidth="{h.width:g}" '
        f'markerHeight="{h.height:g}" orient="auto" '
        f'markerUnits="userSpaceOnUse">\n'
        f'{indent}  {h.path.format(c=color)}\n'
        f"{indent}</marker>\n")


# --------------------------------------------------------------------------- #
# Checking a figure's markers
# --------------------------------------------------------------------------- #
MARKER_RE = re.compile(r"<marker\b[^>]*/>|<marker\b.*?</marker>",
                       re.DOTALL)
ID_RE = re.compile(r'\bid="([^"]+)"')
COLOR_ATTR_RE = re.compile(r'\b(fill|stroke)="(#[0-9a-fA-F]{3,6})"')


def _normal(text: str) -> str:
    """`text` with its id and colors blanked and its whitespace collapsed."""
    text = ID_RE.sub('id=""', text, count=1)
    text = COLOR_ATTR_RE.sub(r'\1="#"', text)
    return " ".join(text.replace(">", "> ").replace("<", " <").split())


STANDARD: dict[str, str] = {
    _normal(marker_def("x", kind, "#000")): kind for kind in HEADS}


def marker_kinds(svg: str) -> dict[str, str | None]:
    """Each marker's id and its standard kind, or None for a nonstandard one."""
    out: dict[str, str | None] = {}
    for m in MARKER_RE.finditer(svg):
        mid = ID_RE.search(m.group())
        out[mid.group(1) if mid else "?"] = STANDARD.get(_normal(m.group()))
    return out


# --------------------------------------------------------------------------- #
# Shortening an edge so its head reaches the target
# --------------------------------------------------------------------------- #
Point = tuple[float, float]


def _toward(a: Point, b: Point, d: float) -> Point:
    """The point `d` from `b` back toward `a`."""
    length = math.dist(a, b) or 1
    f = d / length
    return (b[0] + (a[0] - b[0]) * f, b[1] + (a[1] - b[1]) * f)


def shorten_line(a: Point, b: Point, d: float) -> Point:
    """`b` moved `d` toward `a`."""
    if math.dist(a, b) <= d:
        raise ValueError(f"segment {a}->{b} is shorter than {d}")
    return _toward(a, b, d)


def _bezier(pts: list[Point], t: float) -> Point:
    while len(pts) > 1:
        pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
               for p, q in zip(pts, pts[1:])]
    return pts[0]


def _split(pts: list[Point], t: float) -> list[Point]:
    """The control points of the curve from 0 to `t` (de Casteljau)."""
    left = [pts[0]]
    while len(pts) > 1:
        pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
               for p, q in zip(pts, pts[1:])]
        left.append(pts[0])
    return left


def shorten_curve(pts: list[Point], d: float) -> list[Point]:
    """The Bézier `pts` with arc length `d` cut off its end."""
    steps = 2000
    samples = [_bezier(pts, i / steps) for i in range(steps + 1)]
    run = 0.0
    for i in range(steps, 0, -1):
        step = math.dist(samples[i], samples[i - 1])
        if run + step >= d:
            # Interpolate within the step so the cut lands on `d`.
            return _split(pts, (i - (d - run) / step) / steps)
        run += step
    raise ValueError(f"curve {pts} is shorter than {d}")


def _fmt(v: float) -> str:
    return f"{v:.1f}".removesuffix(".0")


TOKEN_RE = re.compile(r"[MLQC]|-?\d+(?:\.\d+)?")


def _parse_path(d: str) -> list[tuple[str, list[Point]]]:
    tokens = TOKEN_RE.findall(d.replace(",", " "))
    segs: list[tuple[str, list[Point]]] = []
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        n = {"M": 1, "L": 1, "Q": 2, "C": 3}[cmd]
        nums = [float(x) for x in tokens[i + 1:i + 1 + 2 * n]]
        segs.append((cmd, list(zip(nums[::2], nums[1::2]))))
        i += 1 + 2 * n
    return segs


def _write_path(segs: list[tuple[str, list[Point]]]) -> str:
    return " ".join(
        cmd + " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in pts)
        for cmd, pts in segs)


def shorten_path_end(d: str, by: float) -> str:
    """Path data `d` with `by` cut off the end of its last segment."""
    segs = _parse_path(d)
    cmd, pts = segs[-1]
    start = segs[-2][1][-1]
    if cmd == "L":
        segs[-1] = (cmd, [shorten_line(start, pts[0], by)])
    else:
        segs[-1] = (cmd, shorten_curve([start, *pts], by)[1:])
    return _write_path(segs)


def reverse_path(d: str) -> str:
    """Path data `d` drawn from its end back to its start."""
    segs = _parse_path(d)
    out: list[tuple[str, list[Point]]] = [("M", [segs[-1][1][-1]])]
    for k in range(len(segs) - 1, 0, -1):
        cmd, pts = segs[k]
        start = segs[k - 1][1][-1]
        out.append((cmd, [*reversed(pts[:-1]), start]))
    return _write_path(out)


def shorten_path_start(d: str, by: float) -> str:
    """Path data `d` with `by` cut off the start of its first segment."""
    return reverse_path(shorten_path_end(reverse_path(d), by))


EDGE_RE = re.compile(r"<(?:line|polyline|path)\b[^>]*?/>", re.DOTALL)
USE_RE = re.compile(r'marker-(?:start|end)="url\(#([^)]+)\)"')
STROKE_RE = re.compile(r'\bstroke="([^"]+)"')


def marker_colors(svg: str) -> dict[str, str]:
    """Each marker's id and the stroke color its shape is drawn in."""
    out: dict[str, str] = {}
    for m in MARKER_RE.finditer(svg):
        mid, color = ID_RE.search(m.group()), STROKE_RE.search(m.group())
        if mid and color:
            out[mid.group(1)] = color.group(1).lower()
    return out


def mismatched_heads(svg: str) -> list[str]:
    """Each marker used on an edge drawn in a color other than its own.

    A head matches its line, so a gray edge carries a gray head and a
    red one a red head; a marker per color does it.
    """
    colors = marker_colors(svg)
    out: list[str] = []
    for m in EDGE_RE.finditer(svg):
        stroke = STROKE_RE.search(m.group())
        for mid in USE_RE.findall(m.group()):
            if (stroke and mid in colors
                    and colors[mid] != stroke.group(1).lower()
                    and mid not in out):
                out.append(mid)
    return out


# An edge must show this much line behind its head, or the head sits
# alone between two boxes and the edge's kind (dashed, heavy) is lost.
MIN_LINE = 8.0
LINE_RE = re.compile(r'<line\b[^>]*\bx1="([-\d.]+)"[^>]*\by1="([-\d.]+)"'
                     r'[^>]*\bx2="([-\d.]+)"[^>]*\by2="([-\d.]+)"[^>]*/>')


# A head's tip stops this far short of the box or circle it points at, or
# more; the book's figures leave 4. How far each head's tip reaches past
# the line's end (the shape's front minus refX): the diamond and the V
# anchor at their front.
MIN_GAP = 3.0
TIP_REACH: dict[str, float] = {
    "filled": 12.4, "hollow": 16.4, "open": 0.0, "diamond": 0.0}
END_RE = re.compile(r'marker-end="url\(#([^)]+)\)"')
TAG_RE = re.compile(r"<(\w+)")
NUM_ATTR_RE = re.compile(r'\b([\w-]+)="(-?[\d.]+)"')
POINTS_RE = re.compile(r'\bpoints="([^"]*)"')
D_RE = re.compile(r'\bd="([^"]*)"')
SHAPE_RE = re.compile(r"<(?:rect|circle)\b[^>]*>", re.DOTALL)
VIEWBOX_W_RE = re.compile(
    r'<svg\b[^>]*\bviewBox="[-\d.]+ [-\d.]+ ([\d.]+)', re.DOTALL)


def _edge_points(edge: str) -> list[Point]:
    tag = TAG_RE.match(edge)
    kind = tag.group(1) if tag else ""
    nums = dict(NUM_ATTR_RE.findall(edge))
    if kind == "line":
        return [(float(nums["x1"]), float(nums["y1"])),
                (float(nums["x2"]), float(nums["y2"]))]
    if kind == "polyline":
        m = POINTS_RE.search(edge)
        vals = [float(v) for v in re.findall(r"-?[\d.]+", m.group(1))] if m else []
        return list(zip(vals[::2], vals[1::2]))
    m = D_RE.search(edge)
    return [p for _, pts in _parse_path(m.group(1)) for p in pts] if m else []


def _shapes(svg: str) -> list[tuple[str, tuple[float, ...]]]:
    """Each box and circle an edge could point at, skipping a background
    rect as wide as the viewBox."""
    m = VIEWBOX_W_RE.search(svg)
    width = float(m.group(1)) if m else math.inf
    out: list[tuple[str, tuple[float, ...]]] = []
    for s in SHAPE_RE.finditer(svg):
        a = {k: float(v) for k, v in NUM_ATTR_RE.findall(s.group())}
        if s.group().startswith("<rect"):
            w, h = a.get("width", 0), a.get("height", 0)
            if w < width - 1:
                out.append(("rect", (a.get("x", 0), a.get("y", 0), w, h)))
        else:
            out.append(("circle", (a.get("cx", 0), a.get("cy", 0),
                                   a.get("r", 0))))
    return out


def _gap(p: Point, kind: str, s: tuple[float, ...]) -> float:
    """From `p` to the shape's border, negative inside it."""
    if kind == "circle":
        return math.dist(p, (s[0], s[1])) - s[2]
    x, y, w, h = s
    dx = max(x - p[0], 0, p[0] - (x + w))
    dy = max(y - p[1], 0, p[1] - (y + h))
    if dx or dy:
        return math.hypot(dx, dy)
    return -min(p[0] - x, x + w - p[0], p[1] - y, y + h - p[1])


def tight_tips(svg: str, min_gap: float = MIN_GAP) -> list[str]:
    """Each end-marker tip closer than `min_gap` to the nearest box or
    circle, as `tip x,y: gap G`.

    The tip is the line's end plus the head's `TIP_REACH` along the last
    segment. An edge drawn to its target's border and then trimmed by
    `trim` puts the tip back on the border; the check catches that.
    Start markers are not checked, since a start diamond sits on its
    owner.
    """
    kinds = marker_kinds(svg)
    shapes = _shapes(svg)
    out: list[str] = []
    for m in EDGE_RE.finditer(svg):
        use = END_RE.search(m.group())
        kind = kinds.get(use.group(1)) if use else None
        if kind is None or not shapes:
            continue
        pts = _edge_points(m.group())
        if len(pts) < 2:
            continue
        end = pts[-1]
        back = next((p for p in reversed(pts) if p != end), end)
        length = math.dist(back, end) or 1
        reach = TIP_REACH[kind] / length
        tip = (end[0] + (end[0] - back[0]) * reach,
               end[1] + (end[1] - back[1]) * reach)
        gap = min(_gap(tip, k, s) for k, s in shapes)
        if gap < min_gap:
            out.append(f"tip {tip[0]:.1f},{tip[1]:.1f}: "
                       f"gap {round(gap, 1) + 0.0:.1f}")  # no -0.0
    return out


def short_edges(svg: str) -> list[str]:
    """Each marked `<line>` shorter than `MIN_LINE`, as `x1,y1 -> x2,y2`."""
    out = []
    for m in LINE_RE.finditer(svg):
        if not USE_RE.search(m.group()):
            continue
        x1, y1, x2, y2 = (float(v) for v in m.groups())
        if math.dist((x1, y1), (x2, y2)) < MIN_LINE:
            out.append(f"{x1:g},{y1:g} -> {x2:g},{y2:g}")
    return out
