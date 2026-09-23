"""Generate the coupling-notation panel at the top of each pattern chapter.

Appendix C (`Chapters/C_Coupling.md`) draws six GoF patterns in one
notation: a heavy edge names a concrete class, a thin edge names an
interface, a dashed edge with a hollow head satisfies one, and the red
box is the part the pattern keeps free of change. This script draws one
such panel per pattern chapter, 23 through 36, into
`resources/images/coupling_NN.svg`, so the chapters share a figure the
way they share a question: which edge does the pattern move, and where
does it put it?

Every panel is a `Panel` in `PANELS`, keyed by chapter number: its
nodes, its edges, and the "heavy edges" note under the drawing. The
names in a panel are the names in that chapter's listings, so a listing
rename means editing the spec here and regenerating, never editing an
SVG by hand:

    uv run python -m tools.coupling_panels            # write all
    uv run python -m tools.coupling_panels --check    # report drift

`--check` regenerates in memory and exits nonzero if any committed SVG
differs, so a future gate can call it the way `extract_examples`'s
check mode works for `Examples/`. It is not in any gate today.

The visual vocabulary matches the hand-authored figures: a `viewBox`
with no width or height, JetBrains Mono, the cover palette from
`make_cover.py`, and a `<title>` for screen readers. The canvas is 700
wide like the other figures, so the site renders every figure at the
same scale; the drawing sits on the left and a three-line legend on the
right.
"""
from __future__ import annotations
import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "resources" / "images"

INK = "#1a1612"
BOX = "#c8bfb0"
MUTED = "#7a6e62"
MARK = "#8b1a1a"
PAPER = "#f5f0e8"
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

    def svg(self) -> str:
        rx = 4
        stroke, width, dash, fill_text, weight = BOX, 1.3, "", INK, ""
        match self.kind:
            case "mark":
                stroke, width, weight = MARK, 1.6, ' font-weight="bold"'
            case "interface":
                stroke, rx, fill_text = MUTED, 12, MUTED
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
    """`kind` is heavy, thin, realize, inherit, or checked."""
    a: str
    b: str
    kind: str = "thin"
    label: str | None = None
    dx: float = 0
    dy: float = -6
    shift: float = 0
    bend: float = 0


STYLES: dict[str, tuple[str, float, str, str]] = {
    "heavy": (INK, 2.8, "", "solid"),
    "thin": (INK, 1.3, "", "solid"),
    "realize": (MUTED, 1.2, ' stroke-dasharray="5,4"', "hollow"),
    "inherit": (INK, 1.3, "", "hollow"),
    "checked": (MUTED, 1.2, ' stroke-dasharray="1.5,3"', "hollow"),
}


def edge_svg(e: Edge, nodes: dict[str, Node], pid: str) -> str:
    a, b = nodes[e.a], nodes[e.b]
    x1, y1 = a.edge_point(b.cx, b.cy, 2)
    x2, y2 = b.edge_point(a.cx, a.cy, 4)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    if e.shift:
        x1, y1 = x1 + nx * e.shift, y1 + ny * e.shift
        x2, y2 = x2 + nx * e.shift, y2 + ny * e.shift
    stroke, width, dash, head = STYLES[e.kind]
    marker = f'marker-end="url(#{pid}-{head})"'
    if e.bend:
        mx, my = (x1 + x2) / 2 + nx * e.bend, (y1 + y2) / 2 + ny * e.bend
        out = (f'  <path d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} '
               f'{x2:.1f},{y2:.1f}" fill="none" stroke="{stroke}" '
               f'stroke-width="{width}"{dash} {marker}/>\n')
        lx = (x1 + x2) / 2 + nx * e.bend / 2
        ly = (y1 + y2) / 2 + ny * e.bend / 2
    else:
        out = (f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
               f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"'
               f'{dash} {marker}/>\n')
        lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
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
    return f'''  <defs>
    <marker id="{pid}-solid" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="9" markerHeight="9" orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L10,5 L0,10 Z" fill="{INK}" stroke="{INK}" stroke-width="1"/>
    </marker>
    <marker id="{pid}-hollow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="10" markerHeight="10" orient="auto"
            markerUnits="userSpaceOnUse">
      <path d="M0,0 L10,5 L0,10 Z" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>
    </marker>
  </defs>
'''


