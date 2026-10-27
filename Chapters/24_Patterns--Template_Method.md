# Template Method

> An algorithm runs the same sequence of steps every time,
> and some of those steps differ from one use to the next.
> A *Template Method* sets the sequence and lets you supply the steps that vary.

An application framework lets you build a new application by reusing its existing classes and overriding methods to customize behavior.
At the heart of a framework is the *Template Method* of *GoF Design Patterns*:
a base-class method that drives the application by calling other base-class methods,
some of which you override.

Python's own `unittest` is this kind of application framework.
You subclass `TestCase` and supply `setUp()`, your `test_*` methods,
and `tearDown()`.
`TestCase.run()` is the template method.
It calls `setUp()`, then your test method, then `tearDown()`.
Constructing a `TestCase` records the name of the test method to run.
The test runner calls `run()` on the finished object.

## The Anchored Algorithm

A *Template Method* anchors the algorithm's sequence of steps in the base class.
Subclasses provide the individual steps.

[Making a Class Final](17_Techniques--Metaprogramming.md#making-a-class-final)
puts the `typing.final` decorator on a class.
The decorator also works on a single method.
On a method, it declares that no subclass may override that method.
`run()` is the template method.
`@final` on `run()` makes the type checker reject any subclass that overrides it:

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

The inherited `run()` holds the loop and calls the steps `MyApp` supplies,
so `MyApp().run()` starts the engine that drives the application.

A test supplies steps that record their calls,
confirms that the record stays empty after construction,
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
At runtime the decorator sets `__final__ = True` on the function.
The interpreter ignores that attribute.
Your own code can read it.
If you want an override to fail at runtime,
the [`__init_subclass__()` technique](17_Techniques--Metaprogramming.md#making-a-class-final)
also works with methods.
`near_miss.py` in the next section includes that check.
The check raises a `TypeError` when a subclass replaces a function that carries `__final__`.

### Hooks and the Misspelled Override

The step methods default to `...`,
so a subclass overrides only the steps that matter to it.
This kind of optional step is a *hook*.
The `setUp()` and `tearDown()` in the opening example are hooks.
`TestCase` supplies empty versions,
so a test class overrides `setUp()` only when it has setup work to do.

A forgotten step silently runs the base's `...` body.
The empty default also hides a misspelling.
`def customise1()` ('s' instead of 'z')
adds a new method and leaves the base's empty version in place.
So every step override in these listings carries [`@override`](07_Foundations--Classes.md#marking-overrides-with-override).
The type checker then rejects a method that overrides nothing.

That check depends on the decorator.
If you leave `@override` off the misspelled method,
the checker accepts it as a new method,
because the typing rules let a subclass add any method.
A runtime check can reject the misspelled method.
`CheckedFramework` inherits from `ApplicationFramework` and adds that check.
Its `__init_subclass__()` runs at each subclass's `class` statement,
and uses the standard library's `difflib` to find names that nearly match:

```python
# near_miss.py
from difflib import get_close_matches
from typing import override
from exceptions import expected
from framework import ApplicationFramework

class CheckedFramework(ApplicationFramework):
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

class MyApp(CheckedFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Typo(CheckedFramework):
        def customise1(self) -> None:
            print("never runs")
#: [TypeError] Typo.customise1: did you mean customize1?

with expected(TypeError):
    class Hijack(CheckedFramework):
        def run(self) -> None:  # type: ignore
            print("never runs")
#: [TypeError] Hijack.run overrides a @final method

with expected(TypeError):
    class Weird(CheckedFramework):
        def customer(self) -> None: ...
#: [TypeError] Weird.customer: did you mean customize2?
```

`inherited` collects every non-dunder name the base classes define.
For `MyApp` those bases are `CheckedFramework`, which adds no such name,
and `ApplicationFramework`, which supplies `run` and the two steps.
For each name the subclass defines,
`getattr(super(cls, cls), name, None)` finds the attribute that the name replaces,
searching the classes that follow `cls` in its [method resolution order](07_Foundations--Classes.md#method-resolution-order).

The `__final__` check exists because a subclass that replaces `run()` moves the algorithm out of the base class,
and `@final` stops that replacement only when the type checker runs.

The `__final__` check reads a flag rather than a method name.
A second `@final` instance method in `ApplicationFramework` therefore needs no change to `__init_subclass__()`.
The `class` statement of a subclass that replaces that method raises the same `TypeError`.
The check misses a `@final` on a `@property`,
and a `@final` written above `@classmethod` or `@staticmethod`.
For those, `getattr()` on the class returns the property object, a bound method,
or the bare function.
None of them carries `__final__`.
Written below `@classmethod` or `@staticmethod`, `@final` marks the function,
which `getattr()` returns as the bare function or through a bound method.
The check then catches the override.

Reading the attribute through `getattr()` also passes the type checker,
because `getattr()` with a default accepts any name.
A function's type declares no `__final__`,
so the checker reports a direct read such as `ApplicationFramework.run.__final__` as an unresolved attribute.

A name that matches a step, such as `customize1`, is an ordinary override.
A name far from every inherited name, such as `report()`,
is an ordinary new method.
Both pass the check.
The misspelled `customise1` fails at import time,
before the framework runs and calls the empty default in place of the step.

Rejecting every new method also catches the typo, but it forbids `report()` too.
A framework that bans helper methods in its subclasses is too restrictive.

The close-match check also rejects legitimate names.
`class Weird` fails, although its author meant `customer()`.
`customer` and `customize2` share the six letters `custom` and an `e`,
a similarity of 0.78.
`get_close_matches()` flags any name that scores 0.6 or higher.
A team that adopts this check should expect to catch typos and to rename an occasional legitimate method.

If every subclass must supply a step,
inherit from `ABC` and declare that step with [`@abstractmethod`](20_Patterns--Rethinking_Objects.md#abstract-base-classes).
Instantiating a subclass that leaves the step abstract then raises a `TypeError`,
and the type checker reports the attempt.
The older convention gives the step a body that raises `NotImplementedError`.
Under that convention,
Python instantiates the same subclass and the type checker accepts it.
The step raises `NotImplementedError` when `run()` calls it,
after any earlier steps have run.

### Don't Start the Engine in the Constructor {#dont-start-the-engine-in-the-constructor}

The client starts the engine, not `ApplicationFramework`.
A framework can call `run()` from its own constructor,
but that constrains any subclass with its own `__init__()`.
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

`super().__init__()` calls `run()`, `run()` calls `step()`,
and `step()` reads `self.name` before the constructor assigns it.

The quick repair is reordering.
Assign `self.name` first, then call `super().__init__()`.
That works, but it inverts the convention Python programmers expect.
The next subclass author might restore the usual order out of habit.
The reliable repair changes the framework.
Separate construction from starting,
and have the client call `run()` on a fully built object.
So `ApplicationFramework` has no `__init__()`,
and the client calls `MyApp().run()`.

### Substitutability

The *Template Method* depends on the [Liskov Substitution Principle](20_Patterns--Rethinking_Objects.md#liskov-substitution):
when code expects a base-class instance,
an instance of a subclass must work in its place.
The base `run()` calls `customize1()` and `customize2()`.
The algorithm works only if each method the subclass supplies performs its step every time `run()` calls it.
A subclass can break that requirement in three ways and still pass the type checker:
it raises an exception where the base does not,
leaves a step empty when the anchored algorithm depends on it,
or performs the step on one pass and skips the next.
The listing shows the third failure:

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

    @override
    def customize2(self) -> None:
        print("Say no more, say no more!")

OnlyOnce().run()
#: Nudge, nudge, wink, wink!
#: Say no more, say no more!
#: Say no more, say no more!
```

Each step's name, parameters, and return type match the base,
so the type checker accepts `@override` on both methods.
The base states its algorithm in the loop, not in any type.
Each pass calls the step, so each pass must perform it.

An unexpected exception, an empty step the flow needs,
and a skipped pass each stop `run()` from performing every step on every pass.
Because the `...` defaults make a step optional,
a step left empty on purpose looks identical to a forgotten one.
The *Template Method* works only when every subclass is a faithful substitute for its base.

## Passing the Steps as Functions

A subclass is one way to supply the varying steps.
Because Python functions are first-class,
you can also pass the steps as arguments:

```python
# template_function.py
from collections.abc import Callable

type Step = Callable[[], None]

def run_framework(customize1: Step,
                  customize2: Step = lambda: None) -> None:
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

run_framework(lambda: print("one"))
#: one
#: one
```

The figure lays the subclass form and the function form side by side,
starting from the base class with its empty hooks:

![](_images/template_method_story)

The loop and its two step slots stay the same in all three frames.
The box beneath them changes from empty hooks to `MyApp` to two lambdas.
In frame 3 a function, `run_framework()`,
holds the loop in place of `ApplicationFramework`.
In the first two frames each arrow is a call through `self`,
and in frame 2 those calls reach the subclass's methods.
In frame 3 the arrow labels read `customize1()` and `customize2()`,
with no `self`.
`run_framework()` calls its own parameters.
The output column shows that the lambdas print the same four lines as `MyApp`.

Both the *Template Method* and the function version have an anchored algorithm and varying steps.
If the steps share state, build on each other, or come as a coherent group,
the subclass is clearer.
If each step is independent,
passing functions takes fewer lines and needs no class hierarchy.

The subclass form also makes each step optional,
since the base supplies the `...` default.
The function form makes a step optional by giving its parameter a default.
With `lambda: None` as the default,
the loop calls both steps on every pass and needs no `None` test.
`customize1` is a required parameter,
so the type checker reports a call that omits it.

The function version also needs no `@final`.
Here a caller passes the steps in as arguments.
The loop stays in the body of `run_framework()`, out of the caller's reach.
`@final` stops an override only when the type checker runs.
Structure anchors the algorithm,
and that anchor holds at runtime as well as under the type checker.

Passing functions is not the *Strategy* pattern,
although at the call site both pass a function as an argument.
A *Strategy* swaps out a whole algorithm behind a single interface.
In `template_function.py` the algorithm stays in `run_framework()`,
and the caller supplies the steps.

A stateless step is usually better as a function than as an overridden method.
You make the same choice between a class and a function when you write a [*Strategy*](27_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime).

## What Anchors the Algorithm

Each of this chapter's four anchors guards against a different way of breaking the anchored algorithm:

- Structure, in `template_function.py`.
  The loop lives in a function body, out of every caller's reach.
  This anchor works only when you can pass functions instead of subclassing.
- The type checker, via `@final`.
  It reports an overridden `run()` before the program runs.
- The interpreter, via `__init_subclass__()`.
  It raises a `TypeError` at an offending subclass's `class` statement,
  whether the subclass overrides `run()` or misspells a hook.
  This anchor holds at runtime,
  whereas the type checker alone enforces `@final`.
- Discipline, via the Liskov Substitution Principle.
  The principle governs whether each step is a faithful substitute.
  `@abstractmethod` ensures that a required step exists.
  No tool checks what the step does.

Ask how the algorithm might break, and choose the mechanism that protects it.

## Exercises

Try each exercise before opening its [solution](../Solutions/24_Patterns--Template_Method/).

1.  Create a framework that takes a list of file names.
    It opens every file but the last for reading, and the last one for writing.
    It processes each input file by a step the subclass or the function supplies,
    and writes the output to the last file.
    Supply each of these steps twice,
    once by subclassing and once by passing a function:

    1.  Convert all the letters in each file to uppercase.
    2.  Treat the first file as a list of search words, one per line,
        and report which of those words appear in each remaining input file.
2.  Repair `premature_engine.py` both ways:
    first reorder the two lines in `Greeter.__init__()`,
    then redesign `Framework` instead,
    so clients construct the object and then call `run()`.
    Which repair still protects a second subclass author who has not read this chapter?
3.  Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
    Run it, then run `ty` over it.
    Which of the two, Python or the type checker, objects to the change?
    What does that tell you about the source of the anchored algorithm's guarantee?
4.  Write two subclasses of `ApplicationFramework` that both type-check but break the anchored algorithm:
    one whose `customize1()` raises an exception the base does not raise,
    and one that leaves `customize2()` at its `...` default when the anchored algorithm depends on it.
    The type checker reports neither.
    What must be true of the base class for the type checker to catch either one?
5.  In `near_miss.py`, subclass `MyApp` with a class that adds a method named `reports()`.
    Predict what the `class` statement does, then run it.
    Against which names does `__init_subclass__()` compare a new method?
    Change the check so it compares a new method only against the names `ApplicationFramework` defines.
    What does the narrower check no longer catch?
