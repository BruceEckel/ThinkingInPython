# Toolkits: Solutions

## 1. `deep_sum()` with an explicit stack

> Rewrite `deep_sum()` from `nested_sum.py` without recursion,
> using a list as an explicit stack.
> Compare the two versions for length,
> and name the mistakes the loop version allows that the recursive one cannot make.

<details>
<summary>Where to look</summary>

[Recursion](../../Chapters/41_Functional--Toolkits.md#recursion) shows `deep_sum()` letting the call stack hold the sublists still to walk.
Replace that call stack with a list you manage: pop an item, add its total if it is an `int`,
and otherwise push its elements back onto the list.
Copy the input before you seed the stack, and consider from which end you pop.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    ...
```

<details>
<summary>Solution</summary>

If you seed the stack with `items` instead of `list(items)`,
`deep_sum()` still returns `21`, but the caller's list is empty
afterward, and printing it shows `[]`. The stack and the argument are
one list, so every `pop()` drains the caller's data. The solution copies
`items` with `list()`, which gives the loop a list of its own to
consume.

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

The loop version runs two lines longer than the recursive one, so
brevity is not the argument either way. The rewrite changes how much
of the bookkeeping is yours. The recursive version names no stack. The
call stack holds the sublists still to walk, and `return` pops one.
Here you allocate the stack, seed it with a copy of `items`, choose
`pop()` over `pop(0)`, and choose `extend()` over `append()`. Three of
those choices are places to be wrong.

**Protect the caller's list.** Seeding with `items`
instead of `list(items)` mutates the caller's list as the loop drains
it.

**Pick which item comes next.** The pop end decides the visiting
order, and neither end gives the recursive version's left-to-right
walk. `pop()` visits the leaves right to left, and `pop(0)` walks the
structure breadth-first. Both still give the right total, but the
order matters the moment the function does anything order-dependent.

**Descend into a sublist.** Using `append()` where `extend()` belongs pushes the sublist as
a single element and loops forever on it.

The recursive version cannot make any of these
mistakes, because it makes none of those choices.

</details>
</details>
</details>

## 2. `lru_cache` with `maxsize=3`

> `functools_lru_cache.py` prints `CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)`.
> Change `maxsize` to `3`, predict the four numbers before running it,
> then run it and account for any difference.

<details>
<summary>Where to look</summary>

[`lru_cache`](../../Chapters/41_Functional--Toolkits.md#lru_cache) shows `cache_info()` after a run with `maxsize=2`.
Count the distinct arguments the function sees and compare that count with the new `maxsize`.
The difference tells you whether the cache evicts any entry, and so which calls are hits.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from functools import lru_cache

@lru_cache(maxsize=3)
def square(n: int) -> int:
    ...
```

<details>
<summary>Solution</summary>

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
all three results. The cache evicts nothing, so the repeat calls to
`square(2)` and `square(1)` both find their stored answers.

The difference from the chapter's `maxsize=2` run is the second
`square(1)`. Under `maxsize=2` that call is a fourth miss, because
computing `square(3)` has pushed `1` out to make room. One extra slot
converts that miss into a hit, and that conversion is the whole of
what `maxsize` controls. With three slots the cache keeps every
result, so `functools_lru_cache.py`'s comment, "Evicts 1, the least
recently used," stops being true here.

</details>
</details>
</details>

## 3. `batch_totals()` stays lazy

> Write `batch_totals(source, n)`,
> which takes an iterator and yields the sum of each `n`-element batch,
> built only from `itertools` pieces and a generator expression.
> Show that it stays lazy by passing it `count(1)` and taking five values.

<details>
<summary>Where to look</summary>

