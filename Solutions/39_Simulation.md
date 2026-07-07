# Simulation: Solutions

## 1. Testing a `Rat` with a fake blackboard

```python
# exercise_1.py
import asyncio
from dataclasses import dataclass, field
from typing import Final, Protocol

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

class Recorder(Protocol):
    def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...
    def log(self, message: str) -> None: ...
    def next_number(self) -> int: ...

@dataclass
class Rat:
    blackboard: Recorder
    x: int
    y: int
    number: int = field(init=False)

    def __post_init__(self) -> None:
        self.number = self.blackboard.next_number()
        self.blackboard.log(
            f"Rat {self.number} starts at {(self.x, self.y)}.")

    async def run(self) -> None:
        while True:
            neighbors = [(self.x + dx, self.y + dy)
                         for dx, dy in DIRECTIONS]
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
            await asyncio.sleep(0)  # Sibling rats can run

class FakeBlackboard:
    def __init__(self, claim_results: list[bool]) -> None:
        self.claim_results = iter(claim_results)
        self.spawned: list[tuple[int, int]] = []
        self.messages: list[str] = []

    def claim(self, x: int, y: int) -> bool:
        return next(self.claim_results, False)

    def spawn(self, x: int, y: int) -> None:
        self.spawned.append((x, y))

    def log(self, message: str) -> None:
        self.messages.append(message)

    def next_number(self) -> int:
        return 1

# DIRECTIONS checks (0,1), (0,-1), (-1,0), (1,0) in that order.
# Script the 2nd and 4th as open, the 1st and 3rd as walls/visited:
fake = FakeBlackboard([False, True, False, True])
rat = Rat(fake, 0, 0)
asyncio.run(rat.run())
print(rat.x, rat.y)     # Kept the first successful claim
#: 0 -1
print(fake.spawned)     # Spawned down every claim after that
#: [(1, 0)]
```

`Rat` never imports `Blackboard`, only the `Recorder` `Protocol`, so
`FakeBlackboard` satisfies it purely by shape: it has `claim()`,
`spawn()`, `log()`, and `next_number()`, with none of them touching a
real `Maze` or `asyncio.create_task()`. Scripting `claim()`'s return
values in a fixed sequence pins down exactly which neighbor the rat
keeps for itself (the first the loop finds open, `(0, -1)`) and which
neighbors it spawns down (every open one after that, here just
`(1, 0)`), with no randomness and no real maze needed.

## 2. Reporting unreached cells

```python
# exercise_2.py
import asyncio
import itertools
from enum import StrEnum
from typing import Self

type Coord = tuple[int, int]

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
        rows = [line for line in text.splitlines() if line]
        return cls(rows)

    def is_open(self, x: int, y: int) -> bool:
        return (0 <= y < self.height and 0 <= x < self.width
                and self.rows[y][x] == self.Cell.OPEN)

    def entry(self) -> Coord:
        for y in range(self.height):
            for x in range(self.width):
                if self.is_open(x, y):
                    return x, y
        raise ValueError("the maze has no open cell")

class Rat:
    def __init__(self, blackboard: Blackboard, x: int,
                 y: int) -> None:
        self.blackboard = blackboard
        self.x, self.y = x, y

    async def run(self) -> None:
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        while True:
            neighbors = [(self.x + dx, self.y + dy)
                         for dx, dy in directions]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

class Blackboard:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited: set[Coord] = set()
        self.tasks: list[asyncio.Task[None]] = []
        self._numbers = itertools.count(1)

    def claim(self, x: int, y: int) -> bool:
        if self.maze.is_open(x, y) and (x, y) not in self.visited:
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(asyncio.create_task(rat.run()))

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        self.spawn(*start)
        while pending := [t for t in self.tasks if not t.done()]:
            await asyncio.gather(*pending)

layout_with_a_moat = """
*********
*   *   *
*   *   *
*   *   *
*********
"""

async def main() -> None:
    maze = Maze.from_text(layout_with_a_moat)
    board = Blackboard(maze)
    await board.explore()
    all_open = {(x, y) for y in range(maze.height)
                for x in range(maze.width) if maze.is_open(x, y)}
    unreached = all_open - board.visited
    print(len(unreached), min(unreached), max(unreached))

asyncio.run(main())
#: 9 (5, 1) (7, 3)
```

For a maze built with two separate rooms and no connecting opening
between them:

```
*********
*   *   *
*   *   *
*   *   *
*********
```

