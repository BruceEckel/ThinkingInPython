# exercise_3.py
from typing import Final

COLORS: Final[tuple[str, str, str]] = (
    "skyblue", "palegreen", "khaki")
type Coord = tuple[int, int]
type Grid = dict[Coord, str]

def new_grid(size: int) -> Grid:
    return {(x, y): COLORS[(x + y) % len(COLORS)]
            for x in range(size) for y in range(size)}

def adjacent(a: Coord, b: Coord) -> bool:
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1

class FloodGame:
    "Flood-fill game: grow a patch from the origin to fill the board."
    def __init__(self, size: int, origin: Coord = (0, 0)) -> None:
        self.size = size
        self.grid = new_grid(size)
        self.origin = origin
        self.clicks = 0
        self.owned = self._flood(self.grid[origin])

    def _flood(self, color: str) -> set[Coord]:
        "Every cell reachable from origin through same-colored cells."
        seen: set[Coord] = set()
        stack = [self.origin]
        while stack:
            cell = stack.pop()
            if cell in seen or self.grid.get(cell) != color:
                continue
            seen.add(cell)
            for other in self.grid:
                if adjacent(cell, other) and other not in seen:
                    stack.append(other)
        return seen

    def click(self, cell: Coord) -> bool:
        "Recolor the owned patch to the clicked cell's color."
        new_color = self.grid[cell]
        if new_color == self.grid[self.origin]:
            return False  # No-op: already this color
        for c in self.owned:
            self.grid[c] = new_color
        self.owned = self._flood(new_color)  # Absorb new neighbors
        self.clicks += 1
        return True

    def is_complete(self) -> bool:
        return len(self.owned) == self.size * self.size

game = FloodGame(4)
while not game.is_complete():
    remaining = [c for c in game.grid if c not in game.owned]
    game.click(remaining[0])
print("solved in", game.clicks, "clicks")
#: solved in 6 clicks
