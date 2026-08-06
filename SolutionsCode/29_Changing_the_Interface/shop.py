# shop.py
from dataclasses import dataclass

@dataclass
class _A:
    x: object

@dataclass
class _B:
    x: object

def make_a(x: object) -> _A:
    return _A(x)

def make_b(x: object) -> _B:
    return _B(x)
