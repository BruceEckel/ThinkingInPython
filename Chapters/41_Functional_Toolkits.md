# Functional Toolkits

[Functional Foundations](40_Functional_Foundations.md)
built behavior from small, pure, composable pieces.
The standard library supplies two modules of such pieces.
`functools` operates on functions themselves.
`itertools` assembles lazy iterators from composable parts.
This chapter tours both toolkits,
then turns to two techniques that pair naturally with them,
recursion and lazy evaluation,
and closes with a case study that puts several of the pieces to work on one problem.

## The `functools` Toolkit

The standard library ships the building blocks of functional Python under `functools`,
from a single fold to an alternate dispatch mechanism.
Each one replaces code you would otherwise write and debug yourself.
Caching logic, an eviction policy, a dispatch table,
each one hides an edge case that's easy to miss on the first attempt.
These tools are already written, already correct,
and implemented in C for speed.
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

For addition specifically, `sum()` is the built-in spelling,
and `math.prod()` covers multiplication.
`reduce()` earns its keep for every other fold,
where no dedicated built-in exists.

### `cache`

Remembers every result forever,
so repeated calls with the same arguments cost nothing.
Note that this only works correctly for pure functions.
Caching a side-effecting function skips the effects.

```python
# functools_cache.py
from functools import cache

@cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(30))
#: 832040
```

Because `fib()` is recursive, the values up to and including 30 are now cached.
This accelerates future calls to `fib()`.

One trap: decorating a *method* with `@cache` keys every entry on `self`,
so the cache holds a strong reference to each instance forever,
the lapsed-listener leak of [Observer](30_Observer.md) in cache form.
For the usual case, one expensive value per instance,
use `@cached_property` below,
which stores the result on the instance and dies with it.

### `lru_cache`

Like `cache()`, but bounds memory by discarding the least recently used entry once `maxsize` is reached.

```python
# functools_lru_cache.py
from functools import lru_cache

@lru_cache(maxsize=2)
def square(n: int) -> int:
    return n * n

square(1)
square(2)
square(3)  # Evicts 1, the least recently used
print(square.cache_info())
#: CacheInfo(hits=0, misses=3, maxsize=2, currsize=2)
```

### `partial`

