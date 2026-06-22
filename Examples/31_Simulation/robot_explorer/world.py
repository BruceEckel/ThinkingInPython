# robot_explorer/world.py
# A Room holds one Item and connects to neighbors through its Doors.
# Unset doors point at the shared EDGE room outside the maze.

from items import Edge, Item, Robot, Urge

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
                rooms: dict[tuple[int, int], Room]) -> None:
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
EDGE = Room(Edge())
