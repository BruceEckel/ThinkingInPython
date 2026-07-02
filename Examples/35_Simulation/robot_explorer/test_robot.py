# robot_explorer/test_robot.py
from typing import Final
from game import GameBuilder, solution, string_maze
from items import EndGame

FINISHED: Final[str] = """
###############################
#_#.____#_____#_______#_______#
#_###_#_###_#_#_#_#####_#####_#
#___#_#___#_#_#_#.#__b__#___#_#
###_#_###_#_#_###_#_#####_#_#_#
#.#_#_#___#_#___#_#__b__#_#___#
#_#_#_#_###_###_#_#####_#_#####
#_#_#_#___#_#_#_____#___#_____#
#_#_#_###_#_#_#_#####_#######_#
#.#___#___#_#___#_____#_____#_#
#_#####_###_#_###_#####_#_###_#
#___#a__#___#___#___#___#_#___#
#_#_#_###_#####_###_###_###_#_#
#_#.#_#___#R______#_____#___#_#
#_#_#_###_#############_#_###_#
#_#_#__a#_______________#___#_#
#_#####_###_###########_###_#_#
#_____#___#_#___#_____#_#___#_#
#_#_#####_###_#_#_###_###_###_#
#.#___________#___#_______#___#
###############################
""".strip()

def test_solution_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solution)
    room = game.robot.room
    assert isinstance(room.occupant, EndGame)  # Finished on the "!"
    assert game.robot.finished  # And the model recorded it
    assert game.show_maze() == FINISHED  # Food eaten, robot moved

def test_walls_block_and_food_is_eaten() -> None:
    game = GameBuilder("R.#")  # Robot, food, wall in one row
    start = game.robot.room
    game.run("e")  # east: eat the food and move in
    assert "." not in game.show_maze()  # Food gone
    assert game.robot.room is not start
    blocked = game.robot.room
    game.run("e")  # East again: a wall, so stay put
    assert game.robot.room is blocked
