# Function Objects: Solutions

## 1. Undo, added to `command.py`

```python
# exercise_1.py
class UndoableCommand:
    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError

class Deposit(UndoableCommand):
    def __init__(self, account: dict, amount: int) -> None:
        self.account = account
        self.amount = amount

    def execute(self) -> None:
        self.account["balance"] += self.amount

    def undo(self) -> None:
        self.account["balance"] -= self.amount

class Macro:
    def __init__(self) -> None:
        self.commands: list[UndoableCommand] = []

    def add(self, command: UndoableCommand) -> None:
        self.commands.append(command)

    def run(self) -> None:
        for c in self.commands:
            c.execute()

    def undo_all(self) -> None:
        for c in reversed(self.commands):  # Reverse order to undo
            c.undo()

account = {"balance": 0}
macro = Macro()
macro.add(Deposit(account, 10))
macro.add(Deposit(account, 5))
macro.run()
print(account["balance"])
#: 15
macro.undo_all()
print(account["balance"])
#: 0
```

A bare function is no longer enough, though not because of state.
`callable_command.py`'s `Repeat` already carries its configuration and
is still called with `()`, so state alone would not force a class.
Undo forces one, because a command now answers two requests,
`execute()` and `undo()`, and a callable has only one call.

`Deposit` also has to remember what it did, here the account and the
amount, so it can reverse that action later: a fresh call to the same
function cannot know what a previous call changed. That is the step
the chapter names, where the `Command` class earns its keep because
the command needs a second operation.

## 2. `chain.py`, reporting every attempt

```python
# exercise_2.py
TOLERANCE = 1e-12
MAX_ITER = 200

def bisection(f, a, b):
    if f(a) * f(b) > 0:
        return None
    mid = (a + b) / 2
    for _ in range(MAX_ITER):
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
        mid = (a + b) / 2
    return mid

def secant(f, a, b):
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f, a, b):
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None

def solve(f, a, b, chain):
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            print(f"{finder.__name__} succeeded: {root:.6f}")
            return root
        print(f"{finder.__name__} failed: could not converge")
    print("all finders failed")
    return None

def f(x):
    return x * x - 2

solve(f, 1.0, 1.3, [bisection, secant, newton])
#: bisection failed: could not converge
#: secant succeeded: 1.414214
```

Each handler function already reports its own outcome through its
return value, `None` for failure, a number for success, so `solve()`
only needs to print that outcome as it checks it, rather than asking
each handler for a separate explanation. `finder.__name__` reads the
function's own name, since every ordinary Python function carries its
name as an attribute, so the report needs no extra bookkeeping to say
*which* handler just ran.

## 3. `sorted()` with a compound key, and why `key` is *Strategy*

```python
# exercise_3.py
scores = [("Bob", 85), ("Amy", 92), ("Cid", 85), ("Amy", 70)]
by_score_then_name = sorted(scores, key=lambda t: (t[1], t[0]))
print(by_score_then_name)
#: [('Amy', 70), ('Bob', 85), ('Cid', 85), ('Amy', 92)]
```

The key function returns a tuple, `(score, name)`, and Python compares
tuples element by element, so `sorted()` orders primarily by score
and, among equal scores (`Bob` and `Cid`, both `85`), falls back to
comparing names. `key` is exactly a *Strategy*: `sorted()` fixes the
*algorithm* (some comparison-based sort), and the caller supplies the
interchangeable *policy* that decides what "in order" means for this
particular call, without `sorted()` itself needing to know anything
about tuples, scores, or names. Passing a different `key` swaps the
ordering strategy the same way `strategy_pattern.py` swaps
`RootSolver`'s algorithm, except here the "context" object holding the
current strategy is just the call to `sorted()` itself.

## 4. A configurable `newton()`, closed over and partially applied

