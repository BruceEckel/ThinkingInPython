#!/usr/bin/env python3
"""Generate the book cover and favicon from one parametric design.

The artwork is an M. C. Escher-inspired ouroboros: a python whose
body traces a lemniscate (infinity sign) and whose mouth closes on
its own tail. The body is a ribbon of alternating tessellated
segments in the site's palette, woven over/under at the central
crossing the way Escher's "Knots" woodcuts weave.

Everything is computed here and emitted as SVG, so the design is a
program, not a binary asset. Outputs, all under resources/static/:

- cover.svg          master cover (site + PDF, vector)
- cover-eink.svg     grayscale variant for the e-ink EPUB
- cover-color.png    1600x2560 raster for the color EPUB (Kindle
                     sleep screens show the cover full-bleed)
- cover-eink.png     the same for the e-ink EPUB
- favicon.svg        stripped-down angular infinity + diamond head

Rasterization uses resvg (the same renderer build_epub.py uses for
diagrams). Text is set in Palatino Linotype, which ships with
Windows and macOS; regenerate on a machine that has it.

Usage:
    uv run python tools/make_cover.py            # write everything
    uv run python tools/make_cover.py --preview  # small PNG preview
"""

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "resources" / "static"

# Page geometry (SVG user units). 1:1.6, Kindle's cover ratio.
W, H = 1000, 1600

# The site's palette (build_site.py), so every surface matches.
PAPER = "#f5f0e8"
INK = "#1a1612"
ACCENT = "#8b1a1a"
MUTED = "#7a6e62"

# E-ink variant: same drawing, no color.
EINK = {ACCENT: "#555049", MUTED: "#555049"}

TITLE_FONT = "Palatino Linotype, Palatino, Georgia, serif"


# --------------------------------------------------------------------------- #
# The serpent's spine: a lemniscate of Bernoulli
# --------------------------------------------------------------------------- #
def lemniscate(t: float, a: float) -> tuple[float, float]:
    """Point on the lemniscate for parameter t, half-width a."""
    d = 1 + math.sin(t) ** 2
    return (a * math.cos(t) / d,
            a * math.sin(t) * math.cos(t) / d)


def spine(a: float, cx: float, cy: float,
          t_head: float, t_tail: float,
          n: int) -> list[tuple[float, float]]:
    """Sampled spine from head parameter to tail parameter.

    The head sits just past the crossing on the right lobe and the
    body runs the long way around both lobes, so the mouth meets
    the tail after a full figure-eight.
    """
    points = []
    for i in range(n + 1):
        t = t_head + (t_tail - t_head) * i / n
        x, y = lemniscate(t, a)
        points.append((cx + x, cy - y))
    return points


def widths(n: int, w_head: float, w_tail: float) -> list[float]:
    """Ribbon half-widths: thick behind the head, tapering tail."""
    out = []
    for i in range(n + 1):
        u = i / n
        # Ease-out taper: stays thick for most of the body.
        w = w_tail + (w_head - w_tail) * (1 - u) ** 1.6
        out.append(w)
    return out


