# exercise_2.py
import asyncio
import itertools
from enum import StrEnum
from typing import Self

type Coord = tuple[int, int]

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [
            r.ljust(self.width, self.Cell.WALL) for r in rows]

    @classmethod
    def from_text(cls, text: str) -> Self:
        rows = [line for line in text.splitlines() if line]
        return cls(rows)

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")

class Rat:
    def __init__(self, blackboard: Blackboard, x: int,
                 y: int) -> None:
        self.blackboard = blackboard
        self.x, self.y = x, y

    async def run(self) -> None:
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        while True:
            neighbors = [(self.x + dx, self.y + dy)
                         for dx, dy in directions]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

class Blackboard:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: set[Coord] = set()
        self.tasks: list[asyncio.Task[None]] = []
        self._numbers = itertools.count(1)

    def claim(self, x: int, y: int) -> bool:
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(asyncio.create_task(rat.run()))

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        self.spawn(*start)
        while pending := [t for t in self.tasks if not t.done()]:
            await asyncio.gather(*pending)

layout_with_a_moat = """
*********
*   *   *
*   *   *
*   *   *
*********
"""

async def main() -> None:
    maze = Maze.from_text(layout_with_a_moat)
    board = Blackboard(maze)
    await board.explore()
    all_open = {(x, y) for y in range(maze.height)
                for x in range(maze.width) if maze.is_open(x, y)}
    unreached = all_open - board.visited
    print(len(unreached), min(unreached), max(unreached))

asyncio.run(main())
#: 9 (5, 1) (7, 3)
