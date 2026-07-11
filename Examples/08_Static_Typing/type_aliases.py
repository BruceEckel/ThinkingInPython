# type_aliases.py
from typing import Literal

type Coord = tuple[int, int]
type Grid = dict[Coord, str]
type Color = Literal["red", "blue", "green", "yellow"]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "red")
print(grid)
#: {(2, 3): 'red'}
