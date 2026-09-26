"""Generate the coupling-notation panel at the top of each pattern chapter.

Chapter 21's Coupling section draws six GoF patterns in one
notation: a heavy edge names a concrete class, a thin edge names an
interface, a dashed edge with a hollow head satisfies one, and the red
box is the part the pattern protects from change. This script draws
one such panel per pattern chapter, 23 through 36, into
`resources/images/coupling_NN.svg`, so the chapters share a figure the
way they share a question: which edge does the pattern move, and where
does it put it?

Every panel is a `Panel` in `PANELS`, keyed by chapter number: its
nodes, its edges, and the "heavy edges" note under the drawing. The
names in a panel are the names in that chapter's listings, so a listing
rename means editing the spec here and regenerating, never editing an
SVG by hand. Chapter 21's `coupling_gallery.svg`, its six patterns in
the same notation, is generated here too, from the `Cell` specs in
`GALLERY`:

    uv run python -m tools.coupling_panels            # write all
    uv run python -m tools.coupling_panels --check    # report drift
    uv run python -m tools.coupling_panels --png      # rasterize to look

`--check` regenerates in memory and exits nonzero if any committed SVG
differs, the way `extract_examples`'s check mode works for `Examples/`;
`make coupling-panels` runs it in the gate. Every run also checks each
spec's edges (`edge_problems()`): a head's tip must sit `TIP_PAD` from
its target's drawn outline, rounded corners included, give or take
`TIP_SLACK`, and no edge may cross a box other than its own two. `--png` rasterizes every
`resources/images/coupling_*.svg` (the panels and chapter 21's figures)
into `build/coupling/` with the same rasterizer and width the EPUB
uses, since text that fits in a browser can collide once rasterized;
`make coupling-panels-png` is the one-command form. It needs one of
`build_epub.SVG_TOOLS` on PATH and says so when none is.

The visual vocabulary matches the hand-authored figures: a `viewBox`
with no width or height, JetBrains Mono, the cover palette from
`make_cover.py`, and a `<title>` for screen readers. The canvas is 700
wide like the other figures, so the site renders every figure at the
same scale; the drawing sits on the left and a legend on the right,
listing only the edge kinds the drawing uses, and the red box only when
a node is marked.
"""
from __future__ import annotations
import argparse
import math
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools.arrowheads import HEADS, marker_def, shorten_curve

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "resources" / "images"

INK = "#1a1612"
BOX = "#c8bfb0"
MUTED = "#7a6e62"
MARK = "#8b1a1a"
FONT = "font-family=\"'JetBrains Mono', Consolas, monospace\""

WIDTH = 700
HEIGHT = 236


@dataclass(frozen=True)
class Node:
    """A box. `kind` is concrete, interface, mark (red), or absent (dashed)."""
    name: str
    x: float
    y: float
    w: float = 96
    h: float = 38
    kind: str = "concrete"
    size: float = 12
    sub: str | None = None

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def rx(self) -> float:
        return 12 if self.kind == "interface" else 4

    def distance(self, p: tuple[float, float]) -> float:
        """Signed distance from `p` to the drawn outline, rounded
        corners included: positive outside, negative inside."""
        qx = abs(p[0] - self.cx) - (self.w / 2 - self.rx)
        qy = abs(p[1] - self.cy) - (self.h / 2 - self.rx)
        outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
        return outside + min(max(qx, qy), 0.0) - self.rx

    def reach(self, x1: float, y1: float, x2: float, y2: float,
              pad: float) -> tuple[float, float]:
        """The first point on the ray from (x1, y1) through (x2, y2)
        that lies `pad` from the drawn outline, or (x2, y2) if the ray
        passes wide of it."""
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        dx, dy = dx / length, dy / length
        step, t = 0.5, 0.0
        limit = length + self.w + self.h
        while t < limit:
            if self.distance((x1 + dx * t, y1 + dy * t)) <= pad:
                lo, hi = t - step, t
                for _ in range(30):
                    mid = (lo + hi) / 2
                    if self.distance((x1 + dx * mid, y1 + dy * mid)) <= pad:
                        hi = mid
                    else:
                        lo = mid
                return x1 + dx * hi, y1 + dy * hi
            t += step
        return x2, y2

    def edge_point(self, tx: float, ty: float, pad: float = 0.0) -> tuple[float, float]:
        """The point on this box's border toward (tx, ty)."""
        dx, dy = tx - self.cx, ty - self.cy
        if dx == 0 and dy == 0:
            return self.cx, self.cy
        hw, hh = self.w / 2 + pad, self.h / 2 + pad
        sx = hw / abs(dx) if dx else math.inf
        sy = hh / abs(dy) if dy else math.inf
        s = min(sx, sy)
        return self.cx + dx * s, self.cy + dy * s

    def entry(self, x1: float, y1: float, x2: float, y2: float,
              pad: float = 0.0) -> tuple[float, float]:
        """Where the line from (x1, y1) through (x2, y2) first meets this
        box grown by `pad` on every side."""
        t_in = -math.inf
        for p0, d, lo, hi in (
                (x1, x2 - x1, self.cx - self.w / 2 - pad,
                 self.cx + self.w / 2 + pad),
                (y1, y2 - y1, self.cy - self.h / 2 - pad,
                 self.cy + self.h / 2 + pad)):
            if d:
                t_in = max(t_in, min((lo - p0) / d, (hi - p0) / d))
        return x1 + (x2 - x1) * t_in, y1 + (y2 - y1) * t_in

    def svg(self) -> str:
        rx = self.rx
        stroke, width, dash, fill_text, weight = BOX, 1.3, "", INK, ""
        match self.kind:
            case "mark":
                stroke, width, weight = MARK, 1.6, ' font-weight="bold"'
            case "interface":
                stroke, fill_text = MUTED, MUTED
            case "absent":
                dash, fill_text = ' stroke-dasharray="4,3"', MUTED
        out = (f'  <rect x="{self.x}" y="{self.y}" width="{self.w}" '
               f'height="{self.h}" fill="none" stroke="{stroke}" '
               f'stroke-width="{width}" rx="{rx}"{dash}/>\n')
        ty = self.cy + self.size * 0.35
        if self.sub:
            ty -= 7
        out += (f'  <text x="{self.cx}" y="{ty:.1f}" font-size="{self.size}"'
                f'{weight} fill="{fill_text}" text-anchor="middle">'
                f'{self.name}</text>\n')
        if self.sub:
            out += (f'  <text x="{self.cx}" y="{ty + 15:.1f}" '
                    f'font-size="{self.size - 3}" fill="{MUTED}" '
                    f'text-anchor="middle">{self.sub}</text>\n')
        return out


