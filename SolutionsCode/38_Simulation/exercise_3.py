# exercise_3.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

LAYOUT: Final[str] = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [
            r.ljust(self.width, self.Cell.WALL)
            for r in rows]

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

class Recorder(Protocol):
    async def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...

@dataclass
class Rat:
    blackboard: Recorder
    x: int
    y: int

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if await self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    true_claims: int = field(init=False, default=0)
    group: asyncio.TaskGroup = field(init=False)

    async def claim(self, x: int, y: int) -> bool:
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            # The gap: another rat can run
            await asyncio.sleep(0)
            self.visited.add((x, y))
            self.true_claims += 1
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        self.group.create_task(Rat(self, x, y).run())

    async def explore(self) -> None:
        start = self.maze.entry()
        await self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

async def main() -> None:
    board = Blackboard(Maze.from_text(LAYOUT))
    await board.explore()
    print("claims that returned True:", board.true_claims)
    print("cells visited:", len(board.visited))

asyncio.run(main())
#: claims that returned True: 25
#: cells visited: 24
