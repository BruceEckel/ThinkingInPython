#!/usr/bin/env python3
"""Generate the book cover and favicon, from art or from code.

Two modes, chosen by whether `resources/cover-source.jpg` exists:

- **Art mode** (the usual one): composite that image, whatever its
  size, with the book's typography. Drop in a new image and run
  `make cover` to restyle every distribution at once. The page
  background is sampled from the image's corners so the art sits
  on its own paper color with no visible seam.
- **Drawn mode** (fallback, no source image): a parametric serpent
  computed here: a python coiled into an infinity sign, woven at
  the crossing, swallowing its tail.

Outputs land in resources/static/ and are committed, so the book
builds themselves never need this script's tools (resvg, Pillow).
Each mode deletes the other mode's outputs; the builders accept
either family:

- art mode:   cover-color.jpg, cover-eink.jpg (EPUB covers,
              1600x2560, Kindle's ratio), cover-letter.jpg (the
              PDF's full-bleed first page), cover-art.jpg (site
              index)
- drawn mode: the same four roles as SVG/PNG (cover.svg,
              cover-eink.svg, cover-letter.svg, cover-art.svg,
              cover-color.png, cover-eink.png)
- always:     favicon.svg (an angular infinity with a diamond
              head, per the site's palette)

Text is set in Palatino Linotype, which ships with Windows and
macOS; regenerate on a machine that has it.

Usage:
    uv run python tools/make_cover.py            # everything
    uv run python tools/make_cover.py --preview  # small PNG only
"""

import argparse
import base64
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "resources" / "static"
ART_SOURCE = ROOT / "resources" / "cover-source.jpg"
TEMP = ROOT / "build" / "cover"

# Page geometry (SVG user units). 1:1.6, Kindle's cover ratio;
# 1294 is the same width at US Letter's ratio.
W, H = 1000, 1600
LETTER_H = 1294

# The site's palette (build_site.py), so every surface matches.
PAPER = "#f5f0e8"
INK = "#1a1612"
ACCENT = "#8b1a1a"

# E-ink drawn variant: same drawing, no color.
EINK = {ACCENT: "#555049"}

TITLE_FONT = "Palatino Linotype, Palatino, Georgia, serif"

DRAWN_FILES = ("cover.svg", "cover-eink.svg", "cover-letter.svg",
               "cover-art.svg", "cover-color.png",
               "cover-eink.png")
ART_FILES = ("cover-color.jpg", "cover-eink.jpg",
             "cover-letter.jpg", "cover-art.jpg")


# --------------------------------------------------------------------------- #
# Shared page furniture
# --------------------------------------------------------------------------- #
def titles_svg(h: int, ink: str = INK,
               accent: str = ACCENT) -> str:
    """Title, rule, and author for a page of height h."""
    return f'''<text x="{W / 2}" y="170" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="92"
        fill="{ink}">Thinking</text>
  <text x="{W / 2}" y="280" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="92"
        fill="{ink}">in Python</text>
  <rect x="{W / 2 - 60}" y="330" width="120" height="4"
        fill="{accent}"/>
  <text x="{W / 2}" y="{h - 90}" text-anchor="middle"
        font-family="{TITLE_FONT}" font-size="44"
        letter-spacing="10" fill="{ink}">BRUCE ECKEL</text>'''


def rasterize(svg_path: Path, png_path: Path, width: int) -> None:
    resvg = shutil.which("resvg")
    if resvg is None:
        raise SystemExit("resvg not found; scoop install resvg")
    subprocess.run(
        [resvg, "--width", str(width), str(svg_path),
         str(png_path)],
        check=True)


# --------------------------------------------------------------------------- #
# Art mode: composite a supplied image with the typography
# --------------------------------------------------------------------------- #
def sample_bg(img) -> str:
    """The art's own paper color, averaged from its corners."""
    px = img.convert("RGB")
    w, h = img.size
    corners = [px.getpixel(p) for p in
               ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4))]
    r, g, b = (round(sum(c[i] for c in corners) / 4)
               for i in range(3))
    return f"#{r:02x}{g:02x}{b:02x}"