@dataclass(frozen=True)
class Edge:
    """`kind` is heavy, thin, realize, inherit, or checked. `corner`
    aims the edge at the target's corner nearest the source."""
    a: str
    b: str
    kind: str = "thin"
    label: str | None = None
    dx: float = 0
    dy: float = -6
    shift: float = 0
    bend: float = 0
    corner: bool = False


STYLES: dict[str, tuple[str, float, str, str]] = {
    "heavy": (INK, 2.8, "", "solid"),
    "thin": (INK, 1.3, "", "solid"),
    "realize": (MUTED, 1.2, ' stroke-dasharray="5,4"', "hollow-muted"),
    "inherit": (INK, 1.3, "", "hollow"),
    "checked": (MUTED, 1.2, ' stroke-dasharray="1.5,3"', "hollow-muted"),
}

# Each marker a style names: its shape in tools/arrowheads.py and its
# color, which matches the line's.
MARKERS: dict[str, tuple[str, str]] = {
    "solid": ("filled", INK),
    "hollow": ("hollow", INK),
    "hollow-muted": ("hollow", MUTED),
}


Point = tuple[float, float]


def edge_points(e: Edge, nodes: dict[str, Node]) -> list[Point]:
    """The edge's start, its curve's control point if it bends, and the
    head's tip, before the line is shortened for the head."""
    a, b = nodes[e.a], nodes[e.b]
    if e.corner:
        # Aim at the target's corner nearest the source, on the padded
        # side facing the source's longer run and inset by the corner's
        # radius, so the head meets a straight stretch of the border.
        sx = math.copysign(1, a.cx - b.cx)
        sy = math.copysign(1, a.cy - b.cy)
        if abs(a.cy - b.cy) >= abs(a.cx - b.cx):
            x2 = b.cx + sx * (b.w / 2 - b.rx)
            y2 = b.cy + sy * (b.h / 2 + 4)
        else:
            x2 = b.cx + sx * (b.w / 2 + 4)
            y2 = b.cy + sy * (b.h / 2 - b.rx)
        x1, y1 = a.edge_point(x2, y2, 2)
    else:
        x1, y1 = a.edge_point(b.cx, b.cy, 2)
        x2, y2 = b.edge_point(a.cx, a.cy, 4)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    if e.shift:
        x1, y1 = x1 + nx * e.shift, y1 + ny * e.shift
        x2, y2 = x2 + nx * e.shift, y2 + ny * e.shift
        # Shifted sideways, a slanted edge's end slides toward the box;
        # aim it at the padded border again.
        x2, y2 = b.entry(x1, y1, x2, y2, 4)
    # Aimed at the grown rectangle, a tip near a rounded corner stops
    # short of it; slide the tip to 4 from the outline the box draws.
    x2, y2 = b.reach(x1, y1, x2, y2, TIP_PAD)
    if e.bend:
        return [(x1, y1), ((x1 + x2) / 2 + nx * e.bend,
                           (y1 + y2) / 2 + ny * e.bend), (x2, y2)]
    return [(x1, y1), (x2, y2)]


