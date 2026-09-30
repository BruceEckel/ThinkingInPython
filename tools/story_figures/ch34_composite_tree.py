"""Chapter 34, Composite and Interpreter: one call adds up the filesystem.

The section "The Classic Composite" argues uniformity: one call,
`disk_usage()`, serves a file, a directory, and the whole tree. The
figure draws the section's filesystem once and writes inside each box
what `disk_usage()` returns for that node, so the reader watches the
answers climb: each `File` answers its size, `src` adds its entries'
answers (400 + 250 = 650), and `root` adds its own (90 + 650 + 1200 =
1940). Each box names its kind, `File` or `Directory`, above the name,
so the files and the directories visibly answer the same call. The
open gray arrows are the returns going up. The right panel holds the
demo's three calls and the line they print, including the lone file,
which is a tree too.

This figure used to draw a second tree, the expression `2 * x + 1`, but
the chapter's opening figure (`ch34_composite_and_interpreter.py`,
`composite_story.svg`) draws that tree being built and walked, so this
one keeps to the section it sits in. Names, sizes, and the output come
from `filesystem_classic.py` and `filesystem.py`, which build the same
tree: `Directory("src", (File("main.py", 400), File("util.py", 250)))`,
`Directory("root", (File("readme.md", 90), src, File("data.csv",
1200)))`, the calls `disk_usage(root)`, `disk_usage(src)`,
`disk_usage(File("lone.txt", 10))`, and the marker `1940 650 10`.
"""

from math import hypot

from tools.story_figures import (INK, MUTED, RED, TIP_GAP, Point,
                                 arrow, line, markers, rect, svg, text)

STEM = "composite_tree"
W = 720
NH = 54  # A node box's height
LEVEL_Y = (14, 108, 202)  # Top of each tree level
PX = 506  # The right panel's left edge
# Each node: kind, name, answer, center x, width, level, parent
NODES = {
    "root": ("Directory", "root", "90 + 650 + 1200 = 1940", 245, 180, 0,
             None),
    "readme": ("File", "readme.md", "90", 80, 116, 1, "root"),
    "src": ("Directory", "src", "400 + 250 = 650", 245, 130, 1, "root"),
    "data": ("File", "data.csv", "1200", 410, 116, 1, "root"),
    "main": ("File", "main.py", "400", 180, 110, 2, "src"),
    "util": ("File", "util.py", "250", 310, 110, 2, "src"),
}
# Where each child's return lands on its parent's bottom edge
LAND = {"readme": -44, "src": 0, "data": 44, "main": -22, "util": 22}
TITLE = ("A filesystem tree in which every node answers disk_usage(): "
         "each file returns its size, src returns 400 + 250 = 650, and "
         "root returns 90 + 650 + 1200 = 1940, beside the demo's three "
         "calls, which print 1940 650 10")


def top(key: str) -> float:
    return LEVEL_Y[NODES[key][5]]


def slanted(a: Point, b: Point) -> Point:
    """A target short of `b` that leaves a slanted tip `TIP_GAP` off its edge.

    `arrow()` stops the tip `TIP_GAP` short of its target along the line;
    on a slant that leaves it nearer the edge than `TIP_GAP`, so the target
    moves back along the line until the vertical gap is `TIP_GAP`.
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = hypot(dx, dy)
    extra = TIP_GAP * n / abs(dy) - TIP_GAP
    return b[0] - dx / n * extra, b[1] - dy / n * extra


def render() -> str:
    b = ""
    # Returns: each child's answer goes up to its parent
    for key, (_, _, _, cx, _, _, parent) in NODES.items():
        if parent is None:
            continue
        pcx = NODES[parent][3]
        start = (cx, top(key))
        b += arrow(start, slanted(start, (pcx + LAND[key],
                                          top(parent) + NH)),
                   MUTED, "ct-muted", kind="open")
    for key, (kind, name, answer, cx, w, _, _) in NODES.items():
        y = top(key)
        b += rect(cx - w / 2, y, w, NH, stroke=INK, width=1.1, rx=3)
        b += text(cx, y + 15, kind, 10, MUTED, "middle")
        b += text(cx, y + 31, name, 11.5, INK, "middle", bold=True)
        b += text(cx, y + 47, answer, 11, RED, "middle")

    b += line((PX - 14, 20), (PX - 14, 250))
    b += text(PX, 34, "the same call on", 10.5, MUTED)
    b += text(PX, 49, "any node:", 10.5, MUTED)
    rows = ((74, ("disk_usage(root)",), "1940"),
            (98, ("disk_usage(src)",), "650"),
            (122, ("disk_usage(", 'File("lone.txt", 10))'), "10"))
    for y, calls, value in rows:
        for j, s in enumerate(calls):
            # Continuation lines indent two spaces, which SVG would collapse
            b += text(PX + (2 * 6.3 if j else 0), y + j * 15, s, 10.5)
        b += text(W - 10, y + (len(calls) - 1) * 15, value, 11, RED,
                  "end", bold=True)
    b += text(PX, 186, "the demo prints", 10.5, MUTED)
    b += text(PX, 210, "1940 650 10", 14, RED, bold=True)

    defs = markers(**{"ct-muted": ("open", MUTED)})
    return svg(W, 270, TITLE, defs, b)
