# Performance: Solutions

## 1. Timing random targets instead of the worst case

```python
# exercise_1.py
import random
import timeit

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
random.seed(1)
targets = [random.randrange(n) for _ in range(200)]

def list_lookups():
    for t in targets:
        t in as_list

def set_lookups():
    for t in targets:
        t in as_set

t_list = timeit.timeit(list_lookups, number=20)
t_set = timeit.timeit(set_lookups, number=20)
print(f"set faster on average-case targets too: {t_set < t_list}")
#: set faster on average-case targets too: True
```

The conclusion does not change. `target = n - 1` in the original
measures the single worst case for a `list` scan (the element it has
to walk past every other element to find), but random targets average
in every position, including ones a `list` finds quickly near the
front. Even so, a `set`'s O(1) hash lookup beats a `list`'s O(n) scan
on average by a wide margin (thousands of times faster in this run),
because most random targets still require scanning roughly half the
`list` on average, which is already far more work than one hash
lookup. The worst case and the average case tell the same story here;
they would only diverge if most real lookups clustered very close to
the front of the list.

## 2. Finding the crossover size

```python
# exercise_2.py
import timeit

for size in (1, 2, 5, 10, 20, 50, 100, 200, 500):
    small_list = list(range(size))
    small_set = set(small_list)
    target = size - 1
    t_list = timeit.timeit(
        lambda: target in small_list, number=20_000)
    t_set = timeit.timeit(
        lambda: target in small_set, number=20_000)
    winner = "list" if t_list < t_set else "set"
    print(size, winner)
```

On this machine, the `set` already wins starting at size `2`; only at
size `1` does the `list` edge ahead, and even then by very little. The
`set`'s advantage grows steadily as `size` increases, exactly as the
different growth rates (`O(1)` vs. `O(n)`) predict. This crossover
point is not a fixed number: it depends on the machine, the Python
build, and even which specific values are stored, since it is really a
race between one hash computation and a short linear scan whose cost
only becomes visible once the scan gets long enough to matter. Run
the same loop yourself and expect a different exact number, though the
trend (the `list`'s relative advantage, if any, evaporating almost
immediately) should look similar.

## 3. `eager_first_evens()` as one list comprehension

```python
# exercise_3.py
import tracemalloc

N = 1_000_000

def eager_first_evens_comprehension():
    return [x * x for x in range(N) if (x * x) % 2 == 0][:5]

tracemalloc.start()
result = eager_first_evens_comprehension()
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(result)
#: [0, 4, 16, 36, 64]
```

Collapsing the two comprehensions into one, filtering `x * x` directly
instead of first building a `squares` list and then an `evens` list
from it, removes one of the two million-element intermediate lists.
Peak memory drops accordingly, roughly half of the original two-list
version, but it is still enormously larger than the lazy version's
peak: this comprehension still must build and hold the entire
`evens` list before slicing `[:5]` can throw almost all of it away.
No amount of restructuring the eager version closes that gap, because
the eager style, by its nature, computes every value up front; only
the lazy generator pipeline, which stops the moment `islice()` has its
five values, avoids the large intermediate collection entirely.

## 4. Caching a function with a side effect

```python
# exercise_4.py
from functools import cache

@cache
def noisy(n):
    print(f"computing noisy({n})")
    return n * n

print(noisy(3))
#: computing noisy(3)
#: 9
print(noisy(3))
#: 9
print(noisy(3))
#: 9
```

The `"computing noisy(3)"` message prints only once, on the first
call. Every later call with the same argument returns the cached
result directly, without running the function body again, so the
print statement (and any other side effect) never happens a second
time. This is exactly why caching is reserved for pure functions: a
cache is a promise that calling the function again is unnecessary,
because the answer cannot have changed and nothing observable happens
during the call besides computing that answer. Caching an impure
function silently breaks that promise. Any side effect the function
performs, printing, writing a file, incrementing a counter, happens
only on the first call with a given argument and is silently skipped
on every repeat, which is rarely what you want.

## 5. Popping a heap correctly

```python
# exercise_5.py
from heapq import heapify, heappop

heap = [10, 9, 8, 7, 6, 5, 4, 3]
heapify(heap)
print(heap)
#: [3, 6, 4, 7, 10, 5, 8, 9]

for _ in range(3):
    smallest = heappop(heap)
    print(smallest, heap, heap[0] == min(heap))
#: 3 [4, 6, 5, 7, 10, 9, 8] True
#: 4 [5, 6, 8, 7, 10, 9] True
#: 5 [6, 7, 8, 9, 10] True
```

Each pop returns the true smallest remaining value, `3`, `4`, `5`, and
`heap[0]` is still the minimum after every one of them. Compare this
with `heap.pop(0)` in the original, which returns the right value once
and leaves the list no longer a heap.

The list still looks unsorted because a heap was never meant to be
sorted. It only guarantees that every element is smaller than its two
children at positions `2i + 1` and `2i + 2`, which puts the smallest
element at index 0 and says nothing about the order of the rest.
`heappop()` maintains that weaker property, and maintaining it is
cheap: the last element moves to the front and sinks back down through
O(log n) comparisons. Sorting all of it on every pop would cost far
more and buy nothing, since only the front element is ever read.

## 6. A subclass that forgets `__slots__`

```python
# exercise_6.py

class Point:
    __slots__ = ("x", "y")
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Point3D(Point):  # Declares no __slots__ of its own
    pass

p = Point3D(1, 2)
p.z = 3  # type: ignore
print(vars(p))
#: {'z': 3}
print(hasattr(Point(1, 2), "__dict__"))
#: False
print(Point3D.__slots__)
#: ('x', 'y')
```

`Point` refuses `p.z = 3` with an `AttributeError`, but `Point3D`
accepts it, and `vars(p)` shows where the value went: an instance
`__dict__` that the base class does not have.

Declaring `__slots__` does not disable the instance dictionary for a
whole hierarchy. It only omits one from the class that declares it.
Any subclass that does not declare its own `__slots__` gets the
default behavior, a `__dict__`, and inherits the parent's slots
alongside it. The last line shows the trap: `Point3D.__slots__` reads
`('x', 'y')`, inherited from `Point`, so an attribute lookup suggests
the subclass is slotted when it is not.

The memory saving is quietly lost. Every `Point3D` pays for both the
slot descriptors and a dictionary. A subclass of a slotted class must
declare `__slots__` itself, using an empty tuple when it adds no
fields of its own.
