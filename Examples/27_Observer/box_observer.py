# box_observer.py
# The model for the ColorBoxes example: a grid of colors and the rule
# for a click, wired as a classic Observable. No display code lives
# here, so the model runs and is tested with no window open. The view
# is box_view.py.
from observer import Observable

COLORS = ("skyblue", "palegreen", "khaki")
type Grid = dict[tuple[int, int], str]   # (column, row) -> color

def new_grid(size: int) -> Grid:
    "Build a size x size grid, banded into three colors."
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    "True if two distinct cells touch, including diagonally."
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

def recolored(grid: Grid, clicked: tuple[int, int]) -> Grid:
    "Return a new grid: every neighbor of the click takes its color."
    color = grid[clicked]
    return {cell: color if adjacent(cell, clicked) else current
            for cell, current in grid.items()}

class BoxModel(Observable):
    "The subject: holds the grid and announces every change."
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def click(self, cell: tuple[int, int]) -> None:
        self.grid = recolored(self.grid, cell)
        self.set_changed()
        self.notify_observers(self.grid)
