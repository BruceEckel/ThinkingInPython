# Simulation: Solutions

## 1. Testing a `Rat` with a fake blackboard

> Test a `Rat` with a fake blackboard.
> Because `Rat` depends only on the `Recorder` `Protocol`,
> you can drive it with a stand-in.
> Write a fake whose `claim()` returns a scripted sequence of results and whose `spawn()` records the coordinates it receives instead of starting a rat,
> run one rat with `asyncio.run(rat.run())`,
> and assert which cell the rat kept for itself and which cells it spawned.
> You need no real `Blackboard`, `Maze`, or task scheduling.

<details>
<summary>Where to look</summary>

[The Rat and the Blackboard](../../Chapters/38_Patterns--Simulation.md#the-rat-and-the-blackboard) shows `Rat` calling only the methods of the `Recorder` `Protocol`.
Write a class with those methods, so it satisfies the `Protocol` by shape.
Make `claim()` return values from an iterator you script, and have `spawn()` append to a list.
After `asyncio.run(rat.run())`, assert on the rat's position and on that list.

<details>
<summary>Solution</summary>

If you call `next(self.claim_results)` without the `False` default,
the fake works for the rat's first turn and fails on its second.
The fifth `claim()` finds the script empty, so `next()` raises a `StopIteration` inside the coroutine,
and Python turns it into a `RuntimeError` ("coroutine raised StopIteration") that fails the test.
The default lets the fake answer `False` once the script runs out,
so the rat dead-ends the way it would against walls.

```python
# test_ch38_fake_blackboard.py
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

def test_rat_keeps_one_claim_and_spawns_the_rest() -> None:
    # DIRECTIONS tests (0,1), (0,-1), (-1,0), (1,0) in that
    # order. Script the 2nd and 4th as open, the 1st and
    # 3rd as walls or visited:
    fake = FakeBlackboard([False, True, False, True])
    rat = Rat(fake, 0, 0)
    asyncio.run(rat.run())
    # Kept the first successful claim
    assert (rat.x, rat.y) == (0, -1)
    # Spawned a rat at every claim after that
    assert fake.spawned == [(1, 0)]
    assert fake.messages == [
        "Rat 1 starts at (0, 0).",
        "Rat 1 dead-ends at (0, -1)."]
```

**Stand in for the blackboard.** `Rat` depends on the `Recorder`
`Protocol`, not on `Blackboard`, so `FakeBlackboard` satisfies that
`Protocol` by shape. It defines `claim()`, `spawn()`, `log()`, and
`next_number()`, and none of the four touches a real `Maze` or
`asyncio.create_task()`.

**Script the rat's choices.** Scripting `claim()`'s return values in a
preset sequence decides which neighbor the rat keeps for itself and
into which cells it spawns new rats: the first cell the loop finds
open, `(0, -1)`, and every open one after that, here `(1, 0)` alone.

**Stop the rat when the script ends.** Once the script runs out, `claim()` answers
`False` to everything, so the rat dead-ends on its second turn and
`run()` returns. The test needs no randomness and no real maze.

</details>
</details>

## 2. Reporting unreached cells

> Report the cells no rat reaches.
> After `explore()` finishes,
> compare `blackboard.visited` against every open cell of the `Maze` and print the open cells that no rat claimed.
> Build a maze for which that set is not empty,
> and explain what makes a cell unreachable.

<details>
<summary>Where to look</summary>

[Running the Maze](../../Chapters/38_Patterns--Simulation.md#running-the-maze) shows `explore()` starting every rat from one entry cell and recording what the rats claim in `blackboard.visited`.
Build a set of every open cell in the `Maze` and subtract `visited` from it.
To make the difference non-empty, draw a maze whose open cells split into regions that no open path joins.
Then ask where every rat begins.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
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
        ...

    @classmethod
    def from_text(cls, text: str) -> Self:
        ...

    def is_open(self, x: int, y: int) -> bool:
        ...

    def entry(self) -> Coord:
        ...

@dataclass
class Rat:
    blackboard: Blackboard
    x: int
    y: int

    async def run(self) -> None:
        ...

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    group: asyncio.TaskGroup = field(init=False)

    def claim(self, x: int, y: int) -> bool:
        ...

    def spawn(self, x: int, y: int) -> None:
        ...

    async def explore(self) -> None:
        ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

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

**Reuse the chapter's classes.** The classes are the chapter's, trimmed of what the exercise does not
need: rat numbers, logging, the task list, `render()`, the
`Recorder` `Protocol`, and the file loader.
The structure that matters survives the trim. `claim()` keeps the
chapter's body word for word, and `explore()` still opens a
`TaskGroup` and lets `spawn()` add tasks to that group, because new
rats keep arriving after the block begins.

**Split the open cells into two regions.** For a maze built with two separate rooms and no connecting opening
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
cells.

A cell is unreachable when no path of open cells connects it to the
entry, not when a wall surrounds it. `Maze.entry()` scans row by row
and returns the first open cell it finds, and every rat traces back to
that single starting point through `claim()`. No rat therefore reaches
a cell that has no open-cell path back to the entry, however many rats
spawn.

</details>
</details>
</details>

## 3. Breaking `claim()`'s atomicity

> Break the atomicity of `claim()`.
> Make `claim()` an `async def`,
> which forces matching changes in the `Recorder` protocol,
> `Rat.run()`'s comprehension, and `explore()`.
> Put `await asyncio.sleep(0)` between the membership test and `self.visited.add(...)`.
> Then count how many calls return `True` and compare that count with `len(blackboard.visited)`,
> using a maze that contains a loop.
> `amaze.txt` is a perfect maze,
> so no two rats reach one unclaimed cell and the counts always agree.
> `test_rats_and_mazes.py` still passes, because `visited` is a set.
> The guarantee that broke is "one rat per cell", not "every cell visited".
> What happens to the two rats that both claimed one cell,
> and why does the original `claim()`, with no `await` inside it,
> need no lock?

<details>
<summary>Where to look</summary>

[Contention on a Loop](../../Chapters/38_Patterns--Simulation.md#contention-on-a-loop) shows two rats reaching one unclaimed cell, and [The Rat and the Blackboard](../../Chapters/38_Patterns--Simulation.md#the-rat-and-the-blackboard) shows the `claim()` you are changing.
Making `claim()` an `async def` means each caller must `await` it, which spreads through the `Protocol`, the comprehension, and `explore()`.
Count the `True` results in a field on the `Blackboard` and compare the count with `len(visited)`.
A coroutine gives up control only at an `await`, which decides whether `claim()` needs a lock.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
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
        ...

    @classmethod
    def from_text(cls, text: str) -> Self:
        ...

    def is_open(self, x: int, y: int) -> bool:
        ...

    def entry(self) -> Coord:
        ...

class Recorder(Protocol):
    async def claim(self, x: int, y: int) -> bool: ...
    def spawn(self, x: int, y: int) -> None: ...

@dataclass
class Rat:
    blackboard: Recorder
    x: int
    y: int

    async def run(self) -> None:
        ...

@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(init=False,
                                default_factory=set)
    true_claims: int = field(init=False, default=0)
    group: asyncio.TaskGroup = field(init=False)

    async def claim(self, x: int, y: int) -> bool:
        ...

    def spawn(self, x: int, y: int) -> None:
        ...

    async def explore(self) -> None:
        ...

async def main() -> None:
    ...
```

```python
# The shape of robot_world.py
from enum import Enum, auto
from itertools import groupby
from typing import ClassVar, Final, override

class Urge(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()

class Item:
    symbol: ClassVar[str] = ""

    def interact(self, robot: Robot, room: Room) -> Room:
        ...

    def __str__(self) -> str:
        ...

class Robot(Item):
    symbol: ClassVar[str] = "R"
    # Set by the builder when the robot is placed
    room: Room

    def __init__(self) -> None:
        ...

    def move(self, urge: Urge) -> None:
        ...

class Wall(Item):
    symbol: ClassVar[str] = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...

class Food(Item):
    symbol: ClassVar[str] = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...

class Teleport(Item):
    symbol: ClassVar[str] = ""  # Shown as its target letter
    target_room: Room  # Paired up by the builder

    def __init__(self, target: str) -> None:
        ...

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...

    @override
    def __str__(self) -> str:
        ...

class Empty(Item):
    symbol: ClassVar[str] = "_"

class Edge(Item):
    symbol: ClassVar[str] = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        # The void outside the maze: stay put
        ...

class EndGame(Item):
    symbol: ClassVar[str] = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...

def item_factory(symbol: str) -> Item:
    ...

type Coord = tuple[int, int]
type RoomMap = dict[Coord, Room]

class Room:
    def __init__(self, occupant: Item) -> None:
        ...

    def enter(self, robot: Robot) -> Room:
        ...

    def __repr__(self) -> str:
        ...

class Doors:
    def __init__(self) -> None:
        ...

    def connect(self, row: int, col: int,
                rooms: RoomMap) -> None:
        ...

    def open(self, urge: Urge) -> Room:
        ...

EDGE: Final[Room] = Room(Edge())

class GameBuilder:
    def __init__(self, maze: str) -> None:
        ...

    def run(self, solution: str) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you test the broken `claim()` on `amaze.txt`,
the count of `True` returns equals `len(visited)` on every run,
and the gap looks harmless.
A perfect maze offers one path to each cell,
so no two rats reach one unclaimed cell.
The solution uses the seven-by-nine maze from `test_rats_and_mazes.py`,
whose loop lets two rats approach one cell from opposite directions.

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

**Carry the `async` to every caller.** The one requested change drags three more edits with it, and that
spread is the exercise's quiet lesson: `async` is contagious.
Once `claim()` is an `async def`, the `Recorder` protocol must declare
it `async` too, `Rat.run()`'s comprehension needs
`if await self.blackboard.claim(*pos)`, and `explore()` must `await`
its own first claim.
`spawn()` stays synchronous, because nothing in it suspends.

**Let two rats claim one cell.** On the chapter's seven-by-nine test maze, `claim()` returns `True` 25
times for 24 open cells. One pair of rats collided.
Both rats reach `await asyncio.sleep(0)` while the same cell still
looks unclaimed, because neither has added that cell to `visited`
yet. Both membership tests therefore pass before either rat calls
`self.visited.add(...)`.

Each of the two rats believes it alone claimed the shared cell.
Both move into it, and that overlap breaks the invariant that no two
rats cover the same ground. Every cell is still explored. Here the shared
cell is `(5, 5)`, where the loop closes, so both rats find every
neighbor claimed and dead-end there.

`visited` stays correct, because adding the same cell twice to a set
changes nothing. That correctness is why `test_rats_and_mazes.py`
passes on the broken version every time. The test asserts the set of
cells reached. The extra `True` costs wasted effort. A second rat
moves into an occupied cell. Comparing the count of `True` returns
with the size of `visited` exposes the collision.

The original `claim()` needs no lock because it has no `await`
between the test and the add. A coroutine yields control only at an
`await`, so the two statements run as one uninterruptible unit. The
event loop can hand control to another rat before the test or after
the add, but not between them. Adding the `await` opens that
gap in the middle, and the whole guarantee depends on the gap's absence.

Exercises 4 and 5 both build on the same `robot_explorer` world,
so `robot_world.py` holds that shared apparatus once (`Item` and its
subclasses, `Room`, `Doors`, `GameBuilder`), and each exercise imports
the module:

```python
# robot_world.py
from enum import Enum, auto
from itertools import groupby
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
    symbol: ClassVar[str] = "R"
    # Set by the builder when the robot is placed
    room: Room

    def __init__(self) -> None:
        self.finished = False
        # Exercise 4: a place to count Coin pickups
        self.coins = 0

    def move(self, urge: Urge) -> None:
        self.room = self.room.doors.open(urge).enter(self)

class Wall(Item):
    symbol: ClassVar[str] = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return robot.room  # Cannot pass: stay put

class Food(Item):
    symbol: ClassVar[str] = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten
        return room

class Teleport(Item):
    symbol: ClassVar[str] = ""  # Shown as its target letter
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
    symbol: ClassVar[str] = "_"

class Edge(Item):
    symbol: ClassVar[str] = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        # The void outside the maze: stay put
        return robot.room

class EndGame(Item):
    symbol: ClassVar[str] = "!"

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
        for letter, group in groupby(teleports, key=target):
            pair = list(group)
            assert len(pair) == 2, letter
            room1, room2 = pair
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

</details>
</details>
</details>

## 4. A `Coin` item

> Add a new kind of `Item` to the robot maze.
> Define a `Coin` subclass of `Item` with the symbol `$`.
> Its `interact()` removes the coin from its room,
> as `Food`'s does for the food,
> and adds one to a coin count carried by the `Robot`.
> Place a few `$` characters in the maze and report how many the robot collects.
> `item_factory()`, `Room`, and `GameBuilder` stay as they are.
> Explain why the factory finds your new item on its own,
> and what the factory does if you derive `Coin` from `Food` instead.

<details>
<summary>Where to look</summary>

[Rooms, Robots, and the Item Factory](../../Chapters/38_Patterns--Simulation.md#rooms-robots-and-the-item-factory) shows how `Food.interact()` replaces its own occupant and how `item_factory()` finds an `Item` class from its `symbol`.
Give `Coin` the `$` symbol, an `interact()` that does the same replacement, and a count on `Robot`.
To see why the factory finds `Coin` by itself, read which classes `Item.__subclasses__()` returns.
Then check whether a class derived from `Food` appears in that list.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import ClassVar, override
from robot_world import (Empty, GameBuilder, Item,
                         Robot, Room)

class Coin(Item):
    symbol: ClassVar[str] = "$"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        ...
```

<details>
<summary>Solution</summary>

If you derive `Coin` from `Food`, the program prints `0`,
and `item_factory("$")` returns a `Teleport`.
`Item.__subclasses__()` lists direct subclasses alone,
so the factory's search misses `Coin` and treats `$` as a
teleport target.
The solution derives `Coin` from `Item`, which puts it on the
list the factory searches.

```python
# exercise_4.py
from typing import ClassVar, override
from robot_world import (Empty, GameBuilder, Item,
                         Robot, Room)

class Coin(Item):
    symbol: ClassVar[str] = "$"

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

**Register the item by subclassing.** `item_factory()` needs
no change. It searches `Item.__subclasses__()` for a
class whose `symbol` matches the character it receives, and
`__subclasses__()` reports the subclasses that exist right now, so
`class Coin(Item)` in `exercise_4.py` puts `Coin` on the list the
factory searches.

**Act through the shared interface.** `Room` and `GameBuilder` need no change either.
`Room.enter()` calls `occupant.interact(robot, self)` through the
shared `Item` interface, and `GameBuilder` gets each occupant from
`item_factory()`.
Neither one needs to know which concrete `Item` subclasses exist.

**Give the robot a counter.** `Robot.__init__()` needs one new line, `self.coins = 0`, to have
somewhere to count (folded into `robot_world.py` above so this
exercise's file stays a single, runnable unit).

Deriving `Coin` from `Food` instead breaks the maze, and the reason is
where the factory searches, not what `Coin` inherits. `item_factory()`
walks `Item.__subclasses__()`, which lists the direct subclasses of
`Item` and misses their descendants, so a `Coin(Food)` is absent from
that list. No entry matches
`$`, and the loop falls through to the factory's last line, which
treats any unrecognized symbol as a teleport target. So
`item_factory("$")` returns `Teleport("$")`. The two `$` cells become
a teleport pair, the robot walks into a teleporter where the maze
should hold a coin, the topology changes underneath the hard-coded
route, and `game.robot.coins` stays
`0`. A one-word change to a class header moves a character out of
the factory's search and silently substitutes a different `Item`.

</details>
</details>
</details>

## 5. Sending the robot somewhere other than the `!`

> Send the robot to something other than the `!`.
> `solve()` stops at whatever room holds an `EndGame`,
> the one goal it can express.
> Replace that `isinstance()` test with a `Callable[[Room], bool]` parameter,
> so the caller says what counts as arriving,
> and change nothing else in the search,
> beyond letting `solve()` return `None` when no room matches.
> Then use the new parameter to feed the robot:
> search for the nearest room holding a `Food`, walk there,
> and repeat until no `Food` remains,
> then search for the `!` and walk the route the search finds.
> Report how many pieces of food the robot ate and how many moves the whole tour took.
> The run answers two questions for you.
> Why must the search run again after every meal instead of once at the start?
> And why does asking for the nearest food each time not produce the shortest tour that eats everything?

<details>
<summary>Where to look</summary>

[Choosing the Path](../../Chapters/38_Patterns--Simulation.md#choosing-the-path) shows `solve()` searching breadth-first and stopping at the room that holds an `EndGame`.
Replace that `isinstance()` test with a call to the `Callable[[Room], bool]` parameter, and return `None` when the queue empties.
Write one small predicate function for food and another for the `!`.
Loop with the walrus operator, `while (leg := solve(...)) is not None`, and walk each leg with `run()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections import deque
from collections.abc import Callable
from typing import Final
from robot_world import (Edge, EndGame, Food, GameBuilder,
                         Room, Teleport, Urge, Wall)

MOVES: Final[dict[Urge, str]] = {
    Urge.NORTH: "n", Urge.SOUTH: "s",
    Urge.EAST: "e", Urge.WEST: "w"}

def landing(room: Room, urge: Urge) -> Room | None:
    ...

def solve(game: GameBuilder,
          arrived: Callable[[Room], bool]) -> str | None:
    ...

def food(room: Room) -> bool:
    ...

def end(room: Room) -> bool:
    ...
```

<details>
<summary>Solution</summary>

If you keep the chapter's final `raise ValueError`,
the food loop cannot end normally.
After the last meal, the search for more food raises the `ValueError`,
and the script stops with a traceback before the walk to the `!` and before either `print()`.
Returning `None` makes an empty search the loop's ordinary exit.

```python
# exercise_5.py
from collections import deque
from collections.abc import Callable
from typing import Final
from robot_world import (Edge, EndGame, Food, GameBuilder,
                         Room, Teleport, Urge, Wall)

MOVES: Final[dict[Urge, str]] = {
    Urge.NORTH: "n", Urge.SOUTH: "s",
    Urge.EAST: "e", Urge.WEST: "w"}

def landing(room: Room, urge: Urge) -> Room | None:
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall | Edge):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder,
          arrived: Callable[[Room], bool]) -> str | None:
    start = game.robot.room
    queue: deque[tuple[Room, str]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if arrived(room):
            return path
        for urge, char in MOVES.items():
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + char))
    return None

def food(room: Room) -> bool:
    return isinstance(room.occupant, Food)

def end(room: Room) -> bool:
    return isinstance(room.occupant, EndGame)

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
meals = 0
moves = 0
while (leg := solve(game, food)) is not None:
    game.run(leg)
    meals += 1
    moves += len(leg)
last = solve(game, end)
assert last is not None
game.run(last)
moves += len(last)
print(meals, "meals,", moves, "moves")
#: 16 meals, 282 moves
print("finished:", game.robot.finished)
#: finished: True
```

**Let the caller define arrival.** `solve()`'s search changes in one place. The `isinstance(room.occupant,
EndGame)` test becomes `arrived(room)`, a predicate the caller
supplies. Nothing else in the search knows or cares what counts as
arriving. The `EndGame` version is now a one-line function on the
caller's side, `end()`, and `food()` is another.

**Report an empty search as `None`.** The other change is the return type.
The chapter's version raises a `ValueError` when the search runs out
of rooms, because a maze with no reachable `!` is a broken maze.
Here, running out of rooms is the ordinary way the food loop ends,
so `solve()` returns `None` and the walrus in the `while` reads it as
"nothing left to eat."

**Replan after every meal.** The search must run again after every
meal because its start and its goal both move.
`Food.interact()` replaces the food with an `Empty()`, so the
room the robot just arrived at stops being a goal, and the robot's
own room is now the new start. A path planned from the entry is no
use from any other room, so one search at the start yields the first
leg and no more. Searching again costs little. Each search touches at
most the maze's 299 rooms that hold no wall.

<!-- vale proselint.GenderBias = NO -->
Nearest-first does not give the shortest tour that eats everything.
Choosing the closest food each time is a greedy choice made with no
view of what comes after it, and the maze makes that costly. Two pieces
of food can sit close together down one dead-end corridor while a
third sits one step nearer in the opposite direction, with the rest
of the food far beyond it. Taking the single near one first means
walking to it, back past the start to the corridor, and out past it
again. The shortest
complete tour is a travelling-salesman problem over the food rooms,
and its first leg is often not the shortest leg available. The greedy
tour does guarantee that every leg is a shortest path, which is all
breadth-first search guarantees.
<!-- vale proselint.GenderBias = YES -->

</details>
</details>
</details>

## 6, 7, and 8: the Chladni plate

The last three exercises all shake the same plate, so this file
carries the chapter's `chladni.py` once, with two changes: `Plate`
takes the field function as a constructor argument instead of calling
the module-level `amplitude()`, and the module adds `membrane()`
beside `amplitude()`. That argument makes exercise
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

    def render(self, width: int = 57,
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

> Freeze the plate.
> Run the Chladni view with `MODES` starting at `(2, 2)`.
> Work out what `amplitude()` returns whenever `m == n`,
> and explain why the view shows neither chaos nor a figure.
> Then explain why the main diagonal shows up in every figure this plate makes.
> Swapping `x` and `y` in the two terms of `amplitude()` is the clue.

<details>
<summary>Where to look</summary>

[The Model](../../Chapters/38_Patterns--Simulation.md#the-model) shows `step()` scaling each grain's random displacement by `amplitude()`.
Substitute `m == n` into the two products of `amplitude()` and compare them.
For the diagonal, swap `x` and `y` and compare the sign of the difference inside `abs()` before and after.
Then ask what that implies where `x == y`.

<details>
<summary>Solution</summary>

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

**Probe the field at `m == n`.** With `m == n`, `amplitude()` returns zero everywhere. Its two terms
become `cos(mπx)cos(mπy)` and `cos(mπx)cos(mπy)`, the same product
written twice, and the function subtracts one from the other. Not
approximately zero: the two multiplications produce identical floats,
so the difference is exactly `0.0` at every point on the plate.

**Confirm that no grain moves.** A zero field means a zero kick. `step()` scales each grain's random
displacement by the amplitude under that grain, so
`uniform(-kick, kick) * 0.0` moves nothing, and 1200 steps leave every
grain where the constructor scattered it. The view shows
neither chaos nor a figure because no grain moves. It shows the
initial random scatter, frozen. Agitation reads `0.000` from
the first step, the same number a perfectly settled plate reports, so
the summary statistic cannot tell "finished" from "never started."

**Probe a point on the diagonal.** The main diagonal in every figure follows from the same two terms.
Swapping `x` and `y` turns the first term into the second and the
second into the first, so the swap reverses the subtraction inside
`amplitude()`'s `abs()`. On the line `x == y` the swap changes
nothing, so the subtraction there must equal its own negation, which
forces that value to zero. Every mode in which this plate can ring therefore
has a nodal line straight down the main diagonal, and the figures all
share that one feature no matter which `(m, n)` produced them.

</details>
</details>

## 7. Changing the physics

> Change the physics.
> Replace the body of `amplitude()` with `abs(math.sin(m * math.pi * x) * math.sin(n * math.pi * y))`,
> the standing waves of a membrane clamped at its edges, like a drumhead.
> Predict the figures before you run the view.
> Why are the nodal lines now straight?

<details>
<summary>Where to look</summary>

[What the Numbers Show](../../Chapters/38_Patterns--Simulation.md#what-the-numbers-show) explains how agitation measures the plate settling toward its nodal lines.
Pass a second field function to `Plate` and compare the figures.
Write the new field as a product of a function of `x` and a function of `y`.
A product is zero when either factor is zero, so find where each `sin` factor vanishes.

<details>
<summary>Solution</summary>

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

The plate's own field does not separate into a factor in `x` times a
factor in `y`. Each of its two terms mixes `x` and `y`, and
subtracting one from the other leaves zeros along the curves where the
two products agree, which is why the original figures are
diagonals, crosses, and rings rather than a grid. Those mixed terms
come from the physics the chapter's formula approximates, a real plate
with free edges rather than a membrane clamped all around its rim.

The simulation machinery stays the same across both fields: same
grains, same random walk, same rule that a grain moves in proportion
to the vibration under it. Only the field changes, and with it every
pattern the model produces.

</details>
</details>

## 8. Tuning the noise

> Tune the noise.
> Rerun `chladni_demo.py` passing `kick=0.005` and then `kick=0.5` to `plate.step()`,
> printing agitation at the same checkpoints.
> One setting produces order too slowly.
> The other drives agitation down as convincingly as the default kick,
> yet no figure appears.
> Explain both failures, and why an intermediate kick avoids them.

<details>
<summary>Where to look</summary>

[The Model](../../Chapters/38_Patterns--Simulation.md#the-model) shows `step()` multiplying the random kick by the amplitude, so a grain slows as it nears a nodal line.
Loop over the three kick values with a fresh `Plate` for each, and print agitation at the same checkpoints.
For the large kick, compare a grain's maximum single step with the size of the plate.
[The Model](../../Chapters/38_Patterns--Simulation.md#the-model) shows `render()`'s figure, which is the check that agitation cannot make.

<details>
<summary>Solution</summary>

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
        readings.append(f"{plate.agitation():.2f}")
    print(f"kick {kick:<5}: {' '.join(readings)}")
#: kick 0.005: 0.58 0.56 0.49 0.38
#: kick 0.05 : 0.58 0.07 0.00 0.00
#: kick 0.5  : 0.58 0.11 0.01 0.00
```

`kick=0.005` produces order too slowly. Each step displaces a grain by
at most one percent of the plate, so a grain starting in the middle
of a bright region needs hundreds of steps to walk anywhere near a
nodal line. After 1200 steps agitation has fallen from `0.58` to
`0.38`, roughly a third of the way, while the default kick was
down to `0.00` by step 400. Rendered, this run still looks
like noise with a faint trace of structure in it. The physics is
correct. The run is not finished, and finishing it
means more steps than anyone wants to watch.

`kick=0.5` fails differently, and the agitation column hides the
failure. Agitation collapses to `0.00` as convincingly as it does at
the default kick, and the figure does not appear. A kick of up to
half the plate, and the full width where the amplitude peaks at 2,
can throw a grain across the plate in one step, so a grain does not
walk toward the nearest nodal line. It jumps somewhere unrelated
and stays only if that spot is quiet. The spots that hold a grain
best are the two corners where the main diagonal ends. At `(0, 0)`
and `(1, 1)` the field is zero and also flat, so it stays weak over
a whole patch, where along a nodal line it is weak only in a thin
strip. Rendered, the run shows nearly every grain in those two
corners and the nodal lines between them empty. The plate reports
settled sand in the wrong places.

Agitation measures whether the grains sit where the field is weak,
not whether the figure is right, so one number cannot distinguish a
sharp pattern from two blobs. The render is the check the number
cannot perform.

An intermediate kick avoids both failures because the amplitude scaling
in `step()` is a feedback loop, and the loop works within a range
of step sizes and fails outside it.
A grain in a loud region gets a large kick and moves
fast. As it nears a nodal line the amplitude shrinks and so does its
step, so it slows down and stops without overshooting. Too small a kick
starves the loop's first half, and the grain barely travels. Too large a
kick breaks the second half, since even a heavily scaled step is still
big enough to leave the neighborhood into which the grain is settling. The
default `0.05` sits where both halves work: at most a tenth of the
plate where the amplitude peaks, and vanishingly small once a grain
arrives.

</details>
</details>
