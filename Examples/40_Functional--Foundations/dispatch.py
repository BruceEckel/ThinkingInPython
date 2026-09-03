# dispatch.py
from collections.abc import Callable
from operator import mod
from exceptions import ignore

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b
def floordiv(a: int, b: int) -> int:
    return a // b

# A table of functions replaces a long if/elif chain:
operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "//": floordiv,
}
# A row can come from outside the literal, unchanged:
operations["%"] = mod
print(operations["+"](6, 4), operations["-"](6, 4),
      operations["//"](6, 4), operations["%"](6, 4))
#: 10 2 1 2
# A missing key is a plain KeyError, no else branch:
with ignore(KeyError):
    operations["^"](6, 4)
#: KeyError('^')