def art_page_svg(uri: str, iw: int, ih: int, h: int,
                 bg: str) -> str:
    """One cover page: sampled background, art band, titles.

    The art's top and bottom edges are feathered into the page
    background, so a slight mismatch between the sampled corner
    color and the art's interior paper never shows as a seam.
    """
    art_h = W * ih / iw
    y = h * 0.52 - art_h / 2
    feather = 70
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {h}" width="{W}" height="{h}">
  <defs>
    <linearGradient id="ftop" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{bg}" stop-opacity="1"/>
      <stop offset="1" stop-color="{bg}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fbot" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{bg}" stop-opacity="0"/>
      <stop offset="1" stop-color="{bg}" stop-opacity="1"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{h}" fill="{bg}"/>
  <image x="0" y="{y:.0f}" width="{W}" height="{art_h:.0f}"
         href="{uri}"/>
  <rect x="0" y="{y:.0f}" width="{W}" height="{feather}"
        fill="url(#ftop)"/>
  <rect x="0" y="{y + art_h - feather:.0f}" width="{W}"
        height="{feather}" fill="url(#fbot)"/>
  {titles_svg(h)}
</svg>'''


def art_outputs(preview: bool) -> None:
    from PIL import Image, ImageOps

    img = Image.open(ART_SOURCE)
    iw, ih = img.size
    bg = sample_bg(img)
    data = ART_SOURCE.read_bytes()
    uri = ("data:image/jpeg;base64,"
           + base64.b64encode(data).decode("ascii"))
    TEMP.mkdir(parents=True, exist_ok=True)

    def compose(h: int, out_png: Path, width: int) -> None:
        svg = TEMP / f"page-{h}.svg"
        svg.write_text(art_page_svg(uri, iw, ih, h, bg),
                       encoding="utf-8")
        rasterize(svg, out_png, width)

    if preview:
        compose(H, STATIC / "cover-preview.png", 500)
        print("wrote cover-preview.png (art mode)")
        return

    compose(H, TEMP / "kindle.png", 1600)
    compose(LETTER_H, TEMP / "letter.png", 1600)
    kindle = Image.open(TEMP / "kindle.png").convert("RGB")
    kindle.save(STATIC / "cover-color.jpg", quality=87,
                optimize=True)
    gray = ImageOps.autocontrast(ImageOps.grayscale(kindle),
                                 cutoff=1)
    gray.save(STATIC / "cover-eink.jpg", quality=87,
              optimize=True)
    letter = Image.open(TEMP / "letter.png").convert("RGB")
    letter.save(STATIC / "cover-letter.jpg", quality=87,
                optimize=True)
    site = img.convert("RGB")
    site.thumbnail((1100, 1100))
    site.save(STATIC / "cover-art.jpg", quality=84,
              optimize=True)
    for stale in DRAWN_FILES:
        (STATIC / stale).unlink(missing_ok=True)


# --------------------------------------------------------------------------- #
# Drawn mode: the serpent's spine, a lemniscate of Bernoulli
# --------------------------------------------------------------------------- #
def lemniscate(t: float, a: float) -> tuple[float, float]:
    """Point on the lemniscate for parameter t, half-width a."""
    d = 1 + math.sin(t) ** 2
    return (a * math.cos(t) / d,
            a * math.sin(t) * math.cos(t) / d)


def spine(a: float, cx: float, cy: float,
          t_head: float, t_tail: float,
          n: int) -> list[tuple[float, float]]:
    """Sampled spine from head parameter to tail parameter."""
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


def poly(points: list[tuple[float, float]], fill: str) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{coords}" fill="{fill}"/>'


def strand(pts: list[tuple[float, float]],
           nrm: list[tuple[float, float]],
           hw: list[float], s: int, e: int) -> str:
    """A smooth solid stretch of body for spine samples s..e.

    Ink ribbon with a narrower accent stripe riding its inner
    (right) side, the snake's belly line.
    """
    left = edge(pts, nrm, hw, +1.0)
    right = edge(pts, nrm, hw, -1.0)
    body = poly(left[s:e + 1] + right[s:e + 1][::-1], INK)
    # The belly stripe ends short of the tail tip, so the tip
    # that disappears into the mouth is pure ink.
    se = min(e, len(pts) - 1 - 40)
    if se <= s:
        return body
    s_out = edge(pts, nrm, [w * 0.78 for w in hw], -1.0)
    s_in = edge(pts, nrm, [w * 0.38 for w in hw], -1.0)
    stripe = poly(s_out[s:se + 1] + s_in[s:se + 1][::-1], ACCENT)
    return body + stripe


def body_svg(a: float, cx: float, cy: float) -> str:
    """The serpent: a smooth woven figure-eight eating its tail."""
    # Head at the right lobe's outer edge, facing back along the
    # curve; the tail arrives one full figure-eight later and
    # would stop a small gap short of the mouth.
    t_head = -0.47
    t_tail = t_head + 2 * math.pi - 0.30
    n = 630
    pts = spine(a, cx, cy, t_head, t_tail, n)
    hw = widths(n, 50.0, 7.0)

    # The head's local frame: f points forward (out of the mouth,
    # toward the arriving tail), m is its left-hand normal.
    (hx, hy), (bx, by) = pts[0], pts[6]
    fl = math.hypot(hx - bx, hy - by) or 1.0
    f = ((hx - bx) / fl, (hy - by) / fl)
    m = (-f[1], f[0])
    w0 = hw[0]

    def loc(u: float, v: float) -> tuple[float, float]:
        return (hx + f[0] * u + m[0] * v,
                hy + f[1] * u + m[1] * v)

    # Bend the tail's last stretch off the lemniscate so its tip
    # lands inside the open mouth.
    target = loc(0.5 * w0, -0.5 * w0)
    dx, dy = target[0] - pts[n][0], target[1] - pts[n][1]
    bend = 110
    for j in range(n - bend, n + 1):
        u = (j - (n - bend)) / bend
        ease = u * u * (3 - 2 * u)
        pts[j] = (pts[j][0] + dx * ease, pts[j][1] + dy * ease)
    nrm = normals(pts)

    # The spine passes through the crossing at t = pi/2 (early,
    # drawn under) and t = 3pi/2 (late, drawn over with a paper
    # halo so the under-strand visibly dips beneath).
    def idx(t: float) -> int:
        return round((t - t_head) / (t_tail - t_head) * n)

    o_s = max(idx(3 * math.pi / 2 - 0.55), 0)
    o_e = min(idx(3 * math.pi / 2 + 0.55), n)

    under = strand(pts, nrm, hw, 0, n)
    halo_hw = [w + 30 for w in hw]
    h_left = edge(pts, nrm, halo_hw, +1.0)
    h_right = edge(pts, nrm, halo_hw, -1.0)
    halo = (h_left[o_s:o_e + 1] + h_right[o_s:o_e + 1][::-1])
    over = poly(halo, PAPER) + strand(pts, nrm, hw, o_s, o_e)
    head = head_svg(loc, w0, pts, nrm, hw, n)
    return under + over + head


def bez(*points: tuple[float, float]) -> str:
    """M start, then cubic segments, three control points each."""
    d = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    for i in range(1, len(points), 3):
        c1, c2, p = points[i], points[i + 1], points[i + 2]
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} "
                 f"{c2[0]:.1f},{c2[1]:.1f} "
                 f"{p[0]:.1f},{p[1]:.1f}")
    return " ".join(d)


def head_svg(loc, w: float,
             pts: list[tuple[float, float]],
             nrm: list[tuple[float, float]],
             hw: list[float], n: int) -> str:
    """A smooth head whose open jaws close around the tail.

    `loc(u, v)` maps head-local coordinates (u forward out of the
    mouth, v to the snake's left) into the page.
    """
    outline = bez(
        loc(-0.5 * w, 1.0 * w),
        loc(0.8 * w, 1.28 * w), loc(2.0 * w, 1.1 * w),
        loc(2.6 * w, 0.45 * w),
        loc(2.95 * w, 0.05 * w), loc(2.9 * w, -0.2 * w),
        loc(2.6 * w, -0.38 * w),
        loc(2.2 * w, -0.62 * w), loc(1.8 * w, -0.98 * w),
        loc(1.05 * w, -1.18 * w),
        loc(0.35 * w, -1.32 * w), loc(-0.2 * w, -1.12 * w),
        loc(-0.5 * w, -1.0 * w),
    ) + " Z"
    head = f'<path d="{outline}" fill="{INK}"/>'
    # The gape: a curved paper wedge opening toward the tail.
    gape = bez(
        loc(0.5 * w, -0.10 * w),
        loc(1.4 * w, -0.02 * w), loc(2.2 * w, -0.14 * w),
        loc(2.62 * w, -0.36 * w),
        loc(2.1 * w, -0.7 * w), loc(1.7 * w, -0.95 * w),
        loc(1.15 * w, -1.1 * w),
        loc(0.9 * w, -0.75 * w), loc(0.68 * w, -0.38 * w),
        loc(0.5 * w, -0.10 * w),
    ) + " Z"
    mouth = f'<path d="{gape}" fill="{PAPER}"/>'
    # The tail's end, redrawn so it bisects the open mouth:
    # paper shows above and below it, and the tip runs on into
    # the ink of the head. Swallowed.
    tail = strand(pts, nrm, hw, n - 90, n)
    # A round eye, set high and back on the crown.
    ex, ey = loc(0.55 * w, 0.52 * w)
    eye = (f'<circle cx="{ex:.1f}" cy="{ey:.1f}" '
           f'r="{w * 0.36:.1f}" fill="{PAPER}"/>'
           f'<circle cx="{ex:.1f}" cy="{ey:.1f}" '
           f'r="{w * 0.17:.1f}" fill="{INK}"/>')
    return head + mouth + tail + eye


def cover_svg(h: int = H) -> str:
    """The drawn cover at width W and any height."""
    art = body_svg(a=415, cx=W / 2, cy=h * 0.505)
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {h}" width="{W}" height="{h}">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  {art}
  {titles_svg(h)}
</svg>'''