def normals(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Unit normals per point, from central differences."""
    out = []
    for i in range(len(pts)):
        x0, y0 = pts[max(i - 1, 0)]
        x1, y1 = pts[min(i + 1, len(pts) - 1)]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1.0
        out.append((-dy / length, dx / length))
    return out


def edge(pts: list[tuple[float, float]],
         nrm: list[tuple[float, float]],
         hw: list[float], side: float) -> list[tuple[float, float]]:
    return [(x + side * hw[i] * nx, y + side * hw[i] * ny)
            for i, ((x, y), (nx, ny)) in enumerate(zip(pts, nrm))]


def poly(points: list[tuple[float, float]], fill: str,
         extra: str = "") -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{coords}" fill="{fill}" {extra}/>'


def path_d(points: list[tuple[float, float]]) -> str:
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


# --------------------------------------------------------------------------- #
# Building the woven, tessellated body
# --------------------------------------------------------------------------- #
def strand(left: list[tuple[float, float]],
           right: list[tuple[float, float]],
           s: int, e: int, step: int) -> str:
    """Slanted bands plus edge outlines for spine samples s..e.

    Each band leads by half a step on the left edge, so the seams
    run diagonally: chevrons, not rings.
    """
    parts = []
    cycle = (INK, ACCENT)
    lead = step // 2
    last = len(left) - 1
    for b in range(s, e, step):
        b2 = min(b + step, e)
        lo, hi = min(b + lead, last), min(b2 + lead, last)
        quad = left[lo:hi + 1] + right[b:b2 + 1][::-1]
        parts.append(poly(quad, cycle[(b // step) % 2]))
    parts.append(
        f'<path d="{path_d(left[s:e + 1])}" fill="none" '
        f'stroke="{INK}" stroke-width="4"/>'
        f'<path d="{path_d(right[s:e + 1])}" fill="none" '
        f'stroke="{INK}" stroke-width="4"/>')
    return "".join(parts)


def body_svg(a: float, cx: float, cy: float) -> str:
    """The serpent: a woven figure-eight with a banded body."""
    # Head at the right lobe's outer edge, facing back along the
    # curve; the tail arrives one full figure-eight later and
    # stops a small gap short, inside the mouth.
    t_head = -0.47
    t_tail = t_head + 2 * math.pi - 0.30
    n = 630
    pts = spine(a, cx, cy, t_head, t_tail, n)
    nrm = normals(pts)
    hw = widths(n, 52.0, 9.0)
    left = edge(pts, nrm, hw, +1.0)
    right = edge(pts, nrm, hw, -1.0)
    step = 10

    # The spine passes through the crossing at t = pi/2 (early,
    # drawn under) and t = 3pi/2 (late, drawn over with a paper
    # halo so the under-strand visibly dips beneath).
    def idx(t: float) -> int:
        return round((t - t_head) / (t_tail - t_head) * n)

    o_s = max(idx(3 * math.pi / 2 - 0.55), 0)
    o_e = min(idx(3 * math.pi / 2 + 0.55), n)

    under = strand(left, right, 0, n, step)
    halo = (edge(pts, nrm, [w + 22 for w in hw], +1.0)
            [o_s:o_e + 1]
            + edge(pts, nrm, [w + 22 for w in hw], -1.0)
            [o_s:o_e + 1][::-1])
    # Start the redraw on a band boundary so its bands land
    # exactly on the ones drawn underneath.
    over = poly(halo, PAPER) + strand(
        left, right, (o_s // step) * step, o_e, step)
    head = head_svg(pts, nrm, hw, left, right, n, step)
    return under + over + head


def head_svg(pts: list[tuple[float, float]],
             nrm: list[tuple[float, float]],
             hw: list[float],
             left: list[tuple[float, float]],
             right: list[tuple[float, float]],
             n: int, step: int) -> str:
    """An angular head at the spine's start, jaws on the tail."""
    (hx, hy), (nx, ny) = pts[0], nrm[0]
    # The head faces backwards along the parameter direction,
    # toward the arriving tail.
    x2, y2 = pts[4]
    fx, fy = hx - x2, hy - y2
    fl = math.hypot(fx, fy) or 1.0
    fx, fy = fx / fl, fy / fl
    w = hw[0]
    length = w * 3.1
    base_l = (hx + nx * w * 1.35, hy + ny * w * 1.35)
    base_r = (hx - nx * w * 1.35, hy - ny * w * 1.35)
    rear = (hx - fx * w * 1.1, hy - fy * w * 1.1)
    snout = (hx + fx * length, hy + fy * length)
    head = poly([base_l, snout, base_r, rear], INK)
    # An open mouth: a paper wedge cut back from the snout.
    m_deep = (hx + fx * w * 1.1, hy + fy * w * 1.1)
    m_up = (hx + fx * length * 0.92 + nx * w * 0.34,
            hy + fy * length * 0.92 + ny * w * 0.34)
    m_dn = (hx + fx * length * 0.92 - nx * w * 0.34,
            hy + fy * length * 0.92 - ny * w * 0.34)
    mouth = poly([m_deep, m_up, m_dn], PAPER)
    # Redraw the last stretch of tail so it lies inside the
    # jaws, then close the upper jaw over it: swallowed.
    tail = strand(left, right, n - 4 * step, n, step)
    jaw = poly([m_deep, m_up, snout], INK)
    tail += jaw
    # Eye: a paper diamond with an ink pupil, set high and back.
    ex = hx + fx * w * 0.1 + nx * w * 0.62
    ey = hy + fy * w * 0.1 + ny * w * 0.62
    r = w * 0.30
    eye = poly([(ex + r, ey), (ex, ey + r),
                (ex - r, ey), (ex, ey - r)], PAPER)
    pupil = poly([(ex + r * .45, ey), (ex, ey + r * .45),
                  (ex - r * .45, ey), (ex, ey - r * .45)], INK)
    return head + mouth + tail + eye + pupil


# --------------------------------------------------------------------------- #
# Assembling the cover page
# --------------------------------------------------------------------------- #
def cover_svg(h: int = H) -> str:
    """The full cover at width W and any height (Kindle's 1600
    tall, or 1294 for a full-bleed US Letter PDF page)."""
    art = body_svg(a=415, cx=W / 2, cy=h * 0.505)
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {h}" width="{W}" height="{h}">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  <text x="{W / 2}" y="170" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="92"
        fill="{INK}">Thinking</text>
  <text x="{W / 2}" y="280" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="92"
        fill="{INK}">in Python</text>
  <rect x="{W / 2 - 60}" y="330" width="120" height="4"
        fill="{ACCENT}"/>
  {art}
  <text x="{W / 2}" y="{h - 90}" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="44"
        letter-spacing="10" fill="{INK}">BRUCE ECKEL</text>
</svg>'''


def art_svg() -> str:
    """The serpent alone, for the site's index page."""
    art = body_svg(a=415, cx=W / 2, cy=280)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {W} 560">{art}</svg>')


def favicon_svg() -> str:
    """Angular infinity polyline with a diamond head, on paper."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="{PAPER}"/>
  <path d="M16 16 L9 10 L4 16 L9 22 L16 16 L23 10 L28 16
           L23 22 L20.4 19.8"
        fill="none" stroke="{INK}" stroke-width="3.2"
        stroke-linejoin="miter"/>
  <path d="M16.4 16.4 L21.2 17.6 L18.4 20.9 Z"
        fill="{ACCENT}"/>
</svg>'''


def eink(svg: str) -> str:
    for src, dst in EINK.items():
        svg = svg.replace(src, dst)
    return svg


def rasterize(svg_path: Path, png_path: Path, width: int) -> None:
    resvg = shutil.which("resvg")
    if resvg is None:
        raise SystemExit("resvg not found; scoop install resvg")
    subprocess.run(
        [resvg, "--width", str(width), str(svg_path),
         str(png_path)],
        check=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preview", action="store_true",
                    help="write a small preview PNG only")
    args = ap.parse_args(argv)

    STATIC.mkdir(parents=True, exist_ok=True)
    master = cover_svg()
    (STATIC / "cover.svg").write_text(master, encoding="utf-8")
    if args.preview:
        rasterize(STATIC / "cover.svg",
                  STATIC / "cover-preview.png", 500)
        print("wrote cover-preview.png")
        return 0
    (STATIC / "cover-eink.svg").write_text(
        eink(master), encoding="utf-8")
    (STATIC / "cover-letter.svg").write_text(
        cover_svg(h=1294), encoding="utf-8")
    (STATIC / "cover-art.svg").write_text(
        art_svg(), encoding="utf-8")
    (STATIC / "favicon.svg").write_text(
        favicon_svg(), encoding="utf-8")
    rasterize(STATIC / "cover.svg",
              STATIC / "cover-color.png", 1600)
    rasterize(STATIC / "cover-eink.svg",
              STATIC / "cover-eink.png", 1600)
    for name in ("cover.svg", "cover-eink.svg",
                 "cover-letter.svg", "cover-art.svg",
                 "favicon.svg",
                 "cover-color.png", "cover-eink.png"):
        size = (STATIC / name).stat().st_size
        print(f"{name}: {size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