def legend(x: float, y: float, pid: str) -> str:
    """Three edge samples and the red box, stacked, for the panel's right side."""
    rows = [
        ("heavy", "names a concrete class"),
        ("thin", "names an interface"),
        ("realize", "satisfies it"),
        ("inherit", "inherits its internals"),
    ]
    out = ""
    for i, (kind, label) in enumerate(rows):
        yy = y + i * 20
        stroke, width, dash, head = STYLES[kind]
        out += (f'  <line x1="{x}" y1="{yy}" x2="{x + 30}" y2="{yy}" '
                f'stroke="{stroke}" stroke-width="{width}"{dash} '
                f'marker-end="url(#{pid}-{head})"/>\n')
        out += text(x + 38, yy + 4, label, 10.5, MUTED)
    yy = y + len(rows) * 20
    out += (f'  <rect x="{x + 2}" y="{yy - 8}" width="26" height="16" fill="none" '
            f'stroke="{MARK}" stroke-width="1.6" rx="3"/>\n')
    out += text(x + 38, yy + 4, "kept free of change", 10.5, MUTED)
    return out


@dataclass(frozen=True)
class Panel:
    title: str
    alt: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    note: str
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
        b += text(10, self.height - 12, self.note, 10.5, MUTED)
        b += legend(480, 60, pid)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {WIDTH} {self.height}"\n     {FONT}>\n'
                f'  <title>{self.alt}</title>\n' + defs(pid) + b + '</svg>\n')


# The per-chapter specs. Columns C1..C3 and rows R1..R3 are the usual
# positions; a panel moves a box when its edges would otherwise cross.
C1, C2, C3 = 20, 172, 324
R1, R2, R3 = 48, 108, 168


