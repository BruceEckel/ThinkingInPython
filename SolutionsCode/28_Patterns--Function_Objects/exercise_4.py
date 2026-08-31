# exercise_4.py
from collections.abc import Callable
from functools import partial

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

MAX_ITER = 200

def newton(f: Fn, a: float, b: float,
           tolerance: float = 1e-12) -> float | None:
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < tolerance:
            return x
    return None

def newton_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: float, b: float) -> float | None:
        return newton(f, a, b, tolerance)
    return finder

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None

def f(x: float) -> float:
    return x * x - 2

coarse_closure = newton_within(0.5)
coarse_partial: RootFinder = partial(newton, tolerance=0.5)
fine_closure = newton_within(1e-12)

for finder in (coarse_closure, coarse_partial,
               fine_closure):
    root = solve(f, 0.0, 2.0, [finder])
    assert root is not None
    print(f"{root:.6f}")
#: 1.500000
#: 1.500000
#: 1.414214
