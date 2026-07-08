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
This is called an *Effect Management System*, and this chapter explores aspects of effect management.

## Are Exceptions Impure?

Consider the following:

```python
# divide_by_zero_impurity.py
def slope(rise: int, run: int) -> float:
    return rise / run
```

This always produces the same result for the same inputs, *except when `run` is zero*.
Because an exception is raised instead of returning a result, does that break purity?

There are three schools of thought on this:

1. **Practical**: Raising `ZeroDivisionError` instead of returning a number does not break purity.
The same arguments still produce that same exception every time,
and the function reads nothing outside itself and changes nothing outside itself.
Purity says the outcome depends on the arguments alone.

2. **Theoretical**: Formal computer science theory (and pure languages like Haskell) treats an unhandled runtime exception or crash as a "bottom" value (denoted as \(\bot \)).
A bottom value represents a computation that does not terminate normally or result in a standard value.
Because \(\bot \) is a valid theoretical value, throwing an uncatchable error is technically referentially transparent.
You could replace the function call with the crash itself, and the program's behavior wouldn't change.

3. **Functional**: Exceptions bypass normal control flow which makes code difficult to reason about.
To make code easier to reason about, functional programming avoids exceptions altogether.
A *Total Function* doesn't raise exceptions, but instead returns errors as data using explicit wrapper types, as we saw in [Functional Error Handling](41_Functional_Error_Handling.md).
