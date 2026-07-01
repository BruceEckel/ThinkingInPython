# strategy.py
from algorithms import Fn, RootFinder, bisection, newton, secant

def solve(f: Fn, a: float, b: float,
          finder: RootFinder) -> float | None:
    return finder(f, a, b)

def f(x: float) -> float:
    return x * x - 2   # Root at the square root of 2

for finder in (bisection, newton, secant):
    root = solve(f, 0.0, 2.0, finder)
    assert root is not None
    print(f"{root:.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
