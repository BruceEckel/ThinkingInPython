"""Chapter 31, State Machines: the vending machine's table as a hub.

A state diagram, redrawn for legibility. The `stateMachine.svg` it
replaced (from the retired `tools/state_machine_figure.py`) drew all
thirteen transitions as curves, four of them `Quit / refund` arcs, and
its labels crowded each other. Here every edge is straight and every state sits on one of
two columns. `SELECTING` is the hub: each of the other three states in
the shaded region is one spoke, with `FirstDigit / choose_row` running
in and a `SecondDigit` row running out. The four `Quit / refund` rows
become one arrow from the shaded region to `QUIESCENT`, which is what
the prose says about them: `Quit` refunds from any other state.

The three `SecondDigit` rows are red and numbered 1 to 3 in the order
the table lists them, since the engine tries them in that order and the
first condition that passes wins; the chapter's last three events turn
on that order.

This is not a trace: the chapter's opening figure (`ch31_state_machines`,
`state_story.svg`) already traces the mousetrap's run. State, event,
condition, and action names come from the `table` in
`tabledriven/vending_machine.py`; the initial state is the one its
`super().__init__()` call passes.
"""

from tools.story_figures import (INK, MUTED, RED, SHADE, arrow, line,
                                 markers, rect, region, svg, text)

STEM = "vending_story"
W, H = 720, 470
BW, BH = 124, 36  # A state's box
LX, RX = 122, 440  # The two columns' centers
QY = 44  # QUIESCENT's center
UY, SY, WY = 150, 280, 410  # UNAVAILABLE, SELECTING, WANT_MORE
RTOP, RBOT = 100, 454  # The shaded region
OFF = 11  # Half the gap between the two edges of a pair
TITLE = ("The vending machine's states: Money moves QUIESCENT to "
         "COLLECTING, FirstDigit moves any of three states to SELECTING, "
         "SELECTING's SecondDigit rows lead to three states in table "
         "order, and Quit returns every shaded state to QUIESCENT")


def state(cx: float, cy: float, name: str, stroke: str = INK) -> str:
    b = rect(cx - BW / 2, cy - BH / 2, BW, BH, stroke=stroke, width=1.6)
    return b + text(cx, cy + 4.5, name, 12, INK, "middle", bold=True)


def label(x: float, y: float, lines: tuple[str, ...], anchor: str,
          red: bool = False) -> str:
    """An edge's label: event, then any [condition], then / action."""
    b = ""
    for i, s in enumerate(lines):
        if s.startswith("/"):
            fill, size = MUTED, 10.5
        elif red:
            fill, size = RED, 11
        else:
            fill, size = INK, 11
        b += text(x, y + i * 14, s, size, fill, anchor)
    return b


def render() -> str:
    top, bot = -BH / 2, BH / 2
    b = region(LX - BW / 2 - 28, RTOP, W - 16 - (LX - BW / 2 - 28),
               RBOT - RTOP, fill=SHADE)

    # QUIESCENT, the initial state, above the region.
    b += state(LX, QY, "QUIESCENT")
    b += text(LX + BW / 2 + 60, QY + 4, "VendingMachine()", 11, MUTED)
    b += arrow((LX + BW / 2 + 54, QY), (LX + BW / 2, QY), MUTED, "vs-muted")
    b += text(W - 16, 26, "each edge:", 10, MUTED, "end")
    b += text(W - 16, 40, "event [condition] / action", 10, MUTED, "end")

    # Quit / refund, once for all four shaded states.
    qx = LX + 22
    b += arrow((qx, RTOP), (qx, QY + bot), INK, "vs-ink")
    b += label(qx + 8, QY + bot + 18, ("Quit / refund",), "start")
    b += text(qx + 8 + 13 * 6.6 + 16, QY + bot + 18,
              "from every shaded state", 10.5, MUTED)
    # Money into COLLECTING, and Money again while collecting.
    mx = LX - 22
    b += arrow((mx, QY + bot), (mx, SY + top), INK, "vs-ink")
    b += label(mx - 8, 190, ("Money", "/ add_money"), "end")
    ly = SY + bot + 26
    b += line((LX - 30, SY + bot), (LX - 30, ly), INK, 1.3)
    b += line((LX - 30, ly), (LX + 30, ly), INK, 1.3)
    b += arrow((LX + 30, ly), (LX + 30, SY + bot), INK, "vs-ink")
    b += label(LX, ly + 18, ("Money", "/ add_money"), "middle")

    # The hub's spokes.
    b += state(LX, SY, "COLLECTING")
    b += state(RX, SY, "SELECTING", RED)
    b += state(RX, UY, "UNAVAILABLE")
    b += state(RX, WY, "WANT_MORE")
    first = ("FirstDigit", "/ choose_row")
    # COLLECTING and SELECTING, side by side.
    l, r = LX + BW / 2, RX - BW / 2
    b += arrow((l, SY - OFF), (r, SY - OFF), INK, "vs-ink")
    b += label((l + r) / 2, SY - OFF - 22, first, "middle")
    b += arrow((r, SY + OFF), (l, SY + OFF), RED, "vs-red")
    b += label((l + r) / 2, SY + OFF + 18,
               ("1 SecondDigit", "[too_expensive]", "/ clear"), "middle",
               red=True)
    # UNAVAILABLE above SELECTING, WANT_MORE below it.
    for y, row in ((UY, ("2 SecondDigit", "[sold_out]", "/ clear")),
                   (WY, ("3 SecondDigit", "/ dispense"))):
        other = y + (bot if y < SY else top)
        hub = SY + (top if y < SY else bot)
        mid = (other + hub) / 2
        b += arrow((RX - OFF, other), (RX - OFF, hub), INK, "vs-ink")
        b += label(RX - OFF - 8, mid - 3, first, "end")
        b += arrow((RX + OFF, hub), (RX + OFF, other), RED, "vs-red")
        b += label(RX + OFF + 8, mid - 10 if len(row) == 3 else mid - 3,
                   row, "start", red=True)
    b += text(RX + BW / 2 + 14, SY - 4, "SecondDigit tries", 10.5, RED)
    b += text(RX + BW / 2 + 14, SY + 10, "rows 1, 2, 3 in order;", 10.5,
              RED)
    b += text(RX + BW / 2 + 14, SY + 24, "the first that passes wins",
              10.5, RED)
    defs = markers(**{"vs-ink": ("filled", INK), "vs-red": ("filled", RED),
                      "vs-muted": ("filled", MUTED)})
    return svg(W, H, TITLE, defs, b)
