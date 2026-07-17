# box_observer.py
from typing import Final
from observers import Observable

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, str]  # Cell -> color

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

def recolored(grid: Grid, clicked: Coord) -> Grid:
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked) else current
            for cell, current in grid.items()}

class BoxModel(Observable):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.notify(self.grid)
