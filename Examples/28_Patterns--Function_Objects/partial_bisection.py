# partial_bisection.py
from functools import partial
from algorithms import Fn

def bisection_tol(f: Fn, a: float, b: float,
                   tolerance: float) -> float | None:
    while abs(b - a) > tolerance:
        mid = (a + b) / 2
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = partial(bisection_tol, tolerance=0.1)
fine = partial(bisection_tol, tolerance=1e-9)
print(f"{coarse(f, 0.0, 2.0):.6f}")
#: 1.406250
print(f"{fine(f, 0.0, 2.0):.6f}")
#: 1.414214
