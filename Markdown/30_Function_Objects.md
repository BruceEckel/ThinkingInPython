# Function Objects

A *function object* decouples the choice of function to call from the place that calls it.
That decoupling is the goal of several patterns: *Command*, *Strategy*,
and *Chain of Responsibility*.

In Python a function is already an object.
You can name it, store it in a list, pass it as an argument, and return it.
So these three patterns are largely unnecessary in Python.
Where *GoF Design Patterns* builds a hierarchy, Python uses a function.
The sections below show the function form first,
then the classic object form for contrast.

## Command: Choosing the Operation at Runtime

A *Command* wraps an action so you can pass it around and run it later.
In Python the action is just a function, and a "macro" is just a list of actions:

```python
# command.py
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
#: You're a loony.
#: You might even need a new brain.
#: I couldn't afford a whole new brain.
```

The classic object form wraps each action in a `Command` subclass with an `execute()` method:

```python
# command_pattern.py
from typing import override

class Command:
    def execute(self) -> None: ...

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
#: You're a loony.
#: You might even need a new brain.
#: I couldn't afford a whole new brain.
```

Both do the same thing.
The class version is four classes and a wrapper to say what one list of functions says directly.
*GoF Design Patterns* calls commands "an object-oriented replacement for callbacks."
In Python a callback is just a function, so the replacement is unnecessary.
The object form earns its keep only when a command must also carry state or support extra operations such as undo.

## Strategy: Choosing the Algorithm at Runtime

A *Strategy* is an interchangeable algorithm chosen at runtime.
For the following examples we will use three real algorithms that find a *root* of a
function `f`, a value where `f(x)` is zero.
Each takes the function and two hints and returns the root,
or `None` when it cannot find one.
The hints are a bracket for bisection and two starting points for the open methods.
They share one signature, so they are interchangeable:

```python
# algorithms.py
from collections.abc import Callable
from typing import Final

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200

def bisection(f: Fn, a: float, b: float) -> float | None:
    if f(a) * f(b) > 0:   # Endpoints must bracket a root
        return None
    for _ in range(MAX_ITER):
        mid = (a + b) / 2
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
    return mid

def secant(f: Fn, a: float, b: float) -> float | None:
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:   # Flat step: cannot continue
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f: Fn, a: float, b: float) -> float | None:
    x = (a + b) / 2   # Start between the hints
    h = 1e-7
    for _ in range(MAX_ITER):
        # Approximate the derivative with a central difference:
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None
```

Because each finder is a function with the same signature,
you achieve a *Strategy* by stepping through the algorithms:

```python
# strategy.py
from algorithms import Fn, RootFinder, bisection, newton, secant

def solve(f: Fn, a: float, b: float,
          finder: RootFinder) -> float | None:
    return finder(f, a, b)

def f(x: float) -> float:
    return x * x - 2   # Root at the square root of 2

for finder in (bisection, newton, secant):
    root = solve(f, 0.0, 2.0, finder)
    assert root is not None
    print(f"{root:.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
```

The classic form makes each algorithm a class deriving from a common interface,
and adds a "Context" object to hold the current strategy:

```python
# strategy_pattern.py
from typing import override
from algorithms import Fn, bisection, newton, secant

# The strategy interface:
class FindRoot:
    def find(self, f: Fn, a: float, b: float) -> float | None:
        raise NotImplementedError

# Each strategy wraps one algorithm from algorithms.py:
class Bisection(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return bisection(f, a, b)

class Newton(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return newton(f, a, b)

class Secant(FindRoot):
    @override
    def find(self, f: Fn, a: float, b: float) -> float | None:
        return secant(f, a, b)

# The "Context" controls the strategy:
class RootSolver:
    def __init__(self, strategy: FindRoot) -> None:
        self.strategy = strategy

    def solve(self, f: Fn, a: float, b: float) -> float | None:
        return self.strategy.find(f, a, b)

    def change_algorithm(self, new_algorithm: FindRoot) -> None:
        self.strategy = new_algorithm

def f(x: float) -> float:
    return x * x - 2

solver = RootSolver(Bisection())
for algorithm in (Bisection(), Newton(), Secant()):
    solver.change_algorithm(algorithm)
    root = solver.solve(f, 0.0, 2.0)
    assert root is not None
    print(f"{root:.6f}")
#: 1.414214
#: 1.414214
#: 1.414214
```

We use strategies-as-functions constantly in Python without naming it as a pattern.
The `key` argument to `sorted()`, `min()`, and `max()` is a strategy.
You provide a function that decides how to compare.
The object form is worth it only when a strategy needs its own configuration or several related methods.

