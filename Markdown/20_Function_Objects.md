# Function Objects

In *Advanced C++: Programming Styles And Idioms* (Addison-Wesley, 1992), Jim
Coplien coins the term *functor*: an object whose sole purpose is to wrap a
function (since "functor" has a meaning in mathematics, this book uses the more
explicit term *function object*). The point is to decouple the choice of
function to call from the place where it is called.

That decoupling is the goal of several patterns: *Command*, *Strategy*, and
*Chain of Responsibility*. In a language where a function is not a value, you
need an object to carry the function around, so each of these patterns builds a
small class hierarchy whose only job is to hold one method.

In Python a function is already an object. You can name it, store it in a list,
pass it as an argument, and return it. So these three patterns largely dissolve:
where the *Design Patterns* book builds a hierarchy, Python uses a function. The
sections below show the function form first, then the classic object form for
contrast.

## Command: Choosing the Operation at Runtime

A *Command* wraps an action so you can pass it around and run it later. In
Python the action is just a function, and a "macro" is just a list of them:

```python
# command.py
# A function is already a command object; a macro is a list of them.
from collections.abc import Callable


def loony() -> None:
    print("You're a loony.")


def new_brain() -> None:
    print("You might even need a new brain.")


def afford() -> None:
    print("I couldn't afford a whole new brain.")


macro: list[Callable[[], None]] = [loony, new_brain, afford]
for command in macro:
    command()
```

The classic object form wraps each action in a `Command` subclass with an
`execute()` method:

```python
# command_pattern.py

class Command:
    def execute(self): pass

class Loony(Command):
    def execute(self):
        print("You're a loony.")

class NewBrain(Command):
    def execute(self):
        print("You might even need a new brain.")

class Afford(Command):
    def execute(self):
        print("I couldn't afford a whole new brain.")

# An object that holds commands:
class Macro:
    def __init__(self):
        self.commands = []
    def add(self, command):
        self.commands.append(command)
    def run(self):
        for c in self.commands:
            c.execute()

macro = Macro()
macro.add(Loony())
macro.add(NewBrain())
macro.add(Afford())
macro.run()
```

Both do the same thing. The class version is four classes and a wrapper to say
what one list of functions says directly. *Design Patterns* calls commands "an
object-oriented replacement for callbacks." In Python a callback is just a
function, so the replacement is unnecessary: the object form earns its keep only
when a command must also carry state or support extra operations such as undo.

## Strategy: Choosing the Algorithm at Runtime

A *Strategy* is an interchangeable algorithm chosen at run time. Again, the
algorithm is a function, and you pass it in:

```python
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
```

The classic form makes each algorithm a class deriving from a common interface,
and adds a "Context" object to hold the current strategy:

```python
# strategy_pattern.py

# The strategy interface:
class FindMinima:
    # Line is a sequence of points:
    def algorithm(self, line): pass

# The various strategies:
class LeastSquares(FindMinima):
    def algorithm(self, line):
        return [ 1.1, 2.2 ] # Dummy

class NewtonsMethod(FindMinima):
    def algorithm(self, line):
        return [ 3.3, 4.4 ]  # Dummy

class Bisection(FindMinima):
    def algorithm(self, line):
        return [ 5.5, 6.6 ] # Dummy

class ConjugateGradient(FindMinima):
    def algorithm(self, line):
        return [ 3.3, 4.4 ] # Dummy

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
```

You use strategies-as-functions constantly in Python without naming the pattern.
The `key` argument to `sorted()`, `min()`, and `max()` is a strategy: you hand
in a function that decides how to compare. The object form is worth it only when
a strategy needs its own configuration or several related methods.

## Chain of Responsibility

*Chain of Responsibility* tries a sequence of handlers until one succeeds. The
*Design Patterns* book implements the chain as a linked list, largely because it
predates standard list types. As that machinery is an implementation detail, in
Python the chain is just a list of functions, and the first one to produce a
result wins:

```python
# chain.py
# Try each handler in order; the first to return a result wins. The
# "chain" is an ordinary list of functions, not a hand-built linked
# list.
from collections.abc import Callable

Line = list[float]
Result = list[float] | None


def least_squares(line: Line) -> Result:
    return None  # this strategy did not find a solution


def newtons_method(line: Line) -> Result:
    return None  # neither did this one


def bisection(line: Line) -> Result:
    return [5.5, 6.6]  # success


def solve(line: Line,
          chain: list[Callable[[Line], Result]]) -> Result:
    for strategy in chain:
        result = strategy(line)
        if result is not None:
            return result
    return None


line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, [least_squares, newtons_method, bisection]))
```

Each handler is a *Strategy* function; the chain is the list; success is a
non-`None` return. There is no `ChainLink` class and no linked list to maintain.
Adding, removing, or reordering handlers is editing a list. This is the same
flexibility the pattern promises, with none of the scaffolding.

## Exercises

1.  Add an "undo" capability to `command.py`. What do the commands need to
    become, and is a function still enough, or do you now want an object?
2.  Rewrite `chain.py` so each handler also reports why it failed, and the
    solver prints every attempt before returning the winner.
3.  Use `sorted()` with a `key` function to sort a list of `(name, score)`
    tuples by score, then by name. Explain why `key` is the *Strategy* pattern.
