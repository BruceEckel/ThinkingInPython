# exercise_3.py
import asyncio

class StubMaze:  # Every cell reads as open, for this demo
    def is_open(self, x: int, y: int) -> bool:
        return True

class BrokenBlackboard:
    def __init__(self) -> None:
        self.maze = StubMaze()
        self.visited: set[tuple[int, int]] = set()

    async def claim(self, x: int, y: int) -> bool:
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            await asyncio.sleep(0)  # The gap: another task can run
            self.visited.add((x, y))
            return True
        return False

async def main() -> None:
    board = BrokenBlackboard()
    results = await asyncio.gather(
        board.claim(2, 2), board.claim(2, 2))
    print("both claims succeeded:", results)
    print("visited set size:", len(board.visited))

asyncio.run(main())
#: both claims succeeded: [True, True]
#: visited set size: 1
