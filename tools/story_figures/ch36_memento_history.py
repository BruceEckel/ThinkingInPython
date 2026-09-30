"""Chapter 36, Memento: what `History`'s two stacks hold after each call.

Chapter 36's second figure, beside `history.py`, replaced a hand-drawn
diagram on 2026-09-29 whose arrows floated between labels. It is a
filmstrip: one row per call, each showing what `_past`, `_present`, and
`_future` hold once the call returns, so the reader watches states move
instead of decoding a legend of moves. A red arrow in a gap is the one
push or pop that call made; `_past` grows toward `_present` and `_future`
toward it from the other side, so each stack's top sits next to the
present. The last row shows `do()`'s `_future.clear()`: after an undo, a
new edit discards the undone state, drawn crossed out.

Rows 0-4 follow `history.py`'s demo: `History(Drawing("Duck"))`, two
`apply()` calls drawing `circle` and `beak`, `undo()`, `redo()`, with
their `#:` output. A state is shown by its strokes as `Drawing.__str__()`
in `frozen_sketch.py` prints them, less the `Duck: ` title every state
shares. Row 5 (an undo, then an edit drawing `scribble`) is in no
listing, so its new state is dashed; `test_new_action_clears_redo` in
`test_history.py` checks the same behavior with strings.
"""

from tools.story_figures import (INK, MUTED, RED, arrow, cross, line,
                                 markers, rect, svg, text)

STEM = "memento_history"
W = 730
RH = 74  # One row's height
TOP = 62  # Where the first row begins
CW, CH = 92, 26  # A state cell
PAST_R = 408  # The right edge of _past's top cell
PX, PW = 448, 124  # The _present box
FX = 612  # The left edge of _future's top cell
TITLE = ("History's stacks after each call: apply() pushes the present "
         "onto _past, undo() and redo() move one state between the "
         "stacks and the present, and a new edit after an undo clears "
         "_future")


def cell(x: float, y: float, s: str, stroke: str = INK,
         fill: str = INK, dash: bool = False) -> str:
    return (rect(x, y, CW, CH, stroke=stroke, width=1.1, rx=3, dash=dash)
            + text(x + CW / 2, y + 17, s, 10.5, fill, "middle"))


def row(i: int, name: str, code: str, out: str, past: tuple[str, ...],
        present: str, future: tuple[str, ...],
        dash_present: bool = False, cleared: bool = False) -> str:
    """One call's row: its name, code, output, and the three holders."""
    y0 = TOP + i * RH
    cy = y0 + 18  # A cell's top
    b = line((16, y0 - 6), (W - 16, y0 - 6)) if i else ""
    b += text(20, y0 + 26, str(i), 24, RED, bold=True)
    b += text(48, y0 + 14, name, 12, bold=True)
    b += text(48, y0 + 32, code, 10, MUTED)
    if out:
        b += text(48, y0 + 50, f"#: {out}", 10, RED)
    if past:
        for k, s in enumerate(reversed(past)):
            b += cell(PAST_R - CW - k * (CW + 6), cy, s)
    else:
        b += text(PAST_R - 12, cy + 17, "[]", 10.5, MUTED, "end")
    b += rect(PX, cy - 4, PW, CH + 8, stroke=INK, width=1.6,
              dash=dash_present)
    b += text(PX + PW / 2, cy + 17, present, 11.5, INK, "middle", bold=True)
    if future:
        for k, s in enumerate(reversed(future)):
            b += cell(FX + k * (CW + 6), cy, s)
    elif not cleared:
        b += text(FX + 12, cy + 17, "[]", 10.5, MUTED)
    return b


def move(i: int, left_gap: bool, rightward: bool, label: str) -> str:
    """The red push or pop across one gap, labeled above the arrow."""
    y = TOP + i * RH + 18 + CH / 2
    lo, hi = (PAST_R, PX) if left_gap else (PX + PW, FX)
    a, b = ((lo, y), (hi, y)) if rightward else ((hi, y), (lo, y))
    return (arrow(a, b, RED, "mh-red", width=1.6)
            + text((lo + hi) / 2, y - 18, label, 10, RED, "middle"))


def render() -> str:
    b = ""
    heads = ((PAST_R - CW, "_past", "list, top at right"),
             (PX + PW / 2, "_present", "one state"),
             (FX + CW / 2, "_future", "list, top at left"))
    for x, name, note in heads:
        b += text(x, 22, name, 13, INK, "middle", bold=True)
        b += text(x, 38, note, 10, MUTED, "middle")
    b += text(20, 22, "Drawing(\"Duck\") states,", 10, MUTED)
    b += text(20, 38, "shown by their strokes", 10, MUTED)

    b += row(0, "start", 'History(Drawing("Duck"))', "", (), "(blank)", ())
    b += row(1, "apply()", 'd.draw("circle")', "", ("(blank)",), "circle",
             ())
    b += move(1, True, False, "push")
    b += row(2, "apply()", 'd.draw("beak")', "Duck: circle beak",
             ("(blank)", "circle"), "circle beak", ())
    b += move(2, True, False, "push")
    b += row(3, "undo()", "history.undo()", "Duck: circle",
             ("(blank)",), "circle", ("circle beak",))
    b += move(3, True, True, "pop")
    b += move(3, False, True, "push")
    b += row(4, "redo()", "history.redo()", "Duck: circle beak",
             ("(blank)", "circle"), "circle beak", ())
    b += move(4, False, False, "pop")
    b += move(4, True, False, "push")

    # Row 5: an undo (the same stacks as row 3), then a new edit.
    b += row(5, "undo(), apply()", 'd.draw("scribble")', "",
             ("(blank)", "circle"), "circle scribble", (), dash_present=True,
             cleared=True)
    b += move(5, True, False, "push")
    y0 = TOP + 5 * RH
    b += cell(FX, y0 + 18, "circle beak", stroke=MUTED, fill=MUTED)
    b += cross(FX + CW + 12, y0 + 18 + CH / 2, size=6)
    b += text(FX + CW / 2 + 6, y0 + 62, "_future.clear()", 10, RED,
              "middle")

    defs = markers(**{"mh-red": ("filled", RED)})
    return svg(W, TOP + 6 * RH + 4, TITLE, defs, b)
