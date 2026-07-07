# Functional Programming

Introductions to functional programming usually call it "programming with functions," and functions are indeed a central part of the practice.
But after (slowly) studying it for over ten years, I have started to wonder whether it's actually more about "functionality."
One definition of science is "what works."
Science has theories that fit the data, are predictive, and are falsifiable.
If "computer science" is to live up to its name, there should be some ideas and practices that fit that definition, and perhaps even some aspects that are mathematically provable.
This seems to me to be the broader challenge that functional programming takes on, and what I explore in this chapter.
That said, we must still begin with the more traditional explanations of functional programming.

## Pure Functions

A *pure function* computes its result from its arguments alone.
It reads nothing else and changes nothing else.
Given the same arguments, it always returns the same value.
It has no *side effects*: no printing, no file or network access, no mutation of anything outside the function.

Purity is the foundation on which everything else in this chapter builds.
You can test a pure function in isolation, because what you pass in fully determines its behavior.
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
`withdraw()` does not, because each call changes `balance` and the next call sees the new value.
You cannot understand a single `withdraw()` call without tracking the history of every call before it.

The payoff is trust.
A pure function is the most reliable code you can write, because its behavior is fully described by its inputs.
You test it with a single assertion and no fixture, since there is nothing to set up or restore.
You can call it from many threads at once, because it shares no state to corrupt.
[Parallelism for Free](#parallelism-for-free) turns that safety into speed.
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

Every later feature in this chapter is, in part, a way to keep more of your code pure.

## Immutability

An *immutable* value cannot change after creation.
Tuples, strings, `frozenset`, and frozen dataclasses are immutable.
Removing shared mutable state is the practical core of the functional style. A value that never changes cannot develop a bug from some forgotten change elsewhere.

Instead of modifying an object, you build a new one from the old:

```python
# immutability.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
try:
    setattr(p, "x", 5)  # A frozen instance rejects assignment
except AttributeError as e:
    print(e)
#: cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
```

The original `p` is untouched.
`moved` is a separate value.
When values never change underneath you, two parts of a program can share one without coordinating, and concurrent code needs no lock to read it.

Type annotations can state immutability so a checker enforces it.
`typing.Final` marks a name that must not be rebound.
The read-only collection types in `collections.abc`, such as `Sequence` and `Mapping`, describe a value you only read. They have no `append()` or item assignment, so a checker rejects any attempt to mutate through them:

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

The annotation is a promise the checker keeps for you, even when the value passed in is a mutable `list`.
Writing `MAX_SIZE = 200` later, or `values.append(4)` inside `total()`, is a type error caught before the program runs.

Immutability also unlocks abilities a mutable value lacks.
An immutable object can be *hashable*.
It can promise a stable hash for its whole life, so it can serve as a dictionary key or a set member.
You can also share it without a defensive copy, because no recipient can change it out from under you.
A `list` can do neither:

```python
# hashable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# A list has no stable hash, so it cannot be a key:
try:
    hash([3, 4])
except TypeError as e:
    print(e)
#: unhashable type: 'list'
```

These abilities are why the standard library uses tuples and frozen dataclasses whenever a value must be a key, cached, or shared across threads.

## Functions as First-Class Objects

A function in Python is an object like any other.
This is what *first-class* means. You can bind a function to a name, store it in a container, pass it as an argument, and return it from another function.
A function value is not special syntax. It is data you can move around.

```python
# first_class.py
def shout(text: str) -> str:
    return text.upper() + "!"

# A function is an object you can bind to another name:
loud = shout
print(loud("hello"))
#: HELLO!
# Functions can live in a data structure:
table = {"upper": str.upper, "title": str.title}
print(table["title"]("functional python"))
#: Functional Python
```

The dictionary holds functions as values, so a lookup yields a function you can immediately call.
The [Function Objects](30_Function_Objects.md) chapter approaches the same capability from the pattern side.

Treating functions as values lets data drive control flow.
A dictionary of functions replaces a long `if`/`elif` chain, because you select the behavior by looking it up:

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
Returning a function is the other half of the definition, covered under [Closures](#closures), below.

Higher-order functions provide separation of concerns.
`map()`, `filter()`, and `sorted()` each contain the loop that walks the data, written once,
and you supply only the part that differs from one use to the next.
You stop rewriting the same iteration scaffold,
along with the off-by-one and accumulator-initialization mistakes that scaffold invites.
The idea runs the other direction, too.
A function that takes a function can wrap it with operations like timing, retries, or logging.
This is what a decorator does in [Decorators](15_Decorators.md).

## Lambdas

A *lambda* is an unnamed function written as a single expression,
introduced in [Functions](05_Functions.md#lambdas).
The examples above already used lambdas as inline arguments, which is where they fit best.
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

When an inner function refers to a variable from the function that created it, Python keeps that variable alive.
The inner function plus the captured variables is a *closure*.
This is how a function can carry state without a class:

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

`multiplier()` returns `multiply()`, and each returned function remembers its own `factor`.
`double` and `triple` are the same code with different captured values.
A closure is the functional answer to "an object with one method and some stored data."

A closure fits when you want behavior configured once and then reused, with its configuration kept private.
The captured variable is reachable only through the returned function, so no other code can read or overwrite it.
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
Nothing outside `increment()` can reach that state, so no accident can corrupt it.

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

`square` and `cube` are specializations of `power`, each with one argument already supplied.
Partial application turns a general function into the specific one a caller needs,
which is handy when a higher-order function needs a single-argument callable.

Use partial application when an API expects a function of one argument and you have a function of several.
Rather than write a throwaway wrapper, you preset the fixed arguments and pass the result straight in.
Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect through its `.func` and `.args`,
and it binds their values at the moment you build it, which avoids the late-binding surprise a lambda created in a loop can produce.

## Composing Functions

*Function composition* builds a new function by feeding one function's output straight into the next.
You can assemble behavior from small pieces, the way a pipeline reads as a sequence of steps:

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

`compose(double, increment)` returns a function that increments first, then doubles.
Each piece stays small and pure, and you combine them without touching their internals.

Composition scales by addition.
Each stage stays small, pure, and testable on its own, and you build larger behavior by naming a new composition rather than writing new logic.
Stacking `compose()` calls forms a pipeline that reads as the list of steps it performs.
When a requirement changes, you insert or swap a single stage and leave every other one untouched.

## The `functools` Toolkit

The standard library ships the building blocks of functional Python.
`functools.reduce()` folds a sequence into a single value.
`functools.lru_cache` records a pure function's results so repeated calls are free:

```python
# toolkits.py
from functools import lru_cache, reduce
from operator import add

# reduce() folds a sequence down to a single value:
print(reduce(add, [1, 2, 3, 4]))
#: 10
# lru_cache remembers results, so repeats are free:
@lru_cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(30))
#: 832040
```

`lru_cache` is only correct because `fib()` is pure. Caching a function with side effects would skip the effects.
The toolkit rewards you for writing pure functions in the first place.

The reason to look here before writing your own version is that these tools are already written, already correct, and implemented in C.
A memoized cache or a fold over a sequence is one call, not a loop you have to debug.
Assembling a solution from vetted parts is faster to write and harder to get wrong, and it keeps the code declarative, naming the operation instead of spelling out its mechanics.
`itertools`, covered next, applies the same idea to lazy iteration.

## The `itertools` Toolkit

`itertools` builds lazy iterators from a small set of composable pieces.
Each one produces values on demand instead of building a list up front.
Combine them the way you combine any small function, by feeding one's output to the next.
What follows starts with the simplest tools and works up to the ones
with the most moving parts.

### `repeat()`

Yields the same object over and over, forever or a fixed number of times.

```python
# itertools_repeat.py
from itertools import repeat

print(list(repeat("x", 3)))
#: ['x', 'x', 'x']
```

### `count()`

Counts up (or down) forever from a start value, with a fixed step.

```python
# itertools_count.py
from itertools import count, islice

print(list(islice(count(10, 2), 5)))
#: [10, 12, 14, 16, 18]
```

### `cycle()`

Repeats an iterable forever.

```python
# itertools_cycle.py
from itertools import cycle, islice

print(list(islice(cycle("AB"), 5)))
#: ['A', 'B', 'A', 'B', 'A']
```

### `chain()`

Iterates several iterables one after another, as if they were one.
`chain.from_iterable(iterables)` does the same when the iterables
themselves arrive as one lazy sequence, rather than as separate arguments.

```python
# itertools_chain.py
from itertools import chain

print(list(chain([1, 2], [3, 4])))
#: [1, 2, 3, 4]
```

### `islice()`

Slices any iterable, including an infinite one, the way `[start:stop:step]` slices a list.

```python
# itertools_islice.py
from itertools import islice

print(list(islice(range(10), 2, 8, 2)))
#: [2, 4, 6]
```

### `pairwise()`

Yields consecutive overlapping pairs from an iterable.

```python
# itertools_pairwise.py
from itertools import pairwise

print(list(pairwise([1, 2, 3, 4])))
#: [(1, 2), (2, 3), (3, 4)]
```

### `batched()`

Groups an iterable into fixed-size tuples, with a shorter final batch if the length does not divide evenly.

```python
# itertools_batched.py
from itertools import batched

print(list(batched(range(7), 3)))
#: [(0, 1, 2), (3, 4, 5), (6,)]
```

### `accumulate()`

Yields the running total of an iterable, or the running result of any two-argument function.

```python
# itertools_accumulate.py
from itertools import accumulate

print(list(accumulate([1, 2, 3, 4])))
#: [1, 3, 6, 10]
```

### `compress()`

Keeps the elements of one iterable wherever the matching selector is true.

```python
# itertools_compress.py
from itertools import compress

print(list(compress("ABCD", [1, 0, 1, 0])))
#: ['A', 'C']
```

### `takewhile()`

Yields elements while a predicate holds, then stops at the first failure.

```python
# itertools_takewhile.py
from itertools import takewhile

print(list(takewhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [1, 2]
```

### `dropwhile()`

Skips elements while a predicate holds, then yields everything after.

```python
# itertools_dropwhile.py
from itertools import dropwhile

print(list(dropwhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [3, 4, 1]
```

### `filterfalse()`

Keeps the elements a predicate rejects, the mirror of `filter()`.

```python
# itertools_filterfalse.py
from itertools import filterfalse

print(list(filterfalse(lambda n: n % 2 == 0, range(6))))
#: [1, 3, 5]
```

### `starmap()`

Like `map()`, but unpacks each element as the arguments to the function.

```python
# itertools_starmap.py
from itertools import starmap

print(list(starmap(pow, [(2, 5), (3, 2)])))
#: [32, 9]
```

### `zip_longest()`

Zips iterables of different lengths, filling the gaps instead of stopping at the shortest.

```python
# itertools_zip_longest.py
from itertools import zip_longest

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]
```

### `groupby()`

Groups consecutive elements that share a key.
The input must already be sorted by that key, since it only merges neighbors.

```python
# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
```

### `tee()`

Splits one iterable into several independent iterators over the same data.

```python
# itertools_tee.py
from itertools import tee

a, b = tee([1, 2, 3])
print(list(a), list(b))
#: [1, 2, 3] [1, 2, 3]
```

### `product()`

The Cartesian product of the input iterables, the same pairs a nested `for` loop would build.

```python
# itertools_product.py
from itertools import product

print(list(product("AB", [1, 2])))
#: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
```

### `permutations()`

Every ordering of `r` elements from the iterable.

```python
# itertools_permutations.py
from itertools import permutations

print(list(permutations("AB")))
#: [('A', 'B'), ('B', 'A')]
```

### `combinations()`

Every way to choose `r` elements where order does not matter and nothing repeats.

```python
# itertools_combinations.py
from itertools import combinations

print(list(combinations("ABC", 2)))
#: [('A', 'B'), ('A', 'C'), ('B', 'C')]
```

### `combinations_with_replacement()`

Like `combinations()`, but the same element can appear more than once.

```python
# itertools_combinations_with_replacement.py
from itertools import combinations_with_replacement

print(list(combinations_with_replacement("AB", 2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'B')]
```

## Recursion

*Recursion* expresses a repeated computation as a function that calls itself.
Each recursive function needs a *base case* that stops the recursion and a *recursive case* that moves toward it:

```python
# recursion.py
import sys

def factorial(n: int) -> int:
    # Base case stops the recursion:
    if n <= 1:
        return 1
    # Recursive case moves toward the base case:
    return n * factorial(n - 1)

print(factorial(5))
#: 120
# Python caps how deep recursion can go:
print(sys.getrecursionlimit())
#: 1000
```

Recursion suits problems that are naturally self-similar, such as walking a tree.
Python does not optimize tail calls and limits the call stack, so very deep recursion will raise `RecursionError`.
For long flat sequences, a loop or one of the `itertools` tools is the better choice.

Recursion pays off when the data is itself recursive.
Code that walks a tree, nested data, or a directory reads most clearly when its shape matches the data's shape.
The function handles one node and trusts itself for the rest:

```python
# nested_sum.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)  # Recurse into a sublist
        else:
            total += item  # A plain number
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
```

`deep_sum()` states what to do with one element and delegates the nesting to itself.
An iterative version would have to maintain its own stack to remember where it was, reintroducing by hand the bookkeeping recursion gives you for free.

## Lazy Evaluation

*Lazy evaluation* computes a value only when something needs it.
A generator is the canonical example. It yields one value at a time instead of building a whole list up front.
Combined with `itertools`, you can describe an infinite sequence and take only the part you use:

```python
# lazy.py
from collections.abc import Iterator
from itertools import count, islice

# A generator yields values one at a time, on demand:
def squares() -> Iterator[int]:
    for n in count(1):
        yield n * n

# count() is infinite; islice() pulls only what we ask for:
first_five = list(islice(squares(), 5))
print(first_five)
#: [1, 4, 9, 16, 25]
```

`squares()` never finishes on its own, yet the program terminates because `islice()` requests exactly five values.
Nothing beyond those five is ever computed.
The [Performance](19_Performance.md) chapter looks at laziness from the angle of memory and speed.

Laziness matters most at scale.
A generator pipeline can process a multi-gigabyte file or a live network stream one item at a time, so memory stays flat no matter how large the source grows.
Stages chain together without building intermediate lists between them, and a consumer that stops early, such as `any()` or `next()`, means the upstream work for the items it never reaches never happens at all.

## Pattern Matching as Destructuring

The `match` statement, covered in [Pattern Matching](13_Pattern_Matching.md),
is used in this chapter as a declarative tool for taking data apart.
You describe the structures you expect, and Python binds the pieces for you.
One `match` collapses a stack of `isinstance()` tests, length checks,
and key or index lookups into a single readable description of each shape.
The test and the extraction happen together,
so there is no gap where you have confirmed the shape but not yet pulled out its parts.
This pays off most on shaped data, such as parsed JSON,
an abstract syntax tree, or the messages of a protocol,
where the alternative is a thicket of nested conditionals.

## Functional Error Handling

Raising an exception is one way to report failure.
The functional alternative returns a value that represents the failure,
so the caller must handle it in the open instead of through a separate control path.
[Functional Error Handling](14_Functional_Error_Handling.md) develops the approach in full,
from a return type of `float | None` up to a `Result` type that carries either an answer or an error.
The point for this chapter is what the style buys.
Failure appears in the return type,
so the type checker reminds every caller to handle it,
and a reviewer sees it without reading the body.
Control flow stays local,
with no exception leaping past intermediate frames to a distant handler.
You do pay by handling the failure at each step,
but that is the same discipline that stops an unhandled error from escaping unnoticed.

## Referential Transparency

An expression is *referentially transparent* when you can replace it with its value without changing the program's behavior.
Pure functions give you this property, and it is the precise reason purity matters:

```python
# referential_transparency.py
def add(a: int, b: int) -> int:
    return a + b

# The call add(2, 3) always equals 5, so the call and the
# value 5 are interchangeable everywhere in the program.
x = add(2, 3) + add(2, 3)
y = 5 + 5
print(x, y, x == y)
#: 10 10 True
```

Because `add(2, 3)` and `5` are interchangeable, a compiler can cache the call, evaluate it in any order, or skip a repeat.
You can also reason about the code by substitution, the same move you make in algebra.
This is the property that lets you check parts of a program, and sometimes prove them correct, and it connects back to this chapter's opening question about what counts as "what works."

This property is also the quiet reason the `lru_cache` from earlier is safe.
A memoizer may hand back a stored result only because the call is interchangeable with its value.
Every optimization that skips or reuses work, from a cache to a database query planner, is cashing in referential transparency.
The more of your program holds this property, the more of it a machine, or a proof, can verify.

## Declarative Style

*Declarative* code states the result you want.
*Imperative* code spells out each step to produce it.
A comprehension is the everyday example (see [Comprehensions](17_Comprehensions.md)).
The loop that filters and appends says *how*;
`[n * n for n in numbers if n % 2 == 0]` says *what*,
"the squares of the even numbers," and leaves the looping to Python.
This is the broader "functionality" the introduction points toward:
describe the result, and let the machine arrange the steps.
Declarative code says less and means more.
By naming the result instead of the steps,
you hand the reader your intent and give the runtime freedom to choose how to deliver it.
That freedom is why a SQL query, a NumPy expression,
or a dataframe operation can run on an optimized or parallel engine you never see.
You described the what, not a fixed sequence of moves.

## Parallelism for Free

The previous section ended with engines that parallelize behind your back.
Purity lets you claim that freedom in the open.
A pure function is automatically parallelizable.
Each call depends only on its arguments, so no call can affect another.
The calls can run in any order, on any schedule, on any number of cores, and the answers do not change.

Impure code has no such freedom.
Recall `withdraw()` from the start of this chapter.
Two parallel calls could both read `balance` before either writes it back, and one withdrawal would vanish.
Making that safe means adding a lock, and the lock serializes the very work you wanted to overlap.
Purity removes the problem instead of managing it.
With nothing shared, there is nothing to lock.

`count_primes()` is pure, and each call does enough work to be worth spreading across cores:

```python
# parallel_pure.py
# A pure function runs in parallel without modification.
from concurrent.futures import ProcessPoolExecutor

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count

def main() -> None:
    limits = [10_000, 20_000, 30_000, 40_000]
    serial = list(map(count_primes, limits))
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(count_primes, limits))
    assert parallel == serial
    print(parallel)

if __name__ == "__main__":
    main()
```

`map()` runs the four calls one at a time, on one core.
`pool.map()` sends the same calls to worker processes, which the operating system places on separate cores.
Run as a script, this prints `[1229, 2262, 3245, 4203]`.
The `assert` passes on every run, because a pure call returns the same answer no matter which process ran it, or when.
Notice what is missing: no locks, no queues, no shared state, and no changes to `count_primes()` itself.
The function needed no preparation for parallel execution.
It was ready the day it was written, because it was pure.
`ProcessPoolExecutor`, and the reasons Python parallelism uses processes rather than threads, are covered in [Concurrency](20_Concurrency.md#parallelism).

## An Assurance Spectrum

The chapter opened by asking whether programming can make the kind of provable claims a science makes.
Functional programming's honest answer is not one guarantee but a spectrum.
The properties built up here, purity, immutability, and referential transparency, buy assurance at every level.
You decide how far to take it.

1. The cheapest rung is local reasoning. Pure functions and immutable values let you understand one piece at a time, with no hidden state to carry in your head. Most code never needs more.
2. Next is type checking. A type signature is a small theorem, and the function body is its proof.
   This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence). Types are propositions and programs are their proofs.
   Running `ty` over the examples in this book discharges that proof for a useful class of mistakes.
3. Above that is *property-based testing*. You state a law the code must obey, then check it against many generated inputs. It does not prove the law.
   It works to falsify it, which is the falsifiability the chapter's opening requests.
4. At the top is formal proof.
   Dependently-typed languages such as Lean, Idris, and Rocq prove a program correct for every possible input, checked by machine.
   This is real, but rare outside specialized work.

The middle rung is the one most worth adopting now.
You can write a property check by hand, looping over random inputs and asserting the law.
A tool like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) does the same thing with sharper inputs,
and shrinks any failure to a minimal counterexample:

```python
# property_check.py
import random

def encode(text: str) -> str:
    # A trivial reversible transform:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

alphabet = "abcde"
for _ in range(1000):
    size = random.randint(0, 8)
    sample = "".join(random.choice(alphabet) for _ in range(size))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
```

The law is "decoding an encoding returns the original," and it holds for every input the loop tries.
A property test states what must always be true.
The machine searches for a counterexample, instead of forcing you to write one example at a time.

Hypothesis turns that loop into a declaration.
You describe the inputs with a *Strategy* and state the law once, as a normal `test_` function.
The framework supplies the cases, including awkward ones a handwritten loop would miss,
such as the empty string and unusual Unicode:

```python
# test_property.py
from hypothesis import given
from hypothesis import strategies as st

def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

@given(st.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
```

`@given(st.text())` feeds `test_roundtrip()` a stream of generated strings.
When a law fails, Hypothesis does not only report the failing input.
It shrinks it to the smallest example that still fails, so the bug surfaces as the clearest case rather than a random one.
That is the falsification machinery the chapter's opening called for, automated.

Two caveats keep this honest.
First, proof is not exclusive to functional code.
Hoare logic and tools like Dafny verify imperative programs too.
What purity changes is the cost. With no mutable state to track, each step of the reasoning is shorter.
Functional programming does not make correctness provable so much as it makes the proof affordable.
Second, most functional code stops well below the top rung.
Haskell programmers rarely prove a program correct.
They lean on types and on reasoning by substitution, and save full proof for the few places that earn it.

So the thread running through this chapter is not that functions are special.
It is that purity, immutability, and referential transparency shrink the distance between "I believe this is correct" and "I can show why."
Proof is the far end of that distance.
The everyday win is everything below it: code you can read, check, and test as statements about what is true.
That, more than the presence of functions, is the "functionality" the introduction set out to find.

## Exercises

1.  In `pure_functions.py`, write a third function, `deposit(amount)`, that behaves like `withdraw()`
    but adds to `balance` instead of subtracting.
    Explain, the way the text does for `withdraw()`, why `deposit()` is impure.
2.  In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
    with no change to how `operations["*"](6, 4)` gets called.
3.  In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of
    `double` and `triple`, each remembering its own `factor`.
4.  In `composing.py`, write a third small function, `square(n)`, and build
    `increment_then_double_then_square = compose(square, increment_then_double)`.
    Predict `increment_then_double_then_square(3)` before running it.
5.  In `parallel_pure.py`, add a fifth limit, `50_000`, to the `limits` list,
    and confirm `parallel == serial` still holds after the change.
