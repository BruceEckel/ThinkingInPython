# rats_and_mazes/blackboard.py
import asyncio
import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field
from maze import Coord, Maze
from rat import Rat

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False, default_factory=set)
    tasks: list[asyncio.Task[None]] = field(
        init=False, default_factory=list)
    messages: list[str] = field(init=False, default_factory=list)
    _numbers: Iterator[int] = field(
        init=False, default_factory=lambda: itertools.count(1))
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        # No await between the test and the add, so this is atomic
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(self.group.create_task(rat.run()))

    def next_number(self) -> int:
        return next(self._numbers)

    def log(self, message: str) -> None:
        self.messages.append(message)

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

    def render(self) -> str:
        lines = []
        for y in range(self.maze.height):
            row = []
            for x in range(self.maze.width):
                if not self.maze.is_open(x, y):
                    row.append("#")
                elif (x, y) in self.visited:
                    row.append(".")
                else:
                    row.append(" ")
            lines.append("".join(row))
        return "\n".join(lines)
