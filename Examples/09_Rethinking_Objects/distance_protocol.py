# distance_protocol.py
# The free function generalizes to anything with x and y, described
# by a Protocol. That is the structural typing from the Static Type
# Checking chapter. A class that lacks x and y can be adapted by
# composition, with no inheritance.
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Protocol


class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...


def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Pair:  # Suppose you are handed this, with no x or y.
    a: float
    b: float


@dataclass(frozen=True)
class PairCoord:  # An adapter built by composition, not inheritance.
    pair: Pair

    @property
    def x(self) -> float:
        return self.pair.a

    @property
    def y(self) -> float:
        return self.pair.b


if __name__ == "__main__":
    print(distance(Point(3, 0), Point(0, 4)))
    print(distance(PairCoord(Pair(3, 0)), PairCoord(Pair(0, 4))))
