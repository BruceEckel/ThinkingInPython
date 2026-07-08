# Effect Management

In numerous places throughout this book, we have emphasized the benefits of pure functions:

- [Functional Programming](40_Functional_Programming.md#pure-functions) contrasts `double()`, a pure function, with `withdraw()`, which depends on state left over from earlier calls.
- [Performance](18_Performance.md#caching) turns naive recursive Fibonacci from 242,785 calls into 26 with `functools.cache`. Caching only works because the cached function is pure.
- [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance) turns shapes into immutable data, so one pure function replaces a method on each class.
- [Observer](31_Observer.md#a-visual-example-of-observers) has `recolored()` return a new grid instead of mutating the one it received, so a test checks the change with no GUI in sight.
- [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many) reduces competition between items to pure logic, a dictionary lookup with nothing to mock.
- [Composite and Interpreter](34_Composite_and_Interpreter.md#simplification-rewrites-the-tree) has `simplify()` return a new tree instead of editing the one it receives.

There's one important thing these all have in common: you can verify function purity just by examining the code in that function.

What happens if your potentially-pure function calls other functions?
If one or more of those other functions have side effects, their impurity causes the calling function to also be impure.
And to discover whether a function is impure, you either have to trust the documentation or examine that function's code yourself.
This rapidly becomes tedious and error-prone.
It would be great if the type checking system could perform purity verification for you.
This is called an *Effect Management System*, and this chapter explores aspects of Effect Management.

## What is an Effect?

An *Effect* is anything other than purity.
We say that a function has *side effects* if the result of calling it is anything other than returning a result.
For example, it might:

- Display something on the console
- Change a pixel on your screen
- Activate a motor
- Write to a database
- Make a network request
- Modify a non-local variable

Side effects are relatively easy to spot because they change things in their environment.

But the meaning of "Effect" is broader than just side effects.
It also encompasses environmental impacts on the function.
For example, suppose your function reads the time of day, or a random number.
This doesn't change anything in the environment.
However, the result of your function is almost certainly going to be different from one call to the next
(unless your function ignores the time of day, but we will treat that case as ignorable).
Involving the time of day or a random number has turned your function from pure to impure,
even though your function hasn't modified its environment.
These are called *side causes* (which matches nicely with side effects) or *implicit inputs*.

Thus, Effects are the union of side effects and side causes.
But there's another factor that doesn't quite fit either category.

## Are Exceptions Impure?

Consider the following:

```python
# divide_by_zero_impurity.py
def slope(rise: int, run: int) -> float:
    return rise / run
```

This always produces the same result for the same inputs, *except when `run` is zero*.
Because an exception is raised instead of returning a result, does that break purity?

There are two schools of thought:

1. **Pure**: Raising `ZeroDivisionError` instead of returning a number does not break purity.
    The same arguments still produce that same exception every time.
    The function reads nothing outside itself and changes nothing outside itself.
    Purity says the outcome depends on the arguments alone.

    Formal computer science theory backs this up.
    Pure languages like Haskell treat an unhandled runtime exception or crash as a *bottom* value, denoted ⊥.
    A bottom value represents a computation that does not terminate normally or result in a standard value.
    Because ⊥ is a valid theoretical value, throwing an uncatchable error is technically referentially transparent.
    You could replace the function call with the crash itself, and the program's behavior wouldn't change.

2. **Functional**: Exceptions bypass normal control flow which makes code difficult to reason about.
To make code easier to reason about, functional programming avoids exceptions altogether.
A *Total Function* doesn't raise exceptions, but instead returns errors as data using explicit wrapper types,
as we saw in [Functional Error Handling](41_Functional_Error_Handling.md).

From an Effect Management standpoint, exceptions are impure.
If you write a function `a()` that calls a function `b()` that raises an exception,
then `a()` also raises that exception unless it is caught within `a()`.
To know the Effects that your function has, exceptions must be tracked as Effects on all functions.

## A Program can Never be Pure

A perfectly pure program computes something but never lets anyone see it.
It reads nothing from its environment and changes nothing in its environment,
so its result never reaches a screen, a file, a socket, or even the exit code the operating system checks.
From outside the process, that program is indistinguishable from a program that computes nothing at all.

```python
# pure_and_pointless.py
import timeit

def compute_and_discard() -> None:
    total = 0
    for i in range(2_000_000):
        total += i * i

def do_nothing() -> None:
    pass

busy = timeit.timeit(compute_and_discard, number=5)
idle = timeit.timeit(do_nothing, number=5)
print(f"burned real CPU time for nothing: {busy > idle * 100}")
#: burned real CPU time for nothing: True
```

`compute_and_discard()` and `do_nothing()` produce the same observable result: none.
Neither prints, writes, nor returns anything a caller can act on.
But `compute_and_discard()` still takes measurably longer to run,
because Python does not notice the work is worthless and skip it.
A perfectly pure computation, followed to its logical end, is a space heater with extra steps.

Effects are not a defect to design away.
They are the entire reason a program exists.
The goal of Effect Management is not to eliminate effects.
It is to know exactly which parts of a program have them, so the rest can stay pure.

## A Taxonomy of Benefits

- Simple pure/impure: concurrency and testability
- By further subdividing the impure portion we can produce specific benefits:
- Functional Error Handling: trackable failure, and testability
- Tracking side causes: testability (replace side cause during testing)
- Tracking side effects: replace with dummy side effect for testing

## Converting Effectful to Pure

Let's revisit `slope()` from `divide_by_zero_impurity.py`.
We can transform away the exception Effect, which makes the function pure again.
Here are three ways to do it.

### Return a Result Type

Wrap the answer and the failure in a `Result`,
the way [Functional Error Handling](41_Functional_Error_Handling.md#turning-exceptions-into-results) does.
`result.py` and `safe.py` are shared helpers, so this chapter imports them directly instead of rebuilding them.
Decorate the original `slope()`, unchanged, and every exception it raises becomes a value instead of a crash:

```python
# slope_result.py
from result import Failure, Success
from safe import safe

@safe
def slope(rise: int, run: int) -> float:
    return rise / run

for args in [(10, 2), (10, 0)]:
    match slope(*args):
        case Success(answer):
            print(f"slope{args} = {answer}")
        case Failure(error):
            print(f"slope{args}: {type(error).__name__}")
#: slope(10, 2) = 5.0
#: slope(10, 0): ZeroDivisionError
```

`slope()`'s body never changed.
`@safe` catches whatever it raises, so the fix lives entirely outside the function being fixed.
`slope()` is total again, and `match` still forces the caller to handle both outcomes.
Nothing escapes through a raised exception, because `@safe` never lets one leave.

### Catch the Exception You Expect

A narrower fix keeps the exception local.
`slope()` can catch the one exception it knows about
and fold the failure into an ordinary value of its existing return type, `float`,
instead of introducing a new type:

```python
# slope_catch.py
def validate(run: int) -> int:
    if run < 0:
        raise ValueError(f"run cannot be negative: {run}")
    return run

def slope(rise: int, run: int) -> float:
    try:
        return rise / validate(run)
    except ZeroDivisionError:
        return float("inf")

print(slope(10, 2))
#: 5.0
print(slope(10, 0))
#: inf
try:
    slope(10, -1)
except ValueError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: ValueError: run cannot be negative: -1
```

This works, and it needs no new type.
But it only guards the exception `slope()` was written to expect.
`validate()` raises `ValueError` for a negative `run`,
an exception `slope()` never anticipated,
and it passes straight through the `try` untouched.
Catching by hand is only as complete as your knowledge of every exception every callee can raise,
which is exactly the tracking problem an Effect Management System exists to solve.

### Make the Bad Value Impossible

The third approach removes the failure instead of handling it.
[Data Classes as Types](12_Data_Classes_as_Types.md#a-value-that-must-be-checked-everywhere)
makes illegal values impossible to construct.
Give `run` a type that cannot hold zero,
and `slope()` never needs to check for zero at all:

```python
# slope_nonzero.py
from dataclasses import dataclass

@dataclass(frozen=True)
class NonZero:
    value: int

    def __post_init__(self) -> None:
        if self.value == 0:
            raise ValueError("NonZero cannot hold 0")

def slope(rise: int, run: NonZero) -> float:
    return rise / run.value

print(slope(10, NonZero(2)))
#: 5.0
try:
    NonZero(0)
except ValueError as e:
    print(e)
#: NonZero cannot hold 0
```

The check still happens, but only once, at the one place a `NonZero` comes into existence.
Every function that receives a `NonZero`, including `slope()`, inherits the guarantee for free.
`slope()` was never in danger of dividing by zero, so it needed no `try` and no `Result` to say so.

All three approaches produce a pure `slope()`, but they push the cost to different places.
A `Result` makes every caller handle failure explicitly, at every call site.
Catching by hand hides the fix inside `slope()`,
at the cost of a blind spot for any exception nobody thought to catch.
A restrictive type pays once, at construction,
and every function downstream is pure by inheritance rather than by discipline.

## Effect Management Systems

### Native Effect Managment

### Library Effect Management

## Effect Management for Python?

[[Survey, libraries that are pieces, possibility of adding effect tracking to the Python type system]]
