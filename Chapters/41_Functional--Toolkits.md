# Toolkits

[Foundations](40_Functional--Foundations.md) built behavior from small, pure,
composable pieces.
The standard library supplies two modules of such pieces.
`functools` operates on functions themselves.
`itertools` assembles lazy iterators from composable parts.
This chapter tours both toolkits,
then turns to two techniques that pair naturally with them,
lazy evaluation and recursion,
and closes with a case study that puts several of the pieces to work on one problem.

## The `functools` Toolkit

The standard library provides the building blocks of functional Python under `functools`,
from a single `reduce()` call to an alternate dispatch mechanism.
Each one replaces code you would otherwise write and debug yourself.
Caching logic, an eviction policy, a dispatch table:
each hides an edge case that's easy to miss on the first attempt.
These tools are already written and already correct.
Where speed matters most, in `reduce()`, `partial()`, and the two caches,
the implementation is C.
What follows starts with the simplest tools and works up to the ones with the most moving parts.

### `reduce`

Folds a sequence into a single value by repeatedly applying a two-argument function.

```python
# functools_reduce.py
from functools import reduce
from operator import add

print(reduce(add, [1, 2, 3, 4]))
#: 10
```

`operator.add` is `+` as a function:
the `operator` module supplies a named function for each operator,
so a fold never needs a `lambda a, b: a + b`.
For addition specifically, `sum()` is the dedicated built-in,
and `math.prod()` covers multiplication.
`reduce()` earns its keep for every other fold,
where no dedicated built-in exists.
On an empty sequence it raises `TypeError: reduce() of empty iterable with no initial value`,
because it has nothing to return.
A third argument supplies that starting value,
so `reduce(add, [], 0)` returns `0` instead of raising an exception.

### `cache`

Remembers every result forever,
so repeated calls with the same arguments cost nothing.
`@cache` works correctly only for pure functions.
A cached function with side effects runs those effects on the first call and never again.

```python
# functools_cache.py
from functools import cache

@cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(30))
#: 832040
print(fib.cache_info())
#: CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
```

