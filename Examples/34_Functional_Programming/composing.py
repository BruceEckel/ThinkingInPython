# composing.py
from collections.abc import Callable

def compose(
    f: Callable[[int], int], g: Callable[[int], int]
) -> Callable[[int], int]:
    # Return a function that runs g, then feeds the result to f:
    def composed(x: int) -> int:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2

increment_then_double = compose(double, increment)
print(increment_then_double(10))
#: 22
