# Decorators

> The same few lines of logging or timing belong in many functions,
> and none of those functions is about logging or timing.
> A decorator wraps that behavior around a function from outside.

Logging, timing, retrying,
and validating arguments are *cross-cutting concerns*:
they show up across many unrelated functions.
Writing them into each function's own body copies the same few lines into every function that needs them.
A change to that logic then means editing every copy.

A decorator is a callable that you apply to a function or a class.
The decorator receives the function or class it decorates,
does something with it, then returns a result,
which Python binds to the original name.
Most decorators apply to functions.

## What `@` Does {#what-at-does}

To apply a decorator,
put `@` followed by the decorator name on the line above the definition.

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

The `@hijack` above `cheese()` means:

    cheese = hijack(cheese)

The `@` line is *syntactic sugar* for that assignment:
the same call and the same rebinding,
written above the function instead of after it.
`hijack` returns `doesnt_matter`, which Python assigns to the name `cheese`,
so `cheese` now refers to `doesnt_matter`.
The original body of `cheese()` never runs.

Since Python binds the returned function to the name `cheese`, the local name
(`doesnt_matter()`) can be anything.
Convention calls it `wrapper()`.

A typical decorator returns a wrapper that does some work,
calls the original function, then does some more work:

```python
# typical_decorator.py
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

A decorator that forgets its `return wrapper` returns `None`,
so Python binds `cheese` to `None`.
Python reports the failure at the next call to `cheese()`,
not at the decoration that caused it.
The error is a `TypeError` saying that a `NoneType` object is not callable.

The decorator runs when Python executes the `def`,
not when you call the decorated function:

```python
# decoration_time.py
from collections.abc import Callable

def announce(func: Callable) -> Callable:
    print("Decorating")
    def wrapper() -> None:
        print("Calling")
        func()
    return wrapper

@announce
def cheese() -> None:
    print("Wensleydale")
#: Decorating

print("Definitions done")
#: Definitions done
cheese()
#: Calling
#: Wensleydale
```

The body of `wrapper()` is the one part of `announce` that runs at the call.

`wrapper()` is a [*closure*](40_Functional--Foundations.md#closures).
Defined inside its decorator, it refers to `func`,
a variable from the enclosing scope, not one of its own parameters.
Python keeps `func` alive as long as `wrapper()` exists,
so `func` outlives the decorator call that received it.
A call to `cheese()`, long after decoration finished,
still calls the original `cheese` function through `func`.

Decoration is a simple kind of [metaprogramming](17_Techniques--Metaprogramming.md).
The same idea appears in design patterns as the [*Decorator* pattern](#the-decorator-pattern):
wrap an object to add responsibilities to it,
while keeping the wrapped object's interface.
Code written for the wrapped object then works unchanged with the wrapper.

## Maintaining the Wrapped Interface

The wrappers so far take zero parameters,
so `add_behavior` works on a function that takes zero arguments and fails on any other.
With `add_behavior` on a `def add(a, b)`,
the call `add(2, 3)` raises a `TypeError`.
The wrapper takes zero positional arguments.
The call passes two.

A wrapper that must accept any function's arguments uses the [argument-unpacking pattern](05_Foundations--Functions.md#unpacking-arguments).
The wrapper collects the arguments with `*args, **kwargs` and passes them on to the original function.
Here, the `trace` decorator traces calls, and its `wrapper()` takes that shape.
The helper `call_text()` formats a call as text, such as `add(2, b=3)`,
so `wrapper()` holds only the trace lines, the forwarded call, and the return:

```python
# tracer.py
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

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
```

### `wraps` Keeps the Runtime Interface

`functools.wraps` copies the original function's metadata onto the wrapper.
It copies the attributes named in the tuple `functools.WRAPPER_ASSIGNMENTS`:
`__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotate__`,
and `__type_params__`.
It also merges the original's `__dict__` into the wrapper's `__dict__`.
Without `wraps`, the decorated `add` reports its name as `wrapper` and loses its docstring,
so debuggers, `help()`,
and documentation tools show the wrapper's metadata instead of the function's metadata.
`wraps` is optional.
Nearly every wrapper should use it.

`tracer.py` relies on that copy.
Inside `wrapper()`, the name `wrapper` refers to the wrapper function itself,
the same object now bound to `add`, and `wraps` has set its `__name__` to `add`.

`wraps` also sets `__wrapped__` on the wrapper, pointing at the original.
A call to `add.__wrapped__(2, 3)` runs the original `add` and bypasses the tracing.
`inspect.signature()` follows the `__wrapped__` chain automatically.

The tests verify two things: the wrapper reports the original function's name,
and it still returns the original result:

```python
# test_tracer.py
from tracer import trace

def test_trace_preserves_name() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add.__name__ == "add"

