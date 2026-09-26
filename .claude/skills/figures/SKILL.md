---
name: figures
description: >-
  Rules for drawing or editing a figure in this book: where text goes (labels, caption, prose), the palette and arrowheads, the generated state-machine and coupling-panel SVGs, and what tip figures checks. Use before creating or changing any SVG in resources/images/ or a figure spec in tools/.
---

# Figures

Moved from `CLAUDE.md`.

## Diagrams: the figure labels, the caption names, the prose explains

A figure is a hand-authored SVG in `resources/images/`, referenced from
the prose as `![caption](_images/<name>)` with no extension.
`build_site.py` and `build_epub.py` resolve it (the EPUB rasterizes the
SVG to PNG, so a rasterizer must be on PATH: `resvg`, `rsvg-convert`,
`magick`, or `inkscape`). There is no Mermaid, Graphviz, or PlantUML
anywhere in the repo, and a diagram written as a fenced block renders
as nothing.

Three rules about what text goes where, from Bruce's 2026-09-18 ruling
on chapter 30's `observer_broadcast.svg`:

- **No caption inside the SVG.** A drawing carries labels on its
  parts, nothing else. A sentence summarizing the figure, set in small
  type along the bottom, is a caption in the wrong place: pandoc
  already prints the Markdown alt text as a `<figcaption>` under the
  image, so an embedded one shows up twice, in two type sizes.
- **The Markdown caption is one short sentence** naming what the figure
  shows, and only when the drawing does not already say it. Chapter
  30's is "Assigning to celsius calls every listener." A caption that
  restates the figure's own title or labels is cut down to what they
  leave unsaid, or removed (Bruce, 2026-09-26, on the coupling panels).
- **A figure with no caption is written `![](_images/name)`.** Pandoc
  builds a figure only from an image with alt text, so
  `build_site.image_ref()` supplies the SVG's `<title>` as the alt
  text and the class `nocaption`, and `tools/nocaption.lua` (run by the
  site, EPUB, and PDF builds) drops the caption. The figure keeps its
  centering and spacing; the `<title>` is what a screen reader reads,
  so an uncaptioned figure's `<title>` must describe it.
- **Everything else goes in the prose after the figure**, as ordinary
  sentences with the usual code spans. The second clause cut from
  chapter 30's caption became the paragraph under it: "`Thermometer`
  holds the list and names no observer type, so a `Plot` and a `Table`
  would attach the way `Display` does."

The existing diagrams share a visual vocabulary worth matching, since
nothing enforces it: a `viewBox` with no width or height,
`font-family="'JetBrains Mono', Consolas, monospace"`, a `<title>` for
screen readers, and the cover palette from `tools/make_cover.py`,
`#1a1612` for ink and text, `#c8bfb0` for ordinary box strokes,
`#7a6e62` for muted text, `#8b1a1a` to mark the one class the figure
is about. A dashed stroke marks a box that the listing does not
contain (`surrogate.svg`'s "Etc.", `observer_broadcast.svg`'s `Plot`
and `Table`). Arrowheads come from `tools/arrowheads.py` and nowhere
else (2026-09-24, Bruce's pick from a comparison sheet): `filled`, a
swept head, for anything that points; `hollow`, an open triangle, only
for inherits or satisfies; `open`, a V, for a return; `diamond` for
aggregation. None is filled with the paper color, since the EPUB and
the gallery draw on white, so the edge stops short of its target by
the head's `trim` and the head, anchored at its back, reaches the
border. `marker_def()` writes the `<marker>`; `shorten_line()` and
`shorten_path_end()`/`shorten_path_start()` shorten a hand-drawn edge.
Each head takes its line's color, one marker per color in a figure
(a gray edge gets a gray head, a red edge a red one).
`tip figures` fails on any other marker and on a head whose color
differs from its line's.
It also measures text (`tools/svg_text.py`, 0.6 em per character in
JetBrains Mono) and fails on text past the `viewBox`, which every
renderer cuts off, or overlapping other text; text lying across a line
still needs the PNG and an eye. Before committing a new one, rasterize it the way the
EPUB does and look at the PNG; text that fits in a browser can collide
once rasterized. `tip figures` (in `tip verify` since 2026-09-24,
`tools/figure_gallery.py`) builds `build/figures/index.html`: every
figure in book order, numbered, with its file name, chapter, line,
and caption, switchable between the live SVG and the EPUB's PNG,
and a style line per figure (colors, stroke widths, dashes, fonts,
arrowhead markers) that marks anything outside the palette. Bruce
names a figure by its number there or its file stem; it fails on a
reference with no file and only reports a file no chapter references.

Two figure sources are generated, and their SVGs are never edited by
hand. Chapter 31's `stateMachine.svg` comes from
`tools/state_machine_figure.py` (since 2026-09-24): each transition
names its two states, how far its curve bows, and where along the curve
its label sits, and the script computes the rest. Edit the spec, run
`tip fix-state-machine-figure`, and look at the PNG in `tip figures`,
since nothing detects two labels colliding; `tip state-machine-figure`
(in `gate`, `verify-ch`, and `sweep`) fails on drift.

The larger family of generated figures is the coupling-notation panel at
the top of each pattern chapter, 23 through 36
(`resources/images/coupling_NN.svg`, merged 2026-09-23). Chapter 21's
Coupling section (merged from Appendix C on 2026-09-24) defines the
notation: a heavy edge names a
concrete class (stroke 3.8, raised from 2.8 on 2026-09-26 so it
reads apart from the thin 1.3 at a glance), a thin edge names an interface, a dashed hollow-headed
edge satisfies one, a solid hollow-headed edge inherits, and the red
box is the part the pattern protects from change. `tools/coupling_panels.py`
holds a `Panel` spec per chapter, in that chapter's own class and
function names. A panel prints no caption: its title and legend say
what it shows, and its `<title>` is the alt text. Edit the spec and run `tip fix-coupling-panels`; never edit
one of these SVGs by hand. Chapter 21's `coupling_gallery.svg` comes
from the same file (`GALLERY`, a `Cell` per pattern, since
2026-09-25); the section's other three figures are still hand-drawn.
`tip coupling-panels` (in `gate`,
`verify-ch`, and `sweep`) fails when a committed SVG differs from what
the spec draws, so a listing rename that misses the spec is loud. It
also fails an arrowhead whose tip is not 4 units (within 1) from its
target's rounded outline, and an edge that crosses a third box
(2026-09-25); `edge_points()` slides every tip onto that 4-unit line,
so a new failure usually means two boxes need moving, not a tweak. The
2026-09-23 verification of all fourteen found two recurring mistakes
worth checking a new panel for: drawing the GoF shape instead of the
listing's (chapter 26 had a `Service` protocol no listing declares),
and counting a call through `Any` as naming a class (chapter 32's
`eval_*()` methods). Panels carry no note under the drawing
(2026-09-25) and no caption (2026-09-26): each panel's height follows its lowest box or legend line, and its legend
lists only the edge kinds it draws.
