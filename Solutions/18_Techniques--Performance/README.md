# Performance: Solutions

## 1. Timing random targets instead of the worst case

> `membership.py` sets `target` to the worst case, the last element.
> Measure the average case by timing lookups of many random targets,
> and see whether the conclusion changes.

```python
# exercise_1.py
import random
import timeit
from benchmark import report

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
random.seed(1)
targets = [random.randrange(n) for _ in range(200)]

def list_lookups() -> None:
    for t in targets:
        t in as_list

def set_lookups() -> None:
    for t in targets:
        t in as_set

t_list = timeit.timeit(list_lookups, number=20)
t_set = timeit.timeit(set_lookups, number=20)
report(list=t_list, set=t_set)
print(f"set faster on average-case targets too: "
      f"{t_set < t_list}")
#: set faster on average-case targets too: True
```

The conclusion does not change. `target = n - 1` in the original
measures the single worst case for a `list` scan: the element the
scan reaches only after walking past every other one. Random targets
land in every position instead, including ones near the front that a
`list` finds quickly. The `set`'s O(1) hash lookup still beats the
`list`'s O(n) scan by a wide margin (thousands of times faster in
this run), because the scan for an average target still walks about
half the `list`, far more work than one hash lookup. The worst case
and the average case tell the same story here.
They only diverge if most real lookups cluster near
the front of the list.

## 2. Finding the crossover size

> Use `timeit` to find the collection size below which the `list` scan beats the `set` lookup on your machine.

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

On this machine, the `set` already wins starting at size `2`. Only at
size `1` does the `list` edge ahead, and even then barely. The
`set`'s advantage grows steadily as `size` increases, as the
different growth rates (`O(1)` vs. `O(n)`) predict. The crossover
point is not a fixed number. It depends on the machine, the Python
build, and even which values you store, because the race is between
one hash computation and a short linear scan that costs almost
nothing until the list grows long. Run the same loop yourself and
expect a different exact number, though the trend (the `list`'s
relative advantage, if any, evaporating almost immediately) should
look similar.

## 3. `eager_first_evens()` as one list comprehension

> Rewrite `eager_first_evens()` as a single list comprehension and measure its peak with `tracemalloc`.
> How close can an eager version get to the lazy one?

```python
# exercise_3.py
import tracemalloc
from collections.abc import Callable
from itertools import islice

n = 1_000_000

def two_lists() -> list[int]:  # The original
    squares = [x * x for x in range(n)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def one_list() -> list[int]:
    return [x * x for x in range(n) if (x * x) % 2 == 0][:5]

def lazy() -> list[int]:  # The chapter's lazy version
    squares = (x * x for x in range(n))
    evens = (s for s in squares if s % 2 == 0)
    return list(islice(evens, 5))

def peak_of(func: Callable[[], list[int]]) -> int:
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

result = one_list()
print(result, result == two_lists() == lazy())
#: [0, 4, 16, 36, 64] True
two, one = peak_of(two_lists), peak_of(one_list)
print("peak ratio, one list to two:", round(one / two, 1))
#: peak ratio, one list to two: 0.5
print(f"lazy peak under 1% of one list: "
      f"{peak_of(lazy) * 100 < one}")
#: lazy peak under 1% of one list: True
```

`one_list()` filters `x * x` directly instead of first building a
`squares` list and then an `evens` list from it, so the
million-element `squares` list is gone. Peak memory drops to about
half of the two-list version's. That is as close as an eager version
gets, and the last line shows how far away it still is: the lazy
peak is under one percent of it. The comprehension must build and
hold the whole list of half a million even squares before `[:5]`
discards nearly all of them. Restructuring the eager version cannot
close that gap, because an eager version computes every value up
front. The lazy generator pipeline stops when `islice()` has its
five values, so it builds no large collection.

## 4. Caching a function with a side effect

> Apply `@cache` to a function that prints as a side effect,
> and demonstrate that repeated calls skip the printing.
> Explain why caching suits only pure functions.

