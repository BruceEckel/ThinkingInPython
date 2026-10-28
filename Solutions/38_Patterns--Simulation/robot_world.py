# robot_world.py
from enum import Enum
from itertools import groupby
from typing import ClassVar, Final, override

class Urge(Enum):
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"

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
type Route = str

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

# The void outside the maze
EDGE: Final[Room] = Room(Wall())

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[tuple[Teleport, Room]] = []
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
                    teleports.append((occupant, room))
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        teleports.sort(key=lambda entry: entry[0].target)
        for letter, group in groupby(
            teleports, key=lambda entry: entry[0].target
        ):
            pair = list(group)
            assert len(pair) == 2, letter
            (t1, room1), (t2, room2) = pair
            t1.target_room = room2
            t2.target_room = room1

    def run(self, moves: Route) -> None:
        for char in moves:
            self.robot.move(Urge(char))
