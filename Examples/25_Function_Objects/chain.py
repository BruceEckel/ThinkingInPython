# chain.py
# Try each handler in order; the first to return a result wins. The
# "chain" is an ordinary list of functions, not a hand-built linked
# list.
from collections.abc import Callable

type Line = list[float]
type Result = list[float] | None

def least_squares(line: Line) -> Result:
    return None  # This strategy did not find a solution

def newtons_method(line: Line) -> Result:
    return None  # Neither did this one

def bisection(line: Line) -> Result:
    return [5.5, 6.6]  # Success

def solve(line: Line,
          chain: list[Callable[[Line], Result]]) -> Result:
    for strategy in chain:
        result = strategy(line)
        if result is not None:
            return result
    return None

line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, [least_squares, newtons_method, bisection]))