def test_trace_returns_original_result() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
```

### `**P` and `R` Keep the Static Interface {#p-and-r-keep-the-static-interface}

`wraps` keeps the runtime interface.
The [type parameters](08_Foundations--Static_Types.md#generic-functions-and-classes)
keep the static one.
`trace[**P, R]` declares two of them.
`R` is the wrapped function's return type.
`**P` is a *parameter specification* (`ParamSpec`).
It captures the whole parameter list of the wrapped function as a single unit,
names and types included.
`func: Callable[P, R]` reads as "a function whose parameters are `P` and whose result is `R`,"
and returning `Callable[P, R]` declares that the wrapper has that same signature.

Inside the wrapper, `*args: P.args` and `**kwargs: P.kwargs` are the two halves of that captured list.
`P.args` is the positional part and `P.kwargs` the keyword part.
They must appear together,
as the `*args` and `**kwargs` of a function typed with `P`.
They bind the wrapper's arguments to the parameters captured by `**P`.
The type checker then accepts `add(2, 3)` but rejects `add("x")` or `add(2, 3, 4)`,
although the body of `wrapper()` forwards anything.
Without `**P` you fall back to `*args: Any, **kwargs: Any`.
The wrapper then accepts any arguments,
discarding the signature the decorator should preserve.

`R` checks the wrapper's result the same way.
A wrapper that calls `func(*args, **kwargs)` and drops the result makes every decorated function return `None`.
The `-> R` annotation lets the type checker report the missing `return`.

### A Coroutine Function Needs an `async` Wrapper {#coroutine-needs-async-wrapper}

`trace` prints the value `func` returns as the function's result.
That is correct for an ordinary function,
whose body runs to completion inside the call,
and wrong for a generator function or an `async def` function.
Decorating a coroutine function succeeds, and so does calling it,
but the trace reports the wrong result.
`func(*args, **kwargs)` returns a coroutine object immediately,
before any of the coroutine's body runs,
so `result` holds that coroutine object rather than the value the coroutine eventually produces.
The trace line then prints `<- add = <coroutine object add at 0x...>`.

A wrapper over a coroutine function must be [`async def`](19_Techniques--Concurrency.md#asyncio-mechanics)
and `await func(*args, **kwargs)`.
The annotations change to match.
`func` is a `Callable[P, Awaitable[R]]`,
and the wrapper is `async def wrapper(...) -> R`.
The decorator returns a `Callable[P, Coroutine[Any, Any, R]]`,
since calling an `async def` function produces a coroutine,
and awaiting that coroutine produces the `R`.

## Decorators That Take Arguments

To pass arguments to a decorator, add another layer.
A decorator with arguments is a function that returns a decorator:

```python
# repeat.py
from collections.abc import Callable
from functools import wraps

def repeat[**P, R](
        times: int
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if times < 1:
        raise ValueError(f"times must be >= 1, got {times}")
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times):
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

