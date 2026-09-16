# strategy.py
from algorithms import (Fn, RootFinder, bisection,
                        newton, secant)

def solve(f: Fn, a: float, b: float,
          finder: RootFinder) -> float:
    root = finder(f, a, b)
    if root is None or abs(f(root)) > 1e-6:
        raise ValueError(f"no root in [{a}, {b}]")
    return root

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for finder in (bisection, newton, secant):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
