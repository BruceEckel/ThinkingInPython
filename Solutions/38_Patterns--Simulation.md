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
            f"Rat {self.number} starts at "
            f"{(self.x, self.y)}.")

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

# DIRECTIONS checks (0,1), (0,-1), (-1,0), (1,0) in that
# order. Script the 2nd and 4th as open, the 1st and 3rd
# as walls/visited:
fake = FakeBlackboard([False, True, False, True])
rat = Rat(fake, 0, 0)
asyncio.run(rat.run())
print(rat.x, rat.y)     # Kept the first successful claim
#: 0 -1
# Spawned down every claim after that
print(fake.spawned)
#: [(1, 0)]
```

`Rat` never imports `Blackboard`, only the `Recorder` `Protocol`, so
`FakeBlackboard` satisfies that `Protocol` purely by shape: it defines
`claim()`, `spawn()`, `log()`, and `next_number()`, and none of the
four touches a real `Maze` or `asyncio.create_task()`. Scripting
`claim()`'s return values in a fixed sequence pins down exactly which
neighbor the rat keeps for itself and which cells it spawns new rats
into: the first cell the loop finds open, `(0, -1)`, and every open
one after that, here just `(1, 0)`. The test needs no randomness and
no real maze.

## 2. Reporting unreached cells

```python
# exercise_2.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [
            r.ljust(self.width, self.Cell.WALL)
            for r in rows]

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

@dataclass
class Rat:
    blackboard: Blackboard
    x: int
    y: int

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            self.visited.add((x, y))
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        self.group.create_task(Rat(self, x, y).run())

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

two_rooms: Final[str] = """
*********
*   *   *
*   *   *
*   *   *
*********
"""

async def main() -> None:
    maze = Maze.from_text(two_rooms)
    board = Blackboard(maze)
    await board.explore()
    all_open = {(x, y) for y in range(maze.height)
                for x in range(maze.width)
                if maze.is_open(x, y)}
    unreached = all_open - board.visited
    print(len(unreached), min(unreached), max(unreached))

asyncio.run(main())
#: 9 (5, 1) (7, 3)
```

The classes are the chapter's, trimmed of what the exercise does not
need: rat numbers, logging, and the file loader.
The structure that matters survives the trim. `claim()` keeps the
chapter's body word for word, and `explore()` still opens a
`TaskGroup` and lets `spawn()` add tasks to that group, because new
rats keep arriving after the block begins.

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
none of the right room's, so `unreached` is the right room's nine open
cells. A cell is unreachable when no path of open cells connects it to
the entry, not when a wall happens to surround it. `Maze.entry()`
scans row by row and returns the first open cell it finds, and every
rat traces back to that single starting point through `claim()`. No
rat can therefore reach a cell that has no open-cell path back to the
entry, however many rats spawn.

## 3. Breaking `claim()`'s atomicity

```python
# exercise_3.py
import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol, Self

type Coord = tuple[int, int]

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (0, 1), (0, -1), (-1, 0), (1, 0)]

LAYOUT: Final[str] = """\
*********
*       *
*** *** *
*   *   *
* ***** *
*       *
*********
"""

class Maze:
    class Cell(StrEnum):
        WALL = "*"
        OPEN = " "

    def __init__(self, rows: list[str]) -> None:
        self.height = len(rows)
        self.width = max((len(r) for r in rows), default=0)
        self.rows = [
            r.ljust(self.width, self.Cell.WALL)
            for r in rows]

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

class Recorder(Protocol):
    async def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...

@dataclass
class Rat:
    blackboard: Recorder
    x: int
    y: int

    async def run(self) -> None:
        while True:
            neighbors = [
                (self.x + dx, self.y + dy)
                for dx, dy in DIRECTIONS]
            moves = [pos for pos in neighbors
                     if await self.blackboard.claim(*pos)]
            if not moves:
                return
            for branch in moves[1:]:
                self.blackboard.spawn(*branch)
            self.x, self.y = moves[0]
            await asyncio.sleep(0)

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    true_claims: int = field(init=False, default=0)
    group: asyncio.TaskGroup = field(init=False)

    async def claim(self, x: int, y: int) -> bool:
        if (self.maze.is_open(x, y)
            and (x, y) not in self.visited):
            # The gap: another rat can run
            await asyncio.sleep(0)
            self.visited.add((x, y))
            self.true_claims += 1
            return True
        return False

    def spawn(self, x: int, y: int) -> None:
        self.group.create_task(Rat(self, x, y).run())

    async def explore(self) -> None:
        start = self.maze.entry()
        await self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)

