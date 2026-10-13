# partial_bisection.py
from functools import partial
from algorithms import bisection_tol, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = partial(bisection_tol, tolerance=0.1)
fine = partial(bisection_tol, tolerance=1e-9)
for finder in (coarse, fine):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.406250
#: 1.414214
