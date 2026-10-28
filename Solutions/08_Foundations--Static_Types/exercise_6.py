# exercise_6.py
from typing import Literal

type Coord = tuple[int, int]
type Color = Literal[
    "red", "blue", "green", "yellow", "purple"]
type Grid = dict[Coord, Color]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "purple")
print(grid)
#: {(2, 3): 'purple'}
