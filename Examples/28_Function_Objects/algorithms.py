# algorithms.py
from collections.abc import Callable
from typing import Final

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200

def bisection(f: Fn, a: float, b: float) -> float | None:
    if f(a) * f(b) > 0:  # Endpoints must bracket a root
        return None
    for _ in range(MAX_ITER):
        mid = (a + b) / 2
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
    return mid

def secant(f: Fn, a: float, b: float) -> float | None:
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:  # Flat step: cannot continue
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f: Fn, a: float, b: float) -> float | None:
    x = (a + b) / 2  # Start between the hints
    h = 1e-7
    for _ in range(MAX_ITER):
        # Approximate the derivative with a central difference:
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None
