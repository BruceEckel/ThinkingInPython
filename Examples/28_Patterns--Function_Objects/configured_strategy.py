# configured_strategy.py
from algorithms import Fn, RootFinder, bisection_tol, solve

def bisection_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: float, b: float) -> float | None:
        return bisection_tol(f, a, b, tolerance)
    return finder

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = bisection_within(0.1)
fine = bisection_within(1e-9)
for finder in (coarse, fine):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.406250
#: 1.414214