def edge_svg(e: Edge, nodes: dict[str, Node], pid: str) -> str:
    pts = edge_points(e, nodes)
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    stroke, width, dash, head = STYLES[e.kind]
    marker = f'marker-end="url(#{pid}-{head})"'
    # The line stops short by the head's length, and the head reaches the box.
    trim = HEADS[MARKERS[head][0]].trim
    if e.bend:
        lx = (x1 + x2) / 2 - dy / length * e.bend / 2
        ly = (y1 + y2) / 2 + dx / length * e.bend / 2
        _, (mx, my), (x2, y2) = shorten_curve(pts, trim)
        out = (f'  <path d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} '
               f'{x2:.1f},{y2:.1f}" fill="none" stroke="{stroke}" '
               f'stroke-width="{width}"{dash} {marker}/>\n')
    else:
        lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
        x2, y2 = x2 - dx / length * trim, y2 - dy / length * trim
        out = (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
               f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"'
               f'{dash} {marker}/>\n')
    if e.label:
        out += (f'  <text x="{lx + e.dx:.1f}" y="{ly + e.dy:.1f}" '
                f'font-size="10.5" fill="{MARK}" text-anchor="middle">'
                f'{e.label}</text>\n')
    return out


def text(x: float, y: float, s: str, size: float = 12, fill: str = INK,
         anchor: str = "start", bold: bool = False, italic: bool = False) -> str:
    w = ' font-weight="bold"' if bold else ""
    st = ' font-style="italic"' if italic else ""
    return (f'  <text x="{x}" y="{y}" font-size="{size}"{w}{st} fill="{fill}" '
            f'text-anchor="{anchor}">{s}</text>\n')


def defs(pid: str) -> str:
    return ("  <defs>\n"
            + "".join(marker_def(f"{pid}-{name}", kind, color)
                      for name, (kind, color) in MARKERS.items())
            + "  </defs>\n")


LEGEND_ROWS: tuple[tuple[str, str], ...] = (
    ("heavy", "names a concrete class"),
    ("thin", "names an interface"),
    ("realize", "satisfies it"),
    ("inherit", "inherits its internals"),
)


def legend(x: float, y: float, pid: str, kinds: set[str],
           marked: bool) -> str:
    """A sample of each edge kind in `kinds`, and the red box if a node
    is `marked`, stacked for the panel's right side. A legend lists only
    what its drawing uses."""
    rows = [(k, label) for k, label in LEGEND_ROWS if k in kinds]
    out = ""
    for i, (kind, label) in enumerate(rows):
        yy = y + i * 20
        stroke, width, dash, head = STYLES[kind]
        end = x + 30 - HEADS[MARKERS[head][0]].trim
        out += (f'  <line class="legend" x1="{x}" y1="{yy}" '
                f'x2="{end:g}" y2="{yy}" '
                f'stroke="{stroke}" stroke-width="{width}"{dash} '
                f'marker-end="url(#{pid}-{head})"/>\n')
        out += text(x + 38, yy + 4, label, 10.5, MUTED)
    if marked:
        yy = y + len(rows) * 20
        out += (f'  <rect x="{x + 2}" y="{yy - 8}" width="26" height="16" '
                f'fill="none" stroke="{MARK}" stroke-width="1.6" rx="3"/>\n')
        out += text(x + 38, yy + 4, "does not change", 10.5, MUTED)
    return out


@dataclass(frozen=True)
class Panel:
    title: str
    alt: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    note: str = ""
    height: float = HEIGHT
    extra: tuple[str, ...] = field(default_factory=tuple)

    def svg(self, pid: str) -> str:
        nodes = {n.name: n for n in self.nodes}
        b = text(10, 20, self.title, 13, INK, bold=True, italic=True)
        b += (f'  <line x1="10" y1="27" x2="440" y2="27" stroke="{BOX}" '
              f'stroke-width="0.8"/>\n')
        for n in self.nodes:
            b += n.svg()
        for e in self.edges:
            b += edge_svg(e, nodes, pid)
        for s in self.extra:
            b += s
        if self.note:
            b += text(10, self.height - 12, self.note, 10.5, MUTED)
        b += legend(480, 60, pid, {e.kind for e in self.edges},
                    any(n.kind == "mark" for n in self.nodes))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {WIDTH} {self.height}"\n     {FONT}>\n'
                f'  <title>{self.alt}</title>\n' + defs(pid) + b + '</svg>\n')


# The per-chapter specs. Columns C1..C3 and rows R1..R3 are the usual
# positions; a panel moves a box when its edges would otherwise cross.
C1, C2, C3 = 20, 172, 324
R1, R2, R3 = 48, 108, 168


def divider(x: float, bottom: float = 212) -> str:
    return (f'  <line x1="{x}" y1="40" x2="{x}" y2="{bottom:g}" stroke="{BOX}" '
            f'stroke-width="1" stroke-dasharray="4,4"/>\n')


