# Foundations

Some code you can check by reading it, and the rest you must run to find out.
Functional programming grows the first kind at the expense of the second.

This chapter begins the book's exploration of functional programming.
The ideas are useful before you learn their names.
A pure function cannot corrupt state you forgot about.
A bug in a pure function reproduces from the arguments alone,
and the function needs no mock or fixture to test.
A cache from `functools`, or a sliding window from `itertools`,
is code the library wrote for you,
already correct on the edge case you would otherwise miss.
A function that shares no state is already safe to run in parallel.
And you can reason about code built from small,
checkable pieces by substitution, the same way you check a line of algebra.
The functional style lets you keep loops, classes, and mutation.
It asks you to notice when a piece of code can depend on its arguments alone,
and then write it that way.

This chapter builds the foundations: pure functions, immutable values,
and the ways Python lets you pass, capture, specialize, and combine functions.
[Toolkits](41_Functional--Toolkits.md) tours the standard library's support,
[Error Handling](42_Functional--Error_Handling.md)
turns failure into an ordinary value,
and [Confidence](43_Functional--Confidence.md)
examines what the discipline lets you claim about your code.
Those four chapters are Part IV.
Part V then applies the same discipline to a function's effects.
[Effect Management](44_Effects--Effect_Management.md)
tracks a function's effects in its type,
and [Generators](45_Effects--Generators.md)
supplies the mechanism Python already has for describing a computation without running it.
[Stateless](46_Effects--Stateless.md)
and [Stateless in Practice](47_Effects--Stateless_in_Practice.md)
then build a checked Effect system on that mechanism.

## Pure Functions

A *pure function* computes its result from its arguments alone.
It reads nothing that can change, and it changes nothing outside itself.
Given the same arguments, it always produces the same outcome,
whether that outcome is a returned value or a raised exception.
A *side effect* is anything a function does beyond producing that outcome,
such as printing, reading or writing a file or the network,
or mutating something outside the function.
A pure function has none.

Purity is the foundation on which everything else in these chapters builds.
You can reason about a pure function the way you reason about an equation:

```python
# pure_functions.py
# Pure: the result depends only on the arguments:
def double(x: int) -> int:
    return x * 2

# Impure: it depends on and mutates outside state:
balance = 100
def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(double(5), double(5))
#: 10 10
print(withdraw(30), withdraw(30))
#: 70 40
```

`double()` returns the same answer every time.
`withdraw()` does not,
because each call changes `balance` and the next call reads the new value.
To understand one `withdraw()` call you must trace every call before it.

