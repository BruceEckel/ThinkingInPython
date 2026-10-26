# Decorators: Solutions

## 1. A class decorator that reports and returns

> Write a class decorator `announce` that prints the name of each class it decorates and returns it unchanged,
> then apply it to two small classes.
> Compare what it can do to what `register` does.

<details>
<summary>Where to look</summary>

[Decorating Classes](../../Chapters/14_Techniques--Decorators.md#decorating-classes)
shows `register` receiving a class and returning it.
Write a function that takes the class, prints its `__name__`,
and returns the same object.
The decorator runs once, when the `class` statement finishes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
def announce[T](cls: type[T]) -> type[T]:
    ...

@announce
class Point:
    x: int
    y: int

@announce
class Empty:
    pass
```

<details>
<summary>Done when</summary>

each of your two classes prints its name once,
as its `class` statement finishes and before any later line runs,
and printing each class's `__name__` afterward gives the names back.
`uv run ty check` passes,
and deleting the `return` from `announce` makes it report `invalid-return-type`.

<details>
<summary>Solution</summary>

If you leave out `return cls`, `announce` returns `None`.
Python then binds `None` to `Point` and to `Empty`.
Both `decorating` lines still print,
but the final `print()` raises an `AttributeError`,
since `None` has no `__name__`.
`ty` reports an `invalid-return-type` on `announce` before the program runs.
The solution returns `cls`, so each name stays bound to its class.

```python
# exercise_1.py
def announce[T](cls: type[T]) -> type[T]:
    print(f"decorating {cls.__name__}")
    return cls

@announce
class Point:
    x: int
    y: int
#: decorating Point

@announce
class Empty:
    pass
#: decorating Empty

print(Point.__name__, Empty.__name__)
#: Point Empty
```

**Report at definition time.**
Both `decorating` lines print before anything else,
because a class decorator runs when the `class` statement finishes,
not at instantiation.

`register` returns its argument the same way,
so the two decorators can do the same kinds of work.
A class decorator that returns the class it received can observe and record.
Observing and recording covers most uses: a registry, a plugin table,
a validation pass at import time.

Two other kinds of class decorator change the class or replace it.
`@dataclass` returns the class it received after adding generated methods to it.
[`@singleton`](../../Chapters/23_Patterns--Singleton.md#singleton-by-class-decorator)
returns a different object, a callable that returns one cached instance.
Two things decide which kind you have written:
what the decorator does to its argument, and what it returns.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A `timing` decorator stacked with `@trace`

> Write a `timing` decorator that prints how long the wrapped function took,
> using `time.perf_counter()`.
> Apply it together with `@trace` and predict the order of the output.

<details>
<summary>Where to look</summary>

[Stacking Decorators](../../Chapters/14_Techniques--Decorators.md#stacking-decorators)
shows how `@a` over `@b` means `a(b(func))`.
Build `timing` like `tracer.py`'s wrapper,
with `time.perf_counter()` read before and after the call.
The outermost wrapper runs first,
so work out which layer prints before and which after.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
import time
from collections.abc import Callable, Mapping
from functools import wraps

def call_text(name: str, args: tuple[object, ...],
              kwargs: Mapping[str, object]) -> str:
    ...

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    ...

def timing[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    ...

@trace
@timing
def add(a: int, b: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

with `@trace` above `@timing`, one call prints `trace`'s `->` line,
then your timing line,
then `trace`'s `<-` line showing the real return value rather than `None`.
Swapping the two decorators moves your timing line after the `<-` line.

<details>
<summary>Solution</summary>

If `timing`'s wrapper calls `func(*args, **kwargs)` and discards its value,
the timing line still prints, but `add(2, 3)` returns `None`.
`trace` then prints `<- add = None`.
`ty` reports an `invalid-return-type`,
because the wrapper declares `-> R` and implicitly returns `None`.
The solution's wrapper saves the call's value in `result` before it reads the clock again,
and returns `result` after the report.

```python
# exercise_2.py
import time
from collections.abc import Callable, Mapping
from functools import wraps

def call_text(name: str, args: tuple[object, ...],
              kwargs: Mapping[str, object]) -> str:
    positional = [repr(a) for a in args]
    named = [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{name}({', '.join(positional + named)})"

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        name = wrapper.__name__
        print("->", call_text(name, args, kwargs))
        result = func(*args, **kwargs)
        print(f"<- {name} = {result!r}")
        return result
    return wrapper

def timing[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        ok = elapsed >= 0
        name = wrapper.__name__
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

**Keep the output reproducible.**
In real code you would print the raw `elapsed`.
The listing prints a deterministic check,
because the raw number changes every run while the `#:` marker stays constant.

**Stack the layers.**
`@trace` above `@timing` means `add = trace(timing(add))`,
so `trace`'s wrapper is the outermost layer and `timing`'s wrapper is inside it.

**Run the layers outside in.**
Calling `add(2, 3)` enters `trace`'s wrapper first.
The output order follows the wrapping order.
The outermost decorator prints first and last,
and each inner layer's output appears nested in between.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A coffee shop, object *Decorator* pattern

> Implement the object-oriented *Decorator* pattern for a coffee shop:
> plain drinks (Espresso, Cappuccino) and extra decorators
> (Whipped cream, Decaf, Extra shot).
> Build an espresso decorated with an extra shot and whipped cream,
> then print its cost and description.

<details>
<summary>Where to look</summary>

[The *Decorator* Pattern](../../Chapters/14_Techniques--Decorators.md#the-decorator-pattern)
builds pizzas from a base and wrapper objects that share one interface.
Define a `Protocol` for a drink, plain drink classes that satisfy it,
and a wrapper base class that holds one drink and forwards `cost` and `description`.
Each extra adds its own price and name to what the inner drink reports.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
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
        ...

    @property
    def cost(self) -> float:
        ...

    @property
    def description(self) -> str:
        ...

class Whipped(Extra):
    add_cost = 0.75

class Decaf(Extra):
    add_cost = 0.0

class ExtraShot(Extra):
    add_cost = 0.90
```

<details>
<summary>Done when</summary>

your espresso with an extra shot and whipped cream prints a description naming all three,
innermost first, and a cost equal to the espresso's price plus both extras' prices.
Wrapping the two extras in the other order changes the description and leaves the cost alone,
and `uv run ty check` passes.

<details>
<summary>Solution</summary>

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

**Share one interface.**
The listing has `pizza_decorator.py`'s shape with the menu changed.
`Espresso`, `Cappuccino`,
and `Extra` satisfy `Drink` by providing `cost` and `description`.
The type checker matches a `Protocol` structurally,
so none of the three needs to inherit from `Drink`.

A class-per-combination design needs a separate class for every decaf variant.
Here, adding a fourth extra means writing one class with one number in it.
The extras compose in any order,
since each layer reads `cost` and `description` from the one drink it wraps.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A class-level counter shared across every decorated function

> Write `trace` as a class-form decorator that also keeps a class-level counter shared across every decorated function,
> and report the total number of traced calls in the program.
> Note where the shared state lives compared to the per-instance `count` in `count_calls`.

<details>
<summary>Where to look</summary>

[A Class-Form Decorator with State](../../Chapters/14_Techniques--Decorators.md#a-class-form-decorator-with-state)
keeps `count` on each instance, one instance per decorated function.
A `ClassVar` on the decorator class is one value that every instance reads and writes through the class name.
Increment both counters in `__call__()`,
and use `update_wrapper()` so the instance keeps the function's name.

<details>
<summary>The shape</summary>

```python
# The shape of trace_counting.py
from collections.abc import Callable
from functools import update_wrapper
from typing import ClassVar

class trace_counting[**P, R]:
    # Shared by every decorated function:
    total_calls: ClassVar[int] = 0
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        ...

    def __call__(self, *args: P.args,
                 **kwargs: P.kwargs) -> R:
        ...

@trace_counting
def f(x: int) -> int:
    ...

@trace_counting
def g(x: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

after two calls to one decorated function and one call to another,
the two per-function counts read `2` and `1`, the class-level total reads `3`,
and every call prints its `->` and `<-` trace lines.
`uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

If you increment the shared counter with `self.total_calls += 1`,
the assignment creates an instance attribute on each `trace_counting` instance.
That instance attribute shadows the class attribute,
so `trace_counting.total_calls` stays at `0` and the last line prints `2 1 0`.
`ty` reports an `invalid-attribute-access` for assigning to a `ClassVar` through an instance.
The solution writes through the class name,
so every instance updates the one shared value.

```python
# trace_counting.py
from collections.abc import Callable
from functools import update_wrapper
from typing import ClassVar

class trace_counting[**P, R]:
    # Shared by every decorated function:
    total_calls: ClassVar[int] = 0
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.count = 0  # Per-function, like count_calls
        update_wrapper(self, func)

    def __call__(self, *args: P.args,
                 **kwargs: P.kwargs) -> R:
        self.count += 1
        trace_counting.total_calls += 1
        positional = [repr(a) for a in args]
        named = [f"{k}={v!r}" for k, v in kwargs.items()]
        arglist = ", ".join(positional + named)
        print(f"-> {self.__name__}({arglist})")
        result = self.func(*args, **kwargs)
        print(f"<- {self.__name__} = {result!r}")
        return result

@trace_counting
def f(x: int) -> int:
    return x + 1

@trace_counting
def g(x: int) -> int:
    return x * 2

f(1)
#: -> f(1)
#: <- f = 2
f(2)
#: -> f(2)
#: <- f = 3
g(3)
#: -> g(3)
#: <- g = 6
print(f.count, g.count, trace_counting.total_calls)
#: 2 1 3
```

**Count each function's calls.**
As with `count_calls`,
each decorated function gets its own instance of `trace_counting`,
so `f.count` and `g.count` track their own function's calls: `2` and `1`.

The two counters show the [class-attribute-versus-instance-attribute distinction](../../Chapters/09_Foundations--Class_Attributes.md).
`self.count` lives on each instance, one per decorated function.
`total_calls` lives on the class,
one value that every decorated function shares,
and `__call__()` reads and writes it through the class name.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A `memo` that works with and without parentheses

> Write a `memo` decorator that works both with and without parentheses,
> so `@memo` and `@memo(maxsize=10)` both decorate a function.
> Cache each result in a dictionary keyed by the arguments,
> and drop the oldest entry when the cache holds more than `maxsize` of them.
> Distinguish the two forms by checking whether a first argument arrived.

<details>
<summary>Where to look</summary>

[Decorators With Optional Parentheses](../../Chapters/14_Techniques--Decorators.md#decorators-with-optional-parentheses)
tests whether the function argument arrived and returns either the wrapper or a decorator.
Give `memo` a `func` parameter that defaults to `None` and a keyword-only `maxsize`.
A `dict` remembers insertion order,
so the first key is the oldest entry to drop.
Two `@overload` declarations tell the type checker about both call shapes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

@overload
def memo[**P, R](
    func: Callable[P, R]
) -> Callable[P, R]: ...

@overload
def memo[**P, R](
    *, maxsize: int = ...
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def memo[**P, R](
    func: Callable[P, R] | None = None, *,
    maxsize: int = 128
) -> Any:
    ...

@memo
def square(n: int) -> int:
    ...

@memo(maxsize=2)
def add(a: int, b: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

a function under `@memo` and another under `@memo(maxsize=2)` print when their bodies run.
A repeated call returns its cached result silently,
a third distinct call evicts the first so repeating the first call prints again,
a call with a keyword argument works, and both functions keep their `__name__`.
`uv run ty check` passes.

<details>
<summary>Solution</summary>

If you key the cache on `(args, kwargs)`, the first call, `square(4)`,
raises a `TypeError`.
The tuple holds a `dict`, which is unhashable,
so the tuple cannot be a dictionary key.
The type checker accepts that version,
so the failure shows up when the program runs.
The solution turns the keyword arguments into a tuple of name-value pairs,
so the key hashes whenever every argument does.

```python
# exercise_5.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

@overload
def memo[**P, R](
    func: Callable[P, R]
) -> Callable[P, R]: ...

@overload
def memo[**P, R](
    *, maxsize: int = ...
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def memo[**P, R](
    func: Callable[P, R] | None = None, *,
    maxsize: int = 128
) -> Any:
    def decorate(target: Callable[P, R]) -> Callable[P, R]:
        cache: dict[tuple[Any, ...], R] = {}

        @wraps(target)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, tuple(kwargs.items()))
            if key not in cache:
                cache[key] = target(*args, **kwargs)
                if len(cache) > maxsize:
                    del cache[next(iter(cache))]
            return cache[key]
        return wrapper
    return decorate if func is None else decorate(func)

@memo
def square(n: int) -> int:
    print(f"computing square({n})")
    return n * n

@memo(maxsize=2)
def add(a: int, b: int) -> int:
    print(f"computing add({a}, {b})")
    return a + b

print(square(4), square(4))
#: computing square(4)
#: 16 16
add(1, 2)
#: computing add(1, 2)
add(3, 4)
#: computing add(3, 4)
add(5, 6)  # A third entry, so add(1, 2) is evicted
#: computing add(5, 6)
add(5, 6)  # Still cached, so nothing prints
add(1, 2)  # Gone from the cache, so it runs again
#: computing add(1, 2)
print(square.__name__, add.__name__)
#: square add
```

**Describe both call shapes.**
The two `@overload` declarations tell the type checker which of the two shapes a given call has.
The implementation returns `Any` because `Any` satisfies both overloads.
The type checker verifies each call against the overloads,
not the implementation.
`square(4)` type-checks as an `int`,
and `memo(maxsize=2)` type-checks as a decorator you can apply to a function.

**Tell the two forms apart.**
The two decorations call `memo` two different ways.
The body tells them apart by what arrives in `func`.
Used bare, `@memo` calls `memo(square)`,
so `func` is the function and the decoration finishes immediately with `decorate(func)`.
Used with parentheses, `@memo(maxsize=2)` calls `memo(maxsize=2)` first.
That call leaves `func` as `None`, so `memo` returns `decorate`,
and Python applies `decorate` to `add`.

**Keep the forms distinct.**
The signature has one positional parameter, `func`,
so a positional argument always binds to it.
`maxsize` is keyword-only and must arrive by name.

**Key on every argument.**
The key records how each argument arrived.
`add(1, 2)` and `add(a=1, b=2)` make different keys,
so `memo` computes and caches each call separately.

**Drop the oldest entry.**
A dictionary preserves insertion order,
so `next(iter(cache))` is the oldest key.
Evicting the oldest key makes `memo` a first-in-first-out cache rather than the least-recently-used cache `functools.lru_cache` gives you.
A real implementation should choose the eviction policy that fits its callers.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. `retry(times)` in the function form

> Write a `retry(times)` decorator in the function form that calls the wrapped function again when it raises an exception,
> up to `times` attempts, and re-raises the last exception when they all fail.
> Check that `__name__` survives.

<details>
<summary>Where to look</summary>

[Decorators That Take Arguments](../../Chapters/14_Techniques--Decorators.md#decorators-that-take-arguments)
uses three nested functions: the outer takes the argument,
the middle takes the function, and the inner is the wrapper.
Catch the exception in a loop for all attempts but the last,
then make the final call outside any `try`.
Apply [`@wraps`](../../Chapters/14_Techniques--Decorators.md#wraps-keeps-the-runtime-interface)
in the wrapper.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from collections.abc import Callable
from functools import wraps
from exceptions import expect

def retry[**P, R](
    times: int
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...

@retry(times=3)
def flaky() -> str:
    ...

@retry(times=2)
def always_fails() -> str:
    ...
```

<details>
<summary>Done when</summary>

under `retry(times=3)`,
a function that raises an exception on its first two calls returns its result on the third.
Under `retry(times=2)`,
a function that always fails runs twice and its last exception reaches the caller,
as `expect()` shows.
`__name__` reports the original name, and `uv run ty check` passes.

<details>
<summary>Solution</summary>

If you re-raise the exception from inside the loop with a bare `raise` on the last attempt,
`retry` works at runtime.
But the type checker infers a path where the loop finishes and `wrapper()` returns `None` implicitly,
so `ty` reports an `invalid-return-type`.
The solution makes the final attempt outside the `try`.

```python
# exercise_6.py
from collections.abc import Callable
from functools import wraps
from exceptions import expect

def retry[**P, R](
    times: int
) -> Callable[[Callable[P, R]], Callable[P, R]]:
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

expect(RuntimeError, always_fails)
#: attempt 1 failed: no luck
#: [RuntimeError] no luck
```

**Keep the wrapped function's identity.**
`@wraps(func)` copies the wrapped function's metadata onto `wrapper`,
so `flaky.__name__` reports `flaky`, not `wrapper`.
Without `@wraps`, a log line or a test report that reads `__name__` shows `wrapper` for every retried function.
A traceback is the same either way.
It names each stack frame from the code object, which `wraps` leaves alone,
so the `wrapper` stack frame appears with or without `@wraps`.

**Make the last attempt unguarded.**
The final attempt meets two requirements at once.
It returns `R` on success,
so `wrapper()` has a return value on every path the type checker can see.
It also lets the last exception propagate to the caller,
since that attempt sits outside the `try`.

**Retry after any ordinary failure.**
Catching every `Exception` is a deliberate shortcut here.
A real `retry` should take the exception types to retry as an argument,
because some failures repeat on every attempt.
A `TypeError` from a bad call signature fails the same way each time,
so retrying it repeats the failure until the last attempt raises the `TypeError` to the caller.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. Two class-form decorators on methods

> Decorate one method of a small class with the class-form `repeat` from `repeat_class.py`,
> and a second method with `logged` from `method_decoration.py`.
> Call the first through an instance,
> then print the type of the object each method name refers to in the class.
> Explain why one class-form decorator works on a method and the other does not.

<details>
<summary>Where to look</summary>

[A Limitation: Methods Need a Descriptor](../../Chapters/14_Techniques--Decorators.md#a-limitation-methods-need-a-descriptor)
shows why binding `self` depends on what object the class stores under the method name.
Read both names from `Counter.__dict__` and check each result with `hasattr(obj, "__get__")`.
Compare what `__call__()` returns in `repeat` with what the `logged` instance is.

<details>
<summary>The shape</summary>

```python
# The shape of decorated_methods.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        ...

    def __call__[**P, R](
        self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        ...

class logged:
    def __init__(self, func: Callable) -> None:
        ...

    def __call__(self, *args: object,
                 **kwargs: object) -> object:
        ...

@dataclass
class Counter:
    total: int = 0

    @repeat(times=3)
    def bump(self, by: int) -> int:
        ...

    @logged
    def peek(self) -> int:
        ...
```

<details>
<summary>Done when</summary>

one call to the `repeat`-decorated method through an instance runs its body `times` times with that instance as `self`,
and your printout shows a `function` under one name and a `logged` instance under the other.
You can say which of the two objects has `__get__()` and why that decides whether `self` binds.

<details>
<summary>Solution</summary>

```python
# decorated_methods.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        if times < 1:
            raise ValueError(
                f"times must be >= 1, got {times}")
        self.times = times

    def __call__[**P, R](
        self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(self.times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper

class logged:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, *args: object,
                 **kwargs: object) -> object:
        print(f"logged: args={args}")
        return self.func(*args, **kwargs)

@dataclass
class Counter:
    total: int = 0

    @repeat(times=3)
    def bump(self, by: int) -> int:
        self.total += by
        return self.total

    @logged
    def peek(self) -> int:
        return self.total

counter = Counter()
print(counter.bump(2))
#: 6
bump = Counter.__dict__["bump"]
peek = Counter.__dict__["peek"]
print(type(bump).__name__, hasattr(bump, "__get__"))
#: function True
print(type(peek).__name__, hasattr(peek, "__get__"))
#: logged False
```

Both decorators are classes.
They differ in what each one leaves in `Counter`.

**Return a function that binds.**
`@repeat(times=3)` builds a `repeat` instance and then calls it with `bump`.
That `__call__()` returns `wrapper`, an ordinary function.
A function has `__get__()`,
so `counter.bump` binds `counter` to `wrapper` like any other method.
The name `bump` refers to `wrapper`.
The `repeat` instance finishes its work at decoration time.

**Store an instance that cannot bind.**
`@logged` stores the `logged` instance in the class.
That instance has no `__get__()`,
so `counter.peek` returns the `logged` instance unbound.
Calling `counter.peek()` then runs `peek()` with no `self`.
The call fails the way `method_decoration.py` fails,
but the `TypeError` from `counter.peek()` reports a missing `self`,
since `self` is `peek()`'s one parameter.

**Read what the class stores.**
Reading the two names from `Counter.__dict__` gets each entry from the class namespace,
before any binding, so each `print()` shows the object the class stores.

The class form fails on a method only when an instance of the decorator class replaces the method.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
