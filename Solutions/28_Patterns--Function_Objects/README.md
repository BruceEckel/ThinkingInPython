# Function Objects: Solutions

## 1. Undo, added to `command.py`

> Add an "undo" capability to `command.py`.
> What do the commands need to become, and is a function still enough,
> or do you now want an object?

<details>
<summary>Where to look</summary>

[A Callable Object as a Command](../../Chapters/28_Patterns--Function_Objects.md#a-callable-object-as-a-command) shows a command that carries its own state, which the macro still calls with `()`.
A command that must answer two requests, running and reversing, needs a type with two members.
Describe that type with a `Protocol`, and make each command remember what it did so it can reverse it.
A `Macro` then undoes its list in `reversed()` order.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Protocol
from record import record

class UndoableCommand(Protocol):
    def __call__(self) -> None: ...
    def undo(self) -> None: ...

@record
class Deposit:
    account: dict[str, int]
    amount: int

    def __call__(self) -> None:
        ...

    def undo(self) -> None:
        ...

class Macro:
    def __init__(self) -> None:
        ...

    def add(self, command: UndoableCommand) -> None:
        ...

    def run(self) -> None:
        ...

    def undo_all(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you keep `command.py`'s `Command` alias as the type of the macro's list,
the script still prints `15` and `0`,
but `ty` reports `unresolved-attribute` on `c.undo()`,
because an object of type `Command` has no attribute `undo`.
`Command` describes one call,
so the solution gives the list a `Protocol` that declares both operations.

```python
# exercise_1.py
from typing import Protocol
from record import record

class UndoableCommand(Protocol):
    def __call__(self) -> None: ...
    def undo(self) -> None: ...

@record
class Deposit:
    account: dict[str, int]
    amount: int

    def __call__(self) -> None:
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
            c()

    def undo_all(self) -> None:
        for c in reversed(self.commands):
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
`callable_command.py`'s `Repeat` already carries its configuration, and
the macro still calls it with `()`, so state alone does not force more
than a callable. Undo does, because a command now answers two requests,
`__call__()` and `undo()`, and a callable has only one call.

**Name both requests in one type.** `Command`, the chapter's
`Callable[[], None]`, has room for one call, so a list of undoable
commands needs a type with two members, `__call__()` and `undo()`, and
in Python that type is a `Protocol`. `UndoableCommand` above is that
`Protocol`. `Macro` annotates `self.commands` against it, `Deposit`
inherits nothing, and `run()` still calls each `Deposit` with `()`, so
the function form's habit survives. The *GoF Design Patterns* shape is
a base class with two `raise NotImplementedError` bodies. A base class
pays for itself when the commands share implementation, and these
commands share none.

**Remember what to reverse.** `Deposit` must also remember what it
did, here the account and the amount, so it can reverse that action
later. A fresh call to the same function cannot know what a previous
call changed. `Deposit` is a record, like `Repeat`, because neither
field changes after construction. The record is frozen and the
dictionary it references is not, so `__call__()` and `undo()` can
still update the balance.

</details>
</details>
</details>

## 2. `chain.py`, reporting every attempt

> Rewrite `chain.py` so each handler also reports why it failed,
> and the solver prints every attempt before returning the winner.

<details>
<summary>Where to look</summary>

[Chain of Responsibility: Choosing the Handler at Runtime](../../Chapters/28_Patterns--Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) uses `None` to mean that a handler failed.
`None` carries no reason, so give each handler a failure value that does, and return `float | Failed`.
In `solve()`, tell a root from a failure with `match`, print each attempt, and read the handler's name from `__name__`.
Because `Callable` has no name, the type of the chain needs a `Protocol` that declares `__name__`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Callable
from typing import Final, Protocol
from record import record

type Fn = Callable[[float], float]

@record
class Failed:
    reason: str

class Finder(Protocol):
    __name__: str
    def __call__(self, f: Fn, a: float,
                 b: float) -> float | Failed: ...

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200
NO_CONVERGENCE: Final[Failed] = Failed(
    f"no convergence in {MAX_ITER} steps")

def bisection(f: Fn, a: float, b: float) -> float | Failed:
    ...

def secant(f: Fn, a: float, b: float) -> float | Failed:
    ...

def newton(f: Fn, a: float, b: float) -> float | Failed:
    ...

def solve(f: Fn, a: float, b: float,
          chain: list[Finder]) -> float | None:
    ...

def f(x: float) -> float:
    ...

def g(x: float) -> float:
    ...
```

<details>
<summary>Solution</summary>

If you annotate `chain` with a `Callable` type, as the chapter's `RootFinder` is,
the script runs and prints the same report,
but `ty` reports `unresolved-attribute` on both reads of `finder.__name__`.
A `Callable` describes a call and says nothing about a name,
so the solution types `chain` with the `Finder` protocol, which declares `__name__`.

```python
# exercise_2.py
from collections.abc import Callable
from typing import Final, Protocol
from record import record

type Fn = Callable[[float], float]

@record
class Failed:
    reason: str

class Finder(Protocol):
    __name__: str
    def __call__(self, f: Fn, a: float,
                 b: float) -> float | Failed: ...

TOLERANCE: Final[float] = 1e-12
MAX_ITER: Final[int] = 200
NO_CONVERGENCE: Final[Failed] = Failed(
    f"no convergence in {MAX_ITER} steps")

def bisection(f: Fn, a: float, b: float) -> float | Failed:
    if f(a) * f(b) > 0:
        return Failed(f"no root bracketed by [{a}, {b}]")
    for _ in range(MAX_ITER):
        mid = (a + b) / 2
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return NO_CONVERGENCE

def secant(f: Fn, a: float, b: float) -> float | Failed:
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            return Failed(f"flat step at {x1}")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return NO_CONVERGENCE

def newton(f: Fn, a: float, b: float) -> float | Failed:
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return Failed(f"zero slope at {x}")
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return NO_CONVERGENCE

def solve(f: Fn, a: float, b: float,
          chain: list[Finder]) -> float | None:
    for finder in chain:
        match finder(f, a, b):
            case Failed(reason):
                print(f"{finder.__name__}: {reason}")
            case root:
                print(f"{finder.__name__}: {root:.6f}")
                return root
    print("every finder failed")
    return None

def f(x: float) -> float:
    return x * x - 2

solve(f, 1.0, 1.3, [bisection, secant, newton])
#: bisection: no root bracketed by [1.0, 1.3]
#: secant: 1.414214

def g(x: float) -> float:
    return x * x + 1  # No real root

solve(g, 0.0, 2.0, [bisection])
#: bisection: no root bracketed by [0.0, 2.0]
#: every finder failed
```

**Give failure a reason.** `None` says that a handler failed and cannot say why, so a handler
that reports its reason needs a failure value with room for the reason.
`Failed` is that value, a record with one field, and each finder now
returns `float | Failed`.

**Report each way to fail.** A finder has more than one way to fail.
`bisection()` gives up at once when the interval holds no sign change,
and it can also run out of iterations, so each failing `return`
states its own reason.

**Tell a root from a failure.** `solve()` tells a root from a `Failed`
with `match`. `case Failed(reason)` prints the reason and lets the
loop continue, and any other value is the root.

The chapter's advice about the failure value still holds. A `Failed`
is never a root, so `float | Failed` says which result is which, and
`solve()` checks the result's type, not its truthiness.

**Name each attempt.** `finder.__name__` reads the function's own name, since every function
carries its name as an attribute, so the report needs no extra
bookkeeping to say which handler ran. That name is why `chain` needs a
`Protocol` here instead of an alias like the chapter's `RootFinder`.
`Callable[...]` describes what a handler accepts and returns, and
says nothing about a name, so `ty` rejects `finder.__name__` on a
handler annotated that way (Pyright allows it, inferring the
attributes of a function object). `Finder` declares `__name__`
alongside `__call__()`, and a function satisfies both. The listing
copies the finders from `algorithms.py` rather than importing them,
because each solution runs on its own.

</details>
</details>
</details>

## 3. `sorted()` with a compound key, and why `key` is *Strategy*

> Use `sorted()` with a `key` function to sort a list of `(name, score)` tuples by score,
> then by name.
> Explain why `key` is the *Strategy* pattern.

<details>
<summary>Where to look</summary>

[Strategy: Choosing the Algorithm at Runtime](../../Chapters/28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) shows a caller supplying the interchangeable part of an algorithm as a function.
Have the `key` function return a tuple, since Python compares tuples element by element.
For the explanation, ask what `sorted()` fixes and what the caller supplies.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
scores = [("Bob", 85), ("Amy", 92), ("Cid", 85),
          ("Amy", 70)]
by_score_then_name = sorted(scores,
                            key=lambda t: (t[1], t[0]))
print(by_score_then_name)
#: [('Amy', 70), ('Bob', 85), ('Cid', 85), ('Amy', 92)]
```

The key function returns a tuple, `(score, name)`, and Python compares
tuples element by element. `sorted()` therefore orders by score first,
and among equal scores (`Bob` and `Cid`, both `85`) it compares names.
`key` is a *Strategy*. `sorted()` provides the algorithm (some
comparison-based sort), and the caller supplies the interchangeable
policy that decides what "in order" means for this call. `sorted()`
knows nothing about tuples, scores, or names. Passing a different
`key` swaps the ordering strategy the same way the chapter's classic
*Strategy* form swaps the algorithm its Context holds. Here the
Context holding the current strategy is the call to `sorted()`.

</details>
</details>

## 4. A configurable `newton()`, closed over and partially applied

> Following `bisection_within()`,
> add a `tolerance` parameter to `newton()` in `algorithms.py` and build a configured strategy from it two ways:
> with a closure, and with `functools.partial`.
> Confirm that `chain.py`'s `solve()` runs a chain holding either one,
> with no change to `solve()`.

<details>
<summary>Where to look</summary>

[Strategy: Choosing the Algorithm at Runtime](../../Chapters/28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) builds a configured *Strategy* from `bisection_within()` and again with `functools.partial`.
Give `newton()` a `tolerance` parameter with a default so existing calls keep working.
Then write a factory that returns an inner function calling `newton()` with the tolerance, and build a second finder with `partial()` and a keyword argument.
Both match the `RootFinder` type, which is why `solve()` needs no change.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Callable
from functools import partial
from typing import Final

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

MAX_ITER: Final[int] = 200

def newton(f: Fn, a: float, b: float,
           tolerance: float = 1e-12) -> float | None:
    ...

def newton_within(tolerance: float) -> RootFinder:
    ...

def solve(f: Fn, a: float, b: float,
          chain: list[RootFinder]) -> float | None:
    ...

def f(x: float) -> float:
    ...
```

<details>
<summary>Solution</summary>

If you leave out the keyword and write `partial(newton, 0.6)`,
`partial()` binds `0.6` to `f`, the first positional parameter.
`ty` rejects the assignment to `RootFinder` with `invalid-assignment`,
and at run time calling the finder raises a `TypeError` when `newton()` adds the function in `a` to a float.
The solution binds `tolerance` by keyword, as `partial_bisection.py` does.

```python
# exercise_4.py
from collections.abc import Callable
from functools import partial
from typing import Final

type Fn = Callable[[float], float]
type RootFinder = Callable[[Fn, float, float], float | None]

MAX_ITER: Final[int] = 200

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

coarse_closure = newton_within(0.6)
coarse_partial: RootFinder = partial(newton, tolerance=0.6)
fine_closure = newton_within(1e-12)

for finder in (coarse_closure, coarse_partial,
               fine_closure):
    root = solve(f, 0.0, 2.0, [finder])
    assert root is not None
    print(f"{root:.6f}")
#: 1.500000
#: 1.500000
#: 1.414214
```

**Keep existing calls working.** `tolerance` becomes a parameter with a default, so every existing call
to `newton(f, a, b)` keeps working.

**Configure the finder two ways.** The closure and the `partial` then
reach the same configured strategy from two directions. `newton_within()`
writes a new function whose body supplies the argument.
`partial(newton, tolerance=0.6)` stores the argument and supplies it at
the call. Both produce a finder matching `RootFinder`, so `solve()`
accepts either with no change.

The two coarse finders print the same wrong-looking answer, `1.500000`,
and that answer shows the tolerance took effect.
Newton's method starting at `1.0` moves by `0.5` on its first step, to
`1.5`, and a tolerance of `0.6` accepts a step that size, so the loop
stops there. The fine finder runs the same code to `1e-12` and agrees
with the true root to six places.

`partial` is the shorter of the two ways to configure the finder, and
it works here because the caller can supply `tolerance` by keyword.
You need a closure when the setting is not a parameter of the
function, the way `bisection_within()` writes the tolerance into its
`while` condition.

</details>
</details>
</details>

## 5. An event bus that walks the MRO, and can unsubscribe

> Because `EventBus.publish()` looks up `type(event)`,
> a subclass of `Deposit` finds no handler.
> Change `publish()` to walk `type(event).__mro__` and call every handler registered along it,
> parents last.
> Then add `unsubscribe()`.
> Which of the two changes can break an existing caller, and why?

<details>
<summary>Where to look</summary>

[An Event Bus: Handlers Keyed by Type](../../Chapters/28_Patterns--Function_Objects.md#an-event-bus-handlers-keyed-by-type) looks handlers up by `type(event)` in a `defaultdict`.
Iterate over `type(event).__mro__` instead, and read each class's handlers with `.get()` so a lookup does not insert keys.
`unsubscribe()` removes a handler from that list, so decide what it should do with a handler that is not in the list.
For the last question, compare which change alters what an existing caller receives.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections import defaultdict
from collections.abc import Callable
from typing import Any
from record import record

type Handler[E] = Callable[[E], None]

@record
class Deposit:
    amount: int

@record
class BigDeposit(Deposit):
    pass

class EventBus:
    def __init__(self) -> None:
        ...

    def subscribe[E](self, event_type: type[E],
                     handler: Handler[E]) -> None:
        ...

    def unsubscribe[E](self, event_type: type[E],
                       handler: Handler[E]) -> None:
        ...

    def publish(self, event: object) -> None:
        ...

def on_deposit(event: Deposit) -> None:
    ...

def on_big(event: BigDeposit) -> None:
    ...
```

<details>
<summary>Solution</summary>

If you index `self._handlers[cls]` inside the MRO walk, the program
prints the same four lines, but each read of a missing class inserts an
empty list. After the demo, `bus._handlers` holds three keys,
`Deposit`, `BigDeposit`, and `object`, where the solution's bus holds
two. The solution reads with `.get(cls, [])`, which returns an empty
list without storing it.

```python
# exercise_5.py
from collections import defaultdict
from collections.abc import Callable
from typing import Any
from record import record

type Handler[E] = Callable[[E], None]

@record
class Deposit:
    amount: int

@record
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

**Ignore a handler that is not subscribed.** `unsubscribe()` guards
with `if handler in handlers` rather than calling `remove()` outright,
since `remove()` raises a `ValueError` for a handler not in the list.
Whether that case should be silent or loud is a design decision. A
silent `unsubscribe()` matches the bus's habit of letting an unmatched
event pass without complaint.

**Walk the ancestry, most specific first.** `type(event).__mro__`
already runs from the class outward to `object`, so iterating over it
in order calls the most specific handlers first and the inherited ones
after. That order meets the "parents last" requirement. `publish()`
keeps using `.get()` for the same reason the chapter gives. Indexing
a `defaultdict` on a read inserts an empty list for every class in
every published event's MRO, `object` included.

Adding `unsubscribe()` cannot break an existing caller, which does not
call it and so behaves as before. The MRO walk can.
A handler subscribed to `Deposit` starts receiving every subclass of
`Deposit`, including subclasses written after the handler, so a
`BigDeposit` that reached `on_big` before the change now reaches
`on_deposit` too. That wider reach is the intended feature, and it
still changes how existing code behaves. Any handler that assumes
`type(event) is Deposit`, or that counts events, now sees more than it
did before.

</details>
</details>
</details>

## 6. Three fixes for late binding, and what none of them fix

> Build a list of three commands in a `for` loop (not a comprehension)
> with `lambda: print(n)`.
> Call them and explain the output.
> Fix the loop three ways: with a default argument, with `functools.partial`,
> and with a factory function that takes `n` and returns the command.
> Which one still works if you must compute the value at call time rather than at build time?

<details>
<summary>Where to look</summary>

[The Late-Binding Trap](../../Chapters/28_Patterns--Function_Objects.md#the-late-binding-trap) explains that a closure reads a variable when the closure runs, not when Python creates it.
Each fix evaluates `n` while the loop runs: a default argument, `partial()`, and a factory function with its own scope.
For the closing question, find a value the command must still read at call time and ask which fix freezes it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from collections.abc import Callable
from functools import partial

type Command = Callable[[], None]

def make(n: int) -> Command:
    ...

def report() -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from collections.abc import Callable
from functools import partial

type Command = Callable[[], None]

broken: list[Command] = []
for n in range(3):
    broken.append(lambda: print(n))
for command in broken:
    command()
#: 2
#: 2
#: 2

by_default: list[Command] = []
for n in range(3):
    by_default.append(lambda n=n: print(n))

by_partial: list[Command] = []
for n in range(3):
    by_partial.append(partial(print, n))

def make(n: int) -> Command:
    return lambda: print(n)

by_factory: list[Command] = [
    make(n) for n in range(3)
]

for fixed in (by_default, by_partial, by_factory):
    for command in fixed:
        command()
#: 0
#: 1
#: 2
#: 0
#: 1
#: 2
#: 0
#: 1
#: 2

# Late lookup, kept on purpose:
settings = {"level": "low"}

def report() -> None:
    print(settings["level"])

settings["level"] = "high"
report()
#: high
```

**Reproduce the late-binding trap.** A `for` loop does not create a scope, so `n` is one variable that the
loop rebinds three times. All three lambdas close over that one
variable rather than over its value. By the time anything calls them,
the loop has finished and `n` holds 2. Nothing is wrong with the
lambdas. They read the variable they name, at the moment of the call.

**Capture the value at build time.** The three fixes all work, and all
work the same way. Each one evaluates `n` while the loop is still
running and stores the result. `lambda n=n:` evaluates the default at
definition. `partial(print, n)` evaluates the argument where it appears.
`make(n)` gives each lambda its own `n` in its own function scope, and
only that fix keeps the value private. `lambda n=n:` exposes the value
as a parameter a caller can override, and `partial(print, n)` passes the
value straight to `print()`.

A value computed from the frozen `n` separates the fixes. The two
lambda forms run their body at the call, so
`lambda n=n: print(n * rate())` and the factory's lambda both read
`rate()` when the command runs. `partial(print, n * rate())`
evaluates the product while the loop builds the command.

**Read the variable at call time.** None of the three preserves late
lookup of `n`, and that is the point of the exercise's closing
question. If the command must read `n` when it runs, all three fixes
are wrong. Each one freezes the value when the loop builds the
command. You then want the original behavior, aimed at something that
outlives the loop, as `report()` does by reading `settings` at call
time. The late-binding trap and late binding as a feature are the same
mechanism. Which one you have depends on whether the name you close
over still means what you wanted when the command finally runs.

</details>
</details>
</details>

## 7. `event()` registering `cls`

> In `tagged_bus.py`, change `event()` to register `cls` in place of `built`.
> Predict what importing `bank_events.py` then does, and which line stops it.
> Run it to check.

<details>
<summary>Where to look</summary>

[A Tagged Bus: Handlers That Name Their Event](../../Chapters/28_Patterns--Function_Objects.md#a-tagged-bus-handlers-that-name-their-event) builds the class first and registers `built`.
With `slots=True`, `dataclass()` returns a new class, so ask which class ends up bound to the name `Deposit` and which class `EVENTS` holds.
Then trace how `handler()` checks its first decorated class against `EVENTS`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
import inspect
from dataclasses import dataclass
from typing import Final, dataclass_transform
from exceptions import expect

EVENTS: Final[set[type]] = set()

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    ...

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    ...

@event
class Deposit:
    amount: int

class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
import inspect
from dataclasses import dataclass
from typing import Final, dataclass_transform
from exceptions import expect

EVENTS: Final[set[type]] = set()

@dataclass_transform(frozen_default=True)
def event[E](cls: type[E]) -> type[E]:
    built = dataclass(frozen=True, slots=True)(cls)
    EVENTS.add(cls)  # The change: cls, not built
    return built

@dataclass_transform(frozen_default=True)
def handler[H](cls: type[H]) -> type[H]:
    call = vars(cls)["__call__"]
    sig = inspect.signature(call)
    handled = list(sig.parameters.values())[1].annotation
    if handled not in EVENTS:
        raise TypeError(f"{cls.__name__}: not an @event")
    return dataclass(frozen=True, slots=True)(cls)

@event
class Deposit:
    amount: int

print(len(EVENTS), Deposit in EVENTS)
#: 1 False
print(type(Deposit(5)) in EVENTS)
#: False

class Announce:
    prefix: str
    def __call__(self, event: Deposit) -> None:
        print(f"{self.prefix} deposit {event.amount}")

expect(TypeError, handler, Announce)
#: [TypeError] Announce: not an @event
```

The listing copies the two decorators, makes the change, leaves out
the checks the question does not reach, and applies `handler()` as a
call so that `expect()` can report the failure.

**Register the wrong class.** Python creates the three `@event` classes in `bank_events.py` without
complaint, which makes the mistake easy to miss. `EVENTS` holds one
class for each, and none of them is the class the module's names
reference. `dataclass()` with `slots=True` builds a new class, `event()`
returns that new class, and the `class` statement binds `Deposit` to
what `event()` returns. The set holds the class from which `dataclass()`
started, which no name references and of which no event is an instance.

**Refuse the first handler.** The import stops at the first `@handler`, on `Announce`.
`handler()` reads the annotation on `event`, which is `Deposit`, the
class `dataclass()` returned, and does not find it in `EVENTS`.
`handler()` then raises `TypeError: Announce: not an @event`, although `Deposit` went
through `@event` a few lines earlier. If something else created
the handlers, `publish()` would refuse every event for the same
reason, since `type(event)` is the returned class too.

</details>
</details>
</details>
