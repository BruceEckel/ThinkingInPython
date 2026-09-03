# rats_and_mazes/ring_contention.py
import asyncio
from typing import override
from blackboard import Blackboard
from maze import Maze

RING = """\
*****
*   *
* * *
*   *
*****
"""

class CountingBlackboard(Blackboard):
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.taken = 0

    @override
    def claim(self, x: int, y: int) -> bool:
        won = super().claim(x, y)
        if not won and self.maze.is_open(x, y):
            self.taken += 1
        return won

async def main() -> None:
    maze = Maze.from_text(RING)
    blackboard = CountingBlackboard(maze)
    await blackboard.explore()
    for message in blackboard.messages:
        print(message)
    backtracks = len(blackboard.visited) - 1
    print(f"{blackboard.taken} rejections, "
          f"{backtracks} from backtracking alone.")

asyncio.run(main())
#: Rat 1 starts at (1, 1).
#: Rat 2 starts at (2, 1).
#: Rat 1 dead-ends at (2, 3).
#: Rat 2 dead-ends at (3, 3).
#: 9 rejections, 7 from backtracking alone.
