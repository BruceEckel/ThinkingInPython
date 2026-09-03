# tile_enum_match.py
from tile_enum import Tile

# ty: function can implicitly return `None`,
# not assignable to return type `str`
def describe(tile: Tile) -> str:  # type: ignore
    match tile:
        case Tile.GRASS:
            return "grass"
        case Tile.WATER:
            return "water"

if __name__ == "__main__":
    print(describe(Tile.GRASS))
#: grass