```python
# exercise_4.py
from functools import cache

@cache
def noisy(n: int) -> int:
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
time. Skipping the body is the reason to cache only pure functions.
A cache assumes that calling the function again is unnecessary,
because the answer cannot have changed and nothing observable
happens during the call besides computing that answer. An impure
function breaks that assumption. Any side effect the function
performs, such as printing, writing a file, or incrementing a
counter, occurs on the first call with a given argument, and
the cache silently skips it on every repeat.

## 5. Popping a heap correctly

> In `heap_corruption.py`, replace `heap.pop(0)` with `heappop(heap)`.
> Pop three times, printing the heap after each one,
> and confirm `heap[0]` is the smallest remaining value every time.
> Why does the list still look unsorted after a correct pop?

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

Each pop returns the true smallest remaining value: `3`, then `4`,
then `5`. After every pop, `heap[0]` is still the minimum. Compare
`heap.pop(0)` in the original, which returns the right value once and
then leaves a list that is no longer a heap.

The list still looks unsorted because a heap does not guarantee
sorted order. A heap guarantees that the element at position `i` is
no larger than its two children at positions `2i + 1` and `2i + 2`,
which puts the smallest element at index 0 and says nothing about
the order of the rest. `heappop()` maintains that weaker property, and maintaining it
is cheap: the last element moves to the front and sinks back down
through O(log n) comparisons. Sorting the whole list on every pop
costs far more and gains nothing, since callers read only the front
element.

## 6. A subclass that forgets `__slots__`

> In `slots.py`, add `class Point3D(Point)` that declares no `__slots__` of its own.
> Confirm that an instance accepts `p.z = 3`,
> which `Point` rejects with an `AttributeError`,
> and find where the storage for it came from.

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
`('x', 'y')`, inherited from `Point`, so reading that attribute makes
the subclass look slotted while it still carries a `__dict__`.

The memory saving is quietly lost. Every `Point3D` pays for both the
two slots and a dictionary. A subclass of a slotted class must
declare `__slots__` itself, using an empty tuple when it adds no
fields of its own.

## 7. Global monitoring versus two local attachments

> In `monitoring_counts.py`,
> swap `set_local_events()` for `set_events()` and say which entry in the `Counter` is new and why.
> Then get the same two counts back using two local attachments instead,
> and explain what the two versions stop agreeing about in a larger program.

```python
# exercise_7.py
import sys
from collections import Counter
from types import CodeType
from typing import Final

monitoring = sys.monitoring
TOOL: Final[int] = monitoring.PROFILER_ID
PY_START: Final[int] = monitoring.events.PY_START
NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS
counts: Counter[str] = Counter()

def on_start(code: CodeType, offset: int) -> None:
    counts[code.co_name] += 1

def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def square(n: int) -> int:
    return n * n

monitoring.use_tool_id(TOOL, "call counter")
monitoring.register_callback(TOOL, PY_START, on_start)
for target in (fib, square):
    monitoring.set_local_events(TOOL, target.__code__,
                                PY_START)
print(fib(10), square(4))
#: 55 16
for target in (fib, square):
    monitoring.set_local_events(TOOL, target.__code__,
                                NO_EVENTS)
monitoring.free_tool_id(TOOL)
print(counts)
#: Counter({'fib': 177, 'square': 1})
```

With `set_events()` in place of the local attachment, the new entry
is `'square': 1`. Nothing else appears, because `PY_START` fires when
a Python code object starts running, and the module's own frame
starts before the tool attaches. CPython implements `print()` in C,
so it never starts a Python frame, and a program this small has no
other candidates.

The two local attachments above produce the identical `Counter`, and
that agreement is an artifact of the example's size. In a real
program `set_events()` reports every Python function the process
runs, including library code you did not write and never wanted
counted, and it pays the callback cost on all of it. Local
attachment names the code objects you care about and leaves the rest
running at full speed. Global monitoring answers "what ran."
Local monitoring answers "how often did *this* run," which is the
question you already had when you opened `sys.monitoring` instead of
a profiler.

## 8. Reading `tottime` against `cumtime`

> Profile a script of your own with `uv run python -m cProfile -s cumulative`.
> Name the function with the largest `tottime` and the one with the largest `cumtime`,
> and explain why they are usually not the same function.

Any script works. This one makes the two columns disagree on purpose:

```python
# exercise_8.py
def inner() -> int:
    return sum(i * i for i in range(100_000))

def outer() -> int:
    return inner() + inner()

