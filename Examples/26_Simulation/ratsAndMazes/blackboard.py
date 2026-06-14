# ratsAndMazes/blackboard.py
# The shared surface the rats write to. It owns the maze, records visited
# cells, hands out rat numbers, and launches rats. One lock guards every update.
from __future__ import annotations
import itertools
import threading

from maze import Maze
from rat import Rat


class Blackboard:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: set[tuple[int, int]] = set()
        self.threads: list[Rat] = []
        self.messages: list[str] = []
        self.lock = threading.Lock()
        self._numbers = itertools.count(1)

    def claim(self, x: int, y: int) -> bool:
        with self.lock:
            if self.maze.is_open(x, y) and (x, y) not in self.visited:
                self.visited.add((x, y))
                return True
            return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        with self.lock:
            self.threads.append(rat)
        rat.start()

    def next_number(self) -> int:
        with self.lock:
            return next(self._numbers)

    def log(self, message: str) -> None:
        with self.lock:
            self.messages.append(message)

    def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        self.spawn(*start)
        self._wait_all()

    def _wait_all(self) -> None:
        i = 0
        while True:
            with self.lock:
                threads = list(self.threads)
            if i >= len(threads):
                return
            threads[i].join()
            i += 1

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
