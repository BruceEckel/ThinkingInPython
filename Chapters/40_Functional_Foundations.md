# Foundations

This chapter begins the book's exploration of functional programming.
Here is what its ideas buy you, before the vocabulary arrives.
A pure function cannot corrupt state you forgot about.
It has fewer bugs to chase, and it needs no mock or fixture to test.
A cache or a fold from `functools` or `itertools` is code you never write yourself,
already correct on the edge case you would have missed at first.
A function with no shared state needs no lock,
so it parallelizes with no new code.
And code built from small,
checkable pieces is code you can reason about by substitution,
the same way you check a line of algebra.
None of this asks you to abandon loops, classes, or mutation.
It asks you to notice when a piece of code can depend on nothing but its arguments,
and to write it that way when it can.

This chapter builds the foundations: pure functions, immutable values,
and the ways Python lets you pass, capture, specialize, and combine functions.
[Toolkits](41_Functional_Toolkits.md) tours the standard library's support,
[Error Handling](42_Functional_Error_Handling.md)
turns failure into an ordinary value,
and [Assurance](43_Functional_Assurance.md)
examines what the discipline lets you claim about your code.

## Pure Functions

A *pure function* computes its result from its arguments alone.
It reads nothing else and changes nothing else.
Given the same arguments, it always produces the same outcome,
whether that outcome is a returned value or a raised exception.
It has no *side effects*: no printing, no file or network access,
no mutation of anything outside the function.

