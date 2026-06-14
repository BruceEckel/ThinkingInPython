# ratsAndMazes/maze.py
# Reads a maze layout and reports walls, openings, and an entry point.
from __future__ import annotations
from pathlib import Path


class Maze:
    WALL = "*"
    OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [r.ljust(self.width, self.WALL) for r in rows]

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        rows = [line for line in text.splitlines()
                if line and not line.lstrip().startswith("#")]
        return cls(rows)

    @classmethod
    def from_file(cls, filename: str) -> "Maze":
        return cls.from_text(Path(filename).read_text(encoding="utf-8"))

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.OPEN)

    def entry(self) -> tuple[int, int]:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")
