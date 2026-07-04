# strategy_pattern.py
from typing import override
from algorithms import Fn, bisection, newton, secant

# The strategy interface:
class FindRoot:
    def find(self, f: Fn, a: float, b: float) -> float | None:
        raise NotImplementedError

# Each strategy wraps one algorithm from algorithms.py:
class Bisection(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return bisection(f, a, b)

class Newton(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return newton(f, a, b)

class Secant(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return secant(f, a, b)

# The "Context" controls the strategy:
class RootSolver:
    def __init__(self, strategy: FindRoot) -> None:
        self.strategy = strategy

    def solve(self, f: Fn, a: float, b: float) -> float | None:
        return self.strategy.find(f, a, b)

    def change_algorithm(self, new_algorithm: FindRoot) -> None:
        self.strategy = new_algorithm

def f(x: float) -> float:
    return x * x - 2

solver = RootSolver(Bisection())
for algorithm in (Bisection(), Newton(), Secant()):
    solver.change_algorithm(algorithm)
    root = solver.solve(f, 0.0, 2.0)
    assert root is not None
    print(f"{root:.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
