# robot_explorer/items.py
# The things that can occupy a room. Room.enter() calls
# occupant.interact(), and each Item subclass decides what happens.
# There is no conditional on the item's type.

from enum import Enum
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from world import Room

class Urge(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4

class Item:
    symbol = ""

    def interact(self, robot: Robot, room: Room) -> Room:
        return room  # Default: the robot enters the room.

    def __str__(self) -> str:
        return self.symbol

class Robot(Item):
    symbol = "R"

    def __init__(self) -> None:
        self.room: Room | None = None

    def move(self, urge: Urge) -> None:
        assert self.room is not None
        self.room = self.room.doors.open(urge).enter(self)

class Wall(Item):
    symbol = "#"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert robot.room is not None
        return robot.room  # Cannot pass: stay put.

class Food(Item):
    symbol = "."

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        room.occupant = Empty()  # Eaten.
        return room

class Teleport(Item):
    symbol = ""  # Set per target letter

    def __init__(self, target: str) -> None:
        self.target = target
        self.target_room: Room | None = None

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert self.target_room is not None
        return self.target_room

    @override
    def __str__(self) -> str:
        return self.target

class Empty(Item):
    symbol = "_"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        return room

class Edge(Item):
    symbol = "/"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        assert robot.room is not None
        return robot.room  # The void outside the maze: stay put.

class EndGame(Item):
    symbol = "!"

    @override
    def interact(self, robot: Robot, room: Room) -> Room:
        print("Game over!")
        return room

def item_factory(symbol: str) -> Item:
    for item_type in Item.__subclasses__():
        if symbol == item_type.symbol:
            return item_type()
    return Teleport(symbol)  # Anything else is a teleport target.
