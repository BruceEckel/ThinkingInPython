"""Chapter 33, Visitor: two dispatches, then one.

Three frames of one layout: the `Flower` hierarchy, which cannot change,
on the left, and everything outside it on the right. In frames 1 and 2
a `Worm` visits two flowers, and the call bounces across the line
twice: `accept()` hands the flower to the visitor, the visitor's type
picks `Predator.visit`, and that method calls back into the flower,
whose type picks `eat()`. The frames differ only at the second
dispatch (the `Chrysanthemum` override against the inherited
`Flower.eat`), which is what `dispatch_trace.py` prints. Frame 3 is
`visitor_singledispatch.py`: the flowers carry no methods, and one
lookup in `nectar()`'s dispatch table, keyed by the flower's type,
does the work, with `Ranunculus` falling through to the `object` entry.
A storyboard suits this chapter because its argument is about how many
hops a call takes, which a class diagram cannot show. The method names
are the qualified names `dispatch_trace.py` prints; the output lines
are the `#:` markers of `dispatch_trace.py` and
`visitor_singledispatch.py`.
"""

from tools.story_figures import (
    INK,
    MUTED,
    RED,
    SHADE,
    arrow,
    line,
    markers,
    rect,
    region,
    svg,
    text,
)

STEM = "visitor_story"
W = 730
FH = 190  # One frame's height
FX, FW = 140, 200  # The Flower hierarchy's region
OX = FX + FW + 14  # Where the region outside Flower begins
BW, BH = 140, 30  # A method box
AX = 160  # The flower-side method boxes
VX = 540  # The visitor-side method box
TITLE = ("Visitor's two dispatches and singledispatch's one: "
         "flower.accept(worm) calls Predator.visit, which calls back "
         "into Chrysanthemum.eat or the inherited Flower.eat, while "
         "nectar(f) looks the flower's type up in one table "
         "with no method on Flower")


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          right: str) -> str:
    """The layout every frame shares: the two regions and the gutter."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += region(FX, y0 + 6, FW, FH - 18, fill=SHADE, r=0)
    out += text(FX + 8, y0 + 22, "Flower: cannot change", 10, MUTED)
    out += text(W - 18, y0 + 22, right, 10, MUTED, "end")
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def method(x: float, y: float, s: str, stroke: str = INK) -> str:
    return (rect(x, y, BW, BH, stroke=stroke)
            + text(x + BW / 2, y + 20, s, 12, INK, "middle"))


def bounce(y0: float, eat: str, output: str) -> str:
    """flower.accept(worm): across to the visitor and back."""
    ay, vy, ey = y0 + 48, y0 + 88, y0 + 128
    b = text(AX + BW / 2, ay - 6, "flower.accept(worm)", 10, INK, "middle")
    b += method(AX, ay, "Flower.accept")
    b += method(VX, vy, "Predator.visit", RED)
    b += method(AX, ey, eat, RED)
    b += text(VX + BW / 2, vy - 6, "dispatch 1: worm's type", 10, RED,
              "middle")
    b += text(VX + BW / 2, vy + BH + 14, "Worm inherits it", 10, MUTED,
              "middle")
    b += text(AX + BW / 2, ey + BH + 14, "dispatch 2: flower's type", 10,
              RED, "middle")
    a, t = (AX + BW, ay + BH / 2), (VX, vy + BH / 2)
    b += arrow(a, t, INK, "vs-ink")
    b += text((a[0] + t[0]) / 2 + 12, a[1] + 4, "visitor.visit(self)", 10,
              INK, "middle")
    a, t = (VX, vy + BH / 2), (AX + BW, ey + BH / 2)
    b += arrow(a, t, INK, "vs-ink")
    b += text((a[0] + t[0]) / 2 + 12, t[1] + 4, "flower.eat(self)", 10,
              INK, "middle")
    b += text(OX + 14, y0 + FH - 20, output, 11, RED)
    return b


def render() -> str:
    y = [10 + i * FH for i in range(3)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, "override", ("a worm visits a", "Chrysanthemum;",
                                   "two dispatches"), "outside Flower")
    b += bounce(y0, "Chrysanthemum.eat", "Chrysanthemum is toxic to Worm")

    y0 = y[1]
    b += frame(1, y0, "inherit", ("the same worm", "visits a Gladiolus;",
                                  "dispatch 2 differs"), "outside Flower")
    b += bounce(y0, "Flower.eat", "Gladiolus eaten by Worm")

    y0 = y[2]
    b += frame(2, y0, "one dispatch", ("singledispatch:", "no accept(),",
                                       "no Visitor class"),
               "outside Flower")
    rows = (("Gladiolus", "Gladiolus", "Gladiolus: abundant nectar"),
            ("Ranunculus", "object", "Ranunculus: no nectar"),
            ("Chrysanthemum", "Chrysanthemum",
             "Chrysanthemum: a little nectar"))
    kx, kw, rh, gap = OX + 26, 116, 30, 8
    b += text(kx + kw / 2, y0 + 38, "nectar.registry", 10, MUTED, "middle")
    b += region(kx, y0 + 44, kw, 3 * rh + 2 * gap + 8, stroke=INK,
                width=1.3)
    for k, (flower, key, out) in enumerate(rows):
        fy = y0 + 48 + k * (rh + gap)
        b += rect(AX, fy, BW, rh, stroke=INK)
        b += text(AX + BW / 2, fy + 20, flower, 12, INK, "middle")
        hit = key != "object"
        b += rect(kx + 8, fy + 4, kw - 16, rh - 8,
                  stroke=RED if hit else MUTED, rx=3)
        b += text(kx + kw / 2, fy + 19, key, 11, INK if hit else MUTED,
                  "middle")
        b += arrow((AX + BW, fy + rh / 2), (kx + 8, fy + rh / 2), INK,
                   "vs-ink")
        b += text(kx + kw + 10, fy + 19, out, 10.5, RED)
    b += text((AX + BW + kx) / 2 - 6, y0 + 56, "nectar(f)", 10, INK,
              "middle")
    b += text(AX + BW / 2, y0 + FH - 18, "nothing edits Flower", 10.5,
              RED, "middle")
    b += text(kx + kw / 2, y0 + FH - 18, "dispatch: flower's type", 10,
              RED, "middle")

    defs = markers(**{"vs-ink": ("filled", INK)})
    return svg(W, 10 + 3 * FH, TITLE, defs, b)
