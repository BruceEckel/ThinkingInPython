# Foundations

This chapter begins the book's exploration of functional programming.
The ideas pay off before the vocabulary arrives.
A pure function cannot corrupt state you forgot about.
It has fewer bugs to chase, and it needs no mock or fixture to test.
A cache from `functools`, or a sliding window from `itertools`,
is code you never write yourself,
already correct on the edge case you would otherwise miss.
A function with no shared state needs no lock,
so it parallelizes with no new code.
And code built from small,
checkable pieces is code you can reason about by substitution,
the same way you check a line of algebra.
None of this asks you to abandon loops, classes, or mutation.
It asks you to notice when a piece of code can depend on its arguments alone,
and to write it that way when it can.

This chapter builds the foundations: pure functions, immutable values,
and the ways Python lets you pass, capture, specialize, and combine functions.
[Toolkits](41_Functional_Toolkits.md) tours the standard library's support,
[Error Handling](42_Functional_Error_Handling.md)
turns failure into an ordinary value,
and [Assurance](43_Functional_Assurance.md)
examines what the discipline lets you claim about your code.
Those four chapters are Part IV.
Part V then takes the same discipline further.
[Effect Management](44_Effect_Management.md)
tracks a function's effects in its type, and [Generators](45_Generators.md)
supplies the mechanism Python already has for describing a computation without running it.
[Stateless](46_Stateless.md)
and [Stateless in Practice](47_Stateless_in_Practice.md)
then build a checked Effect system on that mechanism.

## Pure Functions

A *pure function* computes its result from its arguments alone.
It reads nothing else and changes nothing else.
Given the same arguments, it always produces the same outcome,
whether that outcome is a returned value or a raised exception.
It has no *side effects*: no printing, no file or network access,
no mutation of anything outside the function.

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
because each call changes `balance` and the next call sees the new value.
You cannot understand a single `withdraw()` call without tracking the history of every call before it.