async def main() -> None:
    board = Blackboard(Maze.from_text(LAYOUT))
    await board.explore()
    print("claims that returned True:", board.true_claims)
    print("cells visited:", len(board.visited))

asyncio.run(main())
#: claims that returned True: 25
#: cells visited: 24
```

The one requested change drags three more edits with it, and that
spread is the exercise's quiet lesson: `async` is contagious.
Once `claim()` is an `async def`, the `Recorder` protocol must declare
it `async` too, `Rat.run()`'s comprehension needs
`if await self.blackboard.claim(*pos)`, and `explore()` must `await`
its own first claim.
`spawn()` stays synchronous, because nothing in it suspends.

On the chapter's seven-by-nine test maze, `claim()` returns `True` 25
times for 24 open cells: one pair of rats collided.
Both rats reached `await asyncio.sleep(0)` while the same cell still
looked unclaimed, because neither had added that cell to `visited`
yet. Both membership tests therefore passed, and only afterward did
each rat call `self.visited.add(...)`.
The result is two rats that each believe they alone claimed that cell.
Both move into it, and that overlap breaks the invariant that no two
rats cover the same ground. Nothing goes unexplored. Both rats proceed
from the shared cell and duplicate each other's work from there, while
`visited` stays correct, because adding the same cell twice to a set
changes nothing. That correctness is why `test_rats_and_mazes.py`
passes on the broken version every time: the test asserts the set of
cells reached. The extra success costs the rats wasted effort, two
tasks tracing overlapping paths. Comparing the count of `True` returns
with the size of `visited` exposes the collision.

The original `claim()` needs no lock because it has no `await`
between the test and the add. A coroutine yields control only at an
`await`, so the two statements run as one uninterruptible unit: the
event loop can hand control to another rat before the test or after
the add, but never between them. Adding the `await` opens exactly that
gap in the middle, and the whole guarantee depends on its absence.

Exercises 4 and 5 both build on the same `robot_explorer` world,
so `robot_world.py` holds that shared apparatus once (`Item` and its
subclasses, `Room`, `Doors`, `GameBuilder`), and each exercise imports
the module:

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
    # Set by the builder when the robot is placed
    room: Room

    def __init__(self) -> None:
        self.finished = False
        # Exercise 4: a place to count Coin pickups
        self.coins = 0

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
        # The void outside the maze: stay put
        return robot.room

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
    # Anything else is a teleport target
    return Teleport(symbol)

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
from robot_world import (Empty, GameBuilder, Item,
                         Robot, Room)

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
class whose `symbol` matches the character it receives, and
`__subclasses__()` reports the subclasses that exist right now, so
`class Coin(Item)` in `exercise_4.py` puts `Coin` on the list the
factory searches. `Room` and `GameBuilder` need no change either,
since both only ever call `occupant.interact(robot, room)` through the
shared `Item` interface.
Neither one has ever needed to know which concrete `Item` subclasses
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
    ("Where this door actually leads, "
     "or None if it's blocked.")
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
`EndGame`, returning the sequence of move letters that got there.
Breadth-first search reaches every room by the fewest moves in an
unweighted graph, so that sequence is the shortest path. `run()`
expects exactly such a string, the same as the previously hard-coded
`solution`, so `game.run(solution)` and the assertion that follows
match `test_robot.py`. Unlike the pre-computed `solution` string, the
computed one adapts automatically if the maze layout changes.

## 6, 7, and 8: the Chladni plate

The last three exercises all shake the same plate, so this file
carries the chapter's `chladni.py` once, with one change: `Plate`
takes the field function as a constructor argument instead of calling
the module-level `amplitude()` directly. That argument makes exercise
7's different physics a second function rather than an edit, so both
functions can run side by side in one program.

```python
# chladni.py
import math
import random
from collections.abc import Callable
from dataclasses import dataclass

