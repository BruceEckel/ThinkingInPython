# strategy_pattern.py

# The strategy interface:
class FindMinima:
    # Line is a sequence of points:
    def algorithm(self, line): pass

# The various strategies:
class LeastSquares(FindMinima):
    def algorithm(self, line):
        return sum(line) / len(line)  # mean

class NewtonsMethod(FindMinima):
    def algorithm(self, line):
        return min(line)

class Bisection(FindMinima):
    def algorithm(self, line):
        return (min(line) + max(line)) / 2  # midpoint

class ConjugateGradient(FindMinima):
    def algorithm(self, line):
        return max(line)

# The "Context" controls the strategy:
class MinimaSolver:
    def __init__(self, strategy):
        self.strategy = strategy

    def minima(self, line):
        return self.strategy.algorithm(line)

    def change_algorithm(self, new_algorithm):
        self.strategy = new_algorithm

solver = MinimaSolver(LeastSquares())
line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solver.minima(line))
solver.change_algorithm(Bisection())
print(solver.minima(line))
