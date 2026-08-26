# Template Method

Application frameworks build new applications by reusing existing classes and overriding one or more methods to customize behavior.
At the heart of a framework is the *Template Method*: a method,
defined in the base class,
that drives the application by calling other base-class methods,
some of which you override.

Python's own `unittest` is this kind of application framework.
You subclass `TestCase` and supply `setUp()`, your `test_*` methods,
and `tearDown()`.
`TestCase.run()` is the template method.
It calls `setUp()`, then your test method, then `tearDown()`.
Constructing a `TestCase` runs nothing;
the test runner calls `run()` on the finished object.

## The Fixed Algorithm

A Template Method fixes the shape of the algorithm in the base class.
Subclasses provide the individual steps.
The `@final` decorator from `typing`,
used on a class in [Making a Class Final](17_Metaprogramming.md#making-a-class-final),
also works on a single method.
It locks the template method so a subclass cannot change the overall flow.
Here, `@final` on `run()` rejects any subclass that overrides it:

```python
# template_method.py
from typing import final, override

class ApplicationFramework:
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

MyApp().run()
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
```

The client supplies `customize1()` and `customize2()`.
`run()` starts the engine that drives the application.
In a GUI program that engine is the main event loop.

The base class calls code written after it, sometimes years after.
Framework authors call this the *Hollywood Principle*: "don't call us,
we'll call you."
Your code supplies the steps; the framework decides when they run.
The general name for this reversal is *Inversion of Control*:
the framework holds the flow of control and calls into your code,
rather than your code calling into a library.

`@final` is only enforced by the type checker.
At runtime the decorator only sets `__final__ = True` on the function,
and nothing in the interpreter reads that attribute.
If you need the interpreter to refuse an override,
the `__init_subclass__()` technique from [Making a Class Final](17_Metaprogramming.md#making-a-class-final)
also works with methods, raising an exception when `"run" in cls.__dict__`.

The step methods default to `...`,
so a subclass overrides only the steps it cares about,
and a forgotten step silently does nothing.
This kind of optional step is a *hook*.
The `setUp()` and `tearDown()` in the opening example are hooks:
`TestCase` supplies do-nothing versions,
so a test class that needs no setup skips them.
This silence hides a misspelling:
`def customise1()` adds a new method and leaves the base's do-nothing version in place.
That's why every step override in these listings is decorated with `@override`.
This way, the checker rejects a method that overrides nothing.

If every subclass must supply a step,
inherit from `ABC` and declare the step with `@abstractmethod`,
as shown in [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance).
The runtime then refuses to instantiate a subclass that forgot it.

In the test, we supply a recording subclass and verify the fixed flow:

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

    Recorder().run()  # The client starts the engine
    assert calls == ["one", "two", "one", "two"]  # Loop runs twice
```

### Don't Start the Engine in the Constructor {#dont-start-the-engine-in-the-constructor}

`ApplicationFramework` requires the client to start the framework engine.
The example below shows what goes wrong when the client forgets to do this.

A framework can call `run()` from its own constructor.
A subclass with its own `__init__()` encounters a pitfall.
`run()` calls methods the subclass supplies,
so a subclass that defines its own `__init__()` must finish its own setup before it calls `super().__init__()`.
If you call it first, in the usual style,
the engine runs using a half-initialized state:

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
        self.name = name  # ...before this line runs

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

try:
    Greeter("Robin")
except AttributeError as e:
    print(e)
#: 'Greeter' object has no attribute 'name'
```

`Greeter("Robin")` never runs.
`super().__init__()` starts the engine, the engine calls `step()`,
and `step()` reads `self.name` one line before the constructor assigns it.
The quick fix is reordering: assign `self.name` first,
then call `super().__init__()`.
That works, but it inverts the convention Python programmers understand,
and the next subclass author might restore the usual order without thinking.
The reliable fix changes the framework: separate construction from starting,
and have the client call `run()` explicitly on a fully built object.
That is why `ApplicationFramework` has no `__init__()` and the client writes `MyApp().run()`.

### Substitutability

This pattern leans on the [Liskov Substitution Principle](20_Rethinking_Objects.md#liskov-substitution):
when code expects a base-class instance,
an instance of any subclass must work in its place.
The base `run()` calls `customize1()` and `customize2()`,
trusting that whatever a subclass supplies still fits the algorithm's shape.
An override that breaks that trust corrupts the fixed algorithm even though the code still type-checks:
raising an exception where the base would not,
or leaving a step empty when the flow depends on it.
That last case is the price of the `...` defaults above.
They make a step optional,
and nothing distinguishes "deliberately empty" from "forgotten"
(when a step must not be forgotten, use `@abstractmethod`).
The Template Method only works when every subclass is a faithful substitute for its base.

## Passing the Steps as Functions

Subclassing is one way to supply varying steps, but not the only one.
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

Both the Template Method and the function version have a fixed algorithm and varying steps.
If the steps share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions is lighter and avoids a class hierarchy.
The subclass form also gets optional steps without extra work,
since the base supplies the `...` default;
the function form must give each parameter a default of its own.

The function version also needs no `@final`,
a decorator that stops an override only when the checker runs.
Here a caller supplies the steps and cannot replace the loop,
because no subclass exists through which to replace it.
Structure fixes the algorithm instead of relying on a decorator the runtime ignores.

Passing functions is not the *Strategy* pattern,
although the two look alike at the call site.
A Strategy swaps out a whole algorithm behind a single interface.
Here the algorithm stays where it is and only uses external steps.
The choice between a class and a function is the same trade-off as in [Function Objects](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime).
A hook that holds no state is usually better as a function than as a method to override.

## What Actually Fixes the Algorithm

The fixed algorithm is only as fixed as the mechanism holding it.
This chapter shows four.
Each has a cost, and each protects against a different way of breaking the flow:

- Structure, in `template_function.py`:
  no subclass exists through which to replace the loop.
  It costs nothing and cannot be bypassed,
  but it only applies when you can pass functions instead of subclassing.
- The checker, via `@final`: it reports an override.
  It costs one decorator and protects everyone who runs the checker.
- The interpreter, via `__init_subclass__()`:
  it refuses the offending subclass outright.
  It costs a base-class method and protects everyone,
  including the caller who skips the checker.
- Discipline, via the Liskov Substitution Principle:
  this governs whether each step is a faithful substitute,
  but no tool checks it.
  It reaches what the other three cannot:
  what the steps do once the flow itself is safe.

Ask how the algorithm might break, and choose the mechanism that protects it.

## Exercises

1.  Create a framework that takes a list of file names.
    It opens every file but the last for reading, and the last one for writing.
    It processes each input file by an undetermined policy,
    and writes the output to the last file.
    Customize it two ways, once by subclassing and once by passing a function:

    1.  Convert all the letters in each file to uppercase.
    2.  Treat the first file as a list of search words, one per line,
        and report which of those words appear in each remaining input file.
2.  Fix `premature_engine.py` both ways:
    first reorder the two lines in `Greeter.__init__()`,
    then instead redesign `Framework` so clients construct the object and call `run()` explicitly.
    Which fix still protects a second subclass author who has never read this chapter?
3.  Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
    Run it, then run `ty` over it.
    Which of the two, Python or `ty`, objects to the change?
    What does that tell you about where the fixed algorithm's guarantee comes from?
4.  Write two subclasses of `ApplicationFramework` that both type-check but break the fixed algorithm:
    one whose `customize1()` raises an exception the base never raises,
    and one that leaves `customize2()` at its `...` default when the flow depends on it.
    `ty` reports neither.
    What would have to be true of the base class for a checker to catch either one?