PANELS: dict[int, Panel] = {
    23: Panel(
        "Iterator",
        "total() names only Iterable, and a list, a generator, and "
        "Countdown satisfy it without naming it",
        (Node("total()", C1, R2, kind="mark"),
         Node("Iterable[int]", C2 - 6, R2, w=118, kind="interface"),
         Node("list", C3, R1, w=90),
         Node("fibonacci()", C3, R2, w=100),
         Node("Countdown", C3, R3, w=100)),
        (Edge("total()", "Iterable[int]", "thin"),
         Edge("list", "Iterable[int]", "realize", corner=True),
         Edge("fibonacci()", "Iterable[int]", "realize"),
         Edge("Countdown", "Iterable[int]", "realize", corner=True)),
        "heavy edges: 0 in total(). Only the demo that hands it a source "
        "names that source.",
    ),
    24: Panel(
        "Singleton",
        "Every importer names config.py by its module name, and the import "
        "system hands each one the same instance",
        (Node("config.py", C2 + 30, R2, w=170, kind="mark",
              sub="one instance per interpreter"),
         Node("module_singleton.py", C1, R1, w=160),
         Node("shared_config.py", C1, R3, w=160)),
        (Edge("module_singleton.py", "config.py", "heavy", label="import",
              dx=10, dy=-10, corner=True),
         Edge("shared_config.py", "config.py", "heavy", label="import",
              dx=10, dy=18, corner=True)),
        "heavy edges: one per importer, all pointing at a name that does not "
        "change.",
    ),
    25: Panel(
        "Template Method",
        "MyApp inherits ApplicationFramework's internals, while "
        "run_framework() names only the Step signature its two functions satisfy",
        (Node("ApplicationFramework", C1, 44, w=180, kind="mark", sub="run()"),
         Node("MyApp", C1, 192, w=180),
         Node("run_framework()", 256, 44, w=160, kind="mark"),
         Node("Step", 271, 118, w=130, kind="interface",
              sub="Callable[[], None]"),
         Node("two lambdas", 256, 192, w=160)),
        (Edge("MyApp", "ApplicationFramework", "inherit",
              label="overrides two steps", dx=70, dy=4),
         Edge("run_framework()", "Step", "thin"),
         Edge("two lambdas", "Step", "realize")),
        "left: the inherit edge is the widest rung; right: the same algorithm "
        "with one thin edge.",
        height=262,
        extra=(divider(228, 236),),
    ),
    26: Panel(
        "Surrogate",
        "Proxy and Complete both inherit Service, Proxy holds one, and only "
        "the caller names either class",
        (Node("Proxy", C1, R1, w=90, kind="mark"),
         Node("Service", C2 + 10, R1, kind="interface", sub="ABC"),
         Node("Complete", C3 + 10, R1, w=96),
         Node("caller", C2 + 10, R3, w=96)),
        (Edge("Proxy", "Service", "inherit", shift=-8),
         Edge("Proxy", "Service", "thin", shift=8, label="holds", dy=18),
         Edge("Complete", "Service", "inherit"),
         Edge("caller", "Proxy", "heavy", corner=True),
         Edge("caller", "Complete", "heavy", corner=True)),
        "heavy edges: 2, both in the caller that builds the pair. Proxy "
        "names only Service.",
    ),
    27: Panel(
        "Factory",
        "The caller names make(), and make() is the one place that names "
        "Shape, Circle, and Square",
        (Node("caller", C1, R1, w=80, kind="mark"),
         Node("make()", C2, R1, w=90),
         Node("Shape", C1, R3, w=80, kind="interface"),
         Node("Circle", C2 + 5, R3, w=80),
         Node("Square", C3, R3, w=80)),
        (Edge("caller", "make()", "heavy"),
         Edge("make()", "Shape", "thin", label="returns", dx=-30, dy=-4,
              corner=True),
         Edge("make()", "Circle", "heavy", label="SHAPES", dx=30, dy=4),
         Edge("make()", "Square", "heavy", corner=True),
         Edge("Circle", "Shape", "inherit"),
         Edge("Square", "Shape", "inherit", bend=-46)),
        "heavy edges: 3. The two that name a shape sit in one table, and "
        "self-registration removes them.",
    ),
    28: Panel(
        "Function Objects",
        "The list that builds macro names three functions, and the loop that "
        "runs it names only the Command signature",
        (Node("macro", C1, R1, w=100, sub="list[Command]"),
         Node("no_more()", C2, R1, w=96),
         Node("ceased()", C2, R2, w=96),
         Node("fjords()", C2, R3, w=96),
         Node("Command", C3, R2, w=120, kind="interface",
              sub="Callable[[], None]"),
         Node("for command in macro", C3 - 20, R3 + 14, w=160, kind="mark",
              sub="command()")),
        (Edge("macro", "no_more()", "heavy"),
         Edge("macro", "ceased()", "heavy"),
         Edge("macro", "fjords()", "heavy", corner=True),
         Edge("no_more()", "Command", "realize"),
         Edge("ceased()", "Command", "realize"),
         Edge("fjords()", "Command", "realize"),
         Edge("for command in macro", "Command", "thin")),
        "heavy edges: 3, all in the line that builds the list. The loop "
        "names none.",
        height=HEIGHT + 10,
    ),
    29: Panel(
        "Adapter",
        "WhatIUse names WhatIWant, and ProxyAdapter is the one class that "
        "names both WhatIWant and WhatIHave",
        (Node("WhatIUse", C1, R1, kind="mark"),
         Node("WhatIWant", C2 + 5, R1, w=100, kind="interface"),
         Node("ProxyAdapter", C2, R3, w=110),
         Node("WhatIHave", C3 + 6, R3, w=96)),
        (Edge("WhatIUse", "WhatIWant", "thin"),
         Edge("ProxyAdapter", "WhatIWant", "inherit"),
         Edge("ProxyAdapter", "WhatIHave", "heavy")),
        "heavy edges: 1 among the classes, inside ProxyAdapter. The demo "
        "names what it wires.",
    ),
    30: Panel(
        "Observer",
        "Subject names only Observer, Thermometer inherits Subject, and "
        "Display satisfies Observer while naming Subject in its signature",
        (Node("Subject", C1, R1, w=110, kind="mark"),
         Node("Observer", C2 + 24, R1, w=100, kind="interface"),
         Node("Thermometer", C1, R3, w=110),
         Node("Display", C2 + 24, R3, w=100)),
        (Edge("Subject", "Observer", "thin", label="notify", dy=-8),
         Edge("Thermometer", "Subject", "inherit"),
         Edge("Display", "Observer", "realize"),
         Edge("Display", "Subject", "heavy", label="update()", dx=-36,
              dy=14, corner=True)),
        "heavy edges: 1, in Display's signature. The subject side names no "
        "observer class.",
    ),
    31: Panel(
        "State Machine",
        "StateMachine names only State, each state satisfies it, and "
        "MouseTrap and its states name each other",
        (Node("StateMachine", C1, R1, w=110, kind="mark"),
         Node("State", C2 + 10, R1, w=90, kind="interface"),
         Node("MouseTrap", C1, R3, w=110),
         Node("Waiting", C3, 92, w=90),
         Node("Luring", C3, 170, w=90)),
        (Edge("StateMachine", "State", "thin"),
         Edge("MouseTrap", "StateMachine", "inherit"),
         Edge("Waiting", "State", "realize", corner=True),
         Edge("Luring", "State", "realize", bend=-44),
         Edge("Waiting", "MouseTrap", "heavy", shift=5, label="next",
              dx=-30, dy=-10),
         Edge("MouseTrap", "Waiting", "heavy", shift=5, label="builds",
              dx=30, dy=18),
         Edge("Luring", "MouseTrap", "heavy", shift=5),
         Edge("MouseTrap", "Luring", "heavy", shift=5)),
        "heavy edges: two per state, a cycle. The table form moves the "
        "next-state choice into a dict per state.",
    ),
    32: Panel(
        "Multiple Dispatching",
        "Paper, Scissors, and Rock each define an eval method for every item "
        "and call one through Any, so a fourth item edits all three",
        (Node("Paper", C1, R1, w=90),
         Node("Scissors", C1, R3, w=90),
         Node("Rock", C3 + 10, R2, w=90),
         Node("eval_*()", C2 - 4, R2, w=118, kind="absent",
              sub="undeclared")),
        (Edge("Paper", "eval_*()", "thin", shift=6),
         Edge("Paper", "eval_*()", "realize", shift=-6),
         Edge("Scissors", "eval_*()", "thin", shift=-6),
         Edge("Scissors", "eval_*()", "realize", shift=6),
         Edge("Rock", "eval_*()", "thin", shift=6),
         Edge("Rock", "eval_*()", "realize", shift=-6)),
        "heavy edges: 0. The coupling is in the method names eval_paper(), "
        "eval_scissors(), and eval_rock().",
    ),
    33: Panel(
        "Visitor",
        "Flower names only Visitor and Pollinator names only Flower, so no "
        "visitor names a concrete flower",
        (Node("Flower", C1 + 10, 44, w=110, kind="mark", sub="cannot change"),
         Node("Visitor", C3, 44, w=96, kind="interface"),
         Node("Chrysanthemum", C1, 196, w=130),
         Node("Pollinator", C3, 120, w=96),
         Node("Bee", C3, 196, w=96)),
        (Edge("Flower", "Visitor", "thin", label="pollinate, eat", dy=-8),
         Edge("Pollinator", "Flower", "thin", label="visit", dx=-24, dy=14,
              corner=True),
         Edge("Chrysanthemum", "Flower", "inherit"),
         Edge("Pollinator", "Visitor", "inherit"),
         Edge("Bee", "Pollinator", "inherit")),
        "heavy edges: 0. Each side names the other's base, and the second "
        "dispatch is a method on Flower.",
        height=266,
    ),
    34: Panel(
        "Composite",
        "disk_usage() and walk() each name both node types, and Directory "
        "names only the Node union",
        (Node("disk_usage()", C1, R1, w=110),
         Node("walk()", C1, R2, w=96),
         Node("File", C3, R1, w=90),
         Node("Directory", C3, R2, w=96),
         Node("Node", C2 + 10, R3 + 6, w=90, kind="interface",
              sub="File | Directory")),
        (Edge("disk_usage()", "File", "heavy"),
         Edge("disk_usage()", "Directory", "heavy", corner=True),
         Edge("walk()", "File", "heavy", corner=True),
         Edge("walk()", "Directory", "heavy"),
         Edge("disk_usage()", "Node", "thin"),
         Edge("walk()", "Node", "thin", corner=True),
         Edge("Directory", "Node", "thin", label="entries", dx=38, dy=10,
              corner=True)),
        "heavy edges: two per function, on purpose: a new node type must "
        "reach every match, and ty lists them.",
    ),
    35: Panel(
        "Flyweight",
        "parse_map() names tile(), to_symbol(), and Tile, and tile() is the "
        "one place that constructs a Tile",
        (Node("parse_map()", C1, R2, w=110, kind="mark"),
         Node("tile()", C2 + 10, R1, w=90, sub="@cache"),
         Node("Tile", C3 + 10, R1, w=80),
         Node("to_symbol()", C2 + 10, R3, w=100),
         Node("SPECS", C3 + 10, R3, w=80)),
        (Edge("parse_map()", "tile()", "heavy", corner=True),
         Edge("parse_map()", "to_symbol()", "heavy", corner=True),
         Edge("parse_map()", "Tile", "heavy", bend=30, label="returns",
              dx=0, dy=16),
         Edge("tile()", "Tile", "heavy", label="constructs", dy=-10),
         Edge("tile()", "SPECS", "heavy", corner=True),
         Edge("to_symbol()", "SPECS", "heavy")),
        "heavy edges: 6, and only tile() constructs, so every caller shares "
        "its instances.",
    ),
    36: Panel(
        "Memento",
        "Sketch names Memento, and History names only a type parameter, so it "
        "holds a Memento without reading it",
        (Node("Sketch", C1, R1, w=100, kind="mark"),
         Node("Memento", C3, R1, w=96),
         Node("History[S]", C1, R3, w=110),
         Node("S", C3, R3, w=96, kind="interface", sub="any value")),
        (Edge("Sketch", "Memento", "heavy", label="save, restore", dy=18),
         Edge("History[S]", "S", "thin"),
         Edge("Memento", "S", "realize")),
        height=218,
    ),
}


