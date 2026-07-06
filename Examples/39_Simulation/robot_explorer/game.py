# robot_explorer/game.py
# Build the maze in three stages, then run it.

from items import Empty, Robot, Teleport, Urge, item_factory
from world import Room, RoomMap

class GameBuilder:
    def __init__(self, maze: str) -> None:
        self.rooms: RoomMap = {}
        teleports: list[Room] = []
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
                    teleports.append(room)
        # Stage 2: connect each room to its neighbors
        for (row, col), room in self.rooms.items():
            room.doors.connect(row, col, self.rooms)
        # Stage 3: pair the teleports that share a target letter
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

solution = (
    "sseesssssseennnnnnnneesseesswwsseesswwsswwsseesseeeenneessee"
    "nneeeesseeeenneennwwnneenneennnnwwwwnnnneesseennnnwwwwwwssww"
    "eesswwsswwwwsseesseeeesswwwwwwwwwwwwwwnnnneennnnnnnnnneessss"
    "eesssswwsseesswwww"
)

game = GameBuilder(string_maze)
print("start:")
print(game.show_maze())
#: start:
#: ###############################
#: #R#.____#____.#_______#_______#
#: #_###_#_###_#_#_#_#####_#####_#
#: #___#_#___#_#_#_#.#__b__#___#_#
#: ###_#_###_#_#_###_#_#####_#_#_#
#: #.#_#_#.__#_#__.#_#__b__#_#___#
#: #_#_#_#_###_###_#_#####_#_#####
#: #_#_#_#__.#_#_#_____#___#_____#
#: #_#_#_###_#_#_#_#####_#######_#
#: #.#___#___#_#___#____.#_____#_#
#: #_#####_###_#_###_#####_#_###_#
#: #___#a__#.__#.__#__.#___#_#___#
#: #_#_#_###_#####_###_###_###_#_#
#: #_#.#_#___#!______#_____#___#_#
#: #_#_#_###_#############_#_###_#
#: #_#_#__a#_______________#___#_#
#: #_#####_###_###########_###_#_#
#: #_____#.__#_#___#_____#_#___#_#
#: #_#_#####_###_#_#_###_###_###_#
#: #.#___________#___#____.__#___#
#: ###############################
game.run(solution)
if game.robot.finished:
    print("Game over!")
print("\nfinal:")
print(game.show_maze())
#: Game over!
#:
#: final:
#: ###############################
#: #_#.____#_____#_______#_______#
#: #_###_#_###_#_#_#_#####_#####_#
#: #___#_#___#_#_#_#.#__b__#___#_#
#: ###_#_###_#_#_###_#_#####_#_#_#
#: #.#_#_#___#_#___#_#__b__#_#___#
#: #_#_#_#_###_###_#_#####_#_#####
#: #_#_#_#___#_#_#_____#___#_____#
#: #_#_#_###_#_#_#_#####_#######_#
#: #.#___#___#_#___#_____#_____#_#
#: #_#####_###_#_###_#####_#_###_#
#: #___#a__#___#___#___#___#_#___#
#: #_#_#_###_#####_###_###_###_#_#
#: #_#.#_#___#R______#_____#___#_#
#: #_#_#_###_#############_#_###_#
#: #_#_#__a#_______________#___#_#
#: #_#####_###_###########_###_#_#
#: #_____#___#_#___#_____#_#___#_#
#: #_#_#####_###_#_#_###_###_###_#
#: #.#___________#___#_______#___#
#: ###############################
