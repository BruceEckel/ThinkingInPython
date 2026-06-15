# robot_explorer/game.py
# The Builder pattern: build the maze in stages, then run it.
from __future__ import annotations

from items import Empty, Robot, Teleport, Urge, item_factory
from world import Room


class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: dict[tuple[int, int], Room] = {}
        teleports: list[Room] = []
        # Stage 1: a Room for every character.
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
        # Stage 2: connect each room to its neighbors.
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        # Stage 3: pair the teleports that share a target letter.
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

    def run(self, solution: str) -> None:
        moves = {"n": Urge.NORTH, "s": Urge.SOUTH,
                 "e": Urge.EAST, "w": Urge.WEST}
        for char in "".join(solution.split()):
            self.robot.move(moves[char])


string_maze = """
a_...#..._c
R_...#...__
###########
a_......._b
###########
!_c_....._b
""".strip()

solution = "eeeenwwww eeeeeeeeee wwwwwwww eeennnwwwwwsseeeeeen ww"

if __name__ == "__main__":
    game = GameBuilder(string_maze)
    print("start:")
    print(game.show_maze())
    game.run(solution)
    print("\nfinal:")
    print(game.show_maze())
