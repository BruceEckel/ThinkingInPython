# strategy.py
# A strategy is a function you pass in. No class hierarchy, no
# Context object.
from collections.abc import Callable

Line = list[float]
Minima = list[float]


def least_squares(line: Line) -> Minima:
    return [1.1, 2.2]  # dummy result


def bisection(line: Line) -> Minima:
    return [5.5, 6.6]  # dummy result


def solve(line: Line, strategy: Callable[[Line], Minima]) -> Minima:
    return strategy(line)


line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, least_squares))
print(solve(line, bisection))
