# Toolkits: Solutions

## 1. `deep_sum()` with an explicit stack

```python
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

The loop version is the same length as the recursive one, so brevity
is not the argument either way. What changed is how much of the
bookkeeping is yours. The recursive version never names a stack: the
call stack holds the sublists still being walked, and `return` pops
one. Here you allocate the stack, seed it with a copy of `items`,
choose `pop()` over `pop(0)`, and choose `extend()` over `append()`.

Three of those are places to be wrong. Seeding with `items` instead of
`list(items)` mutates the caller's list as the loop drains it. Using
`append()` where `extend()` belongs pushes the sublist as a single
element and loops forever on it. Using `pop(0)` still gives the right
total but walks the structure breadth-first, which is a different
traversal than the recursive version and would matter the moment the
function did anything order-dependent. The recursive version cannot
make any of these mistakes, because it never has the choice.

## 2. `lru_cache` with `maxsize=3`

```python
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
distinct arguments arrive, so there are three misses, and the cache
now has room for all three. Nothing is ever evicted, so the repeat
calls to `square(2)` and `square(1)` both find their stored answers.

The difference from the chapter's `maxsize=2` run is the second
`square(1)`. There it was a fourth miss, because computing `square(3)`
had pushed `1` out to make room. One extra slot converts that miss
into a hit, which is the whole of what `maxsize` controls. The comment
in the chapter's listing, "Evicts 1, the least recently used," stops
being true here: with three slots there is nothing to evict.

## 3. `batch_totals()` stays lazy

```python
from collections.abc import Iterable, Iterator
from itertools import batched, count, islice

def batch_totals(source: Iterable[int],
                 n: int) -> Iterator[int]:
    return (sum(b) for b in batched(source, n))

print(list(islice(batch_totals(count(1), 3), 5)))
#: [6, 15, 24, 33, 42]
```

`batched()` does the chunking and a generator expression does the
summing, so the body is one line and no loop is written by hand.

Passing `count(1)` is the proof of laziness. `count()` never ends, so
if `batch_totals()` built a list of batches, or if `batched()` read
its source eagerly, the call would never return. It returns
immediately, and `islice()` then pulls exactly five totals, which
means exactly fifteen integers were ever generated. The first total
is `1 + 2 + 3`, and each later one is nine larger, since every batch
advances the source by three.

## 4. `grouped()` cannot repeat a key

```python
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
whole input before returning anything, so it cannot be handed an
infinite source and it holds every item in memory at once.
`groupby()` yields each group as it reaches it and keeps only the
current one, which is why it can stream a file larger than memory. It
also preserves the input's order, while `grouped()` reports groups in
first-appearance order and loses the interleaving between them.
Sorting first to make `groupby()` safe costs the same memory that
`grouped()` costs, plus the sort, so `grouped()` is the better answer
whenever the input already fits in memory.

## 5. `@cache` on `deep_sum()`

```python
from functools import cache

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    return 0

try:
    deep_sum([1, [2, 3]])
except TypeError as e:
    print(f"{type(e).__name__}: {e}")
#: TypeError: unhashable type: 'list'
```

`cache` stores results in a dictionary keyed on the arguments, so
every argument has to be hashable. A `list` is not, because its
contents can change after it is stored, which would leave the key
unfindable in the dictionary that holds it. The call fails before
`deep_sum()`'s body runs at all.

For caching to be possible, `Nested` would have to describe an
immutable structure: `type Nested = int | tuple[Nested, ...]`, with
the parameter annotated `tuple[Nested, ...]` rather than
`list[Nested]`. Tuples hash by contents, and their contents cannot
change, so the two conditions a cache key needs are both met. That is
the same requirement the chapter's `cache` entry states as "only works
correctly for pure functions," seen from the key's side rather than
the function's.

Note that the exception says nothing about purity. `deep_sum()` is
already pure, and caching it would be correct; the obstacle is the
argument type alone.

## 6. Injecting the random source

```python
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

What it preserves is determinism. Two callers who pass
`random.Random(0)` still get identical schedules, so the function
remains testable by calling it twice and comparing, exactly as before.
Nothing about the algorithm reaches outside its arguments for
randomness.

What it hands to the caller is control of the seed, and with it the
responsibility for reproducibility. The `seed: int = 0` version could
not be given an existing random source, so a caller who wanted two
different schedules had to pass a different integer, and a caller who
wanted this function to share a program-wide random stream could not
do it at all. The `rng` version allows both, and in exchange the
caller can now pass `random.Random()` with no seed and get a function
that is no longer reproducible.

This is dependency injection applied to a source of nondeterminism,
the same move [Random Numbers](../Chapters/11_Testing.md#random-numbers)
makes for testing. The function does not become more or less pure either way:
it was always a pure function of its arguments, and the argument it
depends on simply became explicit.
