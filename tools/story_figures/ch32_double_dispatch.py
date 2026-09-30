"""Chapter 32, Multiple Dispatching: one duel's two calls.

Chapter 32's second figure, after `paper_scissors_rock.py`, follows the
duel the prose follows, `scissors.compete(paper)`. It replaced a UML
sequence diagram on 2026-09-29. The two calls sit side by side, each
with its `self` and `item`; two crossing arrows between them show the
arguments trading places, the detail the sequence diagram left to an
italic note. Under each call, the figure says which types are known:
after the first dispatch, `Scissors` alone; after the second, `Paper`
from `self` and `Scissors` from the method's name. The bottom band
carries `Outcome.WIN` back to `duel()` and says whose result it is,
the point the prose under the figure turns on. Names and the printed
line come from `paper_scissors_rock.py` and `arena.py`.
"""

from tools.story_figures import (INK, MUTED, RED, Point, arrow, markers,
                                 rect, region, svg, text)

STEM = "double_dispatch"
W = 730
LX, RX = 20, 410  # The two calls' regions
RW = 300
BOX_W, BOX_H = 250, 34  # The self and item boxes
SELF_Y, ITEM_Y = 125, 175
TITLE = ("One duel's two calls: scissors.compete(paper) knows only "
         "Scissors, so it calls paper.eval_scissors(scissors) with self "
         "and item swapped, which knows both types and returns WIN, the "
         "result for scissors")


def slots(x: float, self_name: str, item_name: str) -> str:
    """The `self` and `item` boxes of one call, left edge `x`."""
    return (rect(x, SELF_Y, BOX_W, BOX_H, stroke=INK, width=1.1)
            + text(x + 12, SELF_Y + 22, "self", 11, MUTED)
            + text(x + BOX_W / 2 + 20, SELF_Y + 22, self_name, 12.5,
                   INK, "middle")
            + rect(x, ITEM_Y, BOX_W, BOX_H, stroke=INK, width=1.1)
            + text(x + 12, ITEM_Y + 22, "item", 11, MUTED)
            + text(x + BOX_W / 2 + 20, ITEM_Y + 22, item_name, 12.5,
                   INK, "middle"))


def call(x: float, n: int, step: str, caller: str, code: str,
         method: str) -> str:
    """One call's header, code line, and region with its method name."""
    return (text(x, 34, str(n), 26, RED, bold=True)
            + text(x + 24, 32, step, 13, bold=True)
            + text(x, 64, caller, 12, MUTED)
            # JetBrains Mono advances 0.6 em per character
            + text(x + (len(caller) + 1) * 7.2, 64, code, 12)
            + region(x, 80, RW, 200, stroke=INK)
            + text(x + 20, 107, method, 13, bold=True))


def render() -> str:
    b = ""
    lb, rb = LX + 20, RX + 20  # Left edges of the slot boxes

    b += call(LX, 1, "first dispatch", "duel() calls",
              "scissors.compete(paper)", "Scissors.compete()")
    b += slots(lb, "scissors", "paper")
    b += text(lb, 238, "self's type picks the method:", 10.5, MUTED)
    b += text(lb, 256, "Scissors known", 11, RED)
    b += text(lb, 272, "item's type still unknown", 10.5, MUTED)

    b += call(RX, 2, "second dispatch", "compete() calls",
              "item.eval_scissors(self)", "Paper.eval_scissors()")
    b += slots(rb, "paper", "scissors")
    b += text(rb, 238, "self's type picks the method:", 10.5, MUTED)
    b += text(rb, 256, "Paper known", 11, RED)
    b += text(rb, 272, "Scissors known from the name", 10.5, INK)

    # The arguments trade places between the two calls.
    ls: Point = (lb + BOX_W, SELF_Y + BOX_H / 2)
    li: Point = (lb + BOX_W, ITEM_Y + BOX_H / 2)
    rs: Point = (rb, SELF_Y + BOX_H / 2)
    ri: Point = (rb, ITEM_Y + BOX_H / 2)
    b += arrow(ls, ri, INK, "dd-ink")
    b += arrow(li, rs, INK, "dd-ink")
    b += text((ls[0] + rs[0]) / 2, SELF_Y - 8, "swap", 11, RED, "middle")

    # The answer travels back to duel(), and it is the scissors' result.
    b += text(LX, 334, "3", 26, RED, bold=True)
    b += text(LX + 24, 332, "answer", 13, bold=True)
    b += rect(rb, 350, BOX_W, BOX_H, stroke=INK, width=1.1)
    b += text(rb + BOX_W / 2, 372, "return Outcome.WIN", 12, INK,
              "middle")
    b += rect(lb, 350, BOX_W, BOX_H, stroke=INK, width=1.1)
    b += text(lb + BOX_W / 2, 372, "duel() prints", 12, INK, "middle")
    b += arrow((rb, 367), (lb + BOX_W, 367), MUTED, "dd-muted",
               kind="open", dash=True)
    b += text((lb + BOX_W + rb) / 2, 357, "via", 10.5, MUTED, "middle")
    b += text((lb + BOX_W + rb) / 2, 386, "compete()", 10.5, MUTED,
              "middle")
    b += text(lb, 410, "Scissors <--> Paper : win", 12.5, RED)
    b += text(lb, 440, "WIN answers for scissors, the type in the name "
              "eval_scissors,", 11, RED)
    b += text(lb, 457, "not for the Paper whose code runs: scissors cut "
              "paper.", 11, RED)

    defs = markers(**{"dd-ink": ("filled", INK),
                      "dd-muted": ("open", MUTED)})
    return svg(W, 475, TITLE, defs, b)