Purity is the foundation on which everything else in these chapters builds.
You can test a pure function in isolation,
because what you pass in fully determines its behavior.
You can cache its result, because the answer never changes.
You can reason about it the way you reason about an equation:

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
You test it with a single assertion and no fixture,
since there is nothing to set up or restore.
You can call it from many threads at once,
because it shares no state to corrupt.
[Automatic Parallelism](43_Functional_Assurance.md#automatic-parallelism)
turns that safety into speed.
A cache can store its results, knowing the answer will never go stale:

```python
# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

# No setup or teardown: assert the result directly:
assert slope(10, 2) == 5.0
assert slope(9, 3) == 3.0
print("ok")
#: ok
```

Every later feature in these chapters is, in part,
a way to keep more of your code pure.

## Immutability

An *immutable* value cannot change after creation.
Tuples, strings, `frozenset`, and frozen dataclasses are immutable.
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

The demonstration spells the assignment `setattr(p, "x", 5)` because the direct spelling `p.x = 5` never gets to run:
the type checker rejects it statically, as it should.
`setattr()` slips past the static check so the listing can show the *runtime* rejection too.
The original `p` is untouched.
`moved` is a separate value.
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

The annotation is a promise the checker keeps for you,
even when the value passed in is a mutable `list`.
Writing `MAX_SIZE = 200` later, or `values.append(4)` inside `total()`,
is a type error caught before the program runs.
Mind what `Final` does and does not freeze.
It locks the *binding*, not the object:
declare `CONFIG: Final[list[int]] = [...]` and `CONFIG.append(...)` still succeeds,
for the checker and at runtime alike.
This is the shallow-freezing lesson of [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)
in another costume.
For an immutable value, make the value's own type immutable,
`Final[tuple[int, ...]]`, and let `Final` guard only the name.

Immutability also unlocks abilities a mutable value lacks.
An immutable object can be *hashable*.
It can promise a stable hash for its whole life,
so it can serve as a dictionary key or a set member.
You can also share it without a defensive copy,
because no recipient can change it out from under you.
A `list` can do neither:

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

These abilities are why the standard library uses tuples and frozen dataclasses whenever a value must be a key,
cached, or shared across threads.

## Functions as First-Class Objects

A function in Python is an object like any other.
This is what *first-class* means.
You can bind a function to a name, store it in a container,
pass it as an argument, and return it from another function.
A function value is not special syntax.
It is data you can move around.

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
This is the structure behind dispatch tables and the plugin registries that let a program grow without editing its core.

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

The lambdas above exist to show the machinery,
and for exactly these cases Python offers a lookalike you should usually prefer:
the comprehension ([Comprehensions](16_Comprehensions.md)).
`[n * n for n in numbers]` says what `map()` plus a fresh lambda says,
more directly, and `[n for n in numbers if n % 2 == 0]` replaces the `filter()` call the same way.
`map()` and `filter()` earn their keep when the function *already exists*:
`map(str.strip, lines)` beats `[line.strip() for line in lines]` because the name is the whole story.
The rule of thumb: existing function, use the higher-order form;
expression you are writing on the spot, use the comprehension.
`sorted()`'s `key` has no comprehension equivalent,
so it is a higher-order argument either way.

Higher-order functions provide separation of concerns.
`map()`, `filter()`, and `sorted()` each contain the loop that walks the data,
written once, and you supply only the part that differs from one use to the next.
You stop rewriting the same iteration scaffold,
along with the off-by-one and accumulator-initialization mistakes that scaffold invites.
The idea runs the other direction, too.
A function that takes a function can wrap it with operations like timing,
retries, or logging.
This is what a decorator does in [Decorators](14_Decorators.md).

## Lambdas

A *lambda* is an unnamed function written as a single expression,
introduced in [Functions](05_Functions.md#lambdas).
The examples above already used lambdas as inline arguments,
which is where they fit best.
Their value is locality.
When a transformation is one short expression,
a lambda keeps it at the call site, where the reader already is,
instead of sending them to a named function defined elsewhere.
`sorted(words, key=lambda w: w.lower())` states the sort order right where the sort happens.
Naming that one-liner would cost a line, a name to invent,
and a definition to look up, with nothing gained in clarity.
For anything larger, write a `def`.
A named function carries a docstring, a readable name in tracebacks,
and room to grow.

## Closures

When an inner function refers to a variable from the function that created it,
Python keeps that variable alive.
The inner function plus the captured variables is a *closure*.
This way, a function can carry state without a class:

```python
# closures.py
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
```

`multiplier()` returns `multiply()`,
and each returned function remembers its own `factor`.
`double` and `triple` are the same code with different captured values.
A closure is the functional answer to "an object with one method and some stored data."

A closure fits when you want behavior configured once and then reused,
with its configuration kept private.
The captured variable is reachable only through the returned function,
so no other code can read or overwrite it.
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

Each call to `make_counter()` builds an independent counter with its own hidden `count`.
Nothing outside `increment()` can reach that state,
so no accident can corrupt it.

The `nonlocal` statement is what lets `increment()` *assign* to the captured variable.
Reading a captured name, as `multiply()` read `factor`, needs no declaration.
But assignment is how Python decides a name is local,
so `count += 1` alone would make `count` a fresh local,
one referenced before assignment,
and the call would fail with `UnboundLocalError`.
`nonlocal count` redirects the assignment to the enclosing function's variable.
Forgetting it is the standard stumble when a closure first needs to write,
and the error message, complaining about a local variable,
points nowhere near the missing declaration.

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
```

`square` and `cube` are specializations of `power`,
each with one argument already supplied.
Partial application turns a general function into the specific one a caller needs,
which is handy when a higher-order function needs a single-argument callable.

Use partial application when an API expects a function of one argument and you have a function of several.
Rather than write a throwaway wrapper,
you preset the fixed arguments and pass the result straight in.
Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect,
through its `.func`, `.args`, and `.keywords` attributes,
and it binds their values when you build it.
This avoids the late-binding surprise a lambda created in a loop can produce,
demonstrated in [Function Objects](28_Function_Objects.md#command-choosing-the-operation-at-runtime)'s `late_binding.py`.

## Composing Functions

*Function composition* builds a new function by feeding one function's output straight into the next.
You can assemble behavior from small pieces,
the way a pipeline reads as a sequence of steps:

```python
# composing.py
from collections.abc import Callable

def compose(
    f: Callable[[int], int], g: Callable[[int], int]
) -> Callable[[int], int]:
    # Return a function that runs g, then feeds the result to f:
    def composed(x: int) -> int:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2

increment_then_double = compose(double, increment)
print(increment_then_double(10))
#: 22
```

`compose(double, increment)` returns a function that increments first,
then doubles.
Each piece stays small and pure,
and you combine them without touching their internals.

Composition scales by addition.
Each stage stays small, pure, and testable on its own,
and you build larger behavior by naming a new composition rather than writing new logic.
Stacking `compose()` calls forms a pipeline that reads as the list of steps it performs.
When a requirement changes,
you insert or swap a single stage and leave every other one untouched.

The standard library ships these building blocks ready-made;
[Toolkits](41_Functional_Toolkits.md) tours them.

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