[`batched`](../../Chapters/41_Functional--Toolkits.md#batched) yields fixed-size tuples from any iterable, and a generator expression can sum each one.
[Lazy Evaluation](../../Chapters/41_Functional--Toolkits.md#lazy-evaluation) explains why `islice()` over an infinite `count()` pulls only what it needs.
If every stage is lazy, taking five values from `count(1)` terminates.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Iterable, Iterator
from itertools import batched, count, islice

def batch_totals(source: Iterable[int],
                 n: int) -> Iterator[int]:
    ...
```

<details>
<summary>Solution</summary>

If you build the totals with a list comprehension, `[sum(b) for b in batched(source, n)]`,
`ty` reports an `invalid-return-type`.
A `list[int]` has no `__next__()`, so it is not an `Iterator[int]`.
If you change the annotation to `list[int]` to match,
the demo's call hangs,
because the comprehension tries to sum every batch `count(1)` can supply
and `islice()` gets no total to take.
The generator expression computes each total only when `islice()` requests it.

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

**Total each batch.** `batched()` chunks the source and a generator expression sums
each batch, so the body fits on one line with no hand-written loop.

**Test laziness on an infinite source.** Passing `count(1)` proves the function is lazy. `count()` is infinite, so
if `batch_totals()` builds a list of batches, or if `batched()` reads
its source eagerly, the call hangs. The call returns
immediately, and `islice()` then pulls exactly five totals, so
`count()` yields exactly fifteen integers in all. The first total is
`1 + 2 + 3`, and each later one is nine larger, since every batch
advances the source by three.

</details>
</details>
</details>

## 4. `grouped()` cannot repeat a key

> `groupby()` on unsorted input silently returns the same key more than once.
> Write `grouped(data, key)` returning a `dict[K, list[V]]` that cannot make that mistake,
> and say what it loses compared with `groupby()`.

<details>
<summary>Where to look</summary>

[`groupby`](../../Chapters/41_Functional--Toolkits.md#groupby) shows why `groupby()` repeats a key when equal items are not adjacent.
Accumulate into a `defaultdict(list)` keyed by `key(item)` instead, so each key exists once by construction.
What `grouped()` loses follows from what the loop must finish before it can return anything.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable

def grouped[V, K: Hashable](
    data: Iterable[V], key: Callable[[V], K]
) -> dict[K, list[V]]:
    ...
```

<details>
<summary>Solution</summary>

If you wrap `groupby()` in a dictionary comprehension, `{k: list(g) for k, g in groupby(data, key)}`,
the demo prints `{'B': ['b'], 'A': ['a']}`.
The second `"b"` group replaces the first under the same key,
so one item disappears with no error, and the type checker passes the function.
The solution's `defaultdict` appends each item to the list stored under its key,
so a key that comes back adds to its group instead of replacing it.

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

**Collect each item under its key.** Because a dictionary key exists
once by construction, the duplicate-key failure `groupby()` has on
unsorted input cannot occur. The two `"b"` entries go into the same
list no matter how far apart they arrive, and the caller needs no
`sorted()` call to group them.

`grouped()` loses the streaming that `groupby()` provides. It reads
the whole input before returning anything, so an infinite source makes
it loop forever, and a finite one sits entirely in memory. `groupby()`
yields each group as it arrives and keeps only the current one, which
is why it can stream a file larger than memory. It also preserves the
input's order, while `grouped()` reports groups in first-appearance
order and loses the interleaving between them. Sorting first to make
`groupby()` safe costs the same memory as `grouped()`, plus the sort,
so `grouped()` is the better answer whenever the input fits in memory.

</details>
</details>
</details>

## 5. `@cache` on `deep_sum()`

> Decorate `deep_sum()` with `@cache` and explain the exception.
> What must change about the `Nested` alias for caching to be possible?

<details>
<summary>Where to look</summary>

[`cache`](../../Chapters/41_Functional--Toolkits.md#cache) says the cache stores results in a dictionary keyed on the arguments.
A dictionary key must be hashable, so ask which argument type in the signature fails that test.
The fix changes the `Nested` alias, and the same section's note on pure functions covers a separate requirement.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from functools import cache
from exceptions import expect

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from functools import cache
from exceptions import expect

type Nested = int | list[Nested]

@cache
def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)  # type: ignore
        else:
            total += item
    return total

expect(TypeError, deep_sum,
       [1, [2, [3, 4], 5], 6])  # type: ignore
#: [TypeError] unhashable type: 'list'
```

**Show why the call fails.** Because `cache()` stores results in a
dictionary keyed on the arguments, every argument must be hashable. A
`list` is not hashable, because its contents can change after the
cache stores it, and a mutated key no longer hashes to the slot
holding its entry. The call fails before `deep_sum()`'s body runs.

**Silence the checker so the listing runs.** `ty` reports the same problem before the program runs. The standard
library's type declarations give a cached function's parameters the
type `Hashable`, so both calls draw
`invalid-argument-type`: "Expected `Hashable`, found `list[Nested]`"
on the recursive call, and the same diagnostic, naming the literal's
inferred type, on the list passed through `expect()`. The two
`# type: ignore` comments silence those diagnostics so the listing
can run and show the exception.

For caching to be possible, `Nested` must describe an immutable
structure: `type Nested = int | tuple[Nested, ...]`, with the
parameter annotated `tuple[Nested, ...]` rather than `list[Nested]`.
Tuples hash by contents, and their contents cannot change, so a tuple
meets both conditions a cache key needs.

Purity is a second, separate requirement. The chapter's `cache` entry
states that "`@cache` works correctly only for pure functions."
Hashability constrains the key, purity constrains the function, and a
function can meet one without the other.

The exception says nothing about purity. `deep_sum()` is pure,
and caching it would be correct. The obstacle is the
argument type alone.

</details>
</details>
</details>

## 6. Injecting the random source

> `group_rounds()` takes a `seed` and builds its own `random.Random`.
> Replace the `seed` parameter with an `rng: random.Random` parameter.
> Which property of the function does the `rng` parameter preserve,
> and which one does it leave to the caller?

<details>
<summary>Where to look</summary>

[Case Study: Pairing Rotations](../../Chapters/41_Functional--Toolkits.md#case-study-pairing-rotations) builds its own `random.Random` from a `seed`.
Accept the `Random` object as a parameter and call its `shuffle()` where the function called its own.
Then ask which part of reproducibility the function still controls and which part the caller now decides.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, rng: random.Random
) -> Iterator[Round]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, rng: random.Random
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()

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

students = ["Ana", "Bo", "Cy", "Di", "Eve", "Fi", "Gia"]
first = next(group_rounds(students, 2, random.Random(0)))
second = next(group_rounds(students, 2, random.Random(0)))
print(first == second)
#: True
print(first)
#: [('Gia', 'Eve', 'Ana'), ('Di', 'Cy'), ('Fi', 'Bo')]
```

What the `rng` parameter preserves is determinism. Two callers who
pass `random.Random(0)` still get identical schedules, so the function
remains testable by calling it twice and comparing, as before.
The first round is the same one `pair_rounds.py` prints, because
`random.Random(0)` is what `seed: int = 0` builds internally. The
algorithm draws its randomness from its arguments alone.

What the `rng` parameter hands to the caller is control of the seed,
and with it the responsibility for reproducibility. The
`seed: int = 0` version accepts only an integer. A caller who needs
two different schedules must pass a different integer, and a caller who
wants this function to share a program-wide random stream has no way
to say so. The `rng` version allows both. In exchange, a caller can
now pass `random.Random()` with no seed and get schedules that differ
on every run.

Passing the `rng` is dependency injection applied to a source of
nondeterminism, the same move
[Random Numbers](../../Chapters/11_Techniques--Testing.md#random-numbers)
makes for testing. The `rng` version is deterministic per `Random`
object. Two callers who each build `random.Random(0)` get identical
schedules, while two calls sharing one `Random` do not, because
`shuffle()` advances that object's state.

</details>
</details>
</details>
