# strategy.py
from algorithms import bisection, newton, secant, solve

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

for finder in (bisection, newton, secant):
    root = solve(f, 0.0, 2.0, finder)
    print(f"{finder.__name__}: {root:.6f}")
#: bisection: 1.414214
#: newton: 1.414214
#: secant: 1.414214
