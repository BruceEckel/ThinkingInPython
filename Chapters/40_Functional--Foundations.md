# Foundations

> Some code you can check by reading it, and the rest you must run to find out.
> Functional programming grows the first kind at the expense of the second.

This chapter begins the book's exploration of functional programming.
The ideas are useful before you learn their names.
A pure function cannot corrupt state you overlooked.
A bug in a pure function reproduces from the arguments alone.
A test of a pure function is a call and a comparison.
The standard library supplies and tests a cache in `functools` and a sliding window in `itertools`,
so each one handles the edge case you would otherwise miss.
A function that keeps its state private is safe to run in parallel.
And you can reason about code built from small,
checkable pieces the way you check a line of algebra, by substitution.

The functional style lets you keep loops, classes, and mutation.
It asks you to notice when a piece of code can depend on its arguments alone,
and then write it that way.

This chapter builds the foundations: pure functions, immutable values,
and the ways Python lets you pass, capture, specialize, and combine functions.
[Functional Toolkits](41_Functional--Toolkits.md)
tours the standard library's support,
[Error Handling](42_Functional--Error_Handling.md)
turns failure into an ordinary value,
and [Confidence](43_Functional--Confidence.md)
examines what the discipline lets you claim about your code.
Those four chapters are Part IV.
Part V then applies the same discipline to a function's effects.
[Effect Management](44_Effects--Effect_Management.md)
tracks a function's effects in its type,
and [Generators](45_Effects--Generators.md)
supplies Python's built-in mechanism for describing a computation without running it.
[Stateless](46_Effects--Stateless.md)
and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
then build a checked Effect system on that mechanism.

## Pure Functions

A *pure function* computes its result from its arguments.
It reads only values that stay the same,
and it leaves everything outside itself as it was.
Given the same arguments, it always produces the same outcome,
whether that outcome is a returned value or a raised exception.
A *side effect* is anything a function does beyond producing that outcome,
such as printing, reading or writing a file or the network,
or mutating something outside the function.
A pure function has none.

Everything else in these chapters builds on purity.
You can reason about a pure function the way you reason about an equation:

```python
# pure_functions.py
type Balance = int

# Pure: the result depends only on the arguments:
def double(x: int) -> int:
    return x * 2

# Impure: it depends on and mutates outside state:
balance: Balance = 100
def withdraw(amount: int) -> Balance:
    global balance
    balance -= amount
    return balance

print(double(5), double(5))
#: 10 10
print(withdraw(30), withdraw(30))
#: 70 40
```

`double()` returns the same answer every time.
`withdraw()` returns a different answer each time,
because each call changes `balance` and the next call reads the new value.
To understand one `withdraw()` call you must trace every call before it.