type Mode = tuple[int, int]  # Vibration pattern (m, n)
type Field = Callable[[float, float, Mode], float]

def amplitude(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.cos(m * math.pi * x)
        * math.cos(n * math.pi * y)
        - math.cos(n * math.pi * x)
        * math.cos(m * math.pi * y))

def membrane(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.sin(m * math.pi * x)
        * math.sin(n * math.pi * y))

def bounce(v: float) -> float:
    if v < 0.0:
        return -v
    if v > 1.0:
        return 2.0 - v
    return v

@dataclass
class Grain:
    x: float
    y: float

class Plate:
    def __init__(self, grains: int, mode: Mode,
                 seed: int | None = None,
                 field: Field = amplitude) -> None:
        self.rng = random.Random(seed)
        self.mode = mode
        self.field = field
        self.grains = [
            Grain(self.rng.random(), self.rng.random())
            for _ in range(grains)]

    def step(self, kick: float = 0.05) -> None:
        for g in self.grains:
            a = self.field(g.x, g.y, self.mode)
            g.x = bounce(
                g.x + self.rng.uniform(-kick, kick) * a)
            g.y = bounce(
                g.y + self.rng.uniform(-kick, kick) * a)

    def agitation(self) -> float:
        return sum(
            self.field(g.x, g.y, self.mode)
            for g in self.grains) / len(self.grains)

    def render(self, width: int = 60,
               height: int = 30) -> str:
        counts: list[list[int]] = [
            [0] * width for _ in range(height)]
        for g in self.grains:
            col = min(int(g.x * width), width - 1)
            row = min(int(g.y * height), height - 1)
            counts[row][col] += 1
        shades = " .:*#"
        return "\n".join(
            "".join(shades[min(c, len(shades) - 1)]
                    for c in row).rstrip()
            for row in counts)
```

## 6. Freezing the plate

```python
# exercise_6.py
from chladni import Plate, amplitude

print(amplitude(0.31, 0.79, (2, 2)))
#: 0.0
plate = Plate(grains=2000, mode=(2, 2), seed=42)
before = [(g.x, g.y) for g in plate.grains]
for _ in range(1200):
    plate.step()
after = [(g.x, g.y) for g in plate.grains]
print(f"agitation {plate.agitation():.3f}, "
      f"moved {before != after}")
#: agitation 0.000, moved False
print(amplitude(0.37, 0.37, (1, 2)))
#: 0.0
```

With `m == n`, `amplitude()` returns zero everywhere. Its two terms
become `cos(mπx)cos(mπy)` and `cos(mπx)cos(mπy)`, the same product
written twice, and the function subtracts one from the other. Not
approximately zero: the two multiplications produce identical floats,
so the difference is exactly `0.0` at every point on the plate.

A zero field means a zero kick. `step()` scales each grain's random
displacement by the amplitude under that grain, so
`uniform(-kick, kick) * 0.0` moves nothing, and 1200 steps leave every
grain exactly where the constructor scattered it. The result is
neither chaos nor a figure because no grain ever moves: what you see
is the initial random scatter, frozen. Agitation reads `0.000` from
the first step, the same number a perfectly settled plate reports, so
the summary statistic cannot tell "finished" from "never started."

The main diagonal in every figure follows from the same symmetry.
Swapping `x` and `y` turns the first term into the second and the
second into the first, so the swap reverses the subtraction inside
`amplitude()`'s `abs()`. On the line `x == y` the swap changes
nothing, so the subtraction there must equal its own negation, which
forces that value to zero. Every mode this plate can ring in therefore
has a nodal line straight down the main diagonal, and the figures all
share that one feature no matter which `(m, n)` produced them.

## 7. Changing the physics

```python
# exercise_7.py
from chladni import Plate, membrane

plate = Plate(grains=2000, mode=(2, 3), seed=42,
              field=membrane)
steps = 0
for target in (0, 100, 400, 1200):
    for _ in range(target - steps):
        plate.step()
    steps = target
    print(f"steps {target:4}: "
          f"agitation {plate.agitation():.3f}")
