"""Chapter 16, Comprehensions: the parts, and the order Python runs them.

The figure sits under `list_comprehension.py`, whose comprehension is
`[e ** 2 for e in a_list if isinstance(e, int)]`, and it replaced a
hand-drawn figure that labeled the four parts on 2026-09-29. The top
band keeps those labels (the chapter's list names them) and numbers
each part by when it runs, so the reader sees that the order of
evaluation differs from the order of reading: the output expression,
written first, runs last. The table below runs the chapter's own
`a_list` (`a_list.py`, `[1, "4", 9, "a", 0, 4]`) through the numbered
steps: step 1 evaluates `a_list` once, then each column is one element
taking steps 2, 3, and 4 top to bottom. The two strings stop at step 3,
and their shaded columns contribute nothing. The bottom line is the
listing's `#:` output, `[1, 81, 0, 16]`.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, SHADE, arrow,
                                 line, markers, rect, region, svg, text)

STEM = "listComprehensions"
W = 720
CW = 10.2  # Width of one character at the comprehension's 17
TITLE = ("The list comprehension [e ** 2 for e in a_list if "
         "isinstance(e, int)] with its parts numbered by the order Python "
         "evaluates them, a_list first, then for each element the variable, "
         "the filter, and last the output expression, and a table that "
         "runs a_list = [1, \"4\", 9, \"a\", 0, 4] through those steps to "
         "give [1, 81, 0, 16]")

# The comprehension line.
BOX_Y, BOX_H = 64, 42
A_X, A_W = 60, 90  # e ** 2
B_X, B_W = 166, 190  # for e in a_list
C_X, C_W = 372, 290  # if isinstance(e, int)
B_TEXT = B_X + 18
C_TEXT = C_X + (C_W - 21 * CW) / 2


def step(cx: float, y: float, n: int, label: str) -> str:
    """A red step number and its part's name, centered on `cx`."""
    width = len(label) * 7.2 + 18  # Numeral plus gap, then the name
    left = cx - width / 2
    return (text(left, y + 2, str(n), 18, RED, bold=True)
            + text(left + 18, y, label, 12, INK, bold=True))


def comprehension() -> str:
    b = text(32, BOX_Y + 33, "[", 36, INK)
    b += text(C_X + C_W + 12, BOX_Y + 33, "]", 36, INK)
    b += rect(A_X, BOX_Y, A_W, BOX_H)
    b += text(A_X + A_W / 2, BOX_Y + 27, "e ** 2", 17, INK, "middle",
              bold=True)
    b += rect(B_X, BOX_Y, B_W, BOX_H)
    b += text(B_TEXT, BOX_Y + 27, "for e in a_list", 17, INK, bold=True)
    b += rect(C_X, BOX_Y, C_W, BOX_H)
    b += text(C_TEXT, BOX_Y + 27, "if isinstance(e, int)", 17, INK,
              bold=True)

    e_x = B_TEXT + 4.5 * CW  # Center of "e"
    list_x = B_TEXT + 12 * CW  # Center of "a_list"
    c_x = C_X + C_W / 2
    a_x = A_X + A_W / 2
    top, bottom = BOX_Y, BOX_Y + BOX_H
    b += step(a_x + 30, 22, 4, "Output Expression")
    b += arrow((a_x, 28), (a_x, top), MUTED, "lc-muted")
    b += step(list_x, 22, 1, "Input Sequence")
    b += arrow((list_x, 28), (list_x, top), MUTED, "lc-muted")
    b += arrow((e_x, bottom + 26), (e_x, bottom), MUTED, "lc-muted")
    b += step(e_x, bottom + 42, 2, "Variable")
    # A bracket under the whole filter.
    b += line((C_X + 4, bottom + 6), (C_X + 4, bottom + 11), MUTED, 1.2)
    b += line((C_X + C_W - 4, bottom + 6), (C_X + C_W - 4, bottom + 11),
              MUTED, 1.2)
    b += line((C_X + 4, bottom + 11), (C_X + C_W - 4, bottom + 11), MUTED,
              1.2)
    b += line((c_x, bottom + 11), (c_x, bottom + 26), MUTED, 1.2)
    b += step(c_x, bottom + 42, 3, "Optional Filter")
    return b


# The trace table.
LABEL_X = 24
COL_X, COL_W = 222, 80  # Left edge of the first element column
VALUES = ["1", '"4"', "9", '"a"', "0", "4"]
IS_INT = [True, False, True, False, True, True]
SQUARES = ["1", "", "81", "", "0", "16"]
ROW1_Y = 196  # Baselines
ROWS_Y = [258, 290, 322]
RESULT_Y = 368


def col_x(i: int) -> float:
    """Center of element column `i`."""
    return COL_X + COL_W * i + COL_W / 2


def trace() -> str:
    b = line((LABEL_X, 160), (W - 24, 160), BOX, 0.8)
    # Step 1: a_list, evaluated once, drawn as the list's six cells.
    b += text(LABEL_X, ROW1_Y + 2, "1", 18, RED, bold=True)
    b += text(LABEL_X + 18, ROW1_Y, "a_list, once", 12, INK)
    for i, v in enumerate(VALUES):
        b += rect(COL_X + COL_W * i + 6, ROW1_Y - 20, COL_W - 12, 30,
                  stroke=INK, width=1.1)
        b += text(col_x(i), ROW1_Y, v, 13, INK, "middle")
    b += text(LABEL_X, 230, "then per element, left to right:", 11, MUTED)
    # The strings fail the filter; their columns stop at step 3.
    for i, ok in enumerate(IS_INT):
        if not ok:
            b += region(COL_X + COL_W * i + 6, 240, COL_W - 12, 96,
                        fill=SHADE)
    labels = [("2", "e ="), ("3", "isinstance(e, int)"),
              ("4", "e ** 2")]
    for (n, label), y in zip(labels, ROWS_Y):
        b += text(LABEL_X, y + 2, n, 18, RED, bold=True)
        b += text(LABEL_X + 18, y, label, 12, INK)
    for i in range(len(VALUES)):
        x = col_x(i)
        b += text(x, ROWS_Y[0], VALUES[i], 13, INK, "middle")
        if IS_INT[i]:
            b += text(x, ROWS_Y[1], "True", 12, INK, "middle")
            b += text(x, ROWS_Y[2], SQUARES[i], 13, INK, "middle",
                      bold=True)
        else:
            b += text(x, ROWS_Y[1], "False", 12, RED, "middle")
            b += text(x, ROWS_Y[2], "skipped", 10.5, MUTED, "middle")
    b += text(LABEL_X, RESULT_Y, "squared_ints =", 12, INK)
    b += text(COL_X + 6, RESULT_Y, "[1, 81, 0, 16]", 14, INK, bold=True)
    return b


def render() -> str:
    defs = markers(**{"lc-muted": ("filled", MUTED)})
    return svg(W, 388, TITLE, defs, comprehension() + trace())
