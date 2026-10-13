# rats_and_mazes/ring_contention.py
import asyncio
from typing import Final, override
from blackboard import Blackboard
from maze import Maze

RING: Final[str] = """\
*****
*   *
* * *
*   *
*****
"""

class CountingBlackboard(Blackboard):
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.rejections = 0

    @override
    def claim(self, x: int, y: int) -> bool:
        won = super().claim(x, y)
        if not won and self.maze.is_open(x, y):
            self.rejections += 1
        return won

async def main() -> None:
    maze = Maze.from_text(RING)
    blackboard = CountingBlackboard(maze)
    await blackboard.explore()
    for message in blackboard.messages:
        print(message)
    backtracks = len(blackboard.visited) - 1
    contested = blackboard.rejections - backtracks
    print(f"{blackboard.rejections} rejections: "
          f"{backtracks} backtracking, "
          f"{contested} contested.")

asyncio.run(main())
#: Rat 1 ran (1, 1) to (2, 3).
#: Rat 2 ran (2, 1) to (3, 3).
#: 9 rejections: 7 backtracking, 2 contested.
