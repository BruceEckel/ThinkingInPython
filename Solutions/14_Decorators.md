# Decorators: Solutions

## 1. A class decorator that reports and returns

```python
# exercise_1.py
def slots_report[T: type](cls: T) -> T:
    print(f"decorating {cls.__name__}")
    return cls

@slots_report
class Point:
    x: int
    y: int

@slots_report
class Empty:
    pass

print(Point.__name__, Empty.__name__)
#: decorating Point
#: decorating Empty
#: Point Empty
```

Both `decorating` lines print before anything else, because a class
decorator runs when the `class` statement finishes, not when an
instance is made. `slots_report` returns `cls` unchanged, so `Point`
is the same class object it would have been without the decorator;
the only effect is the side effect.

That is also what `register` does, and the comparison is the point: a
class decorator that returns its argument can observe and record, and
that covers most real uses (a registry, a plugin table, a validation
pass at import time). What it cannot do is change the class into
something else, which is what `@dataclass` does when it returns a
class with generated methods, and what `@singleton` does when it
returns a function instead of a class. The return value decides which
kind of decorator you have written.

## 2. A `timing` decorator stacked with `@trace`

```python
# exercise_2.py
import time
from collections.abc import Callable
from functools import wraps

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"-> {func.__name__}{args}")  # type: ignore
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")  # type: ignore
        return result
    return wrapper

def timing[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        # elapsed differs every run: print a fixed message plus a
        # deterministic check, not the raw, ever-changing number.
        ok = elapsed >= 0
        name = func.__name__  # type: ignore
        print(f"{name} timed, non-negative: {ok}")
        return result
    return wrapper

@trace
@timing
def add(a: int, b: int) -> int:
    return a + b

add(2, 3)
#: -> add(2, 3)
#: add timed, non-negative: True
#: <- add = 5
```

`@trace` above `@timing` means `add = trace(timing(add))`, so `trace`'s
wrapper is the outermost layer and `timing`'s is inside it. Calling
`add(2, 3)` enters `trace`'s wrapper first, which prints the `->` line,
then calls the *wrapped* function, which is `timing`'s wrapper. That
one measures and reports the elapsed time around the real `add()`
call (in real code you would print the raw `elapsed`, shown here as a
deterministic check instead, since a fixed marker cannot capture a
number that changes every run), then control returns outward to
`trace`'s wrapper, which prints the `<-` line last. The output order
mirrors the wrapping order: outermost decorator prints first and
last, and each inner layer's output appears nested in between.

## 3. A coffee shop, object *Decorator* pattern

```python
# exercise_3.py
from typing import ClassVar, Protocol

class Drink(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...

class Espresso:
    cost = 2.50
    description = "Espresso"

class Cappuccino:
    cost = 3.25
    description = "Cappuccino"

class Extra:
    add_cost: ClassVar[float] = 0.0

    def __init__(self, drink: Drink) -> None:
        self.drink = drink
        self.name = type(self).__name__

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"

class Whipped(Extra):
    add_cost = 0.75

class Decaf(Extra):
    add_cost = 0.0

class ExtraShot(Extra):
    add_cost = 0.90

order = Whipped(ExtraShot(Espresso()))
print(f"{order.description}: ${order.cost:.2f}")
#: Espresso + ExtraShot + Whipped: $4.15
decaf = Decaf(Cappuccino())
print(f"{decaf.description}: ${decaf.cost:.2f}")
#: Cappuccino + Decaf: $3.25
```

This is `pizza_decorator.py`'s shape with the menu changed: a `Drink`
`Protocol` naming the two readable properties, plain drinks that
satisfy it with class attributes, and an `Extra` base that wraps one
`Drink` and forwards through the same interface. Nothing inherits from
`Drink`, and nothing needs to; the `Protocol` is checked structurally.

`Decaf` is worth noticing. Its `add_cost` is `0.0`, so it changes the
description without changing the price, which a class-per-combination
design would still force you to enumerate. Adding a fourth extra means
one class with one number in it, and the extras compose in any order,
since each layer knows only about the drink directly inside it.

## 4. A class-level counter shared across every decorated function

```python
# trace_counting.py
from collections.abc import Callable
from functools import update_wrapper
from typing import ClassVar

class trace_counting[**P, R]:
    # Shared by every decorated function:
    total_calls: ClassVar[int] = 0

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.count = 0  # Per-function, like count_calls
        update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.count += 1
        trace_counting.total_calls += 1
        return self.func(*args, **kwargs)

@trace_counting
def f(x: int) -> int:
    return x + 1

@trace_counting
def g(x: int) -> int:
    return x * 2

f(1)
f(2)
g(3)
print(f.count, g.count, trace_counting.total_calls)
#: 2 1 3
```

Each decorated function gets its own instance of `trace_counting`
(the same as `count_calls`), so `f.count` and `g.count` track only
their own function's calls: `2` and `1`. `total_calls` is declared
`ClassVar[int]`, so it belongs to the `trace_counting` class itself,
not to any one instance. Every `__call__()`, on any decorated function,
increments the same shared counter through `trace_counting.total_calls
+= 1`, so it accumulates across every function decorated with
`@trace_counting`, reaching `3` after the three calls above. This is
the same class-attribute-versus-instance-attribute distinction from
[Class Attributes](09_Class_Attributes.md): `self.count` shadows
nothing and lives per-instance, while `total_calls`, read and written
through the class name, is one value the whole family of decorated
functions shares.

## 6. `retry(times)` in the function form

```python
# exercise_6.py
from collections.abc import Callable
from functools import wraps

def retry[**P, R](
        times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"attempt {attempt} failed: {e}")
            return func(*args, **kwargs)
        return wrapper
    return decorate

attempts = 0

@retry(times=3)
def flaky() -> str:
    global attempts
    attempts += 1
    if attempts < 3:
        raise ValueError(f"not yet ({attempts})")
    return "succeeded"

print(flaky())
#: attempt 1 failed: not yet (1)
#: attempt 2 failed: not yet (2)
#: succeeded
print(flaky.__name__)
#: flaky

@retry(times=2)
def always_fails() -> str:
    raise RuntimeError("no luck")

try:
    always_fails()
except RuntimeError as e:
    print("escaped:", e)
#: attempt 1 failed: no luck
#: escaped: no luck
```

The loop runs `times - 1` attempts inside a `try`, and the final
attempt sits outside it, with no handler. That last call is what
satisfies both requirements at once: it returns `R` on success, so the
function has a return value on every path the checker can see, and it
lets the last exception propagate untouched rather than re-raising a
copy. Re-raising from inside the loop with `raise` would also work,
but then the checker cannot tell that the function always either
returns or raises.

`@wraps(func)` keeps the identity: `flaky.__name__` reports the
wrapped function's name, not `wrapper`. Without it, every retried
function in a traceback or a log would report itself as `wrapper`,
which is precisely when you least want the name to be wrong.

Catching bare `Exception` is deliberate here and worth flagging: a
real `retry` should take the exception types it retries, since
retrying a `TypeError` from a bad call signature just fails three
times more slowly.
