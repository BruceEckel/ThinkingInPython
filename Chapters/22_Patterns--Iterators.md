# Iterators

> A loop needs the next item, wherever that item is stored.
> An *Iterator* supplies the item and hides the storage.

Code written against an iterator works the same whether the data comes from a list,
a file, a database cursor, or a computation.
It asks only for the next item.
[Design Patterns](21_Patterns--Design_Patterns.md#design-principles)
calls this approach designing the communication, not the parts.
The caller states what it needs and leaves the container's type unnamed.

Python builds iterators into the language.
Any object that follows the *iterator protocol* works with `for`,
comprehensions, `sum()`, `sorted()`, unpacking,
and every function that takes an iterable.

## Iteration Comes Built In

Two methods make up the protocol.
An *iterable* has `__iter__()`, which returns an *iterator*.
An iterator has `__next__()`,
which returns the next item or raises `StopIteration`.
An iterator is also iterable.
Its `__iter__()` returns itself,
so an iterator works anywhere code expects an iterable.
The `for` loop calls these methods, so you rarely call them.
Every container uses this protocol,
so a function written against an iterable stays decoupled from the container.

```python
# basic_iteration.py
nums = [1, 2]
it = iter(nums)  # Called by a for loop
print(iter(nums) is iter(nums))  # [1]
#: False
print(iter(it) is it)  # [2]
#: True
print(next(it), next(it))  # What the loop calls per step
#: 1 2
try:
    next(it)
except StopIteration:
    print("StopIteration ends the loop")
#: StopIteration ends the loop
```

The `is` at `[1]` shows that calling `iter()` on a list creates a new iterator each time.
The `is` at `[2]` shows that calling `iter()` on an iterator returns that iterator.
The tempting call is `next(nums)`, and it fails.
`next()` requires an iterator, and a list has no `__next__()`,
so `next(nums)` raises a `TypeError` at runtime.
The type checker rejects `next(nums)` before the program runs.

A `for` loop makes one `iter()` call,
then calls `next()` until the iterator raises `StopIteration`.
A loop absorbs `StopIteration` as the normal end rather than an error.
Written out, `for x in nums:` is this loop:

```
it = iter(nums)          # Once, before the loop
while True:
    try:
        x = next(it)     # Once per step
    except StopIteration:
        break
    ...                  # The loop body
```

One legacy path bypasses `__iter__()`.
A class is still iterable if it defines `__getitem__()` in place of `__iter__()`,
with `__getitem__()` taking integers from zero.
`iter()` builds an iterator that calls `__getitem__()` with 0, 1, 2, and so on,
until `IndexError`.
Such a class works with `for`,
yet `isinstance(obj, Iterable)` returns `False` and a parameter annotated `Iterable[T]` rejects it.
This legacy path is the one case where a `for` loop accepts an object that fails an `Iterable` annotation.
Write `__iter__()` in new code.

## Generators {#generators}

You rarely write `__iter__()` and `__next__()` yourself.
A *generator* writes them.
A function with a `yield` statement returns an iterator that produces each yielded value in turn.
The generator pauses after each value and resumes with its local variables intact.
[Generators](45_Effects--Generators.md#half-a-coroutine-by-design)
explains where that pause came from and why each `yield` hands control back to the loop that called `next()`.

The generators in this chapter produce values without receiving any,
so `Iterator[T]` annotates them.
That annotation is the short form of a three-part type that also describes what a generator receives and what it returns.
[Generators](45_Effects--Generators.md#annotating-a-generator)
covers the full form, which an Effect system needs.

`fibonacci()` is a generator function.
`Countdown` is a class that becomes iterable because its `__iter__()` is a generator:

```python
# iterators.py
from collections.abc import Iterable, Iterator
from record import record

def fibonacci(n: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

@record
class Countdown:
    start: int

    def __iter__(self) -> Iterator[int]:
        n = self.start
        while n > 0:
            yield n
            n -= 1

def total(numbers: Iterable[int]) -> int:
    return sum(numbers)
```

The demo builds each source and passes it to `total()`:

```python
# iterators_demo.py
from iterators import Countdown, fibonacci, total

print(list(fibonacci(8)))
#: [0, 1, 1, 2, 3, 5, 8, 13]
print(list(Countdown(5)))
#: [5, 4, 3, 2, 1]
print(total(fibonacci(8)))  # Works on a generator
#: 33
print(total([1, 2, 3, 4]))  # and a list
#: 10
print(total(Countdown(5)))  # and a custom iterable
#: 15
```

The figure follows one loop over `nums` through the protocol,
then puts `total()` in the loop's place:

![](_images/iterator_story)

The shaded region in each frame holds what the iterator hides from its caller.
Inside `total()`, `sum()` makes the same `iter()` and `next()` calls as the written-out `for` loop,
so a new source needs no change to `total()`.

The third frame shows a limit of the protocol.
A caller learns that the items have run out by asking for one more.

`fibonacci(8)` returns an iterator, which one pass exhausts.
`Countdown(5)` is an iterable whose `__iter__()` builds a fresh generator for every pass,
so you can iterate over it repeatedly.

The test file confirms that:

- `fibonacci()` produces the expected sequence,
  including the empty and one-item cases.
- `Countdown` counts down to 1, and `list(Countdown(0))` is empty.
- A `Countdown` produces the same values on a second pass.
- `total()` sums a list, a generator, and a `Countdown`.

```python
# test_iterators.py
import pytest
from iterators import Countdown, fibonacci, total

@pytest.mark.parametrize("n, expected", [
    (8, [0, 1, 1, 2, 3, 5, 8, 13]),
    (0, []),
    (1, [0]),
])
def test_fibonacci_sequence(
    n: int, expected: list[int]
) -> None:
    assert list(fibonacci(n)) == expected

def test_countdown_sequence() -> None:
    assert list(Countdown(5)) == [5, 4, 3, 2, 1]
    assert list(Countdown(0)) == []

def test_countdown_is_reiterable() -> None:
    c = Countdown(3)
    assert list(c) == [3, 2, 1]
    assert iter(c) is not iter(c)
    assert list(c) == [3, 2, 1]

def test_total_over_any_iterable() -> None:
    assert total([1, 2, 3, 4]) == 10
    assert total(fibonacci(8)) == 33
    assert total(Countdown(5)) == 15
```

`Fibonacci` produces the same sequence as `fibonacci()`,
with a written-out `__next__()` in place of `yield`:

```python
# fibonacci_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass(eq=False)
class Fibonacci(Iterator[int]):
    remaining: int
    _a: int = field(default=0, init=False)
    _b: int = field(default=1, init=False)

    @override
    def __next__(self) -> int:
        if self.remaining == 0:
            raise StopIteration
        self.remaining -= 1
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        return value

print(list(Fibonacci(8)))
#: [0, 1, 1, 2, 3, 5, 8, 13]
```

The loop is gone.
Its local variables `a` and `b` are the fields `_a` and `_b`,
its `range(n)` counter is `remaining`,
and `__next__()` tests that counter and advances the pair on every call,
because the fields are the one place the position can live between calls.
The generator keeps the loop.
`yield a` suspends it with `a`, `b`, and the position in the `for` loop intact,
and `next()` resumes it after the `yield`.
`eq=False` keeps `object`'s identity comparison,
for the reason [A Type-Checking Iterator](#a-type-checking-iterator) gives.

Generators are lazy.
`fibonacci(1_000_000)` starts computing when you iterate over it,
then produces one value at a time,
so a generator works on streams too large to hold in memory.
Iterating over a generator keeps one value alive at a time,
while collecting the same million values into a list keeps all of them alive at once.
In [Performance](18_Techniques--Performance.md#lazy-evaluation-with-generators),
`lazy_pipeline.py` measures the difference with `tracemalloc`.
The generator pipeline's peak stays under one percent of the list version's peak.

A [generator expression](16_Techniques--Comprehensions.md#generator-expressions)
such as `(i * i for i in range(n))` is the one-line form of a generator,
and it is lazy in the same way.

A generator can be infinite.
A `while True` loop that yields forever, or `itertools.count()`,
produces values on demand with no end.
You take as many as you need with [`itertools.islice()`](#reusable-algorithms),
while a list must hold every value first.

## What Laziness Hides

Laziness has two surprising consequences, and both are silent:

```python
# generator_lifecycle.py
from collections.abc import Iterator

def squares(n: int) -> Iterator[int]:
    print("first next() reached the body")
    for i in range(n):
        yield i * i

sq = squares(6)  # Body not executed
print("created")
#: created
print(next(sq))
#: first next() reached the body
#: 0
print(list(sq))  # The values that are left
#: [1, 4, 9, 16, 25]
print(list(sq))  # Exhausted: empty, and no error
#: []
```

### The Body Waits for the First `next()`

The `print()` at the top runs once,
when the first `next()` call requests a value.
Each later `next()` resumes the body just after the `yield` instead of restarting it.

Any validation at the top of a generator also waits for the first `next()`.
A check meant to reject a bad argument raises its exception at the first `next()`,
far from the call that passed the bad argument.

`lazy_squares()` shows the delay.
`squares()` removes the delay by being a plain function.

```python
# eager_validation.py
from collections.abc import Iterator
from exceptions import expect

def lazy_squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    for i in range(n):
        yield i * i

gen = lazy_squares(-1)
print("no error yet")
#: no error yet
expect(ValueError, next, gen)
#: [ValueError] n must not be negative: -1

def squares(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError(f"n must not be negative: {n}")
    def produce() -> Iterator[int]:
        for i in range(n):
            yield i * i
    return produce()

# The check runs now, not at first next():
expect(ValueError, squares, -1)
#: [ValueError] n must not be negative: -1
```

`lazy_squares()` contains a `yield`,
so the call `lazy_squares(-1)` runs none of its body.
`squares()` has no `yield`, so calling it runs the check immediately.
Only `produce()` waits.

### An Exhausted Generator Is Silently Empty

The second surprise in `generator_lifecycle.py` is its second call to `list(sq)`.
An exhausted generator answers every `next()` with `StopIteration`,
which `list()` absorbs as the normal end.
No exception reports the bug.

When you must walk data twice, collect it into a list once,
or hand out an iterable like `Countdown` in `iterators.py`,
whose `__iter__()` builds a fresh generator for every pass.

Laziness and single use are separate properties.
`Countdown` is as lazy as the generator its `__iter__()` builds,
yet it supports repeated passes, because each pass gets a fresh iterator.
`range()` works the same way.
One `range` object can drive loop after loop.
The iterator runs out, not the iterable that made it.

An `Iterable[T]` annotation gives no warning,
because it describes a list and a half-spent generator equally well.
A function that walks its argument twice therefore type-checks and then returns a wrong answer on the second pass:

```python
# walked_twice.py
from collections.abc import Collection, Iterable, Iterator

def gen(n: int) -> Iterator[int]:
    yield from range(n)

def twice_iterable(xs: Iterable[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)

def twice_collection(
    xs: Collection[int]
) -> tuple[int, int]:
    return sum(xs), sum(xs)

# Type checker sees nothing wrong
print(twice_iterable(gen(3)))
#: (3, 0)
# The same values, in a list
print(twice_iterable([0, 1, 2]))
#: (3, 3)
```

The two calls differ in the argument alone,
so the `(3, 0)` comes from the spent generator.

When a function iterates over its argument more than once,
say so in the signature with `Collection[T]` or `Sequence[T]`.
Beyond `__iter__()`, both types require `__len__()` and `__contains__()`,
which no generator has.
The type checker therefore flags the generator at the call,
before the function runs and returns a wrong answer.
On `twice_collection(gen(3))` it reports an `invalid-argument-type`:
expected `Collection[int]`, found `Iterator[int]`.
The listing leaves that call out, because every chapter listing must type-check.
`total()` in `iterators.py` stays `Iterable[int]` because it sums once.

`Collection[T]` also rejects `Countdown`, which supports any number of passes.
`Countdown` defines `__iter__()`,
while a `Collection` also requires `__len__()` and `__contains__()`.
A reiterable class passes `Collection[T]` by adding those two methods.
`collections.abc` has no protocol for "iterable more than once,"
so `Collection[T]` is the closest annotation.

### What `tee()` Buffers

`itertools.tee(it, 2)` splits one iterator into two independent ones.
`tee()` looks like a third way to walk data twice,
but it saves memory over a list only when the two branches advance together:

```python
# tee.py
from itertools import tee
from typing import Final
from benchmark import report, traced

# Two independent branches, one source
a, b = tee(i * i for i in range(5))
print(list(a), list(b))
#: [0, 1, 4, 9, 16] [0, 1, 4, 9, 16]

N: Final[int] = 100_000
first, second = tee(i * i for i in range(N))
with traced() as buffered:
    for _ in first:  # Drain first; second waits
        pass
with traced() as listed:
    collected = [i * i for i in range(N)]
report(tee_bytes=buffered.current,
       list_bytes=listed.current)
print(f"tee held as much as the list: "
      f"{buffered.current > listed.current * 0.9}")
#: tee held as much as the list: True

# Same N, but both branches advance together:
first2, second2 = tee(i * i for i in range(N))
with traced() as lockstep:
    for _ in zip(first2, second2, strict=True):
        pass
report(lockstep_bytes=lockstep.peak)
print(f"lockstep buffered far less: "
      f"{lockstep.peak < listed.current * 0.1}")
#: lockstep buffered far less: True
```

Both branches see all five squares,
so `tee()` delivers the second pass the generator could not.
Each `with traced()` block measures the memory its body allocates,
using the helper from [Numbers on Your Machine](18_Techniques--Performance.md#numbers-on-your-machine).
`current` is what the block leaves allocated,
and `peak` is the most it held at once.
`tee()` buffers every item the leading branch consumes until the trailing branch catches up.
When `first` drains while `second` waits,
the buffer therefore holds the whole stream.
That buffer uses as much memory as a list,
and the `buffered.current > listed.current * 0.9` comparison confirms it
(one machine measured 4,096,384 bytes buffered against 4,000,672 for the list).
The last block advances `first2` and `second2` together,
one `zip()` step at a time, so `tee()` buffers at most the gap between them.
Use `tee()` when two branches advance together,
not when one finishes before the other starts.

The branches of one `tee()` call also belong in a single thread.
They share one buffer with no lock,
so two threads advancing them at the same time can raise a `RuntimeError`.
[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
covers `threading.concurrent_tee()`, the thread-safe version,
along with what two threads get when they call `next()` on the same unguarded iterator:
duplicate items from a class iterator, and a `ValueError` from a generator.

## Delegating with `yield from`

A generator can delegate part of its work to another iterator using `yield from`.
`yield from` yields every value that iterator produces, in turn,
as if the outer generator had written the loop:

```python
# yield_from.py
from collections.abc import Iterator, Sequence

type Nested = int | Sequence[Nested]

def flatten_loop(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            # Spelled out
            for x in flatten_loop(item):  # noqa: UP028
                yield x

def flatten(nested: Sequence[Nested]) -> Iterator[int]:
    for item in nested:
        if isinstance(item, int):
            yield item
        else:
            # The same loop, delegated
            yield from flatten(item)
```

Both functions flatten the same nested list, with the same result:

```python
# yield_from_demo.py
from collections.abc import Sequence
from yield_from import Nested, flatten, flatten_loop

data: Sequence[Nested] = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten(data)))
#: [1, 2, 3, 4, 5, 6, 7]
print(list(flatten_loop(data)) == list(flatten(data)))
#: True
```

`flatten_loop()` carries a `# noqa` because of ruff's `UP028` rule.
That rule reports a `for` loop whose body is a lone `yield` of the loop variable,
and tells you to write `yield from` instead.

The two forms agree for a generator that yields values and returns `None`,
as `flatten()` does.
The `yield from` expression, however, has a value.
`result = yield from inner()` binds the value `inner()` returned when it stopped.
The hand-written loop drops that value.
`yield from` also forwards `send()` and `throw()` into the inner generator.
The hand-written loop forwards neither.
[Generators](45_Effects--Generators.md#yield-from-composes-descriptions)
uses all three channels: the yielded values, the return value, and `send()`.
The same section shows `yield from` relaying `throw()` and `close()` to the innermost generator.

`test_flatten()` runs `flatten()` and `flatten_loop()` over the same inputs and expects the same flat list from each:

```python
# test_yield_from.py
from collections.abc import Callable, Iterator, Sequence
import pytest
from yield_from import Nested, flatten, flatten_loop

type Flattener = Callable[[Sequence[Nested]], Iterator[int]]

@pytest.mark.parametrize("flatten_with",
                         [flatten, flatten_loop])
@pytest.mark.parametrize("nested, expected", [
    ([1, [2, 3], [4, [5, 6]], 7], [1, 2, 3, 4, 5, 6, 7]),
    ([1, 2, 3], [1, 2, 3]),
])
def test_flatten(
    flatten_with: Flattener,
    nested: Sequence[Nested], expected: list[int]
) -> None:
    assert list(flatten_with(nested)) == expected
```

## Reusable Algorithms

The standard library's `itertools` module contains the generic iterator algorithms `chain()`,
`islice()`, `groupby()`, `takewhile()`, and more.
Each of these consumes iterables and produces iterators.
Combine them with [generator expressions](16_Techniques--Comprehensions.md#generator-expressions)
such as `(x * x for x in data if x > 0)` to build pipelines that stay lazy end to end.
Each stage pulls one item at a time,
so a pipeline over an infinite source ends when a later stage stops pulling:

```python
# reusable_algorithms.py
from itertools import count, islice, takewhile

numbers = count(1)  # Infinite: 1, 2, 3, ...
# The generator expression squares the odd numbers, lazily:
odd_squares = (n * n for n in numbers if n % 2)
print(list(islice(odd_squares, 5)))  # Take the first five
#: [1, 9, 25, 49, 81]

# takewhile() stops when its condition fails:
print(list(takewhile(lambda s: s < 50,
                     (n * n for n in count(1)))))
#: [1, 4, 9, 16, 25, 36, 49]
```

Each stage runs when `list()` pulls a value.
`islice()` and `takewhile()` decide when to stop,
so the infinite `count(1)` produces as many values as they pull.

`islice()` is also how you slice an iterator.
A generator defines no `__getitem__()`,
so the list habit `odd_squares[:5]` raises a `TypeError` instead.

[Functional Toolkits](41_Functional--Toolkits.md#the-itertools-toolkit)
covers `chain()` and `groupby()` in full,
including why `groupby()` needs sorted input.

Choose `takewhile()` deliberately.
Its lookalike is the `if` clause of a generator expression (or `filter()`).
The two behave differently with an infinite source.
The `if` version skips nonmatching values but keeps looking,
so once values stop matching, a `list()` around it runs forever.
`takewhile()` stops at the first failure.
On finite data whose values stop matching for good, as the rising squares do,
skipping and stopping give the same result.
On infinite data of that kind, `takewhile()` finishes.
The `if` clause runs forever.

A test can demonstrate that difference, but not by writing `list(count(1))`.
That call runs forever, and so does the test.
`counter()` stands in for `count(1)`.

```python
# test_endless.py
from collections.abc import Iterator
from itertools import count, islice, takewhile
from typing import Final
import pytest

LIMIT: Final[int] = 1000

class Tripwire(Exception):
    pass

def counter(limit: int) -> Iterator[int]:
    for n in count(1):
        if n > limit:
            raise Tripwire(
                f"pulled {limit} values and kept asking")
        yield n

def test_list_keeps_pulling_from_an_infinite_source(
) -> None:
    with pytest.raises(Tripwire):
        list(counter(LIMIT))

def test_the_if_clause_skips_but_never_stops() -> None:
    small = (n for n in counter(LIMIT) if n < 3)
    with pytest.raises(Tripwire):
        list(small)

def test_takewhile_stops_at_the_first_failure() -> None:
    assert list(takewhile(lambda n: n < 3,
                          counter(LIMIT))) == [1, 2]

def test_islice_stops_after_its_count() -> None:
    assert list(islice(counter(LIMIT), 3)) == [1, 2, 3]
```

`test_list_keeps_pulling_from_an_infinite_source()` is `list(count(1))` with a stopping point built into the source.
In `test_the_if_clause_skips_but_never_stops()`,
every value after `2` is 3 or more,
yet the generator expression keeps pulling from `counter()` to find another match,
until `counter()` raises the same `Tripwire`.

Failing at 1,000 values models how a real program fails.
A real program hangs, or it dies when it exhausts memory.

No tool in the toolchain reports `list(count(1))`.
The type checker accepts it,
because no type checker can read the code and decide whether an iterator ever ends.
A generator built from `while True` has the same type as a finite one,
`Iterator[T]`.
`ruff` accepts it too, with every one of its rules enabled.
The one rule that applies here is `C416`, a comprehension check.
It offers to rewrite `[n for n in count(1)]` as `list(count(1))`,
the same problem with fewer characters.

## A Type-Checking Iterator

Applied to an iterator,
the [*Decorator* Pattern](14_Techniques--Decorators.md#the-decorator-pattern)
wraps the existing iterator and produces a new one with the same interface and added behavior.
Here, the wrapper checks every item against an expected type and raises a `TypeError` on a mismatch:

```python
# typed_iterator.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import override

@dataclass(eq=False)
class TypedIterator[T](Iterator[T]):
    source: Iterator[object]
    expected: type[T]
    # State a generator cannot expose
    accepted: int = field(default=0, init=False)

    @override
    def __next__(self) -> T:
        item = next(self.source)
        if not isinstance(item, self.expected):
            raise TypeError(
                f"TypedIterator for {self.expected} "
                f"encountered {type(item).__name__}")
        self.accepted += 1
        return item
```

`collections.abc.Iterator` supplies `__iter__()` to its subclasses,
so `TypedIterator` defines `__next__()` and inherits `__iter__()`.

The `dataclass` decoration carries `eq=False`.
A data class that generates `__eq__()` sets `__hash__` to `None`,
so such a wrapper, unlike a built-in iterator or a generator,
cannot go in a set or serve as a dict key.
Field-by-field comparison is also the wrong question to ask about an iterator.
Two wrappers over one source compare equal as soon as their counts agree,
though each has delivered different items.
Two wrappers over separate iterators of the same list compare unequal.
With `eq=False`, the wrapper keeps `object`'s identity-based `__eq__()` and `__hash__()`,
as other iterators do.

A generator can wrap an iterator and check each item, in fewer lines:

```python
# typed_generator.py
from collections.abc import Iterable, Iterator

def typed[T](
    items: Iterable[object], expected: type[T]
) -> Iterator[T]:
    for item in items:
        if not isinstance(item, expected):
            raise TypeError(
                f"expected {expected}, "
                f"got {type(item).__name__}")
        yield item
```

Both wrappers deliver `int` items unchanged.
Handed a `str`, `typed()` raises a `TypeError`:

```python
# typed_demo.py
from exceptions import expect
from typed_generator import typed
from typed_iterator import TypedIterator

checked = TypedIterator(iter([1, 2, 3]), int)
print(next(checked), next(checked))
#: 1 2
print(checked.accepted)  # Read mid-stream
#: 2
print(list(typed([1, 2, 3], int)))
#: [1, 2, 3]
expect(TypeError, list, typed([1, "two"], int))
#: [TypeError] expected <class 'int'>, got str
```

Use the class when the wrapper needs its own state or extra methods,
such as `accepted` in `typed_iterator.py`, and use the generator otherwise.
`typed_demo.py` reads `accepted` mid-stream,
while a generator's local variables stay hidden from its caller.
Either way, the wrapper works with every function that takes an iterator,
because every such function calls `iter()` and `next()`,
and both wrappers support those calls.

The two wrappers' inputs differ, though.
`typed()` takes an `Iterable[object]`, so a list is fine.
`TypedIterator` calls `next()` on what it stores,
so it needs an `Iterator[object]`.
Write `TypedIterator(iter(items), int)`, not `TypedIterator(items, int)`.
The type checker rejects the second form.

Both take `expected: type[T]`,
so the type checker infers the element type from the `expected` argument.
`typed(items, int)` is an `Iterator[int]`, not an `Iterator[Any]`.

`expected` must be a class such as `list`.
The type checker accepts a parameterized generic such as `list[int]` as readily as `list`,
but `isinstance()` raises a `TypeError` when it receives one,
so either wrapper fails at the first item.

Each test passes a list of `int` through one wrapper and gets it back unchanged,
then expects a `TypeError` once a `str` appears:

```python
# test_typed.py
import pytest
from typed_generator import typed
from typed_iterator import TypedIterator

def test_typed_generator_passes_and_rejects() -> None:
    assert list(typed([1, 2, 3], int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(typed([1, "two", 3], int))

def test_typed_iterator_passes_and_rejects() -> None:
    assert list(TypedIterator(iter([1, 2, 3]),
                              int)) == [1, 2, 3]
    with pytest.raises(TypeError):
        list(TypedIterator(iter([1, "two", 3]), int))
```

## The Pattern That Disappeared

*GoF Design Patterns* gives *Iterator* a class of its own,
with separate methods to start a traversal, advance it,
test whether it has finished, and read the current item.
It names them `First()`, `Next()`, `IsDone()`, and `CurrentItem()`.
Nothing in this chapter looks like that.
Those four methods [dissolved](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
into two: `__iter__()` and `__next__()`.
The language calls both on your behalf.

### `first()` and `current_item()` Rebuild the List

Written in Python, the four GoF *Iterator* methods show what `first()` and `current_item()` require from a source.
The listing renames GoF's `Next()` to `advance()`,
to keep the name distinct from Python's `next()`.
Over a list the four are unremarkable: `first()` resets an index,
`is_done()` compares it to `len()`,
and `current_item()` reads at the index and leaves the index where it is.
Over a generator, writing all four means keeping everything the traversal has seen:

```python
# gof_iterator.py
from collections.abc import Iterable, Iterator
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        # Every item the traversal has read
        self.seen: list[T] = []
        self.index = 0

    def first(self) -> None:
        self.index = 0  # Rewinds into seen, not into source

    def advance(self) -> None:
        self.index += 1

    def is_done(self) -> bool:
        while len(self.seen) <= self.index:
            item = next(self.source, DONE)
            if item is DONE:
                return True
            self.seen.append(item)
        return False

    def current_item(self) -> T:
        return self.seen[self.index]

def traverse(it: GoFIterator[int]) -> list[int]:
    out: list[int] = []
    while not it.is_done():
        out.append(it.current_item())
        it.advance()
    return out

stream = OverStream(x * 2 for x in [1, 2, 3])
print(traverse(stream))
#: [2, 4, 6]
stream.first()
# A second pass, from a spent generator
print(traverse(stream))
#: [2, 4, 6]
print(stream.seen)
#: [2, 4, 6]
```

`traverse()` is the loop a GoF caller writes.
It drives any type with those four methods,
because `GoFIterator` is a [protocol](20_Patterns--Rethinking_Objects.md#protocols)
rather than a base class.

The `seen` list makes the rewind in `first()` possible.
`is_done()` pulls with `next(self.source, DONE)`.
Given a second argument,
`next()` returns that argument when the source runs out,
in place of raising `StopIteration`.
`current_item()` then indexes `seen` instead of calling `next()` on the source,
so reading a value leaves the position where it was.
Supporting the four methods takes more than a small lookahead buffer.
`OverStream` rebuilds the list.

The GoF interface hides that rebuild.
`first()` and `current_item()` require a collection you can re-read and inspect in place,
so implementing them over a stream means recreating one, item by item.
The same rebuild appears twice more: in `tee()`'s buffer,
and in the list you collect when you must walk data twice.
Python dropped `first()` and `current_item()` rather than make every iterator buffer its stream.
With those two gone, `advance()` returns the value it reached.
That method is `__next__()`.

### Asking Consumes an Item

A GoF iterator's `is_done()` reports whether the traversal has finished and leaves the position where it was,
however often you call it.
Python puts that test inside `__next__()`,
so finding out whether the iterator has finished means requesting the next item.
`__next__()` reports the end by raising `StopIteration`,
which the `for` loop absorbs on your behalf.
You can catch that exception yourself,
or hand `next()` a default to return at the end.
Either way, the call that tests for the end consumes an item,
where the GoF *Iterator*'s `is_done()` leaves every item in place:

```python
# asking_consumes.py
DONE = sentinel("DONE")

numbers = iter([1, 2])
print(next(numbers, DONE), next(numbers, DONE),
      next(numbers, DONE))
#: 1 2 DONE
letters = iter("abcd")
# A membership test consumes too:
print("c" in letters, list(letters))
#: True ['d']
```

`"c" in letters` pulls items until it finds a match,
and consumes the match along with every item before it.

Every protocol operation that looks ahead also advances the iterator.
That is why a peekable iterator must buffer,
and why `tee()` buffers the whole stream in `tee.py` when one branch drains first.

`DONE` is a [sentinel](05_Foundations--Functions.md#sentinel-values),
because the default must differ from every value the source could yield.
With `None` as the default,
an exhausted source and a source that yields `None` produce the same return value.
The built-in `iter()` uses a sentinel the same way in its two-argument form.
`iter(callable, DONE)` calls `callable` until `callable` returns `DONE`.

Two generators double the items of a stream,
one calling a bare `next()` and one letting a `for` loop call it:

```python
# escaped_stop.py
from collections.abc import Iterator
from exceptions import expect

def doubled(source: Iterator[int]) -> Iterator[int]:
    # The exception escapes when the source runs out:
    while True:
        yield next(source) * 2

expect(RuntimeError, list, doubled(iter([1, 2])))
#: [RuntimeError] generator raised StopIteration

def doubled_ok(source: Iterator[int]) -> Iterator[int]:
    for n in source:  # The loop absorbs the exception
        yield n * 2

print(list(doubled_ok(iter([1, 2]))))
#: [2, 4]
```

A `StopIteration` that escapes a generator body becomes a `RuntimeError`
([PEP 479](https://peps.python.org/pep-0479/)),
so the ordinary end of the source propagates out of `list()` as an error.
Only a bare `next()` raises `StopIteration` into your code.
With a default, `next()` returns the default.
Every other construct here absorbs the exception.

`yield from source` stops delegating when the source runs out.
It passes each value through unchanged, though,
so per-item work such as doubling needs a loop.
That is why `doubled_ok()` uses `for`.
The fix is rarely a `try`.
Let a `for` loop call `next()`.

## The Protocol Answers Nothing

Both surprises in [What Laziness Hides](#what-laziness-hides)
come from the same rule.
The only way to find out whether the body accepts its arguments is to pull a value and let the body run.
The only way to find out whether the source has run out is to pull and receive `StopIteration`.
`for` and `list()` catch that second answer and stop,
so an exhausted source and an empty one produce identical output.
The protocol answers only after a pull,
and it passes each value on as it arrives.
Each tool in this chapter that answers in advance holds a buffer to give that answer:
`tee()`, `OverStream`, and a `Peekable` wrapper (see exercise 8).

## Exercises

Try each exercise before opening its [solution](../Solutions/22_Patterns--Iterators/).

1.  Write a generator `evens(n)` that yields the first `n` even numbers,
    and confirm `total()` from `iterators.py` sums them without modification.
2.  Rewrite `Countdown` to also support `len()`,
    then explain why a generator cannot.
3.  Use `itertools.islice()` to take the first 10 values of `fibonacci(1_000_000)` without computing the rest.
4.  `generator_lifecycle.py` returns an empty list on its second pass.
    Fix the caller two ways: collect into a list once and reuse it,
    then instead convert `squares()` into a `Countdown`-style iterable class whose `__iter__()` builds a fresh generator.
    Which fix would you choose for a stream of a million items, and why?
5.  `tee.py` measures two extremes: one branch drained before the other starts,
    and both branches in lockstep.
    Measure what lies between them.
    Advance one branch `k` items ahead of the other,
    then walk both together so the leading branch stays `k` items ahead.
    Predict how the buffer grows with `k` before you measure it,
    then measure it for two values of `k` with `traced()`, as `tee.py` does,
    and explain the result using the rule in [What `tee()` Buffers](#what-tee-buffers).
6.  The prose pairs the generator expression's `if` clause with `filter()`,
    but no test covers `filter()`.
    Add one to `test_endless.py`,
    and say which existing test it should resemble.
7.  `gof_iterator.py` shows only the stream version.
    Write `OverSequence` over a `Sequence[T]`,
    confirm `traverse()` drives it with no changes to `traverse()`,
    and explain why it needs no `seen` list.
    Then build an `OverStream` over `itertools.count(1)`.
    `traverse()` runs forever on an infinite source,
    so drive the four methods yourself for 50,000 steps and report `len(stream.seen)`.
    What has `first()` cost you on an infinite source?
8.  Write `peek(it)` that reports an iterator's next value without consuming it.
    You cannot, so write a `Peekable` wrapper that can,
    and name what it stores that a bare iterator does not.
9.  `flatten()` recurses on anything that is not an `int`.
    Call it on `[1, "ab", 2]` and explain the `RecursionError` you get,
    given that a one-character string is still a `Sequence`.
    Then fix `flatten()` so a `str` yields as one item,
    and say what the same fix looks like in `flatten_loop()`.
10. `typed()` raises a `TypeError` on the first item of the wrong type,
    which ends the stream.
    Write `typed_skipping()`, which drops mismatched items and keeps going,
    then say which of the two you would want wrapping a parsed log file,
    and why.
    Which one is easier to write as `TypedIterator`?