The payoff is trust.
A pure function is the most reliable code you can write,
because its behavior is fully described by its inputs.
You can call it from many threads at once,
because it shares no state to corrupt.
[Automatic Parallelism](43_Functional_Assurance.md#automatic-parallelism)
turns that safety into speed.
A cache can store its results, knowing the answer will never go stale.
That makes [`functools.cache`](41_Functional_Toolkits.md#cache)
safe on a pure function, and wrong on an impure one.
And you test it with a single assertion and no fixture,
since there is nothing to set up or restore:

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

If you delete either `total = 0`, the second assertion fails.
That line is the whole fixture, and purity removes it.
`slope()` appears again later in the book:
[Are Exceptions Impure?](44_Effect_Management.md#are-exceptions-impure)
asks of this same function whether raising an exception breaks its purity.

## Immutability

An *immutable* value cannot change after creation.
Tuples, strings, `frozenset`, and frozen dataclasses are immutable.
Each is immutable in itself, and no deeper:
the tuple `([1], 2)` will always hold that same list,
which anyone can still append to.
Removing shared mutable state is the practical core of the functional style.
A value that never changes cannot develop a bug from some forgotten change elsewhere.

Instead of modifying an object, you build a new one from the old:

```python
# immutability.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
with ignore(AttributeError):
    setattr(p, "x", 5)  # A frozen instance rejects assignment
#: FrozenInstanceError("cannot assign to field 'x'")
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
```

The demonstration writes the assignment as `setattr(p, "x", 5)` because the direct form `p.x = 5` never gets to run:
the type checker rejects it statically, as it should.
`setattr()` slips past the static check so the listing can show the runtime rejection too.
The original `p` stays untouched, and `moved` is a separate value.
When values never change underneath you,
two parts of a program can share one without coordinating,
and concurrent code needs no lock to read it.

Type annotations can state immutability so a checker enforces it.
`typing.Final` marks a name that must not be rebound.
The read-only collection types in `collections.abc`,
such as `Sequence` and `Mapping`, describe a value you only read.
They have no `append()` or item assignment,
so a checker rejects any attempt to mutate through them:

```python
# immutable_types.py
from collections.abc import Sequence
from typing import Final

# Final marks a name the checker won't let you rebind:
MAX_SIZE: Final[int] = 100

# Sequence is read-only: no append, no item assignment:
def total(values: Sequence[int]) -> int:
    return sum(values)

print(MAX_SIZE, total([1, 2, 3]))
#: 100 6
```

The annotation is a constraint the checker enforces,
even when the value passed in is a mutable `list`.
Writing `MAX_SIZE = 200` later, or `values.append(4)` inside `total()`,
is a type error caught before the program runs.
The constraint runs one way only.
`Sequence[int]` states that `total()` will not mutate its argument.
It says nothing about the caller,
who still holds the `list` and can append to it whenever it likes,
including from another thread while `total()` is running.
Mind what `Final` does and does not freeze.
It locks the binding, not the object:
if you declare `CONFIG: Final[list[int]] = [...]`,
`CONFIG.append(...)` still succeeds, for the checker and at runtime alike.
This is the shallow-freezing lesson of [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)
in another costume.
For an immutable value, make the value's own type immutable,
`Final[tuple[int, ...]]`, and let `Final` guard only the name.

Immutability also makes two things possible that a mutable value cannot offer.
The first is a *stable hash*, one that holds for the value's whole life,
so the value can serve as a dictionary key or a set member.
The second is sharing without a defensive copy,
because no recipient can change the value out from under you.
A `list` offers neither:

```python
# hashable.py
from dataclasses import dataclass
from exceptions import ignore

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# A list has no stable hash, so it cannot be a key:
with ignore(TypeError):
    hash([3, 4])
#: TypeError("unhashable type: 'list'")
```

Mutability alone is not what removes hashing.
A plain class instance is mutable and still hashes, by identity,
so it works as a dictionary key.
What removes hashing is equality based on *contents*.
A `list` and an unfrozen `@dataclass` both compare that way,
so Python sets their `__hash__` to `None`:
the dictionary that stored a key could no longer find it once its contents changed.
`frozen=True` lets a dataclass keep contents-based equality and a hash at the same time.
That combination is why a value that must be a dictionary key, a cache entry,
or a shared read across threads is normally a tuple or a frozen dataclass.

## Functions as First-Class Objects

A function in Python is an object like any other.
This is what *first-class* means.
You can bind a function to a name, store it in a container,
pass it as an argument, and return it from another function.
A function value is data you can move around.

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
The [Function Objects](28_Function_Objects.md)
chapter approaches the same capability from the pattern side.

Treating functions as values lets data drive control flow.
A dictionary of functions replaces a long `if`/`elif` chain,
because you select the behavior by looking it up:

```python
# dispatch.py
from collections.abc import Callable

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b

# A table of functions replaces a long if/elif chain:
operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
}
print(operations["+"](6, 4), operations["-"](6, 4))
#: 10 2
```

Supporting a new operator means adding a row to the table.
The dispatch code never changes.
The same structure is behind [the dictionary factory](27_Factory.md#the-pythonic-factory-a-dictionary)
and the plugin registries that let a program grow without editing its core.

[Pattern Matching](13_Pattern_Matching.md)
solves the same `if`/`elif` problem with `match`,
and the two are not interchangeable.
A `match` is code: adding an operator means editing the function,
and the checker sees every case.
The table is data: adding an operator means adding a row,
which another module can do at import time and a test can do at runtime.
Choose `match` when the set of cases stays fixed and known to the compiler,
and a table when the set should grow from outside.

## Lambdas

A *lambda* is an unnamed function written as a single expression,
introduced in [Functions](05_Functions.md#lambdas).
The higher-order functions below take them as inline arguments,
which is where they fit best.
Their value is locality.
When a transformation is one short expression,
a lambda keeps it at the call site, where the reader already is,
instead of sending them to a named function defined elsewhere.
`sorted(words, key=lambda w: w.lower())` states the sort order right where the sort happens.
Naming that one-liner costs a line, a name to invent,
and a definition to look up, with nothing gained in clarity.
For anything larger, write a `def`.
A named function carries a docstring, a readable name in tracebacks,
and room to grow.

## Higher-Order Functions

A *higher-order function* takes a function as an argument, returns one, or both.
Three built-ins are the workhorses.
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

Each call hands a function to another function and lets it do the looping.
Returning a function is the other half of the definition,
covered under [Closures](#closures), below.

The `list()` calls are not decoration.
`map()` and `filter()` return one-shot iterators,
so `print(map(...))` shows `<map object at 0x...>` instead of values,
and a second pass over the same object produces nothing at all,
with no error to point at ([Generators](23_Iterators.md#generators)).
`sorted()` is the exception:
it has to see every element before it can order any of them,
so it always returns a list.

The lambdas above exist to show the machinery,
and for these cases Python offers a lookalike you should usually prefer:
the comprehension ([Comprehensions](16_Comprehensions.md)).
`[n * n for n in numbers]` says what `map()` plus a fresh lambda says,
more directly, and `[n for n in numbers if n % 2 == 0]` replaces the `filter()` call the same way.
`map()` and `filter()` earn their keep when the function already exists:
`map(str.strip, lines)` beats `[line.strip() for line in lines]` because the name is the whole story.
The two are not quite the same object, either.
The comprehension hands you a finished list;
`map()` hands you an iterator you can feed into the next stage without building the list at all.
The rule of thumb: existing function, use the higher-order form;
expression you are writing on the spot, use the comprehension.
`sorted()`'s `key` has no comprehension equivalent,
so it is a higher-order argument either way.

Higher-order functions separate the walking from the work.
`map()`, `filter()`, and `sorted()` each contain the loop that walks the data,
written once, and you supply only the part that differs from one use to the next.
You stop rewriting the same iteration scaffold,
along with the off-by-one and accumulator-initialization mistakes that scaffold invites.
The idea runs the other direction, too.
A function that takes a function can wrap it with operations like timing,
retries, or logging.
This is what a decorator does in [Decorators](14_Decorators.md).

## Closures

When an inner function refers to a variable from the function that created it,
Python keeps that variable alive.
The inner function plus the captured variables is a *closure*.
This way, a function can carry state without a class:

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
and each returned function remembers its own `factor`.
The last two lines show that memory directly:
`double` and `triple` are the same code holding different captured values.
A closure is the functional answer to "an object with one method and some stored data."

`multiply()` reads `factor` rather than receiving it, yet it stays pure:
`factor` never changes after capture,
so the same argument always produces the same answer.
That is the difference between a captured constant and the global `balance` that made `withdraw()` unpredictable.

A closure fits when you want behavior configured once and then reused,
with its configuration kept private.
The captured variable has no name in any enclosing scope,
so ordinary code cannot read or rebind it.
That gives you encapsulation without declaring a class:

```python
# counter.py
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
No other code can name that variable, so no accident can corrupt it.

`increment()` is impure, and deliberately so.
The contrast with `withdraw()` is the lesson.
`withdraw()` mutated a module-level name that any code could touch;
`increment()` mutates a name that only it can touch.
When state has to exist,
a closure is one way to give exactly one function the right to change it.

The privacy is Python's usual kind, though, and not a lock.
`inspect.getclosurevars(tally).nonlocals` reports `{'count': 3}`,
and `tally.__closure__[0].cell_contents = 100` rewrites it.
Like the single leading underscore,
a closure states an intention that the language does not enforce.

The `nonlocal` statement lets `increment()` assign to the captured variable.
Reading a captured name, as `multiply()` read `factor`, needs no declaration.
But assignment is how Python decides a name is local,
so `count += 1` alone makes `count` a fresh local,
one referenced before assignment, and the call fails with `UnboundLocalError`.
`nonlocal count` redirects the assignment to the enclosing function's variable.
Forgetting it is the standard stumble when a closure first needs to write,
and the runtime message, complaining about a local variable
("cannot access local variable 'count' where it is not associated with a value"),
points nowhere near the missing declaration.
The checker is the better guide here.
If you delete the `nonlocal` line,
`ty` reports `Name 'count' used when not defined` on the `count += 1` line itself,
before the program runs.

## Partial Application

*Partial application* fixes some of a function's arguments and produces a new function that expects the rest.
`functools.partial()` does this without writing a wrapper by hand:

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
The keyword is doing real work here.
`partial(power, 2)` would bind `base` instead,
because positional arguments fill from the left,
and `square(5)` would then compute `2 ** 5`.
Partial application turns a general function into the specific one a caller needs,
which is handy when a higher-order function needs a single-argument callable.

Use partial application when an API expects a function of one argument and you have a function of several.
Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect,
through its `.func`, `.args`, and `.keywords` attributes,
and it binds their values when you build it.
This avoids the late-binding surprise a lambda created in a loop can produce,
demonstrated in [Function Objects](28_Function_Objects.md#command-choosing-the-operation-at-runtime)'s `late_binding.py`.

### Leaving a Gap with `Placeholder` {#leaving-a-gap-with-placeholder}

Binding `exponent` above worked because `power()` accepts it by keyword.
Positional arguments have no such freedom: `partial()` fills them from the left,
so fixing the third argument used to mean fixing the first two.
A function whose parameters are positional-only
(see [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters))
had no recourse.
`functools.Placeholder` (Python 3.14 and later)
is a marker that reserves a position for the caller:

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

`percent` fixes the bounds and leaves the middle argument open,
which is the specialization a caller needs and the one `partial()` could not previously express.
A `Placeholder` is not a default.
The caller must supply it:
calling `percent()` with no argument raises a `TypeError`.
The library also rejects a *trailing* placeholder, but for the opposite reason:
it would add nothing.
`partial()` already appends the call's arguments after the bound ones,
so `partial(clamp, 0, Placeholder)` would mean exactly what `partial(clamp, 0)` already means.

The `# type: ignore` comments mark a checker limitation rather than a code problem.
`ty` reads `partial(clamp, 0, Placeholder, 100)` as three arguments of the declared types,
so the marker looks like an `int` in the wrong place and the resulting callable looks like it takes nothing.
The runtime behaves correctly;
the annotations for this feature have not caught up.

## Composing Functions

*Function composition* builds a new function by feeding one function's output straight into the next.
You can assemble behavior from small pieces,
the way a pipeline reads as a sequence of steps:

```python
# composing.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    # Return a function that runs g, then feeds the result to f:
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
and you combine them without touching their internals.
The type parameters earn their place on the second `print()`:
the checker verifies that `label` accepts what `increment_then_double` produces,
and types the composed function `(int) -> str` rather than `(int) -> int`.

Composition grows by adding a stage rather than by enlarging one.
Each stage is also testable on its own,
and you build larger behavior by naming a new composition rather than writing new logic.
When a requirement changes,
you insert or swap a single stage and leave every other one untouched.

The standard library provides these building blocks ready-made;
[Toolkits](41_Functional_Toolkits.md) tours them.

## Putting the Pieces Together

Every section above showed one construct on its own.
Here they work together:

```python
# pipeline.py
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
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

data = [Reading("a", 18.0), Reading("b", 25.0), Reading("c", 30.5)]
print(report(data))
#: ['b 77.0', 'c 86.9']
print(data[0])
#: Reading(sensor='a', celsius=18.0)
```

Five of the chapter's ideas are doing work at once:
a frozen dataclass for the value,
`Sequence` to state that `report()` only reads, two pure functions,
`partial()` to turn a two-argument predicate into the one-argument callable `filter()` requires,
and `map()` and `filter()` for the traversal.
The second `print()` is the payoff.
The input list stays unchanged, so you can recompute the whole report, cache it,
or run it on another core with no coordination.

None of this is a different language.
It is ordinary Python in which each piece depends on its arguments alone,
and the chapters ahead build on that single property.

## Exercises

1.  In `pure_functions.py`, write a third function, `deposit(amount)`,
    that behaves like `withdraw()` but adds to `balance` instead of subtracting.
    Explain, the way the text does for `withdraw()`, why `deposit()` is impure.
2.  In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
    with no change to how `operations["*"](6, 4)` gets called.
3.  In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of `double` and `triple`,
    each remembering its own `factor`.
4.  In `composing.py`, write a third small function, `square(n)`,
    and build `increment_then_double_then_square = compose(square, increment_then_double)`.
    Predict `increment_then_double_then_square(3)` before running it.
5.  In `placeholder.py`, build a second partial, `at_least_ten`,
    that fixes only `low` to 10 and leaves both other arguments to the caller.
    Then try to fix only `high` without a `Placeholder` and explain why that is impossible.
6.  In `immutable_types.py`,
    add `CONFIG: Final[list[int]] = [1, 2]` and a line that appends to it.
    Run `ty`, and explain why it reports nothing when `MAX_SIZE = 200` on the next line is an error.
    Then change the annotation so appending *is* rejected.
7.  In `higher_order.py`,
    replace the `map()` and `filter()` calls with comprehensions,
    and the `sorted(key=len)` call with one that sorts by last letter.
    Then delete the `list()` around the `map()` call, print the result,
    and say what you see and why.
