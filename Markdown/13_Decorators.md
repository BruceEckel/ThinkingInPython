# Decorators

Python builds decoration into the language.
You write `@something` above a function or a class, and Python wraps it.
The same idea appears in *Design Patterns* as the *decorator* pattern:
wrap an object to add responsibilities to it,
while keeping the wrapped object's interface so the wrapping stays invisible to the code that uses it.

This chapter starts with the language feature,
because that is where you meet decoration first.
Then it shows the object-level pattern,
for when you need to decorate individual objects at runtime.

## The `@` Syntax

A *decorator* is a callable that takes a function and returns a function.
The returned function usually does some work, calls the original,
and does some more work.
Here is a decorator that traces calls:

```python
# trace.py
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


@trace
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    add(2, 3)
```

The output is:

    -> add(2, 3)
    <- add = 5

The `@trace` above `add` means:

    add = trace(add)

`trace` returns `wrapper`, so the name `add` now refers to `wrapper`.
Calling `add(2, 3)` runs the wrapper, which prints, calls the real `add`,
prints again, and returns the result.

`functools.wraps` copies the original function's name and docstring onto the wrapper,
so the wrapped function still looks like itself when you inspect it.

### Decorators That Take Arguments

To pass arguments to a decorator, add another layer.
A decorator with arguments is a function that returns a decorator:

```python
# repeat.py
from collections.abc import Callable
from functools import wraps


def repeat[**P, R](
        times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
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

`@repeat(times=3)` calls `repeat(3)`, which returns the real decorator,
which then wraps `greet`.
The greeting prints three times.

### Decorators as Classes

A decorator only has to be a callable that takes a function and returns a callable.
A class with `__call__` is a callable,
so a decorator can be a class instead of a function.
The class form separates the two phases cleanly: the constructor runs once,
when the function is decorated,
and `__call__` runs on every call to the decorated function.
Here is the `trace` decorator written as a class:

```python
# trace_class.py
from collections.abc import Callable
from functools import update_wrapper
from typing import Any


class trace:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        update_wrapper(self, func)  # copy __name__, __doc__, etc.

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"-> {self.func.__name__}{args}")  # type: ignore
        result = self.func(*args, **kwargs)
        print(f"<- {self.func.__name__} = {result!r}")  # type: ignore
        return result


@trace
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    add(2, 3)
```

`@trace` runs `add = trace(add)`,
so the constructor receives the function and stores it.
The name `add` now refers to a `trace` instance,
and calling `add(2, 3)` invokes `__call__`.
`functools.update_wrapper` does for a class instance what `functools.wraps` does for a function:
it copies the wrapped function's name and docstring across.

Because the instance can hold attributes, state between calls is natural.
A class decorator that counts calls keeps the count on the instance,
with no closure trick:

```python
# count_calls.py
from collections.abc import Callable
from functools import update_wrapper
from typing import Any


class count_calls:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.count = 0
        update_wrapper(self, func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1
        print(f"call {self.count} of {self.func.__name__}")  # type: ignore
        return self.func(*args, **kwargs)


@count_calls
def hello() -> None:
    print("hello")


if __name__ == "__main__":
    hello()
    hello()
    print(hello.count)  # 2: the state lives on the decorator instance
```

The class form shifts in an important way when the decorator itself takes arguments.
Without arguments, the constructor receives the function.
With arguments, the constructor receives the *arguments*,
and `__call__` receives the function and returns the wrapper:

```python
# repeat_class.py
from collections.abc import Callable
from functools import wraps
from typing import Any


class repeat:
    def __init__(self, times: int) -> None:
        self.times = times  # the decoration arguments

    def __call__(
        self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            for _ in range(self.times):
                result = func(*args, **kwargs)
            return result
        return wrapper


@repeat(times=3)
def greet(name: str) -> None:
    print(f"Hello, {name}")


if __name__ == "__main__":
    greet("Bob")
```

Compare the two cases.
`@trace` with no arguments calls `trace(add)`:
the function goes straight to the constructor.
`@repeat(times=3)` calls `repeat(3)` first, producing an instance,
then applies that instance to `greet`: the arguments go to the constructor,
and the function arrives later, at `__call__`.
The function form hides this shift inside an extra nested `def`.
The class form makes it visible:
the function moves from `__init__` to `__call__` the moment the decorator gains arguments.

Which form to use is mostly taste.
The function form is more compact,
and with `ParamSpec` it preserves the wrapped function's exact signature for the type checker,
where the class form erases it to `Callable[..., Any]`.
The class form reads better when the decorator carries state or grows complicated,
because the phases are separate methods instead of nested closures.
That argument-capturing class decorator scales up to small frameworks:
a build tool or task runner can offer a `@rule(target, *deps)` decorator whose constructor records the target and dependencies,
whose `__call__` registers the decorated function in a class-level table with that metadata,
and whose driver later walks the table to run things in order.
The decorator becomes the registration mechanism for the whole system.

### Stacking Decorators

You can apply more than one decorator.
They nest from the bottom up:

    @trace
    @repeat(times=2)
    def f() -> None: ...

This is `f = trace(repeat(2)(f))`.
Each decorator wraps the result of the one below it.
That nesting is the transparency the pattern depends on.
Every layer presents the same interface, so the layers compose.

### Decorating Classes

A decorator can take a class instead of a function.
This one records every class it is applied to:

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

The output is `['Espresso', 'Latte']`.
The [Metaprogramming](15_Metaprogramming.md) chapter shows `__init_subclass__`,
which builds a registry like this without a decorator.

## The Decorator Pattern

The `@` syntax decorates a function or class once, at definition.
Every call or every instance gets the wrapping.
Sometimes you want to add responsibilities to one object at runtime,
and let the caller choose which responsibilities to add.
That is the object *Decorator* pattern.

Consider a coffee shop.
A class for every drink-and-extra combination explodes: espresso,
espresso with whipped cream, decaf espresso with whipped cream, and so on.
Each new extra doubles the menu.

Instead, model the extras as decorators.
A plain drink knows its own cost and description.
An extra wraps a drink, adds to the cost, and adds to the description.
Because an extra is itself a drink, you can wrap an extra in another extra.

```python
# coffee.py

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

`Whipped(ExtraShot(Espresso()))` is the object version of stacked `@` decorators.
Each extra wraps the drink inside it and forwards through the same two-property interface,
`cost` and `description`.
The `Drink` `Protocol` describes that interface.
Both the plain drinks and the extras satisfy it structurally,
with no shared base class required.
This is the structural typing from the [Static Typing](08_Static_Typing.md) chapter.

Adding a new extra means adding one class.
Changing the price of an extra means changing one number, in one place.
Compare that to a class per combination,
where a price change touches every class that includes that extra.

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

1.  Add a `Syrup` extra (cost 0.30) and use it to build a decaf latte with syrup.
2.  Write a `timing` decorator that prints how long the wrapped function took,
    using `time.perf_counter`.
    Apply it together with `@trace` and predict the order of the output.
3.  Implement the object *Decorator* pattern for a pizza shop:
    plain pizzas (Margherita, Hawaiian) and topping decorators (Garlic, Olives, Feta).
    Build a Margherita decorated with Olives and Feta,
    then print its cost and description.
4.  Write `trace` as a class decorator that also keeps a class-level counter shared across every decorated function,
    and report the total number of traced calls in the program.
    Note where the shared state lives compared to the per-instance `count` in `count_calls`.
