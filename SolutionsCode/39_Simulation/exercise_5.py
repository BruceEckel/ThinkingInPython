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
    "Where this door actually leads, or None if it's blocked."
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
