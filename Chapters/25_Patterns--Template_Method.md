# Template Method

> An algorithm runs the same sequence of steps every time,
> and some of those steps differ from one use to the next.
> A *Template Method* sets the sequence and lets you supply the steps that vary.

An application framework lets you build a new application by reusing its existing classes and overriding methods to customize behavior.
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

A *Template Method* anchors the shape of the algorithm in the base class.
Subclasses provide the individual steps.

The `typing.final` decorator,
used on a class in [Making a Class Final](17_Techniques--Metaprogramming.md#making-a-class-final),
also works on a single method.
It declares that no subclass may override the template method.
Here, `@final` on `run()` makes the type checker reject any subclass that overrides it:

```python
# framework.py
from typing import final

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...
```

`MyApp` imports the framework and supplies the two steps:

```python
# template_method.py
from typing import override
from framework import ApplicationFramework

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

A test supplies steps that record their calls,
confirms that constructing the subclass calls none of them,
then checks the order in which `run()` makes them:

```python
# test_template_method.py
from typing import override
from framework import ApplicationFramework

def test_template_method_runs_steps_in_order() -> None:
    calls: list[str] = []

    class Recorder(ApplicationFramework):
        @override
        def customize1(self) -> None:
            calls.append("one")

        @override
        def customize2(self) -> None:
            calls.append("two")

    app = Recorder()
    assert calls == []
    app.run()
    assert calls == ["one", "two", "one", "two"]
```

The base class calls code written later, sometimes years later.
Framework authors call this the *Hollywood Principle*: "don't call us,
we'll call you."
The general name for this reversal is *Inversion of Control*:
the framework defines the flow of control and calls your code,
rather than your code calling into a library.

Only the type checker enforces `@final`.
At runtime the decorator sets `__final__ = True` on the function,
and nothing in the interpreter reads that attribute.
Your own code can read it.
If you want the interpreter to refuse an override,
the [`__init_subclass__()` technique](17_Techniques--Metaprogramming.md#making-a-class-final)
also works with methods.
`near_miss.py` in the next section includes that check.
It raises an exception when a subclass replaces a function that carries `__final__`.

### Hooks and the Misspelled Override

The step methods default to `...`,
so a subclass overrides only the steps that matter to it,
and a forgotten step silently does nothing.
This kind of optional step is a *hook*.
The `setUp()` and `tearDown()` in the opening example are hooks.
`TestCase` supplies do-nothing versions,
so a test class that needs no setup skips them.

The do-nothing default also hides a misspelling.
`def customise1()` ('s' instead of 'z')
adds a new method and leaves the base's do-nothing version in place.
That is why every step override in these listings carries `@override`.
The type checker then rejects a method that overrides nothing.

That check depends on the decorator.
If you leave `@override` off the misspelled method,
the checker accepts it as a new method.
No typing construct forbids a subclass from adding methods,
so the checker cannot catch this case.
The interpreter can.
The base class's `__init_subclass__()` runs at each subclass's `class` statement,
and the standard library's `difflib` finds names that nearly match:

```python
# near_miss.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

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
        inherited = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            replaced = getattr(super(cls, cls), name, None)
            if getattr(replaced, "__final__", False):
                raise TypeError(
                    f"{cls.__name__}.{name} "
                    "overrides a @final method"
                )
            if name in inherited:
                continue
            if near := get_close_matches(name, inherited):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Typo(ApplicationFramework):
        def customise1(self) -> None:
            print("never runs")
#: [TypeError] Typo.customise1: did you mean customize1?

with expected(TypeError):
    class Hijack(ApplicationFramework):
        def run(self) -> None:  # type: ignore
            print("never runs")
#: [TypeError] Hijack.run overrides a @final method

with expected(TypeError):
    class Weird(ApplicationFramework):
        def customized_report(self) -> None: ...
#: [TypeError] Weird.customized_report: did you mean
#: customize2?
```

`inherited` collects every non-dunder name the base classes define,
including `run`.
For each name the subclass defines,
`getattr(super(cls, cls), name, None)` finds the attribute that the name replaces,
searching the classes that follow `cls` in its [method resolution order](07_Foundations--Classes.md#method-resolution-order).
If that attribute carries `__final__`,
`__init_subclass__()` raises a `TypeError`.
`class Hijack` fails because a subclass that replaces the anchor moves the algorithm out of the base class,
and `@final` stops that replacement only for the type checker.
The `__final__` check names no method,
so a second `@final` instance method in `ApplicationFramework` gets the same protection with no change to `__init_subclass__()`.
The check misses a `@final` on a `@property`,
and a `@final` written above `@classmethod` or `@staticmethod`.
For those, `getattr()` on the class returns the property object, a bound method,
or the bare function, and none of them carries `__final__`.
Written below `@classmethod` or `@staticmethod`,
`@final` marks the function that `getattr()` returns,
and the check catches the override.

Reading the attribute through `getattr()` also keeps the type checker quiet.
A function's type declares no `__final__`,
so `ty` reports `ApplicationFramework.run.__final__` as an unresolved attribute,
while `getattr()` with a default accepts any name.

A name that matches a step, `customize1` or `customize2`,
is an ordinary override, and a name that resembles none of them,
like `report()`, is an ordinary new method.
Both of those pass.
Among the remaining names,
only one that nearly matches an inherited name produces a `TypeError`,
and the message names the method the author probably meant.
The `class Typo` statement also raises a `TypeError`,
so the misspelling fails at import time,
not later when the framework runs and the step silently does nothing.

Rejecting every new method catches the typo too, but it also forbids `report()`,
and a framework that bans helper methods in its subclasses is too restrictive.
The close-match check also rejects legitimate names.
`class Weird` fails too,
because `customized_report()` shares enough letters with `customize2` for `get_close_matches()` to flag it,
although it is not a typo.
A team that adopts this check should expect to catch typos and also to rename an occasional legitimate method.

If every subclass must supply a step,
inherit from `ABC` and declare that step with [`@abstractmethod`](20_Patterns--Rethinking_Objects.md#abstract-base-classes).
The interpreter then refuses to instantiate a subclass that forgot it,
and the type checker reports the attempt.

### Don't Start the Engine in the Constructor {#dont-start-the-engine-in-the-constructor}

The client starts the engine, not `ApplicationFramework`.
A framework can call `run()` from its own constructor,
but then a subclass with its own `__init__()` falls into a trap.
Because `run()` calls methods the subclass supplies,
the subclass must finish its own setup before it calls `super().__init__()`.
Calling `super().__init__()` first, in the usual style,
runs the engine on a half-initialized object:

```python
# premature_engine.py
from typing import final, override
from exceptions import expect

class Framework:
    def __init__(self) -> None:
        self.run()

    @final
    def run(self) -> None:
        self.step()

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        # In the usual order, this call runs the engine
        super().__init__()
        self.name = name  # ...before this line runs

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

expect(AttributeError, Greeter, "Robin")
#: [AttributeError] 'Greeter' object has no attribute 'name'
```

`Greeter("Robin")` fails with an `AttributeError`.
`super().__init__()` starts the engine, the engine calls `step()`,
and `step()` reads `self.name` before the constructor assigns it.

The quick repair is reordering.
Assign `self.name` first, then call `super().__init__()`.
That works, but it inverts the convention Python programmers expect,
and the next subclass author might restore the usual order without thinking.
The reliable repair changes the framework.
Separate construction from starting,
and have the client call `run()` explicitly on a fully built object.
That is why `ApplicationFramework` has no `__init__()` and the client calls `MyApp().run()`.

### Substitutability

The *Template Method* depends on the [Liskov Substitution Principle](20_Patterns--Rethinking_Objects.md#liskov-substitution):
when code expects a base-class instance,
an instance of a subclass must work in its place.
The base `run()` calls `customize1()` and `customize2()`,
trusting that what the subclass supplies fits the algorithm's shape.
A subclass can break that trust and still type-check.
It raises an exception where the base does not,
leaves a step empty when the flow depends on it,
or performs the step on one pass and skips the next:

```python
# faithless_step.py
from typing import override
from framework import ApplicationFramework

class OnlyOnce(ApplicationFramework):
    def __init__(self) -> None:
        self._ran = False

    @override
    def customize1(self) -> None:
        if not self._ran:  # The second pass does nothing
            self._ran = True
            print("Nudge, nudge, wink, wink!")

OnlyOnce().run()
#: Nudge, nudge, wink, wink!
```

`run()` calls `customize1()` twice, and `OnlyOnce` prints once.
The name, the parameters, and the return type all match the base,
so the type checker accepts `@override` and reports nothing.
The base states its algorithm in the loop, not in any type.
Each pass calls the step, so each pass must perform it.
An unexpected exception, an empty step the flow needs,
and a skipped pass each corrupt the anchored algorithm.
The `...` defaults make a step optional,
and nothing distinguishes "deliberately empty" from "forgotten."
The *Template Method* works only when every subclass is a faithful substitute for its base.

## Passing the Steps as Functions

A subclass is one way to supply the varying steps.
Because Python functions are first-class,
you can also pass the steps as arguments:

```python
# template_function.py
from collections.abc import Callable
from exceptions import expect

type Step = Callable[[], None]

def run_framework(customize1: Step,
                  customize2: Step) -> None:
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

expect(TypeError, run_framework, lambda: print("one"))  # type: ignore
#: [TypeError] run_framework() missing 1 required positional
#: argument: 'customize2'
```

The figure lays the subclass form and the function form side by side,
starting from the base class with its empty hooks:

![](_images/template_method_story)

The loop and its two step slots stay the same in all three frames.
The box beneath them changes,
along with the name of the function that holds the loop,
`run_framework()` in frame 3.
In the second frame each arrow is a call through `self`,
so the base calls the subclass's methods.
In the third the arrows lose `self`.
`run_framework()` calls its own parameters,
and the output column shows that the lambdas print the same four lines as `MyApp`.

Both the *Template Method* and the function version have an anchored algorithm and varying steps.
If the steps share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions is lighter and avoids a class hierarchy.

The subclass form also makes each step optional,
since the base supplies the `...` default.
The function form must give each parameter a default of its own.
Without one, omitting `customize2` in `template_function.py` raises a `TypeError`.
A do-nothing default such as `lambda: None` makes a step optional and keeps the loop free of `None` tests.

The function version also needs no `@final`.
That decorator stops an override only when the type checker runs.
Here no subclass exists,
so a caller supplies the steps but cannot touch the loop.
Structure anchors the algorithm,
with no help from a decorator the runtime ignores.

Passing functions is not the *Strategy* pattern,
although the two look alike at the call site.
A *Strategy* swaps out a whole algorithm behind a single interface.
In `template_function.py` the algorithm stays put,
and only its steps come from outside.
The choice between a class and a function is the same trade-off a [*Strategy*](28_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime)
faces.
A stateless hook is usually better as a function than as an overridden method.

## What Anchors the Algorithm

An anchored algorithm is only as secure as its anchor.
Each of this chapter's four anchors guards against a different way of breaking the flow:

- Structure, in `template_function.py`.
  No subclass exists, so nothing can replace the loop.
  This works only when you can pass functions instead of subclassing.
- The type checker, via `@final`.
  It discovers an overridden `run()` before the program executes.
- The interpreter, via `__init_subclass__()`.
  It refuses an offending subclass at its `class` statement,
  whether the subclass overrides `run()` or misspells a hook.
  This holds at runtime, whereas the type checker alone enforces `@final`.
- Discipline, via the Liskov Substitution Principle.
  This governs whether each step is a faithful substitute.
  `@abstractmethod` checks that a required step exists,
  and no tool checks what the step does.

Ask how the algorithm might break, and choose the mechanism that protects it.

## Exercises

The [solutions](../Solutions/25_Patterns--Template_Method/)
are in the book's repository.

1.  Create a framework that takes a list of file names.
    It opens every file but the last for reading, and the last one for writing.
    It processes each input file by a step the subclass or the function supplies,
    and writes the output to the last file.
    Supply each of these policies twice,
    once by subclassing and once by passing a function:

    1.  Convert all the letters in each file to uppercase.
    2.  Treat the first file as a list of search words, one per line,
        and report which of those words appear in each remaining input file.
2.  Repair `premature_engine.py` both ways:
    first reorder the two lines in `Greeter.__init__()`,
    then redesign `Framework` instead,
    so clients construct the object and call `run()` explicitly.
    Which repair still protects a second subclass author who has not read this chapter?
3.  Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
    Run it, then run `ty` over it.
    Which of the two, Python or the type checker, objects to the change?
    What does that tell you about the source of the anchored algorithm's guarantee?
4.  Write two subclasses of `ApplicationFramework` that both type-check but break the anchored algorithm:
    one whose `customize1()` raises an exception the base does not raise,
    and one that leaves `customize2()` at its `...` default when the flow depends on it.
    The type checker reports neither.
    What must be true of the base class for the type checker to catch either one?
5.  In `near_miss.py`, subclass `MyApp` with a class that adds a method named `reports()`.
    Predict what the `class` statement does, then run it.
    Against which names does `__init_subclass__()` compare a new method?
    Change the check so it compares a new method only against the names `ApplicationFramework` defines.
    What does the narrower check no longer catch?
