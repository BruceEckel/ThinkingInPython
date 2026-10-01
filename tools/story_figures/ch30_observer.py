"""Chapter 30, Observer: four frames of one notification.

Four frames of one layout, so only the changes stand out: responders
connect, an assignment to `celsius` calls each one, each reacts and
none replies, and a new responder connects with no edit to
`Thermometer`. The shaded region on the right is what `Thermometer`
cannot see; its list holds only callables. The names are the ones in
`thermometer_demo.py` and `broadcaster.py` (`display` and `alarm` are
that demo's two lambdas; `plot` is dashed because no listing has it).
"""

from tools.story_figures import (
    BOX,
    INK,
    MUTED,
    RED,
    SHADE,
    Point,
    arrow,
    cross,
    line,
    markers,
    rect,
    region,
    svg,
    text,
)

STEM = "observer_story"
W = 730
FH = 190  # One frame's height
TX, TW = 140, 250  # The Thermometer box
SX, SW, SH = 285, 95, 26  # The slots in its list
RX, RW, RH = 530, 170, 36  # The responders
HIDE_X = 452  # Where the region Thermometer cannot see begins
SLOT_Y = (50, 94, 138)
RESP_Y = (45, 89, 133)
TITLE = ("Four steps of Observer: responders connect as callables, "
         "an assignment to celsius calls each one, none replies, "
         "and a new responder connects with no change to Thermometer")


def slot_mid(y0: float, k: int) -> Point:
    return (SX + SW, y0 + SLOT_Y[k] + SH / 2)


def resp_mid(y0: float, k: int) -> Point:
    return (RX, y0 + RESP_Y[k] + RH / 2)


def resp_label(y0: float, k: int, s: str, fill: str = INK) -> str:
    return text(RX + RW / 2, y0 + RESP_Y[k] + 23, s, 12.5, fill, "middle")


def frame(i: int, y0: float, slots: int, name: str,
          lines: tuple[str, ...]) -> str:
    """The layout every frame shares, with `slots` responders filled."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += region(HIDE_X, y0 + 6, W - HIDE_X - 10, FH - 18, fill=SHADE, r=0)
    out += region(TX, y0 + 14, TW, FH - 30, stroke=RED if i == 3 else INK)
    out += text(TX + 12, y0 + 34, "Thermometer", 13, bold=True)
    out += text(SX, y0 + 44, "_responders", 10, MUTED)
    for k, sy in enumerate(SLOT_Y):
        filled = k < slots
        out += rect(SX, y0 + sy, SW, SH, stroke=INK if filled else BOX,
                    width=1.1, dash=not filled, rx=3)
        if filled:
            out += text(SX + SW / 2, y0 + sy + 17, "callable", 10.5, MUTED,
                        "middle")
    for k in range(slots):
        out += rect(RX, y0 + RESP_Y[k], RW, RH, dash=(k == 2))
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def connect(y0: float, k: int, s: str) -> str:
    a, t = resp_mid(y0, k), slot_mid(y0, k)
    return (arrow(a, t, INK, "os-ink")
            + text((a[0] + t[0]) / 2 + 10, t[1] - 6, f"t.connect({s})", 10,
                   INK, "middle"))


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, 2, "connect",
               ("each responder", "is stored as", "a callable"))
    b += text(W - 18, y0 + 24, "hidden from Thermometer", 10, MUTED, "end")
    b += text(TX + 12, y0 + 70, "celsius: 20.0", 11)
    for k, s in enumerate(("display", "alarm")):
        b += resp_label(y0, k, s) + connect(y0, k, s)

    y0 = y[1]
    b += frame(1, y0, 2, "change",
               ("t.celsius = 150", "runs the setter,", "which announces"))
    b += text(TX + 12, y0 + 70, "celsius: 150", 11, RED)
    b += text(TX + 12, y0 + 92, "announce(150)", 11, RED)
    b += text(TX + 12, y0 + 110, "iterates", 10, MUTED)
    b += text(TX + 12, y0 + 124, "through the list", 10, MUTED)
    for k, s in enumerate(("display", "alarm")):
        a, t = slot_mid(y0, k), resp_mid(y0, k)
        b += resp_label(y0, k, s)
        b += arrow(a, t, RED, "os-red", width=1.6)
        b += text((a[0] + t[0]) / 2, a[1] - 6, "responder(150)", 10, RED,
                  "middle")

    y0 = y[2]
    b += frame(2, y0, 2, "respond",
               ("each reacts in", "its own way;", "none replies"))
    b += text(TX + 12, y0 + 70, "celsius: 150", 11)
    b += text(TX + 12, y0 + 92, "announce()", 11)
    b += text(TX + 12, y0 + 106, "returns", 11)
    for k, s in enumerate(("display: 150C", "alarm!")):
        a, t = resp_mid(y0, k), slot_mid(y0, k)
        b += resp_label(y0, k, s, RED)
        b += arrow(a, t, MUTED, "os-muted", kind="open", dash=True)
        b += cross((a[0] + t[0]) / 2, t[1])
    b += text((RX + SX + SW) / 2, y0 + SLOT_Y[0] + SH / 2 - 10,
              "returns None", 10, MUTED, "middle")

    y0 = y[3]
    b += frame(3, y0, 3, "extend",
               ("a new responder", "connects the", "same way"))
    b += text(TX + 12, y0 + 70, "no edit to", 11, RED)
    b += text(TX + 12, y0 + 85, "Thermometer", 11, RED)
    for k, s in enumerate(("display", "alarm", "plot")):
        b += resp_label(y0, k, s, MUTED if k == 2 else INK)
    b += connect(y0, 2, "plot")

    defs = markers(**{"os-ink": ("filled", INK), "os-red": ("filled", RED),
                      "os-muted": ("open", MUTED)})
    return svg(W, 10 + 4 * FH, TITLE, defs, b)
