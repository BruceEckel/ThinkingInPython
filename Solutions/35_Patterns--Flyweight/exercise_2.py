# exercise_2.py
import tracemalloc
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

SPECS: Final[dict[Symbol, TileSpec]] = {
    ".": ("grass", True),
    "~": ("water", False),
    "#": ("rock", False),
}

@cache
def shared_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def unshared_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def to_symbol(char: str) -> Symbol:
    if char not in SPECS:
        raise KeyError(char)
    return char

def make_map(size: int) -> str:
    row = "".join(".~#"[i % 3] for i in range(size))
    return "\n".join(row for _ in range(size))

for size in (50, 100, 200):
    text = make_map(size)
    tracemalloc.start()
    shared_field = [[shared_tile(to_symbol(s))
                     for s in line]
                    for line in text.split()]
    _, shared_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    unshared_field = [[unshared_tile(to_symbol(s))
                       for s in line]
                      for line in text.split()]
    _, unshared_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ratio = round(unshared_peak / shared_peak, 1)
    print(size, "ratio unshared/shared:", ratio)
#: 50 ratio unshared/shared: 6.2
#: 100 ratio unshared/shared: 6.2
#: 200 ratio unshared/shared: 6.9
