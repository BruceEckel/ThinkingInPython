"""Chapter 28, Function Objects: one place decides, another place calls.

The chapter's opening says each of its three patterns defers something
(*Command* what, *Strategy* how, *Chain of Responsibility* which), and
that a function object carries the decision from the place that makes it
to the place that calls it. The figure is three lanes of one layout, so
only what each pattern defers differs: on the left, shaded, the callables
one place chooses; in the middle, outlined in red, the call site, which
stays the same and sees only the signature; on the right, what each run
produces, one row per callable. The names and output come from
`command.py` (the `macro` list and its three lines), `strategy.py`
(`bisection`, `newton`, `secant` passed to `solve()`, `1.414214` each
time), and `chain.py` (`solve(f, 1.0, 1.3, chain)`, where `bisection`
returns `None`, `secant` finds the root, and `newton` never runs, as
`test_chain.py` asserts).
"""

from tools.story_figures import (
    BOX,
    INK,
    MUTED,
    RED,
    SHADE,
    arrow,
    cross,
    line,
    markers,
    rect,
    region,
    svg,
    text,
)

STEM = "function_objects_story"
W = 730
LH = 158  # One lane's height
TOP = 40  # Where the first lane begins
AX, AW = 152, 140  # The column where the callables are chosen
FX, FW, FH = 168, 108, 26  # A callable's box
ROWS = (40, 74, 108)  # Each callable's row within a lane
CX, CW, CH = 356, 180, 76  # The call site
OX = 556  # The output column
TITLE = ("Command, Strategy, and Chain of Responsibility as function "
         "objects: one place chooses the callables, and an unchanging "
         "call site calls them knowing only their signature")


def row_y(y0: float, k: int) -> float:
    return y0 + ROWS[k]


def lane(y0: float, names: tuple[str, ...], defers: str,
         gloss: tuple[str, ...]) -> str:
    """The gutter and the separator every lane shares."""
    out = line((16, y0), (W - 16, y0))
    for j, s in enumerate(names):
        out += text(20, y0 + 28 + j * 16, s, 13, bold=True)
    gy = y0 + 28 + len(names) * 16
    out += text(20, gy + 4, defers, 11.5, RED)
    for j, s in enumerate(gloss):
        out += text(20, gy + 24 + j * 14, s, 10.5, MUTED)
    return out


def callables(y0: float, labels: tuple[str, ...],
              muted: int = -1) -> str:
    out = ""
    for k, s in enumerate(labels):
        y = row_y(y0, k)
        out += rect(FX, y, FW, FH)
        out += text(FX + FW / 2, y + 17, s, 11,
                    MUTED if k == muted else INK, "middle")
    return out


def code(x: float, y: float, s: str, size: float, fill: str,
         bold: bool = False) -> str:
    """A line of code whose leading spaces indent it, as SVG drops them."""
    body = s.lstrip(" ")
    return text(x + (len(s) - len(body)) * 0.6 * size, y, body, size, fill,
                bold=bold)


def call_site(y0: float, context: tuple[str, ...], call: str,
              sees: str) -> str:
    """The red box: the lines around the call, then the call."""
    top = y0 + (LH - CH) / 2 - 6
    out = rect(CX, top, CW, CH, stroke=RED, width=1.6)
    n = len(context) + 1
    first = top + CH / 2 - (n - 1) * 8 + 4
    for j, s in enumerate(context):
        out += code(CX + 10, first + j * 16, s, 10, MUTED)
    out += code(CX + 10, first + len(context) * 16, call, 11, RED,
                bold=True)
    out += text(CX + CW / 2, top + CH + 16, sees, 10, MUTED, "middle")
    return out


def outputs(y0: float, lines: tuple[tuple[str, str], ...],
            head: str = "") -> str:
    """One output line beside each callable's row, under the run's call."""
    out = text(OX, y0 + 30, head, 10, MUTED) if head else ""
    return out + "".join(text(OX, row_y(y0, k) + 17, s, 10.5, fill)
                   for k, (s, fill) in enumerate(lines))


def render() -> str:
    y = [TOP + i * LH for i in range(3)]
    b = region(AX - 8, 8, AW + 16, TOP + 3 * LH - 12, fill=SHADE, r=0)
    b += text(AX + AW / 2, 26, "one place chooses", 11, MUTED, "middle")
    b += text(CX + CW / 2, 26, "another place calls", 11, MUTED, "middle")
    b += text(OX, 26, "result", 11, MUTED)

    y0 = y[0]
    b += lane(y0, ("Command",), "defers what",
              ("store the", "actions and", "run them later"))
    b += region(AX, y0 + 12, AW, LH - 26, stroke=BOX, width=1)
    b += text(AX + 8, y0 + 30, "macro", 10, MUTED)
    b += callables(y0, ("no_more", "ceased", "fjords"))
    mid = y0 + (LH - 12) / 2
    b += arrow((AX + AW, mid), (CX, mid), INK, "fo-ink")
    b += text((AX + AW + CX) / 2, mid - 8, "later", 10, INK, "middle")
    b += call_site(y0, ("for command in macro:",), "    command()",
                   "sees only Command")
    b += outputs(y0, (("This parrot is no more.", INK),
                      ("It has ceased to be.", INK),
                      ("It's pining for the fjords.", INK)))

    y0 = y[1]
    b += lane(y0, ("Strategy",), "defers how",
              ("the caller", "passes the", "algorithm"))
    b += text(AX + 8, y0 + 30, "one per call", 10, MUTED)
    b += callables(y0, ("bisection", "newton", "secant"))
    mid = y0 + (LH - 12) / 2
    for k in range(3):
        a = (FX + FW, row_y(y0, k) + FH / 2)
        b += arrow(a, (CX, mid + (k - 1) * 14), INK, "fo-ink")
    b += text((FX + FW + CX) / 2, mid - 30, "any one", 10, INK, "middle")
    b += call_site(y0, ("def solve(..., finder):",),
                   "    finder(f, a, b)", "sees only RootFinder")
    b += outputs(y0, (("1.414214", INK), ("1.414214", INK),
                      ("1.414214", INK)), "solve(f, 0.0, 2.0, finder)")

    y0 = y[2]
    b += lane(y0, ("Chain of", "Responsibility"), "defers which",
              ("tries each", "until one", "succeeds"))
    b += region(AX, y0 + 12, AW, LH - 26, stroke=BOX, width=1)
    b += text(AX + 8, y0 + 30, "chain", 10, MUTED)
    b += callables(y0, ("bisection", "secant", "newton"), muted=2)
    mid = y0 + (LH - 12) / 2
    b += arrow((AX + AW, mid), (CX, mid), INK, "fo-ink")
    b += text((AX + AW + CX) / 2, mid - 8, "in order", 10, INK, "middle")
    b += call_site(y0, ("def solve(..., chain):",
                        "    for finder in chain:"),
                   "        finder(f, a, b)", "sees only RootFinder")
    b += outputs(y0, (("bisection: None", MUTED),
                      ("secant: 1.414214", INK),
                      ("newton: never runs", MUTED)),
                 "solve(f, 1.0, 1.3, chain)")
    b += cross(OX + 15 * 6.3 + 12, row_y(y0, 0) + 13, 5)

    defs = markers(**{"fo-ink": ("filled", INK)})
    return svg(W, TOP + 3 * LH, TITLE, defs, b)
