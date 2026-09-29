"""Chapter 23, Iterators: four frames of one loop and its iterator.

Four frames of one layout, so only the changes stand out. A `for` loop
calls `iter()` once and gets an iterator that keeps the place in the
list; each `next()` hands over one item; the next `next()` raises
`StopIteration`, which the loop takes as its end; and `total()` makes
the same calls on a list, a generator, or `Countdown` with no edit. The
shaded region is what the loop cannot see: where the items come from.
The coupling panel this replaces showed that `total()` names only
`Iterable[int]`; this figure shows the conversation that makes that
true, and that the only way to ask whether the source is done is to
take.

Frames 1-3 follow the chapter's written-out form of `for x in nums:`
and `basic_iteration.py` (`nums = [1, 2]`, `it = iter(nums)`, the
values `1 2`, "StopIteration ends the loop"). Frame 4's names and totals
come from `iterators.py` (`total()`, `fibonacci(8)`, `Countdown(5)`,
and the printed 10, 33, and 15).
"""

from tools.story_figures import (
    BOX,
    INK,
    MUTED,
    RED,
    SHADE,
    arrow,
    line,
    markers,
    rect,
    region,
    svg,
    text,
)

STEM = "iterator_story"
W = 730
FH = 150  # One frame's height
LX, LW = 140, 150  # The loop box
IX, IW = 405, 90  # The iterator box
IY, IH = 30, 90  # The iterator box, relative to its frame
HIDE_X, HIDE_W = 525, 140  # The region the loop cannot see
CELLS = (552, 598)  # The two items of nums
CW, CY, CH = 40, 50, 30
MID = (LX + LW + IX) / 2  # Where labels on loop-iterator arrows sit
TITLE = ("Four steps of iteration: a for loop calls iter(nums) once, "
         "calls next(it) for each item, ends when next(it) raises "
         "StopIteration, and total() makes the same calls on a list, "
         "a generator, or Countdown with no edit")


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          loop: str, it: str) -> str:
    """The layout every frame shares."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += region(HIDE_X, y0 + 6, HIDE_W, FH - 18, fill=SHADE,
                  r=0)
    out += rect(LX, y0 + 14, LW, FH - 28, stroke=RED if i == 3 else INK,
                width=1.6)
    out += text(LX + 12, y0 + 34, loop, 13, bold=True)
    out += rect(IX, y0 + IY, IW, IH, stroke=INK, width=1.3)
    out += text(IX + IW / 2, y0 + IY + 50, it, 13 if i < 3 else 11,
                bold=i < 3, anchor="middle")
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def nums(y0: float, fill: str) -> str:
    """The list the loop walks, drawn inside the hidden region."""
    out = text(CELLS[0], y0 + CY - 8, "nums", 10, MUTED)
    for x, v in zip(CELLS, ("1", "2"), strict=True):
        out += rect(x, y0 + CY, CW, CH, stroke=BOX, width=1.3, rx=3)
        out += text(x + CW / 2, y0 + CY + 20, v, 13, fill, "middle")
    return out


def call(y: float, s: str, color: str = RED, marker: str = "is-red") -> str:
    """A call from the loop to the iterator, labeled above the line."""
    return (arrow((LX + LW, y), (IX, y), color, marker, width=1.6)
            + text(MID - 6, y - 5, s, 10, color, "middle"))


def reply(y: float, s: str, color: str = INK,
          marker: str = "is-ink-open") -> str:
    """What the iterator hands back to the loop."""
    return (arrow((IX, y), (LX + LW, y), color, marker, kind="open")
            + text(MID + 6, y - 5, s, 10 if len(s) > 1 else 12, color,
                   "middle"))


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, "iter", ("once, before", "the loop; the", "iterator keeps",
                               "the place"),
               "for x in nums", "it")
    b += text(HIDE_X + HIDE_W - 8, y0 + 24, "hidden from the loop", 10,
              MUTED, "end")
    b += nums(y0, INK)
    b += call(y0 + 65, "iter(nums)", INK, "is-ink")
    b += arrow((IX + IW, y0 + 65), (CELLS[0], y0 + 65), INK, "is-ink")
    b += text(CELLS[0], y0 + CY + CH + 14, "next up", 10, MUTED)

    y0 = y[1]
    b += frame(1, y0, "next", ("once per step;", "each call hands",
                               "over one item"),
               "for x in nums", "it")
    b += nums(y0, RED)
    for k, v in enumerate(("1", "2")):
        cy = y0 + 44 + k * 48
        b += call(cy, "next(it)")
        b += reply(cy + 20, v)
        b += text(LX + 12, cy + 24, f"x = {v}", 11, RED)

    y0 = y[2]
    b += frame(2, y0, "stop", ("the only way to", "ask is to take;",
                               "the loop ends"),
               "for x in nums", "it")
    b += nums(y0, MUTED)
    b += call(y0 + 56, "next(it)")
    b += reply(y0 + 92, "StopIteration", RED, "is-red-open")
    b += text(LX + 12, y0 + 96, "break", 11, RED)
    b += text(IX + IW / 2, y0 + IY + 72, "none left", 10, MUTED, "middle")

    y0 = y[3]
    b += frame(3, y0, "swap", ("any source", "answers the", "same calls"),
               "total()", "iterator")
    b += text(HIDE_X + HIDE_W - 8, y0 + 24, "hidden from total()", 10,
              MUTED, "end")
    b += text(LX + 12, y0 + 54, "sum(numbers)", 11, MUTED)
    b += text(LX + 12, y0 + 100, "no edit to", 11, RED)
    b += text(LX + 12, y0 + 115, "total()", 11, RED)
    b += call(y0 + 60, "next()")
    rx = (W + HIDE_X + HIDE_W) / 2
    b += text(rx, y0 + 24, "returns", 10, MUTED, "middle")
    for k, (src, got) in enumerate((("[1, 2, 3, 4]", "10"),
                                    ("fibonacci(8)", "33"),
                                    ("Countdown(5)", "15"))):
        sy = y0 + 45 + k * 30
        b += rect(540, sy - 12, 116, 24, stroke=BOX, width=1.3, rx=3)
        b += text(598, sy + 4, src, 10.5, INK, "middle")
        b += arrow((IX + IW, sy), (540, sy), INK, "is-ink")
        b += text(rx, sy + 4, got, 12, INK, "middle")

    defs = markers(**{"is-ink": ("filled", INK), "is-red": ("filled", RED),
                      "is-ink-open": ("open", INK),
                      "is-red-open": ("open", RED)})
    return svg(W, 10 + 4 * FH, TITLE, defs, b)