print(outer() > 0)
#: True
```

Run `uv run python -m cProfile -s cumulative exercise_8.py`. The
largest
`cumtime` belongs to `exec`, then `<module>`, then `outer`. The
largest `tottime` belongs to `{built-in method builtins.sum}`, with
the generator expression inside `inner()` second: the largest of the
script's own Python frames, where the arithmetic happens.

They differ because the two columns measure different things.
`cumtime` is the time from entering a function to leaving it,
including everything it called, so a caller can never show a smaller
`cumtime` than the work beneath it. Every caller on the path
accumulates the same time. `tottime` excludes the callees, so it
attributes time to the frame that is executing.

A function high on `cumtime` and near zero on `tottime` is a
pass-through: it is slow only because of what it calls, and rewriting
it changes nothing. The two coincide only for a leaf function, one
that calls nothing else, which is why the bottom of a call chain is
where the two lists finally meet.

## 9. A compact `array` is not a faster `array`

> `compact_array.py` compares an `array` against a `list` of the same floats.
> Time an element-by-element sum over each with `timeit`.
> The `array` uses a quarter of the memory: is it also faster to iterate,
> and why not?

```python
# exercise_9.py
import timeit
from array import array
from collections.abc import Callable
from benchmark import report

n = 200_000
as_list = [float(i) for i in range(n)]
as_array = array("d", as_list)

def best(f: Callable[[], float]) -> float:
    return min(timeit.repeat(f, number=20, repeat=5))

t_list = best(lambda: sum(as_list))
t_array = best(lambda: sum(as_array))
report(list=t_list, array=t_array)
print(f"array is slower to iterate: {t_array > t_list}")
#: array is slower to iterate: True
```

Not faster: on one machine the `array` took about 1.4 times as long
as the `list`. The memory saving is real (the chapter measures
325,176 bytes against 80,080). The speed saving does not exist.

A `list` of floats stores pointers to `float` objects that already
exist, so reading one hands back a reference. An `array` stores raw
eight-byte doubles with no objects at all, so reading one has to
build a fresh `float` object to hand to Python. That allocation, on
every single element, is the cost that eats the advantage of the
tighter layout.

That cost is the chapter's NumPy lesson arriving early: a compact
layout pays off when the loop over it leaves Python. `sum()` over an
`array` stays in Python and boxes every element. A NumPy `sum` over
the same bytes creates no Python object per element, which is why
vectorizing wins where `array` alone does not.

## 10. `"".join()` against `+=`, at two sizes

> Time `"".join(parts)` against `+=` in a loop for 10,000 short strings,
> then repeat at 100 strings.
> At which size does the difference stop mattering,
> and which of the two would you write anyway?

```python
# ch18_join_vs_concat.py
import timeit
from benchmark import report

def build_join(parts: list[str]) -> str:
    return "".join(parts)

def build_concat(parts: list[str]) -> str:
    out = ""
    for p in parts:
        out += p
    return out

many = ["ab"] * 10_000
few = ["ab"] * 100
assert build_join(many) == build_concat(many)

j_many = timeit.timeit(lambda: build_join(many), number=200)
c_many = timeit.timeit(lambda: build_concat(many),
                       number=200)
report(join=j_many, concat=c_many)
print(f"join wins at 10,000 parts: {j_many < c_many}")
#: join wins at 10,000 parts: True

j_few = timeit.timeit(lambda: build_join(few), number=200)
c_few = timeit.timeit(lambda: build_concat(few), number=200)
print(f"join still wins at 100 parts: {j_few < c_few}")
#: join still wins at 100 parts: True
print(f"both under 50 microseconds per call at 100 parts: "
      f"{max(j_few, c_few) / 200 < 50e-6}")
#: both under 50 microseconds per call at 100 parts: True
```

The ratio does not go away. One machine measured `join` about 19
times faster at 10,000 parts and about 7 times faster at 100. What
goes away is the amount at stake: at 100 short strings both versions
finish in a couple of microseconds, so the loop must run thousands
of times before the choice shows up in a profile.

That is the answer to "at which size does it stop mattering": not at
a size where the two become equally fast, but at a size where both
are fast enough that the difference is below anything you would
measure.

Write `join()` anyway. It is one line instead of three, it says what
the result is rather than how it accumulates, and it is the version
that keeps working when the 100 parts turn into 100,000. CPython
does special-case `out += p` when `out` has a single reference,
resizing in place instead of copying, which is why the loop is merely
slower rather than quadratic. That optimization is an implementation
detail, and it disappears the moment a second name refers to the
string the loop is building.

## 11. `bisect()` and `bisect_left()` against duplicates

> `bisect_search.py` uses `bisect()` and `search_comparison.py` uses `bisect_left()`.
> Build a sorted list with duplicates,
> run both against a value that appears three times,
> and explain which one you need to find the first occurrence and which one you need to insert after the last.

```python
# ch18_bisect_duplicates.py
import bisect

