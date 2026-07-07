# exercise_2.py
import tracemalloc
from dataclasses import dataclass
from functools import cache
from typing import Final, Literal, cast

type Symbol = Literal[".", "~", "#"]
type TileSpec = tuple[str, bool]

@dataclass(frozen=True)
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
def cached_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def uncached_tile(symbol: Symbol) -> Tile:
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def to_symbol(char: str) -> Symbol:
    if char not in SPECS:
        raise KeyError(char)
    return cast(Symbol, char)

def make_map(size: int) -> str:
    row = "".join(".~#"[i % 3] for i in range(size))
    return "\n".join(row for _ in range(size))

for size in (50, 100, 200):
    text = make_map(size)
    tracemalloc.start()
    cached_field = [[cached_tile(to_symbol(s)) for s in line]
                    for line in text.split()]
    _, cached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    uncached_field = [[uncached_tile(to_symbol(s)) for s in line]
                       for line in text.split()]
    _, uncached_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ratio = round(uncached_peak / cached_peak, 1)
    print(size, "ratio uncached/cached:", ratio)
#: 50 ratio uncached/cached: 9.8
#: 100 ratio uncached/cached: 9.9
#: 200 ratio uncached/cached: 11.1
