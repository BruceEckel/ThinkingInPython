# FunctionObjects/ChainOfResponsibility.py
from __future__ import annotations

from typing import Any


# Carry the information into the strategy:
class Messenger: pass

# The Result object carries the result data and
# whether the strategy was successful:
class Result:
    def __init__(self) -> None:
        self.succeeded = 0
    def isSuccessful(self) -> int:
        return self.succeeded
    def setSuccessful(self, succeeded: int) -> None:
        self.succeeded = succeeded

class Strategy:
    def __call__(self, messenger: Any) -> Any: ...
    def __str__(self) -> str:
        return "Trying " + self.__class__.__name__ + " algorithm"

# Manage the movement through the chain and
# find a successful result:
class ChainLink:
    def __init__(self, chain: list[ChainLink], strategy: Strategy) -> None:
        self.strategy = strategy
        self.chain = chain
        self.chain.append(self)

    def next(self) -> ChainLink | None:
        # Where this link is in the chain:
        location = self.chain.index(self)
        if not self.end():
            return self.chain[location + 1]
        return None

    def end(self) -> bool:
        return self.chain.index(self) + 1 >= len(self.chain)

    def __call__(self, messenger: Any) -> Any:
        r = self.strategy(messenger)
        if r.isSuccessful() or self.end():
            return r
        nxt = self.next()
        assert nxt is not None
        return nxt(messenger)

# For this example, the Messenger
# and Result can be the same type:
class LineData(Result, Messenger):
    def __init__(self, data: Any) -> None:
        self.data = data
    def __str__(self) -> str:
        return repr(self.data)

class LeastSquares(Strategy):
    def __call__(self, messenger: Any) -> Any:
        print(self)
        # [ Actual test/calculation here ]
        result = LineData([1.1, 2.2])  # Dummy data
        result.setSuccessful(0)
        return result

class NewtonsMethod(Strategy):
    def __call__(self, messenger: Any) -> Any:
        print(self)
        # [ Actual test/calculation here ]
        result = LineData([3.3, 4.4])  # Dummy data
        result.setSuccessful(0)
        return result

class Bisection(Strategy):
    def __call__(self, messenger: Any) -> Any:
        print(self)
        # [ Actual test/calculation here ]
        result = LineData([5.5, 6.6])  # Dummy data
        result.setSuccessful(1)
        return result

class ConjugateGradient(Strategy):
    def __call__(self, messenger: Any) -> Any:
        print(self)
        # [ Actual test/calculation here ]
        result = LineData([7.7, 8.8])  # Dummy data
        result.setSuccessful(1)
        return result

solutions: list[ChainLink] = []
ChainLink(solutions, LeastSquares())
ChainLink(solutions, NewtonsMethod())
ChainLink(solutions, Bisection())
ChainLink(solutions, ConjugateGradient())

line = LineData([
  1.0, 2.0, 1.0, 2.0, -1.0,
  3.0, 4.0, 5.0, 4.0
])

print(solutions[0](line))