xs = [1, 3, 5, 5, 5, 7, 9]
left = bisect.bisect_left(xs, 5)
right = bisect.bisect(xs, 5)  # bisect() is bisect_right()
print(left, right)
#: 2 5
print(xs[left])  # The first 5
#: 5
print(xs[right])  # One past the last 5
#: 7
print(xs[left:right])  # Every 5, as a slice
#: [5, 5, 5]

bisect.insort(xs, 5)  # insort() is insort_right()
print(xs)
#: [1, 3, 5, 5, 5, 5, 7, 9]
```

`bisect_left()` finds the first occurrence. It returns the position
before any equal elements, so `xs[left]` is the target when the
target is present, which is what a membership test needs and what
`search_comparison.py` relies on.

`bisect()`, the alias for `bisect_right()`, returns the position
after the last equal element. That is the position to insert at when
you want a new duplicate to land after the existing ones. It is the
wrong index to read: `xs[right]` is the next larger value, or an
`IndexError` when the target is the largest element in the list.

The pair together answers a third question the chapter does not
raise. `xs[left:right]` is the run of equal values, and
`right - left` counts them, both in O(log n) with no scan.

## 12. Which build am I running, and does the JIT show up?

> Run `jit_status.py` on your own interpreter and say which of the three states it reports.
> If it reports the second,
> run `membership.py` under `PYTHON_JIT=1` and `PYTHON_JIT=0` with the `--numbers` flag,
> and compare the two `ratio` lines.
> Explain why a listing this small is a poor test of the JIT.

```python
# ch18_jit_probe.py
import sys

print(sys._jit.is_available(), sys._jit.is_enabled())
```

The listing carries no `#:` line, because its output depends on the
interpreter. The book's build prints `False False`.
The two flags name the state directly. `False False` means the build
has no JIT compiled in, so `PYTHON_JIT` does nothing. `True False` is
the python.org Windows and macOS shape, built with
`--enable-experimental-jit=yes-off`: the compiler sits in the binary,
waiting for `PYTHON_JIT=1`. `True True` means the JIT is already
running, and `PYTHON_JIT=0` switches it back off.

On a `True False` build, the comparison is two runs of the same file
with nothing else changed. `tip` and `uv run` use the project's own
interpreter, which has no JIT, so run the file with that build's
`python`, from the chapter directory with `utils/` on the import path
(`tip membership` prints those commands in your shell's syntax):

    $ cd Examples/18_Techniques--Performance
    $ PYTHON_JIT=0 PYTHONPATH=../utils python membership.py --numbers
    $ PYTHON_JIT=1 PYTHONPATH=../utils python membership.py --numbers

`membership.py` is a poor subject for that comparison, for three
reasons.

The measured work happens in C, not in bytecode. `target in as_list`
and `target in as_set` both run their loops in the interpreter's own
C code, so almost none of the time the listing reports is time the
JIT could compile. The advice in [Write Idiomatic
Python](../../Chapters/18_Techniques--Performance.md#write-idiomatic-python) speeds
a program up for the same reason: work handed to C is work the
interpreter skips, and the JIT compiles only what the interpreter
runs.

The program is too short to get hot. The JIT compiles a code path
after it has run often enough to look worth compiling. A script that
starts, times two lookups, and exits pays the tracing and
compilation cost on whatever it does reach, then exits before that
machine code earns the cost back.

The listing prints a ratio, not a duration. `set at least 100x
faster` compares the two lookups against each other, so anything
that speeds up or slows down both of them equally leaves that ratio
alone. On a python.org 3.15 build, the `--numbers` lines from the
two runs differ by no more than two runs under the same setting do.

A better subject runs a Python-level loop over Python objects, long
enough to cross the compiler's threshold and keep going:
`count_primes()` from the Numba section, at its full `limit`, timed
with `min(timeit.repeat(...))`. Expect a single-digit percentage
either way, and run-to-run noise of the same size. That noise is why
`pyperformance` reports a geometric mean over dozens of benchmarks
instead of one number from one program.
