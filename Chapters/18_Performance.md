# Performance

Performance means at least two things when it comes to computing:

1. Application development speed
2. Execution speed

Python addresses the first issue with clear syntax and extensive power and flexibility.
As to the second issue, Python is commonly considered to be slow.

## Is It Actually Too Slow?

Computer programming projects have a long history of *premature optimization*.
This means optimizing before any measurement shows where the time goes.
Often people decide ahead of time, based on biases,
that runtime performance will be insufficient.
This results in elaborate, expensive designs that solve nonexistent problems.

Python can be surprising.
A program coded in the most straightforward way,
without concern for performance, can often run fast enough for your needs.
Do not automatically assume that a simply written program will be too slow.
Try it out first.
It might be fine.

If it is too slow, try the simplest remedy first.
That might be enough, and if it is, you save time and money.

What follows is an approach to solving performance problems,
starting with the simplest techniques and growing successively more complex.

## Try a Faster Platform

Alternative interpreters for Python exist, notably PyPy,
which boasts a 4x to 10x speedup.
PyPy typically trails CPython's newest language version,
so confirm it supports the features and third-party packages you rely on.

How much does a hardware upgrade cost compared to paying programmers to solve the performance problem?
If it's noticeably less, then buying new hardware might be a quick win.

## Profilers

A *profiler* looks for the slow spots in your code, so you know where to focus.
Although it is tempting to think you "have a pretty good idea where the slowdown is,"
we turn out to be bad at guessing this.
A profiler tells you for sure, preventing wasted time.

The standard library includes two profilers.
The classic `cProfile` was introduced in 2006.
It deterministically records every function call and return.
Its numbers are exact, but the instrumentation slows the program,
sometimes enough to distort the behavior you are measuring.
Here's how you run `cProfile` on `my_program.py`:

    python -m cProfile -s cumulative my_program.py

