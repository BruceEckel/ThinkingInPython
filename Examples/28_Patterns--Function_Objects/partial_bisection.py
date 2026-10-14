# partial_bisection.py
from functools import partial
from algorithms import bisection_tol, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for tolerance in (0.1, 1e-9):
    finder = partial(bisection_tol, tolerance=tolerance)
    root = solve(f, 0.0, 2.0, finder)
    print(f"tolerance {tolerance}: {root:.6f}")
#: tolerance 0.1: 1.406250
#: tolerance 1e-09: 1.414214
