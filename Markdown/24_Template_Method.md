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
The framework's runner is the template method: it calls `setUp()`,
then your test, then `tearDown()`, for each test,
and you never call that sequence yourself.

## Template Method

The defining trait of a Template Method is that the *shape* of the algorithm is fixed in the base class.
Subclasses complete the individual steps.
The `@final` decorator from `typing` locks the template method so a subclass cannot change the overall flow
(see [Making a Class Final](18_Metaprogramming.md#making-a-class-final)).
Here, `run()` is marked with `@final` so the checker rejects any subclass that overrides it,
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

This pattern leans on the [The Liskov Substitution Principle](20_Rethinking_Objects.md#liskov-substitution):
a subclass must be usable wherever its base class is expected.
The base `run()` calls `customize1()` and `customize2()` through `self`,
trusting that whatever a subclass supplies still fits the algorithm's shape.
An override that breaks that trust, doing nothing the flow relies on,
or raising an exception where the base would not, corrupts the fixed algorithm
even though the code still type-checks.
The Template Method works only when every subclass is a faithful substitute for its base.

Here's a second implementation of `ApplicationFramework`:

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
    for _ in range(2):   # The fixed algorithm
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
This is the same trade-off seen in [Function Objects](29_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime):
a hook that holds no state is usually better as a function than as a method to override.

## Exercises

1.  Create a framework that takes a list of file names.
    It opens each file except the last for reading and the last for writing,
    processes each input file by an undetermined policy,
    and writes the output to the last file.
    Customize it two ways, once by subclassing and once by passing a function:

    > 1.  Convert all the letters in each file to uppercase.
    > 2.  Search the files for words given in the first file.
