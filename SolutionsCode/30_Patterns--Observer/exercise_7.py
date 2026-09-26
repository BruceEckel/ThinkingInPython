# exercise_7.py
from enum import StrEnum

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    def next(self) -> Color:
        colors = list(Color)
        nxt = colors.index(self) + 1
        return colors[nxt % len(colors)]

type Coord = tuple[int, int]
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    return grid | {cell: color.next()
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
