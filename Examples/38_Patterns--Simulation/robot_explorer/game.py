# robot_explorer/game.py
from itertools import groupby
from items import Empty, Robot, Teleport, Urge, item_factory
from world import Room, RoomMap

type Moves = str

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[tuple[Teleport, Room]] = []
        # Stage 1: a Room for every character
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
        # Stage 2: connect each room to its neighbors
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        # Stage 3: pair teleports sharing a target letter
        teleports.sort(key=lambda entry: entry[0].target)
        for letter, group in groupby(
            teleports, key=lambda entry: entry[0].target
        ):
            pair = list(group)
            assert len(pair) == 2, letter
            (t1, room1), (t2, room2) = pair
            t1.target_room = room2
            t2.target_room = room1

    def show_maze(self) -> str:
        rows: list[str] = []
        current = -1
        for (row, _), room in self.rooms.items():
            if row != current:
                rows.append("")
                current = row
            if room is self.robot.room:
                rows[-1] += str(self.robot)
            else:
                rows[-1] += str(room.occupant)
        return "\n".join(rows)

    def run(self, moves: Moves) -> None:
        for char in moves:
            self.robot.move(Urge(char))
