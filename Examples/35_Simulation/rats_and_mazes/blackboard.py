# rats_and_mazes/blackboard.py
import asyncio
import itertools
from maze import Coord, Maze
from rat import Rat

class Blackboard:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: set[Coord] = set()
        self.tasks: list[asyncio.Task[None]] = []
        self.messages: list[str] = []
        self._numbers = itertools.count(1)

    def claim(self, x: int, y: int) -> bool:
        # No await between the test and the add, so this is atomic
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(asyncio.create_task(rat.run()))

    def next_number(self) -> int:
        return next(self._numbers)

    def log(self, message: str) -> None:
        self.messages.append(message)

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        self.spawn(*start)
        # Wait for every rat, including ones spawned while we wait
        while pending := [t for t in self.tasks if not t.done()]:
            await asyncio.gather(*pending)

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
