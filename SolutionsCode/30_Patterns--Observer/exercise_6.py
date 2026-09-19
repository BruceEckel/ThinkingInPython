# exercise_6.py
from collections import Counter
from collections.abc import Callable
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
type Listener[T] = Callable[[T], None]

def new_grid(size: int) -> Grid:
    colors = list(Color)
    return {(x, y): colors[(x + y) % len(colors)]
            for x in range(size) for y in range(size)}

def recolored(grid: Grid, selected: Coord) -> Grid:
    x, y = selected
    cross = [(x, y), (x - 1, y), (x + 1, y),
             (x, y - 1), (x, y + 1)]
    return grid | {cell: grid[cell].next()
                   for cell in cross if cell in grid}

class Broadcaster[T]:
    def __init__(self) -> None:
        self._listeners: list[Listener[T]] = []

    def subscribe(self, listener: Listener[T]) -> None:
        self._listeners.append(listener)

    def announce(self, data: T) -> None:
        for listener in list(self._listeners):
            listener(data)

class BoxModel(Broadcaster[Grid]):
    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size
        self.grid = new_grid(size)

    def select(self, cell: Coord) -> None:
        self.grid = recolored(self.grid, cell)
        self.announce(self.grid)

model = BoxModel(3)

def letters(grid: Grid) -> None:
    for y in range(model.size):
        print(" ".join(grid[(x, y)][0]
                       for x in range(model.size)))

def tally(grid: Grid) -> None:
    counts = Counter(grid.values())
    print(" ".join(f"{c[0]}:{counts[c]}" for c in Color))

model.subscribe(letters)
model.subscribe(tally)
model.select((1, 1))
#: s k k
#: k s p
#: k p p
#: s:2 p:3 k:4
model.select((0, 0))
#: p s k
#: s s p
#: k p p
#: s:3 p:4 k:2