Take the return type apart: `Callable[[Callable[P, R]], Callable[P, R]]`.
[`Callable[[A, B], X]`](08_Foundations--Static_Types.md#containers)
reads as "a callable that takes `A` and `B` and returns `X`".
The first bracket group is a list holding the parameter types,
so `[Callable[P, R]]` is a parameter list of length one,
not a list of callables.
That single parameter type is `Callable[P, R]`, the wrapped function's type.
So the whole annotation reads as "a callable that takes a `Callable[P, R]` and returns a `Callable[P, R]`."
The annotation describes `decorate`, which takes `func` and returns `wrapper`,
both typed `Callable[P, R]`.

`@repeat(times=3)` first evaluates `repeat(times=3)`.
`repeat(times=3)` returns `decorate`, the real decorator,
and Python then calls `decorate(greet)`.
Only now does the body of `decorate` run, including its `@wraps(func)` line.
`@wraps(func)` is the same two-step pattern one level down.
Python calls `wraps(func)` to get a decorator,
then applies that decorator to `wrapper`.
The inner decoration runs inside the outer one,
so `@repeat(times=3)` and `@wraps(func)` are two separate decorations,
not one recursive call.
The nesting stops at two levels, matching the two nested `def`s in the source.

Forgetting the parentheses is the common mistake here.
`@repeat` without them calls `repeat(greet)`,
passing the function where `repeat` expects `times`.
The `times < 1` check makes that mistake raise a `TypeError` at decoration,
since it compares a function with an `int`.
The message describes the failed comparison,
so you must trace the comparison back to the missing parentheses.
A `repeat` without that comparison fails silently.
Python binds `greet` to `decorate`.
Calling `greet("Bob")` then runs `decorate("Bob")`,
which wraps the string where it expects a function and returns the wrapper.
The call runs silently.
The caller gets a wrapper where it expected `"Bob"`.

The annotations let the type checker report the mistake either way,
at the decoration rather than at the call.
Its diagnostic says that `repeat` expected an `int` for `times` and got a function.
A second diagnostic follows at `greet("Bob")`,
but that one is harder to trace to the missing `()`.

`repeat()` rejects `times` below one rather than quietly rounding it up to one.
The check runs at decoration,
so Python raises the exception at the `@` line rather than at some later call.
Because that check guarantees `times >= 1`,
`wrapper()`'s loop always runs at least once.
The loop therefore always leaves a value of type `R` in `result` to return.
The tests parametrize over `times` and cover the rejection:

```python
# test_repeat.py
import pytest
from repeat import repeat

@pytest.mark.parametrize("times", [3, 1])
def test_repeat_call_count(times: int) -> None:
    calls: list[str] = []

    @repeat(times=times)
    def record() -> None:
        calls.append("call")

    record()
    assert len(calls) == times

@pytest.mark.parametrize("times", [0, -1])
def test_repeat_rejects_times_below_one(times: int) -> None:
    with pytest.raises(ValueError):
        repeat(times=times)
```

## Decorators With Optional Parentheses

You apply `trace(func: Callable[P, R])` bare, as `@trace`,
but you always apply `repeat(times: int)` with arguments, as `@repeat(times=3)`.
A decorator can support both conventions at once, `@name` and `@name(...)`,
so a caller adds arguments only to change a default.
`pytest.fixture` and `click.command` both work this way.

The two forms differ in what Python passes first.
`@label` calls `label(one)`, so a function arrives as the only argument.
`@label(prefix="TAG")` calls `label(prefix="TAG")` first, with no function,
then applies the result to `two`.
Checking whether a first argument arrived tells the two calls apart:

```python
# optional_parens.py
from collections.abc import Callable
from functools import wraps
from typing import Any, overload

type Decorator[**P, R] = Callable[
    [Callable[P, R]], Callable[P, R]]

@overload
def label[**P, R](
        func: Callable[P, R],
) -> Callable[P, R]: ...
@overload
def label[**P, R](
        func: None = None, *, prefix: str = "LOG"
) -> Decorator[P, R]: ...

def label[**P, R](
        func: Callable[P, R] | None = None,
        *, prefix: str = "LOG",
) -> Any:
    def decorate(
            f: Callable[P, R]
    ) -> Callable[P, R]:
        @wraps(f)
        def wrapper(
                *args: P.args, **kwargs: P.kwargs
        ) -> R:
            print(f"[{prefix}] {wrapper.__name__}")
            return f(*args, **kwargs)
        return wrapper
    return decorate if func is None else decorate(func)

@label
def one() -> None: ...

@label(prefix="TAG")
def two() -> None: ...

if __name__ == "__main__":
    one()
    two()
#: [LOG] one
#: [TAG] two
```

The two `@overload` declarations state for the type checker what the runtime `func is None` branch does:
given a function, `label` returns a function of the same signature;
given keyword arguments alone, it returns a decorator.
The second overload gives that decorator the type `Decorator[P, R]`,
a generic alias for the shape `repeat.py` takes apart.
The alias takes its parameters from the wrapped function.
The implementation must satisfy both overloads,
so it declares the widest return type, `Any`,
and the overloads narrow that back down at every call site.

A `callable(func)` test also tells the two calls apart,
but it asks what kind of value arrived rather than whether one arrived.
The `callable()` test then fails silently when a caller passes a prefix positionally.
With `callable(func)`,
`@label("TAG")` decorates the function with the default `LOG` prefix and drops `"TAG"`.
With `func is None`, the same call raises a `TypeError` at decoration.
`decorate("TAG")` wraps the string,
and when Python applies that wrapper to the function,
the wrapper calls `"TAG"` as if the string were the decorated function.
With either test, a decorator whose own argument could be callable,
such as a `key` function, mistakes that argument, passed positionally,
for the function it decorates.
For that reason `label` makes its arguments keyword-only,
so a caller must name them.

The tests decorate one function each way and confirm that both forms keep the result and the name:

```python
# test_optional_parens.py
from optional_parens import label

def test_bare_decoration() -> None:
    @label
    def greet() -> str:
        return "hi"

    assert greet() == "hi"
    assert greet.__name__ == "greet"

def test_decoration_with_arguments() -> None:
    @label(prefix="TAG")
    def greet() -> str:
        return "hi"

    assert greet() == "hi"
    assert greet.__name__ == "greet"
```

## Stacking Decorators

A decorator can wrap the wrapper another decorator produced.
Decorators stack, nesting from the bottom up:

```python
# stacking.py
from repeat import repeat
from tracer import trace

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

The two `@` lines mean `greet = trace(repeat(times=2)(greet))`.
`@repeat(times=2)` wraps `greet()` first, then `@trace` wraps that result,
so a single `greet("Bob")` traces one call whose body runs twice.

Stacking works because each wrapper preserves the interface of what it wraps.
Every layer has the original function's name and signature,
so the layers compose to any depth.

Each layer also adds two things that remain after `wraps` copies the metadata.
A traceback through a decorated function shows a `wrapper` stack frame for each layer,
on top of the stack frames for the caller and the original body.
Each call also makes an extra Python-level function call per layer,
the call to that layer's wrapper, before the real body runs.
For a function called occasionally, both are small.
For one called in a tight loop, both add up,
and they grow with the number of stacked layers.

The tests confirm that the name survives two layers of wrapping,
and that one call through both layers still runs the body twice:

```python
# test_stacking.py
from repeat import repeat
from tracer import trace

def test_stacked_decorators_preserve_name() -> None:
    @trace
    @repeat(times=2)
    def greet(name: str) -> str:
        return name

    assert greet.__name__ == "greet"

def test_stacked_decorators_repeat_the_call() -> None:
    calls: list[str] = []

    @trace
    @repeat(times=2)
    def record() -> None:
        calls.append("call")

    record()
    assert calls == ["call", "call"]
```

## Decorators as Classes

A decorator is any callable that accepts one argument.
A class with `__call__()` is a callable,
so a decorator can be a class instead of a function.

The class form puts the two phases in separate methods.
The constructor runs once, at decoration.
`__call__()` runs on every call to the decorated function.

These classes take lowercase names, against the usual `PascalCase` rule,
because a decorator reads like a function at the call site.
`property`, `staticmethod`,
and `functools.partial` are all lowercase classes for that reason.

### A Stateless Class-Form Decorator

The class version of `trace` imports `call_text()` from `tracer.py`:

```python
# trace_class.py
from collections.abc import Callable
from functools import update_wrapper
from tracer import call_text

class trace[**P, R]:
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        # Copy __name__, __doc__, etc
        update_wrapper(self, func)

    def __call__(self, *args: P.args,
                 **kwargs: P.kwargs) -> R:
        print("->", call_text(self.__name__, args, kwargs))
        result = self.func(*args, **kwargs)
        print(f"<- {self.__name__} = {result!r}")
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

`functools.update_wrapper(self, func)` copies `func`'s metadata onto an existing object.
`wraps` is the decorator form of that same call.
`@wraps(func)` above `def wrapper` runs `update_wrapper(wrapper, func)`.
In the class form, the object that takes the function's place is `self`,
so `__init__()` calls `update_wrapper(self, func)`.

The `__name__: str` declaration tells the type checker about the attribute `update_wrapper()` sets,
so `__call__()` can print `self.__name__`.
In `tracer.py` the type checker reads `__name__` from `wrapper`'s type,
because `wrapper` is a function and a function's type includes `__name__`.
Like the function form, the class is generic in `**P` and `R`,
so `__call__()` keeps the wrapped signature and `add(2, 3)` still type-checks as an `int`.

The class form passes the function form's two tests,
`test_trace_preserves_name` and `test_trace_returns_original_result`,
in a file that differs in its import alone:

```python
# test_trace_class.py
from trace_class import trace

def test_trace_preserves_name() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add.__name__ == "add"

def test_trace_returns_original_result() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
```

### A Class-Form Decorator with State

Because the instance holds attributes, it carries state between calls.
Here, `count_calls` counts calls and keeps the count on the instance:

```python
# count_calls.py
from collections.abc import Callable
from functools import update_wrapper

class count_calls[**P, R]:
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.count = 0
        update_wrapper(self, func)

    def __call__(self, *args: P.args,
                 **kwargs: P.kwargs) -> R:
        self.count += 1
        print(f"call {self.count} of {self.__name__}")
        return self.func(*args, **kwargs)

@count_calls
def hello() -> None: ...

if __name__ == "__main__":
    hello()
    hello()
    # The state lives on the decorator instance
    print(hello.count)
#: call 1 of hello
#: call 2 of hello
#: 2
```

Each `@count_calls` creates its own instance,
so each decorated function keeps its own count:

```python
# test_count_calls.py
from count_calls import count_calls

def test_counts_are_independent_per_function() -> None:
    @count_calls
    def greet() -> None:
        pass

    @count_calls
    def farewell() -> None:
        pass

    greet()
    greet()
    farewell()

    assert greet.count == 2
    assert farewell.count == 1
```

The function form can keep a count too,
in a variable of the decorator's body that `wrapper()` updates through [`nonlocal`](40_Functional--Foundations.md#closures).
The wrapper's own `__dict__` could hold the count as well,
but the type checker reports every dotted access to an attribute stored there.
Call state therefore goes in a closure or an instance.
[Attributes on a Function](17_Techniques--Metaprogramming.md#attributes-on-a-function)
shows a use that suits a function's `__dict__`.

### A Class-Form Decorator with Arguments

When the decorator takes arguments,
the class form is easier to follow than the [function form](#decorators-that-take-arguments).
Without arguments, the constructor receives the function.
With arguments, the constructor receives the arguments.
`__call__()` then receives the function and returns the wrapper:

```python
# repeat_class.py
from collections.abc import Callable
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        if times < 1:
            raise ValueError(
                f"times must be >= 1, got {times}")
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

`repeat` here raises the same `ValueError` for a `times` below one that `repeat.py` raises,
in the constructor rather than in the outer function.
Its `wrapper()` makes the first call before the loop,
so `result` holds a value before the loop starts.
`repeat.py` relies on the `times >= 1` check for that guarantee.

The class form's tests differ from `test_repeat.py` in their import alone:

```python
# test_repeat_class.py
import pytest
from repeat_class import repeat

@pytest.mark.parametrize("times", [3, 1])
def test_repeat_call_count(times: int) -> None:
    calls: list[str] = []

    @repeat(times=times)
    def record() -> None:
        calls.append("call")

    record()
    assert len(calls) == times

@pytest.mark.parametrize("times", [0, -1])
def test_repeat_rejects_times_below_one(times: int) -> None:
    with pytest.raises(ValueError):
        repeat(times=times)
```

### A Limitation: Methods Need a Descriptor

The class form has one limitation,
which arises because the decorator instance replaces the function it decorates.
A method decorated that way becomes an instance rather than a function,
and calling it fails.
`trace_class.py` and `count_calls.py` decorate module-level functions for that reason.
Like those two classes,
`logged` stores the function in its constructor and calls it from `__call__()`,
and decorating a method with it fails at the call:

```python
# method_decoration.py
from collections.abc import Callable
from exceptions import expect

class logged:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, *args: object,
                 **kwargs: object) -> object:
        print(f"logged: args={args}")
        return self.func(*args, **kwargs)

class Ex:
    @logged
    def method(self, x: int) -> int:
        return x

ex = Ex()
expect(TypeError, ex.method, 5)
#: logged: args=(5,)
#: [TypeError] Ex.method() missing 1 required positional
#: argument: 'x'
```

`Ex.method` is a `logged` instance, stored as a class attribute.
Python binds a class attribute to an instance only when that attribute is a descriptor,
an object whose class defines `__get__()`.
Every ordinary function is a descriptor.
A `logged` instance has no `__get__()`,
so `ex.method` returns the `logged` instance unbound.

The call `ex.method(5)` therefore runs `logged.__call__(logged_instance, 5)`.
The printed `args=(5,)` shows what arrives: `5`, and no `Ex` instance.
`self.func` runs with `5` as its only argument,
so `5` fills `method`'s own `self` parameter and leaves nothing for `x`.
The `TypeError` reports a missing `x`,
while the real cause is a missing `__get__()`.
[Metaprogramming](17_Techniques--Metaprogramming.md#learning-a-name-with-__set_name__)
shows the full descriptor protocol,
including the `__get__()` that `logged` needs to work on methods.

Because a function is a descriptor,
`wrapper()` in the function form binds to an instance like any other method:

```python
# method_function_form.py
from tracer import trace

class Ex:
    @trace
    def method(self, x: int) -> int:
        return x

    def __repr__(self) -> str:
        return "Ex()"

ex = Ex()
print(ex.method(5))
#: -> method(Ex(), 5)
#: <- method = 5
#: 5
```

`self` arrives as the first traced argument,
and the `__repr__()` the class defines prints it as `Ex()`.
The method decoration that failed with `logged` works here,
through the descriptor every function carries.
For the same reason, `repeat_class.repeat` works on methods.
Its `__call__()` returns `wrapper`, an ordinary function,
so a method decorated with `@repeat(times=3)` is still a function.

If `method_decoration.py` decorates `Ex.method` with a fully typed class-form decorator,
such as `trace_class.trace`, instead of `logged`,
the type checker catches the failure before the program runs.
It reports a missing argument and a type mismatch on a call like `ex.method(5)`.

### Function Form or Class Form?

`@trace` with no arguments calls `trace(add)`.
Python passes the function to the constructor.
`@repeat(times=3)` calls `repeat(times=3)` first, producing an instance,
then applies that instance to `greet`.
Python passes the arguments to the constructor.
The function arrives later, at `__call__()`.
Adding arguments moves the function from a parameter of `__init__()` to a parameter of `__call__()`.
The function form hides this shift inside an extra nested `def`.
The class form makes it visible.

Outside methods, the form you choose is mostly a matter of taste.
Both forms preserve the wrapped function's exact signature for the type checker,
using the same `**P` and `R` type parameters.
Both forms also stack,
the way `stacking.py` stacks two function-form decorators.
The function form is more compact.
The class form reads better when the decorator carries state or grows complicated,
because the phases are separate methods instead of nested closures.

The class form with arguments is enough to build a small framework.
A build tool can offer a `@rule(target, *deps)` decorator whose constructor records the target and its dependencies,
and whose `__call__()` registers the decorated function in a class-level table with that metadata.
A driver walks the table later and runs the rules in order,
so the decorator becomes the registration mechanism for the whole system.

The descriptor limitation is the one hard reason to choose the function form.
A decorator meant for methods either returns a function,
as the function form and `repeat_class.repeat` both do,
or implements `__get__()`.

A [context manager can also decorate a function](15_Techniques--Context_Managers.md#context-manager-as-decorator),
running its setup code before every call and its cleanup code after it.

## Decorating Classes

Every example so far decorates a function.
A `class` statement takes a decorator the same way,
and the decorator receives the class object.
Decorating a class differs from [Decorators as Classes](#decorators-as-classes),
where the class is the decorator.
Here the decorator is an ordinary function,
and the class is the thing decorated.
The `register()` decorator records every class it decorates in `registry`:

```python
# register.py

registry: dict[str, type] = {}

def register[T](cls: type[T]) -> type[T]:
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

`register()` returns the same `cls` it received,
so the name `Espresso` refers to the original class.
`register()` exists for the side effect of recording the class.
A class decorator can also return a replacement class,
just as a function decorator returns a replacement function.

The type parameter `T` keeps the decorated class's type for the type checker,
as `**P` and `R` keep a decorated function's signature.
If `register`'s annotation is `(cls: type) -> type`,
`register()` returns a bare `type`.
`ty` and Pyright then infer `Espresso()` as an `Any`.

A registry filled this way is as complete as the imports that ran.
A class in a module nobody imported stays out of the registry.
Because `register()` keys on `cls.__name__`,
when two modules each define a class with the same name,
the class registered second replaces the first.
[Factory](26_Patterns--Factory.md#hazards-of-self-registration) returns to both.

[Metaprogramming](17_Techniques--Metaprogramming.md#self-registration-of-subclasses)
shows `__init_subclass__()`,
which builds a registry like this without a decorator.

The tests confirm that `register()` returns the class it receives,
and that `registry` maps each class name to its class:

```python
# test_register.py
from register import Espresso, Latte, register, registry

def test_register_returns_same_class() -> None:
    assert register(Espresso) is Espresso

def test_registry_looks_up_by_name() -> None:
    assert registry["Espresso"] is Espresso
    assert registry["Latte"] is Latte
```

## What `@` Does Not Require

`@` constrains the statement below it.
A decorator line must sit directly above a `def`, an `async def`, a `class`,
or another decorator line.
`@decorator` above a bare assignment, or above a `type` alias,
is a syntax error rather than a decorator applied to something unusual.
Past that, the decorator decides what it accepts.
The callable you decorate can come from somewhere other than a `def`:

```python
# lambda_decoration.py
from collections.abc import Callable

def report(
        func: Callable[[int], int]) -> Callable[[int], int]:
    def wrapper(n: int) -> int:
        print(f"Calling {func.__name__} with {n}")  # type: ignore
        return func(n)
    return wrapper

double = report(lambda n: n * 2)

@report
def triple(n: int) -> int:
    return n * 3

if __name__ == "__main__":
    print(double(21))
    print(triple(21))
#: Calling <lambda> with 21
#: 42
#: Calling triple with 21
#: 63
```

`report` requires a callable.
`func` can come from anywhere.
Calling `report` as an ordinary function, instead of through `@`,
decorates the `lambda` in place.
`@` is convenient sugar for the common case of decorating a fresh `def`,
not a requirement.
The same call decorates a `functools.partial`, a bound method,
or an instance of a class with `__call__()`,
since all a decorator receives is a callable.

Calling the result is another matter.
`report`'s wrapper reads `func.__name__`,
which a `partial` and a callable instance lack.
Calling the wrapper around either of those two raises an `AttributeError`,
while the wrappers around a function and a bound method run.

The `# type: ignore` in `report` silences `ty`'s diagnostic for the same hazard.
`ty` rejects `func.__name__`,
since a `Callable` need not have a `__name__` attribute,
though every function does.
Pyright and mypy both accept the attribute here,
because they give a `Callable` the attributes of a function object.
`report` has no `wraps`, so `wrapper.__name__` is `wrapper`,
and the name the trace prints must come from `func`.

The return side is equally unconstrained.
A decorator "returns a result, which Python binds to the original name."
That result can be any object:

```python
# run_once.py
from collections.abc import Callable

def run_once[T](func: Callable[[], T]) -> T:
    return func()

@run_once
def greeting() -> str:
    return "Hello, world"

if __name__ == "__main__":
    print(greeting)
    print(type(greeting).__name__)
#: Hello, world
#: str
```

After decoration the name `greeting` refers to a `str`,
so `greeting()` raises a `TypeError`, because a `str` is not callable.

`run_once` suits a value that needs one-time setup logic but stays constant afterward.
For a value that a single expression computes,
assign the expression to a module-level constant.

A class decorator can also return an object that is not a class.
[*Singleton*](23_Patterns--Singleton.md#singleton-by-class-decorator)
replaces a class with a callable object that stands in for it.
The name that follows `class` then refers to that callable object,
not to a class.

Before Python 3.9, the expression after `@` had to be a dotted name,
optionally followed by one call,
as in `@config.decorator` or `@repeat(times=3)`.
A decorator looked up by subscript, as in `@handlers["json"]`,
was a syntax error.
Since Python 3.9 (PEP 614), the expression after `@` can be any expression,
so you can write `run_once` inline as `@lambda`:

```python
# lambda_decorator.py
@lambda f: f()
def fib_table() -> list[int]:
    table = [0, 1]
    while len(table) < 10:
        table.append(table[-1] + table[-2])
    return table

print(fib_table)
#: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

The run-once idiom is the most common use of `@lambda`, and it exists for scope.
The loop needs a working variable, `table`,
and building the list inside a function keeps `table` local.
The module gains one name, `fib_table`, holding the finished list.

Treat `@lambda` as a curiosity and avoid it.
A reader who sees `def fib_table()` expects a function and finds a list.

Neither type checker types `fib_table` as the `list[int]` it holds.
The lambda's parameter has no annotation,
so `ty` reports `fib_table` as `Unknown`,
where the generic `run_once` carries `T` through to `greeting`'s `str`.
Pyright keeps the type of the `def`, `() -> list[int]`.
It accepts `fib_table()`, which raises a `TypeError` at runtime,
and rejects `fib_table[0]`, which works.
If you want the run-once idiom, use the named decorator.

## The Decorator Pattern

The `@` syntax decorates a function or class once, at definition,
so every call or every instance gets the wrapping.
Sometimes you want to choose later:
add responsibilities to individual objects at runtime,
and let each caller decide which responsibilities to add.
That is the object-oriented *Decorator* pattern.

Consider a pizza shop.
A class for every pizza-and-topping combination produces a long list of classes:
Margherita, Margherita with olives, Margherita with olives and feta, and so on.
Each new topping doubles the menu.

Instead, the toppings become decorators.
A plain pizza stores its own cost and description.
A topping wraps a pizza at runtime, adds to the cost,
and adds to the description.
A topping can wrap another topping, because a topping is a pizza.

![Each topping wraps a Pizza and is itself a Pizza](_images/decorator_pattern)

```python
# pizza_decorator.py
from typing import ClassVar, Protocol

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
    add_cost: ClassVar[float] = 0.0

    def __init__(self, pizza: Pizza) -> None:
        self.pizza = pizza
        self.name = type(self).__name__

    @property
    def cost(self) -> float:
        return self.pizza.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.pizza.description} + {self.name}"

class Garlic(Topping):
    add_cost = 0.50

class Olives(Topping):
    add_cost = 0.75

class Feta(Topping):
    add_cost = 1.25

if __name__ == "__main__":
    for order in (Feta(Olives(Margherita())),
                  Garlic(Feta(Hawaiian()))):
        print(f"{order.description}: ${order.cost:.2f}")
#: Margherita + Olives + Feta: $10.00
#: Hawaiian + Feta + Garlic: $11.25
```

`Feta(Olives(Margherita()))` is the object version of stacked `@` decorators.
Both the plain pizzas and the toppings satisfy the `Pizza` `Protocol` structurally,
with no shared base class required.
Satisfying a `Protocol` by shape alone is [structural typing](08_Foundations--Static_Types.md#structural-typing-with-protocols).

A read-only `@property` in a `Protocol` requires that reading the name produce the property's return type,
and lets each class choose how.
`Margherita` supplies `cost` as a class attribute.
`Topping` computes it in a property.
Both read as a `float`, so both match.

`Topping.__init__()` sets `self.name = type(self).__name__`,
reading each subclass's own name at construction time instead of repeating it as a string.
`Garlic`, `Olives`, and `Feta` each write their name once, in the `class` line.

Adding a new topping means adding one class with one line, `add_cost`.
Changing the price of a topping means changing one number, in one place.
Compare that with a class per combination,
where a price change means editing every class that includes that topping.

A `Pizza` with a `toppings: list[Topping]` field solves the same combinatorial problem,
with no wrapping and no `Protocol`.
It sums the toppings' `add_cost` values and joins their names.
That list is the simpler design here, where a topping contributes data
(a number and a name).
The *Decorator* pattern becomes the simpler design when a topping needs behavior as well as data:
a topping that changes how `cost` rounds,
adds a description only under some condition,
or must pass to other code as a `Pizza`.
A list of toppings is data that a pizza holds.
A decorator chain is a pizza,
each layer satisfying the same interface the plain pizzas do.

[Factory](26_Patterns--Factory.md#builder) has its own `Pizza`,
a frozen data class that a `PizzaBuilder` assembles,
to illustrate the unrelated *Builder* pattern.
The two examples share a topic, not a type.

A *Decorator* keeps the wrapped object's interface and adds behavior.
*Proxy*, *Adapter*, and *Façade* wrap the same way and [differ in intent](29_Patterns--Changing_the_Interface.md#distinguishing-the-wrappers).

The tests check the cost and description of a stacked order,
`Feta(Olives(Margherita()))`, and of a single topping, `Garlic(Margherita())`:

```python
# test_pizza_decorator.py
import pytest
from pizza_decorator import Feta, Garlic, Margherita, Olives

def test_stacked_toppings() -> None:
    order = Feta(Olives(Margherita()))
    assert order.cost == pytest.approx(10.00)
    assert order.description == (
        "Margherita + Olives + Feta")

def test_single_topping() -> None:
    order = Garlic(Margherita())
    assert order.cost == pytest.approx(8.50)
    assert order.description == "Margherita + Garlic"
```

## Decorators You Already Know

Several decorators elsewhere in this book use this mechanism.
[`@property`](07_Foundations--Classes.md#properties), `@cached_property`,
[`@staticmethod`](07_Foundations--Classes.md#static-and-class-methods),
and [`@classmethod`](07_Foundations--Classes.md#static-and-class-methods)
are class-form decorators like `trace_class.trace`.
Each is a class, and decorating a function stores that function in a new instance.
Unlike `logged`, each of these classes also implements `__get__()`,
so its instances are descriptors.
Python calls that `__get__()` when code reads the attribute,
so `@property` runs its getter, `@staticmethod` returns the plain function,
and `@classmethod` binds the function to the class.
The same `__get__()` makes them work on methods, where `logged` fails.
[`@dataclass`](12_Techniques--Data_Classes_as_Types.md#data-classes)
is a class decorator like `register`, except it mutates the class,
adding a generated `__init__()`, `__repr__()`,
and `__eq__()` to the same object it received.
[`@functools.cache`](18_Techniques--Performance.md#caching)
and `@functools.lru_cache` wrap a function the way `add_behavior` does,
in a wrapper that holds `func` and calls it,
storing results in a memo dictionary instead of printing around the call.

The one piece of machinery left for later is the descriptor protocol that `@property`,
`@cached_property`, `@staticmethod`, and `@classmethod` implement.
[Metaprogramming](17_Techniques--Metaprogramming.md#learning-a-name-with-__set_name__)
takes it up.

## Exercises

Try each exercise before opening its [solution](../Solutions/14_Techniques--Decorators/).

1.  Write a class decorator `announce` that prints the name of each class it decorates and returns it unchanged,
    then apply it to two small classes.
    Compare what it can do to what `register` does.
2.  Write a `timing` decorator that prints how long the wrapped function took,
    using `time.perf_counter()`.
    Apply it together with `@trace` and predict the order of the output.
3.  Implement the object-oriented *Decorator* pattern for a coffee shop:
    plain drinks (Espresso, Cappuccino) and extra decorators
    (Whipped cream, Decaf, Extra shot).
    Build an espresso decorated with an extra shot and whipped cream,
    then print its cost and description.
4.  Write `trace` as a class-form decorator that also keeps a class-level counter shared across every decorated function,
    and report the total number of traced calls in the program.
    Note where the shared state lives compared to the per-instance `count` in `count_calls`.
5.  Write a `memo` decorator that works both with and without parentheses,
    so `@memo` and `@memo(maxsize=10)` both decorate a function.
    Cache each result in a dictionary keyed by the arguments,
    and drop the oldest entry when the cache holds more than `maxsize` of them.
    Distinguish the two forms by checking whether a first argument arrived.
6.  Write a `retry(times)` decorator in the function form that calls the wrapped function again when it raises an exception,
    up to `times` attempts, and re-raises the last exception when they all fail.
    Check that `__name__` survives.
7.  Decorate one method of a small class with the class-form `repeat` from `repeat_class.py`,
    and a second method with `logged` from `method_decoration.py`.
    Call the first through an instance,
    then print the type of the object each method name refers to in the class.
    Explain why one class-form decorator works on a method and the other does not.
