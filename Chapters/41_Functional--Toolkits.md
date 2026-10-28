# Toolkits

> Pure functions are parts,
> and the same few operations on parts recur in every program: fold, cache,
> specialize, chain.
> `functools` and `itertools` supply them, written and tested.

[Functional Foundations](40_Functional--Foundations.md)
builds behavior from small, pure, composable pieces.
`functools` operates on functions.
`itertools` assembles lazy iterators from composable parts.
This chapter tours both toolkits,
then turns to two techniques that pair naturally with them:
lazy evaluation and recursion.
A case study then puts several of the pieces to work on one problem.

## The `functools` Toolkit

The standard library provides the building blocks of functional Python under `functools`.
Each one replaces code you would otherwise write and debug yourself.
Caching logic, an eviction policy,
and a dispatch table each have an edge case that's easy to get wrong on the first attempt.
The library's versions handle those edge cases correctly.
CPython implements in C the tools where speed matters most: `reduce()`,
`partial()`, and the two caches.

What follows starts with the simplest tools and works up to `singledispatch` and `singledispatchmethod`,
which take one registered function per type.

### `reduce`

Folds an iterable into a single value by repeatedly applying a two-argument function.

```python
# functools_reduce.py
from functools import reduce
from operator import or_

print(reduce(or_, [{"a": 1}, {"b": 2}, {"a": 3}], {}))
#: {'a': 3, 'b': 2}
```

`operator.or_()` is `|` as a function.
On two dictionaries `|` is a union that keeps the right operand's value for a key both hold,
so the later `"a": 3` replaces `"a": 1`.
The `operator` module supplies a named function for each operator,
ready to pass to a fold in place of `lambda a, b: a | b`.
A function call has one too.
`operator.call(f, x)` is `f(x)`,
so `map(call, funcs, args)` applies each function in `funcs` to the matching argument in `args`.

For addition, `sum()` is the dedicated built-in,
and `math.prod()` covers multiplication.
`reduce()` is the tool for every other fold, such as this dictionary union.

On an empty iterable `reduce()` raises `TypeError: reduce() of empty iterable with no initial value`,
because it needs an item or a starting value to return.
The third argument, `{}` in the listing, supplies a starting value,
so `reduce(or_, [], {})` returns `{}`.
Since Python 3.14 you can pass the starting value by keyword,
as `reduce(or_, [], initial={})`, so the call names the role of the `{}`.

### `cache`

Stores every result for as long as the function exists,
so a repeated call with the same arguments returns the stored result straight from the cache.
This caching by argument is memoization,
the term [*Singleton*](23_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance)
applies to its cached constructor function.
`@cache` works correctly only for pure functions.
A cached function with side effects runs those effects on the first call with each set of arguments,
and skips them on every repeat.

