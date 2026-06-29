# rats_and_mazes/test_rats_and_mazes.py
import asyncio
from blackboard import Blackboard
from maze import Coord, Maze

LAYOUT = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""

def flood(maze: Maze, start: Coord) -> set[Coord]:
    seen: set[Coord] = set()
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
