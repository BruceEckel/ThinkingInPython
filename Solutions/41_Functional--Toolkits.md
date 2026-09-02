# Toolkits: Solutions

## 1. `deep_sum()` with an explicit stack

```python
# exercise_1.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    stack: list[Nested] = list(items)
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item)
        else:
            total += item
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
```

The loop version runs a line longer than the recursive one, so brevity
is not the argument either way. What changed is how much of the
bookkeeping is yours. The recursive version never names a stack: the
call stack holds the sublists still to walk, and `return` pops one.
Here you allocate the stack, seed it with a copy of `items`, choose
`pop()` over `pop(0)`, and choose `extend()` over `append()`.

Three of those choices are places to be wrong. Seeding with `items`
instead of `list(items)` mutates the caller's list as the loop drains
it. Using `append()` where `extend()` belongs pushes the sublist as
a single element and loops forever on it. Using `pop(0)` still gives
the right total but walks the structure breadth-first, a different
order from the recursive version's. That order would matter the moment
the function did anything order-dependent. The recursive version
cannot make any of these mistakes, because it never has the choice.

## 2. `lru_cache` with `maxsize=3`

```python
# exercise_2.py
from functools import lru_cache

@lru_cache(maxsize=3)
def square(n: int) -> int:
    return n * n

square(1)
square(2)
square(3)
square(2)
square(1)
print(square.cache_info())
#: CacheInfo(hits=2, misses=3, maxsize=3, currsize=3)
```

The prediction: `hits=2, misses=3, maxsize=3, currsize=3`. Three
distinct arguments arrive, so the cache misses three times and keeps
all three results. Nothing is ever evicted, so the repeat calls to
`square(2)` and `square(1)` both find their stored answers.

The difference from the chapter's `maxsize=2` run is the second
`square(1)`. Under `maxsize=2` that call was a fourth miss, because
computing `square(3)` had pushed `1` out to make room. One extra slot
converts that miss into a hit, and that conversion is the whole of
what `maxsize` controls. With three slots the cache never evicts
anything, so the chapter listing's comment, "Evicts 1, the least
recently used," stops being true here.

## 3. `batch_totals()` stays lazy

```python
# exercise_3.py
from collections.abc import Iterable, Iterator
from itertools import batched, count, islice

def batch_totals(source: Iterable[int],
                 n: int) -> Iterator[int]:
    return (sum(b) for b in batched(source, n))

print(list(islice(batch_totals(count(1), 3), 5)))
#: [6, 15, 24, 33, 42]
```

`batched()` does the chunking and a generator expression does the
summing, so the body fits on one line with no hand-written loop.

Passing `count(1)` is the proof of laziness. `count()` never ends, so
if `batch_totals()` built a list of batches, or if `batched()` read
its source eagerly, the call would never return. The call returns
immediately, and `islice()` then pulls exactly five totals, so
`count()` yields exactly fifteen integers in all. The first total is
`1 + 2 + 3`, and each later one is nine larger, since every batch
advances the source by three.

## 4. `grouped()` cannot repeat a key

```python
# exercise_4.py
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable

def grouped[V, K: Hashable](
    data: Iterable[V], key: Callable[[V], K]
) -> dict[K, list[V]]:
    out: defaultdict[K, list[V]] = defaultdict(list)
    for item in data:
        out[key(item)].append(item)
    return dict(out)

print(grouped(["b", "a", "b"], str.upper))
#: {'B': ['b', 'b'], 'A': ['a']}
```

A dictionary key exists once by construction, so the duplicate-key
failure `groupby()` has on unsorted input cannot occur. The two `"b"`
entries land in the same list no matter how far apart they arrive, and
the caller needs no `sorted()` call to make that happen.

The cost is everything `groupby()` was buying. `grouped()` reads the
whole input before returning anything, so an infinite source makes it
loop forever, and a finite one sits entirely in memory. `groupby()`
yields each group as it arrives and keeps only the current one, which
is why it can stream a file larger than memory. It also preserves the
input's order, while `grouped()` reports groups in first-appearance
order and loses the interleaving between them. Sorting first to make
`groupby()` safe costs the same memory as `grouped()`, plus the sort,
so `grouped()` is the better answer whenever the input already fits in
memory.

## 5. `@cache` on `deep_sum()`

```python
# exercise_5.py
from functools import cache

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    return 0

try:
    deep_sum([1, [2, 3]])  # type: ignore
except TypeError as e:
    print(f"{type(e).__name__}: {e}")
#: TypeError: unhashable type: 'list'
```

`cache` stores results in a dictionary keyed on the arguments, so
every argument has to be hashable. A `list` is not hashable, because
its contents can change after the cache stores it, and a mutated key
would no longer hash to the slot holding its entry. The call fails
before `deep_sum()`'s body runs at all.

For caching to be possible, `Nested` would have to describe an
immutable structure: `type Nested = int | tuple[Nested, ...]`, with
the parameter annotated `tuple[Nested, ...]` rather than
`list[Nested]`. Tuples hash by contents, and their contents cannot
change, so a tuple meets both conditions a cache key needs. That is
the same requirement the chapter's `cache` entry states as "`@cache`
works correctly only for pure functions," seen from the key's side
rather than the function's.

Note that the exception says nothing about purity. `deep_sum()` is
already pure, and caching it would be correct. The obstacle is the
argument type alone.

## 6. Injecting the random source

```python
# exercise_6.py
import random
from collections.abc import Iterator

def group_rounds(
    students: list[str], size: int, rng: random.Random
) -> Iterator[list[tuple[str, ...]]]:
    while True:
        pool = list(students)
        rng.shuffle(pool)
        yield [tuple(pool[i:i + size])
               for i in range(0, len(pool), size)]

students = ["Ana", "Bo", "Cy", "Di"]
first = next(group_rounds(students, 2, random.Random(0)))
second = next(group_rounds(students, 2, random.Random(0)))
print(first == second)
#: True
```

What the `rng` parameter preserves is determinism. Two callers who
pass `random.Random(0)` still get identical schedules, so the function
remains testable by calling it twice and comparing, exactly as before.
Nothing about the algorithm reaches outside its arguments for
randomness.

What the `rng` parameter hands to the caller is control of the seed,
and with it the responsibility for reproducibility. The
`seed: int = 0` version accepted only an integer. A caller who wanted
two different schedules had to pass a different one, and a caller who
wanted this function to share a program-wide random stream had no way
to say so. The `rng` version allows both. In exchange, a caller can
now pass `random.Random()` with no seed and get schedules that differ
on every run.

Passing the `rng` is dependency injection applied to a source of
nondeterminism, the same move
[Random Numbers](../Chapters/11_Techniques--Testing.md#random-numbers)
makes for testing. The function stays pure either way: it was always
a pure function of its arguments, and the argument it depends on
simply became explicit.
