# strategy.py
# A strategy is a function you pass in. No class hierarchy, no
# Context object.
from collections.abc import Callable

type Line = list[float]

def least_squares(line: Line) -> float:
    # A flat least-squares fit minimizes squared error at the mean
    return sum(line) / len(line)

def bisection(line: Line) -> float:
    # Halve the interval: the midpoint of the value range
    return (min(line) + max(line)) / 2

def solve(line: Line, strategy: Callable[[Line], float]) -> float:
    return strategy(line)

line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, least_squares))
print(solve(line, bisection))