## Chain of Responsibility

*Chain of Responsibility* tries a sequence of handlers until one succeeds.
*GoF Design Patterns* implements the chain as a linked list,
largely because it predates standard list types.
In Python the chain is a list of functions.
Bisection needs the interval to bracket a root; the open methods do not:

```python
# chain.py
from algorithms import Fn, RootFinder, bisection, newton, secant

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None

def f(x: float) -> float:
    return x * x - 2   # Root at the square root of 2

chain: list[RootFinder] = [bisection, secant, newton]
# [0, 2] brackets the root, so bisection succeeds first:
r1 = solve(f, 0.0, 2.0, chain)
print(f"{r1:.6f}" if r1 is not None else "no root")
#: 1.414214
# [1.0, 1.3] does not bracket it; bisection fails, secant finds it:
r2 = solve(f, 1.0, 1.3, chain)
print(f"{r2:.6f}" if r2 is not None else "no root")
#: 1.414214
```

Each handler is a *Strategy* function, the chain is the list,
and success is a non-`None` return.
Adding, removing, or reordering handlers means editing a list.
We see the fall-through when bisection cannot bracket a root.
It returns `None`, and the chain continues looking for a method that can.

We test that the first finder that converges wins,
a later finder rescues one that fails, and an empty chain returns `None`:

```python
# test_chain.py
from algorithms import bisection, newton, secant
from chain import solve

def f(x: float) -> float:
    return x * x - 2   # Root at the square root of 2

def test_first_successful_finder_wins() -> None:
    root = solve(f, 0.0, 2.0, [bisection, secant, newton])
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6

def test_chain_falls_through_to_a_later_method() -> None:
    # [1.0, 1.3] does not bracket the root: bisection fails
    root = solve(f, 1.0, 1.3, [bisection, secant, newton])
    assert root is not None
    assert abs(root - 2 ** 0.5) < 1e-6

def test_empty_chain_returns_none() -> None:
    assert solve(f, 0.0, 2.0, []) is None

def test_all_fail_returns_none() -> None:
    def g(x: float) -> float:
        return x * x + 1   # No real root
    assert solve(g, 0.0, 2.0, [bisection]) is None
```

## An Event Bus: Handlers Keyed by Type

Chain of Responsibility kept its handlers in a list and tried them in order.
If you key that structure by type instead of by position, you have an *event bus*.
This is a `dict` from each event type to the functions that care about it.
The events are plain values,
written as [frozen data classes](12_Data_Classes_as_Types.md#immutability).
Publishing an event looks up its type and calls every handler registered for it.
The handlers are ordinary functions,
so there is no `Handler` interface to implement and no registration ceremony:

```python
# event_bus.py
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

type Handler[E] = Callable[[E], None]

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
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

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
#: + deposit 100
#:   audit: a deposit of 100
bus.publish(Withdraw(30))
#: - withdraw 30
bus.publish(Closed("inactivity"))    # No handler: nothing happens
```

`subscribe` is generic on the event type `E`.
The checker reads `E` from the first argument and requires the handler to accept that exact type,
so `subscribe(Deposit, on_withdraw)` is a type error.
The safety check happens once, at registration.
The stored `defaultdict`, though, mixes handlers for every event type in one structure.
Its lists cannot name a single event class, so the element type erases the parameter to `Handler[Any]`.
The generic guards the boundary; the `Any` covers the heterogeneous storage behind it.

`subscribe` indexes `self._handlers` directly,
letting the `defaultdict` build each event type's list on first use.
`publish` still calls `.get(type(event), [])` instead of indexing.
Indexing on a read would insert an empty list as a side effect,
leaving a stray entry behind for every published event type
that happens to have no subscriber, such as `Closed`.

For testing, publishing calls every handler registered for a type,
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

This is the [Observer](32_Observer.md#the-pythonic-observer-a-list-of-callables),
narrowed to a single subject.
The subscribers are functions, and the bus routes each event to them by its type.
Here a type may have many handlers.
If you instead want exactly one handler per type,
chosen by the argument's type and open to new types without editing a central function,
that is `functools.singledispatch`,
used by [Visitor](34_Visitor.md#the-pythonic-visitor-singledispatch) and [Pattern Refactoring](38_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it).

## Exercises

1.  Add an "undo" capability to `command.py`.
    What do the commands need to become, and is a function still enough,
    or do you now want an object?
2.  Rewrite `chain.py` so each handler also reports why it failed,
    and the solver prints every attempt before returning the winner.
3.  Use `sorted()` with a `key` function to sort a list of `(name, score)` tuples by score,
    then by name.
    Explain why `key` is the *Strategy* pattern.
