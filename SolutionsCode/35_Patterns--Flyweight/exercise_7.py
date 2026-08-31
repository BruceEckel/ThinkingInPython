# exercise_7.py
from enum import Enum

class Tile(Enum):
    GRASS = (".", True)
    WATER = ("~", False)
    ROCK = ("#", False)

    walkable: bool

    def __new__(cls, symbol: str, walkable: bool) -> Tile:
        member = object.__new__(cls)
        member._value_ = symbol
        member.walkable = walkable
        return member

def parse_map(text: str) -> list[list[Tile]]:
    return [[Tile(s) for s in line]
            for line in text.split()]

field = parse_map("""
    ..~~..
    ..~~.#
    ......
    ##..~~
""")
cells = [*row for row in field]
print(len(cells), len({id(t) for t in cells}))
#: 24 3
print(field[0][2] is field[3][5], field[0][2].walkable)
#: True False
try:
    parse_map("?")
except ValueError as e:
    print(type(e).__name__, e)
#: ValueError '?' is not a valid Tile
