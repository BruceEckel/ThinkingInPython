# robot_explorer/test_robot.py
from game import GameBuilder, string_maze
from items import EndGame
from solver import solve

def test_search_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solve(game))
    # Finished on the "!"
    assert isinstance(game.robot.room.occupant, EndGame)
    assert game.robot.finished  # And the model recorded it

def test_walls_block_and_food_is_eaten() -> None:
    game = GameBuilder("R.#")
    assert game.show_maze() == "R.#"
    start = game.robot.room
    game.run("e")  # East: eat the food and move in
    assert game.robot.room is not start
    blocked = game.robot.room
    game.run("e")  # East again: a wall, so stay put
    assert game.robot.room is blocked
    game.run("w")  # Back west: the food cell is empty
    assert game.show_maze() == "R_#"
