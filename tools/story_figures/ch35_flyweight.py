"""Chapter 35, Flyweight: four frames of `tile_map.py`'s factory at work.

The chapter's opening names two ideas: split each object's state into an
intrinsic part the shared object holds and an extrinsic part the context
supplies, and construct every object through a factory that returns the
existing instance for a value. The coupling panel showed who names whom;
this figure shows the factory's cache filling and answering, one layout
per frame: the parsed grid on the left, `tile()` and its `@cache` entries
in the middle, the shared `Tile` objects on the right.

1. `parse_map()` reaches `field[0][2]` and calls `tile("~")`. The cache
   has no `"~"` entry, so `tile()` builds a `Tile` and caches it.
2. `field[0][3]` calls `tile("~")` again, and the cache returns the same
   `Tile` without running the body.
3. `field[1][5].walkable` reads the rock tile through the grid: the grid
   holds the position, the `Tile` holds the rest.
4. `test_tile_map.py`'s direct `Tile("~", "water", False)` skips the
   cache and builds a second object, equal to the cached one and not the
   same one: the reason every construction must go through the factory.

Chapter 35's `flyweight_tiles.svg` already shows the whole grid resolving
to three objects, so this figure shows how the factory gets there. The
names come from `tile_map.py` (`parse_map`, `tile`, `SPECS`, `Tile`, the
map text) and frame 4's lines from `test_tile_map.py`.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, SHADE, arrow, line,
                                 markers, rect, region, svg, text)

STEM = "flyweight_story"
W = 730
FH = (154, 154, 192, 206)  # Each frame's height
GX, GY, CELL = 150, 34, 22  # The grid of parsed cells
MAP = ("..~~..", "..~~.#", "......", "##..~~")
FX, FW, FTOP, FBOT = 336, 170, 14, 132  # The tile() box
SX, SW = 446, 50  # Its cache entries
KEYS = (".", "~", "#")
RX, RW, RH = 540, 170, 28  # The Tile objects
ROW_Y = (22, 62, 102, 146)  # Tile rows; the fourth is frame 4's bypass
TILES = ('Tile(".", "grass", True)', 'Tile("~", "water", False)',
         'Tile("#", "rock", False)', 'Tile("~", "water", False)')
TITLE = ("Four steps of Flyweight: tile() builds a Tile on the first "
         "request for a symbol and caches it, returns that same Tile on "
         "every later request, the grid supplies each cell's position, "
         "and a direct Tile() call builds a second, equal object")


def row_mid(y0: float, k: int) -> float:
    return y0 + ROW_Y[k] + RH / 2


def grid(y0: float, parsed: int, active: tuple[int, int] | None) -> str:
    """The map's cells; the first `parsed` are shaded as parsed."""
    out = text(GX, y0 + GY - 8, "field", 10, MUTED)
    for r, row in enumerate(MAP):
        for c, s in enumerate(row):
            x, y = GX + c * CELL, y0 + GY + r * CELL
            done = r * 6 + c < parsed
            out += region(x, y, CELL, CELL, stroke=BOX, width=0.8,
                          fill=SHADE if done else "none", r=0)
            out += text(x + CELL / 2, y + 15, s, 12,
                        INK if done or (r, c) == active else MUTED, "middle")
    if active:
        x, y = GX + active[1] * CELL, y0 + GY + active[0] * CELL
        out += region(x, y, CELL, CELL, stroke=RED, width=2, r=0)
    return out


def frame(i: int, y0: float, filled: int, hot: int | None, name: str,
          lines: tuple[str, ...]) -> str:
    """The layout every frame shares, with `filled` cache entries."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += rect(FX, y0 + FTOP, FW, FBOT - FTOP, stroke=INK)
    out += text(FX + 10, y0 + 34, "tile()", 13, bold=True)
    out += text(FX + 10, y0 + 50, "@cache", 10, MUTED)
    for k, key in enumerate(KEYS):
        y = y0 + ROW_Y[k]
        on = k < filled
        color = RED if k == hot else INK if on else BOX
        out += rect(SX, y, SW, RH, stroke=color,
                    width=1.6 if k == hot else 1.1, dash=not on, rx=3)
        if on:
            out += text(SX + SW / 2, y + 18, f'"{key}"', 11, color, "middle")
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)
    return out


def tile_box(y0: float, k: int, color: str = BOX, label: str = INK) -> str:
    y = y0 + ROW_Y[k]
    return (rect(RX, y, RW, RH, stroke=color,
                 width=1.6 if color == RED else 1.3)
            + text(RX + RW / 2, y + 18, TILES[k], 10.5, label, "middle"))


def link(y0: float, k: int, color: str = MUTED) -> str:
    """A cache entry's reference to its Tile."""
    y = row_mid(y0, k)
    hot = color == RED
    return arrow((SX + SW, y), (RX, y), color, "fs-red" if hot else "fs-muted",
                 width=1.6 if hot else 1.1)


