"""Chapter 31, State Machines: the mousetrap's run, one row per input.

A trace, not a structure: the four state objects head four columns,
each row is one pass of `run_all()`'s loop, and a dot marks the state
the machine occupies after that input. The red arrows are the calls to
`next(event)`, so the reader sees the current state, not the machine,
pick each successor, and the machine's position move by itself from
object to object. The right column is what each new state's `run()`
prints. Below the trace, one unexpected input (`mouse escapes` in
`Waiting`) meets the two versions' policies side by side: the `match`
version's `case _` keeps the state and runs it again, and the table
version's `next()` raises a `RuntimeError`.

This complements the chapter's other figure, `stateMachine.svg`, which
draws the vending machine's states and transitions as a static graph.
The names, inputs, and printed lines come from `mouse_action.py`,
`mouse_moves.txt`, `mouse_trap_states.py`, and `mouse_trap_tables.py`
and their `#:` markers.
"""

from tools.story_figures import (INK, MUTED, RED, Point, arrow, cross,
                                 line, markers, rect, svg, text)

STEM = "state_story"
W = 740
EX = 20  # The event column
CX = (212, 294, 376, 458)  # The four state columns' centers
BW, BH = 72, 26  # A state's header box
OX = 510  # The column of printed lines
HY = 50  # The header boxes' top
R0, RH = 104, 25  # The first row's center, the row pitch
DOT = 5
STATES = ("Waiting", "Luring", "Trapping", "Holding")
RUN = {
    "Waiting": "Waiting: Broadcasting cheese smell",
    "Luring": "Luring: Presenting Cheese, door open",
    "Trapping": "Trapping: Closing door",
    "Holding": "Holding: Mouse caught",
}
# (input, the state next(input) returns), from mouse_moves.txt.
MOVES = (
    ("mouse appears", "Luring"),
    ("mouse runs away", "Waiting"),
    ("mouse appears", "Luring"),
    ("mouse enters trap", "Trapping"),
    ("mouse escapes", "Waiting"),
    ("mouse appears", "Luring"),
    ("mouse enters trap", "Trapping"),
    ("mouse trapped", "Holding"),
    ("mouse removed", "Waiting"),
)
TITLE = ("The mousetrap's nine inputs as a trace: in each row the current "
         "state's next(event) picks the next of four state objects, whose "
         "run() prints a line; below, an input Waiting does not name keeps "
         "the match version in Waiting and makes the table version raise "
         "a RuntimeError")


def dot(p: Point) -> str:
    return (f'  <circle cx="{p[0]:g}" cy="{p[1]:g}" r="{DOT}" '
            f'fill="{INK}"/>\n')


def edge(a: Point, b: Point) -> str:
    """A red `next()` arrow from dot `a` to dot `b`, border to border."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    start = (a[0] + ux * DOT, a[1] + uy * DOT)
    end = (b[0] - ux * DOT, b[1] - uy * DOT)
    return arrow(start, end, RED, "ss-red", width=1.5)


def trace() -> tuple[str, float]:
    """The header, the grid, and the nine rows; the bottom's y."""
    b = text(EX, 22, "MouseTrap().run_all(moves)", 12, bold=True)
    b += text(EX, 38, "each row: current_state.next(event) returns the "
              "next state (red), and run() on it prints", 10, MUTED)
    b += text(EX, HY + 18, "event", 11, MUTED)
    b += text(OX, HY + 18, "run() prints", 11, MUTED)
    last = R0 + len(MOVES) * RH
    for x, s in zip(CX, STATES):
        b += line((x, HY + BH), (x, last + 10))
        b += rect(x - BW / 2, HY, BW, BH, stroke=INK)
        b += text(x, HY + 17, s, 11.5, anchor="middle", bold=True)
    col = {s: x for x, s in zip(CX, STATES)}
    b += text(EX, R0 + 4, "MouseTrap()", 10.5, MUTED)
    here = (col["Waiting"], R0)
    b += dot(here) + text(OX, R0 + 4, RUN["Waiting"], 10)
    for i, (event, state) in enumerate(MOVES, 1):
        y = R0 + i * RH
        there = (col[state], y)
        b += text(EX, y + 4, event, 10.5)
        b += edge(here, there) + dot(there)
        b += text(OX, y + 4, RUN[state], 10)
        here = there
    return b, last + 26


def policy(x0: float, y0: float, name: str, file: str,
           raises: bool) -> str:
    """One version's answer to `mouse escapes` in Waiting."""
    b = text(x0, y0, name, 11.5, bold=True)
    b += text(x0, y0 + 15, file, 10, MUTED)
    bx, by = x0, y0 + 30
    b += rect(bx, by, BW, BH, stroke=INK)
    b += text(bx + BW / 2, by + 17, "Waiting", 11.5, anchor="middle",
              bold=True)
    tx = bx + BW + 130
    mid = by + BH / 2
    b += text((bx + BW + tx) / 2, mid - 6, "mouse escapes", 10, INK,
              "middle")
    if raises:
        cx = tx + 10
        b += line((bx + BW, mid), (cx - 10, mid), RED, 1.5)
        b += cross(cx, mid)
        b += text(bx, by + BH + 22, "RuntimeError: Waiting has no", 10,
                  RED)
        b += text(bx, by + BH + 36, "transition for mouse escapes", 10,
                  RED)
    else:
        b += arrow((bx + BW, mid), (tx, mid), RED, "ss-red", width=1.5)
        b += rect(tx, by, BW, BH, stroke=INK)
        b += text(tx + BW / 2, by + 17, "Waiting", 11.5, anchor="middle",
                  bold=True)
        b += text(bx, by + BH + 22, "case _ returns the current state,",
                  10, MUTED)
        b += text(bx, by + BH + 36, "so run() prints its line again", 10,
                  MUTED)
    return b


def render() -> str:
    b, y0 = trace()
    b += line((16, y0), (W - 16, y0))
    b += text(EX, y0 + 22, "an input the current state does not name", 11,
              MUTED)
    b += policy(EX, y0 + 48, "match version", "mouse_trap_states.py",
                raises=False)
    b += policy(390, y0 + 48, "table version", "mouse_trap_tables.py",
                raises=True)
    defs = markers(**{"ss-red": ("filled", RED)})
    return svg(W, y0 + 160, TITLE, defs, b)
