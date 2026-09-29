---
name: figures
description: >-
  Rules for drawing or editing a figure in this book: where text goes (labels, caption, prose), the palette and arrowheads, the generated story, state-machine, and coupling-gallery SVGs, and what tip figures checks. Use before creating or changing any SVG in resources/images/ or a figure spec in tools/.
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

Three figure sources are generated, and their SVGs are never edited by
hand. Before changing a pattern chapter's figure, read its module in
`tools/story_figures/`: the docstring says which listings its names
come from. The pattern chapters' opening figures come from
`tools/story_figures/` (since 2026-09-29), one module per chapter
(`chNN_<pattern>.py`, defining `STEM` and `render()`), with the shared
palette, text, boxes, and arrows in the package's `__init__.py`.
Chapter 30's four-frame Observer storyboard came first and replaced
that chapter's coupling panel: Bruce found the class-diagram panel
told the reader too little, called the storyboard "a much more
accessible story," and asked for the same in every pattern chapter,
with no notation or precedent to follow, a coupling-panel variation
included where that suits a pattern. The goal is the picture that best
helps the reader. The same day, one agent per chapter drew the other
thirteen, each choosing its own form: storyboards for most, a trace of
one run for State, parallel lanes for Function Objects, a before/after
table for Multiple Dispatching. What the good ones share: the chapter's
own names, values, and `#:` output; the pattern's key insight made
visible (a shaded region for what one part cannot see); and a payoff
frame, outlined in red, showing what does not have to change. A shaded
region is filled with `SHADE` (`#eeeeee`), never a translucent color:
the EPUB's PNG8 conversion cuts each channel to a multiple of 17 and
turned every pale warm tint yellow. An outer shape enclosing an arrow's target is a
`region()` path, since `tight_tips()` would read a tip on an inner box
as buried in the outer rect. `tip story-figures` (in `gate`,
`verify-ch`, and `sweep`) fails on drift or on any per-figure check
`tip figures` makes; `tip fix-story-figures` regenerates, and
`python -m tools.story_figures --only NN --png DIR` rasterizes one.
Chapter 31's `stateMachine.svg` comes from
`tools/state_machine_figure.py` (since 2026-09-24): each transition
names its two states, how far its curve bows, and where along the curve
its label sits, and the script computes the rest. Edit the spec, run
`tip fix-state-machine-figure`, and look at the PNG in `tip figures`,
since nothing detects two labels colliding; `tip state-machine-figure`
(in `gate`, `verify-ch`, and `sweep`) fails on drift.

Chapter 21's `coupling_gallery.svg` comes from `tools/coupling_panels.py`
(`GALLERY`, a `Cell` per pattern, since 2026-09-25), in the notation
chapter 21's Coupling section defines: a heavy edge names a concrete
class (stroke 3.8, so it reads apart from the thin 1.3 at a glance), a
thin edge names an interface, a dashed hollow-headed edge satisfies
one, and the red box is the part the pattern protects from change. The
section's other three figures are hand-drawn. Edit a `Cell` and run
`tip fix-coupling-panels`; never edit the SVG by hand. `tip
coupling-panels` (in `gate`, `verify-ch`, and `sweep`) fails when the
committed SVG differs from what the spec draws, on an arrowhead whose
tip is not 4 units (within 1) from its target's rounded outline, and on
an edge that crosses a third box; `edge_points()` slides every tip onto
that 4-unit line, so a new failure usually means two boxes need moving.
From 2026-09-23 to 2026-09-29 the same file also drew a coupling panel
at the top of each pattern chapter; the story figures replaced them.
