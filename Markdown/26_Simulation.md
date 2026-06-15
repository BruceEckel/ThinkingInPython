# Simulation

A simulation models a system as a set of objects that act on their own and
interact through shared state. This chapter works one example from end to end: a
pack of rats mapping a maze. It puts threads, a shared coordination object, and
structural typing together in one small program.

## Rats & Mazes

The problem has three objects.

A *maze* knows its own layout and little else. Given a coordinate, it reports
whether each neighboring cell is a wall or an opening, and it can hand out an
entry point. The maze never decides anything. It only answers questions.

A *blackboard* is the shared surface every rat writes to. The blackboard is a
classic coordination idea: independent agents read from and write to one common
data structure instead of talking to each other directly. Here the blackboard
owns the maze, records which cells have been explored, hands out rat numbers, and
launches new rats. One lock guards every update, so the rats can run at the same
time without corrupting the shared record.

A *rat* explores. Each rat runs on its own thread. From its current cell it looks
at the four neighbors and tries to claim the open ones. Claiming a cell is how a
rat both marks it visited and reserves it, so no two rats ever cover the same
ground. When a rat finds more than one open neighbor, it keeps the first for
itself and spawns a new rat down each of the others. When it can claim nothing,
it has reached a dead end and its thread ends. When the last rat dies, the maze
is fully mapped.

The rat does not import the blackboard. It only needs an object with the right
methods, so a `Protocol` describes what it expects. This is the structural typing
from the [Static Type Checking](04_Static_Type_Checking.md) chapter. The rat
works with anything that can claim a cell, spawn a rat, record a message, and
hand out a number.

```python
# rats_and_mazes/rat.py
# A rat explores the maze on its own thread, spawning a new rat at
# every branch. It talks to a blackboard but never imports one: any
# object with the four methods below will do.
from __future__ import annotations

import threading
from typing import Protocol

# South, north, west, east.
DIRECTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]


class Recorder(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...


class Rat(threading.Thread):
    def __init__(self, blackboard: Recorder, x: int, y: int) -> None:
        super().__init__()
        self.blackboard = blackboard
        self.x = x
        self.y = y
        self.number = blackboard.next_number()
        blackboard.log(f"Rat {self.number} starts at {(x, y)}.")

    def run(self) -> None:
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
```

The maze is a grid of characters. A `*` is a wall and a space is an opening.
Out-of-bounds coordinates count as walls, so the rats stay inside.

```python
# rats_and_mazes/maze.py
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
    def from_text(cls, text: str) -> Maze:
        rows = [line for line in text.splitlines()
                if line and not line.lstrip().startswith("#")]
        return cls(rows)

    @classmethod
    def from_file(cls, filename: str) -> Maze:
        return cls.from_text(
            Path(filename).read_text(encoding="utf-8"))

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.OPEN)

    def entry(self) -> tuple[int, int]:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")
```

The blackboard holds everything the rats share. `claim()` is the heart of the
program. It tests and marks a cell in a single locked step, so a cell is handed
to exactly one rat even when several reach it at once. `explore()` claims the
entry, releases the first rat, then waits for every thread, including the ones
spawned along the way.

```python
# rats_and_mazes/blackboard.py
# The shared surface the rats write to. It owns the maze, records
# visited cells, hands out rat numbers, and launches rats. One lock
# guards every update.
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
```

The maze layout lives in a text file. The loader skips blank lines and the path
comment, so the file is the maze and nothing else.

```text
# rats_and_mazes/amaze.txt
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
```

Running it turns the rats loose and prints what they mapped.

```python
# rats_and_mazes/ratsandmazes.py
# Turn a pack of rats loose on the maze and print what they mapped.
from __future__ import annotations

from blackboard import Blackboard
from maze import Maze


def main() -> None:
    maze = Maze.from_file("amaze.txt")
    blackboard = Blackboard(maze)
    blackboard.explore()
    print("Mapped maze (# wall, . visited):")
    print(blackboard.render())
    print(f"{len(blackboard.threads)} rats mapped "
          f"{len(blackboard.visited)} cells.")


if __name__ == "__main__":
    main()
```

Because claiming is atomic, the rats always cover every cell reachable from the
entry, no matter how the threads interleave. A test pins that down by comparing
the cells the rats visited against a plain flood fill of the same maze.

```python
# rats_and_mazes/test_ratsandmazes.py
from blackboard import Blackboard
from maze import Maze

LAYOUT = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""


def flood(maze: Maze, start: tuple[int, int]) -> set[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not maze.is_open(x, y):
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def test_rats_map_every_reachable_cell() -> None:
    maze = Maze.from_text(LAYOUT)
    blackboard = Blackboard(maze)
    blackboard.explore()
    assert blackboard.visited == flood(maze, maze.entry())
```

The original Java version of this example was written by Jeremy Meyer.

## Other Maze Resources

A discussion of algorithms to create mazes:

<http://www.mazeworks.com/mazegen/mazegen.htm>

A discussion of algorithms for collision detection and steering behavior for
autonomous moving objects:

<http://www.red3d.com/cwr/steer/>
