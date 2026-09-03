# robot_explorer/test_robot.py
from game import GameBuilder, string_maze
from items import EndGame
from solver import solve

def test_search_walks_the_robot_to_the_end() -> None:
    game = GameBuilder(string_maze)
    game.run(solve(game))
    room = game.robot.room
    # Finished on the "!"
    assert isinstance(room.occupant, EndGame)
    assert game.robot.finished  # And the model recorded it

def test_walls_block_and_food_is_eaten() -> None:
    # Robot, food, wall in one row
    game = GameBuilder("R.#")
    start = game.robot.room
    game.run("e")  # East: eat the food and move in
    assert "." not in game.show_maze()  # Food gone
    assert game.robot.room is not start
    blocked = game.robot.room
    game.run("e")  # East again: a wall, so stay put
    assert game.robot.room is blocked
