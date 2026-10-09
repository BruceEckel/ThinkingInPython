# grid_observer.py
from enum import StrEnum
from broadcaster import Broadcaster

class Color(StrEnum):
    SKYBLUE = "skyblue"
    PALEGREEN = "palegreen"
    KHAKI = "khaki"

    @classmethod
    def at(cls, n: int) -> Color:
        members = list(cls)
        return members[n % len(members)]

    def next(self) -> Color:
        return Color.at(list(Color).index(self) + 1)

type Coord = tuple[int, int]  # (column, row)
type Grid = dict[Coord, Color]

def new_grid(size: int) -> Grid:
    return {(x, y): Color.at(x + y)
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class GridModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)
