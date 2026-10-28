# configured_strategy.py
from algorithms import (Fn, Hint, Root, RootFinder,
                        bisection_tol, solve)

def bisection_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: Hint, b: Hint) -> Root | None:
        return bisection_tol(f, a, b, tolerance)
    return finder

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for tolerance in (0.1, 1e-9):
    finder = bisection_within(tolerance)
    root = solve(f, 0.0, 2.0, finder)
    print(f"tolerance {tolerance}: {root:.6f}")
#: tolerance 0.1: 1.406250
#: tolerance 1e-09: 1.414214
