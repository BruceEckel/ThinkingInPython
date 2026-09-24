"""Generate chapter 31's vending-machine state diagram.

`resources/images/stateMachine.svg` is drawn from the spec below rather
than by hand, because the figure's hard part is geometry: thirteen
curved transitions among five states, each with a label that has to sit
beside its own curve and clear of every other. By hand, that meant
guessing coordinates, and the labels drifted until one sat a hundred
units from its edge. Here a transition names its two states, how far its
curve bows, and where along the curve its label goes; the script
computes the endpoints on each circle, the curve, the label's side, and
the arrowhead trim from `tools/arrowheads.py`.

    uv run python -m tools.state_machine_figure            # write it
    uv run python -m tools.state_machine_figure --check    # report drift

`--check` regenerates in memory and exits nonzero if the committed SVG
differs; `make state-machine-figure` runs it in the gate, the way
`make coupling-panels` guards the panels. After a spec edit, rasterize
with `make figures` and look at the PNG in the gallery: nothing here
detects two labels colliding.

Geometry, for editing the spec. A transition's curve is a quadratic
whose apex sits `bend` units off the chord between the two circles, to
the left of travel (in SVG's y-down frame) for a positive `bend`. The
two directions of a pair therefore bow apart when they share a `bend`
sign. `spread` rotates both endpoints off the center line, in radians,
so a pair meets each circle at two points. The label sits at `at` along
the curve (0 at the source, 1 at the target), `GAP` units off it on the
bowed side, with `nudge` added last for a label that needs moving
anyway.
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass

from tools.arrowheads import HEADS, marker_def, shorten_curve
from tools.config import ROOT

INK = "#1a1612"
MUTED = "#7a6e62"
MARK = "#8b1a1a"
OUT = ROOT / "resources" / "images" / "stateMachine.svg"
VIEW_BOX = "40 -100 770 740"
GAP = 8
LINE_HEIGHT = 13.5
TRIM = HEADS["filled"].trim


@dataclass(frozen=True)
class State:
    x: float
    y: float
    r: float
    stroke: str = INK
    width: float = 1.6

    def rim(self, angle: float) -> tuple[float, float]:
        return (self.x + self.r * math.cos(angle),
                self.y + self.r * math.sin(angle))


STATES: dict[str, State] = {
    "QUIESCENT": State(110, 330, 50),
    "COLLECTING": State(380, 150, 52),
    "SELECTING": State(410, 350, 58, MARK, 1.8),
    "UNAVAILABLE": State(720, 220, 52),
    "WANT_MORE": State(720, 500, 52),
}


@dataclass(frozen=True)
class Transition:
    """`label` is the event, then any `[guard]`, then the `/ action`."""
    src: str
    dst: str
    bend: float
    label: tuple[str, ...]
    spread: float = 0.25
    at: float = 0.5
    nudge: tuple[float, float] = (0, 0)


TRANSITIONS: tuple[Transition, ...] = (
    Transition("QUIESCENT", "COLLECTING", 22, ("Money", "/ add_money"),
               at=0.72),
    Transition("COLLECTING", "QUIESCENT", 22, ("Quit", "/ refund"), at=0.78),
    Transition("COLLECTING", "SELECTING", -20,
               ("FirstDigit", "/ choose_row"), 0.3, at=0.62),
    Transition("SELECTING", "COLLECTING", -20,
               ("SecondDigit", "[too_expensive]", "/ clear"), 0.3,
               nudge=(0, -40)),
    Transition("SELECTING", "UNAVAILABLE", -18,
               ("SecondDigit", "[sold_out]", "/ clear")),
    Transition("UNAVAILABLE", "SELECTING", -18,
               ("FirstDigit", "/ choose_row"), nudge=(40, -4)),
    Transition("SELECTING", "WANT_MORE", -18,
               ("SecondDigit", "[else]", "/ dispense")),
    Transition("WANT_MORE", "SELECTING", -18,
               ("FirstDigit", "/ choose_row"), at=0.3),
    Transition("SELECTING", "QUIESCENT", 28, ("Quit", "/ refund"), 0.2),
    # The two long Quit arcs: over COLLECTING, and under SELECTING.
    Transition("UNAVAILABLE", "QUIESCENT", -300, ("Quit", "/ refund"), 0.6),
    Transition("WANT_MORE", "QUIESCENT", 150, ("Quit", "/ refund"), 0.6),
)

# The self-loop has no chord to bow off, so it is a cubic over the top.
LOOP_STATE = "COLLECTING"
LOOP_LABEL = ("Money", "/ add_money")


def label_svg(x: float, y: float, nx: float, ny: float,
              lines: tuple[str, ...]) -> str:
    """`lines` set off the point (x, y) toward the unit normal (nx, ny)."""
    anchor = "start" if nx > 0.35 else "end" if nx < -0.35 else "middle"
    height = LINE_HEIGHT * len(lines)
    if ny < -0.35:
        top = y - GAP - height + 10
    elif ny > 0.35:
        top = y + GAP + 10
    else:
        top = y - height / 2 + 10
    out = ""
    for i, line in enumerate(lines):
        action = line.startswith("/")
        size, fill = ("11", MUTED) if action else ("11.5", MARK)
        out += (f'  <text x="{x + nx * GAP:.0f}" y="{top + i * LINE_HEIGHT:.0f}" '
                f'font-size="{size}" fill="{fill}" text-anchor="{anchor}">'
                f"{line}</text>\n")
    return out


def transition_svg(t: Transition) -> str:
    a, b = STATES[t.src], STATES[t.dst]
    angle = math.atan2(b.y - a.y, b.x - a.x)
    side = 1 if t.bend >= 0 else -1
    s = a.rim(angle - t.spread * side)
    e = b.rim(angle + math.pi + t.spread * side)
    length = math.dist(s, e)
    nx, ny = (e[1] - s[1]) / length, -(e[0] - s[0]) / length
    c = ((s[0] + e[0]) / 2 + 2 * t.bend * nx,
         (s[1] + e[1]) / 2 + 2 * t.bend * ny)
    # The label's point and the curve's normal there, before the trim.
    u = t.at
    px = (1 - u) ** 2 * s[0] + 2 * (1 - u) * u * c[0] + u * u * e[0]
    py = (1 - u) ** 2 * s[1] + 2 * (1 - u) * u * c[1] + u * u * e[1]
    tx = 2 * (1 - u) * (c[0] - s[0]) + 2 * u * (e[0] - c[0])
    ty = 2 * (1 - u) * (c[1] - s[1]) + 2 * u * (e[1] - c[1])
    tl = math.hypot(tx, ty)
    _, c, e = shorten_curve([s, c, e], TRIM)
    return (f"  <!-- {t.src} -> {t.dst} -->\n"
            f'  <path d="M{s[0]:.1f},{s[1]:.1f} Q{c[0]:.1f},{c[1]:.1f} '
            f'{e[0]:.1f},{e[1]:.1f}" fill="none" stroke="{MUTED}" '
            f'stroke-width="1.2" marker-end="url(#sm-muted)"/>\n'
            + label_svg(px + t.nudge[0], py + t.nudge[1],
                        side * ty / tl, side * -tx / tl, t.label))


def loop_svg() -> str:
    st = STATES[LOOP_STATE]
    s = st.rim(math.radians(-120))
    e = st.rim(math.radians(-60))
    top = st.y - st.r - 75
    _, c1, c2, e = shorten_curve(
        [s, (st.x - 70, top), (st.x + 70, top), e], TRIM)
    return (f"  <!-- {LOOP_STATE} self-loop -->\n"
            f'  <path d="M{s[0]:.1f},{s[1]:.1f} C{c1[0]:.1f},{c1[1]:.1f} '
            f'{c2[0]:.1f},{c2[1]:.1f} {e[0]:.1f},{e[1]:.1f}" fill="none" '
            f'stroke="{MUTED}" stroke-width="1.2" '
            f'marker-end="url(#sm-muted)"/>\n'
            + label_svg(st.x + 48, st.y - st.r - 50, 1, 0, LOOP_LABEL))


def render() -> str:
    body = ""
    for name, st in STATES.items():
        body += (f'  <circle cx="{st.x:g}" cy="{st.y:g}" r="{st.r:g}" '
                 f'fill="none" stroke="{st.stroke}" '
                 f'stroke-width="{st.width:g}"/>\n'
                 f'  <text x="{st.x:g}" y="{st.y + 5:g}" font-size="13.5" '
                 f'font-weight="bold" fill="{INK}" text-anchor="middle">'
                 f"{name}</text>\n")
    q = STATES["QUIESCENT"]
    top = q.y - q.r
    body += ("  <!-- initial-state marker -->\n"
             f'  <circle cx="{q.x:g}" cy="{top - 40:g}" r="6" fill="{INK}"/>\n'
             f'  <line x1="{q.x:g}" y1="{top - 34:g}" x2="{q.x:g}" '
             f'y2="{top - TRIM:.1f}" stroke="{INK}" stroke-width="1.4" '
             f'marker-end="url(#sm-ink)"/>\n')
    body += "".join(transition_svg(t) for t in TRANSITIONS) + loop_svg()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEW_BOX}"\n'
            "     font-family=\"'JetBrains Mono', Consolas, monospace\">\n"
            "  <title>Vending machine state diagram</title>\n  <defs>\n"
            + marker_def("sm-ink", "filled", INK)
            + marker_def("sm-muted", "filled", MUTED)
            + "  </defs>\n" + body + "</svg>\n")


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
            print("state machine figure: in sync")
            return 0
        print(f"state machine figure: {name} differs from the spec; "
              "rerun without --check")
        return 1
    if current != body:
        OUT.write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
