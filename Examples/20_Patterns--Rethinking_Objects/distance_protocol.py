# distance_protocol.py
from math import sqrt
from typing import Protocol
from record import record

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

@record
class Point:
    x: float
    y: float

@record
class Pair:  # Suppose you are handed this, with no x or y
    a: float
    b: float

@record
# Adapter: uses composition, not inheritance
class PairCoord:
    pair: Pair

    @property
    def x(self) -> float:
        return self.pair.a

    @property
    def y(self) -> float:
        return self.pair.b

if __name__ == "__main__":
    print(distance(Point(3, 0), Point(0, 4)))
    print(distance(PairCoord(Pair(3, 0)),
                   PairCoord(Pair(0, 4))))
#: 5.0
#: 5.0
