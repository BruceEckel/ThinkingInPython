"""Draw the chapter-title serpent as an SVG: a trace of
resources/chapter-snake-source.png, Bruce's hand drawing of an
ouroboros coiled into an infinity sign, rebuilt as geometry.

The drawing is a tube outlined in ink, so the figure is its
centerline's two offset curves, stroked, and nothing is filled
but the eye. The centerline is a Gerono lemniscate,
x = A sin t, y = -(B/2) sin 2t, whose loops are near circles,
as the drawing's are. Ink goes where the drawing has ink:

- The body runs from the neck, at the top right of the right
  loop, leftward through the crossing, around the left loop,
  back through the crossing, under the right loop, and up its
  right side, where the tail tapers and ends inside the mouth.
- At the crossing the neck's strand passes over the other:
  the lower strand's outlines stop where they enter the upper
  strand's tube, which is what the drawing shows.
- The head is a wedge hung outward from the loop's top right
  corner and aimed down, so the loop's right side rises beneath
  it into the mouth, open on the head's lower front. The body's
  outlines stop where they enter the head, and the head's
  outline stops where it lies inside the neck's tube, so the
  neck flows into the head with no line across it.

Every cut is a distance test on sampled points, so the SVG is
a handful of polylines and a circle; round caps close the
sampling gaps. `tip cover` (make_cover.py) rasterizes the SVG
to chapter-snake.png for the EPUBs and the PDF, and the site
uses the SVG as it is.

Usage:
    uv run python -m tools.chapter_snake          # write the SVG
    uv run python -m tools.chapter_snake --check  # fail on drift
"""

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "resources" / "static" / "chapter-snake.svg"

type Point = tuple[float, float]

INK = "#1a1612"
# The drawing's frame, which the loops are laid out in; the
# SVG's own viewBox is fitted to the ink afterward.
W, H = 500, 275
CX, CY = W / 2, H / 2
LINE = 5.0          # Outline stroke width
R = 17.0            # Tube half-width at the body
TAIL_R = 6.0        # Tube half-width at the tail's tip
# Loop half-width and half-height, from the frame less the tube
# and a margin.
A = CX - R - LINE / 2 - 8
B2 = CY - R - LINE / 2 - 8
# Where the head hangs (t of the lemniscate, the loop's top
# right corner), how far outward from that point its center
# sits, where the drawn neck ends (t; its cut end lies inside
# the head), and over how much of the path, in t, the tail
# tapers.
T_HEAD = math.pi / 4 + 0.24
HANG = 4.0
T_NECK = T_HEAD - 0.15
TAPER = 1.4
# The head, in its own frame: its axis points ANGLE below the
# horizontal, u runs along it and v across it, positive on the
# lower side, in units of HEAD_L and HEAD_H. HEAD is its outline
# as a closed Catmull-Rom spline through these points, from the
# base of the lower jaw round the back, over the brow, round
# the snout, and back along the upper lip to the hinge, then
# out along the lower jaw to its tip. The mouth is the notch
# between the upper lip and the jaw, open to the lower front,
# where the tail comes up into it and ends BITE of the way in.
ANGLE = math.radians(32)
HEAD_L = 48.0
HEAD_H = 27.0
HEAD = (
    (-0.35, 0.95),    # Base of the lower jaw
    (-0.80, 0.60),    # Throat
    (-1.00, 0.00),    # Back
    (-0.85, -0.55),   # Nape
    (-0.30, -0.75),   # Crown
    (0.35, -0.75),    # Brow
    (0.85, -0.45),    # Snout, top
    (1.00, 0.10),     # Snout, tip
    (0.60, 0.42),     # Upper lip
    (-0.15, 0.45),    # Hinge
    (0.35, 1.25),     # Lower jaw's tip
)
# The mouth's notch, in the same units: what lies here and
# outside the outline is the open mouth.
MOUTH_U = (-0.15, 1.00)
MOUTH_V = (0.30, 1.30)
BITE = 0.65
EYE = (0.35, -0.30)
EYE_R = 4.5
STEPS = 720


def point(t: float) -> Point:
    return CX + A * math.sin(t), CY - B2 * math.sin(2 * t)


def tangent(t: float) -> Point:
    dx, dy = A * math.cos(t), -2 * B2 * math.cos(2 * t)
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def head_frame() -> tuple[float, float, float, float]:
    """The head's center and unit axis: HANG outward from the
    corner along its normal, pointing ANGLE down."""
    x, y = point(T_HEAD)
    tx, ty = tangent(T_HEAD)
    return (x + HANG * ty, y - HANG * tx,
            math.cos(ANGLE), math.sin(ANGLE))


def head_local(p: Point) -> Point:
    """p in the head's frame: u along the axis, v across it,
    positive on the lower side."""
    hx, hy, ax, ay = head_frame()
    return ((p[0] - hx) * ax + (p[1] - hy) * ay,
            -(p[0] - hx) * ay + (p[1] - hy) * ax)


def head_point(u: float, v: float) -> Point:
    hx, hy, ax, ay = head_frame()
    return hx + u * ax - v * ay, hy + u * ay + v * ax


def head_shape() -> list[Point]:
    """The head's outline in its own frame: a closed Catmull-Rom
    spline through HEAD, sampled, in HEAD_L and HEAD_H units."""
    pts = [(u * HEAD_L, v * HEAD_H) for u, v in HEAD]
    n, per = len(pts), 24
    out: list[Point] = []
    for i in range(n):
        p0, p1, p2, p3 = (pts[(i + k - 1) % n] for k in range(4))
        for j in range(per):
            s = j / per
            out.append((spline(p0[0], p1[0], p2[0], p3[0], s),
                        spline(p0[1], p1[1], p2[1], p3[1], s)))
    return out


