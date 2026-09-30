"""Chapter 37, Pattern Refactoring: one run of the dictionary sorter.

The figure sits in "The `Trash` Hierarchy", whose argument is that a new
recyclable type costs one class definition: it registers itself, and
`create()` builds it. It replaced a class tree on 2026-09-29, which showed
the four materials and a `bins` box but not the run that makes the claim
true. This one follows `recycle_dict_plastic.py` over `plastic.dat`: the
`class Plastic(Trash)` statement adds `"Plastic"` to `Trash.registry`
through `__init_subclass__()`; each data line becomes an object through
`Trash.create()`, which reads that registry; and `bins[type(t)]` drops
each object into the bin for its exact class, so `Plastic` gets a bin of
its own. Everything that says Plastic is red, the one thing the reader
follows; nothing else in the drawing names it, which is the point: the
parser and the sorting line stay as they are.

Names and values come from `trash.py` (the registry, `create()`, the
four materials), `plastic.dat`, `parse_trash.py`, and
`recycle_dict_plastic.py`, whose `#:` output supplies the bin headers,
the totals, and `parsed 4, binned 4`. The object labels are the
`@record` reprs (`weight` is parsed as a float).
"""

from tools.story_figures import (BOX, INK, MUTED, RED, arrow, markers,
                                 rect, svg, text)

STEM = "trash_sorter"
W, H = 730, 395
TITLE = ("The four lines of plastic.dat pass through Trash.create(), which "
         "reads Trash.registry, and bins[type(t)], which files each piece "
         "under its exact class; the new Plastic class registers itself "
         "and gets its own bin with no edit to the parser or the sorter")

PIECES = [("Glass:10", "Glass(weight=10.0)", 0),
          ("Plastic:20", "Plastic(weight=20.0)", 1),
          ("Aluminum:30", "Aluminum(weight=30.0)", 2),
          ("Plastic:40", "Plastic(weight=40.0)", 1)]
BINS = [("Glass", "2.30"), ("Plastic", "9.00"), ("Aluminum", "50.10")]
ROW0, ROW_STEP = 206, 42  # Center of the first piece row, and spacing
DAT_X, DAT_W = 20, 110
OBJ_X, OBJ_W, OBJ_H = 172, 170, 28
BIN_X, BIN_W, BIN_H = 540, 180, 46
BIN_Y = [174, 235, 296]  # Top of each bin box
REG_X, REG_Y, REG_W, REG_H = 102, 20, 310, 72


def color(name: str) -> str:
    return RED if name.startswith("Plastic") else INK


def render() -> str:
    b = ""
    # The class statement registers the new material.
    cx, cy, cw, ch = 490, 28, 230, 48
    b += rect(cx, cy, cw, ch, stroke=RED, width=1.3)
    b += text(cx + 10, cy + 19, "class Plastic(Trash):", 10.5, RED)
    b += text(cx + 22, cy + 36, "value: ClassVar[float] = 0.15", 10,
              RED)
    b += text(cx, cy + ch + 18, "__init_subclass__()", 10, MUTED)
    b += text(cx, cy + ch + 32, "adds it to the registry", 10, MUTED)

    b += rect(REG_X, REG_Y, REG_W, REG_H, stroke=INK, width=1.1)
    b += text(REG_X + 12, REG_Y + 22, "Trash.registry", 11.5, INK,
              bold=True)
    px = REG_X + 12
    for name in ["Aluminum", "Paper", "Glass", "Cardboard", "Plastic"]:
        w = len(name) * 6 + 12
        red = name == "Plastic"
        b += rect(px, REG_Y + 36, w, 24, stroke=RED if red else BOX,
                  width=1.3 if red else 1.1)
        b += text(px + w / 2, REG_Y + 52, name, 10, RED if red else INK,
                  "middle")
        px += w + 6
    b += arrow((cx, cy + ch / 2), (REG_X + REG_W, cy + ch / 2), RED,
               "ts-red")

    # Column headers.
    head_y = 148
    b += text(DAT_X, head_y, "plastic.dat", 11.5, bold=True)
    ox = OBJ_X + OBJ_W / 2
    b += text(ox, head_y, "Trash.create()", 11.5, INK, "middle",
              bold=True)
    b += text(ox, head_y + 15, "registry[name](weight)", 10, MUTED,
              "middle")
    sx = (OBJ_X + OBJ_W + BIN_X) / 2
    b += text(sx, head_y, "bins[type(t)].append(t)", 11.5, INK, "middle",
              bold=True)
    b += text(sx, head_y + 15, "no case per material", 10, MUTED,
              "middle")
    # create() looks up each name in the registry.
    b += arrow((ox, head_y - 16), (ox, REG_Y + REG_H), MUTED, "ts-muted")

    # The data file.
    top = ROW0 - ROW_STEP / 2 - 4
    dat_h = ROW_STEP * len(PIECES) + 8
    b += rect(DAT_X, top, DAT_W, dat_h, stroke=BOX, width=1.1)
    for i, (line, obj, k) in enumerate(PIECES):
        y = ROW0 + i * ROW_STEP
        c = color(line)
        b += text(DAT_X + 12, y + 4, line, 11, c)
        b += arrow((DAT_X + DAT_W, y), (OBJ_X, y), c,
                   "ts-red" if c == RED else "ts-ink")
        b += rect(OBJ_X, y - OBJ_H / 2, OBJ_W, OBJ_H,
                  stroke=RED if c == RED else INK, width=1.1)
        b += text(OBJ_X + OBJ_W / 2, y + 4, obj, 10.5, c, "middle")
        # The two Plastic arrows meet their bin apart, not in one point.
        by = BIN_Y[k] + BIN_H / 2 + {1: -9, 3: 9}.get(i, 0)
        b += arrow((OBJ_X + OBJ_W, y), (BIN_X, by), c,
                   "ts-red" if c == RED else "ts-ink")

    # The bins, with what recycle_dict_plastic.py prints for each.
    for (name, total), y in zip(BINS, BIN_Y, strict=True):
        c = color(name)
        b += rect(BIN_X, y, BIN_W, BIN_H, stroke=c,
                  width=1.6 if c == RED else 1.1)
        b += text(BIN_X + 12, y + 19, f"--- {name} ---", 11, c, bold=True)
        b += text(BIN_X + 12, y + 36, f"Total value = {total}", 10.5, c)
    b += text(BIN_X, BIN_Y[-1] + BIN_H + 26, "parsed 4, binned 4", 11.5,
              INK, bold=True)

    defs = markers(**{"ts-ink": ("filled", INK), "ts-red": ("filled", RED),
                      "ts-muted": ("filled", MUTED)})
    return svg(W, H, TITLE, defs, b)
