# chain_demo.py
from algorithms import (Root, RootFinder, bisection,
                        newton, secant)
from chain import first_root

def f(x: float) -> float:
    return x * x - 2  # Root at the square root of 2

def show(root: Root | None) -> str:
    return "None" if root is None else f"{root:.6f}"

chain: list[RootFinder] = [bisection, secant, newton]
for a, b in ((0.0, 2.0), (1.0, 1.3)):
    alone = show(bisection(f, a, b))
    first = show(first_root(f, a, b, chain))
    print(f"[{a}, {b}] bisection: {alone}, chain: {first}")
#: [0.0, 2.0] bisection: 1.414214, chain: 1.414214
#: [1.0, 1.3] bisection: None, chain: 1.414214