#: steps    0: agitation 0.406
#: steps  100: agitation 0.100
#: steps  400: agitation 0.014
#: steps 1200: agitation 0.002
print(plate.render(width=40, height=20))
#: #:**# ######:#####..#:##*###############
#: #                  ##                  #
#: #                  ##                 .#
#: #    .             ##                  #
#: #                  ##                  #
#: #                  #*                  #
#: ######################*#################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: *                 .##   .             .#
#: ########################################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #               .  ##                  #
#: ##############**##:##.#:##############.#
```

The figure is a grid: one vertical line down the middle of the plate
and two horizontal lines cutting it into thirds, with the four edges
filled in as well.

The nodal lines are straight because the new field is a product of one
function of `x` and one function of `y`. The product vanishes when
either factor does, and `sin(mπx)` is zero at `x = 0, 1/2, 1` for
`m = 2`, regardless of `y`. Those three zeros give vertical lines.
`sin(nπy)` is zero at `y = 0, 1/3, 2/3, 1` for `n = 3`, regardless of
`x`, giving horizontal lines. Every nodal point lies on one of those
seven lines, and the interior lines number `m - 1` vertical and
`n - 1` horizontal, so the mode numbers are readable straight off the
picture.

The plate's own field never separates into a factor in `x` times a
factor in `y`. Each of its two terms mixes `x` and `y`, and
subtracting one from the other leaves zeros along the curves where the
two products happen to agree, which is why the original figures are
diagonals, crosses, and rings rather than a grid. Those mixed terms
come from the physics the chapter's formula approximates, a real plate
with free edges rather than a membrane clamped all around its rim. The
simulation machinery stays the same across both fields: same grains,
same random walk, same rule that a grain moves in proportion to the
vibration under it. Only the field changed, and with it every pattern
the model produces.

## 8. Tuning the noise

```python
# exercise_8.py
from chladni import Plate

for kick in (0.005, 0.05, 0.5):
    plate = Plate(grains=2000, mode=(2, 3), seed=42)
    steps = 0
    readings = []
    for target in (0, 100, 400, 1200):
        for _ in range(target - steps):
            plate.step(kick=kick)
        steps = target
        readings.append(f"{plate.agitation():.3f}")
    print(f"kick {kick:<5}: {' '.join(readings)}")
#: kick 0.005: 0.585 0.560 0.494 0.380
#: kick 0.05 : 0.585 0.073 0.005 0.000
#: kick 0.5  : 0.585 0.106 0.012 0.000
```

`kick=0.005` produces order too slowly. Each step displaces a grain by
at most half a percent of the plate, so a grain starting in the middle
of a bright region needs hundreds of steps to walk anywhere near a
nodal line. After 1200 steps agitation has fallen from `0.585` to
`0.380`, roughly a third of the way, while the default kick was
already down to `0.005` by step 400. Rendered, this run still looks
like noise with a faint trace of structure in it. Nothing is wrong
with the physics. The run is simply not finished, and finishing it
means more steps than anyone wants to watch.

`kick=0.5` fails differently, and the agitation column is what makes
that failure interesting: agitation collapses to `0.000` as
convincingly as it does at the default kick. The figure never appears
anyway. A half-unit displacement can throw a grain across the plate in
one step, so a grain never traces a descent toward the nearest nodal
line. The grain jumps somewhere unrelated and stays only if that spot
happens to be quiet. Grains accumulate in whichever quiet regions they
land in first, mostly the corners, and the lines between them stay
empty. The plate reports settled sand in the wrong places.

That failure is worth keeping in mind. Agitation measures whether the
grains are sitting where the field is weak, not whether the figure is
right, so one number cannot distinguish a sharp pattern from three
blobs. The render is the check the number cannot perform.

An intermediate kick avoids both failures because the amplitude scaling
in `step()` is a feedback loop, and the loop only works within a range
of step sizes. A grain in a loud region gets a large kick and moves
fast. As it nears a nodal line the amplitude shrinks and so does its
step, so it slows down and stops without overshooting. Too small a kick
starves the loop's first half, and the grain never travels. Too large a
kick breaks the second half, since even a heavily scaled step is still
big enough to leave the neighborhood the grain was settling into. The
default `0.05` sits where both halves work: about a twentieth of the
plate at full amplitude, and vanishingly small once a grain arrives.
