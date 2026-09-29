"""Generate chapter 30's Observer storyboard.

`resources/images/observer_story.svg` opens the Observer chapter in
place of the coupling panel the other pattern chapters carry. A class
diagram shows which way knowledge points, but Observer is about what
happens over time, so this figure is four frames of one layout:
responders subscribe, an assignment to `celsius` calls each one, each
reacts and none replies, and a new responder subscribes with no edit
to `Thermometer`. The shaded region on the right is what `Thermometer`
cannot see; its list holds only callables. The names are the ones in
`thermometer_demo.py` and `broadcaster.py` (`display` and `alarm` are
that demo's two lambdas; `plot` is dashed because no listing has it).

    uv run python -m tools.observer_story_figure            # write it
    uv run python -m tools.observer_story_figure --check    # report drift

`--check` regenerates in memory and exits nonzero if the committed SVG
differs; `tip observer-story-figure` runs it in the gate. After an
edit, look at the PNG in `tip figures`: nothing here detects two labels
colliding.

The `Thermometer` outline and the shaded region are paths, not rects.
`arrowheads.tight_tips()` measures a tip against the rects and circles
around it, and a slot inside the thermometer box, or a responder inside
the shaded region, would otherwise read as a tip buried in the outer
shape.
"""

import argparse
import sys

from tools.arrowheads import HEADS, marker_def, shorten_line
from tools.config import ROOT

OUT = ROOT / "resources" / "images" / "observer_story.svg"
INK, BOX, MUTED, RED = "#1a1612", "#c8bfb0", "#7a6e62", "#8b1a1a"
W = 730
FH = 190  # One frame's height
TX, TW = 140, 250  # The Thermometer box
SX, SW, SH = 285, 95, 26  # The slots in its list
RX, RW, RH = 530, 170, 36  # The responders
HIDE_X = 452  # Where the region Thermometer cannot see begins
SLOT_Y = (50, 94, 138)
RESP_Y = (45, 89, 133)
TIP_GAP = 4  # A tip stops this far short of its target
TITLE = ("Four steps of Observer: responders subscribe as callables, "
         "an assignment to celsius calls each one, none replies, "
         "and a new responder subscribes with no change to Thermometer")


def text(x: float, y: float, s: str, size: float = 11, fill: str = INK,
         anchor: str = "start", bold: bool = False) -> str:
    b = ' font-weight="bold"' if bold else ""
    return (f'  <text x="{x:g}" y="{y:g}" font-size="{size:g}" '
            f'fill="{fill}"{b} text-anchor="{anchor}">{s}</text>\n')


def rect(x: float, y: float, w: float, h: float, stroke: str = BOX,
         width: float = 1.3, dash: bool = False, rx: float = 4) -> str:
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'fill="none" stroke="{stroke}" stroke-width="{width:g}" '
            f'rx="{rx:g}"{d}/>\n')


def outline(x: float, y: float, w: float, h: float, r: float = 4) -> str:
    """Path data for a rounded rectangle."""
    return (f"M{x + r:g},{y:g} H{x + w - r:g} Q{x + w:g},{y:g} "
            f"{x + w:g},{y + r:g} V{y + h - r:g} Q{x + w:g},{y + h:g} "
            f"{x + w - r:g},{y + h:g} H{x + r:g} Q{x:g},{y + h:g} "
            f"{x:g},{y + h - r:g} V{y + r:g} Q{x:g},{y:g} {x + r:g},{y:g} Z")


def arrow(a: tuple[float, float], b: tuple[float, float], color: str,
          marker: str, kind: str = "filled", dash: bool = False,
          width: float = 1.3) -> str:
    ex, ey = shorten_line(a, b, TIP_GAP + HEADS[kind].trim)
    d = ' stroke-dasharray="4,3"' if dash else ""
    return (f'  <line x1="{a[0]:g}" y1="{a[1]:g}" x2="{ex:.1f}" '
            f'y2="{ey:.1f}" stroke="{color}" stroke-width="{width:g}"{d} '
            f'marker-end="url(#{marker})"/>\n')