def art_svg() -> str:
    """The drawn serpent alone, for the site's index page."""
    art = body_svg(a=415, cx=W / 2, cy=280)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {W} 560">{art}</svg>')


def eink(svg: str) -> str:
    for src, dst in EINK.items():
        svg = svg.replace(src, dst)
    return svg


def drawn_outputs(preview: bool) -> None:
    master = cover_svg()
    (STATIC / "cover.svg").write_text(master, encoding="utf-8")
    if preview:
        rasterize(STATIC / "cover.svg",
                  STATIC / "cover-preview.png", 500)
        print("wrote cover-preview.png (drawn mode)")
        return
    (STATIC / "cover-eink.svg").write_text(
        eink(master), encoding="utf-8")
    (STATIC / "cover-letter.svg").write_text(
        cover_svg(h=LETTER_H), encoding="utf-8")
    (STATIC / "cover-art.svg").write_text(
        art_svg(), encoding="utf-8")
    rasterize(STATIC / "cover.svg",
              STATIC / "cover-color.png", 1600)
    rasterize(STATIC / "cover-eink.svg",
              STATIC / "cover-eink.png", 1600)
    for stale in ART_FILES:
        (STATIC / stale).unlink(missing_ok=True)


# --------------------------------------------------------------------------- #
# The favicon (both modes)
# --------------------------------------------------------------------------- #
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preview", action="store_true",
                    help="write a small preview PNG only")
    args = ap.parse_args(argv)

    STATIC.mkdir(parents=True, exist_ok=True)
    if ART_SOURCE.exists():
        print(f"art mode: {ART_SOURCE.relative_to(ROOT)}")
        art_outputs(args.preview)
        made = ART_FILES
    else:
        print("drawn mode: no resources/cover-source.jpg")
        drawn_outputs(args.preview)
        made = DRAWN_FILES
    if args.preview:
        return 0
    (STATIC / "favicon.svg").write_text(
        favicon_svg(), encoding="utf-8")
    for name in (*made, "favicon.svg"):
        size = (STATIC / name).stat().st_size
        print(f"{name}: {size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
