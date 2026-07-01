# strategy_pattern.py
from typing import override

# The strategy interface:
class FindMinima:
    # Line is a sequence of points:
    def algorithm(self, line: list[float]) -> float:
        raise NotImplementedError

# The various strategies:
class LeastSquares(FindMinima):
    @override
    def algorithm(self, line: list[float]) -> float:
        return sum(line) / len(line)  # Mean

class NewtonsMethod(FindMinima):
    @override
    def algorithm(self, line: list[float]) -> float:
        return min(line)

class Bisection(FindMinima):
    @override
    def algorithm(self, line: list[float]) -> float:
        return (min(line) + max(line)) / 2  # Midpoint

class ConjugateGradient(FindMinima):
    @override
    def algorithm(self, line: list[float]) -> float:
        return max(line)

# The "Context" controls the strategy:
class MinimaSolver:
    def __init__(self, strategy: FindMinima) -> None:
        self.strategy = strategy

    def minima(self, line: list[float]) -> float:
        return self.strategy.algorithm(line)

    def change_algorithm(self, new_algorithm: FindMinima) -> None:
        self.strategy = new_algorithm

solver = MinimaSolver(LeastSquares())
line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solver.minima(line))
#: 2.3333333333333335
solver.change_algorithm(NewtonsMethod())
print(solver.minima(line))
#: -1.0
solver.change_algorithm(Bisection())
print(solver.minima(line))
#: 2.0
solver.change_algorithm(ConjugateGradient())
print(solver.minima(line))
#: 5.0
