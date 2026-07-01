# chain.py
# Try each root finder in order; the first to converge wins. A method
# that cannot find a root returns None, so the chain moves on.
from algorithms import Fn, RootFinder, bisection, newton, secant

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None

def f(x: float) -> float:
    return x * x - 2   # Root at the square root of 2

chain: list[RootFinder] = [bisection, secant, newton]
# [0, 2] brackets the root, so bisection succeeds first:
r1 = solve(f, 0.0, 2.0, chain)
print(f"{r1:.6f}" if r1 is not None else "no root")
#: 1.414214
# [1.0, 1.3] does not bracket it; bisection fails, secant finds it:
r2 = solve(f, 1.0, 1.3, chain)
print(f"{r2:.6f}" if r2 is not None else "no root")
#: 1.414214