def slot_mid(y0: float, k: int) -> tuple[float, float]:
    return (SX + SW, y0 + SLOT_Y[k] + SH / 2)


def resp_mid(y0: float, k: int) -> tuple[float, float]:
    return (RX, y0 + RESP_Y[k] + RH / 2)


def resp_label(y0: float, k: int, s: str, fill: str = INK) -> str:
    return text(RX + RW / 2, y0 + RESP_Y[k] + 23, s, 12.5, fill, "middle")


def frame(i: int, y0: float, slots: int, name: str,
          lines: tuple[str, ...]) -> str:
    """The layout every frame shares, with `slots` responders filled."""
    out = ""
    if i:
        out += (f'  <line x1="16" y1="{y0 - 4:g}" x2="{W - 16}" '
                f'y2="{y0 - 4:g}" stroke="{BOX}" stroke-width="0.8"/>\n')
    out += (f'  <path d="{outline(HIDE_X, y0 + 6, W - HIDE_X - 10, FH - 18, 0)}" '
            f'fill="{BOX}" fill-opacity="0.22" stroke="none"/>\n')
    stroke = RED if i == 3 else INK
    out += (f'  <path d="{outline(TX, y0 + 14, TW, FH - 30)}" fill="none" '
            f'stroke="{stroke}" stroke-width="1.6"/>\n')
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


def subscribe(y0: float, k: int, s: str) -> str:
    a, t = resp_mid(y0, k), slot_mid(y0, k)
    return (arrow(a, t, INK, "os-ink")
            + text((a[0] + t[0]) / 2 + 10, t[1] - 6, f"t.subscribe({s})", 10,
                   INK, "middle"))


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, 2, "subscribe",
               ("each responder", "is stored as", "a callable"))
    b += text(W - 18, y0 + 24, "hidden from Thermometer", 10, MUTED, "end")
    b += text(TX + 12, y0 + 70, "celsius: 20.0", 11)
    for k, s in enumerate(("display", "alarm")):
        b += resp_label(y0, k, s) + subscribe(y0, k, s)

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
        mx, my = (a[0] + t[0]) / 2, t[1]
        b += (f'  <path d="M{mx - 6:g},{my - 6:g} L{mx + 6:g},{my + 6:g} '
              f'M{mx - 6:g},{my + 6:g} L{mx + 6:g},{my - 6:g}" '
              f'stroke="{RED}" stroke-width="2" fill="none"/>\n')
    b += text((RX + SX + SW) / 2, y0 + SLOT_Y[0] + SH / 2 - 10,
              "returns None", 10, MUTED, "middle")

    y0 = y[3]
    b += frame(3, y0, 3, "extend",
               ("a new responder", "subscribes the", "same way"))
    b += text(TX + 12, y0 + 70, "no edit to", 11, RED)
    b += text(TX + 12, y0 + 85, "Thermometer", 11, RED)
    for k, s in enumerate(("display", "alarm", "plot")):
        b += resp_label(y0, k, s, MUTED if k == 2 else INK)
    b += subscribe(y0, 2, "plot")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {W} {10 + 4 * FH}"\n'
            "     font-family=\"'JetBrains Mono', Consolas, monospace\">\n"
            f"  <title>{TITLE}</title>\n  <defs>\n"
            + marker_def("os-ink", "filled", INK)
            + marker_def("os-red", "filled", RED)
            + marker_def("os-muted", "open", MUTED)
            + "  </defs>\n" + b + "</svg>\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report whether the SVG differs from the spec; "
                         "write nothing")
    args = ap.parse_args(argv)
    body = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    name = OUT.relative_to(ROOT).as_posix()
    if args.check:
        if current == body:
            print("observer story figure: in sync")
            return 0
        print(f"observer story figure: {name} differs from the spec; "
              "rerun without --check")
        return 1
    if current != body:
        OUT.write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
