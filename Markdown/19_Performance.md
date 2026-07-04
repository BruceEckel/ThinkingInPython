# Performance

[[Use new profiling features in Python 3.15]]
[[May need some kind of profiling test rig to demonstrate speedups. If this takes too long for a normal 'make verify', might need to separate and create 'make profile" or something]]

Performance means at least two things when it comes to computing:

1. The speed at which an application is developed.
2. The speed at which that application executes.

Python addresses the first issue with clear syntax and extensive power and flexibility.
As to the second issue, Python is commonly considered to be slow.

## Is It Actually Too Slow?

Computer programming projects have a long history of *premature optimization*,
when the designers decide ahead of time, based on their biases,
that runtime performance will be insufficient.
This results in elaborate designs that generate excessive costs.

Python can be surprising.
A program coded in the most straightforward way, without concern for performance,
can often run fast enough for your needs.
Do not automatically assume that a simply written program will be too slow.
Try it out first. It might be fine.

If it is too slow, use Occam's Razor: try the simplest approach first.
That might be enough, and if it is, you might save a lot of time and money.

What follows is an approach to solving performance problems,
starting with the simplest techniques and getting successively more complex.

## Try a Faster Platform

There are alternative interpreters for Python, notably PyPy, which boasts a 4x to 10x speedup.

How much does a hardware upgrade cost compared to paying programmers to solve the performance problem?
If it's noticeably less, then buying new hardware might be a quick win.

## Profilers

A *profiler* looks for the slow spots in your code, so you know where to focus.
Although it is tempting to think you "have a pretty good idea where the slowdown is," we turn out to be very bad at guessing this.
A profiler tells you for sure, and keeps you from wasting your time.

I am currently most impressed with [Scalene](https://github.com/plasma-umass/scalene).

If you can narrow the problem down to a particular function, there may be techniques that speed up the algorithm used in that function.

## Benchmark Alternatives with `timeit`

[[`timeit` times small snippets, so you can compare two ways of writing the same thing once a profiler has pointed you at a hot spot]]

## Choose Better Algorithms and Data Structures

The biggest speedups usually come from a better algorithm, not faster code.
A lower Big-O complexity beats micro-optimizing a slow one.
Often this just means choosing the right container.
Use a `set` or `dict` for membership and lookup instead of scanning a `list`.
Use a `deque` (see [Containers](03_Containers.md#deque)) when you add and remove at both ends.

For data kept in sorted order, the `bisect` module finds the insertion point with binary search:

```python
# bisect_search.py
import bisect

scores = [60, 70, 75, 90]      # Must stay sorted
i = bisect.bisect(scores, 78)  # Where 78 would go
print(i)
#: 3
bisect.insort(scores, 78)      # Insert and keep it sorted
print(scores)
#: [60, 70, 75, 78, 90]

def grade(score):
    # Map a score to a letter through its cutoff boundaries:
    cutoffs = [60, 70, 80, 90]
    letters = "FDCBA"
    return letters[bisect.bisect(cutoffs, score)]

print([grade(s) for s in (55, 65, 85, 95)])
#: ['F', 'D', 'B', 'A']
```

Because `scores` stays sorted, `bisect` locates a position in O(log n)
instead of the O(n) scan a `list` would need.

When you repeatedly need the smallest item, a *heap* keeps that item reachable in O(log n).
The `heapq` module treats a plain `list` as a binary heap:

```python
# heap_queue.py
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)         # Rearrange into a heap in place
print(nums[0])              # The smallest stays at the front
#: 1
heapq.heappush(nums, 0)
print(heapq.heappop(nums))  # Remove and return the smallest
#: 0
print(heapq.nsmallest(3, [5, 1, 8, 3, 2]))
#: [1, 2, 3]
print(heapq.nlargest(2, [5, 1, 8, 3, 2]))
#: [8, 5]
```

After `heapify()` the smallest element stays at index 0,
and `nsmallest()` and `nlargest()` answer top-N questions directly.
For a priority queue shared across threads, `queue.PriorityQueue` wraps `heapq` with locking,
covered with concurrency below.

[[Frozen data structures: tuples instead of lists, and frozenset and frozendict -- shouldn't these speed up lookup?]]

## Write Idiomatic Python

[[Let the interpreter do the work: built-in functions and comprehensions instead of hand-written loops, the C-implemented standard library (`itertools`, `collections`, `functools`), `str.join` instead of `+=` in a loop, and hoisting repeated attribute or global lookups into locals]]

## Lazy Evaluation with Generators

[[Stream values with generators and `itertools` instead of building large intermediate lists, so work happens on demand and memory stays flat]]

## Caching

[[Demonstrate @cache speedup]]

## Reduce Memory Overhead

When you hold millions of objects, their per-object overhead dominates.
Three tools cut it down.

By default each instance stores its attributes in a `__dict__`.
Declaring `__slots__` replaces that dict with a fixed set of fields,
which shrinks each instance and speeds attribute access:

```python
# slots.py
class Point:
    __slots__ = ("x", "y")  # No per-instance __dict__
    def __init__(self, x, y):
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

[[Can you make a dataclass that has slots? Would that be better here?]]

The tradeoff is that instances can no longer grow attributes outside the declared set.

A `list` of numbers stores full Python objects, each with its own header.
The `array` module packs numbers into a single block of C values instead:

```python
# array_basics.py
from array import array

a = array("d", [1.0, 2.0, 3.0])  # "d" = C double
a.append(4.0)
print(a)
#: array('d', [1.0, 2.0, 3.0, 4.0])
print(a[1], a.typecode, a.itemsize)
#: 2.0 d 8
try:
    # The value must match the type code:
    a.append("x")  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

Every element shares one type, given by the type code,
so `array` stores them compactly and rejects values of the wrong type.

A `memoryview` exposes another object's memory without copying it.
Slicing a large `bytes` or `bytearray` through a view avoids duplicating the data:

```python
# memory_view.py
data = bytearray(b"ABCDEF")
view = memoryview(data)  # No copy of the underlying bytes
chunk = view[1:4]
print(bytes(chunk))
#: b'BCD'
view[0] = ord("z")       # Writes through to the original
print(data)
#: bytearray(b'zBCDEF')
print(view.nbytes)
#: 6
```

The view shares storage with `data`,
so writing through it changes the original and no bytes are copied.

## Vectorize with NumPy

[[Move numeric loops into whole-array operations. NumPy is a fast library you call, not a compiled extension you write]]

## JIT Compilation with Numba

[[`@njit` compiles numeric Python to machine code in place, a lighter step than Rust when the hot spot is number-crunching]]

## Concurrency and Parallelism

When the time goes to waiting on the outside world,
or the work could use more than one core,
the fix is not a faster function but a different architecture:
overlapping tasks with `asyncio`,
or spreading them across processes.
That is a design decision with its own chapter, [Concurrency](20_Concurrency.md).

## Converting a Slow Function to Rust

## Choosing a Strategy

[[Recap: measure first, then work down this list from the cheapest change to the most involved, stopping as soon as the program is fast enough]]
