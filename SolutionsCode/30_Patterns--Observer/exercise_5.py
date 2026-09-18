# exercise_5.py
from typing import Final, Literal

type Color = Literal["skyblue", "palegreen", "khaki"]
COLORS: Final[tuple[Color, Color, Color]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def next_color(color: Color) -> Color:
    nxt = COLORS.index(color) + 1
    return COLORS[nxt % len(COLORS)]

def recolored(grid: Grid, clicked: Coord) -> Grid:
    x, y = clicked
    return grid | {cell: next_color(color)
                   for cell, color in grid.items()
                   if cell[0] == x or cell[1] == y}

def initials(grid: Grid, size: int) -> str:
    return "\n".join(
        " ".join(grid[(x, y)][0] for x in range(size))
        for y in range(size))

grid = new_grid(4)
print(initials(grid, 4))
#: s p k s
#: p k s p
#: k s p k
#: s p k s
print(initials(recolored(grid, (1, 2)), 4))
#: s k k s
#: p s s p
#: s p k s
#: s k k s
