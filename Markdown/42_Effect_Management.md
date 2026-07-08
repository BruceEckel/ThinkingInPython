# Effect Management

In numerous places throughout this book, we have emphasized the benefits of pure functions:

- [Functional Programming](41_Functional_Programming.md#pure-functions) contrasts `double()`, a pure function, with `withdraw()`, which depends on state left over from earlier calls.
- [Performance](19_Performance.md#caching) turns naive recursive Fibonacci from 242,785 calls into 26 with `functools.cache`. Caching only works because the cached function is pure.
- [Rethinking Objects](21_Rethinking_Objects.md#polymorphism-without-inheritance) turns shapes into immutable data, so one pure function replaces a method on each class.
- [Observer](32_Observer.md#a-visual-example-of-observers) has `recolored()` return a new grid instead of mutating the one it received, so a test checks the change with no GUI in sight.
- [Multiple Dispatching](33_Multiple_Dispatching.md#one-type-or-many) reduces competition between items to pure logic, a dictionary lookup with nothing to mock.
- [Composite and Interpreter](35_Composite_and_Interpreter.md#simplification-rewrites-the-tree) has `simplify()` return a new tree instead of editing the one it receives.

There's one important thing these all have in common: you can verify function purity just by examining the code in that function.
