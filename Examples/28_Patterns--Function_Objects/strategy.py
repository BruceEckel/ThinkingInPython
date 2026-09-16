# strategy.py
from algorithms import bisection, newton, secant, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for finder in (bisection, newton, secant):
    print(f"{solve(f, 0.0, 2.0, finder):.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