Python 3.15 gathers the profilers into a single `profiling` package
([PEP 799](https://peps.python.org/pep-0799/)).
The deterministic tracing profiler becomes `profiling.tracing`,
with `cProfile` kept as an alias.
Python 3.15 also adds a new *sampling* profiler named `profiling.sampling`.
Instead of tracing every call, it takes periodic snapshots of the call stack,
so the overhead is near zero and the program runs at full speed while you watch.
You invoke it like this:

    python -m profiling.sampling run my_program.py

The new profiler can also attach to a process that is already running,
using the process ID.
This makes it the tool for a slowdown you can only reproduce live:

    python -m profiling.sampling attach 12345

Either form ends with a table of hot functions ranked by sample count.

Beyond the standard library, [Scalene](https://github.com/plasma-umass/scalene)
separates Python time from native time and profiles memory line by line.

If you can narrow the problem down to a particular function,
there may be techniques that speed up the algorithm used in that function.

## Benchmark Alternatives with `timeit`

A profiler tells you *where* the time goes.
Once you discover a hot spot, `timeit` tells you which rewrite wins.
It runs a small snippet many times and reports the total,
insulating the measurement from startup cost and clock granularity.

Timings differ from machine to machine,
so the following example prints a comparison instead of raw numbers.
A `list` tests membership by scanning.
`target in as_list` walks the list from the start,
comparing each element until it finds a match or reaches the end.
A `set` tests membership through hashing.
`target in as_set` computes a hash of `target` and jumps straight to the bucket that value occupies.
Scanning gets slower as the list grows.
Hashing stays fast no matter how many elements the set holds:

```python
# membership.py
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n - 1  # Worst case: the last element in the list

t_list = timeit.timeit(lambda: target in as_list, number=100)
t_set = timeit.timeit(lambda: target in as_set, number=100)
print(f"set at least 100x faster: {t_set * 100 < t_list}")
#: set at least 100x faster: True
```

`timeit.timeit()` calls its first argument repeatedly and returns the total elapsed time in seconds for every call combined,
not the time for one call.
That first argument is a `lambda` here rather than a string of code,
since a `lambda` can close over `target`, `as_list`, and `as_set` directly,
with no separate `setup` argument needed to build them.
`number` sets how many times `timeit` calls the lambda, 100 in this case.

A single lookup costs little either way.
A million lookups is the difference between instant and minutes.
`timeit` also has a command-line form for one-off questions:

    python -m timeit -s "s = set(range(100_000))" "99_999 in s"

Do your benchmarks using data that is shaped like production data.
A `list` of ten elements can beat a `set`,
and an optimization tuned to toy input can behave badly in production.

## Write Idiomatic Python

The interpreter is written in C.
Built-in functions and comprehensions run their loops in C,
so the more of your loop you hand to the interpreter,
the less bytecode runs per element.
The idiomatic version of a loop is usually also the fast one:

```python
# builtin_sum.py
import timeit

numbers = list(range(100_000))

def hand_written() -> int:
    total = 0
    for n in numbers:
        total += n
    return total

assert hand_written() == sum(numbers)
t_loop = timeit.timeit(hand_written, number=50)
t_sum = timeit.timeit(lambda: sum(numbers), number=50)
print(f"sum() at least twice as fast: {t_sum * 2 < t_loop}")
#: sum() at least twice as fast: True
```

Other examples:

- String concatenation: `"".join(parts)` is faster than `+=` in a loop
  (one linear pass instead of repeated reallocation).
- A comprehension is faster than an `append()` loop.
- The C-implemented standard library's `itertools`, `collections`,
  and `functools`, are faster than hand-rolled equivalents
  ([Iterators](23_Iterators.md#reusable-algorithms) tours the iterator algorithms).

As a last resort in a proven hot loop,
hoist a repeated attribute or global lookup into a local,
as in `append = out.append`.
That is a micro-optimization, so let a measurement justify it:

```python
# hoist_attribute_lookup.py
import timeit

n = 100_000

def with_attribute_lookup() -> list[int]:
    out: list[int] = []
    for i in range(n):
        out.append(i)
    return out

def with_hoisted_local() -> list[int]:
    out: list[int] = []
    append = out.append
    for i in range(n):
        append(i)
    return out

assert with_attribute_lookup() == with_hoisted_local()
t_attr = timeit.timeit(with_attribute_lookup, number=100)
t_local = timeit.timeit(with_hoisted_local, number=100)
close = abs(t_local - t_attr) < 0.2 * t_attr
print(f"hoisting made little difference: {close}")
#: hoisting made little difference: True
```

Here the hoist does not pay off.
Modern CPython already caches a repeated attribute lookup like `out.append` inside a loop,
so it costs little more than the local variable would have.
The measurement proves the point because it catches a "classic" optimization that no longer works,
just as readily as it would catch one that does.

## Choose Better Algorithms and Data Structures

The biggest speedups usually come from a better algorithm.
An algorithm with lower Big-O complexity beats micro-optimizing a slow algorithm.
Often this means choosing the right container.
Use a `set` or `dict` for membership and lookup instead of scanning a `list`.
Use a `deque` (see [Containers](03_Containers.md#deque))
when you add and remove at both ends.

### Bisect

For data kept in sorted order,
the `bisect` module finds the insertion point using binary search:

```python
# bisect_search.py
import bisect

scores = [60, 70, 75, 90]  # Must stay sorted
i = bisect.bisect(scores, 78)  # Where 78 goes
print(i)
#: 3
bisect.insort(scores, 78)  # Insert and keep it sorted
print(scores)
#: [60, 70, 75, 78, 90]

def grade(score: int) -> str:
    # Map a score to a letter through its cutoff boundaries:
    cutoffs = [60, 70, 80, 90]
    letters = "FDCBA"
    return letters[bisect.bisect(cutoffs, score)]

print([grade(s) for s in (55, 65, 85, 95)])
#: ['F', 'D', 'B', 'A']
```

Because `scores` stays sorted, `bisect` locates a position in O(log n)
instead of the O(n) scan a `list` would need.
Only the search is fast,
because `insort()` still shifts everything after the insertion point.
Under heavy insert traffic consider the heap below instead.

### Comparison

That leaves three ways to answer the same membership question: scan a `list`,
binary-search a sorted `list` with `bisect`,
or hash straight to the answer with a `set`.
Timing all three together shows the size of each step:

```python
# search_comparison.py
import bisect
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n // 2

def scan() -> bool:
    return target in as_list

def binary_search() -> bool:
    i = bisect.bisect_left(as_list, target)
    return i < len(as_list) and as_list[i] == target

def hashed() -> bool:
    return target in as_set

assert {scan(), binary_search(), hashed()} == {True}
t_scan = timeit.timeit(scan, number=1000)
t_search = timeit.timeit(binary_search, number=1000)
t_hashed = timeit.timeit(hashed, number=1000)
print(f"binary search at least 100x faster than scan: "
      f"{t_search * 100 < t_scan}")
#: binary search at least 100x faster than scan: True
print(f"hashing at least 3x faster than binary search: "
      f"{t_hashed * 3 < t_search}")
#: hashing at least 3x faster than binary search: True
```

The scan loses badly,
since it walks roughly half the `list` before reaching `target`.
`bisect` narrows that to a handful of comparisons,
one per halving of the remaining range, which is why moving from O(n)
to O(log n) shows up as orders of magnitude here rather than a modest improvement.
Hashing wins again over `bisect`,
since it needs only one hash and one equality check no matter how large `as_set` grows.

### Heap

When you repeatedly need the smallest or largest item,
a *heap* keeps that item reachable in O(log n).
The `heapq` module treats a `list` as a binary heap.
Through Python 3.13, `heapq` only built a min-heap;
getting a max-heap meant negating every value going in and out.
Python 3.14 added `_max` variants
(`heapify_max()`, `heappush_max()`, `heappop_max()`, and friends)
that keep the largest item at index 0 instead,
so the negation trick is no longer necessary:

```python
# heap_queue.py
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)  # Rearrange into a min-heap in place
print(nums)
#: [1, 2, 8, 3, 5]
print(nums[0])  # The smallest stays at the front
#: 1
heapq.heappush(nums, 7)
print(nums)
#: [1, 2, 7, 3, 5, 8]
print(heapq.heappop(nums))  # Remove and return the smallest
#: 1
print(nums)
#: [2, 3, 7, 8, 5]
# Doesn't make a heap from the list:
print(heapq.nsmallest(3, [5, 1, 8, 3, 2]))
#: [1, 2, 3]
print(heapq.nlargest(2, [5, 1, 8, 3, 2]))
#: [8, 5]

max_nums = [5, 1, 8, 3, 2]
heapq.heapify_max(max_nums)  # Rearrange into a max-heap in place
print(max_nums)
#: [8, 3, 5, 1, 2]
print(max_nums[0])  # The largest stays at the front
#: 8
heapq.heappush_max(max_nums, 9)
print(max_nums)
#: [9, 3, 8, 1, 2, 5]
print(heapq.heappop_max(max_nums))  # Remove and return the largest
#: 9
print(max_nums)  # Heap ordering is maintained
#: [8, 3, 5, 1, 2]
```

After `heapify()` the smallest element is placed at index 0,
and `heapify_max()` mirrors it with the largest element at index 0.
`nsmallest()` and `nlargest()` answer top-N questions without building new a heap.

The output shows that the [heap-management algorithm](https://docs.python.org/3.15/library/heapq.html#priority-queue-implementation-notes)
maintains the list according to its own logic.
This means you must always use the heap version of an operation,
not the list version.
Although calling `nums.pop()` does produce the smallest value the first time you do it,
it also destroys the heap ordering,
so if you call it again you won't get the smallest value:

```python
# heap_corruption.py
from heapq import heapify, nsmallest

heap = [10, 9, 8, 7, 6, 5, 4, 3]
heapify(heap)  # In-place
print(heap)
#: [3, 6, 4, 7, 10, 5, 8, 9]
print(heap.pop(0))  # Smallest
#: 3
print(heap)  # 'heap[0]' no longer smallest
#: [6, 4, 7, 10, 5, 8, 9]
print(nsmallest(len(heap), heap))  # True smallest
#: [4, 5, 6, 7, 8, 9, 10]
print(heap)  # Not reordered by nsmallest()
#: [6, 4, 7, 10, 5, 8, 9]
```

For a priority queue shared across threads,
`queue.PriorityQueue` wraps the same heap in a lock.
[Concurrency](19_Concurrency.md#coordinating-threads-with-queues)
shows it in use.

A heap and a hash solve different problems.
Hashing answers "is this here?" in O(1) but has no notion of order,
so finding the smallest element still means scanning every item.
A heap keeps that order updated as you go,
so pulling the smallest item costs only O(log n),
no matter how many times you repeat it:

```python
# heap_vs_hash.py
import heapq
import timeit

n = 10_000
data = list(range(n, 0, -1))
print(data[:8])
#: [10000, 9999, 9998, 9997, 9996, 9995, 9994, 9993]

def heap_min_extractions() -> list[int]:
    heap = data.copy()
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(100)]

def hash_min_extractions() -> list[int]:
    remaining = set(data)
    result = []
    for _ in range(100):
        smallest = min(remaining)
        remaining.remove(smallest)
        result.append(smallest)
    return result

assert heap_min_extractions() == hash_min_extractions()
t_heap = timeit.timeit(heap_min_extractions, number=50)
t_hash = timeit.timeit(hash_min_extractions, number=50)
print(f"heap at least 10x faster than repeated min() on a set: "
      f"{t_heap * 10 < t_hash}")
#: heap at least 10x faster than repeated min() on a set: True
```

Each `min()` call on `remaining` walks the whole `set`,
so extracting 100 smallest items costs roughly O(100n).
`heapify()` pays O(n) once, then each `heappop()` costs only O(log n),
so the same 100 extractions cost roughly O(n + 100 log n).
That gap is why the heap wins by more than an order of magnitude here,
and the gap widens as `n` grows.

The immutable containers from [Containers](03_Containers.md#immutability)
are not a speed upgrade.
A `frozenset` looks up exactly as fast as a `set`,
a `frozendict` behaves like a `dict`, and a `tuple` scans like a `list`.
In CPython these share the same machinery.
Choose immutability for correctness and safe sharing.
Immutable values are hashable,
so they can serve as dictionary keys and as arguments to the caches shown below.

## Lazy Evaluation with Generators

A list-building pipeline materializes every intermediate result.
A generator pipeline
([Comprehensions](16_Comprehensions.md#generator-expressions))
computes one item at a time, on demand,
so memory stays flat no matter how large the source,
and no work happens past the point where the consumer stops.
`tracemalloc` measures the difference:

```python
# lazy_pipeline.py
import tracemalloc
from itertools import islice

N = 1_000_000

def eager_first_evens() -> list[int]:
    squares = [x * x for x in range(N)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def lazy_first_evens() -> list[int]:
    squares = (x * x for x in range(N))
    evens = (s for s in squares if s % 2 == 0)
    return list(islice(evens, 5))

tracemalloc.start()
eager = eager_first_evens()
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
lazy = lazy_first_evens()
_, lazy_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(eager, eager == lazy)
#: [0, 4, 16, 36, 64] True
print(f"lazy peak under 1% of eager: {lazy_peak * 100 < eager_peak}")
#: lazy peak under 1% of eager: True
```

Both versions produce the same five numbers,
but the eager one built two million-element lists to get them,
while the lazy one computed only the handful of values that `islice()` extracted.
When the consumer needs every element anyway and the data fits in memory,
a list is fine, and you can iterate it twice.
A generator is spent after one pass.

## Caching

If a pure function ([Functional Foundations](40_Functional_Foundations.md#pure-functions))
is called repeatedly with the same arguments,
the fastest way to compute the answer is to not compute it.
`functools.cache` stores each result the first time and replays it after that.
The classic demonstration is naive recursive Fibonacci,
which recomputes the same subproblems exponentially many times:

```python
# cache_speedup.py
from functools import cache

calls = 0

def fib_plain(n: int) -> int:
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)

@cache
def fib_cached(n: int) -> int:
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

print(fib_plain(25), calls)
#: 75025 242785
print(fib_cached(25), fib_cached.cache_info().misses)
#: 75025 26
```

Same answer, but 242,785 calls against 26.
The counts are the speedup.
The cached version runs thousands of times faster, and the gap grows with `n`.

`cache` holds every result forever,
but `functools.lru_cache(maxsize=n)` bounds the memory by discarding the least recently used entry.
Arguments must be hashable,
which is another reason to prefer immutable containers.
For an expensive attribute computed once per object,
`functools.cached_property` does the same job on instances
(see [Classes](07_Classes.md#properties)).

Caching is only correct when the function is pure.
Caching a function with side effects replays the answer but skips the effects,
and caching a function that reads outside state can replay a stale answer.

## Reduce Memory Overhead

With millions of objects, per-object overhead can dominate performance.
Three tools reduce that overhead.

### Slots

By default each instance stores its attributes in a `__dict__`.
Declaring `__slots__` replaces that dict with a fixed set of fields,
which shrinks each instance and speeds attribute access:

```python
# slots.py

class Point:
    __slots__ = ("x", "y")  # No per-instance __dict__
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)
#: 1 2
try:
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
```

A data class can generate the slots for you.
`@dataclass(slots=True)` turns the field declarations into `__slots__` and still writes `__init__()`,
`__repr__()`, and `__eq__()`:

```python
# slots_dataclass.py
import sys
from dataclasses import dataclass
from exceptions import ignore

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
try:
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError

@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int

@dataclass(frozen=True, slots=True)
class FrozenSlottedPoint:
    x: int
    y: int

fp = FrozenPoint(1, 2)
with ignore(AttributeError):
    # Frozen prevents new attributes, not just reassignment:
    fp.z = 3  # type: ignore
#: FrozenInstanceError("cannot assign to field 'z'")

frozen_bytes = sys.getsizeof(fp) + sys.getsizeof(fp.__dict__)
slotted_bytes = sys.getsizeof(FrozenSlottedPoint(1, 2))
print(f"slots at least 5x smaller: "
      f"{slotted_bytes * 5 < frozen_bytes}")
#: slots at least 5x smaller: True
```

If a class can be a data class,
prefer `slots=True` over a hand-written class with `__slots__`.
This produces both memory savings and generated methods.
The tradeoff is that instances can no longer grow attributes outside the declared set.

`frozen=True` does not imply `slots=True`.
Frozen blocks every attribute assignment, not just reassignment,
so it already stops an instance from growing new fields,
the same restriction `slots` gives you.
But frozen enforces this by overriding `__setattr__()`.
The instance still keeps a `__dict__` underneath.
`slots=True` removes that `__dict__`,
so pairing it with `frozen=True` is the natural default,
giving you the same immutability in a fraction of the space
(one machine measured 344 bytes against 48, roughly seven to one).
The exact byte counts vary by platform and Python build,
so the listing prints a comparison that holds anywhere rather than numbers that hold only here.

### Array Instead of List

A `list` of numbers stores full Python objects, each with its own header.
The `array` module packs numbers into a single block of C values instead:

```python
# compact_array.py
import sys
from array import array
from exceptions import ignore

a = array("d", [1.0, 2.0, 3.0])  # "d" = C double
a.append(4.0)
print(a)
#: array('d', [1.0, 2.0, 3.0, 4.0])
print(a[1], a.typecode, a.itemsize)
#: 2.0 d 8
with ignore(TypeError):
    # The value must match the type code:
    a.append("x")  # type: ignore
#: TypeError('must be real number, not str')

nums = [float(i) for i in range(10_000)]
packed = array("d", nums)
list_bytes = sys.getsizeof(nums) + sum(
    sys.getsizeof(x) for x in nums
)
array_bytes = sys.getsizeof(packed)
print(f"array at least 3x smaller: "
      f"{array_bytes * 3 < list_bytes}")
#: array at least 3x smaller: True
```

Every element shares one type, given by the type code,
so `array` stores them compactly and rejects values of the wrong type.
The size comparison shows the cost of boxing:
the `list` holds an 8-byte pointer to a 24-byte `float` object per element,
while the `array` spends 8 bytes per element total,
roughly a four-to-one difference
(one machine measured 325,176 bytes against 80,080).
(`sys.getsizeof()` reports a `list`'s own size but not its elements', so the elements are summed separately.)

### Memory View

A `memoryview` exposes another object's memory without copying it.
Slicing a large `bytes` or `bytearray` through a view avoids duplicating the data:

```python
# memory_view.py
data = bytearray(b"ABCDEF")
view = memoryview(data)  # No copy of the underlying bytes
chunk = view[1:4]
print(bytes(chunk))
#: b'BCD'
view[0] = ord("z")  # Writes through to the original
print(data)
#: bytearray(b'zBCDEF')
print(view.nbytes)
#: 6
```

The view shares storage with `data`,
so writing through it changes the original and copies no bytes.

## Vectorize with NumPy

When the hot spot is arithmetic over a large collection of numbers,
the biggest step is to remove the Python loop.
[NumPy](https://numpy.org/) stores numbers unboxed in contiguous arrays,
like `array` above, and executes whole-array expressions in compiled loops.
The plain-Python version repeats one expression per element.
The NumPy version states it once for the whole array:

    import timeit
    import numpy as np

    n = 1_000_000
    numbers = list(range(n))
    a = np.arange(n, dtype=np.float64)

    def pure_python() -> list[float]:
        return [3.0 * x + 1.0 for x in numbers]

    def vectorized() -> np.ndarray:
        return 3.0 * a + 1.0

    t_loop = timeit.timeit(pure_python, number=5)
    t_numpy = timeit.timeit(vectorized, number=5)
    print(f"NumPy speedup: {t_loop / t_numpy:.1f}x")
    # Sample run: NumPy speedup: 12.9x

`vectorized()` computes the same `3x + 1` as `pure_python()`,
but as one compiled pass over contiguous memory instead of a million individual Python-level steps.
NumPy is a fast library you call, not a compiled extension you write.
The benefit only occurs if the data stays inside NumPy.
Calling a Python function on each element,
or converting arrays to lists and back, reproduces the overhead.
This is the declarative trade from [Functional Assurance](43_Functional_Assurance.md#declarative-style):
describe the whole-array result and let the engine arrange the steps.

(NumPy is a third-party dependency, and the book's Python 3.15 target has no NumPy release yet, so unlike the rest of the book's listings, the build does not run this snippet.
The comment above shows one machine's actual output.
Expect a different, but still large, multiple on yours.)

## JIT Compilation with Numba

Sometimes the loop cannot become an array expression,
because each step depends on the previous one, or the control flow is irregular.
[Numba](https://numba.pydata.org/)'s `@njit` decorator compiles such a function to machine code on its first call,
in place.
The source stays Python:

    import timeit
    from numba import njit

    def count_primes(limit: int) -> int:
        count = 0
        for n in range(2, limit):
            for d in range(2, int(n ** 0.5) + 1):
                if n % d == 0:
                    break
            else:
                count += 1
        return count

    fast_count_primes = njit(count_primes)

    limit = 200_000
    fast_count_primes(1)  # Compile once, off the clock

    t_python = timeit.timeit(lambda: count_primes(limit), number=1)
    t_numba = timeit.timeit(lambda: fast_count_primes(limit), number=1)
    print(f"Numba speedup: {t_python / t_numba:.1f}x")
    # Sample run: Numba speedup: 15.9x

`njit(count_primes)` compiles the same function `@njit` would decorate.
Calling it once first pays the compilation cost outside the timed region,
so the comparison measures steady-state speed, not warm-up.
Numba shines on numeric code over simple types and NumPy arrays,
often landing within striking distance of C.
The first call pays a compilation delay,
and code that leans on arbitrary Python objects will not compile.
When the hot spot is number-crunching,
`@njit` is a lighter step than rewriting in another language.

(Numba is also a third-party dependency, and it does not yet support the book's Python 3.15 target, so like the NumPy example above, the build does not run this snippet.
The comment above shows one machine's actual output.
Expect a different, but still large, multiple on yours.)

## Combine NumPy and Numba

NumPy and Numba solve different halves of the same problem,
and a single function often uses both.
NumPy gives you a compact array.
`@njit` compiles a loop that walks it,
for the case where the loop cannot become one vectorized expression,
because the amount of work per element depends on the element's value.
The [Collatz conjecture](https://en.wikipedia.org/wiki/Collatz_conjecture)
is such a case: from `n`,
halve an even value or triple-and-increment an odd one,
and repeat until you reach 1.
The number of steps differs for every starting value,
so no single array expression produces it:

    import timeit
    import numpy as np
    from numba import njit

    def collatz_lengths(values: np.ndarray) -> np.ndarray:
        lengths = np.empty(len(values), dtype=np.int64)
        for i in range(len(values)):
            n = int(values[i])
            steps = 0
            while n != 1:
                n = n // 2 if n % 2 == 0 else 3 * n + 1
                steps += 1
            lengths[i] = steps
        return lengths

    fast_collatz_lengths = njit(collatz_lengths)

    values = np.arange(1, 50_000, dtype=np.int64)
    fast_collatz_lengths(values[:1])  # Compile once, off the clock

    t_python = timeit.timeit(
        lambda: collatz_lengths(values), number=1
    )
    t_numba = timeit.timeit(
        lambda: fast_collatz_lengths(values), number=1
    )
    print(f"Numba speedup: {t_python / t_numba:.1f}x")
    # Sample run: Numba speedup: 54.4x

`collatz_lengths()` takes a NumPy array and returns one,
so it composes with vectorized NumPy code on either side.
Compiling changes only what happens inside the loop:
the same Python source runs as machine code instead of as bytecode over boxed `int` objects.
This is the pattern in practice:
use a vectorized NumPy expression wherever the shape of the computation allows it,
and drop to a `@njit` loop for the steps that resist vectorizing,
keeping the array as the shared data structure throughout.

(Like the two examples above, this one needs both NumPy and Numba, so the build does not run it.
The comment shows one machine's actual output.
Expect a different, but still large, multiple on yours.)

## Concurrency

Sometimes the fix is not a faster function but a different architecture.
When the time goes to waiting on the outside world, use `asyncio`.
If the work can be done in parallel (pure functions can do this seamlessly),
you can spread it across multiple cores or multiple processes.
That is a design decision with its own chapter,
[Concurrency](19_Concurrency.md).

## Converting a Slow Function to Rust

One effective technique is to move the hot function into a compiled language.
Rust is excellent for this because its tooling makes the bridge nearly painless.
More importantly, you can pass the hot Python function to your AI for conversion to Rust.
Your AI can also walk you through the process.
Once you're done, you import a module that looks from the outside like any other Python module.
It just runs faster.
In addition, you can do things in Rust that might be much more difficult in Python.

[PyO3](https://pyo3.rs) generates the Python bindings,
and [maturin](https://www.maturin.rs)
builds and installs the result as an ordinary Python package.
`maturin new --bindings pyo3 fastcount` scaffolds the project,
and one attribute turns a Rust function into a Python function:

    use pyo3::prelude::*;

    #[pyfunction]
    fn count_primes(limit: u64) -> u64 {
        let mut count = 0;
        for n in 2..limit {
            let mut d = 2;
            let mut prime = true;
            while d * d <= n {
                if n % d == 0 {
                    prime = false;
                    break;
                }
                d += 1;
            }
            if prime {
                count += 1;
            }
        }
        count
    }

    #[pymodule]
    fn fastcount(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(count_primes, m)?)?;
        Ok(())
    }

After `maturin develop` compiles and installs it, Python sees a normal module:

    import fastcount
    fastcount.count_primes(100_000)

Keep the interface coarse.
A single call that does significant work wins.
A million calls that each do a little lose the gain due to boundary-crossing overhead.
Shipping millions of small Python objects across the boundary loses it too.
Numbers, strings, bytes, and NumPy arrays cross cheaply.
The cost of this technique is a second language and a build toolchain in your project.

## Choosing a Strategy

Measure first.
Every performance optimization costs something in effort, complexity,
or dependencies.
A profiler is the only way to discover hot spots.
Work down this list from the cheapest change to the most involved,
stopping as soon as the program is fast enough:

1. Run the straightforward version.
   It may be fast enough.
2. Try a faster platform: PyPy, or better hardware.
3. Write idiomatic Python and let the interpreter's C loops do the work.
4. Fix the algorithm and the data structures.
   This can produce order-of-magnitude improvements.
5. Make pipelines lazy with generators.
6. Cache the pure functions.
7. Cut per-object memory with `slots=True`, `array`, and `memoryview`.
8. Vectorize with NumPy, or JIT-compile the loop with Numba.
9. Restructure for async or parallelism ([Concurrency](19_Concurrency.md)).
10. Rewrite the proven-hot function in Rust.

After every change, measure again.
Optimizations interact, the bottleneck moves,
and yesterday's hot spot may be irrelevant today.
The goal is not the fastest possible program.
It is a program that is fast enough, at the lowest cost in clarity.

Step 4 on that list, fixing the algorithm, is usually the biggest win,
because it changes which curve your program is on,
not just where it sits on that curve:

![Big O growth rates vs. input size n](_images/big_o_growth)

## Exercises

1.  `membership.py` fixes `target` at the worst case, the last element.
    Measure the average case by timing lookups of many random targets,
    and see whether the conclusion changes.
2.  Use `timeit` to find the collection size below which the `list` scan beats the `set` lookup on your machine.
3.  Rewrite `eager_first_evens()` as a single list comprehension and measure its peak with `tracemalloc`.
    How close can an eager version get to the lazy one?
4.  Apply `@cache` to a function that prints as a side effect,
    and demonstrate that repeated calls skip the printing.
    Explain why caching is reserved for pure functions.
