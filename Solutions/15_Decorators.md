# Decorators: Solutions

## 1. A `Syrup` extra

```python
# exercise_1.py
class Cappuccino:
    cost = 1.75
    description = "Cappuccino"

class Extra:
    add_cost = 0.0
    name = ""

    def __init__(self, drink) -> None:
        self.drink = drink

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"

class Decaf(Extra):
    add_cost = 0.0
    name = "Decaf"

class Syrup(Extra):
    add_cost = 0.30
    name = "Syrup"

order = Syrup(Decaf(Cappuccino()))
print(f"{order.description}: ${order.cost:.2f}")
#: Cappuccino + Decaf + Syrup: $2.05
```

`Syrup` needs nothing beyond the two class attributes `Extra` already
reads: `add_cost` and `name`. `cost` and `description` are inherited
unchanged from `Extra`, which forwards to whatever it wraps and adds
its own contribution. Wrapping in any order still works: `Syrup` here
wraps a `Decaf`, which wraps a `Cappuccino`, and each layer only knows
about the one directly inside it.

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

## 3. A pizza shop, object *Decorator* pattern

```python
# exercise_3.py
class Pizza:
    def cost(self) -> float:
        raise NotImplementedError

    def description(self) -> str:
        raise NotImplementedError

class Margherita(Pizza):
    def cost(self) -> float:
        return 8.0

    def description(self) -> str:
        return "Margherita"

class Hawaiian(Pizza):
    def cost(self) -> float:
        return 9.0

    def description(self) -> str:
        return "Hawaiian"

class ToppingDecorator(Pizza):
    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza

class Garlic(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 0.5

    def description(self) -> str:
        return self.pizza.description() + " + Garlic"

class Olives(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 0.75

    def description(self) -> str:
        return self.pizza.description() + " + Olives"

class Feta(ToppingDecorator):
    def cost(self) -> float:
        return self.pizza.cost() + 1.0

    def description(self) -> str:
        return self.pizza.description() + " + Feta"

pizza = Feta(Olives(Margherita()))
print(f"{pizza.description()}: ${pizza.cost():.2f}")
#: Margherita + Olives + Feta: $9.75
```

This is `coffee.py`'s shape exactly, renamed: a base `Pizza`, plain
pizza types with their own `cost()`/`description()`, and a
`ToppingDecorator` base that every topping subclasses, wrapping one
`Pizza` and forwarding through the same two-method interface. Adding
a fourth topping needs one more small class, not a new class for every
pizza-and-toppings combination.

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