# The Markdown caption under each figure: the panel's alt text with code
# spans on its identifiers. The SVG <title> stays plain, since a screen
# reader has no use for backticks, and the pattern-name gate reads a bare
# "Proxy" or "Observer" in a caption as an unitalicized pattern name.
CAPTIONS: dict[int, str] = {
    23: "`total()` names only `Iterable`, and a `list`, a generator, and "
        "`Countdown` satisfy it without naming it",
    24: "Every importer names `config.py` by its module name, and the import "
        "system hands each one the same instance",
    25: "`MyApp` inherits `ApplicationFramework`'s internals, while "
        "`run_framework()` names only the `Step` signature its two functions "
        "satisfy",
    26: "`Proxy` and `Complete` both inherit `Service`, `Proxy` holds one, "
        "and only the caller names either class",
    27: "The caller names `make()`, and `make()` is the one place that names "
        "`Shape`, `Circle`, and `Square`",
    28: "The list that builds `macro` names three functions, and the loop "
        "that runs it names only the `Command` signature",
    29: "`WhatIUse` names `WhatIWant`, and `ProxyAdapter` is the one class "
        "that names both `WhatIWant` and `WhatIHave`",
    30: "`Subject` names only `Observer`, `Thermometer` inherits `Subject`, "
        "and `Display` satisfies `Observer` while naming `Subject` in its "
        "signature",
    31: "`StateMachine` names only `State`, each state satisfies it, and "
        "`MouseTrap` and its states name each other",
    32: "`Paper`, `Scissors`, and `Rock` each define an eval method for every "
        "item and call one through `Any`, so a fourth item edits all three",
    33: "`Flower` names only `Visitor` and `Pollinator` names only `Flower`, "
        "so no visitor names a concrete flower",
    34: "`disk_usage()` and `walk()` each name both node types, and "
        "`Directory` names only the `Node` union",
    35: "`parse_map()` names `tile()`, `to_symbol()`, and `Tile`, and "
        "`tile()` is the one place that constructs a `Tile`",
    36: "`Sketch` names `Memento`, and `History` names only a type parameter, "
        "so it holds a `Memento` without reading it",
}