Because `fib()` is recursive,
the cache now holds every value up to and including 30,
and the counts show what caching saved.
The 31 misses are the 31 distinct arguments, `0` through `30`.
The 28 hits are the calls that found a stored answer instead of recomputing it.
Fifty-nine calls in all, against 2,692,537 for the undecorated version,
where every branch recomputes the whole subtree beneath it.
[Caching](18_Techniques--Performance.md#caching)
runs both versions side by side, and [Recursion](#recursion)
comes back to why the recursive form is worth keeping.

One trap: decorating a method with `@cache` keys every entry on `self`,
so the cache holds a strong reference to each instance forever,
the lapsed-listener leak of [The Pythonic Observer](30_Patterns--Observer.md#the-pythonic-observer-a-list-of-callables)
in cache form.
For the usual case, one expensive value per instance,
use `@cached_property` below,
which stores the result on the instance and dies with it.

### `lru_cache`

Like `cache()`, but bounds memory by discarding the least recently used entry once the cache reaches `maxsize`.

```python
# functools_lru_cache.py
from functools import lru_cache

@lru_cache(maxsize=2)
def square(n: int) -> int:
    return n * n

square(1)
square(2)
square(3)  # Evicts 1, the least recently used
square(2)
square(1)
print(square.cache_info())
#: CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)
```

The single hit is the second `square(2)`, which was still in the cache.
The second `square(1)` is a fourth miss even though `1` was the first value computed,
and that miss proves the cache evicted `1`.
`currsize` never passes `maxsize`:
a new entry gets in only by pushing another one out.

### `partial`

Fixes some of a function's arguments and returns a new function that expects the rest.
[Partial Application](40_Functional--Foundations.md#partial-application)
covers it in depth.

```python
# functools_partial.py
from functools import partial

shout = partial(print, end="!\n")
shout("hello")
#: hello!
```

`functools.Placeholder` reserves a position so you can fix a later positional argument and leave an earlier one for the caller.
[Leaving a Gap with `Placeholder`](40_Functional--Foundations.md#leaving-a-gap-with-placeholder)
shows it.

### `partialmethod`

The same idea as `partial()`, but for a method.
The descriptor binds `self` automatically when you access it on an instance.

```python
# functools_partialmethod.py
from dataclasses import dataclass
from functools import partialmethod

@dataclass
class Text:
    value: str

    def pad(self, width: int, fill: str = " ") -> str:
        return self.value.rjust(width, fill)

    zero_pad = partialmethod(pad, fill="0")

print(Text("7").zero_pad(3))
#: 007
```

Since Python 3.14 a `partial` object is a descriptor too,
so writing `zero_pad = partial(pad, fill="0")` here works.
The two stop agreeing the moment an argument is positional.
`partialmethod` passes the instance first and the bound arguments after it,
which a method expects.
`partial` passes the bound arguments first and the instance after them,
so `partial(pad, 5)` calls `pad(5, instance)` and fails with `AttributeError: 'int' object has no attribute 'value'`.
Use `partialmethod` inside a class body and `partial` everywhere else.

### `cached_property`

Runs a property's code once, on first access, then reuses the stored result.
[Classes](07_Foundations--Classes.md#properties)
covers it alongside `@property`.

```python
# functools_cached_property.py
from dataclasses import dataclass
from functools import cached_property

@dataclass
class Lazy:
    n: int

    @cached_property
    def squared(self) -> int:
        print("computing")
        return self.n * self.n

x = Lazy(5)
print(x.squared)
#: computing
#: 25
print(x.squared)  # No second "computing"
#: 25
x.n = 10  # Doesn't change the cached result
print(x.squared)
#: 25
```

Be careful with caching:
changing an attribute the property read doesn't recalculate the cached result.
The escape hatch is `del x.squared`:
deleting the cached attribute discards the stored value,
and the next access recomputes it from the current state.

### `wraps`

Copies a wrapped function's name and docstring onto its wrapper,
so introspection still sees the original.
[Decorators](14_Techniques--Decorators.md#decorators-as-classes)
covers its sibling, `update_wrapper()`, for wrapping with a class instance.

```python
# functools_wraps.py
from collections.abc import Callable
from functools import wraps

def trace(
    func: Callable[[str], str]
) -> Callable[[str], str]:
    @wraps(func)
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

@trace
def greet(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

print(greet.__name__, "-", greet.__doc__)
#: greet - Say hello.
```

If you delete the `@wraps(func)` line,
that same `print()` reports `wrapper - None`,
because `greet` now refers to the inner function and nothing copied the original's identity onto it.
Everything that reads those attributes reads the wrapper instead: `help()`,
a traceback, a debugger, and a test framework that collects functions by name.
`wraps()` also sets `greet.__wrapped__` to the original function,
so a tool that needs the undecorated version can still find it.

### `cmp_to_key`

Wraps an old-style comparator, a function returning negative, zero, or positive,
into a key function `sorted()` uses directly.

```python
# functools_cmp_to_key.py
from functools import cmp_to_key

def by_length_desc(a: str, b: str) -> int:
    return len(b) - len(a)

words = ["a", "ccc", "bb"]
print(sorted(words, key=cmp_to_key(by_length_desc)))
#: ['ccc', 'bb', 'a']
```

### `total_ordering`

Fills in the rest of the comparison methods from `__eq__` and one of `__lt__`,
`__le__`, `__gt__`, or `__ge__`,
so a class needs two methods instead of six to sort and compare correctly.

```python
# functools_total_ordering.py
from functools import total_ordering

@total_ordering
class Weight:
    def __init__(self, kg: float) -> None:
        self.kg = kg

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Weight)
                and self.kg == other.kg)

    def __lt__(self, other: Weight) -> bool:
        return self.kg < other.kg

light = Weight(2)
heavy = Weight(5)
print(light < heavy, light <= heavy, light > heavy)
#: True True False
```

The plain class exists to show the tool.
In real code this `Weight` would be `@dataclass(frozen=True, order=True)`,
which generates all six comparisons from the field order and makes `total_ordering` unnecessary.
`total_ordering` earns its keep when the class cannot be a dataclass,
or when the ordering is not simply the fields in declaration order.

### `singledispatch`

Turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations you register separately.
[Visitor](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
uses `singledispatch()` as an alternative to the Visitor pattern,
including why the registered function below takes the name `_`.

```python
# functools_singledispatch.py
from functools import singledispatch

@singledispatch
def describe(value: object) -> str:
    return f"a {type(value).__name__}"

@describe.register
def _(value: int) -> str:
    return f"the number {value}"

print(describe("hi"), "|", describe(5))
#: a str | the number 5
```

`singledispatch()` examines only the first argument,
so a rule that depends on two types needs [Multiple Dispatching](32_Patterns--Multiple_Dispatching.md),
and a keyword-only argument cannot drive the dispatch.

### `singledispatchmethod`

The same dispatch, written as a method so it reads as `self.op(x)` instead of a bare function call.
The registered method below again takes the name `_`,
which [Visitor](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
explains.

```python
# functools_singledispatchmethod.py
from functools import singledispatchmethod

class Describer:
    @singledispatchmethod
    def describe(self, value: object) -> str:
        return f"a {type(value).__name__}"

    @describe.register
    def _(self, value: int) -> str:
        return f"the number {value}"

d = Describer()
print(d.describe("hi"), "|", d.describe(5))
#: a str | the number 5
```

`singledispatchmethod` dispatches on the first argument after `self`,
never on `self`, so it selects an implementation by the type of `value` the same way the plain function above does.

`itertools` does the same for iteration: ready-made pieces you compose,
instead of loops you write and test again.

## The `itertools` Toolkit

`itertools` builds lazy iterators from a small set of composable pieces.
Each one produces values on demand instead of building a list up front,
the property [Lazy Evaluation](#lazy-evaluation) revisits below.
Each is also a loop you would otherwise write by hand,
already tuned in C and already correct on the edge cases a hand-rolled version tends to miss:
the empty iterable, the single element,
and the point where two sequences run out at different lengths.
Combine them the way you combine any small function,
by feeding one's output to the next.
[Reusable Algorithms](23_Patterns--Iterators.md#reusable-algorithms)
introduced several of these as iterator plumbing.
This section is the catalog.

### `repeat`

Yields the same object over and over, forever or a fixed number of times.

```python
# itertools_repeat.py
from itertools import repeat

print(list(repeat("x", 3)))
#: ['x', 'x', 'x']
print(list(map(pow, range(5), repeat(2))))
#: [0, 1, 4, 9, 16]
```

The fixed form replaces the list you would have written as `["x"] * 3`.
The infinite form is the one that earns the import:
it supplies an argument that never changes, without building a list to hold it.
Here the output stops when `range(5)` runs out,
because `map()` stops at its shortest input.

### `islice`

Slices any iterable, including an infinite one,
the way `[start:stop:step]` slices a list.

```python
# itertools_islice.py
from itertools import islice

print(list(islice(range(10), 2, 8, 2)))
#: [2, 4, 6]
```

Two differences from a list slice.
`islice()` rejects negative indices with a `ValueError`,
since it cannot count back from an end it may never reach.
And it consumes what it passes over:
if you give it an iterator rather than a list,
that iterator resumes where the slice stopped instead of at the beginning.

### `count`

Counts up (or down) forever from a start value, with a fixed step.

```python
# itertools_count.py
from itertools import count, islice

print(list(islice(count(10, 2), 5)))
#: [10, 12, 14, 16, 18]
```

### `cycle`

Repeats an iterable forever.

```python
# itertools_cycle.py
from itertools import cycle, islice

print(list(islice(cycle("AB"), 5)))
#: ['A', 'B', 'A', 'B', 'A']
```

`cycle()` saves each element the first time through,
so the whole input stays in memory as long as the cycle lives.

### `chain`

Iterates several iterables one after another, as if they were one.
`chain.from_iterable(iterables)` does the same when the iterables themselves arrive as one lazy sequence,
rather than as separate arguments.
Where the iterables come from a loop,
[unpacking in a comprehension](16_Techniques--Comprehensions.md#unpacking-in-comprehensions)
says the same thing without the import.

```python
# itertools_chain.py
from itertools import chain

print(list(chain([1, 2], [3, 4])))
#: [1, 2, 3, 4]
print(list(chain.from_iterable([[1, 2], [3, 4]])))
#: [1, 2, 3, 4]
```

### `pairwise`

Yields consecutive overlapping pairs from an iterable,
without indexing by hand and risking an off-by-one at the ends.

```python
# itertools_pairwise.py
from itertools import pairwise

print(list(pairwise([1, 2, 3, 4])))
#: [(1, 2), (2, 3), (3, 4)]
```

### `batched`

Groups an iterable into fixed-size tuples,
with a shorter final batch if the length does not divide evenly,
the kind of remainder logic that's easy to get wrong in a hand-written loop.

```python
# itertools_batched.py
from itertools import batched

print(list(batched(range(7), 3)))
#: [(0, 1, 2), (3, 4, 5), (6,)]
```

A short final batch is normal for pagination and wrong for fixed-width records.
For fixed-width records,
`batched(data, 3, strict=True)` raises `ValueError: batched(): incomplete batch` instead,
the same choice `zip(strict=True)` offers below.

### `accumulate`

Yields the running total of an iterable,
or the running result of any two-argument function.

```python
# itertools_accumulate.py
from itertools import accumulate
from operator import mul

print(list(accumulate([1, 2, 3, 4])))
#: [1, 3, 6, 10]
print(list(accumulate([1, 2, 3, 4], mul)))
#: [1, 2, 6, 24]
```

`accumulate()` is `reduce()` with the intermediate results kept:
the last value it yields is the value `reduce()` would return.

### `compress`

Keeps the elements of one iterable wherever the matching selector is true.

```python
# itertools_compress.py
from itertools import compress

print(list(compress("ABCD", [1, 0, 1, 0])))
#: ['A', 'C']
```

### `takewhile`

Yields elements while a predicate holds, then stops at the first failure.

```python
# itertools_takewhile.py
from itertools import takewhile

print(list(takewhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [1, 2]
```

The input carries a trailing `1` to separate `takewhile()` from `filter()`.
`filter(lambda n: n < 3, ...)` returns `[1, 2, 1]`,
because filtering skips what fails and keeps looking.
`takewhile()` stops at the first failure and never reaches the last element.
On finite data that is a detail.
On an infinite source it decides whether the program terminates.
[Reusable Algorithms](23_Patterns--Iterators.md#reusable-algorithms)
works through that case.

### `dropwhile`

Skips elements while a predicate holds, then yields everything after.

```python
# itertools_dropwhile.py
from itertools import dropwhile

print(list(dropwhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [3, 4, 1]
```

The same trailing `1` marks the same distinction from the other direction.
`dropwhile()` stops testing once the predicate fails,
so the final `1` comes through,
where `filterfalse()` would test every element and return `[3, 4]`.

### `filterfalse`

Keeps the elements a predicate rejects, the mirror of `filter()`.

```python
# itertools_filterfalse.py
from itertools import filterfalse

print(list(filterfalse(lambda n: n % 2 == 0, range(6))))
#: [1, 3, 5]
```

### `starmap`

Like `map()`, but unpacks each element as the arguments to the function.

```python
# itertools_starmap.py
from itertools import starmap

print(list(starmap(pow, [(2, 5), (3, 2)])))
#: [32, 9]
```

### `zip_longest`

Zips iterables of different lengths,
filling the gaps instead of stopping at the shortest.
The default filler is `None`.
When `None` is a valid element,
pass a distinct [sentinel](05_Foundations--Functions.md#default-and-keyword-arguments)
as the `fillvalue` keyword argument:

```python
# itertools_zip_longest.py
from itertools import zip_longest

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]

MISSING = sentinel("MISSING")
print(list(zip_longest([1, 2, 3], [4, 5],
                       fillvalue=MISSING)))
#: [(1, 4), (2, 5), (3, MISSING)]
```

Three ways to zip inputs of different lengths,
and the choice says what a mismatch means.
Plain `zip()` stops at the shortest and says nothing,
which is right when the extra elements are genuinely surplus.
`zip(a, b, strict=True)` raises `ValueError: zip() argument 2 is shorter than argument 1`,
which is right when equal lengths are an invariant you want checked.
`zip_longest()` pads,
which is right when the missing elements are data in their own right.

### `groupby`

Groups consecutive elements that share a key.
The input must arrive sorted by that key, since it merges only neighbors.

```python
# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
print([(k, list(g)) for k, g in groupby(["b", "a", "b"])])
#: [('b', ['b']), ('a', ['a']), ('b', ['b'])]
```

The second line is what unsorted input costs you:
`"b"` comes back as two separate groups, and no error says so.
`sorted(data, key=keyfunc)` before `groupby(data, key=keyfunc)` is the fix,
with the same key function both times.

The `list(g)` in the comprehension is there for a reason.
Each group is a view onto the one underlying iterator,
so advancing to the next group invalidates the previous group's view.
`list(groupby(data))` therefore returns three keys paired with three empty iterators:
the outer `list()` walks all the way to the end before anything reads a group.
Consume each group before asking for the next one,
as the comprehension above does.

### `tee`

Splits one iterable into several independent iterators over the same data,
so two consumers can each walk it once without collecting it into a list first.

```python
# itertools_tee.py
from itertools import tee

a, b = tee([1, 2, 3])
print(list(a), list(b))
#: [1, 2, 3] [1, 2, 3]
```

Two cautions.
After `tee()`, use only the returned iterators.
Advancing the original source steals values the copies never see.
And `tee()` buffers every value one copy has consumed and the other has not,
so draining `a` completely before touching `b`, as this demo does,
stores the whole sequence.
When one consumer runs far ahead of the other,
`list()` is simpler and no more expensive.
`tee()` wins when the consumers stay roughly in step.
[Iterators](23_Patterns--Iterators.md#generators)
measures that buffering and adds a third caution:
`tee()` shares one unlocked buffer between its branches,
so handing them to separate threads corrupts it.

### `product`

The Cartesian product of the input iterables,
the same pairs a nested `for` loop builds,
without writing and re-testing that loop yourself.

```python
# itertools_product.py
from itertools import product

print(list(product("AB", [1, 2])))
#: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
```

Unlike the tools above,
`product()` reads its inputs completely before yielding its first tuple,
so none of them can be infinite: `product(count(1), "AB")` hangs at the call,
before anything asks for a value.

### `permutations`

Every ordering of `r` elements from the iterable.

```python
# itertools_permutations.py
from itertools import permutations

print(list(permutations("AB")))
#: [('A', 'B'), ('B', 'A')]
```

### `combinations`

Every way to choose `r` elements where order does not matter and nothing repeats.

```python
# itertools_combinations.py
from itertools import combinations

print(list(combinations("ABC", 2)))
#: [('A', 'B'), ('A', 'C'), ('B', 'C')]
```

### `combinations_with_replacement`

Like `combinations()`, but the same element can appear more than once.

```python
# itertools_combinations_with_replacement.py
from itertools import combinations_with_replacement

print(list(combinations_with_replacement("AB", 2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'B')]
```

### Composing the Pieces

Each entry above is one stage.
Stacked, they are a pipeline:

```python
# itertools_pipeline.py
from itertools import batched, count, islice, takewhile

squares = (n * n for n in count(1))
batches = batched(squares, 3)
totals = (sum(b) for b in batches)
print(list(takewhile(lambda t: t < 500, totals)))
#: [14, 77, 194, 365]
print(list(islice(squares, 3)))
#: [256, 289, 324]
```

Four stages sit on top of an infinite source,
and none of them run until `list()` pulls.
The second `print()` shows the source resuming at 16 rather than 13,
because `takewhile()` must pull the batch `(169, 196, 225)` and discard it to discover that its total of 590 exceeds the limit.
A pull-based pipeline reads one value further than it keeps,
and that one value cost three squares.

## Lazy Evaluation

*Lazy evaluation* computes a value only when something needs it.
A generator is the canonical example.
It yields one value at a time instead of building a whole list up front.
With `itertools`, you can describe an infinite sequence and take only the part you use:

```python
# lazy.py
from collections.abc import Iterator
from itertools import count, islice

def squares() -> Iterator[int]:
    for n in count(1):
        # Proves this runs on demand
        print(f"computing square {n}")
        yield n * n

# count() is infinite; islice() pulls only what's needed:
first_five = list(islice(squares(), 5))
print(first_five)
#: computing square 1
#: computing square 2
#: computing square 3
#: computing square 4
#: computing square 5
#: [1, 4, 9, 16, 25]
```

`squares()` never finishes on its own,
yet the program terminates because `islice()` requests five values.
Each `computing square N` line appears only when `islice()` pulls that value,
one at a time, the same way any `for` loop consumes a generator.
`squares()` never runs ahead to precompute several values before handing one back.
No sixth `computing square` line appears,
because `islice()` stops asking when it has delivered five.
`list(squares())[:5]` looks equivalent and is a different program.
It builds the whole list before slicing, so it asks `squares()` for every value,
and `squares()` never runs out.
Slicing lazily lets the source be infinite.
Slicing a list requires a source that ends.
[Lazy Evaluation with Generators](18_Techniques--Performance.md#lazy-evaluation-with-generators)
looks at the same idea from the perspective of memory and speed.

Laziness matters most at scale.
A generator pipeline can process a multi-gigabyte file or a live network stream one item at a time,
so memory use doesn't grow with the size of the source.
Stages chain together without building intermediate lists between them,
and a consumer that stops early, such as `any()` or `next()`,
keeps the upstream stages from computing the items it never reaches.

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

A `for` loop computes this same factorial in about the same number of lines and stays clear of that limit.
For counting down to zero, the loop is as fast and as short as the recursion.
Recursion pays off once the problem branches rather than repeats,
as the next example shows.

Branching brings a cost that counting down does not.
More than one branch can reach the same subproblem,
and a plain recursive function recomputes it every time.
That is why the recursive `fib()` under [`cache`](#cache)
gets a decorator rather than a rewrite as a loop:
the recursion states the definition, and the cache removes the repetition.

Recursion suits problems that are naturally self-similar,
such as walking a tree.
Python does not optimize tail calls and limits the call stack,
so deep recursion raises a `RecursionError`.
`sys.setrecursionlimit()` lifts that ceiling when the depth is genuine,
but it is the wrong answer for a long flat sequence,
where a loop or one of the `itertools` tools is the better choice.

Code that walks a tree, nested data,
or a directory reads best when its shape matches the data's shape.
The function handles one node and trusts itself for the rest:

```python
# nested_sum.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            # Recurse into a sublist
            total += deep_sum(item)
        else:
            total += item  # A plain number
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
```

`deep_sum()` states what to do with one element and delegates the nesting to itself.
Writing this as a loop means building your own stack to track which sublists are still open,
and getting the push and pop correct at every depth.
The recursive version gets that bookkeeping from the call stack,
so the body says only what to do with one element and where to descend,
and says nothing about depth.

## Case Study: Pairing Rotations

Pair up participants for an activity across several rounds,
and avoid repeating a pairing until every possible pairing has had a turn.
Several of these ideas work together here,
on one small program instead of one at a time:
an infinite generator for the rounds,
`islice()` to take as many of them as you want,
`combinations()` for the pairs inside a group,
and a seeded random source that makes the whole schedule reproducible.

The *circle method* solves the pairs-only version exactly,
by direct construction.
Fix one player and arrange the rest in a circle.
Each round, pair players sitting across from each other,
then rotate everyone but the fixed player by one seat.
For an even number of players `n`,
that produces `n - 1` rounds with no repeated pair.
No schedule can do better,
because those rounds use every one of the `n * (n - 1) / 2` possible pairs exactly once.
The classical fix for an odd roster is a phantom player:
whoever draws the phantom sits out that round.

The trick stops working the moment the groups are threes, fours,
or any size but two.
The circle method is a closed-form answer to one narrow question,
"how do you 1-factorize a complete graph into perfect matchings,"
and pairs are the only group size where that question has a tidy rotation-based answer.
Scheduling groups of three without repeats is the far harder problem that *Kirkman's schoolgirl problem* poses,
solvable only for specific roster sizes and with no simple formula behind it.
Rather than chase an exact answer that may not exist for a given `students` and `size`,
a general version can settle for a good one: build each group by adding,
one member at a time, whoever the current members have met the fewest times,
with those meeting counts kept in a running history instead of computed from a round number:

```python
# student_pairs.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()
    rng = random.Random(seed)

    def met(group: list[str], candidate: str) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[str]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                closest = min(pool,
                              key=lambda c: met(group, c))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        # Too few left for a full group of `size`
        for extra in pool:
            roomiest = min(groups,
                           key=lambda g: met(g, extra))
            roomiest.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
rounds = list(islice(group_rounds(students, 2),
                     len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
#: 1 [('Di', 'Bo', 'Eve'), ('Cy', 'Ana'), ('Gia', 'Fi')]
#: 2 [('Eve', 'Fi', 'Ana'), ('Bo', 'Gia'), ('Cy', 'Di')]

meetings = [frozenset(pair) for r in rounds for group in r
            for pair in combinations(group, 2)]
possible = set(map(frozenset, combinations(students, 2)))
distinct = set(meetings)
print(len(distinct), "of", len(possible),
      "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(meetings) - len(distinct), "repeat meetings")
#: 14 repeat meetings

trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]

# Fewer than `size`
print(next(group_rounds(["Ana", "Bo"], 5)))
#: [('Ana', 'Bo')]
```

Called with `size=2`,
`group_rounds()` covers all `21` possible pairs across the seven rounds,
at the cost of `14` repeat meetings.
An odd roster leaves one player over,
so each round folds that player into an existing pair,
and those triples produce the repeats.
`group_rounds()` covers the pairs with no rotation and no fixed player:
a shuffle, then a greedy choice repeated until the roster runs out.
Called with `size=3`, the same function schedules trios instead.
Seven students do not split evenly into threes,
so one group grows to four rather than leaving anyone out,
the same join-instead-of-sit-out choice the pair rounds made above.

A roster smaller than one full group takes that choice to its limit.
The `while len(pool) >= size` loop never runs,
so no group exists to fold the leftovers into,
and the `if pool and not groups` line opens one.
Without it, `min()` receives no groups to compare and raises a `ValueError`.
Two students and a requested size of five produce one group of two,
because the alternative is a round in which nobody meets anyone.

`met()` runs once per candidate per slot,
so it looks like the place for `@cache` from earlier in this chapter.
Caching it would be wrong.
`met()` reads `history`, and `history` changes at the end of every round,
so a cached answer from round 0 would still come back in round 6 after every count it summed had moved.
The `cache` entry's rule, pure functions only, is the reason:
a function that reads mutable state is impure, however simple its body looks.

Generality costs something.
The circle method needs no memory.
Which pair sits where in round `r` follows from `r` alone.
`group_rounds()` needs the `history` `Counter`, because no formula predicts,
from a round number alone,
which grouping of arbitrary size keeps every pair's meeting count lowest.
`group_rounds()` is still deterministic in the sense that matters for testing.
The same `students`, `size`,
and `seed` always produce the same infinite sequence of rounds,
since `random.Random(seed)` never reaches outside itself for randomness.
Computing round `100` now means generating rounds `0` through `99` first,
where the circle method could compute round `100` directly,
from its arithmetic alone.
That trade, memory for generality, is the same one [Recursion](#recursion)
makes when a loop's simple counter is not enough and the problem needs a stack instead.

## Choosing From the Toolkits

The rule for both modules is the same: before writing a loop,
ask whether the loop already has a name.
A running total is `accumulate()`, a width-two sliding window is `pairwise()`,
a remainder-safe chunking is `batched()`,
and a memoized pure function is `@cache`.
Each of those replaces a small piece of code that works on the first input you try and fails on the empty input,
the single element, or the last partial batch.

The second rule is that the pieces exist to stack.
`islice(count(10, 2), 5)` in this chapter is two stages.
A real pipeline is five or six, and it still holds one item in memory at a time.
[Error Handling](42_Functional--Error_Handling.md)
asks what such a pipeline does when one stage fails,
the question a chain of pure functions leaves open.

## Exercises

1.  Rewrite `deep_sum()` from `nested_sum.py` without recursion,
    using a list as an explicit stack.
    Compare the two versions for length,
    and name the places an off-by-one can hide in the loop version that do not exist in the recursive one.
2.  `functools_lru_cache.py` prints `CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)`.
    Change `maxsize` to `3`, predict the four numbers before running it,
    then run it and account for any difference.
3.  Write `batch_totals(source, n)`,
    which takes an iterator and yields the sum of each `n`-element batch,
    built only from `itertools` pieces and a generator expression.
    Show that it stays lazy by passing it `count(1)` and taking five values.
4.  `groupby()` on unsorted input silently returns the same key more than once.
    Write `grouped(data, key)` returning a `dict[K, list[V]]` that cannot make that mistake,
    and say what it costs relative to `groupby()`.
5.  Decorate `deep_sum()` with `@cache` and explain the exception.
    What would have to change about the `Nested` alias for caching to be possible?
6.  `group_rounds()` takes a `seed` and builds its own `random.Random`.
    Replace that with an `rng: random.Random` parameter.
    Which property of the function does that preserve,
    and which one does it hand to the caller?