A pure function is the most reliable code you can write,
because its inputs fully describe its behavior.
You can call it from many threads at once,
because it shares no state to corrupt.
[Automatic Parallelism](43_Functional--Confidence.md#automatic-parallelism)
turns that safety into speed.
A cache can store the function's results,
because the same arguments always produce the same answer.
That makes [`functools.cache`](41_Functional--Toolkits.md#cache)
safe on a pure function, and wrong on an impure one.
And you test a pure function with a single assertion and no fixture,
since it holds no state to set up or restore:

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
total = 0
assert running_total(5) == 5
print("ok")
#: ok
```

If you delete the second `total = 0`, the second assertion fails.
That line is the fixture the impure version needs, and purity removes it.
`slope()` appears again later in the book:
[Are Exceptions Impure?](44_Effects--Effect_Management.md#are-exceptions-impure)
asks whether raising an exception breaks its purity.

## Immutability

An *immutable* value cannot change after creation.
Tuples, strings, `frozenset`, and frozen dataclasses are immutable.
Each freezes only its own top level:
the tuple `([1], 2)` always holds that same list,
and anyone can still append to the list.
A value that never changes stays what you last read,
whatever code ran in between,
and that guarantee is why removing shared mutable state is the practical core of the functional style.

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
print(moved)
#: Point(x=11, y=2)
```

The type checker rejects the direct form `p.x = 5` before the program runs.
To show that the runtime rejects the assignment too,
the listing writes it as `setattr(p, "x", 5)`, which the type checker accepts.
The original `p` stays untouched, and `moved` is a separate value.
When a value never changes after creation,
two parts of a program can share one without coordinating,
and concurrent code needs no lock to read it.

That safety has a cost, and the cost is copying.
Python's immutable types share no structure.
`moved = Point(p.x + 10, p.y)` above builds a new `Point`,
and changing one field of a large tuple or frozen dataclass means rebuilding the whole value,
not patching one slot in place.
Copying a two-field `Point` takes so little time that you can ignore it.
A large structure that changes often copies the whole value on every change.
That time and memory are the price of sharing without coordination.
Languages built around immutability answer this with *persistent* data structures,
which share every part a change leaves alone;
Python's standard library has none,
so a large value that changes often is the one place a mutable structure,
kept private to one function, is still the right choice.

### Immutability in Annotations

Type annotations can state immutability so a type checker enforces it.
`typing.Final` marks a name bound once, at its declaration.
The read-only collection types in `collections.abc`,
such as `Sequence` and `Mapping`, describe a value you only read.
They have no `append()` or item assignment,
so a type checker rejects any attempt to mutate through them:

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

The annotation is a constraint the type checker enforces,
even when the caller passes a mutable `list`.
The type checker rejects `MAX_SIZE = 200` written later in the module,
and rejects `values.append(4)` inside `total()`.
The constraint covers only `total()`'s side.
`Sequence[int]` declares that `total()` only reads its argument.
The caller keeps its `list` and can append to it at any time,
including from another thread while `total()` is running.
`Final` freezes the binding, and only the binding:
if you declare `CONFIG: Final[list[int]] = [...]`,
`CONFIG.append(...)` still succeeds, for the type checker and at runtime alike.
Freezing only the binding is the shallow-freezing lesson of [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
again, with `Final` in place of `frozen=True`.
For an immutable value, make the value's own type immutable,
`Final[tuple[int, ...]]`: the tuple guards the contents,
and `Final` guards the binding.

### A Stable Hash and Safe Sharing

Immutability offers two things a mutable value cannot.
The first is a *stable hash* of the contents,
one that holds for the value's whole life,
so the value can be a dictionary key or a set member.
The second is sharing without a defensive copy,
because no recipient can change the value you still hold.
A `list` offers neither:

```python
# hashable.py
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# A list has no stable hash, so it cannot be a key:
with expected(TypeError):
    hash([3, 4])
#: [TypeError] unhashable type: 'list'
```

What costs a type its hash is contents-based equality, not mutability by itself.
A plain class instance is mutable and still hashes, by identity,
so it works as a dictionary key.
A `list` and an unfrozen `@dataclass` both compare by contents,
so a dictionary that stored one as a key could not find it again once its contents changed.
Python therefore sets their `__hash__` to `None`.
Freezing a dataclass lets it keep contents-based equality and a hash at the same time.
[`@record`](18_Techniques--Performance.md#record) freezes `Point`,
so `Point(3, 4)` can key `distances`.
Contents-based equality together with a stable hash is why a dictionary key,
a cache entry, or a value shared across threads is normally a tuple or a record.

## Functions as First-Class Objects

A function in Python is an object like any other,
which is what *first-class* means.
You can bind a function to a name, store it in a container,
pass it as an argument, and return it from another function.
A function value is data you can store and pass.

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

The dictionary holds functions as values,
so a lookup yields a function you can immediately call.
The [Function Objects](28_Patterns--Function_Objects.md)
chapter treats the same capability as a design pattern.

Treating functions as values lets data drive control flow.
A dictionary of functions replaces a long `if`/`elif` chain,
because you select the behavior by looking it up:

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
print(operations["+"](6, 4), operations["-"](6, 4),
      operations["//"](6, 4), operations["%"](6, 4))
#: 10 2 1 2
# A missing key is a plain KeyError, no else branch:
with expected(KeyError):
    operations["^"](6, 4)
#: [KeyError] '^'
```

Supporting a new operator means adding a row to the table,
whether the literal holds that row or a later line adds it,
as the `operations["%"]` line does here.
The dispatch code itself never changes.
A lookup of a missing key raises a plain `KeyError`,
the case an `if`/`elif` chain handles with a trailing `else`.
The same structure underlies [the dictionary factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary)
and the plugin registries that let a program grow without editing its core.

[Pattern Matching](13_Techniques--Pattern_Matching.md)
solves the same `if`/`elif` problem with `match`,
and `match` and the table differ in one way that decides between them.
A `match` is code: adding an operator means editing the function,
and the type checker verifies every case.
The table is data: adding an operator means adding a row,
which another module can do at import time and a test can do at runtime.
Choose `match` when you know the whole set of cases as you write the function,
and a table when the set should grow from outside.

## Higher-Order Functions

A *lambda* is an unnamed function written as a single expression,
introduced in [Functions](05_Foundations--Functions.md#lambdas).
The functions in this section take lambdas as inline arguments,
where a lambda fits best.
A lambda's value is locality.
When a transformation is one short expression,
a lambda keeps it at the call site, where the reader already is,
instead of defining it as a named function elsewhere.
`sorted(words, key=lambda w: w.lower())` states the sort order right where the code sorts.
Naming that one-liner adds a line, a name to invent,
and a definition to look up, and changes nothing about the sort.
For anything larger, write a `def`.
A named function carries a docstring, a readable name in tracebacks,
and room for more than one expression.

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

Each call passes a function to another function, which does the looping.
Returning a function is the other half of the definition.
[Closures](#closures) covers it below.

The `list()` calls do real work.
`map()` and `filter()` return [one-shot iterators](23_Patterns--Iterators.md#generators).
`print(map(...))` therefore shows `<map object at 0x...>` instead of values,
and a second pass over the same object silently produces nothing.
`sorted()` is the exception:
it must read every element before it can order any of them,
so it always returns a list.
It is also the pure counterpart of `list.sort()`,
which [Containers](03_Foundations--Containers.md)
shows reordering the list in place and returning `None`.
`sorted()` builds a new list and leaves its input as it was.

The lambdas above exist to show the machinery.
For these cases Python offers a lookalike you should usually prefer,
the [comprehension](16_Techniques--Comprehensions.md).
`[n * n for n in numbers]` says more directly what `map()` plus a fresh lambda says,
and `[n for n in numbers if n % 2 == 0]` replaces the `filter()` call the same way.
`map()` and `filter()` are the better choice when the function already exists.
`map(str.strip, lines)` reads better than `[line.strip() for line in lines]`,
because `str.strip` names the operation once, with no loop variable to invent.

Beyond how they read, a comprehension and `map()` return different things.
The comprehension builds a finished list.
`map()` returns an iterator you can pass to the next stage without building the list.
A [generator expression](16_Techniques--Comprehensions.md#generator-expressions)
is the comprehension's lazy form, and removes that difference.
The rule of thumb is to use the higher-order form when the function already exists,
and the comprehension when you would write the expression inline.
`sorted()`'s `key` has no comprehension equivalent,
so it is a higher-order argument either way.

Higher-order functions separate the iteration from the operation.
`map()`, `filter()`,
and `sorted()` each contain the loop that iterates over the data, written once,
and you supply only the part that differs from one use to the next.
You stop rewriting the same loop,
and with it the off-by-one and accumulator-initialization mistakes a hand-written loop allows.

A higher-order function can also return a function:
it wraps the one it receives with operations like timing, retries, or logging,
and returns the wrapper.
A decorator does that wrapping, as [Decorators](14_Techniques--Decorators.md)
shows.

## Closures

When an inner function refers to a variable from the function that created it,
Python keeps that variable alive.
The inner function plus the captured variables is a *closure*,
and a closure lets a function carry state without a class:

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

`multiplier()` returns `multiply()`,
and each returned function holds its own `factor`.
The last two lines show the captured values directly:
`double` and `triple` are the same code holding different captured values.
A closure is the functional answer to "an object with one method and some stored data."

`multiply()` reads `factor` rather than receiving it, yet it stays pure.
`factor` never changes after capture,
so the same argument always produces the same answer.
`withdraw()` is unpredictable because every call changes the global `balance`;
nothing changes `factor` after capture.

A closure fits when you want to configure behavior once, reuse it,
and keep its configuration private.
Once the factory returns,
the inner function's scope is the one place the captured variable has a name,
so the inner function alone can read or rebind it.
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
```

Each call to `make_counter()` builds an independent counter with its own `count`.

`increment()` is impure on purpose, to contrast with `withdraw()`.
`withdraw()` mutates a module-level name that any code can assign.
`increment()` mutates a name that only it can assign.
When state must exist,
a closure is one way to let exactly one function change it.

The privacy is Python's usual kind, a convention.
`inspect.getclosurevars(tally).nonlocals` reports `{'count': 3}`,
and `tally.__closure__[0].cell_contents = 100` rewrites `count`.
Like the single leading underscore,
a closure states an intention that the language does not enforce.

The `nonlocal` statement lets `increment()` assign to the captured variable.
Reading a captured name, as `multiply()` reads `factor`, needs no declaration.
But any assignment to a name inside a function makes that name local,
so without a declaration, `count += 1` makes `count` a fresh local variable,
reads that local before anything has assigned it,
and fails with `UnboundLocalError`.
`nonlocal count` redirects the assignment to the enclosing function's variable.

Forgetting the declaration is the usual mistake when a closure first assigns to a captured name.
The runtime message,
"cannot access local variable 'count' where it is not associated with a value,"
names a local variable instead of the missing declaration.
The type checker's report is the more useful one.
If you delete the `nonlocal` line,
`ty` reports `Name 'count' used when not defined` on the `count += 1` line.

## Partial Application

*Partial application* fixes some of a function's arguments and produces a new function that expects the rest.
`functools.partial()` builds that new function from the old one and the fixed arguments:

```python
# partial.py
from functools import partial

def power(base: int, exponent: int) -> int:
    return base ** exponent

# Fix the exponent to build new single-argument functions:
square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5), cube(5))
#: 25 125
print(square.func.__name__, square.keywords)
#: power {'exponent': 2}
```

`square` and `cube` are specializations of `power`,
each with one argument already supplied.
The keyword does real work here.
`partial(power, 2)` binds `base` instead,
because positional arguments fill from the left.
`square(5)` would then compute `2 ** 5`.

Partial application turns a general function into the specific one a caller needs.
`multiplier()` in [Closures](#closures) does the same by hand,
a factory that fixes one argument and returns a function expecting the rest.
When the general function exists, as `power()` does here,
`partial()` removes the factory.

Use partial application when an API expects a function of one argument and you have a function of several.
Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect,
through its `.func`, `.args`, and `.keywords` attributes.
It also binds their values when you build it,
whereas a lambda created in a loop reads each captured name at call time.
`late_binding.py` in [Function Objects](28_Patterns--Function_Objects.md#the-late-binding-trap)
demonstrates that late-binding trap.

### Leaving a Gap with `Placeholder` {#leaving-a-gap-with-placeholder}

Binding `exponent` in `partial.py` works because `power()` accepts it by keyword.
For a function whose parameters are [positional-only](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters),
position is the only way to bind an argument,
and `partial()` fills positional arguments from the left, so before 3.14,
fixing the third argument meant fixing the first two as well.
`functools.Placeholder` (Python 3.14 and later)
is a marker that reserves a position for the caller.
The listing below carries two `# type: ignore` comments,
which the paragraph after it explains:

```python
# placeholder.py
from functools import Placeholder, partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

percent = partial(clamp, 0, Placeholder, 100)  # type: ignore
print(percent(150), percent(-5), percent(42))  # type: ignore
#: 100 0 42
print(percent.args)
#: (0, Placeholder, 100)
```

`percent` fixes the bounds and leaves the middle argument open.
Before 3.14, a hand-written wrapper supplied that specialization.
A `Placeholder` reserves the position and leaves the value to the caller:
calling `percent()` with no argument raises a `TypeError`.
The library also rejects a *trailing* placeholder, because it would do nothing.
`partial()` already appends the call's arguments after the bound ones,
so `partial(clamp, 0, Placeholder)` would mean the same as `partial(clamp, 0)`.

The `# type: ignore` comments mark a type checker limitation rather than a code problem.
The stub for `partial()` does not yet describe what `Placeholder` does at runtime,
so `ty` checks the three arguments in `partial(clamp, 0, Placeholder, 100)` against `clamp`'s declared parameter types.
`ty` therefore reports `Placeholder` as a value of the wrong type,
and types the resulting callable as one that takes no arguments.
The runtime behaves correctly.

## Composing Functions

*Function composition* builds a new function that passes one function's result straight to the next.
You can assemble behavior from small pieces, one stage at a time:

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
print(compose(label, increment_then_double)(10))
#: <22>
```

`compose(double, increment)` returns a function that increments first,
then doubles.
Each piece stays small and pure,
and you combine them without changing either one.
The type parameters matter on the second `print()`.
The type checker verifies that `label` accepts what `increment_then_double` produces,
and types the composed function `(int) -> str` rather than `(int) -> int`.

You grow a composition by adding a stage, and each stage is testable on its own.
A larger behavior is a new named composition of existing stages.
When a requirement changes,
you insert or swap a single stage and the others stay as they were.

The standard library supplies whole modules of these small, composable pieces.
[Toolkits](41_Functional--Toolkits.md) tours them.

## Putting the Pieces Together

Every section above shows one construct on its own.
Here they work together:

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
print(data[0])
#: Reading(sensor='a', celsius=18.0)
```

Five of the chapter's ideas work at once: a record for the value,
`Sequence` to state that `report()` only reads, two pure functions,
`partial()` to turn a two-argument predicate into the one-argument callable `filter()` requires,
and `map()` and `filter()` for the traversal.
The second `print()` shows what the discipline gives you.
The input list stays unchanged, so you can recompute the whole report, cache it,
or run it on another core with no coordination.

All of it is ordinary Python,
written so that each piece depends on its arguments alone.
The chapters ahead build on that single property.

## Exercises

1.  In `pure_functions.py`, write a third function, `deposit(amount)`,
    that behaves like `withdraw()` but adds to `balance` instead of subtracting.
    Explain, the way the text does for `withdraw()`, why `deposit()` is impure.
2.  In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
    with no change to how `operations["*"](6, 4)` gets called.
3.  In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of `double` and `triple`,
    each holding its own `factor`.
4.  In `compose_functions.py`, write a third small function, `square(n)`,
    and build `increment_then_double_then_square = compose(square, increment_then_double)`.
    Predict `increment_then_double_then_square(3)` before running it.
5.  In `placeholder.py`, build a second partial, `at_least_ten`,
    that fixes only `low` to 10 and leaves both other arguments to the caller.
    Then try to fix only `high` without a `Placeholder` and explain why that is impossible.
6.  In `immutable_types.py`,
    add `CONFIG: Final[list[int]] = [1, 2]` and a line that appends to it.
    Run `ty`, which reports nothing.
    Then add `MAX_SIZE = 200`, run `ty` again,
    and explain why the rebinding is an error while the append is not.
    Then change the annotation so appending *is* rejected.
7.  In `higher_order.py`,
    replace the `map()` and `filter()` calls with comprehensions,
    and the `sorted(key=len)` call with one that sorts by last letter.
    Then start again from the original file,
    delete the `list()` around the `map()` call, print the result,
    and say what you see and why.
8.  In `make_counter.py`, give `make_counter()` a `step: int = 1` parameter,
    so `make_counter(10)` builds a counter that counts 10, 20, 30.
    `increment()` reads `step` without declaring it `nonlocal`:
    explain why `count` needs the declaration and `step` does not.
    Then delete the `nonlocal` line and compare `ty`'s report with the runtime failure.
9.  In `pipeline.py`, add `colder_than(limit, r)` beside `warmer_than()`,
    and give `report()` a second `filter()` stage built with `partial()`,
    so only readings between 20.0 and 30.0 Celsius reach the output.
    Then write a second version of `report()` that calls `map(to_fahrenheit, ...)` ahead of both filters,
    and explain the list it returns.
