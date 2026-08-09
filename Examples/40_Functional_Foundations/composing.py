# composing.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    # Return a function that runs g, then feeds the result to f:
    def composed(x: T) -> V:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2
def label(n: int) -> str:
    return f"<{n}>"

increment_then_double = compose(double, increment)
print(increment_then_double(10))
#: 22
print(compose(label, increment_then_double)(10))
#: <22>
