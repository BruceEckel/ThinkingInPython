# strategy.py
from collections.abc import Callable

type Line = list[float]

def least_squares(line: Line) -> float:
    # A flat least-squares fit minimizes squared error at the mean
    return sum(line) / len(line)

def newtons_method(line: Line) -> float:
    return min(line)

def bisection(line: Line) -> float:
    # Halve the interval: the midpoint of the value range
    return (min(line) + max(line)) / 2

def conjugate_gradient(line: Line) -> float:
    return max(line)

def solve(line: Line, strategy: Callable[[Line], float]) -> float:
    return strategy(line)

line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, least_squares))
#: 2.3333333333333335
print(solve(line, newtons_method))
#: -1.0
print(solve(line, bisection))
#: 2.0
print(solve(line, conjugate_gradient))
#: 5.0
