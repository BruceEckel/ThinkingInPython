# exercise_8.py
import threading
import time
from collections.abc import Callable
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
    "^": ("hill", True),
    "*": ("sand", True),
}

@cache
def tile(symbol: str) -> Tile:
    time.sleep(0.1)  # Widen the window between miss and store
    name, walkable = SPECS[symbol]
    return Tile(symbol, name, walkable)

def gather(
    factory: Callable[[str], Tile], symbol: str
) -> list[Tile]:
    "Call factory(symbol) from four threads at once."
    out: list[Tile] = []
    lock = threading.Lock()

    def worker() -> None:
        found = factory(symbol)
        with lock:
            out.append(found)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return out

raced = gather(tile, "^")
print(len(raced), len({id(t) for t in raced}))
#: 4 4

EAGER: Final[dict[str, Tile]] = {
    s: Tile(s, *spec) for s, spec in SPECS.items()}

def eager_tile(symbol: str) -> Tile:
    return EAGER[symbol]

print(len({id(t) for t in gather(eager_tile, "*")}))
#: 1

guard = threading.Lock()

def locked_tile(symbol: str) -> Tile:
    with guard:
        return tile(symbol)

print(len({id(t) for t in gather(locked_tile, "~")}))
#: 1
