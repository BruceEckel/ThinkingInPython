# tile_map.py
from dataclasses import dataclass
from functools import cache
from typing import Final

@dataclass(frozen=True)
class Tile:
    symbol: str
    name: str
    walkable: bool

SPECS: Final[dict[str, tuple[str, bool]]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@cache
def tile(symbol: str) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def parse_map(text: str) -> list[list[Tile]]:
    return [[tile(s) for s in line]
            for line in text.split()]

if __name__ == "__main__":
    field = parse_map("""
        ..~~..
        ..~~.#
        ......
        ##..~~
    """)
    cells = [t for row in field for t in row]
    print(len(cells), len({id(t) for t in cells}))
    print(field[0][2] is field[3][5])
#: 24 3
#: True
