# functionObjects/ChainOfResponsibility.py

# Carry the information into the strategy:
class Messenger: pass

# The Result object carries the result data and
# whether the strategy was successful:
class Result:
    def __init__(self):
        self.succeeded = 0
    def isSuccessful(self):
        return self.succeeded
    def setSuccessful(self, succeeded):
        self.succeeded = succeeded

class Strategy:
    def __call__(messenger): pass
    def __str__(self):
        return "Trying " + self.__class__.__name__ \
          + " algorithm"

# Manage the movement through the chain and
# find a successful result:
class ChainLink:
    def __init__(self, chain, strategy):
        self.strategy = strategy
        self.chain = chain
        self.chain.append(self)

    def next(self):
        # Where this link is in the chain:
        location = self.chain.index(self)
        if not self.end():
            return self.chain[location + 1]

    def end(self):
        return (self.chain.index(self) + 1 >=
                len(self.chain))

    def __call__(self, messenger):
        r = self.strategy(messenger)
        if r.isSuccessful() or self.end(): return r
        return self.next()(messenger)

# For this example, the Messenger
# and Result can be the same type:
class LineData(Result, Messenger):
    def __init__(self, data):
        self.data = data
    def __str__(self): return `self.data`

class LeastSquares(Strategy):
    def __call__(self, messenger):
        print(self)
        linedata = messenger
        # [ Actual test/calculation here ]
        result = LineData([1.1, 2.2]) # Dummy data
        result.setSuccessful(0)
        return result

class NewtonsMethod(Strategy):
    def __call__(self, messenger):
        print(self)
        linedata = messenger
        # [ Actual test/calculation here ]
        result = LineData([3.3, 4.4]) # Dummy data
        result.setSuccessful(0)
        return result

class Bisection(Strategy):
    def __call__(self, messenger):
        print(self)
        linedata = messenger
        # [ Actual test/calculation here ]
        result = LineData([5.5, 6.6]) # Dummy data
        result.setSuccessful(1)
        return result

class ConjugateGradient(Strategy):
    def __call__(self, messenger):
        print(self)
        linedata = messenger
        # [ Actual test/calculation here ]
        result = LineData([7.7, 8.8]) # Dummy data
        result.setSuccessful(1)
        return result

solutions = []
ChainLink(solutions, LeastSquares()),
ChainLink(solutions, NewtonsMethod()),
ChainLink(solutions, Bisection()),
ChainLink(solutions, ConjugateGradient())

line = LineData([
  1.0, 2.0, 1.0, 2.0, -1.0,
  3.0, 4.0, 5.0, 4.0
])

print(solutions[0](line))