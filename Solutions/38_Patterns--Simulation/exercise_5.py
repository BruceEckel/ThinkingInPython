# exercise_5.py
from collections import deque
from collections.abc import Callable
from typing import Final
from robot_world import (EndGame, Food, GameBuilder, Moves,
                         Room, Teleport, Urge, Wall)

def landing(room: Room, urge: Urge) -> Room | None:
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder,
          arrived: Callable[[Room], bool]) -> Moves | None:
    start = game.robot.room
    queue: deque[tuple[Room, Moves]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if arrived(room):
            return path
        for urge in Urge:
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + urge.value))
    return None

def food(room: Room) -> bool:
    return isinstance(room.occupant, Food)

def end(room: Room) -> bool:
    return isinstance(room.occupant, EndGame)

MAZE: Final[str] = """
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

game = GameBuilder(MAZE)
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