@dataclass(frozen=True)
class Cell:
    """One pattern in chapter 21's gallery, at column `col` and row `row`."""
    title: str
    col: int
    row: int
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    note: str


# Chapter 21's coupling_gallery.svg: six patterns in the panel notation,
# three to a row. Nodes carry absolute coordinates; a cell is GALLERY_W
# wide and GALLERY_H tall, and stacked boxes sit 36 apart so every edge
# shows a line behind its head.
GALLERY_W, GALLERY_H = 250, 270
GALLERY_TITLE = ("Six patterns drawn only as coupling: which part names a "
                 "concrete class, which names an interface, and which "
                 "satisfies one")
GALLERY: tuple[Cell, ...] = (
    Cell("Strategy", 0, 0,
         (Node("Context", 30, 64, w=84, h=40, kind="mark"),
          Node("Strategy", 150, 64, w=96, h=40, kind="interface"),
          Node("Max", 100, 164, w=70, h=34, size=11),
          Node("Sum", 178, 164, w=70, h=34, size=11)),
         (Edge("Context", "Strategy", "thin"),
          Edge("Max", "Strategy", "realize"),
          Edge("Sum", "Strategy", "realize")),
         "heavy edges: 0"),
    Cell("Observer", 1, 0,
         (Node("Subject", 272, 64, w=90, h=40, kind="mark"),
          Node("Observer", 412, 64, w=90, h=40, kind="interface"),
          Node("Display", 412, 164, w=90, h=34, size=11)),
         (Edge("Subject", "Observer", "thin", label="notify"),
          Edge("Display", "Observer", "realize"),
          Edge("Display", "Subject", "heavy", label="attach",
               dx=-30, dy=12, corner=True)),
         "heavy edges: 1, toward the stable part"),
    Cell("Factory Method", 2, 0,
         (Node("Client", 530, 50, w=80, h=36, kind="mark"),
          Node("Creator", 660, 50, w=86, h=36, kind="interface", size=11),
          Node("Product", 530, 122, w=80, h=36, kind="interface", size=11),
          Node("PdfCreator", 660, 122, w=86, h=36, size=10.5),
          Node("PdfProduct", 530, 194, w=80, h=36, size=10.5)),
         (Edge("Client", "Creator", "thin"),
          Edge("Client", "Product", "thin"),
          Edge("PdfCreator", "Creator", "realize"),
          Edge("PdfProduct", "Product", "realize"),
          Edge("PdfCreator", "PdfProduct", "heavy", label="creates",
               dx=12, dy=18, corner=True)),
         "heavy edges: 1, moved out of Client"),
    Cell("Adapter", 0, 1,
         (Node("Client", 30, 320, w=80, h=40, kind="mark"),
          Node("Target", 150, 320, w=96, h=40, kind="interface"),
          Node("Adapter", 150, 396, w=96, h=34, size=11),
          Node("Adaptee", 150, 466, w=96, h=34, size=11)),
         (Edge("Client", "Target", "thin"),
          Edge("Adapter", "Target", "realize"),
          Edge("Adapter", "Adaptee", "heavy")),
         "heavy edges: 1, inside Adapter"),
    Cell("Decorator", 1, 1,
         (Node("Client", 280, 320, w=80, h=40, kind="mark"),
          Node("Component", 400, 320, w=96, h=40, kind="interface",
               size=11),
          Node("Pizza", 280, 440, w=80, h=34, size=11),
          Node("Topping", 400, 440, w=96, h=34, size=11)),
         (Edge("Client", "Component", "thin"),
          Edge("Pizza", "Component", "realize", corner=True),
          Edge("Topping", "Component", "realize", shift=-14),
          Edge("Topping", "Component", "thin", label="wraps", shift=14,
               dx=34, dy=4)),
         "heavy edges: 0"),
    Cell("Visitor", 2, 1,
         (Node("Element", 530, 316, w=80, h=36, kind="interface", size=11),
          Node("Visitor", 660, 316, w=86, h=36, kind="interface", size=11),
          Node("Pricer", 668, 388, w=70, h=36, kind="mark"),
          Node("Add", 522, 460, w=62, h=30, size=10.5),
          Node("Mul", 597, 460, w=62, h=30, size=10.5),
          Node("Num", 672, 460, w=62, h=30, size=10.5)),
         (Edge("Element", "Visitor", "thin", label="accept"),
          Edge("Pricer", "Visitor", "realize"),
          Edge("Add", "Element", "realize"),
          Edge("Pricer", "Add", "heavy", corner=True),
          Edge("Mul", "Element", "realize"),
          Edge("Pricer", "Mul", "heavy"),
          Edge("Num", "Element", "realize", corner=True),
          Edge("Pricer", "Num", "heavy")),
         "heavy edges: 3, all in Pricer"),
)


