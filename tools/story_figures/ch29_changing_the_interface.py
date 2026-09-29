"""Chapter 29, Changing the Interface: two before-and-after pairs.

The chapter's story is a caller and existing code that do not fit, and a
new interface placed between them that changes neither side. Every frame
has the same three columns: the caller on the left, the new interface in
the middle, the code you have on the right. Frames 1 and 2 are *Adapter*:
`WhatIUse.op()` calls `f()`, `WhatIHave` has only `g()` and `h()`, and
`ProxyAdapter` turns the one call into the other two. Frames 3 and 4 are
*Façade*: the construction `Ignition(FuelPump(Engine()))` moves out of the
caller and into `Facade.start_car()`, so the caller names one class
instead of three. A before-and-after pair suits these patterns, whose
point is the difference a wrapper makes, better than a class diagram
does. The names come from `adapter.py` and `facade.py`, and the printed
lines are those listings' `#:` markers. Frame 3's caller is dashed
because no listing contains it; the prose describes it ("a caller has to
build the three from the inside out").
"""

from tools.story_figures import (INK, MUTED, RED, arrow, cross, line,
                                 markers, rect, region, svg, text)

STEM = "interface_story"
W = 730
TOP = 44  # The column headings sit above the first frame
FA1, FA2, FF = 140, 170, 210  # Frame heights: mismatch, Adapter, Façade
CX = 150  # The caller column's left edge
MX = 340  # The new-interface column's left edge
RX, RW = 560, 150  # The code-you-have column
CHAR = 0.6  # A character's width, in em
TITLE = ("Adapter and Façade in two before-and-after pairs: ProxyAdapter "
         "turns WhatIUse's f() call into WhatIHave's g() and h(), and "
         "Facade.start_car() takes over building Ignition, FuelPump, and "
         "Engine, so neither the caller nor the existing classes change")


def gutter(i: int, y0: float, name: str, lines: tuple[str, ...]) -> str:
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += text(22, y0 + 38, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 60, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 80 + j * 15, s, 10.5, MUTED)
    return out


def headings() -> str:
    out = ""
    for x, a, b in ((CX + 75, "the caller", "unchanged"),
                    (MX + 75, "the new interface", ""),
                    (RX + RW / 2, "the code you have", "unchanged")):
        out += text(x, 18, a, 10.5, MUTED, "middle")
        if b:
            out += text(x, 32, b, 10, MUTED, "middle")
    return out


# Adapter ------------------------------------------------------------

AW = 130  # WhatIUse's width
PW = 150  # ProxyAdapter's width
G_Y, H_Y, MH = 50, 84, 24  # WhatIHave's method rows, and their height
CALL_Y = 80  # Where op() calls f()


def what_i_use(y0: float) -> str:
    return (rect(CX, y0 + 36, AW, 64, stroke=INK)
            + text(CX + 12, y0 + 58, "WhatIUse", 12, bold=True)
            + text(CX + 12, y0 + 84, "op()", 11))


def what_i_have(y0: float, targeted: bool) -> str:
    """The adaptee; a region when arrows point at its method rows."""
    box = region if targeted else rect
    out = box(RX, y0 + 14, RW, 104, stroke=INK)
    out += text(RX + 12, y0 + 34, "WhatIHave", 12, bold=True)
    for my, s in ((G_Y, "g()"), (H_Y, "h()")):
        out += rect(RX + 14, y0 + my, RW - 28, MH, stroke=INK, width=1.1,
                    rx=3)
        out += text(RX + RW / 2, y0 + my + 16, s, 11, anchor="middle")
    return out


def adapter_frames(y0: float, y1: float) -> str:
    b = gutter(0, y0, "mismatch",
               ("op() calls f();", "WhatIHave has", "g() and h()"))
    b += what_i_use(y0) + what_i_have(y0, targeted=False)
    a, t = (CX + AW, y0 + CALL_Y), (RX, y0 + CALL_Y)
    b += arrow(a, t, INK, "is-ink")
    b += text(CX + AW + 26, a[1] - 6, "f()", 11, anchor="middle")
    mid = MX + PW / 2
    b += cross(mid, a[1])
    b += text(mid, a[1] + 24, "WhatIHave has", 10, RED, "middle")
    b += text(mid, a[1] + 37, "no f()", 10, RED, "middle")

    b += gutter(1, y1, "Adapter",
                ("ProxyAdapter", "turns each f()", "into g() and h()"))
    b += what_i_use(y1) + what_i_have(y1, targeted=True)
    b += text(CX, y1 + 24, "WhatIUse().op(adapt)", 10, MUTED)
    b += rect(MX, y1 + 36, PW, 64, stroke=RED, width=1.6)
    b += text(MX + 12, y1 + 58, "ProxyAdapter", 12, bold=True)
    b += text(MX + 12, y1 + 76, "a WhatIWant", 10, MUTED)
    b += text(MX + 12, y1 + 92, "f()", 11)
    a, t = (CX + AW, y1 + CALL_Y), (MX, y1 + CALL_Y)
    b += arrow(a, t, INK, "is-ink")
    b += text(a[0] + 18, a[1] - 6, "f()", 11, anchor="middle")
    for my, s in ((G_Y, "g()"), (H_Y, "h()")):
        yy = y1 + my + MH / 2
        b += arrow((MX + PW, yy), (RX + 14, yy), RED, "is-red", width=1.6)
        b += text(MX + PW + 18, yy - 5, s, 10, RED, "middle")
    b += text(RX + 14, y1 + 138, "WhatIHave.g()", 10.5, RED)
    b += text(RX + 14, y1 + 153, "WhatIHave.h()", 10.5, RED)
    return b