A pure function is the most reliable code you can write,
because its arguments alone determine what it returns or raises.
You can call it from many threads at once,
because each call keeps its state private.
[Automatic Parallelism](43_Functional--Confidence.md#automatic-parallelism)
uses that safety to spread the calls across cores.
A cache can store the function's results,
because the same arguments always produce the same answer.
That makes [`functools.cache`](41_Functional--Toolkits.md#cache)
safe on a pure function, and wrong on an impure one.
And a single assertion tests a pure function,
since its arguments supply everything the test needs:

```python
# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

total = 0
def running_total(n: int) -> int:
    global total
    total += n
    return total

# The pure function needs no setup and no teardown:
assert slope(10, 2) == 5.0
assert slope(10, 2) == 5.0
# The impure one needs a reset before each check:
total = 0
assert running_total(5) == 5
total = 0  # [1]
assert running_total(5) == 5  # [2]
print("ok")
#: ok
```

If you delete the reset at `[1]`, the assertion at `[2]` fails.
`total` is still 5 from the first call, so the second call returns 10.
The reset at `[1]` is the fixture the impure version needs.
Purity removes it.

[Are Exceptions Impure?](44_Effects--Effect_Management.md#are-exceptions-impure)
asks whether raising an exception breaks the purity of `slope()`.

## Immutability

An *immutable* value cannot change after creation.
Tuples, strings, `frozenset`, and records are immutable.
Each freezes only its top level.
The tuple `([1], 2)` always holds that same list.
Anyone can still append to the list.
A tuple of strings, immutable all the way down, stays what you last read,
whatever code ran in between.
That guarantee is why removing shared mutable state is the practical core of the functional style.

Instead of modifying an object, you build a new one from the old:

```python
# immutability.py
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

p = Point(1, 2)
with expected(AttributeError):
    # A frozen instance rejects assignment
    setattr(p, "x", 5)
#: [FrozenInstanceError] cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(p, moved)
#: Point(x=1, y=2) Point(x=11, y=2)
```

The type checker rejects the direct form `p.x = 5` before the program runs.
To show that the runtime rejects the assignment too,
the listing writes it as `setattr(p, "x", 5)`, which the type checker accepts.

Restating every field works for a two-field `Point`.
For a record with many fields,
[`copy.replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
builds the new value from the old one and the fields that change,
as in `copy.replace(p, x=p.x + 10)`.

When a value is immutable,
two parts of a program can share one without coordinating,
and any number of threads can read it at once.
That safety requires copying.
Python's immutable types share no structure.
`moved = Point(p.x + 10, p.y)` in `immutability.py` builds a new `Point`.
Changing one field of a large tuple or record likewise means rebuilding the whole value,
not patching one slot in place.

Copying a two-field `Point` takes negligible time.
For a large structure that changes often,
those copies add up in time and memory.
Languages built around immutability use *persistent* data structures,
which copy the part a change touches and share the rest with the old value.
Python's standard library has none.
For such a value, keep a mutable structure private to one function,
which then changes it in place with no other code reading it between changes.

### Immutability in Annotations

Type annotations can state immutability so the type checker enforces it.
`typing.Final` marks a name bound once, at its declaration.
The read-only collection types in `collections.abc`,
such as `Sequence` and `Mapping`, expose the operations that read a collection.
They have no `append()` or item assignment,
so the type checker rejects any attempt to mutate through them:

```python
# immutable_types.py
from collections.abc import Sequence
from typing import Final

# Final marks a name the type checker won't let you rebind:
MAX_SIZE: Final[int] = 100

# Sequence is read-only: no append, no item assignment:
def total(values: Sequence[int]) -> int:
    return sum(values)

print(MAX_SIZE, total([1, 2, 3]))
#: 100 6
```

The `Sequence[int]` constraint declares that `total()` reads its argument and leaves it as it was.
The constraint governs `total()`, not the caller,
so it holds when the caller passes a mutable `list`.
The caller keeps its `list` and can append to it at any time,
including from another thread while `total()` is running.

`Final` freezes the binding, and only the binding.
If you declare `CONFIG: Final[list[int]] = [...]`,
`CONFIG.append(...)` still succeeds, for the type checker and at runtime alike.
Freezing only the binding is the [shallow-freezing lesson](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
again, with `Final` in place of `frozen=True`.
For an immutable value, make the value's own type immutable,
as in `Final[tuple[int, ...]]`.
The tuple's contents stay as built,
and `Final` keeps the name bound to that tuple.

### A Stable Hash and Safe Sharing

Immutability offers two things a mutable value cannot.
The first is a *stable hash* of the contents,
one that holds for the value's whole life,
so the value can be a dictionary key or a set member.
The second is sharing without a defensive copy.
You can hand the value to any code.
It stays as you built it.
A frozen `Point` and `MutablePoint`, its unfrozen `@dataclass` twin,
show the difference a stable hash makes:

```python
# hashable.py
from dataclasses import dataclass
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

@dataclass
class MutablePoint:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# The unfrozen twin has no hash, so it cannot be a key:
with expected(TypeError):
    hash(MutablePoint(3, 4))
#: [TypeError] unhashable type: 'MutablePoint'
```

Contents-based equality, not mutability alone, makes a type unhashable.
A plain class instance is mutable and still hashes, by identity,
so it works as a dictionary key.
`MutablePoint` and a `list` both compare by contents,
so a dictionary that stored one as a key would lose the entry if the key's contents changed.
Python therefore sets their `__hash__` to `None`.
`hash([3, 4])` raises the same `TypeError` as `hash(MutablePoint(3, 4))`.

Freezing a dataclass lets it keep contents-based equality and a hash at the same time.
[`@record`](18_Techniques--Performance.md#record) freezes `Point`,
so `Point(3, 4)` can key `distances`.
Python computes that hash from the fields, so every field must be hashable too.
Hashing a frozen record that holds a `list` still raises a `TypeError`.
`frozen_leaky.py` in [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
demonstrates that failure.
Contents-based equality together with a stable hash is why a dictionary key,
a cache entry, or a value shared across threads is normally a tuple or a record.

## Functions as First-Class Objects

A function is an object like any other, which is what *first-class* means.
You can bind a function to a name, store it in a container,
pass it as an argument, and return it from another function.

```python
# first_class.py
def shout(text: str) -> str:
    return f"{text.upper()}!"

# A function is an object you can bind to another name:
loud = shout
print(loud("hello"))
#: HELLO!
# Functions can live in a data structure:
table = {"upper": str.upper, "title": str.title}
print(table["title"]("functional python"))
#: Functional Python
```

The [Function Objects](27_Patterns--Function_Objects.md)
chapter treats first-class functions as a design pattern.

Treating functions as values lets a data lookup select which function runs,
so a dictionary of functions can replace a long `if`/`elif` chain:

```python
# dispatch.py
from collections.abc import Callable
from operator import mod
from exceptions import expected

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b
def floordiv(a: int, b: int) -> int:
    return a // b

# A table of functions replaces a long if/elif chain:
operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "//": floordiv,
}
# A row can come from outside the literal, unchanged:
operations["%"] = mod
for symbol in ["+", "-", "//", "%"]:
    print(symbol, operations[symbol](6, 4))
#: + 10
#: - 2
#: // 1
#: % 2
# A missing key is a KeyError, no else branch:
with expected(KeyError):
    operations["^"](6, 4)
#: [KeyError] '^'
```

Supporting a new operator means adding a row to the table,
whether the literal holds that row or a later line adds it,
as the `operations["%"]` line does here.
The dispatch code stays the same.
The same table of functions underlies [the dictionary factory](26_Patterns--Factory.md#the-pythonic-factory-a-dictionary)
and the plugin registries that let you add features to a program from outside its core.

[Pattern Matching](13_Techniques--Pattern_Matching.md)
replaces the same kind of `if`/`elif` chain with `match`.
`match` and the table differ in one way that decides between them.
A `match` is code, so adding an operator means editing the function,
and the type checker verifies every case.
The table is data, so adding an operator means adding a row,
which another module does at import time and a test does at runtime.
Choose `match` when you know the whole set of cases as you write the function,
and a table when code elsewhere should add cases.

## Higher-Order Functions

A [*lambda*](05_Foundations--Functions.md#lambdas)
is an unnamed function written as a single expression.
The functions in this section take lambdas as inline arguments,
where a lambda fits best.
A lambda's value is locality.
When a transformation is one short expression,
a lambda keeps it at the call site, beside the code that uses it,
instead of defining it as a named function elsewhere.
`sorted(words, key=lambda w: (len(w), w))` states the sort order,
by length and then alphabetically, right where the code sorts.

A *higher-order function* takes a function as an argument, returns one, or both.
Three built-ins cover the common cases.
`map()` applies a function to every element of an iterable.
`filter()` keeps the elements for which a function returns true.
`sorted()` accepts a `key` function that decides the ordering:

```python
# higher_order.py
numbers = [1, 2, 3, 4, 5]
# map() applies a function to each element:
squares = list(map(lambda n: n * n, numbers))
print(squares)
#: [1, 4, 9, 16, 25]
# filter() keeps the elements a predicate accepts:
evens = list(filter(lambda n: n % 2 == 0, numbers))
print(evens)
#: [2, 4]
# sorted() takes a function as its key argument:
words = ["banana", "pie", "kiwi", "watermelon"]
print(sorted(words, key=len))
#: ['pie', 'kiwi', 'banana', 'watermelon']
```

The `list()` calls are necessary.
`map()` and `filter()` return [one-shot iterators](22_Patterns--Iterators.md#an-exhausted-generator-is-silently-empty).
An iterator computes each value only when a consumer asks for it.
`print()` displays the iterator's `repr()` instead of consuming it,
so `print(map(...))` shows `<map object at 0x...>` rather than values.
Once a `list()` call or a `for` loop has consumed the iterator,
a second pass over the same object finds it silently empty.
`sorted()` must read every element before it can order any of them,
so it returns a list rather than an iterator.

`sorted()` is also the pure counterpart of [`list.sort()`](03_Foundations--Containers.md#growing-shrinking-and-sorting),
which reorders the list in place and returns `None`.
`sorted()` builds a new list and leaves its input as it was.

Prefer the comprehension when you would write a fresh lambda,
and `map()` or `filter()` when the function exists,
as [Comprehensions](16_Techniques--Comprehensions.md#the-map-and-filter-equivalent)
explains.
`sorted()`'s `key` has no comprehension equivalent,
so it is a higher-order argument either way.

Beyond how they read, a comprehension and `map()` return different things.
The comprehension builds a finished list.
`map()` returns an iterator that hands the next stage one value at a time.
A [generator expression](16_Techniques--Comprehensions.md#generator-expressions)
is the comprehension's lazy form, and removes that difference.

Higher-order functions separate the iteration from the operation.
`map()`, `filter()`,
and `sorted()` each contain the loop that iterates over the data,
so that loop appears once, inside the function.
You supply only the function each one calls on every element,
the part that differs from one use to the next.
You stop rewriting the same loop,
and with it the off-by-one and accumulator-initialization mistakes a hand-written loop allows.

Returning a function is the other half of the higher-order definition.
Such a function can wrap the function it receives with operations like timing,
retries, or logging, and return the wrapper.
A [decorator](14_Techniques--Decorators.md) does that wrapping.

## Closures

When an inner function refers to a variable from the function that created it,
Python keeps that variable alive.
The inner function plus the captured variables is a *closure*.
A closure lets a function carry state without a class:

```python
# closures.py
import inspect
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    # The inner function captures factor from this scope:
    def multiply(n: int) -> int:
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
#: 20 30
print(inspect.getclosurevars(double).nonlocals)
#: {'factor': 2}
print(inspect.getclosurevars(triple).nonlocals)
#: {'factor': 3}
```

`double` and `triple` are the same code holding different captured values.
A closure is the functional answer to "an object with one method and some stored data."

`multiply()` reads `factor` rather than receiving it, yet stays pure.
`factor` stays the same after capture,
so the same argument always produces the same answer.
`withdraw()` also reads a name from outside, but each call changes that name,
the global `balance`, so each result depends on every call before it.

A closure fits when you want to configure behavior once, reuse it,
and keep its configuration private.
Once the enclosing function returns,
the inner function's scope is the one place the captured variable has a name,
so the inner function alone can read or rebind it by name.
That privacy gives you encapsulation without declaring a class:

```python
# make_counter.py
from collections.abc import Callable

def make_counter() -> Callable[[], int]:
    count = 0
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment

tally = make_counter()
print(tally(), tally(), tally())
#: 1 2 3
fresh = make_counter()
print(fresh())
#: 1
```

Each call to `make_counter()` builds an independent counter with its own `count`.

`increment()` is impure on purpose, to contrast with `withdraw()`.
`withdraw()` mutates a module-level name that any code can assign.
`increment()` mutates a name that it alone can assign.
When state must exist,
a closure is one way to let exactly one function change it.

A closure's privacy is stronger than the privacy of a leading underscore,
and weaker than a guarantee.
Any code can write `obj._field`.
The name `count` exists inside `make_counter()` alone,
because the compiler resolves `count` in that scope.
Introspection reaches the variable through the function object.
`inspect.getclosurevars(tally).nonlocals` reports `{'count': 3}`,
and `tally.__closure__[0].cell_contents = 100` rewrites `count`.

The `nonlocal` statement lets `increment()` assign to the captured variable.
Reading a captured name, as `multiply()` reads `factor`, needs no declaration.
But any assignment to a name inside a function makes that name local.
Without a declaration,
`count += 1` therefore makes `count` a new local variable,
reads that local before anything has assigned it,
and fails with `UnboundLocalError`.
`nonlocal count` redirects the assignment to the enclosing function's variable.
[`global`](05_Foundations--Functions.md#names-inside-a-function)
does the same for a module-level name.
Each statement targets its own scope.
With `global count` in place of `nonlocal count`,
`increment()` looks for a module-level `count`, finds none,
and raises a `NameError`.

Forgetting the declaration is the usual mistake when a closure first assigns to a captured name.
The runtime message names a local variable instead of the missing declaration:
"cannot access local variable 'count' where it is not associated with a value."
The type checker finds the same mistake before the program runs.
If you delete the `nonlocal` line,
`ty` reports `Name 'count' used when not defined` on the `count += 1` line.

## Partial Application

*Partial application* presets some of a function's arguments and produces a new function that expects the rest.
`functools.partial()` builds that new function from the original function and the preset arguments:

```python
# partial.py
from functools import partial

def power(base: int, exponent: int) -> int:
    return base ** exponent

# Bind the exponent to build new single-argument functions:
square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5), cube(5))
#: 25 125
print(square.func.__name__, square.keywords)
#: power {'exponent': 2}
```

Without the keyword, `partial(power, 2)` presets `base`,
because positional arguments fill from the left.
Called with 5, that partial computes `2 ** 5`.

Partial application turns a general function into the specific one a caller needs.
[`multiplier()`](#closures) does the same with a closure.
It is a factory that presets one argument and returns a function expecting the rest.
When the general function exists, as `power()` does here,
`partial()` removes the factory.

Use partial application when an API expects a function of one argument and you have a function of several.
Unlike a lambda, `partial()` keeps the preset arguments as data you can inspect,
through its `.func`, `.args`, and `.keywords` attributes.
It also stores their values when you build it,
whereas a lambda created in a loop reads each captured name at call time,
the [late-binding trap](27_Patterns--Function_Objects.md#the-late-binding-trap).

### Leaving a Gap with `Placeholder` {#leaving-a-gap-with-placeholder}

Binding `exponent` in `partial.py` works because `power()` accepts it by keyword.
For a function whose parameters are [positional-only](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters),
position is the only way to bind an argument.
Because `partial()` fills positional arguments from the left,
presetting the third argument before 3.14 meant presetting the first two as well.
`functools.Placeholder` (Python 3.14 and later)
is a marker that reserves a position for the caller:

```python
# placeholder.py
from collections.abc import Callable
from functools import Placeholder, partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

percent: Callable[[int], int]
percent = partial(clamp, 0, Placeholder, 100)  # type: ignore
print(percent(150), percent(-5), percent(42))
#: 100 0 42
```

Before 3.14, a hand-written wrapper supplied `percent`.

Calling `percent()` with no argument raises a `TypeError`.
The library also rejects a trailing placeholder as redundant.
`partial()` already appends the call's arguments after the preset ones,
so `partial(clamp, 0, Placeholder)` means the same as `partial(clamp, 0)`.

The `# type: ignore` comment marks a type checker limitation rather than a code problem.
The stub for `partial()` does not yet describe what `Placeholder` does at runtime,
so `ty` checks the three arguments in `partial(clamp, 0, Placeholder, 100)` against `clamp()`'s declared parameter types.
`ty` therefore reports `Placeholder` as a value of the wrong type.
It also types the resulting callable as one that takes no arguments,
and refuses to assign that callable to the declared `Callable[[int], int]`.
Both reports fall on the assignment line, so one comment covers them.
At runtime `percent()` clamps each argument, as the `#:` line shows.

The declaration on its own line states the type of `percent`.
`ty` takes the type of `percent` from that declaration and checks the three calls against it.
A call to `percent()` with no argument draws a `missing-argument` report,
so `ty` catches the `TypeError` case before the program runs.

## Composing Functions

*Function composition* builds a new function that passes one function's result to the next as its argument.
Composition assembles behavior from small pieces, one stage at a time:

```python
# compose_functions.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    # A function that runs g, then feeds its result to f:
    def composed(x: T) -> V:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2
def label(n: int) -> str:
    return f"<{n}>"

increment_then_double = compose(double, increment)
print(increment_then_double(10))
#: 22
print(compose(label, increment_then_double)(10))  # [1]
#: <22>
```

Each piece stays small and pure.
`compose()` combines them without changing either one.

The type parameters matter at `[1]`.
The type checker verifies that `label()` accepts what `increment_then_double` produces,
and types the composed function `(int) -> str` rather than `(int) -> int`.

You grow a composition by adding a stage.
Each stage is testable on its own.
A larger behavior is a new named composition of existing stages.
When a requirement changes, you insert or swap a single stage.
The other stages stay as they were.

The standard library supplies [whole modules](41_Functional--Toolkits.md)
of these small, composable pieces.

## Putting the Pieces Together

A report on temperature readings combines several of the chapter's constructs in one program:

```python
# pipeline.py
from collections.abc import Sequence
from functools import partial
from record import record

@record
class Reading:
    sensor: str
    celsius: float

def warmer_than(limit: float, r: Reading) -> bool:
    return r.celsius > limit

def to_fahrenheit(r: Reading) -> Reading:
    return Reading(r.sensor, r.celsius * 9 / 5 + 32)

def report(readings: Sequence[Reading]) -> list[str]:
    warm = filter(partial(warmer_than, 20.0), readings)
    return [f"{r.sensor} {r.celsius:.1f}"
            for r in map(to_fahrenheit, warm)]

data = [Reading("a", 18.0), Reading("b", 25.0),
        Reading("c", 30.5)]
print(report(data))
#: ['b 77.0', 'c 86.9']
print(data[1])  # [1]
#: Reading(sensor='b', celsius=25.0)
```

Five of the chapter's ideas work at once: a record for the value,
`Sequence` to state that `report()` leaves its input unchanged,
three pure functions,
`partial()` to turn a two-argument predicate into the one-argument callable `filter()` requires,
and `map()` and `filter()` for the traversal.

The `print()` at `[1]` shows that the pipeline leaves `data` as it was.
Because the input list stays as built, you can recompute the whole report,
cache it, or run it on another core with no coordination.

`to_fahrenheit()` returns a `Reading` whose `celsius` field holds a Fahrenheit number.
`warmer_than()` reads the field as Celsius, so `report()` converts last,
after the filter.

`pipeline.py` is ordinary Python,
written so that each piece depends on its arguments alone.
The chapters ahead build on that property.

## Exercises

Try each exercise before opening its [solution](../Solutions/40_Functional--Foundations/).

1.  In `pure_functions.py`, write a third function, `deposit(amount)`,
    that behaves like `withdraw()` but adds to `balance` instead of subtracting.
    Explain, the way the text does for `withdraw()`, why `deposit()` is impure.
2.  In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
    with no change to how you call `operations["*"](6, 4)`.
3.  In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of `double` and `triple`,
    each holding its own `factor`.
4.  In `compose_functions.py`, write a third small function, `square(n)`,
    and build `increment_then_double_then_square = compose(square, increment_then_double)`.
    Predict `increment_then_double_then_square(3)` before running it.
5.  In `placeholder.py`, build a second partial, `at_least_ten`,
    that presets `low` to 10 and leaves both other arguments to the caller.
    Then try, with `partial()` and no `Placeholder`,
    to preset `high` and leave `low` and `value` open,
    and explain why that is impossible.
6.  In `immutable_types.py`,
    add `CONFIG: Final[list[int]] = [1, 2]` and a line that appends to it.
    Run `ty`, which accepts the append.
    Then add `MAX_SIZE = 200`, run `ty` again,
    and explain why the rebinding is an error while the append is not.
    Then change the annotation so `ty` rejects the append.
7.  In `higher_order.py`,
    replace the `map()` and `filter()` calls with comprehensions,
    and the `sorted(key=len)` call with one that sorts by last letter.
    Then start again from the original file,
    delete the `list()` around the `map()` call, print the result,
    and say what you see and why.
8.  In `make_counter.py`, give `make_counter()` a `step: int = 1` parameter,
    so `make_counter(10)` builds a counter that counts 10, 20, 30.
    `increment()` reads `step` without declaring it `nonlocal`.
    Explain why `count` needs the declaration and `step` does not.
    Then delete the `nonlocal` line and compare the type checker's report with the runtime failure.
9.  In `pipeline.py`, add `colder_than(limit, r)` beside `warmer_than()`,
    and give `report()` a second `filter()` stage built with `partial()`,
    so only readings between 20.0 and 30.0 Celsius reach the output.
    Then write a second version of `report()` that calls `map(to_fahrenheit, ...)` ahead of both filters,
    and explain the list it returns.