def render_gallery(pid: str = "gl") -> str:
    height = 2 * GALLERY_H + 34
    b = ""
    for cell in GALLERY:
        x0, y0 = 18 + GALLERY_W * cell.col, GALLERY_H * cell.row
        b += text(x0, y0 + 26, cell.title, 13, INK, bold=True, italic=True)
        b += (f'  <line x1="{x0}" y1="{y0 + 32}" x2="{x0 + 230}" '
              f'y2="{y0 + 32}" stroke="{BOX}" stroke-width="0.8"/>\n')
        nodes = {n.name: n for n in cell.nodes}
        for n in cell.nodes:
            b += n.svg()
        for e in cell.edges:
            b += edge_svg(e, nodes, pid)
        b += text(x0, y0 + 256, cell.note, 10.5, MUTED)
    # The legend runs along the bottom, one sample per edge kind.
    y = 2 * GALLERY_H + 12
    for x, kind, label in ((20, "heavy", "names a concrete class"),
                           (230, "thin", "names an interface"),
                           (410, "realize", "satisfies it")):
        stroke, width, dash, head = STYLES[kind]
        end = x + 36 - HEADS[MARKERS[head][0]].trim
        b += (f'  <line class="legend" x1="{x}" y1="{y}" '
              f'x2="{end:g}" y2="{y}" '
              f'stroke="{stroke}" stroke-width="{width}"{dash} '
              f'marker-end="url(#{pid}-{head})"/>\n')
        b += text(x + 42, y + 4, label, 10.5, MUTED)
    b += (f'  <rect x="550" y="{y - 8}" width="26" height="16" fill="none" '
          f'stroke="{MARK}" stroke-width="1.6" rx="3"/>\n')
    b += text(584, y + 4, "the part that does not change", 10.5, MUTED)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 770 {height}"\n     {FONT}>\n'
            f"  <title>{GALLERY_TITLE}</title>\n" + defs(pid) + b + "</svg>\n")


