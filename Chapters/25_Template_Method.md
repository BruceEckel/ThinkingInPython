# Template Method

With an application framework,
you build a new application by reusing existing classes and overriding one or more methods to customize the behavior.
At the heart of a framework is the *Template Method*: a method,
defined in the base class,
that drives the application by calling other base-class methods,
some of which you override.

Python's own `unittest` is an application framework of this kind.
You subclass `TestCase` and supply `setUp()`, your `test_*` methods,
and `tearDown()`.
The framework's runner is the template method.
It calls `setUp()`, then your test, then `tearDown()`, for each test,
and you never call that sequence yourself.

## The Fixed Algorithm

The defining trait of a Template Method is that the base class fixes the *shape* of the algorithm.
Subclasses complete the individual steps.
The `@final` decorator from `typing` locks the template method so a subclass cannot change the overall flow
(see [Making a Class Final](17_Metaprogramming.md#making-a-class-final)).
Here, `@final` marks `run()`,
so the checker rejects any subclass that overrides it,
while leaving the step methods open:

```python
# template_method.py
from typing import final, override

class ApplicationFramework:
    def __init__(self) -> None:
        self.run()

    # The fixed algorithm. Subclasses supply the steps, not the flow:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

# Create an "application" by filling in the steps:
class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("Nudge, nudge, wink, wink!")

    @override
    def customize2(self) -> None:
        print("Say no more, say no more!")

MyApp()
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
```

The base-class constructor starts the engine (`run()`),
which drives the application.
The client supplies `customize1()` and `customize2()`, and the application runs.
In a GUI program that engine is the main event loop.

Notice which direction the calls flow.
`run()` lives in the base class,
yet `self.customize1()` executes `MyApp`'s version,
because attribute lookup on `self` starts at the object's actual type,
and `self` is a `MyApp`.
The base class calls code written after it, sometimes years after.
Framework authors call this the *Hollywood Principle*: don't call us,
we'll call you.
Your code supplies the steps; the framework decides when they run.

A caution about the `@final` lock: it binds only under the type checker.
At runtime Python ignores it,
and a subclass override of `run()` replaces the fixed algorithm without complaint.
The guarantee is real, but it is the checker's guarantee,
one more reason to make `ty` or another checker part of the build.

The step methods default to `...`, doing nothing,
so a subclass overrides only the steps it cares about,
and a forgotten step silently does nothing.
When every subclass must supply a step,
inherit from `ABC` and declare the step with `@abstractmethod`,
as in [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance);
then Python refuses to instantiate a subclass that forgot it.

Starting the engine from the constructor carries a trap.
`run()` calls methods the subclass supplies,
so a subclass that defines its own `__init__()` must finish its setup before it calls `super().__init__()`.
Call it first, in the usual style,
and the engine runs against half-initialized state:

```python
# premature_engine.py
from typing import final, override

class Framework:
    def __init__(self) -> None:
        self.run()

    @final
    def run(self) -> None:
        self.step()

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        super().__init__()  # Usual style: engine runs now...
        self.name = name  # ...before this line has happened

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

try:
    Greeter("Bruce")
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
```

`Greeter("Bruce")` never gets to greet.
`super().__init__()` starts the engine, the engine calls `step()`,
and `step()` reads `self.name` one line before the constructor assigns it.
The quick fix is reordering: assign `self.name` first,
then call `super().__init__()`.
That works, but it inverts the convention every Python programmer carries,
and the next subclass author will restore the usual order without thinking.
The reliable fix changes the framework: separate construction from starting,
and have the client call `run()` explicitly on a fully built object.

This pattern leans on the [Liskov Substitution Principle](20_Rethinking_Objects.md#liskov-substitution).
A subclass must work wherever code expects its base class.
The base `run()` calls `customize1()` and `customize2()` through `self`,
trusting that whatever a subclass supplies still fits the algorithm's shape.
An override that breaks that trust, doing nothing the flow relies on,
or raising an exception where the base would not,
corrupts the fixed algorithm even though the code still type-checks.
The Template Method works only when every subclass is a faithful substitute for its base.

The test supplies a recording subclass and verifies the fixed flow:

```python
# test_template_method.py
from typing import override
from template_method import ApplicationFramework

def test_template_method_runs_steps_in_order() -> None:
    calls: list[str] = []

    class Recorder(ApplicationFramework):
        @override
        def customize1(self) -> None:
            calls.append("one")

        @override
        def customize2(self) -> None:
            calls.append("two")

    Recorder()  # Constructing it runs the framework
    assert calls == ["one", "two", "one", "two"]  # Loop runs twice
```

## Passing the Steps as Functions

Subclassing is one way to supply the varying steps, but not the only one.
Because Python functions are first-class, you can pass the steps in directly,
without using a subclass:

```python
# template_function.py
from collections.abc import Callable

def run_framework(customize1: Callable[[], None],
                  customize2: Callable[[], None]) -> None:
    for _ in range(2):  # The fixed algorithm
        customize1()
        customize2()

run_framework(
    lambda: print("Nudge, nudge, wink, wink!"),
    lambda: print("Say no more, say no more!"),
)
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
```

```python
# test_template_function.py
from template_function import run_framework

def test_template_function_runs_steps_in_order() -> None:
    calls: list[str] = []
    run_framework(
        lambda: calls.append("a"), lambda: calls.append("b"))
    assert calls == ["a", "b", "a", "b"]
```

Both the Template Method and Template Function have a fixed algorithm and varying steps.
If they share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions is lighter and avoids a class hierarchy.
This is the same trade-off seen in [Function Objects](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime).
A hook that holds no state is usually better as a function than as a method to override.

## Exercises

1.  Create a framework that takes a list of file names.
    It opens every file but the last for reading, and the last one for writing.
    It processes each input file by an undetermined policy,
    and writes the output to the last file.
    Customize it two ways, once by subclassing and once by passing a function:

    1.  Convert all the letters in each file to uppercase.
    2.  Search the files for words given in the first file.
2.  Fix `premature_engine.py` both ways:
    first reorder the two lines in `Greeter.__init__()`,
    then instead redesign `Framework` so clients construct the object and call `run()` explicitly.
    Which fix still protects a second subclass author who has never read this chapter?
