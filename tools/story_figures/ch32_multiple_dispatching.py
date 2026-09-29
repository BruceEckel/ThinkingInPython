"""Chapter 32, Multiple Dispatching: one grid of answers, stored two ways.

Paper, scissors, rock has nine answers, one per pair of types, and both
versions of the game hold the same nine. The figure draws them as one
grid twice, rows for the caller and columns for its opponent, so the
reader sees where each version keeps them. On the left,
`paper_scissors_rock.py` spreads the grid across the classes: each
column is one class, each row one `eval_*()` method, and the two
dispatches of `scissors.compete(paper)` pick the row and then the
column. On the right, `paper_scissors_rock_table.py` keeps the grid in
one dict, `OUTCOME`, and one lookup picks the same cell. Both listings
print `Scissors <--> Paper : win` first. A dashed fourth item shows the
cost of growth: on the left its row adds a method to every existing
class, on the right it adds rows to `OUTCOME` alone.

The chapter's `double_dispatch.svg` already draws the call sequence of
that one duel, so this figure draws the answers, not the calls. Cell
values are the `eval_*()` returns and the `OUTCOME` rows, printed the
way the `StrEnum` prints them. No listing has a fourth item, so its
cells are dashed and unnamed.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, line, rect, region,
                                 svg, text)

STEM = "dispatch_story"
W = 740
LX, RX = 14, 386  # Left edge of each panel
RL = 100  # Width of the row-label column
CW, CH = 60, 26  # One cell
HEAD_Y = 60  # Top of the column-header row
NAMES = ("Paper", "Scissors", "Rock")
# ANSWER[caller][opponent], from Paper.eval_paper() and the OUTCOME rows
ANSWER = (("draw", "lose", "win"),
          ("win", "draw", "lose"),
          ("lose", "win", "draw"))
PICK = (1, 0)  # Caller Scissors, opponent Paper
TITLE = ("The nine paper, scissors, rock answers drawn as a grid twice: "
         "the method version spreads them across the classes and picks "
         "a cell with two dispatches, the table version keeps them in "
         "OUTCOME and picks the same cell with one lookup")


def col_x(x0: float, c: int) -> float:
    return x0 + RL + c * CW


def row_y(r: int) -> float:
    return HEAD_Y + CH + r * CH


def grid(x0: float, rows: tuple[str, ...], new_fill: str) -> str:
    """Headers, the nine answers, and the dashed fourth item."""
    out = ""
    for c, name in enumerate(NAMES):
        fill = RED if c == PICK[1] else INK
        out += text(col_x(x0, c) + CW / 2, HEAD_Y + 17, name, 10.5, fill,
                    "middle", bold=True)
    out += text(col_x(x0, 3) + CW / 2, HEAD_Y + 17, "new", 10.5, MUTED,
                "middle")
    for r, label in enumerate(rows):
        fill = RED if r == PICK[0] else INK
        out += text(x0 + RL - 6, row_y(r) + 17, label, 10.5, fill, "end")
        for c in range(3):
            picked = (r, c) == PICK
            out += rect(col_x(x0, c) + 3, row_y(r) + 3, CW - 6, CH - 6,
                        stroke=RED if picked else BOX,
                        width=1.6 if picked else 1, rx=3)
            out += text(col_x(x0, c) + CW / 2, row_y(r) + 17, ANSWER[r][c],
                        10.5, RED if picked else INK, "middle",
                        bold=picked)
    out += text(x0 + RL - 6, row_y(3) + 17, "new", 10.5, MUTED, "end")
    for r, c in [(r, 3) for r in range(4)] + [(3, c) for c in range(3)]:
        edit = new_fill == RED and r == 3 and c < 3
        out += rect(col_x(x0, c) + 3, row_y(r) + 3, CW - 6, CH - 6,
                    stroke=RED if edit else BOX, width=1.3 if edit else 1,
                    dash=True, rx=3)
    return out


def render() -> str:
    b = ""
    bottom = row_y(4)

    # Left: the methods version, one class per column
    b += text(LX, 20, "two dispatches", 13, bold=True)
    b += text(LX, 36, "paper_scissors_rock.py", 10.5, MUTED)
    b += text(col_x(LX, 0), HEAD_Y - 8, "each column is one class", 10,
              MUTED)
    for c in range(4):
        b += region(col_x(LX, c), HEAD_Y, CW, bottom - HEAD_Y,
                    stroke=INK if c < 3 else MUTED, width=1.2,
                    dash=(c == 3))
    b += grid(LX, ("eval_paper()", "eval_scissors()", "eval_rock()"), RED)
    y = bottom + 22
    b += text(LX, y, "1", 13, RED, bold=True)
    b += text(LX + 16, y, "scissors.compete(paper)", 10.5)
    b += text(LX + 16, y + 14, "resolves self: the row", 10.5, MUTED)
    b += text(LX, y + 36, "2", 13, RED, bold=True)
    b += text(LX + 16, y + 36, "paper.eval_scissors(...)", 10.5)
    b += text(LX + 16, y + 50, "resolves paper: the column", 10.5, MUTED)
    b += text(LX, y + 76, "a new item adds an eval method", 10.5, RED)
    b += text(LX, y + 90, "to Paper, Scissors, and Rock", 10.5, RED)

    b += line((RX - 22, 10), (RX - 22, y + 96))

    # Right: the table version, one dict
    b += text(RX, 20, "one lookup", 13, bold=True)
    b += text(RX, 36, "paper_scissors_rock_table.py", 10.5, MUTED)
    b += text(col_x(RX, 0), HEAD_Y - 8, "keys (type(self), type(item))",
              10, MUTED)
    b += text(RX + RL - 6, HEAD_Y + 17, "OUTCOME", 11, bold=True,
              anchor="end")
    b += region(col_x(RX, 0) - 2, HEAD_Y + CH - 2, 4 * CW + 4,
                4 * CH + 4, stroke=INK, width=1.2)
    b += grid(RX, NAMES, MUTED)
    b += text(RX, y, "1", 13, RED, bold=True)
    b += text(RX + 16, y, "OUTCOME[type(self), type(item)]", 10.5)
    b += text(RX + 16, y + 14, "picks the row and the column", 10.5, MUTED)
    b += text(RX + 16, y + 28, "in one step", 10.5, MUTED)
    b += text(RX, y + 76, "a new item adds 7 rows to", 10.5, RED)
    b += text(RX, y + 90, "OUTCOME, with no methods to edit", 10.5, RED)

    b += text(W / 2 - 4, y + 122, "both print", 10.5, MUTED, "end")
    b += text(W / 2 + 4, y + 122, "Scissors <--> Paper : win", 11)
    return svg(W, y + 134, TITLE, "", b)
