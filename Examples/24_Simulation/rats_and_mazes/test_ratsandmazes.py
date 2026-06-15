# rats_and_mazes/test_ratsandmazes.py
import asyncio

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
    asyncio.run(blackboard.explore())
    assert blackboard.visited == flood(maze, maze.entry())