# A tip sits on the target's border grown by TIP_PAD, the margin
# `arrowheads.tight_tips()` requires, and may stray TIP_SLACK from it.
TIP_PAD, TIP_SLACK = 4.0, 1.0


def samples(pts: list[Point], steps: int = 200) -> list[Point]:
    """Points along the straight or quadratic edge `pts`."""
    out = []
    for i in range(steps + 1):
        t = i / steps
        if len(pts) == 2:
            (x1, y1), (x2, y2) = pts
            out.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        else:
            (x1, y1), (mx, my), (x2, y2) = pts
            u = 1 - t
            out.append((u * u * x1 + 2 * u * t * mx + t * t * x2,
                        u * u * y1 + 2 * u * t * my + t * t * y2))
    return out


def edge_problems(nodes: tuple[Node, ...],
                  edges: tuple[Edge, ...]) -> list[str]:
    """Each edge whose tip strays from its target's padded outline, and
    each edge that crosses a box other than its own two."""
    by_name = {n.name: n for n in nodes}
    out: list[str] = []
    for e in edges:
        pts = edge_points(e, by_name)
        gap = by_name[e.b].distance(pts[-1])
        if abs(gap - TIP_PAD) > TIP_SLACK:
            out.append(f"{e.a} -> {e.b}: tip {gap:.1f} from the outline, "
                       f"not {TIP_PAD:g}")
        crossed = [n.name for n in nodes if n.name not in (e.a, e.b)
                   and any(n.distance(q) < 0 for q in samples(pts))]
        if crossed:
            out.append(f"{e.a} -> {e.b}: crosses {', '.join(crossed)}")
    return out


def all_edge_problems() -> list[str]:
    out = [f"coupling_{ch}.svg  {msg}" for ch, p in sorted(PANELS.items())
           for msg in edge_problems(p.nodes, p.edges)]
    out += [f"coupling_gallery.svg ({c.title})  {msg}" for c in GALLERY
            for msg in edge_problems(c.nodes, c.edges)]
    return out


def render_all() -> dict[Path, str]:
    out = {IMAGES / f"coupling_{ch}.svg": p.svg(f"c{ch}")
           for ch, p in sorted(PANELS.items())}
    out[IMAGES / "coupling_gallery.svg"] = render_gallery()
    return out


def rasterize(out_dir: Path) -> int:
    """Rasterize every committed coupling_*.svg into `out_dir` as the EPUB would."""
    from tools import build_epub
    tool = build_epub.find_svg_tool()
    if tool is None:
        print(f"no SVG rasterizer on PATH; {build_epub.svg_tool_hint()}")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    svgs = sorted(IMAGES.glob("coupling_*.svg"))
    for src in svgs:
        dst = out_dir / f"{src.stem}.png"
        subprocess.run(build_epub.svg_command(tool, src, dst), check=True,
                       capture_output=True)
    print(f"rasterized {len(svgs)} figure(s) with {tool} into "
          f"{out_dir.relative_to(ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report SVGs that differ from the spec; write nothing")
    ap.add_argument("--png", nargs="?", const=ROOT / "build" / "coupling",
                    type=Path, metavar="DIR",
                    help="rasterize every coupling_*.svg into DIR "
                         "(default build/coupling/) and write nothing else")
    args = ap.parse_args(argv)
    if args.png is not None:
        return rasterize(args.png)
    drift = 0
    for path, body in render_all().items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if args.check:
            if current != body:
                print(f"drift  {path.relative_to(ROOT)}")
                drift += 1
        elif current != body:
            path.write_text(body, encoding="utf-8", newline="\n")
            print(f"wrote  {path.relative_to(ROOT)}")
    if args.check:
        print("coupling panels: in sync" if not drift else
              f"coupling panels: {drift} file(s) differ; rerun without --check")
    problems = all_edge_problems()
    for msg in problems:
        print(f"edge   {msg}")
    if problems:
        print(f"coupling panels: {len(problems)} edge problem(s)")
    return 1 if drift or problems else 0


if __name__ == "__main__":
    sys.exit(main())