```python
# exercise_4.py
from collections.abc import Callable
from functools import partial

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

MAX_ITER = 200

def newton(f: Fn, a: float, b: float,
           tolerance: float = 1e-12) -> float | None:
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < tolerance:
            return x
    return None

def newton_within(tolerance: float) -> RootFinder:
    def finder(f: Fn, a: float, b: float) -> float | None:
        return newton(f, a, b, tolerance)
    return finder

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            return root
    return None

def f(x: float) -> float:
    return x * x - 2

coarse_closure = newton_within(0.5)
coarse_partial: RootFinder = partial(newton, tolerance=0.5)
fine_closure = newton_within(1e-12)

for finder in (coarse_closure, coarse_partial, fine_closure):
    root = solve(f, 0.0, 2.0, [finder])
    assert root is not None
    print(f"{root:.6f}")
#: 1.500000
#: 1.500000
#: 1.414214
```

`tolerance` becomes a parameter with a default, so every existing call
to `newton(f, a, b)` keeps working. The closure and the `partial` then
reach the same configured strategy from two directions. `newton_within()`
writes a new function whose body supplies the argument;
`partial(newton, tolerance=0.5)` stores the argument and supplies it at
the call. Both produce something matching `RootFinder`, so `solve()`
accepts either with no change.

The two coarse finders print the same wrong-looking answer, `1.500000`,
which is how you can tell the tolerance took effect rather than being
ignored: Newton's method starting at `1.0` reaches `1.5` on its first
step, and a tolerance of `0.5` accepts the second step as close enough.
The fine finder runs the same code to `1e-12` and agrees with the true
root to six places.

`partial` is the shorter of the two, and it works here because
`tolerance` is passed by keyword. A closure is what you need when the
setting is not a parameter at all, the way `bisection_within()` builds
its `while` condition around one.

## 5. An event bus that walks the MRO, and can unsubscribe

```python
# exercise_5.py
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

type Handler[E] = Callable[[E], None]

@dataclass(frozen=True)
class Deposit:
    amount: int

@dataclass(frozen=True)
class BigDeposit(Deposit):
    pass

class EventBus:
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe[E](self, event_type: type[E],
                       handler: Handler[E]) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: object) -> None:
        for cls in type(event).__mro__:  # Parents last
            for handler in self._handlers.get(cls, []):
                handler(event)

def on_deposit(event: Deposit) -> None:
    print(f"deposit {event.amount}")

def on_big(event: BigDeposit) -> None:
    print(f"big deposit {event.amount}")

bus = EventBus()
bus.subscribe(Deposit, on_deposit)
bus.subscribe(BigDeposit, on_big)

bus.publish(BigDeposit(500))
#: big deposit 500
#: deposit 500
bus.publish(Deposit(10))
#: deposit 10

bus.unsubscribe(Deposit, on_deposit)
bus.publish(BigDeposit(500))
#: big deposit 500
```

`type(event).__mro__` already runs from the class outward to `object`,
so iterating it in order calls the most specific handlers first and the
inherited ones after, which is what "parents last" asks for. `publish()`
keeps using `.get()` for the same reason the chapter gives: indexing a
`defaultdict` on a read would insert an empty list for every class in
every published event's MRO, `object` included.

`unsubscribe()` cannot break an existing caller. It adds a method, and
code that never calls it behaves exactly as before. The MRO walk can.
A handler subscribed to `Deposit` starts receiving every subclass of
`Deposit`, including ones defined after it was written, so a bus where
`BigDeposit` used to reach only `on_big` now reaches `on_deposit` too.
That is the intended feature, and it is still a behavior change to
existing code: any handler that assumed `type(event) is Deposit`, or
that counts events, now sees more than it did.

`unsubscribe()` guards with `if handler in handlers` rather than calling
`remove()` outright, since `remove()` raises a `ValueError` for a handler
that was never subscribed. Whether that should be silent or loud is a
design decision: silent matches the bus's existing habit of letting an
unmatched event pass without complaint.
