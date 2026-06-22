# Function Objects

In *Advanced C++: Programming Styles And Idioms* (Addison-Wesley, 1992),
Jim Coplien uses the term *functor*:
an object whose sole purpose is to wrap a function (since "functor" has a meaning in mathematics, this book uses the more explicit term *function object*).
The point is to decouple the choice of function to call from the place where it is called.

That decoupling is the goal of several patterns: *Command*, *Strategy*,
and *Chain of Responsibility*.
In a language where a function is not a value,
you need an object to carry the function around,
so each of these patterns builds a small class hierarchy whose only job is to hold one method.

In Python a function is already an object.
You can name it, store it in a list, pass it as an argument, and return it.
So these three patterns largely dissolve:
where the *Design Patterns* book builds a hierarchy, Python uses a function.
The sections below show the function form first,
then the classic object form for contrast.

## Command: Choosing the Operation at Runtime

A *Command* wraps an action so you can pass it around and run it later.
In Python the action is just a function, and a "macro" is just a list of them:

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

The classic object form wraps each action in a `Command` subclass with an `execute()` method:

```python
# command_pattern.py
from typing import override

class Command:
    def execute(self) -> None: pass

class Loony(Command):
    @override
    def execute(self) -> None:
        print("You're a loony.")

class NewBrain(Command):
    @override
    def execute(self) -> None:
        print("You might even need a new brain.")

class Afford(Command):
    @override
    def execute(self) -> None:
        print("I couldn't afford a whole new brain.")

# An object that holds commands:
class Macro:
    def __init__(self) -> None:
        self.commands: list[Command] = []
    def add(self, command: Command) -> None:
        self.commands.append(command)
    def run(self) -> None:
        for c in self.commands:
            c.execute()

macro = Macro()
macro.add(Loony())
macro.add(NewBrain())
macro.add(Afford())
macro.run()
```

Both do the same thing.
The class version is four classes and a wrapper to say what one list of functions says directly.
*Design Patterns* calls commands "an object-oriented replacement for callbacks."
In Python a callback is just a function, so the replacement is unnecessary:
the object form earns its keep only when a command must also carry state or support extra operations such as undo.

## Strategy: Choosing the Algorithm at Runtime

A *Strategy* is an interchangeable algorithm chosen at run time.
Again, the algorithm is a function, and you pass it in:

```python
# strategy.py
# A strategy is a function you pass in. No class hierarchy, no
# Context object.
from collections.abc import Callable

type Line = list[float]

def least_squares(line: Line) -> float:
    # A flat least-squares fit minimizes squared error at the mean.
    return sum(line) / len(line)

def bisection(line: Line) -> float:
    # Halve the interval: the midpoint of the value range.
    return (min(line) + max(line)) / 2

def solve(line: Line, strategy: Callable[[Line], float]) -> float:
    return strategy(line)

line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
print(solve(line, least_squares))
print(solve(line, bisection))
```

The classic form makes each algorithm a class deriving from a common interface,
and adds a "Context" object to hold the current strategy:

```python
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
solver.change_algorithm(Bisection())
print(solver.minima(line))
```

You use strategies-as-functions constantly in Python without naming the pattern.
The `key` argument to `sorted()`, `min()`, and `max()` is a strategy:
you hand in a function that decides how to compare.
The object form is worth it only when a strategy needs its own configuration or several related methods.

## Chain of Responsibility

*Chain of Responsibility* tries a sequence of handlers until one succeeds.
The *Design Patterns* book implements the chain as a linked list,
largely because it predates standard list types.
As that machinery is an implementation detail,
in Python the chain is just a list of functions,
and the first one to produce a result wins:

```python
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
```

Each handler is a *Strategy* function; the chain is the list;
success is a non-`None` return.
There is no `ChainLink` class and no linked list to maintain.
Adding, removing, or reordering handlers is editing a list.
This is the same flexibility the pattern promises, with none of the scaffolding.

The control flow is what to test: the first handler that returns a result wins,
order decides the winner, and an exhausted or empty chain returns `None`:

```python
# test_chain.py
from chain import (
    Line,
    Result,
    bisection,
    least_squares,
    newtons_method,
    solve,
)

def test_first_successful_handler_wins() -> None:
    assert solve(
        [1.0, 2.0, 3.0],
        [least_squares, newtons_method, bisection],
    ) == [5.5, 6.6]  # Bisection

def test_order_decides_the_winner() -> None:
    def always(line: Line) -> Result:
        return [1.0]

    # 'always' precedes bisection, so it short-circuits the chain.
    assert solve([0.0], [always, bisection]) == [1.0]

def test_no_handler_succeeds_returns_none() -> None:
    assert solve([0.0], [least_squares, newtons_method]) is None

def test_empty_chain_returns_none() -> None:
    assert solve([0.0], []) is None
```

## An Event Bus: Handlers Keyed by Type

Chain of Responsibility kept its handlers in a list and tried them in order.
Key that structure by type instead of by position and you have an *event bus*:
a `dict` from each event type to the functions that care about it.
The events are plain values,
written as frozen data classes (see the [Data Classes as Types](10_Data_Classes_as_Types.md) chapter).
Publishing an event looks up its type and calls every handler registered for it.
The handlers are ordinary functions,
so there is no `Handler` interface to implement and no registration ceremony:

```python
# event_bus.py
# An event bus is a dict from each event type to the functions that
# care about it. Events are values; handlers are plain functions.
# Publishing an event calls every handler for that event's type.
# No Handler base class, and no registration ceremony.
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Deposit:
    amount: int

@dataclass(frozen=True)
class Withdraw:
    amount: int

@dataclass(frozen=True)
class Closed:
    reason: str

class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = {}

    def subscribe[E](self, event_type: type[E],
                     handler: Callable[[E], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: object) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

def on_deposit(event: Deposit) -> None:
    print(f"+ deposit {event.amount}")

def audit(event: Deposit) -> None:
    print(f"  audit: a deposit of {event.amount}")

def on_withdraw(event: Withdraw) -> None:
    print(f"- withdraw {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
bus.subscribe(Deposit, audit)        # Two handlers for one event type
bus.subscribe(Withdraw, on_withdraw)

bus.publish(Deposit(100))
bus.publish(Withdraw(30))
bus.publish(Closed("inactivity"))    # No handler: nothing happens
```

As with the chain, the behavior is what to test:
every handler registered for a type is called,
a handler hears only its own event type,
and an event with no handler is a quiet no-op:

```python
# test_event_bus.py
from event_bus import Closed, Deposit, EventBus, Withdraw

def test_every_handler_for_the_type_is_called() -> None:
    seen: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit, lambda e: seen.append(f"a{e.amount}"))
    bus.subscribe(Deposit, lambda e: seen.append(f"b{e.amount}"))
    bus.publish(Deposit(5))
    assert seen == ["a5", "b5"]

def test_only_the_matching_type_is_called() -> None:
    calls: list[str] = []
    bus = EventBus()
    bus.subscribe(Deposit, lambda e: calls.append("deposit"))
    bus.subscribe(Withdraw, lambda e: calls.append("withdraw"))
    bus.publish(Withdraw(1))
    assert calls == ["withdraw"]

def test_no_handler_is_a_noop() -> None:
    EventBus().publish(Closed("done"))  # Must not raise
```

This is the *Observer* pattern (see the [Observer](27_Observer.md) chapter) narrowed to a single subject:
the subscribers are functions,
and the bus routes each event to them by its type.
Here a type may have many handlers.
When instead you want exactly one handler per type,
chosen by the argument's type and open to new types without editing a central function,
that is `functools.singledispatch`,
which the [Visitor](29_Visitor.md) and [Pattern Refactoring](30_Pattern_Refactoring.md) chapters put to work.

## Exercises

1.  Add an "undo" capability to `command.py`.
    What do the commands need to become, and is a function still enough,
    or do you now want an object?
2.  Rewrite `chain.py` so each handler also reports why it failed,
    and the solver prints every attempt before returning the winner.
3.  Use `sorted()` with a `key` function to sort a list of `(name, score)` tuples by score,
    then by name.
    Explain why `key` is the *Strategy* pattern.
