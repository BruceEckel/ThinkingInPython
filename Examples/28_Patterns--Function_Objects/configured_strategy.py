# configured_strategy.py
from algorithms import Fn, RootFinder

def bisection_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: float, b: float) -> float | None:
        if f(a) * f(b) > 0:  # Endpoints must bracket a root
            return None
        while abs(b - a) > tolerance:
            mid = (a + b) / 2
            if f(a) * f(mid) <= 0:
                b = mid
            else:
                a = mid
        return (a + b) / 2
    return finder

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

coarse = bisection_within(0.1)
fine = bisection_within(1e-9)
r1, r2 = coarse(f, 0.0, 2.0), fine(f, 0.0, 2.0)
assert r1 is not None and r2 is not None
print(f"{r1:.6f} {r2:.6f}")
#: 1.406250 1.414214
