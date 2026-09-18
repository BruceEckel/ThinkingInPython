# box_observer.py
from typing import Final, Literal
from observers import Observable

type Color = Literal["skyblue", "palegreen", "khaki"]
COLORS: Final[tuple[Color, Color, Color]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, clicked: Coord) -> Grid:
    nxt = COLORS.index(grid[clicked]) + 1
    return grid | {clicked: COLORS[nxt % len(COLORS)]}

class BoxModel(Observable[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.notify(self.grid)
