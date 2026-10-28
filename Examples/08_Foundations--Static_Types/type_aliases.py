# type_aliases.py
from typing import Literal

type Coord = tuple[int, int]
type Color = Literal["red", "blue", "green", "yellow"]
type Grid = dict[Coord, Color]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "red")
print(grid)
#: {(2, 3): 'red'}
print(type(grid).__name__)
#: dict
