# exercise_2.py
from collections.abc import Callable
from typing import Final, Protocol
from record import record

type Fn = Callable[[float], float]

@record
class Failed:
    reason: str

class Finder(Protocol):
    __name__: str
    def __call__(self, f: Fn, a: float,
                 b: float) -> float | Failed: ...

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200
NO_CONVERGENCE: Final[Failed] = Failed(
    f"no convergence in {MAX_ITER} steps")

def bisection(f: Fn, a: float, b: float) -> float | Failed:
    if f(a) * f(b) > 0:
        return Failed(f"no root bracketed by [{a}, {b}]")
    for _ in range(MAX_ITER):
        mid = (a + b) / 2
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return NO_CONVERGENCE

def secant(f: Fn, a: float, b: float) -> float | Failed:
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            return Failed(f"flat step at {x1}")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return NO_CONVERGENCE

def newton(f: Fn, a: float, b: float) -> float | Failed:
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return Failed(f"zero slope at {x}")
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return NO_CONVERGENCE

def solve(f: Fn, a: float, b: float,
          chain: list[Finder]) -> float | None:
    for finder in chain:
        match finder(f, a, b):
            case Failed(reason):
                print(f"{finder.__name__}: {reason}")
            case root:
                print(f"{finder.__name__}: {root:.6f}")
                return root
    print("every finder failed")
    return None

def f(x: float) -> float:
    return x * x - 2

solve(f, 1.0, 1.3, [bisection, secant, newton])
#: bisection: no root bracketed by [1.0, 1.3]
#: secant: 1.414214

def g(x: float) -> float:
    return x * x + 1  # No real root

solve(g, 0.0, 2.0, [bisection])
#: bisection: no root bracketed by [0.0, 2.0]
#: every finder failed
