# tile_map.py
from functools import cache
from typing import Final, Literal
from record import record

type Symbol = Literal[".", "~", "#"]
type TileSpec = tuple[str, bool]

@record
class Tile:
    symbol: Symbol
    name: str
    walkable: bool

    def label(self, row: int, col: int) -> str:
        return f"{self.name} at ({row}, {col})"

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@cache
def tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def to_symbol(char: str) -> Symbol:
    if char not in SPECS:
        raise KeyError(char)
    return char

def parse_map(text: str) -> list[list[Tile]]:
    return [[tile(to_symbol(char)) for char in line]
            for line in text.split()]