The cache is a dictionary keyed on the arguments,
so every argument must be hashable.
Passing a `list` raises `TypeError: unhashable type: 'list'`.

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
the cache now holds every value up to and including 30.
The 31 misses are the 31 distinct arguments, `0` through `30`.
The 28 hits are the calls that found a stored answer.
That is fifty-nine calls in all, against 2,692,537 for the undecorated version,
where every branch recomputes the whole subtree beneath it.
[Caching](18_Techniques--Performance.md#caching)
runs both versions side by side.
[Recursion](#recursion) explains why `fib()` keeps its recursive form.

An iterative Fibonacci, `a, b = b, a + b` in a loop,
needs neither recursion nor a cache.
The recursive one stays the running example here because its body is one line and its calls repeat the same arguments,
so the cache's effect shows in the hit count.
The branching and the repeated subproblem matter, not the arithmetic.

One trap: decorating a method with `@cache` keys every entry on `self`,
so the cache holds a strong reference to each instance forever.
That is *Observer*'s [*lapsed listener* leak](30_Patterns--Observer.md#lapsed-listeners)
in cache form.
For the usual case, one slow computation per instance,
use [`@cached_property`](#cached_property).
`@cached_property` stores the result in the instance's `__dict__`,
so the garbage collector frees the result along with the instance.

### `lru_cache`

Like `cache()`, but bounds memory by discarding the least recently used entry once the cache reaches `maxsize`.

```python
# functools_lru_cache.py
from functools import lru_cache

@lru_cache(maxsize=2)
def square(n: int) -> int:
    print(f"computing {n}")
    return n * n

square(1)
#: computing 1
square(2)
#: computing 2
square(3)  # Evicts 1, the least recently used
#: computing 3
square(2)  # [1]
square(1)  # [2]
#: computing 1
print(square.cache_info())
#: CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)
```

Each miss runs the body and prints a `computing` line.
A hit returns the stored result and skips the `print()`,
the skipped side effect the `cache` section describes.
The single hit is the second `square(2)` (`[1]`),
which returns the stored `4` because `2` is still in the cache.
`1` was the first value computed, so the fourth miss, at `[2]`,
proves the cache evicted it.
The cache discards the least recently used entry before it stores a new one,
so `currsize` stays at or below `maxsize`.

Written bare, `@lru_cache` keeps its default `maxsize=128`,
so a function you meant to cache without limit starts evicting at its 129th distinct argument.
`@cache` is `lru_cache(maxsize=None)`, the unbounded form.

### `partial`

Presets some of a function's arguments and returns a new function that expects the rest.
[Partial Application](40_Functional--Foundations.md#partial-application)
covers it in depth.

```python
# functools_partial.py
from functools import partial

shout = partial(print, end="!\n")
shout("hello")
#: hello!
```

[`functools.Placeholder`](40_Functional--Foundations.md#leaving-a-gap-with-placeholder)
reserves a position so you can preset a later positional argument and leave an earlier one for the caller.

### `partialmethod`

The same idea as `partial()`, but for a method.
`partialmethod` returns a descriptor,
which binds `self` automatically when you access the method on an instance.

```python
# functools_partialmethod.py
from functools import partialmethod
from record import record

@record
class Text:
    value: str

    def pad(self, width: int, fill: str = " ") -> str:
        return self.value.rjust(width, fill)

    zero_pad = partialmethod(pad, fill="0")

print(Text("7").zero_pad(3))
#: 007
```

A `partial` object is a descriptor too,
so writing `zero_pad = partial(pad, fill="0")` here works.
`partial` and `partialmethod` differ as soon as an argument is positional.
`partialmethod` passes the instance first and the bound arguments after it,
the order a method expects.
`partial` passes the bound arguments first and the instance after them,
so `partial(pad, 5)` calls `pad(5, instance)` and fails with `AttributeError: 'int' object has no attribute 'value'`.
The type checker reports the mistake before the run.
`pad()`'s first parameter is `self`,
so `partial(pad, 5)` draws `invalid-argument-type`: expected `Text`,
found `Literal[5]`.
Use `partialmethod` inside a class body and `partial` everywhere else.

### `cached_property`

Runs a property's code once, on first access, then reuses the stored result.

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
del x.squared  # [1]
print(x.squared)
#: computing
#: 100
```

The stored result stays when an input changes.
`del x.squared` at `[1]` discards the stored value.
The next access recomputes it from the current state.

A first access from two threads at once is a race.
`cached_property` takes no lock,
so both threads can arrive before either stores a value,
and both run the property's code.

The stored value goes in the instance's `__dict__`, so each instance needs one.
A record uses `__slots__`, which replaces each instance's `__dict__`.
The first access to a `cached_property` on a `@record` raises a `TypeError`,
as `slots_limits.py` in [When Slots Does Not Fit](18_Techniques--Performance.md#when-slots-does-not-fit)
shows.
`Lazy` is a `@dataclass` for that reason, and because the demo assigns to `x.n`.

### `wraps`

Copies a wrapped function's name and docstring onto its wrapper,
so a tool that reads those attributes reports the original.
`@wraps(func)` runs [`update_wrapper()`](14_Techniques--Decorators.md#decorators-as-classes).
A decorator written as a class calls `update_wrapper()` in its `__init__()` to copy the same metadata onto its instance.

```python
# functools_wraps.py
from collections.abc import Callable
from functools import wraps

type StrFn = Callable[[str], str]

def passthrough(func: StrFn) -> StrFn:
    @wraps(func)
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

def bare(func: StrFn) -> StrFn:
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

@passthrough
def greet(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

@bare
def greet_bare(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

print(greet.__name__, "-", greet.__doc__)
#: greet - Say hello.
print(greet_bare.__name__, "-", greet_bare.__doc__)
#: wrapper - None
```

`bare()` is `passthrough()` without the `@wraps(func)` line.
Both decorators return the function they define as `wrapper`,
so `greet` and `greet_bare` each name a wrapper.
For `greet_bare`, `help()` shows the wrapper too,
as does every tool that reads a function's name or docstring.

`wraps()` also sets `greet.__wrapped__` to the original function,
so a tool that needs the original, such as `inspect.signature()`,
can follow that attribute to it.

### `cmp_to_key`

Wraps an old-style comparator into a key function that `sorted()` accepts as its `key` argument.
A comparator takes two values and returns negative, zero, or positive.

```python
# functools_cmp_to_key.py
from functools import cmp_to_key

def larger_first(a: str, b: str) -> int:
    return (b + a > a + b) - (b + a < a + b)

numbers = ["3", "30", "34", "5", "9"]
ordered = sorted(numbers, key=cmp_to_key(larger_first))
print("".join(ordered))
#: 9534330
```

`larger_first()` puts `a` before `b` when `a + b` forms a larger number than `b + a`.
`"3"` goes before `"30"` because `"330"` is larger than `"303"`.
Subtracting one comparison from the other turns the two booleans into the negative,
zero, or positive result a comparator returns.
Joined, the sorted strings form the largest number the five pieces can make.

The rule compares two strings at a time,
so where `"3"` belongs depends on the string beside it.
A per-element key for this order is hard to find.
The comparator states the rule.
When a key function exists, use it,
as in `sorted(words, key=len, reverse=True)`, which orders words by length.
`sorted()` calls a key function once per element and a comparator once per comparison.
`cmp_to_key()` is for a comparator that arrives from older code,
and for an ordering like this one,
where the rule is a comparison between two elements.

### `total_ordering`

Fills in the rest of the comparison methods from `__eq__` and one of `__lt__`,
`__le__`, `__gt__`, or `__ge__`,
so a class writes two methods instead of five and still supports `<`, `<=`, `>`,
and `>=`.

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
print(light <= heavy, light > heavy, light >= heavy)
#: True False False
```

`Weight` is a hand-written class to show the tool.
In real code `Weight` would be `@dataclass(frozen=True, order=True)`,
which generates all five comparison methods from the field order.
`total_ordering` is the right tool when the class cannot be a dataclass,
or when the ordering differs from the fields in declaration order.

Each synthesized comparison is slower than a hand-written one,
because it calls your methods.
The `__le__()` that `total_ordering` supplies for `Weight` calls your `__lt__()`,
then calls `__eq__()` too when `__lt__()` returns `False`.
The `__le__()` that `@dataclass(order=True)` generates returns `(self.kg,) <= (other.kg,)` and calls no other method.

### `singledispatch`

Turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations you register separately.
[*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
uses `singledispatch()` as an alternative to the *Visitor* pattern,
and explains why the registered function below takes the name `_`.

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

`singledispatch()` reads the type of the first positional argument,
so the caller must pass that argument by position.
`describe(value=5)` raises `TypeError: describe requires at least 1 positional argument`.
Because dispatch looks at that one argument alone,
a rule that depends on two types needs [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md).

### `singledispatchmethod`

The same dispatch, written as a method so it reads as `self.op(x)` instead of a bare function call.
Here, the registered method again takes the [placeholder name `_`](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch).

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
not on `self`, so the type of `value` selects the implementation,
just as it does for the plain `describe()` in `functools_singledispatch.py`.

## The `itertools` Toolkit

Each `itertools` function produces values on demand instead of building a list up front.
[Lazy Evaluation](#lazy-evaluation) revisits that property below.
Each is also a loop you would otherwise write yourself.
The `itertools` version of that loop runs as C code in CPython,
and it handles the edge cases a hand-written version can get wrong:
the empty iterable, the single element,
and the point where two sequences run out at different lengths.

Combine `itertools` functions the way you combine any small function,
by passing one's output to the next.
[Reusable Algorithms](22_Patterns--Iterators.md#reusable-algorithms)
introduces several of these as stages in lazy pipelines.
This section is the catalog.

### `repeat`

Yields the same object over and over, forever or a set number of times.

```python
# itertools_repeat.py
from itertools import repeat

print(list(repeat("x", 3)))
#: ['x', 'x', 'x']
print(list(map(pow, range(5), repeat(2))))
#: [0, 1, 4, 9, 16]
```

The counted form replaces the list you would write as `["x"] * 3`.
The infinite form is the reason to import `repeat()`.
It supplies a constant argument for as many calls as `map()` makes,
and it holds one object in memory however many calls receive it.
Here the output stops when `range(5)` runs out,
because `map()` stops at its shortest input.

### `islice`

Slices any iterable, including an infinite one,
the way `[start:stop:step]` slices a list.

```python
# itertools_islice.py
from itertools import islice

it = iter(range(10))
print(list(islice(it, 2, 8, 2)))
#: [2, 4, 6]
print(next(it))
#: 8
```

`islice()` differs from a list slice in two ways.
It rejects negative indices with a `ValueError`,
since a negative index counts back from the end,
and an iterator may have no end.
And it consumes every element it passes.
An iterator you pass to `islice()` resumes where the slice stopped,
so `next(it)` returns `8`.
`islice()` consumed the `7` on its way to the stop index and discarded it.
A list slice leaves the list as it was.

### `count`

Counts up (or down) forever from a start value, with a constant step.

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
so the whole input stays in memory for as long as the `cycle` object exists.

### `chain`

Iterates over several iterables one after another, as if they were one.
`chain.from_iterable(iterables)` does the same when the iterables arrive inside one outer iterable instead of as separate arguments.
It reads that outer iterable lazily, so a generator of iterables works too.
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
in place of hand indexing and the off-by-one errors it invites at the ends.

```python
# itertools_pairwise.py
from itertools import pairwise

print(list(pairwise([1, 2, 3, 4])))
#: [(1, 2), (2, 3), (3, 4)]
```

### `batched`

Groups an iterable into fixed-size tuples,
with a shorter final batch when the length leaves a remainder.
A hand-written loop gets that remainder wrong easily.

```python
# itertools_batched.py
from itertools import batched
from exceptions import expect

print(list(batched(range(7), 3)))
#: [(0, 1, 2), (3, 4, 5), (6,)]
expect(ValueError, list, batched(range(7), 3, strict=True))
#: [ValueError] batched(): incomplete batch
```

A short final batch is normal for pagination and wrong for fixed-width records.
For fixed-width records, `strict=True` raises a `ValueError`.
`zip(strict=True)` under [`zip_longest`](#zip_longest) offers the same choice.

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

`accumulate()` is `reduce()` with the intermediate results kept.
The last value it yields is the value `reduce()` returns.
Like `reduce()`, `accumulate()` accepts a starting value,
through the keyword-only argument `initial`, and yields that value first.
`accumulate([1, 2, 3], initial=10)` yields `10`, `11`, `13`, and `16`.

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

def small(n: int) -> bool:
    return n < 3

data = [1, 2, 3, 4, 1]
print(list(takewhile(small, data)))
#: [1, 2]
print(list(filter(small, data)))
#: [1, 2, 1]
```

The input ends with a `1` to show how `takewhile()` differs from `filter()`.
`filter()` returns `[1, 2, 1]`,
because it skips a failing element and tests the next.
`takewhile()` stops at the first failure, before it reaches the last element.
On finite data the two calls differ in which elements they return.
On an infinite source the difference decides whether the program terminates.
[Reusable Algorithms](22_Patterns--Iterators.md#reusable-algorithms)
works through that case.

### `dropwhile`

Skips elements while a predicate holds, then yields everything after.

```python
# itertools_dropwhile.py
from itertools import dropwhile, filterfalse

def small(n: int) -> bool:
    return n < 3

data = [1, 2, 3, 4, 1]
print(list(dropwhile(small, data)))
#: [3, 4, 1]
print(list(filterfalse(small, data)))
#: [3, 4]
```

The same trailing `1` shows how `dropwhile()` differs from `filterfalse()`.
`dropwhile()` stops testing once the predicate fails,
so it yields the final `1`.
`filterfalse()` tests every element, drops that `1`, and returns `[3, 4]`.

### `filterfalse`

Keeps the elements a predicate rejects, the complement of `filter()`.

```python
# itertools_filterfalse.py
from itertools import filterfalse

print(list(filterfalse(lambda n: n % 2 == 0, range(6))))
#: [1, 3, 5]
```

Since Python 3.14 the `operator` module names the `None` tests,
`is_none()` and `is_not_none()`, so a `None` filter needs no lambda.
`filterfalse(is_none, data)` drops each `None` and keeps a `0` or an empty string,
which `filter(None, data)` discards along with the `None`.

### `starmap`

Like `map()`, but unpacks each element as the arguments to the function.

```python
# itertools_starmap.py
from itertools import starmap

print(list(starmap(pow, [(2, 5), (3, 2)])))
#: [32, 9]
```

`map(pow, [2, 3], [5, 2])` gives the same answer from two parallel iterables,
one per parameter.
`starmap()` is for arguments that arrive paired,
as the tuples `zip()` produces or the rows of a file.

### `zip_longest`

Zips iterables of different lengths,
filling the missing positions instead of stopping at the shortest.
The default filler is `None`.
When `None` is a valid element,
pass a distinct [sentinel](05_Foundations--Functions.md#sentinel-values)
as the `fillvalue` keyword argument:

```python
# itertools_zip_longest.py
from itertools import zip_longest
from exceptions import expect

print(list(zip_longest([1, 2, 3], [4, 5])))
#: [(1, 4), (2, 5), (3, None)]

MISSING = sentinel("MISSING")
print(list(zip_longest([1, 2, 3], [4, 5],
                       fillvalue=MISSING)))
#: [(1, 4), (2, 5), (3, MISSING)]
print(list(zip([1, 2, 3], [4, 5])))  # [1]
#: [(1, 4), (2, 5)]
expect(ValueError, list,  # [2]
       zip([1, 2, 3], [4, 5], strict=True))
#: [ValueError] zip() argument 2 is shorter than argument 1
```

Python offers three ways to zip inputs of different lengths,
and the one you choose records what a mismatch means.
Plain `zip()` (`[1]`) stops at the shortest, drops the `3`,
and raises no exception, the right choice when the extra elements are surplus.
`zip(a, b, strict=True)` (`[2]`) raises a `ValueError`.
`strict=True` is the right choice when equal lengths are an invariant you want checked.
`zip_longest()` pads,
the right choice when the missing elements are data in their own right.

### `groupby`

Groups consecutive elements that share a key.
The input must arrive sorted by that key,
since `groupby()` groups only adjacent elements.

```python
# itertools_groupby.py
from itertools import groupby

data = ["a", "a", "b", "b", "b", "c"]
print([(k, list(g)) for k, g in groupby(data)])
#: [('a', ['a', 'a']), ('b', ['b', 'b', 'b']), ('c', ['c'])]
# [1]
print([(k, list(g)) for k, g in groupby(["b", "a", "b"])])
#: [('b', ['b']), ('a', ['a']), ('b', ['b'])]
# [2]
print([(k, list(g))
       for k, g in groupby(sorted(["b", "a", "b"]))])
#: [('a', ['a']), ('b', ['b', 'b'])]
```

For the unsorted input at `[1]`,
`groupby()` silently returns `"b"` as two separate groups.
Sorting first, at `[2]`, is the fix.
With a key function, pass the same one to both calls,
as in `groupby(sorted(data, key=keyfunc), key=keyfunc)`.
`sorted()` returns a new list and leaves `data` as it was,
so `groupby()` must receive what `sorted()` returns.

Each comprehension's `list(g)` is necessary.
Each group is a view onto the one underlying iterator,
so advancing to the next group empties the previous group's view.
`list(groupby(data))` therefore returns three keys paired with three empty iterators,
because the outer `list()` walks all the way to the end before anything reads a group.
Consume each group before asking for the next one,
as each comprehension in `itertools_groupby.py` does.

### `tee`

Splits one iterable into several independent iterators over the same data,
so two consumers can each walk it once without collecting it into a list first.

```python
# itertools_tee.py
from itertools import tee

a, b = tee([1, 2, 3])
print(list(a), list(b))
#: [1, 2, 3] [1, 2, 3]
source = iter([1, 2, 3])
a, b = tee(source)
next(source)  # [1]
print(list(a), list(b))
#: [2, 3] [2, 3]
```

Two cautions apply.
After `tee()`, use the returned iterators and leave the source alone.
Advancing the original source consumes values that the copies then miss.
The second case advances `source` once at `[1]`, so both copies start at `2`.

The second caution concerns memory.
`tee()` buffers every value one copy has consumed and the other has yet to read.
Each case drains `a` completely before touching `b`,
so `tee()` stores the whole sequence.
When one consumer runs far ahead of the other,
`list()` collects the same values once, and both consumers read that one list.
`tee()` saves memory when the consumers stay roughly in step.

[Iterators](22_Patterns--Iterators.md#what-tee-buffers)
measures `tee()`'s buffering and adds a third caution.
`tee()` shares one unlocked buffer between its branches,
so two threads advancing them at the same time can raise a `RuntimeError`.

### `product`

The Cartesian product of the input iterables,
the same pairs a nested `for` loop builds.

```python
# itertools_product.py
from itertools import product

print(list(product("AB", [1, 2])))
#: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]
```

Unlike the tools above,
`product()` reads its inputs completely before yielding its first tuple,
so every input must be finite.
`product(count(1), "AB")` reads the infinite `count(1)` until memory runs out,
so it yields no tuple.

### `permutations` and `combinations` {#permutations-and-combinations}

Four tools draw `r` elements from an iterable, and two questions separate them:
does order matter, and may an element repeat?
The same input and the same `r` make the answers comparable:

```python
# itertools_selections.py
from itertools import (combinations,
                       combinations_with_replacement,
                       permutations, product)

print(list(permutations("AB", 2)))
#: [('A', 'B'), ('B', 'A')]
print(list(combinations("AB", 2)))
#: [('A', 'B')]
print(list(combinations_with_replacement("AB", 2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'B')]
print(list(product("AB", repeat=2)))
#: [('A', 'A'), ('A', 'B'), ('B', 'A'), ('B', 'B')]
```

`permutations()` counts orderings, so `AB` and `BA` are two results.
`combinations()` treats those as the same draw and keeps one.
Keeping one is right when you want each pair of distinct elements once.
`combinations_with_replacement()` also counts `AB` and `BA` as one draw.
It draws from the full input each time, so `AA` and `BB` appear too.
`product()` with `repeat=` is the fourth combination of answers.
Order matters and elements repeat, so it yields all four pairs.

`math.perm(n, r)` and `math.comb(n, r)` compute how many tuples `permutations()` and `combinations()` yield from `n` elements,
so you can size a draw before you run it.
`math.comb(20, 3)` is `1140`, the number of three-element draws from twenty.
Python 3.15 also groups both under `math.integer`,
a namespace that holds the integer-only functions: `gcd()`, `lcm()`, `isqrt()`,
`factorial()`, `perm()`, and `comb()`.
`math.integer.comb is math.comb` is `True`, so either name works.

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
print(list(islice(squares, 3)))  # [1]
#: [256, 289, 324]
```

Every stage waits for `list()` to pull.
To stop, `takewhile()` pulls one more total,
the 590 from the batch `(169, 196, 225)`, and discards it as over the limit.
That pull consumes squares 13 through 15,
so the `print()` at `[1]` shows the source resuming at `n` = 16.
A pull-based pipeline reads one value further than it keeps,
and here that one value is a batch of three squares.

## Lazy Evaluation

*Lazy evaluation* computes a value only when something needs it.
A generator is the canonical example.
It yields one value at a time, each on request.
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
for sq in islice(squares(), 3):
    print("got", sq)
#: computing square 1
#: got 1
#: computing square 2
#: got 4
#: computing square 3
#: got 9
```

`squares()` yields squares forever, yet the program terminates.
`islice()` requests three values,
so the third `computing square` line is the last.
The output alternates.
Each `computing square N` line appears the moment the loop over `islice()` pulls that value,
and the loop body prints `got` before the generator computes the next square.
An eager function prints every `computing square` line before the first `got`.

`list(squares())[:3]` looks equivalent and is a different program.
It builds the whole list before slicing, so it asks `squares()` for every value.
Because `squares()` has no last value, `list()` keeps asking for more,
printing `computing square` lines and growing its list until memory runs out.
The slice never runs, because `list()` never returns.
Slicing lazily lets the source be infinite.
Slicing a list requires a source that ends.
[Lazy Evaluation with Generators](18_Techniques--Performance.md#lazy-evaluation-with-generators)
looks at the same idea from the perspective of memory and speed.

Laziness matters most at scale.
A generator pipeline can process a multi-gigabyte file or a live network stream one item at a time,
so memory use stays constant whatever the size of the source.
Stages chain together, passing one item at a time between them.
A consumer that stops early, such as `any()` or `next()`,
ends the upstream work at the same point.

## Recursion

*Recursion* expresses a repeated computation as a function that calls itself.
Each recursive function needs a *base case* that stops the recursion and a *recursive case* that moves toward it:

```python
# recursion.py
from exceptions import expect

def factorial(n: int) -> int:
    # Base case stops the recursion:
    if n <= 1:
        return 1
    # Recursive case moves toward the base case:
    return n * factorial(n - 1)

print(factorial(5))
#: 120
expect(RecursionError, factorial, 5000)
#: [RecursionError] maximum recursion depth exceeded
```

A `for` loop computes this same factorial in one stack frame at any `n`.
Python pushes a stack frame for every recursive call,
including one in tail position,
where a language with *tail-call optimization* reuses the caller's stack frame.
The stack has a cap, 1000 frames by default,
so `factorial(5000)` raises a `RecursionError`.
`sys.setrecursionlimit()` raises that limit when the depth is genuine.

A long flat sequence calls for a loop or one of the `itertools` tools.
For a countdown like this one, the loop is as short as the recursion and faster,
since it makes no calls.
Recursion is a better choice if the problem branches rather than repeats,
as `nested_sum.py` shows.

Branching adds a problem of its own.
More than one branch can reach the same subproblem,
and a plain recursive function recomputes it every time.
That recomputation is why the recursive `fib()` under [`cache`](#cache)
gets a decorator rather than a rewrite as a loop.
The recursion states the definition, and the cache removes the repetition.

A tree walk branches too, but each subproblem occurs once,
so a cache would miss on every call.
The reason to recurse there is shape.
Code that walks a tree, nested data,
or a directory can call itself once for each nested level,
so its calls nest the way the data does.
`deep_sum()` adds up one list's integers and calls itself for each nested list:

```python
# nested_sum.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)
        else:
            total += item
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
```

`deep_sum()` states what to do with one element and delegates the nesting to itself.
To write `deep_sum()` as a loop,
you build your own stack to track which sublists are still open,
and you must get the push and pop right at every depth.
In the recursive version the call stack does that bookkeeping.
Each open sublist is a stack frame waiting for its `deep_sum()` call to return.

## Case Study: Pairing Rounds

Pair up participants for an activity across several rounds,
and repeat a pairing only after every possible pairing has occurred once.
A small program solves this scheduling problem by combining several of the chapter's tools:
an infinite generator for the rounds,
`islice()` to take as many of them as you want,
`combinations()` for the pairs inside a group,
and a seeded random source that makes the whole schedule reproducible.

The *circle method* solves the pairs-only version by direct construction.
The method holds one player in place and arranges the rest in a circle.
Each round, it pairs players sitting across from each other,
then rotates everyone but the stationary player by one seat.
For an even number of players `n`,
the circle method produces `n - 1` rounds with no repeated pair.
Those `n - 1` rounds are the longest possible run,
because they use every one of the `n * (n - 1) / 2` possible pairs exactly once.

The classical fix for an odd roster is a phantom player.
Whoever draws the phantom sits out that round.

### Groups of Any Size

The circle method is pairs-only.
It is a closed-form answer to one narrow question:
how do you split every possible pair into rounds in which each player appears exactly once?
Pairs are the only group size where that question has a tidy rotation-based answer.
Groups of three are far harder to schedule so that every pair meets exactly once.
The best-known case is *Kirkman's schoolgirl problem*,
fifteen students walking in threes on seven days.
A perfect trio schedule exists only when the roster size leaves a remainder of 3 when divided by 6,
so seven students have none.

A given `students` and `size` may have no exact answer.
Here, the general version therefore replaces the circle method with a greedy search,
which keeps repeated pairs few rather than ruling them out.
The greedy search builds each group one member at a time,
adding whoever the current members have met the fewest times.
Those meeting counts come from a running history,
updated at the end of every round:

```python
# student_groups.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations

type Student = str
type Group = tuple[Student, ...]
type Round = list[Group]

def group_rounds(
    students: list[Student], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[Student]] = Counter()
    rng = random.Random(seed)

    def met(
        group: list[Student], candidate: Student
    ) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[Student]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                stranger = min(pool,
                               key=lambda c: met(group, c))
                pool.remove(stranger)
                group.append(stranger)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        # Too few left for a full group of `size`
        for extra in pool:
            host = min(groups, key=lambda g: met(g, extra))
            host.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result
```

The first demo schedules eight students in pairs for seven rounds,
the circle method's own case, and counts who met whom:

```python
# pair_rounds.py
from itertools import combinations, islice
from student_groups import group_rounds

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia",
            "Hal"]
rounds = list(islice(group_rounds(students, 2),
                     len(students) - 1))
for i, grouping in enumerate(rounds[:3]):
    print(i, *map("-".join, grouping))
#: 0 Gia-Eve Hal-Bo Di-Fi Ana-Cy
#: 1 Gia-Bo Hal-Ana Cy-Eve Di-Fi
#: 2 Cy-Fi Hal-Eve Bo-Di Ana-Gia

meetings = [*map(frozenset, combinations(group, 2))
            for r in rounds for group in r]
possible = set(map(frozenset, combinations(students, 2)))
distinct = set(meetings)
print(len(distinct), "of", len(possible),
      "pairs met at least once")
#: 26 of 28 pairs met at least once
print(len(meetings) - len(distinct), "repeat meetings")
#: 2 repeat meetings
```

Each round is a shuffle, then a greedy choice repeated until the pool is empty,
in place of the circle method's rotation around a stationary player.

For the same eight students and seven rounds,
the circle method schedules each of the `28` pairs once, with no repeats.
The greedy search picks each partner from the meeting counts so far and plans no later round,
so its seven rounds repeat two meetings and leave two pairs apart.

Trios come from the first seven of those students:

```python
# trio_rounds.py
from itertools import islice
from student_groups import group_rounds

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
trios = list(islice(group_rounds(students, 3), 3))
for i, grouping in enumerate(trios):
    print(i, grouping)
#: 0 [('Gia', 'Eve', 'Cy', 'Fi'), ('Di', 'Bo', 'Ana')]
#: 1 [('Di', 'Eve', 'Bo', 'Gia'), ('Cy', 'Ana', 'Fi')]
#: 2 [('Eve', 'Ana', 'Gia'), ('Bo', 'Fi', 'Di', 'Cy')]
```

Seven students make two threes with one left over, so one group grows to four.
The leftover student joins a group instead of sitting out the round,
the alternative to the circle method's phantom player.

The last case asks for groups of five from a roster of two:

```python
# small_roster.py
from student_groups import group_rounds

print(next(group_rounds(["Ana", "Bo"], 5)))
#: [('Ana', 'Bo')]
```

A roster smaller than one full group is the extreme case of joining instead of sitting out.
Two students and a requested size of five produce one group of two,
because the alternative is a round in which everyone sits out.

In `group_rounds()`,
the `while len(pool) >= size` loop exits at once and leaves `groups` empty.
If you delete the `if pool and not groups` line,
`min()` receives an empty sequence and raises a `ValueError`.

### `history` Is Mutable State

`met()` runs once per candidate per slot,
so it looks like the place for [`@cache`](#cache).
If you add `@cache`, the first call raises a `TypeError`,
because `met()` takes a `list` and a `list` is unhashable.
If you pass a tuple instead, the calls succeed and the schedule gets worse.
The seven rounds `pair_rounds.py` schedules then cover 22 of the 28 pairs instead of 26.
`met()` reads `history`, which changes at the end of every round.
An answer cached in round 0 therefore comes back unchanged in a later round,
after the counts it summed have grown.
Caching `met()` breaks the `cache` entry's rule: pure functions only.
A function that reads mutable state is impure, however simple its body looks.

The general version needs memory, where the circle method needs a round number.
In the circle method, which pair sits where in round `r` follows from `r` alone.
`group_rounds()` needs the `history` `Counter`,
because no formula takes a round number and returns the grouping of arbitrary size that keeps every pair's meeting count lowest.
To reach round `100`,
`group_rounds()` therefore generates rounds `0` through `99` first.
The circle method computes round `100` from its arithmetic alone.
`deep_sum()` in [Recursion](#recursion) needs memory too.
A counter cannot record which sublists are still open,
so the recursive version keeps that state on the call stack,
one stack frame per open sublist.

`group_rounds()` remains deterministic in the sense that matters for testing.
The same `students`, `size`,
and `seed` always produce the same infinite sequence of rounds,
since `random.Random(seed)` draws every number from its own seeded state.

## Choosing From the Toolkits

The first rule applies to both modules: before writing a loop,
ask whether the loop has a name in one of them.
A running total is `accumulate()`, a width-two sliding window is `pairwise()`,
a remainder-safe chunking is `batched()`,
and a cached pure function is `@cache`.
Each of those replaces a small piece of code that works on the first input you try and fails on the empty input,
the single element, or the last partial batch.

The second rule is to stack the pieces,
since most of them take an iterable and return an iterator.
`islice(count(10, 2), 5)` in this chapter is two stages.
A real pipeline is five or six, and it holds only the few items in flight,
however long its source.
[Error Handling](42_Functional--Error_Handling.md)
asks what such a pipeline does when one stage fails.
A chain of pure functions leaves that question open.

## Exercises

Try each exercise before opening its [solution](../Solutions/41_Functional--Toolkits/).

1.  Rewrite `deep_sum()` from `nested_sum.py` without recursion,
    using a list as an explicit stack.
    Compare the two versions for length,
    and name the mistakes the loop version allows that the recursive one cannot make.
2.  `functools_lru_cache.py` prints `CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)`.
    Change `maxsize` to `3`, predict the four numbers before running it,
    then run it and account for any difference.
3.  Write `batch_totals(source, n)`,
    which takes an iterator and yields the sum of each `n`-element batch,
    built only from `itertools` pieces and a generator expression.
    Show that it stays lazy by passing it `count(1)` and taking five values.
4.  `groupby()` on unsorted input silently returns the same key more than once.
    Write `grouped(data, key)` returning a `dict[K, list[V]]` that cannot make that mistake,
    and say what it loses compared with `groupby()`.
5.  Decorate `deep_sum()` with `@cache` and explain the exception.
    What must change about the `Nested` alias for caching to be possible?
6.  `group_rounds()` takes a `seed` and builds its own `random.Random`.
    Replace the `seed` parameter with an `rng: random.Random` parameter.
    Which property of the function does the `rng` parameter preserve,
    and which one does it leave to the caller?
