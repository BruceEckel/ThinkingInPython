"""Chapter 27, Factory: four frames, from scattered creation to a registry.

Frame 1 is the chapter's opening problem (`shapes_naive.py`): two call
sites each name `Circle` and `Square`, `Triangle` joins the hierarchy,
and neither call site builds it, one drawing nothing and one raising a
`ValueError`. Frames 2 to 4 share one layout, the self-registering
factory of `registry.py`: the class statements fill `Shape.registry`
(`registry_demo.py` prints its keys), `make()` looks a name up and calls
the class it finds, a name with no entry is a `KeyError`, and a new
`Triangle` subclass registers itself with no edit to `make()` (the
`Triangle` that `test_registry.py` defines inside a test). The coupling
panel showed which names each box mentions; the frames show the cost of
adding a type before and after the factory, which is the chapter's
opening argument.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, Point, arrow, cross,
                                 line, markers, rect, region, svg, text)

STEM = "factory_story"
W = 725
FH = 180  # One frame's height
AX, AW = 140, 150  # The caller column
BX, BW = 335, 165  # make() and its table
SX, SW, SH = 355, 125, 26  # The slots in Shape.registry
CX, CW, CH = 585, 120, 28  # The classes
SLOT_Y = (58, 92, 126)
TITLE = ("Four steps of Factory: two call sites that each name Circle and "
         "Square miss a new Triangle, class statements fill "
         "Shape.registry, make() looks a name up and calls its class, and "
         "a new Triangle registers itself with no edit to make()")


def slot_left(y0: float, k: int) -> Point:
    return (SX, y0 + SLOT_Y[k] + SH / 2)


def slot_right(y0: float, k: int) -> Point:
    return (SX + SW, y0 + SLOT_Y[k] + SH / 2)


def cls_left(y0: float, k: int) -> Point:
    return (CX, y0 + SLOT_Y[k] + SH / 2)


def gutter(i: int, y0: float, name: str, lines: tuple[str, ...]) -> str:
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def classes(y0: float, names: tuple[str, ...], red: int = -1) -> str:
    out = ""
    for k, s in enumerate(names):
        x, y = CX, y0 + SLOT_Y[k] + SH / 2 - CH / 2
        out += rect(x, y, CW, CH, stroke=RED if k == red else BOX,
                    width=1.6 if k == red else 1.3)
        out += text(x + CW / 2, y + 19, s, 12.5, INK, "middle")
    return out


def factory(y0: float, keys: tuple[str, ...], stroke: str = INK) -> str:
    """make() and the table it reads, with `keys` filled."""
    out = region(BX, y0 + 12, BW, FH - 28, stroke=stroke)
    out += text(BX + 12, y0 + 32, "make(name)", 12, bold=True)
    out += text(BX + 12, y0 + 48, "Shape.registry[name]()", 10, MUTED)
    for k, sy in enumerate(SLOT_Y):
        filled = k < len(keys)
        out += rect(SX, y0 + sy, SW, SH, stroke=INK if filled else BOX,
                    width=1.1, dash=not filled, rx=3)
        if filled:
            out += text(SX + SW / 2, y0 + sy + 17, f"'{keys[k]}'", 10.5,
                        INK, "middle")
    return out


def caller(y0: float) -> str:
    return (rect(AX, y0 + 12, AW, FH - 28, stroke=INK)
            + text(AX + 12, y0 + 32, "caller", 12, bold=True))


def register(y0: float, k: int, color: str = INK,
             marker: str = "fs-ink") -> str:
    a, t = cls_left(y0, k), slot_right(y0, k)
    return (arrow(a, t, color, marker)
            + text((a[0] + t[0]) / 2 + 8, t[1] - 6, "registers", 10, color,
                   "middle"))


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    b = ""

    y0 = y[0]
    b += gutter(0, y0, "scatter", ("each call site", "names each class;",
                                   "Triangle needs", "two edits"))
    b += rect(AX, y0 + 12, AW, 70, stroke=INK)
    b += text(AX + 12, y0 + 32, "render()", 12, bold=True)
    b += text(AX + 12, y0 + 52, 'render("Triangle")', 10, MUTED)
    b += text(AX + 12, y0 + 68, "draws nothing", 10.5, RED)
    b += rect(AX, y0 + 94, AW, 70, stroke=INK)
    b += text(AX + 12, y0 + 114, "export_svg()", 12, bold=True)
    b += text(AX + 12, y0 + 134, 'export_svg("Triangle")', 10, MUTED)
    b += text(AX + 12, y0 + 150, "raises ValueError", 10.5, RED)
    b += classes(y0, ("Circle", "Square", "Triangle"), red=2)
    for j, sy in enumerate((y0 + 38, y0 + 120)):
        for k in (0, 1):
            cx, cy = cls_left(y0, k)
            b += arrow((AX + AW, sy + 12 * k), (cx, cy - 6 + 12 * j), INK,
                       "fs-ink")

    y0 = y[1]
    b += gutter(1, y0, "register", ("each class", "statement adds", "its class",
                                    "to the table"))
    b += caller(y0)
    b += text(AX + 12, y0 + 75, "sorted(Shape.registry)", 10)
    b += text(AX + 12, y0 + 91, "['Circle', 'Square']", 10, RED)
    b += factory(y0, ("Circle", "Square"))
    b += classes(y0, ("Circle", "Square"))
    b += register(y0, 0) + register(y0, 1)

    y0 = y[2]
    b += gutter(2, y0, "make", ("make() looks up", "the name and", "calls the",
                                "class it finds"))
    b += caller(y0)
    b += text(AX + 12, y0 + 75, 'make("Circle").draw()', 10, RED)
    b += text(AX + 12, y0 + 91, "Circle.draw", 10.5, RED)
    b += text(AX + 12, y0 + 125, 'make("Triangle")', 10)
    b += text(AX + 12, y0 + 141, "[KeyError] 'Triangle'", 10, RED)
    b += factory(y0, ("Circle", "Square"))
    b += classes(y0, ("Circle", "Square"))
    b += arrow((AX + AW, y0 + 71), slot_left(y0, 0), RED, "fs-red",
               width=1.6)
    a, t = slot_right(y0, 0), cls_left(y0, 0)
    b += arrow(a, t, RED, "fs-red", width=1.6)
    b += text((a[0] + t[0]) / 2, a[1] - 6, "calls", 10, RED, "middle")
    b += line((AX + AW, y0 + 121), (BX, y0 + 121), MUTED, 1.3, dash=True)
    b += cross((AX + AW + BX) / 2, y0 + 121)

    y0 = y[3]
    b += gutter(3, y0, "extend", ("a new subclass", "registers itself;",
                                  "make() builds it"))
    b += caller(y0)
    b += text(AX + 12, y0 + 75, "no edit to make()", 11, RED)
    b += text(AX + 12, y0 + 90, "or the caller", 11, RED)
    b += text(AX + 12, y0 + 143, 'make("Triangle")', 10)
    b += factory(y0, ("Circle", "Square", "Triangle"), stroke=RED)
    b += classes(y0, ("Circle", "Square", "Triangle"))
    b += register(y0, 2)
    b += arrow((AX + AW, y0 + 139), slot_left(y0, 2), INK, "fs-ink")

    defs = markers(**{"fs-ink": ("filled", INK), "fs-red": ("filled", RED)})
    return svg(W, 10 + 4 * FH, TITLE, defs, b)