def divider(x: float) -> str:
    return (f'  <line x1="{x}" y1="40" x2="{x}" y2="212" stroke="{BOX}" '
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
         Edge("list", "Iterable[int]", "realize"),
         Edge("fibonacci()", "Iterable[int]", "realize"),
         Edge("Countdown", "Iterable[int]", "realize")),
        "heavy edges: 0. The protocol total() names is one the language defines.",
    ),
    24: Panel(
        "Singleton",
        "Every importer names config.py by its module name, and the import "
        "system hands each one the same instance",
        (Node("config.py", C2, R2, w=170, kind="mark",
              sub="one instance per process"),
         Node("a.py", C1, R1, w=80),
         Node("b.py", C1, R3, w=80)),
        (Edge("a.py", "config.py", "heavy", label="import", dx=24, dy=-10),
         Edge("b.py", "config.py", "heavy", label="import", dx=24, dy=18)),
        "heavy edges: one per importer, all pointing at a name that does not change.",
    ),
    25: Panel(
        "Template Method",
        "MyApp inherits ApplicationFramework's internals, while "
        "run_framework() names only the Step signature its two functions satisfy",
        (Node("ApplicationFramework", C1, R1, w=180, kind="mark", sub="run()"),
         Node("MyApp", C1, R3, w=180),
         Node("run_framework()", 256, R1, w=160, kind="mark"),
         Node("Step", 288, R2, w=96, kind="interface",
              sub="Callable[[], None]"),
         Node("two functions", 256, R3, w=160, kind="absent")),
        (Edge("MyApp", "ApplicationFramework", "inherit",
              label="overrides two steps", dx=70, dy=4),
         Edge("run_framework()", "Step", "thin"),
         Edge("two functions", "Step", "realize")),
        "left: the inherit edge is the widest rung; right: the same algorithm "
        "with one thin edge.",
        extra=(divider(228),),
    ),
    26: Panel(
        "Surrogate",
        "The caller names Service, Proxy and Implementation satisfy it, "
        "and only Proxy names Implementation",
        (Node("caller", C1, R2, w=80, kind="mark"),
         Node("Service", C2 - 20, R2, kind="interface"),
         Node("Proxy", C3 - 10, R1, w=90),
         Node("Implementation", C3 - 10, R3, w=126)),
        (Edge("caller", "Service", "thin"),
         Edge("Proxy", "Service", "realize"),
         Edge("Implementation", "Service", "realize"),
         Edge("Proxy", "Implementation", "heavy")),
        "heavy edges: 1, inside Proxy. State swaps the class at the far end "
        "of that edge.",
    ),
    27: Panel(
        "Factory",
        "The caller names Shape and make(), and make() is the one place that "
        "names Circle and Square",
        (Node("caller", C1, R1, w=80, kind="mark"),
         Node("make()", C2, R1, w=90),
         Node("Shape", C1, R3, w=80, kind="interface"),
         Node("Circle", C2, R3, w=80),
         Node("Square", C3, R3, w=80)),
        (Edge("caller", "Shape", "thin"),
         Edge("caller", "make()", "heavy"),
         Edge("make()", "Circle", "heavy", label="SHAPES", dx=30, dy=4),
         Edge("make()", "Square", "heavy"),
         Edge("Circle", "Shape", "inherit"),
         Edge("Square", "Shape", "inherit", bend=-46)),
        "heavy edges: 3. The two that name a shape sit in one table, and "
        "self-registration removes them.",
    ),
    28: Panel(
        "Function Objects",
        "The macro loop names only the Command signature, and three "
        "functions satisfy it by having that signature",
        (Node("macro loop", C1, R2, w=100, kind="mark", sub="command()"),
         Node("Command", C2, R2, w=110, kind="interface",
              sub="Callable[[], None]"),
         Node("no_more()", C3, R1, w=96),
         Node("ceased()", C3, R2, w=96),
         Node("fjords()", C3, R3, w=96)),
        (Edge("macro loop", "Command", "thin"),
         Edge("no_more()", "Command", "realize"),
         Edge("ceased()", "Command", "realize"),
         Edge("fjords()", "Command", "realize")),
        "heavy edges: 0. The interface is a signature, so no class declares it.",
    ),
    29: Panel(
        "Adapter",
        "WhatIUse names WhatIWant, and ProxyAdapter is the one class that "
        "names both WhatIWant and WhatIHave",
        (Node("WhatIUse", C1, R1, kind="mark"),
         Node("WhatIWant", C2, R1, w=100, kind="interface"),
         Node("ProxyAdapter", C2, R3, w=110),
         Node("WhatIHave", C3 + 6, R3, w=96)),
        (Edge("WhatIUse", "WhatIWant", "thin"),
         Edge("ProxyAdapter", "WhatIWant", "inherit"),
         Edge("ProxyAdapter", "WhatIHave", "heavy")),
        "heavy edges: 1, inside ProxyAdapter, so a change to WhatIHave "
        "reaches one class.",
    ),
    30: Panel(
        "Observer",
        "Thermometer names only Observer, Display satisfies it, and the "
        "wiring code is the one place that names both",
        (Node("Thermometer", C1, R1, w=110, kind="mark"),
         Node("Observer", C2 + 24, R1, w=100, kind="interface"),
         Node("Display", C2 + 24, R3, w=100),
         Node("wiring", C1, R3, w=80)),
        (Edge("Thermometer", "Observer", "thin", label="notify", dy=-8),
         Edge("Display", "Observer", "realize"),
         Edge("wiring", "Thermometer", "heavy"),
         Edge("wiring", "Display", "heavy", label="attach", dx=0, dy=14)),
        "heavy edges: 2, both in the wiring. Neither Thermometer nor Display "
        "names the other.",
    ),
    31: Panel(
        "State Machine",
        "StateMachine names only State, each state satisfies it, and the "
        "states name the next state through MouseTrap",
        (Node("StateMachine", C1, R1, w=110, kind="mark"),
         Node("State", C2 + 10, R1, w=90, kind="interface"),
         Node("MouseTrap", C1, R3, w=110),
         Node("Waiting", C3, 92, w=90),
         Node("Luring", 200, 160, w=90)),
        (Edge("StateMachine", "State", "thin"),
         Edge("MouseTrap", "StateMachine", "inherit"),
         Edge("Waiting", "State", "realize"),
         Edge("Luring", "State", "realize"),
         Edge("Waiting", "MouseTrap", "heavy", label="next", dx=-10, dy=-8),
         Edge("Luring", "MouseTrap", "heavy")),
        "heavy edges: one per state. The table form moves them into one dict.",
    ),
    32: Panel(
        "Multiple Dispatching",
        "duel() names only Item, and Paper, Scissors, and Rock each name an "
        "eval method for every other",
        (Node("duel()", C1, R2, w=80, kind="mark"),
         Node("Item", 150, R2, w=76, kind="interface"),
         Node("Paper", 246, 40, w=86),
         Node("Rock", 246, 174, w=86),
         Node("Scissors", 346, 107, w=90)),
        (Edge("duel()", "Item", "thin"),
         Edge("Paper", "Item", "inherit"),
         Edge("Rock", "Item", "inherit"),
         Edge("Scissors", "Item", "inherit"),
         Edge("Paper", "Scissors", "heavy", shift=5),
         Edge("Scissors", "Paper", "heavy", shift=5),
         Edge("Scissors", "Rock", "heavy", shift=5),
         Edge("Rock", "Scissors", "heavy", shift=5),
         Edge("Paper", "Rock", "heavy", shift=5),
         Edge("Rock", "Paper", "heavy", shift=5)),
        "heavy edges: 6. Adding a fourth item edits all three.",
    ),
    33: Panel(
        "Visitor",
        "Flower names only Visitor and Pollinator names only Flower, so no "
        "visitor names a concrete flower",
        (Node("Flower", C1, R1, w=110, kind="mark", sub="cannot change"),
         Node("Visitor", C3, R1, w=96, kind="interface"),
         Node("Chrysanthemum", C1, R3, w=130),
         Node("Pollinator", C3, R2 + 6, w=96),
         Node("Bee", C3, R3 + 6, w=96)),
        (Edge("Flower", "Visitor", "thin", label="accept", dy=-8),
         Edge("Pollinator", "Flower", "thin", label="visit", dx=-24, dy=14),
         Edge("Chrysanthemum", "Flower", "inherit"),
         Edge("Pollinator", "Visitor", "inherit"),
         Edge("Bee", "Pollinator", "inherit")),
        "heavy edges: 0. Each side names the other's base, and the second "
        "dispatch is a method on Flower.",
    ),
    34: Panel(
        "Composite",
        "disk_usage() and walk() each name both node types, and Directory "
        "names only the Node union",
        (Node("disk_usage()", C1, R1, w=110),
         Node("walk()", C1, R2, w=110),
         Node("File", C3, R1, w=90),
         Node("Directory", C3, R2, w=96),
         Node("Node", C2 + 10, R3 + 6, w=90, kind="interface",
              sub="File | Directory")),
        (Edge("disk_usage()", "File", "heavy"),
         Edge("disk_usage()", "Directory", "heavy"),
         Edge("walk()", "File", "heavy"),
         Edge("walk()", "Directory", "heavy"),
         Edge("walk()", "Node", "thin"),
         Edge("Directory", "Node", "thin", label="entries", dx=26, dy=4)),
        "heavy edges: two per function, on purpose: a new node type must "
        "reach every match, and the checker lists them.",
    ),
    35: Panel(
        "Flyweight",
        "parse_map() names tile(), and tile() is the one place that "
        "constructs a Tile",
        (Node("parse_map()", C1, R2, w=110, kind="mark"),
         Node("tile()", C2 + 10, R2, w=90, sub="@cache"),
         Node("Tile", C3 + 10, R2, w=80),
         Node("SPECS", C2 + 10, R3 + 8, w=90)),
        (Edge("parse_map()", "tile()", "heavy"),
         Edge("tile()", "Tile", "heavy", label="constructs", dy=18),
         Edge("tile()", "SPECS", "heavy")),
        "heavy edges: 3. Only tile() constructs, so every caller shares its "
        "instances.",
    ),
    36: Panel(
        "Memento",
        "Sketch names Memento, and History names only a type parameter, so it "
        "holds a Memento without reading it",
        (Node("Sketch", C1, R1, w=100, kind="mark"),
         Node("Memento", C2 + 10, R1, w=96),
         Node("History[S]", C1, R3, w=110),
         Node("S", C2 + 10, R3, w=96, kind="interface", sub="any value")),
        (Edge("Sketch", "Memento", "heavy", label="save, restore", dy=18),
         Edge("History[S]", "S", "thin"),
         Edge("Memento", "S", "realize")),
        "heavy edges: 1, inside the originator. The caretaker names no "
        "memento type.",
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
    26: "The caller names `Service`, `Proxy` and `Implementation` satisfy it, "
        "and only `Proxy` names `Implementation`",
    27: "The caller names `Shape` and `make()`, and `make()` is the one place "
        "that names `Circle` and `Square`",
    28: "The macro loop names only the `Command` signature, and three "
        "functions satisfy it by having that signature",
    29: "`WhatIUse` names `WhatIWant`, and `ProxyAdapter` is the one class "
        "that names both `WhatIWant` and `WhatIHave`",
    30: "`Thermometer` names only `Observer`, `Display` satisfies it, and the "
        "wiring code is the one place that names both",
    31: "`StateMachine` names only `State`, each state satisfies it, and the "
        "states name the next state through `MouseTrap`",
    32: "`duel()` names only `Item`, and `Paper`, `Scissors`, and `Rock` each "
        "name an eval method for every other",
    33: "`Flower` names only `Visitor` and `Pollinator` names only `Flower`, "
        "so no visitor names a concrete flower",
    34: "`disk_usage()` and `walk()` each name both node types, and "
        "`Directory` names only the `Node` union",
    35: "`parse_map()` names `tile()`, and `tile()` is the one place that "
        "constructs a `Tile`",
    36: "`Sketch` names `Memento`, and `History` names only a type parameter, "
        "so it holds a `Memento` without reading it",
}


def render_all() -> dict[Path, str]:
    return {IMAGES / f"coupling_{ch}.svg": p.svg(f"c{ch}")
            for ch, p in sorted(PANELS.items())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report SVGs that differ from the spec; write nothing")
    args = ap.parse_args(argv)
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
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
