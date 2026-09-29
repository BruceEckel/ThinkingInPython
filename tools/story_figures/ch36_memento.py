"""Chapter 36, Memento: three frames of the classic pattern, one of the frozen form.

Four frames of one layout, so only the changes stand out: `save()` copies
the sketch's list into a frozen `Memento`, drawing again changes the
sketch and leaves the memento as it was, `restore()` copies the tuple back
into a new list, and a frozen `Drawing` kept by reference does the
memento's job with no class and no copy. The shaded region on the right is
the caretaker, which holds the snapshot and never reads it. Frames 1-3 use
the names and output of `sketch.py`'s demo (`sketch`, `checkpoint`, the
strokes `circle`, `beak`, `scribble`); frame 4 uses `frozen_sketch.py`'s
(`before`, `after`, `Duck`). A list is drawn as cells and a tuple as its
repr, so the copy between the two kinds is visible. The chapter's other
figure, `memento_history.svg`, covers `History`'s two stacks, so this one
leaves them out.
"""

from tools.story_figures import (
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

STEM = "memento_story"
W = 730
FH = 146  # One frame's height
OX, OW = 140, 240  # The originator box
CX, CW = 150, 70  # The list cells inside it
MX, MW = 515, 195  # The snapshot box
CARE_X = 480  # Where the caretaker region begins
MID = 69  # The arrows' height within a frame
TITLE = ("Four steps of Memento: save() copies the sketch's list into a "
         "frozen Memento, drawing again leaves the memento unchanged, "
         "restore() copies it back into a new list, and a frozen Drawing "
         "kept by reference is its own memento")


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          origin: str, snap: str, care: str) -> str:
    """The layout every frame shares: originator, caretaker, snapshot."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += region(CARE_X, y0 + 6, W - CARE_X - 10, FH - 16, fill=SHADE, r=0)
    out += text(W - 18, y0 + 20, care, 10, MUTED, "end")
    out += rect(OX, y0 + 14, OW, FH - 30, stroke=INK)
    out += text(OX + 12, y0 + 34, origin, 13, bold=True)
    out += text(OX + 12, y0 + 52, "strokes", 10, MUTED)
    out += rect(MX, y0 + 28, MW, FH - 46, stroke=RED if i == 3 else INK)
    out += text(MX + 12, y0 + 48, snap, 12, bold=True)
    out += text(MX + 12, y0 + 64, "strokes", 10, MUTED)
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def cells(y0: float, strokes: tuple[str, ...], red: int = -1) -> str:
    """A list, drawn as one cell per stroke; cell `red` is the new one."""
    out = ""
    for k, s in enumerate(strokes):
        c = RED if k == red else INK
        x = CX + k * (CW + 6)
        out += rect(x, y0 + 58, CW, 24, stroke=c, width=1.1, rx=3)
        out += text(x + CW / 2, y0 + 74, s, 10.5, c, "middle")
    return out


def tuple_repr(x: float, y0: float, s: str, y: float = 84,
               fill: str = INK) -> str:
    return text(x + 12, y0 + y, s, 11, fill)


def output(x: float, y0: float, s: str, y: float, fill: str = RED) -> str:
    return text(x + 12, y0 + y, f"#: {s}", 10.5, fill)


def between(y0: float, rightward: bool, above: str, below: str,
            color: str, marker: str, kind: str) -> str:
    """An arrow across the gap between the two boxes, labeled both sides."""
    left, right = (OX + OW, y0 + MID), (MX, y0 + MID)
    a, b = (left, right) if rightward else (right, left)
    mid = (OX + OW + MX) / 2
    return (arrow(a, b, color, marker, kind=kind, width=1.6)
            + text(mid, y0 + MID - 7, above, 10, color, "middle")
            + text(mid, y0 + MID + 16, below, 10, MUTED, "middle"))


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    care = "caretaker: holds it, never reads it"
    b = ""

    y0 = y[0]
    b += frame(0, y0, "save", ("the list is", "copied into a", "frozen tuple"),
               "sketch: Sketch", "checkpoint: Memento", care)
    b += cells(y0, ("circle", "beak"))
    b += tuple_repr(MX, y0, "('circle', 'beak')", fill=RED)
    b += between(y0, True, "save()", "list -> tuple", RED, "ms-red", "open")

    y0 = y[1]
    b += frame(1, y0, "draw",
               ("the sketch", "changes; the", "memento does not"),
               "sketch: Sketch", "checkpoint: Memento", care)
    b += text(OX + OW - 10, y0 + 34, 'draw("scribble")', 10, RED, "end")
    b += cells(y0, ("circle", "beak", "scribble"), red=2)
    b += output(OX, y0, "circle beak scribble", 104)
    b += tuple_repr(MX, y0, "('circle', 'beak')")
    b += text(MX + 12, y0 + 104, "unchanged", 10, MUTED)

    y0 = y[2]
    b += frame(2, y0, "restore",
               ("the tuple is", "copied back", "into a new list"),
               "sketch: Sketch", "checkpoint: Memento", care)
    b += cells(y0, ("circle", "beak"))
    b += text(CX + 2 * (CW + 6) + 2, y0 + 74, "new list", 10, RED)
    b += output(OX, y0, "circle beak", 104)
    b += tuple_repr(MX, y0, "('circle', 'beak')")
    b += between(y0, False, "restore(checkpoint)", "tuple -> list", RED,
                 "ms-red-call", "filled")

    y0 = y[3]
    b += frame(3, y0, "freeze",
               ("a frozen state", "is its own", "memento"),
               "after: Drawing", "before: Drawing",
               "caretaker: keeps a reference")
    b += text(OX + 12, y0 + 74, "('circle', 'beak', 'scribble')", 10.5)
    b += output(OX, y0, "Duck: circle beak scribble", 104, INK)
    b += tuple_repr(MX, y0, "('circle', 'beak')")
    b += output(MX, y0, "Duck: circle beak", 104, INK)
    b += between(y0, False, 'draw("scribble")', "returns new", INK,
                 "ms-ink", "open")

    defs = markers(**{"ms-red": ("open", RED),
                      "ms-red-call": ("filled", RED),
                      "ms-ink": ("open", INK)})
    return svg(W, 10 + 4 * FH, TITLE, defs, b)
