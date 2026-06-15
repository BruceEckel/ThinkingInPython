# Decorators

Python builds decoration into the language. You write `@something` above a
function or a class, and Python wraps it. The same idea appears in *Design
Patterns* as the *decorator* pattern: wrap an object to add responsibilities to
it, while keeping the wrapped object's interface so the wrapping stays invisible
to the code that uses it.

This chapter starts with the language feature, because that is where you meet
decoration first. Then it shows the object-level pattern, for when you need to
decorate individual objects at runtime.

## The `@` Syntax

A *decorator* is a callable that takes a function and returns a function. The
returned function usually does some work, calls the original, and does some more
work. Here is a decorator that traces calls:

```python
# trace.py
from collections.abc import Callable
from functools import wraps


def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"-> {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")
        return result
    return wrapper


@trace
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    add(2, 3)
```

The output is:

    -> add(2, 3)
    <- add = 5

The `@trace` above `add` is just sugar. It means:

    add = trace(add)

`trace` returns `wrapper`, so the name `add` now refers to `wrapper`. Calling
`add(2, 3)` runs the wrapper, which prints, calls the real `add`, prints again,
and returns the result.

`functools.wraps` copies the original function's name and docstring onto the
wrapper, so the wrapped function still looks like itself when you inspect it.

### Decorators That Take Arguments

To pass arguments to a decorator, add another layer. A decorator with arguments
is a function that returns a decorator:

```python
# repeat.py
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorate


@repeat(times=3)
def greet(name: str) -> str:
    print(f"Hello, {name}")
    return name


if __name__ == "__main__":
    greet("Bob")
```

`@repeat(times=3)` calls `repeat(3)`, which returns the real decorator, which
then wraps `greet`. The greeting prints three times.

### Stacking Decorators

You can apply more than one decorator. They nest from the bottom up:

    @trace
    @repeat(times=2)
    def f() -> None: ...

This is `f = trace(repeat(2)(f))`. Each decorator wraps the result of the one
below it. That nesting is the transparency the pattern depends on. Every layer
presents the same interface, so the layers compose.

### Decorating Classes

A decorator can take a class instead of a function. This one records every class
it is applied to:

```python
# register.py
registry: dict[str, type] = {}


def register(cls: type) -> type:
    registry[cls.__name__] = cls
    return cls


@register
class Espresso:
    ...


@register
class Latte:
    ...


if __name__ == "__main__":
    print(sorted(registry))
```

The output is `['Espresso', 'Latte']`. The [Metaprogramming](09_Metaprogramming.md)
chapter shows `__init_subclass__`, which builds a registry like this without a
decorator.

## The Decorator Pattern

The `@` syntax decorates a function or class once, at definition. Every call or
every instance gets the wrapping. Sometimes you want to add responsibilities to
one object at runtime, and let the caller choose which responsibilities to add.
That is the object decorator pattern.

Consider a coffee shop. A class for every drink-and-extra combination explodes:
espresso, espresso with whipped cream, decaf espresso with whipped cream, and so
on. Each new extra doubles the menu.

Instead, model the extras as decorators. A plain drink knows its own cost and
description. An extra wraps a drink, adds to the cost, and adds to the
description. Because an extra is itself a drink, you can wrap an extra in another
extra.

```python
# coffee.py
from __future__ import annotations

from typing import Protocol


class Drink(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...


class Espresso:
    cost = 1.50
    description = "espresso"


class Cappuccino:
    cost = 1.75
    description = "cappuccino"


class Extra:
    "Base object decorator: wraps a Drink and adds to it."
    add_cost = 0.0
    name = ""

    def __init__(self, drink: Drink) -> None:
        self.drink = drink

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"


class Whipped(Extra):
    add_cost = 0.50
    name = "whipped cream"


class Decaf(Extra):
    add_cost = 0.0
    name = "decaf"


class ExtraShot(Extra):
    add_cost = 0.75
    name = "extra shot"


if __name__ == "__main__":
    order = Whipped(ExtraShot(Espresso()))
    print(f"{order.description}: ${order.cost:.2f}")

    plain = Cappuccino()
    print(f"{plain.description}: ${plain.cost:.2f}")
```

The output is:

    espresso + extra shot + whipped cream: $2.75
    cappuccino: $1.75

`Whipped(ExtraShot(Espresso()))` is the object version of stacked `@`
decorators. Each extra wraps the drink inside it and forwards through the same
two-property interface, `cost` and `description`. The `Drink` `Protocol`
describes that interface. Both the plain drinks and the extras satisfy it
structurally, with no shared base class required. This is the structural typing
from the [Static Type Checking](04_Static_Type_Checking.md) chapter.

Adding a new extra means adding one class. Changing the price of an extra means
changing one number, in one place. Compare that to a class per combination, where
a price change touches every class that includes that extra.

A test fixes the behavior:

```python
# test_coffee.py
from coffee import Cappuccino, Decaf, Espresso, ExtraShot, Whipped


def test_plain_drink() -> None:
    cap = Cappuccino()
    assert cap.cost == 1.75
    assert cap.description == "cappuccino"


def test_stacked_extras() -> None:
    order = Whipped(ExtraShot(Espresso()))
    assert order.cost == 2.75
    assert order.description == (
        "espresso + extra shot + whipped cream")


def test_decaf_adds_no_cost() -> None:
    order = Decaf(Espresso())
    assert order.cost == 1.50
    assert order.description == "espresso + decaf"
```

## Exercises

1.  Add a `Syrup` extra (cost 0.30) and use it to build a decaf latte with
    syrup.
2.  Write a `timing` decorator that prints how long the wrapped function took,
    using `time.perf_counter`. Apply it together with `@trace` and predict the
    order of the output.
3.  Implement the object decorator pattern for a pizza shop: plain pizzas
    (Margherita, Hawaiian) and topping decorators (Garlic, Olives, Feta). Build a
    Margherita decorated with Olives and Feta, then print its cost and
    description.
