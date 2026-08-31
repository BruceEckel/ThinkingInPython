# tile_enum.py
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

if __name__ == "__main__":
    print(Tile.GRASS is Tile["GRASS"] is Tile("."))
    print(Tile.WATER.value, Tile.WATER.walkable)
    print([t.value for t in Tile])
#: True
#: ~ False
#: ['.', '~', '#']
