# exercise_2.py
from collections.abc import Callable
from operator import mod

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b
def mul(a: int, b: int) -> int:
    return a * b
def floordiv(a: int, b: int) -> int:
    return a // b

operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "*": mul,
    "//": floordiv,
}
operations["%"] = mod
print(operations["+"](6, 4), operations["-"](6, 4),
      operations["*"](6, 4), operations["//"](6, 4),
      operations["%"](6, 4))
#: 10 2 24 1 2
try:
    operations["^"](6, 4)
except KeyError as e:
    print(repr(e))
#: KeyError('^')
