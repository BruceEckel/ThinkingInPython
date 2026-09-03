# Template Method

Application frameworks build new applications by reusing existing classes and overriding methods to customize behavior.
At the heart of a framework is the *Template Method* of *GoF Design Patterns*:
a method, defined in the base class,
that drives the application by calling other base-class methods,
some of which you override.

Python's own `unittest` is this kind of application framework.
You subclass `TestCase` and supply `setUp()`, your `test_*` methods,
and `tearDown()`.
`TestCase.run()` is the template method.
It calls `setUp()`, then your test method, then `tearDown()`.
Constructing a `TestCase` runs nothing.
The test runner calls `run()` on the finished object.

## The Anchored Algorithm

A Template Method anchors the shape of the algorithm in the base class.
Subclasses provide the individual steps.
The `typing.final` decorator,
used on a class in [Making a Class Final](17_Techniques--Metaprogramming.md#making-a-class-final),
also works on a single method.
It locks the template method so a subclass cannot change the flow.
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

# Create an application by filling in the steps:
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

The client supplies `customize1()` and `customize2()` in the derived class.
`run()` starts the engine that drives the application.

The base class calls code written later, sometimes years later.
Framework authors call this the *Hollywood Principle*: "don't call us,
we'll call you."
The general name for this reversal is *Inversion of Control*:
the framework defines the flow of control and calls your code,
rather than your code calling into a library.

Only the type checker enforces `@final`.
At runtime the decorator only sets `__final__ = True` on the function,
and nothing in the interpreter reads that attribute.
If the interpreter should refuse an override,
the `__init_subclass__()` technique from [Making a Class Final](17_Techniques--Metaprogramming.md#making-a-class-final)
also works with methods, raising an exception when `"run" in cls.__dict__`.

The step methods default to `...`,
so a subclass overrides only the steps it cares about,
and a forgotten step silently does nothing.
This kind of optional step is a *hook*.
The `setUp()` and `tearDown()` in the opening example are hooks:
`TestCase` supplies do-nothing versions,
so a test class that needs no setup skips them.
This silence hides a misspelling: `def customise1()` ('s' instead of 'z')
adds a new method and leaves the base's do-nothing version in place.
That is why every step override in these listings carries `@override`:
the type checker then rejects a method that overrides nothing.

The checker sees only the decorator.
Leave `@override` off the misspelled method and the checker accepts it as a new method.
No typing construct forbids a subclass from adding methods,
so the checker cannot catch this case.
The interpreter can.
The base class's `__init_subclass__()` runs at each subclass's `class` statement,
and the standard library's `difflib` finds names that nearly match:

```python
# near_miss.py
from difflib import get_close_matches
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        hooks = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            if name == "run":
                raise TypeError(
                    f"{cls.__name__}.run "
                    "overrides the anchor"
                )
            if name in hooks:
                continue
            if near := get_close_matches(name, hooks):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

try:
    class Typo(ApplicationFramework):
        def customise1(self) -> None:
            print("never runs")
except TypeError as e:
    print(e)
#: Typo.customise1: did you mean customize1?

try:
    class Hijack(ApplicationFramework):
        def run(self) -> None:  # type: ignore
            print("never runs")
except TypeError as e:
    print(e)
#: Hijack.run overrides the anchor

try:
    class Weird(ApplicationFramework):
        def customized_report(self) -> None: ...
except TypeError as e:
    print(e)
#: Weird.customized_report: did you mean customize2?
```

`hooks` collects every non-dunder name the base classes define,
including `run` itself.
A name that matches `run` exactly is rejected outright:
`class Hijack` never finishes,
because letting a subclass replace the anchor would defeat it,
and `@final` only stops that replacement for the type checker.
A name that matches a step, `customize1` or `customize2`,
is an ordinary override, and a name that resembles none of them,
like `report()`, is an ordinary new method.
Both of those pass.
Only a near miss produces a `TypeError`,
and the message names the method the author probably meant.
The `class Typo` statement raises a `TypeError` instead of finishing too,
so the misspelling fails at import time,
not later when the framework runs and the step silently does nothing.
Rejecting every new method would catch the typo too,
but it would also forbid `report()`,
and a framework that bans helper methods in its subclasses is too restrictive.
The heuristic cuts the other way too: `class Weird` never finishes either,
because `customized_report()` shares enough letters with `customize2` for `get_close_matches` to flag it,
even though it is not a typo.
A team that adopts this check should expect to rename an occasional legitimate method,
not just catch misspellings for free.

If every subclass must supply a step,
inherit from `ABC` and declare that step with `@abstractmethod`,
as shown in [Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance).
The runtime then refuses to instantiate a subclass that forgot it.

The test supplies a recording subclass and verifies the anchored flow:

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
    # Loop runs twice
    assert calls == ["one", "two", "one", "two"]
```

### Don't Start the Engine in the Constructor {#dont-start-the-engine-in-the-constructor}

The client starts the engine, not `ApplicationFramework`.
A framework *can* call `run()` from its own constructor,
but then a subclass with its own `__init__()` falls into a trap.
Because `run()` calls methods the subclass supplies,
the subclass must finish its own setup before it calls `super().__init__()`.
Call `super().__init__()` first, in the usual style,
and the engine runs on a half-initialized object:

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
        # With the usual style, the engine calls run()
        super().__init__()
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

`Greeter("Robin")` never finishes.
`super().__init__()` starts the engine, the engine calls `step()`,
and `step()` reads `self.name` before the constructor assigns it.
The quick repair is reordering: assign `self.name` first,
then call `super().__init__()`.
That works, but it inverts the convention Python programmers expect,
and the next subclass author might restore the usual order without thinking.
The reliable repair changes the framework: separate construction from starting,
and have the client call `run()` explicitly on a fully built object.
That is why `ApplicationFramework` has no `__init__()` and the client calls `MyApp().run()`.

### Substitutability

This pattern leans on the [Liskov Substitution Principle](20_Patterns--Rethinking_Objects.md#liskov-substitution):
when code expects a base-class instance,
an instance of a subclass must work in its place.
The base `run()` calls `customize1()` and `customize2()`,
trusting that what the subclass supplies fits the algorithm's shape.
An override can break that trust and still type-check:
it raises an exception where the base would not,
or leaves a step empty when the flow depends on it.
Either one corrupts the anchored algorithm.
The `...` defaults make a step optional,
and nothing distinguishes "deliberately empty" from "forgotten".
The Template Method works only when every subclass is a faithful substitute for its base.

## Passing the Steps as Functions

A subclass is one way to supply the varying steps.
Because Python functions are first-class,
you can also pass the steps as arguments:

```python
# template_function.py
from collections.abc import Callable

def run_framework(customize1: Callable[[], None],
                  customize2: Callable[[], None]) -> None:
    for _ in range(2):  # The anchored algorithm
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

try:
    run_framework(lambda: print("one"))  # type: ignore
except TypeError as e:
    print(f"{type(e).__name__}: missing customize2")
#: TypeError: missing customize2
```

Both the Template Method and the function version have an anchored algorithm and varying steps.
If the steps share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions is lighter and avoids a class hierarchy.
The subclass form also gets optional steps without extra work,
since the base supplies the `...` default.
The function form must give each parameter a default of its own:
omit `customize2` above and the call raises a `TypeError` instead.

The function version also needs no `@final`.
That decorator stops an override only when the type checker runs.
Here no subclass exists,
so a caller supplies the steps but cannot touch the loop.
Structure anchors the algorithm,
with no help from a decorator the runtime ignores.

Passing functions is not the *Strategy* pattern,
although the two look alike at the call site.
A Strategy swaps out a whole algorithm behind a single interface.
Here the algorithm stays put, and only its steps come from outside.
The choice between a class and a function is the same trade-off as in [Function Objects](28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime).
A stateless hook is usually better as a function than as an overridden method.

## What Anchors the Algorithm

An anchored algorithm is only as secure as its anchor.
This chapter shows four.
Each guards against a different way of breaking the flow:

- Structure, in `template_function.py`.
  No subclass exists, so nothing can replace the loop.
  This works only when you can pass functions instead of subclassing.
- The type checker, via `@final`.
  It discovers an overridden `run()` before the program executes.
- The interpreter, via `__init_subclass__()`.
  It refuses an offending subclass at its `class` statement,
  whether the subclass overrides `run()` or misspells a hook.
  This holds at runtime, whereas `@final` is only a type-checking attribute.
- Discipline, via the Liskov Substitution Principle.
  This governs whether each step is a faithful substitute,
  but no tool checks it.

Ask how the algorithm might break, and choose the mechanism that protects it.

## Exercises

1.  Create a framework that takes a list of file names.
    It opens every file but the last for reading, and the last one for writing.
    It processes each input file by a policy the customization supplies,
    and writes the output to the last file.
    Customize it two ways, once by subclassing and once by passing a function:

    1.  Convert all the letters in each file to uppercase.
    2.  Treat the first file as a list of search words, one per line,
        and report which of those words appear in each remaining input file.
2.  Repair `premature_engine.py` both ways:
    first reorder the two lines in `Greeter.__init__()`,
    then redesign `Framework` instead,
    so clients construct the object and call `run()` explicitly.
    Which repair still protects a second subclass author who has never read this chapter?
3.  Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
    Run it, then run `ty` over it.
    Which of the two, Python or `ty`, objects to the change?
    What does that tell you about where the anchored algorithm's guarantee comes from?
4.  Write two subclasses of `ApplicationFramework` that both type-check but break the anchored algorithm:
    one whose `customize1()` raises an exception the base never raises,
    and one that leaves `customize2()` at its `...` default when the flow depends on it.
    `ty` reports neither.
    What would have to be true of the base class for a type checker to catch either one?
