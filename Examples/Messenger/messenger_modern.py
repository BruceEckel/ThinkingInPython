# Messenger/messenger_modern.py
# The standard library already provides this idiom and its typed cousins.
from dataclasses import dataclass
from types import SimpleNamespace
from typing import NamedTuple


# SimpleNamespace is exactly the Messenger idiom, built in:
m = SimpleNamespace(info="some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)


# A dataclass is the typed, mutable version:
@dataclass
class Point:
    x: float
    y: float


print(Point(1.0, 2.0))


# A NamedTuple is the typed, immutable version:
class Color(NamedTuple):
    r: int
    g: int
    b: int


print(Color(255, 0, 0).r)
