# still_a_tuple.py
from dataclasses import dataclass
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Dimensions(NamedTuple):
    width: int
    height: int
    depth: int

print(Color(1, 2, 3) == Dimensions(1, 2, 3))
#: True
print(Color(1, 2, 3) == (1, 2, 3))
#: True
print(Color(1, 2, 3) < Dimensions(1, 2, 4))
#: True

@dataclass(frozen=True)
class FrozenColor:
    r: int
    g: int
    b: int

@dataclass(frozen=True)
class FrozenDimensions:
    width: int
    height: int
    depth: int

print(FrozenColor(1, 2, 3) == FrozenDimensions(1, 2, 3))
#: False
try:
    FrozenColor(1, 2, 3) < FrozenColor(1, 2, 4)  # type: ignore
except TypeError as e:
    print(str(e).partition(" and")[0])
#: '<' not supported between instances of 'FrozenColor'

@dataclass(frozen=True, order=True)
class OrderedColor:
    r: int
    g: int
    b: int

@dataclass(frozen=True, order=True)
class OrderedDimensions:
    width: int
    height: int
    depth: int

try:
    OrderedColor(1, 2, 3) < OrderedDimensions(1, 2, 4)  # type: ignore
except TypeError as e:
    print(str(e).partition(" and")[0])
#: '<' not supported between instances of 'OrderedColor'