def spline(a: float, b: float, c: float, d: float,
           s: float) -> float:
    """One coordinate of a Catmull-Rom segment from b to c,
    with a and d as its neighbors, s of the way along."""
    return 0.5 * (2 * b + (c - a) * s
                  + (2 * a - 5 * b + 4 * c - d) * s * s
                  + (3 * b - a - 3 * c + d) * s * s * s)


def inside(u: float, v: float, shape: list[Point]) -> bool:
    """Whether (u, v) lies inside the closed polygon shape."""
    hit = False
    for i in range(len(shape)):
        (u1, v1), (u2, v2) = shape[i - 1], shape[i]
        if (v1 > v) != (v2 > v):
            if u < u1 + (v - v1) * (u2 - u1) / (v2 - v1):
                hit = not hit
    return hit


SHAPE = head_shape()


def in_head(p: Point) -> bool:
    """Whether the head hides p: inside its outline."""
    u, v = head_local(p)
    return inside(u, v, SHAPE)


def head_outline() -> list[Point]:
    """The outline on the page, closed."""
    return [head_point(u, v) for u, v in (*SHAPE, SHAPE[0])]


def in_mouth(p: Point) -> bool:
    """Whether p lies in the open notch between the jaws."""
    u, v = head_local(p)
    return (MOUTH_U[0] * HEAD_L < u < MOUTH_U[1] * HEAD_L
            and MOUTH_V[0] * HEAD_H < v < MOUTH_V[1] * HEAD_H
            and not inside(u, v, SHAPE))


def tail_end() -> float:
    """The t where the tail ends: BITE of the way along the
    centerline's first passage through the mouth past the
    head, entered from below (from larger t)."""
    ts = [T_HEAD + 0.002 * i for i in range(750)]
    inside = [t for t in ts if in_mouth(point(t))]
    if not inside:
        raise SystemExit("the centerline misses the mouth; "
                         "adjust HANG, ANGLE, or the jaws")
    first, last = inside[0], inside[0]
    for t in inside[1:]:
        if t - last > 0.003:
            break
        last = t
    return last - BITE * (last - first)


def radius(t: float, t_start: float) -> float:
    """The tube's half-width at t: R over the body, tapering
    to TAIL_R over the last TAPER of the path (t runs down
    from T_NECK to t_start)."""
    left = t - t_start
    if left >= TAPER:
        return R
    return TAIL_R + (R - TAIL_R) * left / TAPER


def offsets(ts: list[float], t_start: float,
            sign: int) -> list[Point]:
    out = []
    for t in ts:
        x, y = point(t)
        tx, ty = tangent(t)
        r = radius(t, t_start)
        out.append((x - sign * ty * r, y + sign * tx * r))
    return out


def near(p: Point, path: list[Point], r: float) -> bool:
    """Whether p lies within r of any sample on path."""
    x, y = p
    return any(math.hypot(x - px, y - py) < r for px, py in path)


def runs(pts: list[Point], hidden: list[bool]) -> list[list[Point]]:
    """Split pts into the maximal runs of points not hidden."""
    out: list[list[Point]] = []
    run: list[Point] = []
    for p, gone in zip(pts, hidden):
        if not gone:
            run.append(p)
        elif run:
            out.append(run)
            run = []
    if run:
        out.append(run)
    return out


def polyline(pts: list[Point]) -> str:
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'  <polyline points="{d}"/>'


def render() -> str:
    t_end = tail_end() - 2 * math.pi
    ts = [T_NECK - (T_NECK - t_end) * i / STEPS
          for i in range(STEPS + 1)]
    center = [point(t) for t in ts]
    # The neck's strand crosses over: its tube around t = 0
    # cuts the other strand's outlines at t = -pi.
    over = [point(t) for t in ts if abs(t) < 0.9]
    under_t = {t for t in ts if abs(t + math.pi) < 0.9}
    lines: list[list[Point]] = []
    for sign in (1, -1):
        edge = offsets(ts, t_end, sign)
        hidden = [in_head(p) or (
            t in under_t and near(p, over, R + LINE / 2))
            for t, p in zip(ts, edge)]
        lines.extend(runs(edge, hidden))
    neck = [p for t, p in zip(ts, center) if t > T_NECK - 0.6]
    head = head_outline()
    lines.extend(runs(head, [near(p, neck, R) for p in head]))
    ex, ey = head_point(EYE[0] * HEAD_L, EYE[1] * HEAD_H)
    body = "\n".join(polyline(run) for run in lines if len(run) > 1)
    # The frame fits the ink: every drawn point plus half a
    # stroke, so the head's crown sets the top and no side
    # carries slack the site's background-size would leave.
    xs = [x for run in lines for x, _ in run]
    ys = [y for run in lines for _, y in run]
    pad = LINE / 2 + 1
    x0, y0 = math.floor(min(xs) - pad), math.floor(min(ys) - pad)
    x1, y1 = math.ceil(max(xs) + pad), math.ceil(max(ys) + pad)
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">
  <title>A python as an ouroboros, coiled into an infinity sign</title>
  <g fill="none" stroke="{INK}" stroke-width="{LINE:g}"
     stroke-linecap="round" stroke-linejoin="round">
{body}
  </g>
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="{EYE_R:g}" fill="{INK}"/>
</svg>
'''


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed SVG differs")
    args = ap.parse_args(argv)
    svg = render()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != svg:
            print(f"{OUT.relative_to(ROOT)} differs from its spec; "
                  "run: uv run python -m tools.chapter_snake")
            return 1
        print(f"{OUT.relative_to(ROOT)}: up to date")
        return 0
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(svg) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