the rats, starting in the left room, map every cell of that room and
none of the right room's, so `unreached` is exactly the right room's
nine open cells. What makes a cell unreachable is not being walled
off in the abstract but having no path of open cells connecting it to
the entry; `Maze.entry()` finds the first open cell scanning row by
row, and every rat traces back to that single starting point through
`claim()`, so a cell with no open-cell path back to the entry can
never be claimed no matter how many rats spawn.

## 3. Breaking `claim()`'s atomicity

```python
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
```

Both calls reach `await asyncio.sleep(0)` while `(2, 2)` still looks
unclaimed to each of them; neither has added it to `visited` yet, so
both membership tests pass. Only after both have already committed to
succeeding does either one actually call `self.visited.add((2, 2))`.
The result is two rats that each believe they alone claimed the same
cell: both move into it, which breaks the invariant that "no two rats
ever cover the same ground" and, when run inside `test_rats_and_mazes.py`'s
full maze, can leave some other reachable cell unclaimed entirely,
since one of the two rats that collided on `(2, 2)` would otherwise
have gone on to claim a different cell instead.

The original `claim()` needs no lock precisely because it has no
`await` between the test and the add. A coroutine only ever yields
control at an `await`, so with nothing to await in between, the two
statements execute as one uninterruptible unit as far as any other
coroutine is concerned; nothing else can run "in the middle" of them,
because there is no scheduling point in the middle. Adding the
`await` creates exactly that scheduling point, and the whole guarantee
depends on there being none.

Exercises 4 and 5 both build on the same `robot_explorer` world,
so that shared apparatus (`Item` and its subclasses, `Room`, `Doors`,
`GameBuilder`) lives once in `robot_world.py`, and each exercise
imports it:

```python
# robot_world.py
from enum import Enum, auto
from typing import ClassVar, Final, override

class Urge(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()

class Item:
    symbol: ClassVar[str] = ""

    def interact(self, robot: Robot, room: Room) -> Room:
        return room  # Default: the robot enters the room

    def __str__(self) -> str:
        return self.symbol

class Robot(Item):
    symbol = "R"
    room: Room  # Set by the builder when the robot is placed

    def __init__(self) -> None:
        self.finished = False
        self.coins = 0  # Exercise 4: a place to count Coin pickups

    def move(self, urge: Urge) -> None:
        self.room = self.room.doors.open(urge).enter(self)

class Wall(Item):
    symbol = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return robot.room  # Cannot pass: stay put

class Food(Item):
    symbol = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten
        return room

class Teleport(Item):
    symbol = ""  # Set per target letter
    target_room: Room  # Paired up by the builder

    def __init__(self, target: str) -> None:
        self.target = target

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return self.target_room

    @override
    def __str__(self) -> str:
        return self.target

class Empty(Item):
    symbol = "_"

class Edge(Item):
    symbol = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return robot.room  # The void outside the maze: stay put

class EndGame(Item):
    symbol = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        robot.finished = True
        return room

def item_factory(symbol: str) -> Item:
    for item_type in Item.__subclasses__():
        if symbol == item_type.symbol:
            return item_type()
    return Teleport(symbol)  # Anything else is a teleport target

type Coord = tuple[int, int]
type RoomMap = dict[Coord, Room]

class Room:
    def __init__(self, occupant: Item) -> None:
        self.occupant = occupant
        self.doors = Doors()

    def enter(self, robot: Robot) -> Room:
        return self.occupant.interact(robot, self)

    def __repr__(self) -> str:
        return f"Room({self.occupant})"

class Doors:
    def __init__(self) -> None:
        self.neighbors: dict[Urge, Room] = {}

    def connect(self, row: int, col: int,
                rooms: RoomMap) -> None:
        for urge, coord in {
            Urge.NORTH: (row - 1, col),
            Urge.SOUTH: (row + 1, col),
            Urge.EAST: (row, col + 1),
            Urge.WEST: (row, col - 1),
        }.items():
            if coord in rooms:
                self.neighbors[urge] = rooms[coord]

    def open(self, urge: Urge) -> Room:
        return self.neighbors.get(urge, EDGE)

EDGE: Final[Room] = Room(Edge())

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[Room] = []
        for row, line in enumerate(maze.splitlines()):
            for col, char in enumerate(line):
                occupant = item_factory(char)
                if isinstance(occupant, Robot):
                    room = Room(Empty())
                    self.robot = occupant
                    self.robot.room = room
                else:
                    room = Room(occupant)
                self.rooms[row, col] = room
                if isinstance(occupant, Teleport):
                    teleports.append(room)
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)

        def target(room: Room) -> str:
            assert isinstance(room.occupant, Teleport)
            return room.occupant.target

        teleports.sort(key=target)
        pairs = iter(teleports)
        for room1, room2 in zip(pairs, pairs):
            assert isinstance(room1.occupant, Teleport)
            assert isinstance(room2.occupant, Teleport)
            room1.occupant.target_room = room2
            room2.occupant.target_room = room1

    def run(self, solution: str) -> None:
        moves = {"n": Urge.NORTH, "s": Urge.SOUTH,
                 "e": Urge.EAST, "w": Urge.WEST}
        for char in "".join(solution.split()):
            self.robot.move(moves[char])
```

