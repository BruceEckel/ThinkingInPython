"""Chapter 25, Template Method: the anchored loop, filled in two ways.

Three frames of one layout, so only the changes stand out. The top box
in every frame is the anchored algorithm, outlined in red because it
never changes: a loop that runs twice and calls two steps in order.
Frame 1 shows the base alone: `run()` calls its own hooks, which
default to `...` and do nothing.
Frame 2 fills them with `MyApp`'s overrides: the client calls
`MyApp().run()`, the base calls the subclass's methods (the Hollywood
Principle), and the output column shows the four lines the loop
produces. Frame 3 keeps the loop and drops the class: `run_framework()`
takes the steps as two lambdas and prints the same four lines.

A storyboard suits this pattern because its point is who calls whom and
in what order, which a class diagram cannot show: the coupling panel
drew `MyApp` inheriting from `ApplicationFramework`, not the loop
calling `MyApp`'s code. The names, strings, and output come from
`template_method.py` (frames 1 and 2) and `template_function.py`
(frame 3).
"""

from tools.story_figures import (INK, MUTED, RED, arrow, line, markers,
                                 rect, region, svg, text)

STEM = "template_method_story"
W = 730
FH = 222  # One frame's height
AX, AW = 145, 395  # The anchored algorithm's box
SLOT_X = (165, 355)  # Each step's left edge, above and below
SW, SH = 170, 30  # A step slot in the loop
LOW_Y, LOW_H = 160, 42  # The boxes that supply the steps
OX = 562  # The output column
STEPS = ("customize1()", "customize2()")
TITLE = ("Three steps of Template Method: ApplicationFramework.run() "
         "sets the order of two steps, MyApp overrides them and run() "
         "calls each one twice, and run_framework() runs the same loop "
         "on two lambdas")


def mid(k: int) -> float:
    return SLOT_X[k] + SW / 2


def frame(i: int, y0: float, name: str, title: str, lines: tuple[str, ...],
          ) -> str:
    """The layout every frame shares: the gutter and the anchored loop."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    out += region(AX, y0 + 14, AW, 100, stroke=RED)
    out += text(AX + 12, y0 + 36, title, 13, bold=True)
    out += text(AX + 12, y0 + 58, "for _ in range(2):", 11)
    for k, s in enumerate(STEPS):
        out += rect(SLOT_X[k], y0 + 70, SW, SH, stroke=INK, width=1.1, rx=3)
        out += text(mid(k), y0 + 89, s, 11, INK, "middle")
    return out


def supplier(y0: float, label: str, heads: tuple[str, str],
             bodies: tuple[str, str], calls: tuple[str, str]) -> str:
    """The lower band: what supplies each step, and the calls into it."""
    out = region(AX, y0 + LOW_Y - 22, AW, LOW_H + 34, stroke=INK)
    out += text(AX + 12, y0 + LOW_Y - 6, label, 11, INK, bold=True)
    for k in range(2):
        x = SLOT_X[k]
        out += rect(x, y0 + LOW_Y, SW, LOW_H)
        out += text(mid(k), y0 + LOW_Y + 16, heads[k], 11, INK, "middle")
        out += text(mid(k), y0 + LOW_Y + 32, bodies[k], 10, MUTED, "middle")
        out += arrow((mid(k), y0 + 70 + SH), (mid(k), y0 + LOW_Y), INK,
                     "tms-ink")
        out += text(mid(k) + 6, y0 + 128, calls[k], 10, INK)
    return out


def output(y0: float, call: str) -> str:
    """The right-hand column: the client's call and the four lines."""
    out = text(OX, y0 + 36, call, 11, RED)
    out += text(OX, y0 + 54, "prints", 10, MUTED)
    lines = ("Nudge, nudge, wink, wink!", "Say no more, say no more!") * 2
    for j, s in enumerate(lines):
        out += text(OX, y0 + 76 + j * 17, s, 10)
    return out


def render() -> str:
    y = [10 + i * FH for i in range(3)]
    b = ""
    calls = ("self.customize1()", "self.customize2()")
    said = ('"Nudge, nudge, wink, wink!"', '"Say no more, say no more!"')

    y0 = y[0]
    b += frame(0, y0, "anchor", "ApplicationFramework",
               ("run() sets the", "order; each", "step is a hook"))
    b += text(AX + AW - 12, y0 + 36, "@final run()", 11, RED, "end")
    b += supplier(y0, "hooks", STEPS,
                  ("...", "..."), calls)
    b += text(OX, y0 + 36, "@final:", 11)
    b += text(OX, y0 + 54, "no subclass may", 10, MUTED)
    b += text(OX, y0 + 68, "override run()", 10, MUTED)

    y0 = y[1]
    b += frame(1, y0, "fill in", "ApplicationFramework",
               ("MyApp overrides", "the steps;", "run() calls them"))
    b += text(AX + AW - 12, y0 + 36, "@final run()", 11, RED, "end")
    b += supplier(y0, "MyApp", STEPS, said, calls)
    b += output(y0, "MyApp().run()")

    y0 = y[2]
    b += frame(2, y0, "pass", "run_framework()",
               ("the same loop", "in a function;", "the steps come",
                "in as arguments"))
    b += text(AX + AW - 12, y0 + 36, "no @final", 11, MUTED, "end")
    b += supplier(y0, "two lambdas", ("lambda", "lambda"), said, STEPS)
    b += output(y0, "run_framework()")

    defs = markers(**{"tms-ink": ("filled", INK)})
    return svg(W, 10 + 3 * FH, TITLE, defs, b)
