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
Involving the time of day has turned your function from pure to impure,
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

There are two schools of thought on this:

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

[[If it doesn't somehow affect the environmnent, the computer becomes pointless except as a space heater]]

## A Taxonomy of Benefits

- Simple pure/impure: concurrency and testability
- By further subdividing the impure portion we can produce specific benefits:
- Functional Error Handling: trackable failure, and testability
- Tracking side causes: testability (replace side cause during testing)
- Tracking side effects: replace with dummy side effect for testing

## Converting Effectful to Pure

- Catching exceptions within your function (but you must know what exceptions your callees raise)
- Creating a restrictive type argument: for example an int that doesn't accept zero

## Effect Management Systems

### Native Effect Managment

### Library Effect Management

## Effect Management for Python?

[[Survey, libraries that are pieces, possibility of adding effect tracking to the Python type system]]
