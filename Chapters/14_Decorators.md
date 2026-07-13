# Decorators

A decorator is a callable that you apply to a function or a class.
The decorator receives the thing it decorates, does something with it,
then returns a result, which Python binds to the original name.
Most decorators are applied to functions, so that is where we start.

To apply a decorator,
put `@` followed by the decorator name on the line above the definition.
For simplicity, we use an untyped `Callable` here:


```python
# simple_decoration.py
from collections.abc import Callable

def hijack(func: Callable) -> Callable:
    def doesnt_matter() -> None:
        print("Replacement behavior")

    return doesnt_matter

@hijack
def cheese() -> None:
    print("Wensleydale")

cheese()
#: Replacement behavior
```

Later, [Maintaining the Wrapped Interface](#maintaining-the-wrapped-interface) shows decorators with types.

The `@hijack` above `cheese()` means:

    cheese = hijack(cheese)

`hijack` returns `doesnt_matter`, which Python assigns to the name `cheese`,
so `cheese` now refers to `doesnt_matter`.
Calling `cheese()` runs `doesnt_matter` which never calls `func` and prints its own message instead.
The original `cheese()` behavior never happens.

Since decoration binds the local function to the name `cheese`,
the local name (`doesnt_matter()`) can be anything.
The common convention is to name it `wrapper()`.

A typical decorator returns a wrapper that does some work,
calls the original function, then does some more work:

```python
# add_behavior.py
from collections.abc import Callable

def add_behavior(func: Callable) -> Callable:
    def wrapper() -> None:
        print("Some work")
        func()
        print("Some more work")

    return wrapper

@add_behavior
def cheese() -> None:
    print("Wensleydale")

cheese()
#: Some work
#: Wensleydale
#: Some more work
```

Decoration is a simple kind of [metaprogramming](17_Metaprogramming.md).
The same idea appears in design patterns as the *Decorator* pattern:
wrap an object to add responsibilities to it,
while keeping the wrapped object's interface so the wrapping stays invisible to the code that uses it.

## Maintaining the Wrapped Interface

This decorator traces calls:

```python
# tracer.py
from collections.abc import Callable
from functools import wraps

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        positional = [repr(a) for a in args]
        named = [f"{k}={v!r}" for k, v in kwargs.items()]
        arglist = ", ".join(positional + named)
        print(f"-> {func.__name__}({arglist})")  # type: ignore
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")  # type: ignore
        return result
    return wrapper

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
```

`functools.wraps` copies the original function's metadata onto the wrapper:
its name, docstring, and other attributes.
Without it, the decorated `add` would report its name as `wrapper` and lose its docstring,
misleading debuggers, `help()`, and documentation tools.
`wraps` is optional but there is rarely a reason to omit it.

`wraps` keeps the runtime interface.
The type parameters (introduced in [Static Typing](08_Static_Typing.md#generic-functions-and-classes)) keep the static one.
`trace[**P, R]` declares two of them.
`R` is the wrapped function's return type.
`**P` is a *parameter specification* (`ParamSpec`).
It captures the whole parameter list of the wrapped function as a single unit,
names and types included.
`func: Callable[P, R]` reads as "a function whose parameters are `P` and whose result is `R`,"
and returning `Callable[P, R]` promises that the wrapper has that same signature.

Inside the wrapper, `*args: P.args` and `**kwargs: P.kwargs` are the two halves of that captured list.
`P.args` is the positional part and `P.kwargs` the keyword part.
You may only use them together,
as the `*args` and `**kwargs` of a function typed with `P`.
They bind the wrapper's arguments to the parameters `P` captured,
so the checker accepts `add(2, 3)` but rejects `add("x")` or `add(2, 3, 4)`,
even though the body of `wrapper()` forwards anything.
Without `P` you would fall back to `*args: Any, **kwargs: Any`,
and the wrapper would swallow any arguments,
discarding the signature the decorator is meant to preserve.

The `# type: ignore` comments mark the one place the checker cannot follow:
a bare `Callable` is not guaranteed to have a `__name__` attribute,
though every actual function does.

## Decorators That Take Arguments

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
#: Hello, Bob
#: Hello, Bob
#: Hello, Bob
```

`@repeat(times=3)` first evaluates `repeat(times=3)`,
which returns the real decorator, which then wraps `greet`.
Inside `wrapper()`, the first call to `func` happens before the loop,
so `result` always holds a value of type `R` to return;
the loop adds the remaining `times - 1` calls.

## Decorators as Classes

A decorator only has to be a callable that takes a function and returns a callable.
A class with `__call__()` is a callable,
so a decorator can be a class instead of a function.
The class form separates the two phases cleanly: the constructor runs once,
at decoration, and `__call__()` runs on every call to the decorated function.
Here is the `trace` decorator written as a class:

```python
# trace_class.py
from collections.abc import Callable
from functools import update_wrapper

class trace[**P, R]:
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        update_wrapper(self, func)  # Copy __name__, __doc__, etc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        positional = [repr(a) for a in args]
        named = [f"{k}={v!r}" for k, v in kwargs.items()]
        arglist = ", ".join(positional + named)
        print(f"-> {self.func.__name__}({arglist})")  # type: ignore
        result = self.func(*args, **kwargs)
        print(f"<- {self.func.__name__} = {result!r}")  # type: ignore
        return result

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
```

`@trace` runs `add = trace(add)`,
so the constructor receives the function and stores it.
The name `add` now refers to a `trace` instance,
and calling `add(2, 3)` invokes `__call__()`.
`functools.update_wrapper()` does for a class instance what `functools.wraps` does for a function;
`wraps` is itself a thin convenience layer over `update_wrapper()`.
It copies the wrapped function's metadata across.
Like the function form, the class is generic in `**P` and `R`,
so `__call__()` keeps the wrapped signature and `add(2, 3)` still type-checks as an `int`.

Because the instance can hold attributes, state between calls is natural.
A class-based decorator that counts calls keeps the count on the instance:

```python
# count_calls.py
from collections.abc import Callable
from functools import update_wrapper

class count_calls[**P, R]:
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.count = 0
        update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.count += 1
        print(f"call {self.count} of {self.func.__name__}")  # type: ignore
        return self.func(*args, **kwargs)

@count_calls
def hello() -> None:
    print("hello")

if __name__ == "__main__":
    hello()
    hello()
    print(hello.count)  # The state lives on the decorator instance
#: call 1 of hello
#: hello
#: call 2 of hello
#: hello
#: 2
```

The class form shifts in an important way when the decorator itself takes arguments.
Without arguments, the constructor receives the function.
With arguments, the constructor receives the arguments,
and `__call__()` receives the function and returns the wrapper:

```python
# repeat_class.py
from collections.abc import Callable
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        self.times = times  # The decoration arguments

    def __call__[**P, R](
        self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(self.times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper

@repeat(times=3)
def greet(name: str) -> None:
    print(f"Hello, {name}")

if __name__ == "__main__":
    greet("Bob")
#: Hello, Bob
#: Hello, Bob
#: Hello, Bob
```

Compare the two cases.
`@trace` with no arguments calls `trace(add)`.
The function goes straight to the constructor.
`@repeat(times=3)` calls `repeat(times=3)` first, producing an instance,
then applies that instance to `greet`.
The arguments go to the constructor, and the function arrives later,
at `__call__()`.
The function form hides this shift inside an extra nested `def`.
The class form makes it visible.
The function moves from `__init__()` to `__call__()` when the decorator gains arguments.

The form you choose is mostly a matter of taste.
Both forms preserve the wrapped function's exact signature for the type checker,
using the same `**P` and `R` type parameters.
The function form is more compact.
The class form reads better when the decorator carries state or grows complicated,
because the phases are separate methods instead of nested closures.
That argument-capturing class-based decorator scales up to small frameworks.
A build tool or task runner can offer a `@rule(target, *deps)` decorator.
Its constructor records the target and dependencies.
Its `__call__()` registers the decorated function in a class-level table with that metadata.
A driver later walks the table to run things in order.
The decorator becomes the registration mechanism for the whole system.

A context manager can also act as a decorator,
bracketing every call with its setup and cleanup code.
[Context Managers](15_Context_Managers.md#a-context-manager-as-a-decorator) shows `contextlib.ContextDecorator`.

## Stacking Decorators

You can apply more than one decorator.
They nest from the bottom up:

```python
# stacking.py
from repeat_class import repeat
from trace_class import trace

@trace
@repeat(times=2)
def greet(name: str) -> str:
    print(f"Hello, {name}")
    return name

if __name__ == "__main__":
    greet("Bob")
#: -> greet('Bob')
#: Hello, Bob
#: Hello, Bob
#: <- greet = 'Bob'
```

This is `greet = trace(repeat(times=2)(greet))`.
`@repeat(times=2)` wraps `greet()` first, then `@trace` wraps that result,
so a single `greet("Bob")` traces one call whose body runs twice.
Each decorator wraps the result of the one below it.
Stacking works because each wrapper preserves the interface of what it wraps:
every layer looks like the original function,
so the layers compose to any depth.

## Decorating Classes

You can apply a decorator to a class instead of a function.
This one registers every class it decorates, in `registry`:

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
#: ['Espresso', 'Latte']
```

`register()` returns `cls` unchanged, so this decoration adds no wrapper at all;
it exists only for its side effect of recording the class.
A class decorator can also return a replacement class,
just as a function decorator returns a replacement function.

[Metaprogramming](17_Metaprogramming.md#self-registration-of-subclasses) shows `__init_subclass__()`,
which builds a registry like this without a decorator.

## The Decorator Pattern

The `@` syntax decorates a function or class once, at definition,
so every call or every instance gets the wrapping.
Sometimes you want the choice made later:
add responsibilities to individual objects at runtime,
and let each caller decide which responsibilities to add.
That is the object-oriented *Decorator* pattern.

Consider a pizza shop.
A class for every pizza-and-topping combination explodes: Margherita,
Margherita with olives, Margherita with olives and feta, and so on.
Each new topping doubles the menu.

Instead, model the toppings as decorators.
A plain pizza knows its own cost and description.
A topping dynamically wraps a pizza, adds to the cost,
and adds to the description.
Because a topping is itself a pizza, you can wrap a topping in another topping.

![Margherita and Hawaiian satisfy Pizza directly; Topping wraps a Pizza and also satisfies it, so Garlic, Olives, and Feta can wrap any pizza, including each other](_images/decorator_pattern)

```python
# pizza_decorator.py
from typing import Protocol

class Pizza(Protocol):
    @property
    def cost(self) -> float: ...
    @property
    def description(self) -> str: ...

class Margherita:
    cost = 8.00
    description = "Margherita"

class Hawaiian:
    cost = 9.50
    description = "Hawaiian"

class Topping:
    add_cost = 0.0
    name = ""

    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza

    @property
    def cost(self) -> float:
        return self.pizza.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.pizza.description} + {self.name}"

class Garlic(Topping):
    add_cost = 0.50
    name = "Garlic"

class Olives(Topping):
    add_cost = 0.75
    name = "Olives"

class Feta(Topping):
    add_cost = 1.25
    name = "Feta"

if __name__ == "__main__":
    order = Feta(Olives(Margherita()))
    print(f"{order.description}: ${order.cost:.2f}")

    haw = Garlic(Feta(Hawaiian()))
    print(f"{haw.description}: ${haw.cost:.2f}")
#: Margherita + Olives + Feta: $10.00
#: Hawaiian + Feta + Garlic: $11.25
```

`Feta(Olives(Margherita()))` is the object version of stacked `@` decorators.
Each topping wraps the pizza inside it and forwards through the same two-property interface,
`cost` and `description`.
The `Pizza` `Protocol` describes that interface.
Both the plain pizzas and the toppings satisfy it structurally,
with no shared base class required.
This is the structural typing from [Static Typing](08_Static_Typing.md#structural-typing-with-protocols).

Adding a new topping means adding one class.
Changing the price of a topping means changing one number, in one place.
Compare that to a class per combination,
where a price change touches every class that includes that topping.

```python
# test_pizza_decorator.py
from pizza_decorator import Feta, Garlic, Hawaiian, Margherita, Olives

def test_plain_pizza() -> None:
    pizza = Hawaiian()
    assert pizza.cost == 9.50
    assert pizza.description == "Hawaiian"

def test_stacked_toppings() -> None:
    order = Feta(Olives(Margherita()))
    assert order.cost == 10.00
    assert order.description == (
        "Margherita + Olives + Feta")

def test_single_topping() -> None:
    order = Garlic(Margherita())
    assert order.cost == 8.50
    assert order.description == "Margherita + Garlic"
```

## Exercises

1.  Add a `Mushroom` topping (cost 0.60) and use it to build a Hawaiian with mushroom and feta.
2.  Write a `timing` decorator that prints how long the wrapped function took,
    using `time.perf_counter()`.
    Apply it together with `@trace` and predict the order of the output.
3.  Implement the object *Decorator* pattern for a coffee shop:
    plain drinks (Espresso, Cappuccino) and extra decorators (Whipped cream, Decaf, Extra shot).
    Build an espresso decorated with an extra shot and whipped cream,
    then print its cost and description.
4.  Write `trace` as a class-based decorator that also keeps a class-level counter shared across every decorated function,
    and report the total number of traced calls in the program.
    Note where the shared state lives compared to the per-instance `count` in `count_calls`.
