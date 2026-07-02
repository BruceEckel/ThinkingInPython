# rats_and_mazes/maze.py
from enum import StrEnum
from pathlib import Path
from typing import Self

type Coord = tuple[int, int]   # (column, row)

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
        rows = [line for line in text.splitlines()
                if line and not line.lstrip().startswith("#")]
        return cls(rows)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        return cls.from_text(
            Path(filename).read_text(encoding="utf-8"))

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")
