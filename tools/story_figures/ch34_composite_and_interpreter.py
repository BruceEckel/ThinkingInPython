"""Chapter 34, Composite and Interpreter: one tree, built once, read twice.

Three frames of one layout, all on the chapter's expression
`2 * x + 1`, so only the annotations change: Python's operators build
the tree (`x.__rmul__(2)` makes the `Mul`, `__add__(1)` the `Add`, with
`wrap(1)` promoting the `1`) and compute nothing; `evaluate()` makes the
same call on every node, leaf or group, and the ints flow back up to
`7`; `to_infix()`, a second walker in its own file, reads the same tree
as strings, with no edit to `expr.py`. The chapter's claim is that
*Interpreter* is *Composite* with meaning attached, and that the tree
is data while the meaning lives in the walkers; a storyboard over one
fixed tree shows that directly, where the coupling panel it replaces
showed only which functions name which classes. The chapter's
`composite_tree.svg` draws the static shape of both trees, so this
figure draws the walks instead. The names come from `expr.py` (`Num`,
`Var`, `Add`, `Mul`, `__rmul__()`, `__add__()`, `wrap()`),
`evaluate.py` (`x = Var("x")`, `expr = 2 * x + 1`, the `expr.left`
repr, `evaluate(expr, x=3)` and its `7`, `x=10` and its `21`), and
`infix.py` (`to_infix()` and `((2 * x) + 1)`).
"""

from math import hypot

from tools.story_figures import (INK, MUTED, RED, TIP_GAP, Point, arrow,
                                 line, markers, rect, svg, text)

STEM = "composite_story"
W = 730
FH = 180  # One frame's height
NW, NH = 84, 26  # A node box
LEVEL_Y = (22, 74, 126)  # Top of each tree level, within a frame
PX = 496  # The right panel: the call and what it returns
# Each node: its label, its center x, its level, and its parent's key
NODES = {
    "add": ("Add", 330, 0, None),
    "mul": ("Mul", 245, 1, "add"),
    "one": ("Num(1)", 430, 1, "add"),
    "two": ("Num(2)", 195, 2, "mul"),
    "x": ('Var("x")', 295, 2, "mul"),
}
TITLE = ("Three steps on the expression 2 * x + 1: Python's operators "
         "build a tree of Add, Mul, Num, and Var nodes, evaluate() calls "
         "itself on every node and returns 7, and to_infix() walks the "
         "same unchanged tree to return the string ((2 * x) + 1)")


def box(y0: float, key: str) -> tuple[float, float]:
    """The top-left corner of node `key`'s box."""
    _, cx, level, _ = NODES[key]
    return cx - NW / 2, y0 + LEVEL_Y[level]


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


def edges(y0: float, returns: bool) -> str:
    """Parent-child links, or, when `returns`, each child's return."""
    out = ""
    for key, (_, cx, _, parent) in NODES.items():
        if parent is None:
            continue
        x, y = box(y0, key)
        px, py = box(y0, parent)
        pcx = px + NW / 2
        # Land on the parent's bottom edge, toward the child
        tx = pcx + (-18 if cx < pcx else 18)
        if returns:
            out += arrow((cx, y), slanted((cx, y), (tx, py + NH)), MUTED,
                         "cs-muted", kind="open")
        else:
            out += line((tx, py + NH), (cx, y), INK, 1.1)
    return out


def result(y0: float, key: str, s: str, fill: str = RED) -> str:
    """What a node answers: beside a parent, under a leaf."""
    x, y = box(y0, key)
    if key in ("add", "mul"):
        return text(x + NW + 8, y + 17, s, 10.5, fill)
    return text(x + NW / 2, y + NH + 15, s, 10.5, fill, "middle")


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          returns: bool) -> str:
    """The layout every frame shares: the gutter and the same tree."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    out += edges(y0, returns)
    for key, (label, _, _, _) in NODES.items():
        x, y = box(y0, key)
        out += rect(x, y, NW, NH, stroke=INK, width=1.1, rx=3)
        out += text(x + NW / 2, y + 17, label, 11, INK, "middle")
    out += line((PX - 14, y0 + 16), (PX - 14, y0 + FH - 20))
    return out


def render() -> str:
    y = [10 + i * FH for i in range(3)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, "build",
               ("each operator", "builds a node;", "nothing is",
                "computed"), returns=False)
    b += result(y0, "add", "__add__(1)")
    b += result(y0, "mul", "x.__rmul__(2)")
    b += result(y0, "one", "wrap(1)")
    b += text(PX, y0 + 40, 'x = Var("x")', 11)
    b += text(PX, y0 + 58, "expr = 2 * x + 1", 11, RED)
    b += text(PX, y0 + 90, "expr.left is", 10, MUTED)
    b += text(PX, y0 + 108, "Mul(left=Num(value=2),", 10.5)
    # Four spaces of indent, which SVG would collapse if written as text
    b += text(PX + 4 * 6.3, y0 + 124, "right=Var(name='x'))", 10.5)

    y0 = y[1]
    b += frame(1, y0, "evaluate",
               ("the same call", "on every node,", "leaf or group;",
                "ints flow up"), returns=True)
    for key, s in (("add", "7"), ("mul", "6"), ("one", "1"),
                   ("two", "2"), ("x", "3")):
        b += result(y0, key, s)
    b += text(PX, y0 + 40, "evaluate(expr, x=3)", 11)
    b += text(PX, y0 + 58, "returns", 10, MUTED)
    b += text(PX, y0 + 86, "7", 20, RED, bold=True)
    b += text(PX, y0 + 118, "with x=10 the same", 10, MUTED)
    b += text(PX, y0 + 132, "tree returns 21", 10, MUTED)

    y0 = y[2]
    b += frame(2, y0, "to_infix",
               ("a second walker", "in infix.py", "reads the same",
                "tree as text"),
               returns=True)
    for key, s in (("add", '"((2 * x) + 1)"'), ("mul", '"(2 * x)"'),
                   ("one", '"1"'), ("two", '"2"'), ("x", '"x"')):
        b += result(y0, key, s)
    b += text(PX, y0 + 40, "to_infix(expr)", 11)
    b += text(PX, y0 + 58, "returns", 10, MUTED)
    b += text(PX, y0 + 84, "((2 * x) + 1)", 13, RED, bold=True)
    b += text(PX, y0 + 118, "no edit to the", 11, RED)
    b += text(PX, y0 + 134, "nodes in expr.py", 11, RED)

    defs = markers(**{"cs-muted": ("open", MUTED)})
    return svg(W, 10 + 3 * FH, TITLE, defs, b)