def call(y0: float, c: int, s: str) -> str:
    """Row 0's active cell calling tile(), routed above the grid."""
    x, top = GX + c * CELL + CELL / 2, y0 + GY
    lane = y0 + 24
    return (line((x, top), (x, lane), RED, 1.6)
            + arrow((x, lane), (FX, lane), RED, "fs-red", width=1.6)
            + text(FX - 30, lane - 6, s, 10, RED, "end"))


def render() -> str:
    y = [10 + sum(FH[:i]) for i in range(4)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, 2, 1, "miss",
               ('no "~" entry,', "so tile()", "builds a Tile", "and caches it"))
    b += grid(y0, 2, (0, 2))
    b += call(y0, 2, 'tile("~")')
    b += text(FX + 10, y0 + 90, 'SPECS["~"]', 10.5, RED)
    b += text(FX + 10, y0 + 106, "then", 10, MUTED)
    b += text(FX + 10, y0 + 122, "Tile(...)", 10.5, RED)
    b += tile_box(y0, 0) + link(y0, 0)
    b += tile_box(y0, 1, RED, RED) + link(y0, 1, RED)

    y0 = y[1]
    b += frame(1, y0, 2, 1, "hit",
               ("the entry", "exists, so the", "cache returns",
                "the same Tile"))
    b += grid(y0, 3, (0, 3))
    b += call(y0, 3, 'tile("~")')
    b += text(FX + 10, y0 + 90, "body does", 10.5, MUTED)
    b += text(FX + 10, y0 + 106, "not run", 10.5, MUTED)
    b += tile_box(y0, 0) + link(y0, 0)
    b += tile_box(y0, 1, INK) + link(y0, 1, RED)
    b += text(RX + RW / 2, y0 + ROW_Y[1] + RH + 14, "the object from step 1",
              10, RED, "middle")

    y0 = y[2]
    b += frame(2, y0, 3, None, "context",
               ("the grid holds", "the position;", "the Tile holds",
                "the rest"))
    b += grid(y0, 24, (1, 5))
    for k in range(3):
        b += tile_box(y0, k, RED if k == 2 else BOX) + link(y0, k)
    cy = y0 + GY + CELL * 1.5
    turn_y = y0 + 156
    end_x = RX + 40
    side = GX + 6 * CELL + 16
    b += line((GX + 6 * CELL, cy), (side, cy), RED, 1.6)
    b += line((side, cy), (side, turn_y), RED, 1.6)
    b += line((side, turn_y), (end_x, turn_y), RED, 1.6)
    b += arrow((end_x, turn_y), (end_x, y0 + ROW_Y[2] + RH), RED, "fs-red",
               width=1.6)
    b += text(side + 10, turn_y - 6, "field[1][5].walkable", 10.5, RED)
    b += text(GX, turn_y + 20, "extrinsic: row 1, column 5", 10, MUTED)
    b += text(W - 20, turn_y + 20, "intrinsic: symbol, name, walkable", 10,
              MUTED, "end")

    y0 = y[3]
    b += frame(3, y0, 3, None, "bypass",
               ("a direct Tile()", "call skips the", "cache and builds",
                "a second object"))
    b += grid(y0, 24, None)
    for k in range(3):
        b += tile_box(y0, k) + link(y0, k)
    b += tile_box(y0, 3, RED)
    code = 'bypassed = Tile("~", "water", False)'
    cy = row_mid(y0, 3)
    b += text(GX, cy + 4, code, 10, INK)
    b += text(GX, cy + 24, 'assert bypassed == tile("~")', 10, INK)
    b += text(GX, cy + 39, 'assert bypassed is not tile("~")', 10, RED)
    b += arrow((GX + len(code) * 6 + 10, cy), (RX, cy), RED, "fs-red",
               width=1.6)

    defs = markers(**{"fs-red": ("filled", RED),
                      "fs-muted": ("filled", MUTED)})
    return svg(W, 10 + sum(FH), TITLE, defs, b)
