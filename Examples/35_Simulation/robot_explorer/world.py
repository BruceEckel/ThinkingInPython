# robot_explorer/world.py
from typing import Final
from items import Edge, Item, Robot, Urge

type Coord = tuple[int, int]   # (row, col)

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
        self.north: Room | None = None
        self.south: Room | None = None
        self.east: Room | None = None
        self.west: Room | None = None

    def connect(self, row: int, col: int,
                rooms: dict[Coord, Room]) -> None:
        self.north = rooms.get((row - 1, col))
        self.south = rooms.get((row + 1, col))
        self.east = rooms.get((row, col + 1))
        self.west = rooms.get((row, col - 1))

    def open(self, urge: Urge) -> Room:
        neighbor = {
            Urge.NORTH: self.north,
            Urge.SOUTH: self.south,
            Urge.EAST: self.east,
            Urge.WEST: self.west,
        }[urge]
        return neighbor if neighbor is not None else EDGE

# Created once both classes exist; its own doors stay unset
EDGE: Final[Room] = Room(Edge())