## 4. A `Coin` item

```python
# exercise_4.py
from typing import override
from robot_world import Empty, GameBuilder, Item, Robot, Room

class Coin(Item):
    symbol = "$"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Collected, like Food
        robot.coins += 1
        return room

game = GameBuilder("#####\nR$$.#\n#####")
game.run("ee")
print(game.robot.coins)
#: 2
```

`Robot.__init__()` needs only one new line, `self.coins = 0`, to have
somewhere to count (folded into `robot_world.py` above so this
exercise's file stays a single, runnable unit). `item_factory()` needs
no change at all. It already searches `Item.__subclasses__()` for a
class whose `symbol` matches the character it was given, so the moment
`Coin` is defined anywhere the module has imported, it is automatically
one of the classes the factory searches. `Room` and `GameBuilder` need
no change either, since both only ever call
`occupant.interact(robot, room)` through the shared `Item` interface;
neither one has ever needed to know which concrete `Item` subclasses
exist.

## 5. Solving the maze instead of hard-coding the solution

```python
# exercise_5.py
from collections import deque
from robot_world import (
    Edge,
    EndGame,
    GameBuilder,
    Room,
    Teleport,
    Urge,
    Wall,
)

def landing(room: Room, urge: Urge) -> Room | None:
    "Where this door actually leads, or None if it's blocked."
    next_room = room.doors.open(urge)
    if isinstance(next_room.occupant, (Wall, Edge)):
        return None
    if isinstance(next_room.occupant, Teleport):
        return next_room.occupant.target_room
    return next_room

def solve(builder: GameBuilder) -> str:
    start = builder.robot.room
    move_chars = {Urge.NORTH: "n", Urge.SOUTH: "s",
                  Urge.EAST: "e", Urge.WEST: "w"}
    queue: deque[tuple[Room, str]] = deque([(start, "")])
    seen = {id(start)}
    while queue:
        room, path = queue.popleft()
        if isinstance(room.occupant, EndGame):
            return path
        for urge, char in move_chars.items():
            dest = landing(room, urge)
            if dest is not None and id(dest) not in seen:
                seen.add(id(dest))
                queue.append((dest, path + char))
    raise ValueError("no path to EndGame found")

string_maze = """
###############################
#R#.____#____.#_______#_______#
#_###_#_###_#_#_#_#####_#####_#
#___#_#___#_#_#_#.#__b__#___#_#
###_#_###_#_#_###_#_#####_#_#_#
#.#_#_#.__#_#__.#_#__b__#_#___#
#_#_#_#_###_###_#_#####_#_#####
#_#_#_#__.#_#_#_____#___#_____#
#_#_#_###_#_#_#_#####_#######_#
#.#___#___#_#___#____.#_____#_#
#_#####_###_#_###_#####_#_###_#
#___#a__#.__#.__#__.#___#_#___#
#_#_#_###_#####_###_###_###_#_#
#_#.#_#___#!______#_____#___#_#
#_#_#_###_#############_#_###_#
#_#_#__a#_______________#___#_#
#_#####_###_###########_###_#_#
#_____#.__#_#___#_____#_#___#_#
#_#_#####_###_#_#_###_###_###_#
#.#___________#___#____.__#___#
###############################
""".strip()

game = GameBuilder(string_maze)
solution = solve(game)
game.run(solution)
assert isinstance(game.robot.room.occupant, EndGame)
print("reached EndGame in", len(solution), "moves")
#: reached EndGame in 198 moves
```

`solve()` is a breadth-first search over `Room` objects, following
exactly the same `doors.open(urge)` calls `Robot.move()` uses, so it
never has to know anything about coordinates, only rooms and the
moves that connect them. It refuses to step through a `Wall` or off
the `Edge`, and it stops the moment it reaches a room occupied by
`EndGame`, returning the sequence of move letters that got there, the
shortest one first since a breadth-first search always finds the
shortest path in an unweighted graph. That returned string is exactly
what `run()` already expects, the same as the previously hard-coded
`solution`, so `game.run(solution)` and the assertion that follows are
unchanged from `test_robot.py`. Unlike the pre-computed `solution`
string, this one adapts automatically if the maze layout changes.
