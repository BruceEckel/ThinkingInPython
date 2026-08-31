# shop.py
from dataclasses import dataclass

@dataclass(frozen=True)
class _A:
    x: object

@dataclass(frozen=True)
class _B:
    x: object

def make_a(x: object) -> _A:
    return _A(x)

def make_b(x: object) -> _B:
    return _B(x)