# Façade -------------------------------------------------------------

FW = 150  # The caller's width
DW = 120  # Facade's width
PARTS = (("Ignition", "Ignition.turn_key()", 14),
         ("FuelPump", "FuelPump.prime()", 84),
         ("Engine", "Engine.start()", 154))
PH = 36  # A part's height
BUILD = ("Ignition(", "  FuelPump(", "    Engine()))", ".turn_key()")


def parts(y0: float, printed: bool) -> str:
    out = ""
    for k, (name, output, py) in enumerate(PARTS):
        out += rect(RX, y0 + py, RW, PH, stroke=INK)
        if printed:
            out += text(RX + RW / 2, y0 + py + 15, name, 12, anchor="middle")
            out += text(RX + RW / 2, y0 + py + 30, output, 10, RED, "middle")
        else:
            out += text(RX + RW / 2, y0 + py + 23, name, 12, anchor="middle")
        if k:
            top, bottom = y0 + PARTS[k - 1][2] + PH, y0 + py
            x = RX + 34
            out += arrow((x, top), (x, bottom), INK, "is-ink")
            out += text(x + 10, (top + bottom) / 2 + 4,
                        ("prime()", "start()")[k - 1], 10)
    return out


def builds(x: float, y0: float) -> str:
    """The arrows from whoever builds the parts, at `x`, to each part."""
    out = ""
    for k, (_, _, py) in enumerate(PARTS):
        yy = y0 + py + PH / 2
        color, mid, label = ((INK, "is-ink", "turn_key()") if k == 0
                             else (MUTED, "is-muted", "builds"))
        out += arrow((x, yy), (RX, yy), color, mid)
        out += text(x + 10, yy - 6, label, 10, color)
    return out


def code(x: float, y: float) -> str:
    """`BUILD`, one line under another, keeping each line's indent."""
    out = ""
    for j, s in enumerate(BUILD):
        indent = len(s) - len(s.lstrip())
        out += text(x + indent * CHAR * 11, y + j * 16, s.lstrip(), 11)
    return out


def facade_frames(y0: float, y1: float) -> str:
    b = gutter(2, y0, "assembly",
               ("the caller", "builds all three", "inside out,", "then calls",
                "turn_key()"))
    b += rect(CX, y0 + 14, FW, 176, dash=True)
    b += text(CX + 12, y0 + 36, "caller", 12, MUTED, bold=True)
    b += code(CX + 12, y0 + 64)
    b += builds(CX + FW, y0) + parts(y0, printed=False)

    b += gutter(3, y1, "Façade",
                ("one call", "builds and", "starts the car;", "the caller",
                 "names Facade"))
    b += rect(CX, y1 + 14, FW, 60, stroke=INK)
    b += text(CX + 12, y1 + 36, "caller", 12, MUTED, bold=True)
    b += text(CX + 12, y1 + 58, "Facade.start_car()", 10.5)
    fx = MX
    b += rect(fx, y1 + 14, DW, 176, stroke=RED, width=1.6)
    b += text(fx + 12, y1 + 36, "Facade", 12, bold=True)
    b += text(fx + 12, y1 + 56, "start_car()", 11)
    b += code(fx + 12, y1 + 86)
    b += arrow((CX + FW, y1 + 44), (fx, y1 + 44), INK, "is-ink")
    b += builds(fx + DW, y1) + parts(y1, printed=True)
    return b


def render() -> str:
    ya = (TOP, TOP + FA1)
    yf = (TOP + FA1 + FA2, TOP + FA1 + FA2 + FF)
    b = headings()
    b += adapter_frames(*ya)
    b += facade_frames(*yf)
    defs = markers(**{"is-ink": ("filled", INK), "is-red": ("filled", RED),
                      "is-muted": ("filled", MUTED)})
    return svg(W, yf[1] + FF, TITLE, defs, b)