Fixes some of a function's arguments and returns a new function that expects the rest.
[Partial Application](40_Functional_Foundations.md#partial-application)
covers it in depth.

```python
# functools_partial.py
from functools import partial

shout = partial(print, end="!\n")
shout("hello")
#: hello!
```

### `partialmethod`

The same idea as `partial()`, but for a method.
The descriptor binds `self` automatically when accessed on an instance.

```python
# functools_partialmethod.py
from functools import partialmethod

class Text:
    def __init__(self, value: str) -> None:
        self.value = value

    def pad(self, width: int, fill: str = " ") -> str:
        return self.value.rjust(width, fill)

    zero_pad = partialmethod(pad, fill="0")

print(Text("7").zero_pad(3))
#: 007
```

### `cached_property`

Runs a property's code once, on first access, then reuses the stored result.
[Classes](07_Classes.md#properties) covers it alongside `@property`.

```python
# functools_cached_property.py
from functools import cached_property

class Lazy:
    def __init__(self, n: int) -> None:
        self.n = n

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

Note that you must be careful with caching,
because mutating a property doesn't cause the cached result to be recalculated.
The escape hatch is `del x.squared`:
deleting the cached attribute discards the stored value,
and the next access recomputes it from the current state.

### `wraps`

Copies a wrapped function's name and docstring onto its wrapper,
so introspection still sees the original.
[Decorators](14_Decorators.md#decorators-as-classes) covers its sibling,
`update_wrapper()`, for wrapping with a class instance.

```python
# functools_wraps.py
from collections.abc import Callable
from functools import wraps

def trace(func: Callable[[str], str]) -> Callable[[str], str]:
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

### `cmp_to_key`

Wraps an old-style comparator, a function returning negative, zero, or positive,
into a key function `sorted()` can use directly.

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
        return isinstance(other, Weight) and self.kg == other.kg

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
with per-type implementations registered separately.
[Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch)
uses `singledispatch()` as an alternative to the *Visitor* pattern,
including why the registered function below is named `_`.

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

### `singledispatchmethod`

The same dispatch, written as a method so it reads as `self.op(x)` instead of a bare function call.
The registered method below is again named `_`,
explained in [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch).

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

`itertools`, covered next, applies the same idea to lazy iteration.

## The `itertools` Toolkit

`itertools` builds lazy iterators from a small set of composable pieces.
Each one produces values on demand instead of building a list up front.
Each is also a loop you would otherwise write by hand,
already tuned in C and already correct on the edge cases a hand-rolled version tends to miss,
the empty iterable, the single element,
the point where two sequences run out at different lengths.
Combine them the way you combine any small function,
by feeding one's output to the next.
What follows starts with the simplest tools and works up to the ones with the most moving parts.

### `repeat`

Yields the same object over and over, forever or a fixed number of times.

```python
# itertools_repeat.py
from itertools import repeat

print(list(repeat("x", 3)))
#: ['x', 'x', 'x']
```

### `islice`

Slices any iterable, including an infinite one,
the way `[start:stop:step]` slices a list.

```python
# itertools_islice.py
from itertools import islice

print(list(islice(range(10), 2, 8, 2)))
#: [2, 4, 6]
```

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

### `chain`

Iterates several iterables one after another, as if they were one.
`chain.from_iterable(iterables)` does the same when the iterables themselves arrive as one lazy sequence,
rather than as separate arguments.

```python
# itertools_chain.py
from itertools import chain

print(list(chain([1, 2], [3, 4])))
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

### `accumulate`

Yields the running total of an iterable,
or the running result of any two-argument function.

```python
# itertools_accumulate.py
from itertools import accumulate

print(list(accumulate([1, 2, 3, 4])))
#: [1, 3, 6, 10]
```

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

### `dropwhile`

Skips elements while a predicate holds, then yields everything after.

```python
# itertools_dropwhile.py
from itertools import dropwhile

print(list(dropwhile(lambda n: n < 3, [1, 2, 3, 4, 1])))
#: [3, 4, 1]
```

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
pass a distinct sentinel as the `fillvalue` keyword argument:

```python
# itertools_zip_longest.py
from itertools import zip_longest

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]

MISSING = sentinel("MISSING")
print(list(zip_longest([1, 2, 3], [4, 5], fillvalue=MISSING)))
#: [(1, 4), (2, 5), (3, MISSING)]
```

### `groupby`

Groups consecutive elements that share a key.
The input must already be sorted by that key, since it only merges neighbors.

```python
# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
```

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
After `tee()`, use only the returned iterators;
advancing the original source steals values the copies never see.
And `tee()` buffers every value one copy has consumed and the other has not,
so draining `a` completely before touching `b`, as this demo does,
stores the whole sequence anyway.
When one consumer runs far ahead of the other,
`list()` is simpler and no more expensive.
`tee()` wins when the consumers stay roughly in step.

### `product`

The Cartesian product of the input iterables,
the same pairs a nested `for` loop would build,
without writing and re-testing that loop yourself.

```python
# itertools_product.py
from itertools import product

print(list(product("AB", [1, 2])))
#: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
```

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

A `for` loop computes this same factorial in about the same number of lines,
with no risk of hitting that limit.
Recursion is not a faster or shorter way to count down to zero.
Its payoff shows up once the problem branches, not just repeats,
which is shown in the next example.

Recursion suits problems that are naturally self-similar,
such as walking a tree.
Python does not optimize tail calls and limits the call stack,
so deep recursion will raise `RecursionError`.
For long flat sequences,
a loop or one of the `itertools` tools is the better choice.

Recursion is beneficial when the data is recursive.
Code that walks a tree, nested data,
or a directory reads most clearly when its shape matches the data's shape.
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
Writing this as a loop means building your own stack to track which sublists are still open,
and getting the push and pop right at every depth.
The recursive version gets that bookkeeping from the call stack,
which is why it stays three lines instead of growing with every level of nesting you support.

## Lazy Evaluation

*Lazy evaluation* computes a value only when something needs it.
A generator is the canonical example.
It yields one value at a time instead of building a whole list up front.
Combined with `itertools`,
you can describe an infinite sequence and take only the part you use:

```python
# lazy.py
from collections.abc import Iterator
from itertools import count, islice

def squares() -> Iterator[int]:
    for n in count(1):
        print(f"computing square {n}")  # Proves this runs on demand
        yield n * n

# count() is infinite; islice() pulls only what we ask for:
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
Nothing here is a batch.
`squares()` never runs ahead to precompute several values before handing one back.
No sixth `computing square` line appears,
because `islice()` stops asking as soon as it has delivered five.
The [Performance](18_Performance.md)
chapter looks at laziness from the perspective of memory and speed.

Laziness matters most at scale.
A generator pipeline can process a multi-gigabyte file or a live network stream one item at a time,
so memory use doesn't grow with the size of the source.
Stages chain together without building intermediate lists between them,
and a consumer that stops early, such as `any()` or `next()`,
means no upstream work for the items it never reaches.

## Case Study: Pairing Rotations

Here is a recurring practical problem.
Pair up participants for an activity across several rounds,
and avoid repeating a pairing until every possible pairing has had a turn.
This is a good place to see these chapters' ideas working together on one small,
real program instead of one at a time.

The *circle method* solves the pairs-only version exactly,
by direct construction.
Fix one player, arrange the rest in a circle,
and each round pair players sitting across from each other,
then rotate everyone but the fixed player by one seat.
With `n` players that produces `n - 1` rounds where no pair repeats,
which is the best any schedule can do,
since it uses up every one of the `n * (n - 1) / 2` possible pairs exactly once.

None of that trick survives a request for groups of three, four,
or any other size.
The circle method is a closed-form answer to one narrow question,
"how do you 1-factorize a complete graph into perfect matchings,"
and pairs are the only group size where that question has a tidy rotation-based answer.
Scheduling groups of three without repeats is the far harder problem that *Kirkman's schoolgirl problem* poses,
solvable only for specific roster sizes and with no simple formula behind it.
Rather than chase an exact answer that may not exist for a given `students` and `size`,
a general version can settle for a good one:
build each group by always adding whoever its current members have met the fewest times before,
tracked in a running history instead of computed fresh from a round number:

```python
# student_pairs.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice

type Student = str
type Group = tuple[Student, ...]
type Round = list[Group]

def group_rounds(
    students: list[Student], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[Student]] = Counter()
    rng = random.Random(seed)
    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[Student]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                closest = min(pool, key=lambda c: sum(
                    history[frozenset((m, c))] for m in group))
                pool.remove(closest)
                group.append(closest)
            groups.append(group)
        for extra in pool:  # Too few left for a full group of `size`
            roomiest = min(groups, key=lambda g: sum(
                history[frozenset((m, extra))] for m in g))
            roomiest.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
rounds = list(islice(group_rounds(students, 2), len(students)))
for i, grouping in enumerate(rounds[:3]):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
#: 1 [('Di', 'Bo', 'Eve'), ('Cy', 'Ana'), ('Gia', 'Fi')]
#: 2 [('Eve', 'Fi', 'Ana'), ('Bo', 'Gia'), ('Cy', 'Di')]

met = [frozenset(pair) for r in rounds for group in r
       for pair in combinations(group, 2)]
possible = set(map(frozenset, combinations(students, 2)))
print(len(set(met)), "of", len(possible), "pairs met at least once")
#: 21 of 21 pairs met at least once
print(len(met) - len(set(met)), "repeat meetings")
#: 14 repeat meetings

trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]
```

Called with `size=2`,
`group_rounds()` covers all `21` possible pairs across the seven rounds,
at the cost of `14` repeat meetings.
An odd roster cannot pair everyone,
so each round folds the leftover player into an existing pair,
and those triples are where the repeats come from.
It does that with no rotation and no notion of a fixed player,
just a shuffle and a greedy choice repeated until the roster runs out.
Called with `size=3`, the same function schedules trios instead.
Seven students do not split evenly into threes,
so one group grows to four rather than leaving anyone out,
the same join-instead-of-sit-out choice the pair rounds made above.

Generality cost something.
The circle method needed no memory.
Which pair sits where in round `r` followed from `r` alone.
`group_rounds()` needs the `history` `Counter`,
because there is no formula that predicts, from a round number alone,
which grouping of arbitrary size keeps every pair's meeting count lowest.
It is still a pure function in the sense that matters for testing.
The same `students`, `size`,
and `seed` always produce the same infinite sequence of rounds,
since `random.Random(seed)` never reaches outside itself for randomness.
What changed is that computing round `100` now means having already generated rounds `0` through `99`,
where the circle method could compute round `100` directly,
from its arithmetic alone.
That trade, memory for generality, is the same one [Recursion](#recursion)
makes when a loop's simple counter is not enough and the problem needs a stack instead.
