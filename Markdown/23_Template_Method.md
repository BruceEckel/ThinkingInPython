# Template Method

An application framework lets you build a new application by reusing existing classes and overriding one or more methods to customize the behavior.
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

The defining trait of a Template Method is that the *shape* of the algorithm is fixed in the base class,
while the individual steps are left open for subclasses to fill in.
In languages with `final`,
the template method is locked so a subclass cannot change the overall flow.
Python has no `final` keyword ([Singleton](22_Singleton.md) and [Metaprogramming](17_Metaprogramming.md#making-a-class-final) show how it is emulated when truly needed),
so here it is a matter of convention: the base defines the algorithm,
subclasses define the steps.

```python
# template_method.py
from typing import override

class ApplicationFramework:
    def __init__(self) -> None:
        self.run()

    # The fixed algorithm. Subclasses supply the steps, not the flow:
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

A test records the steps to confirm the algorithm calls them in order, twice:

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
with no subclass at all:

```python
# template_function.py
# The same Template Method, with the varying steps passed as functions
# instead of supplied by a subclass.
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

Both versions hold the algorithm fixed and let the steps vary,
which is the whole point of Template Method.
Choose based on what the steps need.
If they share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions is lighter and avoids a class hierarchy.
This is the same trade-off seen in [Function Objects](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime):
a hook that holds no state is usually better as a function than as a method to override.

The function version is checked the same way, recording the order the passed-in steps run:

```python
# test_template_function.py
from template_function import run_framework

def test_template_function_runs_steps_in_order() -> None:
    calls: list[str] = []
    run_framework(
        lambda: calls.append("a"), lambda: calls.append("b"))
    assert calls == ["a", "b", "a", "b"]
```

## Exercises

1.  Create a framework that takes a list of file names.
    It opens each file except the last for reading and the last for writing,
    processes each input file by an undetermined policy,
    and writes the output to the last file.
    Customize it two ways, once by subclassing and once by passing a function:

    > 1.  Convert all the letters in each file to uppercase.
    > 2.  Search the files for words given in the first file.
