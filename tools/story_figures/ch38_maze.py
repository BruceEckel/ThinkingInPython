"""Chapter 38, Simulation: a corner of the robot's maze as a graph of rooms.

The figure sits in "Rooms, Robots, and the Item Factory", between the
paragraph that introduces `EDGE` and the one on `Doors.connect()` and
teleports. It replaced a hand-drawn grid on 2026-09-29 whose teleport
arcs and border-to-`EDGE` arrows showed no real maze and hid the point
the code makes: `GameBuilder` builds a `Room` for every character,
walls included, so a wall is a room whose occupant sends the robot
back, not a gap in the graph.

The left panel is a real piece of `string_maze` in `game.py`, rows 0-5
and columns 19-23, which holds the `b` teleport pair and a stretch of
the top border. The right panel is the graph `GameBuilder` makes of
it, one node per character in the same place: stage 1's rooms, stage
2's doors (`Doors.connect()` links every grid neighbor, walls too, so
a door into a wall room is drawn gray), and stage 3's teleport link
between the two `b` rooms. Row 0 has no neighbor to the north, so
`Doors.open(Urge.NORTH)` returns the shared `EDGE` room there. Stubs
at the other three sides show that the maze continues. `FRAGMENT`
holds rows 0-6 and columns 18-24 of `string_maze` so the stubs can
tell a wall neighbor from an open one; recheck it if the maze changes.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, SHADE, arrow, line,
                                 markers, rect, svg, text)

STEM = "maze_graph"
W, H = 720, 560
# string_maze rows 0-6, columns 18-24; the figure draws rows 0-5 and
# columns 19-23, and uses the outer ring only for the stubs.
FRAGMENT = [
    "#######",
    "____#__",
    "#####_#",
    "#__b__#",
    "#_#####",
    "#__b__#",
    "#####_#",
]
ROW0, COL0 = 0, 18  # Maze coordinates of FRAGMENT[0][0]
ROWS, COLS = range(0, 6), range(19, 24)  # The part the figure draws
S, R = 58, 13  # Node spacing and radius
GX, GY = 352, 138  # Center of the node for room (0, 19)
TX, TY, TS = 70, 226, 24  # Text panel: first character, cell size
STUB = 28
TITLE = ("Rows 0 to 5, columns 19 to 23 of the robot's maze text and the "
         "graph GameBuilder makes of it: a room for every character, "
         "walls included, doors between grid neighbors, a link between "
         "the two b teleports, and every north door on row 0 opening the "
         "shared EDGE room")


def char(row: int, col: int) -> str:
    return FRAGMENT[row - ROW0][col - COL0]


def is_wall(row: int, col: int) -> bool:
    return char(row, col) == "#"


def at(row: int, col: int) -> tuple[float, float]:
    return GX + (col - COLS[0]) * S, GY + (row - ROWS[0]) * S


def door_color(a: tuple[int, int], b: tuple[int, int]) -> tuple[str, float]:
    if is_wall(*a) or is_wall(*b):
        return BOX, 1.1
    return INK, 1.6


def node(row: int, col: int) -> str:
    x, y = at(row, col)
    c = char(row, col)
    if c == "#":
        body = (f'  <circle cx="{x:g}" cy="{y:g}" r="{R}" fill="{SHADE}" '
                f'stroke="{BOX}" stroke-width="1.1"/>\n')
        return body + text(x, y + 4, c, 11, MUTED, "middle")
    stroke, width = (RED, 1.8) if c == "b" else (INK, 1.3)
    body = (f'  <circle cx="{x:g}" cy="{y:g}" r="{R}" fill="none" '
            f'stroke="{stroke}" stroke-width="{width:g}"/>\n')
    return body + text(x, y + 4, c, 12, RED if c == "b" else INK,
                       "middle", bold=c == "b")


def doors() -> str:
    b = ""
    for row in ROWS:
        for col in COLS:
            x, y = at(row, col)
            if col + 1 in COLS:
                color, w = door_color((row, col), (row, col + 1))
                b += line((x + R, y), (x + S - R, y), color, w)
            if row + 1 in ROWS:
                color, w = door_color((row, col), (row + 1, col))
                b += line((x, y + R), (x, y + S - R), color, w)
    # Stubs: doors to rooms outside the part drawn
    for row in ROWS:
        x, y = at(row, COLS[0])
        color, w = door_color((row, COLS[0]), (row, COLS[0] - 1))
        b += line((x - R, y), (x - R - STUB, y), color, w)
        x, y = at(row, COLS[-1])
        color, w = door_color((row, COLS[-1]), (row, COLS[-1] + 1))
        b += line((x + R, y), (x + R + STUB, y), color, w)
    for col in COLS:
        x, y = at(ROWS[-1], col)
        color, w = door_color((ROWS[-1], col), (ROWS[-1] + 1, col))
        b += line((x, y + R), (x, y + R + STUB), color, w)
    return b


def teleport() -> str:
    """The stage 3 link between the two b rooms, bowed past the wall."""
    (x, y1), (_, y2) = at(3, 21), at(5, 21)
    d = R * 0.7
    return (f'  <path d="M{x + d:g},{y1 + d:g} Q{x + 0.75 * S:g},'
            f'{(y1 + y2) / 2:g} {x + d:g},{y2 - d:g}" fill="none" '
            f'stroke="{RED}" stroke-width="2"/>\n')


def edge_room() -> str:
    left, right = at(0, COLS[0])[0] - 40, at(0, COLS[-1])[0] + 40
    top, h = 36, 44
    b = rect(left, top, right - left, h, stroke=INK, width=1.6)
    b += text((left + right) / 2, top + 19, "EDGE = Room(Edge())", 12.5,
              INK, "middle", bold=True)
    b += text((left + right) / 2, top + 35,
              "Edge.interact() returns robot.room", 10.5, MUTED, "middle")
    for col in COLS:
        x, y = at(0, col)
        b += arrow((x, y - R), (x, top + h), MUTED, "mz-muted")
    b += text(left - 10, top + h + 22, "open(Urge.NORTH)", 10.5, MUTED,
              "end")
    b += text(left - 10, top + h + 36, "on row 0", 10.5, MUTED, "end")
    return b


def maze_text() -> str:
    b = text(TX - 26, TY - 44, "string_maze", 12, INK, bold=True)
    for col in COLS:
        b += text(TX + (col - COLS[0]) * TS, TY - 22, str(col), 10, MUTED,
                  "middle")
    for row in ROWS:
        y = TY + (row - ROWS[0]) * TS
        b += text(TX - 26, y, str(row), 10, MUTED, "middle")
        for col in COLS:
            c = char(row, col)
            b += text(TX + (col - COLS[0]) * TS, y, c, 14,
                      RED if c == "b" else INK, "middle", bold=c == "b")
    b += text(TX - 26, 400, "GameBuilder, in stages:", 11, INK)
    for i, s in enumerate(["1 a Room per character",
                           "2 doors to grid neighbors",
                           "3 pair teleports by letter"]):
        b += text(TX - 26, 420 + 17 * i, s, 10.5, MUTED)
    return b


def legend() -> str:
    y = 518
    lx, rx = 44, 392
    b = (f'  <circle cx="{lx:g}" cy="{y - 4:g}" r="9" fill="{SHADE}" '
         f'stroke="{BOX}" stroke-width="1.1"/>\n')
    b += text(lx, y, "#", 10, MUTED, "middle")
    b += text(lx + 20, y, "Room(Wall()): returns robot.room", 10.5, INK)
    b += line((lx - 10, y + 24), (lx + 10, y + 24), BOX, 1.1)
    b += text(lx + 20, y + 28, "door into a wall room", 10.5, INK)
    b += line((rx - 10, y - 4), (rx + 10, y - 4), INK, 1.6)
    b += text(rx + 20, y, "door between enterable rooms", 10.5, INK)
    b += line((rx - 10, y + 24), (rx + 10, y + 24), RED, 2)
    b += text(rx + 20, y + 28, "Teleport: enter one b, land on the other",
              10.5, INK)
    return b


def render() -> str:
    b = maze_text()
    b += doors() + teleport()
    for row in ROWS:
        for col in COLS:
            b += node(row, col)
    b += edge_room()
    for col in COLS:
        x, _ = at(ROWS[-1], col)
        b += text(x, at(ROWS[-1], col)[1] + R + STUB + 16, str(col), 10,
                  MUTED, "middle")
    for row in ROWS:
        b += text(at(row, COLS[0])[0] - R - STUB - 8, at(row, 0)[1] + 4,
                  str(row), 10, MUTED, "end")
    b += legend()
    return svg(W, H, TITLE, markers(**{"mz-muted": ("filled", MUTED)}), b)
