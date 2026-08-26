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
The structure that matters survives the trim: `claim()` is unchanged,
and `explore()` still opens a `TaskGroup` and lets `spawn()` add tasks
to it, since new rats keep arriving after the block begins.

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
none of the right room's, so `unreached` is the right room's
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

The one requested change drags three signatures with it, which is the
exercise's quiet lesson: `async` is contagious.
Once `claim()` is an `async def`, the `Recorder` protocol must declare
it `async` too, `Rat.run()`'s comprehension needs
`if await self.blackboard.claim(*pos)`, and `explore()` must `await`
its own first claim.
`spawn()` stays synchronous; nothing in it suspends.

On the chapter's seven-by-nine test maze, `claim()` returns `True` 25
times for 24 open cells: one pair of rats collided.
Both reached `await asyncio.sleep(0)` while the same cell still looked
unclaimed, since neither had added it to `visited` yet, so both
membership tests passed, and only then did each one call
`self.visited.add(...)`.
The result is two rats that each believe they alone claimed that cell.
Both move into it, which breaks the invariant that no two rats cover
the same ground. Nothing goes unexplored. Both rats proceed from the
shared cell and duplicate each other's work from there, while
`visited` stays correct, because adding the same cell twice to a set
changes nothing. That is why `test_rats_and_mazes.py` passes on the
broken version every time: it asserts the set of cells reached. The
extra success costs the rats wasted effort, two tasks tracing
overlapping paths, and the count of `True` returns against
`len(blackboard.visited)` exposes it.

The original `claim()` needs no lock because it has no `await`
between the test and the add. A coroutine yields control only at an
`await`, so with nothing to await in between, the two statements run
as one uninterruptible unit as far as any other coroutine is
concerned; there is no scheduling point in the middle for another rat
to slip into. Adding the `await` creates that scheduling point, and
the whole guarantee depends on there being none.

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
`EndGame`, returning the sequence of move letters that got there, the
shortest one first since a breadth-first search always finds the
shortest path in an unweighted graph. That returned string is exactly
what `run()` already expects, the same as the previously hard-coded
`solution`, so `game.run(solution)` and the assertion that follows are
unchanged from `test_robot.py`. Unlike the pre-computed `solution`
string, this one adapts automatically if the maze layout changes.

## 6, 7, and 8: the Chladni plate

The last three exercises all shake the same plate, so the chapter's
`chladni.py` is repeated here once, with one change: `Plate` takes the
field function as a constructor argument instead of calling the
module-level `amplitude()` directly. That makes exercise 7's different
physics a second function rather than an edit, so both can run side by
side in one program.

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
displacement by the amplitude under it, so `uniform(-kick, kick) * 0.0`
moves nothing, and 1200 steps leave every grain exactly where the
constructor scattered it. The result is neither chaos nor a figure
because there is no motion at all: what you see is the initial random
scatter, frozen. Agitation reads `0.000` from the first step, which is
the same number a perfectly settled plate reports, so the summary
statistic cannot tell "finished" from "never started."

The diagonal follows from the same symmetry. Swapping `x` and `y`
turns the first term into the second and the second into the first, so
`amplitude(y, x, mode)` is `amplitude(x, y, mode)` with the
subtraction reversed. The absolute value hides the sign, but on the
line `x == y` the swap changes nothing, so a value that equals its own
negation must be zero. Every mode this plate can ring in therefore has
a nodal line straight down the main diagonal, which is why the figures
all share that one feature no matter which `(m, n)` produced them.

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
function of `x` and one function of `y`. It vanishes when either factor
does, and `sin(mπx)` is zero at `x = 0, 1/2, 1` for `m = 2`, regardless
of `y`. That gives vertical lines at those three values of `x`.
`sin(nπy)` is zero at `y = 0, 1/3, 2/3, 1` for `n = 3`, regardless of
`x`, giving horizontal lines. Every nodal point lies on one of those
seven lines, and the number of interior lines is `m - 1` vertical and
`n - 1` horizontal, so the mode numbers are readable straight off the
picture.

The plate's own field factors the other way. Its two terms mix `x` and
`y` in both, and subtracting them creates zeros along curves where the
two products happen to agree, which is why the original figures are
diagonals, crosses, and rings rather than a grid. Fixing a real plate
at its edges only, rather than at a rim, is what produces those mixed
terms. The simulation machinery does not change at all between the two:
same grains, same random walk, same rule that a grain moves in
proportion to the vibration under it. Only the field changed, and with
it every pattern the model produces.

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
`0.380`, roughly a third of the way, where the default kick reached
`0.000` in a quarter of the time. Rendered, this run still looks like
noise with a faint grain of structure in it. Nothing is wrong with the
physics; the run is simply not finished, and finishing it means more
steps than anyone wants to watch.

`kick=0.5` fails differently, and the agitation column is what makes
it interesting: it collapses to `0.000` as convincingly as the default
does. The figure never appears anyway. A half-unit displacement can
throw a grain across the plate in one step, so a grain never traces a
descent toward the nearest nodal line; it jumps somewhere unrelated and
stays only if that spot happens to be quiet. Grains accumulate in
whichever quiet regions they land in first, mostly the corners, and the
lines between them stay empty. The plate reports settled sand in the
wrong places.

That is worth keeping. Agitation measures whether the grains are
sitting where the field is weak, not whether the figure is right, so
one number cannot distinguish a sharp pattern from three blobs. The
render is the check the number cannot perform.

An intermediate kick avoids both failures because the amplitude scaling
in `step()` is a feedback loop, and the loop only works within a range
of step sizes. A grain in a loud region gets a large kick and moves
fast; as it nears a nodal line the amplitude shrinks and so does its
step, so it slows down and stops without overshooting. Too small a kick
starves the loop's first half, and the grain never travels. Too large a
kick breaks the second half, since even a heavily scaled step is still
big enough to leave the neighborhood the grain was settling into. The
default `0.05` sits where both halves work: about a twentieth of the
plate at full amplitude, and vanishingly small once a grain arrives.
