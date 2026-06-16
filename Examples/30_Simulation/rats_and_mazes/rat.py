# rats_and_mazes/rat.py
# A rat explores the maze as its own task, spawning a new rat at every
# branch. It talks to a blackboard but never imports one: any object
# with the four methods below will do.
from __future__ import annotations

import asyncio
from typing import Protocol

# South, north, west, east.
DIRECTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]


class Recorder(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...


class Rat:
    def __init__(self, blackboard: Recorder, x: int, y: int) -> None:
        self.blackboard = blackboard
        self.x = x
        self.y = y
        self.number = blackboard.next_number()
        blackboard.log(f"Rat {self.number} starts at {(x, y)}.")

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy) for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                self.blackboard.log(
                    f"Rat {self.number} dead-ends "
                    f"at {(self.x, self.y)}.")
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)  # Yield so sibling rats can run.
