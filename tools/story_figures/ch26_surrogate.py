"""Chapter 26, Surrogate: one call path, before and after a swap.

Three frames of one layout, from `state_demo.py`: `run(b)` calls `b.f()`,
and `Surrogate`, which defines no `f()`, forwards it through
`__getattr__()` to `first`; `b.change_to(second)` rebinds
`__implementation`; the same `run(b)` on the same `b` now prints
`second`'s line. Frame 1 alone is a *Proxy*, and frames 2 and 3 add what
*State* adds, so the storyboard shows the chapter's claim that the two
patterns are one surrogate with two intents. A storyboard suits this
pattern because its point is a change over time that the caller cannot
see; the coupling panel it replaces showed only who names whom. The
names come from `state_surrogate.py` (`Surrogate`, `__implementation`,
`__getattr__()`, `change_to()`) and `state_demo.py` (`run()`, `b`,
`first`, `second`, `Implementation1`, `Implementation2`, and the first
line each `f()` prints).
"""

from tools.story_figures import (INK, MUTED, RED, Point, arrow, cross,
                                 line, markers, rect, svg, text)

STEM = "surrogate_story"
W = 730
FH = 180  # One frame's height
CX, CW, CH = 135, 128, 112  # The caller box
SX, SW, SH = 298, 150, 112  # The Surrogate box
LX, LW, LH = SX + 12, 126, 26  # The __implementation slot inside it
IX, IW, IH = 530, 180, 44  # The two implementations
IMPL_Y = (18, 76)
CALLS = ("b.f()", "b.g()", "b.h()", "b.g()")
TITLE = ("Three steps of a Surrogate: run(b) calls b.f() and __getattr__() "
         "forwards it to first, b.change_to(second) rebinds the "
         "implementation, and the same run(b) on the same b then reaches "
         "second")


def slot_end(y0: float) -> Point:
    return (LX + LW, y0 + 52 + LH / 2)


def impl_mid(y0: float, k: int) -> Point:
    return (IX, y0 + IMPL_Y[k] + IH / 2)


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          forwarding: bool) -> str:
    """The layout every frame shares: caller, Surrogate, two implementations."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    edge = RED if i == 2 else INK
    out += rect(CX, y0 + 18, CW, CH, stroke=edge)
    out += rect(SX, y0 + 18, SW, SH, stroke=edge)
    out += text(SX + 12, y0 + 38, "Surrogate", 13, bold=True)
    out += text(SX + SW - 12, y0 + 38, "b", 12, MUTED, "end")
    out += rect(LX, y0 + 52, LW, LH, stroke=INK, width=1.1, rx=3)
    out += text(LX + LW / 2, y0 + 69, "__implementation", 10, MUTED,
                "middle")
    out += text(SX + 12, y0 + 102, "__getattr__()", 11,
                RED if forwarding else MUTED)
    out += text(SX + 12, y0 + 120, "change_to()", 11,
                MUTED if forwarding else RED)
    for k, (var, cls) in enumerate((("first", "Implementation1()"),
                                    ("second", "Implementation2()"))):
        iy = y0 + IMPL_Y[k]
        out += rect(IX, iy, IW, IH)
        out += text(IX + 12, iy + 18, var, 12, bold=True)
        out += text(IX + 12, iy + 34, cls, 10.5, MUTED)
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def run_call(y0: float, k: int, printed: str) -> str:
    """`run(b)` calls `b.f()`, which reaches implementation `k`."""
    out = text(CX + 12, y0 + 38, "run(b)", 12, bold=True)
    for j, s in enumerate(CALLS):
        out += text(CX + 12, y0 + 60 + j * 16, s, 10.5,
                    RED if j == 0 else MUTED)
    out += arrow((CX + CW, y0 + 56), (SX, y0 + 56), RED, "ss-red",
                 width=1.6)
    a, t = slot_end(y0), impl_mid(y0, k)
    out += arrow(a, t, RED, "ss-red", width=1.6)
    out += text((a[0] + t[0]) / 2, (a[1] + t[1]) / 2 - 8, "f()", 10.5,
                RED, "middle")
    var = ("first", "second")[k]
    out += text(IX + IW, y0 + 138, f"{var}.f() prints", 10, MUTED, "end")
    out += text(IX + IW, y0 + 154, printed, 10, RED, "end")
    return out


def render() -> str:
    y = [10 + i * FH for i in range(3)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, "forward",
               ("Surrogate has", "no f(), so", "__getattr__()",
                "forwards it"), True)
    b += run_call(y0, 0, "Fiddle de dum, Fiddle de dee,")

    y0 = y[1]
    b += frame(1, y0, "swap",
               ("change_to()", "rebinds the", "slot; only State",
                "takes this step"), False)
    b += text(CX + 12, y0 + 60, "b.change_to(", 10.5, RED)
    b += text(CX + 36, y0 + 76, "second)", 10.5, RED)
    b += arrow((CX + CW, y0 + 56), (SX, y0 + 56), RED, "ss-red",
               width=1.6)
    a = slot_end(y0)
    old, new = impl_mid(y0, 0), impl_mid(y0, 1)
    b += arrow(a, old, MUTED, "ss-muted", dash=True)
    b += cross((a[0] + old[0]) / 2, (a[1] + old[1]) / 2)
    b += arrow(a, new, RED, "ss-red", width=1.6)

    y0 = y[2]
    b += frame(2, y0, "again",
               ("same run(b),", "same b,", "new output"), True)
    b += run_call(y0, 1, "We're Knights of the Round Table.")
    b += text(CX, y0 + 150, "run() and b", 11, RED)
    b += text(CX, y0 + 165, "unchanged", 11, RED)

    defs = markers(**{"ss-red": ("filled", RED),
                      "ss-muted": ("filled", MUTED)})
    return svg(W, 10 + 3 * FH, TITLE, defs, b)
