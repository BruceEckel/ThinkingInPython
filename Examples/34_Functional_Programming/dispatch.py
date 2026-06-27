# dispatch.py
from collections.abc import Callable

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b

# A table of functions replaces a long if/elif chain:
operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
}
print(operations["+"](6, 4), operations["-"](6, 4))
## 10 2
