# Performance: Solutions

## 1. Timing random targets instead of the worst case

> `membership.py` sets `target` to the worst case, the last element.
> Measure the average case by timing lookups of many random targets,
> and see whether the conclusion changes.

<details>
<summary>Where to look</summary>

[Benchmark Alternatives with `timeit`](../../Chapters/18_Techniques--Performance.md#benchmark-alternatives-with-timeit)
times lookups of one target, the last element,
which is the worst case for a `list` scan.
Build a list of targets with `random.randrange()`, seeded so the run repeats.
Time a loop over all of them against the `list`, then against the `set`,
and compare the two totals.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
import random
import timeit
from benchmark import report

def list_lookups() -> None:
    ...

def set_lookups() -> None:
    ...
```

<details>
<summary>Done when</summary>

your file times a seeded list of random targets against both the `list` and the `set` and prints `True` for the `set` total being smaller.
The conclusion of `membership.py` survives:
the solution's run still finds the `set` thousands of times faster.

<details>
<summary>Solution</summary>

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

The conclusion stays the same.
`target = n - 1` in the original measures the single worst case for a `list` scan:
the element the scan reaches last, after walking past every other one.
Random targets cover every position,
including targets near the front that a `list` finds quickly.
The scan for an average target walks about half the `list`,
far more work than one hash lookup.
The `set`'s O(1) lookup therefore still beats the `list`'s O(n)
scan by a wide margin, thousands of times faster in this run.
A worst-case measurement misrepresents a program whose lookups cluster near the front of the list,
where a scan finds them quickly.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Finding the crossover size

> Use `timeit` to find the collection size below which the `list` scan beats the `set` lookup on your machine.

<details>
<summary>Where to look</summary>

[Benchmark Alternatives with `timeit`](../../Chapters/18_Techniques--Performance.md#benchmark-alternatives-with-timeit)
compares a `list` against a `set` at one large size.
Repeat that comparison in a loop over a ladder of small sizes,
building both collections at each size.
Print the faster one per size and look for where the winner changes.

<details>
<summary>Done when</summary>

your loop prints one winner for each size in a ladder that starts at `1`,
and you can name the smallest size at which the `set` wins.
Expect a small number:
on the book's machine the `list` wins at size `1` and the `set` wins from `2` on.

<details>
<summary>Solution</summary>

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

On this machine, the `list` is faster at size `1`, by a small margin.
The `set` wins from size `2` on, and its advantage grows with `size`,
as the growth rates (`O(1)` vs. `O(n)`) predict.

The crossover point depends on the machine, the Python build,
and the values you store,
because the timing compares one hash computation against a short linear scan that stays fast until the list grows long.
Run the same loop yourself and expect a different number,
though the trend should look similar.
The `set` should win within the first few sizes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. `eager_first_evens()` as one list comprehension

> Rewrite `eager_first_evens()` as a single list comprehension and measure its peak with `tracemalloc`.
> How close can an eager version get to the lazy one?

<details>
<summary>Where to look</summary>

[Lazy Evaluation with Generators](../../Chapters/18_Techniques--Performance.md#lazy-evaluation-with-generators)
compares an eager two-list version with a lazy pipeline.
Fold the squaring and the evenness test into one comprehension,
so it builds one list instead of two.
Measure each version's peak with `tracemalloc.get_traced_memory()`,
and compare both against the lazy version.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import tracemalloc
from collections.abc import Callable
from itertools import islice

def two_lists() -> list[int]:  # The original
    ...

def one_list() -> list[int]:
    ...

def lazy() -> list[int]:  # The chapter's lazy version
    ...

def peak_of(func: Callable[[], list[int]]) -> int:
    ...
```

<details>
<summary>Done when</summary>

your single comprehension returns `[0, 4, 16, 36, 64]`,
equal to both of the chapter's versions,
and its `tracemalloc` peak is about half the peak of `eager_first_evens()`,
a ratio near `0.5`.
The lazy version's peak still comes in under 1% of yours.

<details>
<summary>Solution</summary>

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

**Build one list.**
`one_list()` filters `x * x` instead of first building a `squares` list and then an `evens` list from it,
so the million-element `squares` list disappears.
One list is as close as an eager version gets.

**Measure the remaining gap.**
The comprehension must build and hold the whole list of half a million even squares before `[:5]` discards nearly all of them.
Restructuring the eager version cannot close that gap,
because an eager version computes every value up front.
The lazy generator pipeline stops when `islice()` has its five values,
so it computes nine squares and stores the five even ones it returns.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Caching a function with a side effect

> Apply `@cache` to a function that prints as a side effect,
> and demonstrate that repeated calls skip the printing.
> Explain why caching suits only pure functions.

<details>
<summary>Where to look</summary>

[Caching](../../Chapters/18_Techniques--Performance.md#caching)
shows `@cache` returning a stored result for a repeated argument.
Decorate a function that prints before it returns,
then call it three times with the same argument.
Count how many times the message appears,
and ask what else the function body would have done on each call.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from functools import cache

@cache
def noisy(n: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

three calls with the same argument print your function's message once,
before the first result, and print the result three times.
You can say what else, besides the computation,
a cached function skips on a repeat call.

<details>
<summary>Solution</summary>

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

Every later call with the same argument returns the cached result and skips the function body,
along with its `print()` call and any other side effect.

Skipping the body is the reason to cache only pure functions.
A cache assumes its stored answer can stand in for a repeat call,
because the same argument gives the same answer and computing that answer is all the call does.
An impure function breaks that assumption.
Each of its calls also prints, writes a file, or increments a counter.
The cache lets that side effect run on the first call with a given argument and silently skips it on every repeat.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Popping a heap correctly

> In `heap_corruption.py`, replace `heap.pop(0)` with `heappop(heap)`.
> Pop three times, printing the heap after each one,
> and confirm `heap[0]` is the smallest remaining value every time.
> Why does the list still look unsorted after a correct pop?

<details>
<summary>Where to look</summary>

[Heap](../../Chapters/18_Techniques--Performance.md#heap)
shows `list.pop(0)` breaking the heap ordering that `heappop()` maintains.
Call `heapify()`, then pop three times with `heappop()`,
printing the heap and a check of `heap[0]` against `min()` each time.
For the last question, compare the heap ordering with what "sorted" requires.

<details>
<summary>Done when</summary>

your three `heappop()` calls return `3`, `4`, and `5`,
`heap[0] == min(heap)` prints `True` after each one,
and the heap ends as `[6, 7, 8, 9, 10]`.
You can state the rule the heap ordering enforces between an element and the positions below it.

<details>
<summary>Solution</summary>

If you keep `heap.pop(0)` from the original, the three pops return `3`, `6`,
and `4`, and the check prints `False` after the first and the third.
Removing the front element shifts the rest of the list one place left,
and the shifted list breaks the heap ordering.
The solution calls `heappop()`,
which restores that ordering after every removal,
so `heap[0]` stays the smallest value.

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

**Check the invariant after each pop.**
`heap.pop(0)` in the original returns the right value on the first pop,
but it shifts `6` to the front, ahead of the smaller `4`,
so the second pop returns `6`.

The list still looks unsorted because a heap guarantees a weaker order than sorting.
A heap guarantees that the element at position `i` is less than or equal to both of its children at positions `2i + 1` and `2i + 2`,
which puts the smallest element at index 0 and leaves the order of the rest open.

`heappop()` maintains that weaker property in O(log n) comparisons.
The last element moves to index 0,
then moves down the tree past each smaller child until the heap ordering holds again.
Sorting the whole list on every pop does far more work.
The extra order goes unused, since callers read only the front element.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 6. A subclass that forgets `__slots__`

> In `slots.py`, add `class Point3D(Point)` that declares no `__slots__` of its own.
> Confirm that an instance accepts `p.z = 3`,
> which `Point` rejects with an `AttributeError`,
> and find what provides the storage for `z`.

<details>
<summary>Where to look</summary>

[When Slots Does Not Fit](../../Chapters/18_Techniques--Performance.md#when-slots-does-not-fit)
covers what a slotted class gives up,
and [Slots](../../Chapters/18_Techniques--Performance.md#slots)
shows what `__slots__` removes.
Subclass a slotted class without declaring `__slots__`, assign a new attribute,
and inspect the instance with `vars()`.
Ask which class in the hierarchy still creates a `__dict__` for each instance.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x: int, y: int) -> None:
        ...

class Point3D(Point):  # Declares no __slots__ of its own
    pass
```

<details>
<summary>Done when</summary>

`p.z = 3` on a `Point3D` succeeds and `vars(p)` prints `{'z': 3}`,
while `hasattr(Point(1, 2), "__dict__")` prints `False`.
You can explain why `Point3D.__slots__` still reads `('x', 'y')` although the subclass stores `z`.

<details>
<summary>Solution</summary>

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

**Locate the new attribute's storage.**
`Point` rejects `p.z = 3` with an `AttributeError`, but `Point3D` accepts it.
`vars(p)` shows what holds the value: an instance `__dict__`,
which `Point` instances do not have.
Declaring `__slots__` removes the `__dict__` from the declaring class alone.
A subclass that declares no `__slots__` of its own gets the default `__dict__`,
alongside the slots it inherits.

**Expose the inherited `__slots__`.**
The last line shows why the subclass's `__dict__` is easy to miss.
`Point3D.__slots__` reads `('x', 'y')`, inherited from `Point`,
so reading that attribute makes the subclass look slotted while it still carries a `__dict__`.

`Point3D` loses the memory saving silently.
Every instance holds both the two slots and a dictionary.
A subclass of a slotted class must declare `__slots__`,
using an empty tuple when it inherits all its fields.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. Global monitoring versus two local attachments

> In `monitoring_counts.py`,
> swap `set_local_events()` for `set_events()` and say which entry in the `Counter` is new and why.
> Then get the same two counts back using two local attachments instead,
> and explain what the two versions stop agreeing about in a larger program.

<details>
<summary>Where to look</summary>

[Measuring One Function with `sys.monitoring`](../../Chapters/18_Techniques--Performance.md#measuring-one-function-with-sys-monitoring)
attaches `PY_START` to chosen code objects with `set_local_events()`.
`set_events()` attaches the same event to every Python code object in the process,
so read the `Counter` for entries beyond your two functions.
For the local version,
call `set_local_events()` once per function on its `__code__`,
and turn each off again before `free_tool_id()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
import sys
from collections import Counter
from types import CodeType
from typing import Final

monitoring = sys.monitoring
TOOL: Final[int] = monitoring.PROFILER_ID
PY_START: Final[int] = monitoring.events.PY_START
NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS

def on_start(code: CodeType, offset: int) -> None:
    ...

def fib(n: int) -> int:
    ...

def square(n: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

the `set_events()` run prints `Counter({'fib': 177, 'square': 1})`,
and your version with two `set_local_events()` attachments prints the same `Counter`,
switching both off before `free_tool_id()`.
You can say which functions a larger program adds to the global count.

<details>
<summary>Solution</summary>

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

With `set_events()` in place of the local attachment,
the new entry is `'square': 1`.
It is the only addition,
because the interpreter reports `PY_START` when a Python code object starts running,
and the module's own stack frame starts before the tool attaches.
CPython implements `print()` in C, so it starts no Python stack frame.
A program this small has no other candidates.

The two local attachments above produce the same `Counter`.
That agreement is an artifact of the example's size.
In a real program `set_events()` reports every Python function the process runs,
so library code fills the `Counter` beside your own functions,
and the callback runs on every call to each of those functions.
Local attachment specifies the code objects you care about and leaves the rest running at full speed.
Global monitoring answers "what ran."
Local monitoring answers "how often did this run,"
which is the question you had when you opened `sys.monitoring` instead of a profiler.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Reading `tottime` against `cumtime`

> Profile a script of your own with `uv run python -m cProfile -s cumulative`.
> Name the function with the largest `tottime` and the one with the largest `cumtime`,
> and explain why they are usually not the same function.

<details>
<summary>Where to look</summary>

[Reading a `cProfile` Report](../../Chapters/18_Techniques--Performance.md#reading-a-cprofile-report)
defines the two columns.
Write a script in which one function calls another twice,
so a caller sits above the work and a callee performs it.
Run it under `cProfile`,
then compare the top row sorted by `cumtime` with the top row sorted by `tottime`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
def inner() -> int:
    ...

def outer() -> int:
    ...
```

<details>
<summary>Done when</summary>

you can name, from your own `cProfile -s cumulative` report,
the function with the largest `cumtime` and the one with the largest `tottime`,
and they differ.
You can also say why a caller that does little work of its own still ranks high on `cumtime`.

<details>
<summary>Solution</summary>

Any script works.
This example makes the two columns disagree on purpose:

```python
# exercise_8.py
def inner() -> int:
    return sum(i * i for i in range(100_000))

def outer() -> int:
    return inner() + inner()

print(outer() > 0)
#: True
```

Run `uv run python -m cProfile -s cumulative exercise_8.py`.
The largest `cumtime` belongs to `exec`, then `<module>`, then `outer`.
The largest `tottime` belongs to `{built-in method builtins.sum}`.
The generator expression inside `inner()` comes second.
It is the largest of the script's own Python stack frames,
because the arithmetic runs there.

The two columns pick different functions because they measure different things.
`cumtime` is the time from entering a function to leaving it,
including everything it called,
so a caller's `cumtime` always covers the work beneath it.
Every caller on the path accumulates the same time.
`tottime` excludes the callees,
so it attributes time to the stack frame that is executing.

A function high on `cumtime` and near zero on `tottime` is a pass-through.
It is slow because of what it calls, so the gains are in its callees,
and in how often it calls them.

The two columns hold the same value only for a leaf function,
one that does all of its work in its own stack frame.
The top of the `cumtime` ranking is the outermost stack frame,
which calls everything and does almost none of the work,
so the two rankings usually open on different functions.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. A compact `array` is not a faster `array`

> `compact_array.py` compares an `array` against a `list` of the same floats.
> Time an element-by-element sum over each with `timeit`.
> The `array` uses a quarter of the memory.
> Is iterating over the `array` also faster, and why not?

<details>
<summary>Where to look</summary>

[Array Instead of List](../../Chapters/18_Techniques--Performance.md#array-instead-of-list)
measures the memory saving of `array`,
and [Vectorize with NumPy](../../Chapters/18_Techniques--Performance.md#vectorize-with-numpy)
shows where a compact layout saves time.
Time `sum()` over the `list` and over the `array`,
taking the `min()` of several `timeit.repeat()` rounds.
For the why, consider what Python must hand to your code for each element of each container.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
import timeit
from array import array
from collections.abc import Callable
from benchmark import report

def best(f: Callable[[], float]) -> float:
    ...
```

<details>
<summary>Done when</summary>

your file times `sum()` over each container with the `min()` of several `timeit.repeat()` rounds and prints `True` for the `array` taking longer;
the solution's run measured about 1.4 times as long.
You can say what Python hands your code for each element of each container.

<details>
<summary>Solution</summary>

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

Not faster.
On one machine the `array` took about 1.4 times as long as the `list`.
The memory saving is real (the chapter measures 325,176 bytes against 80,080),
but the `array` is the slower of the two.

A `list` of floats stores pointers to existing `float` objects,
so reading an element hands back a reference.
An `array` stores raw eight-byte doubles instead of objects,
so reading an element builds a fresh `float` object to hand to Python.
That allocation, on every element,
outweighs the advantage of the tighter layout.

The per-element allocation previews the chapter's NumPy lesson.
A compact layout saves time when the loop over it reads raw values instead of Python objects.
`sum()` over an `array` works on Python objects and boxes every element.
NumPy's `sum()` adds the same raw doubles in a C loop,
which is why vectorizing is faster and `array` alone is not.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. `"".join()` against `+=`, at two sizes

> Time `"".join(parts)` against `+=` in a loop for 10,000 short strings,
> then repeat at 100 strings.
> At which size does the difference stop mattering,
> and which of the two would you write regardless?

<details>
<summary>Where to look</summary>

[Trusting a Measurement](../../Chapters/18_Techniques--Performance.md#trusting-a-measurement)
says how to read a `timeit` result,
and [Is It Too Slow?](../../Chapters/18_Techniques--Performance.md#is-it-too-slow)
says when a difference justifies an optimization.
Write one function that joins a list of parts and one that concatenates with `+=`,
then time both at 10,000 parts and at 100.
Compare the ratio at each size, and then the absolute time per call.

<details>
<summary>The shape</summary>

```python
# The shape of ch18_join_vs_concat.py
import timeit
from benchmark import report

def build_join(parts: list[str]) -> str:
    ...

def build_concat(parts: list[str]) -> str:
    ...
```

<details>
<summary>Done when</summary>

your timings show `join()` ahead at both 10,000 and 100 parts,
and at 100 parts both versions take under 50 microseconds per call.
You can say which version you would write at either size,
and why the ratio alone does not decide whether the difference matters.

<details>
<summary>Solution</summary>

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

The ratio persists.
One machine measured `join` about 19 times faster at 10,000 parts and about 7 times faster at 100.
The absolute time shrinks.
At 100 short strings both versions finish in a couple of microseconds,
so `build_join()` and `build_concat()` must run thousands of times before the choice shows up in a profile.

The difference therefore stops mattering when both versions run fast enough that the gap falls below anything you would measure,
not when the two run equally fast.

Write `join()` at either size.
It is one line instead of three,
it says what the result is rather than how the parts accumulate,
and it stays fast when the 100 parts turn into 100,000.

The `+=` loop is merely slower rather than quadratic because CPython special-cases `out += p` when `out` has a single reference,
resizing in place instead of copying.
That optimization is an implementation detail.
CPython stops applying it as soon as a second name refers to the string the loop is building.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 11. `bisect()` and `bisect_left()` against duplicates

> `bisect_search.py` uses `bisect()` and `search_comparison.py` uses `bisect_left()`.
> Build a sorted list with duplicates,
> run both against a value that appears three times,
> and explain which one you need to find the first occurrence and which one you need to insert after the last.

<details>
<summary>Where to look</summary>

[Bisect](../../Chapters/18_Techniques--Performance.md#bisect)
uses `bisect()` to find a position in a sorted list.
Build a list in which one value repeats three times,
and print the index each of `bisect_left()` and `bisect()` returns for it.
Index the list at both positions to see which one is the target's first copy and which one is one past its last.

<details>
<summary>Done when</summary>

on a list such as `[1, 3, 5, 5, 5, 7, 9]`,
`bisect_left()` and `bisect()` return `2` and `5` for the value `5`,
and the slice between those indices is `[5, 5, 5]`.
You can say which index reads the first `5` and which one inserts after the last.

<details>
<summary>Solution</summary>

`bisect_search.py` calls `bisect()` to find an insertion point.
If you call `bisect()` to find the first `5` instead, `left` comes back as `5`,
`xs[left]` prints `7`, and `xs[left:right]` prints `[]`.
`bisect()` returns the position after the last equal element,
the right place to insert a duplicate and the wrong place to read one.
The solution uses `bisect_left()` for the first occurrence and keeps `bisect()` for the end of the run.

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

**Find the start of the run.**
`bisect_left()` returns the position before any equal elements,
so `xs[left]` is the target when the target is present.
A membership test needs that, and `search_comparison.py` relies on it.

**Find the end of the run.**
`right` is where a new duplicate goes, after the existing ones,
and it is the wrong index to read.
`xs[right]` is the next larger value,
or an `IndexError` when the target is the largest element in the list.

**Recover the whole run.**
`left` and `right` together answer a third question,
one the chapter leaves unasked.
`xs[left:right]` is the run of equal values, and `right - left` counts them.
Finding the two bounds takes O(log n) with no scan.
The slice then copies the k values between them.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 12. Which build am I running, and does the JIT show up?

> Run `jit_status.py` on your own interpreter and say which of the three states it reports.
> If it reports the second,
> run `membership.py` under `PYTHON_JIT=1` and `PYTHON_JIT=0` with the `--numbers` flag,
> and compare the two `ratio` lines.
> Explain why a listing this small is a poor test of the JIT.

<details>
<summary>Where to look</summary>

[The CPython JIT](../../Chapters/18_Techniques--Performance.md#the-cpython-jit)
describes the three states that `sys._jit.is_available()` and `sys._jit.is_enabled()` report.
Print both flags, then run `membership.py` with `--numbers` under each setting of the `PYTHON_JIT` environment variable.
For the last question, consider where the measured work runs,
how long the program lives, and what the `ratio` line compares.

<details>
<summary>Done when</summary>

you can name the state `jit_status.py` prints on your interpreter
(the book's build prints `no JIT in this build`),
and on a `JIT built in, switched off` build you have compared the two `ratio` lines.
You can give three reasons the two runs differ by about as much as run-to-run noise.

<details>
<summary>Solution</summary>

On the book's build, `jit_status.py` reports the first state,
`no JIT in this build`.

```python
# ch18_jit_probe.py
import sys

print(sys._jit.is_available(), sys._jit.is_enabled())
```

The listing's output depends on the interpreter,
so it appears here instead of in a `#:` line.
The book's build prints `False False`.

The two flags identify the state.
`False False` means the build has no JIT compiled in,
so the interpreter ignores `PYTHON_JIT`.
The python.org Windows and macOS builds report `True False`,
because python.org compiles them with `--enable-experimental-jit=yes-off`.
A `True False` binary contains the JIT compiler, and `PYTHON_JIT=1` turns it on.
`True True` means the JIT is already running,
and `PYTHON_JIT=0` switches it back off.

On a `True False` build,
the comparison is two runs of the same file that differ in `PYTHON_JIT` alone.
`tip` and `uv run` use the project's own interpreter, the `False False` build.
Run the file with the `True False` build's `python` instead,
from the chapter directory with `utils/` on the import path
(`tip membership` prints those commands in your shell's syntax):

    $ cd Examples/18_Techniques--Performance
    $ PYTHON_JIT=0 PYTHONPATH=../utils python membership.py --numbers
    $ PYTHON_JIT=1 PYTHONPATH=../utils python membership.py --numbers

`membership.py` is a poor subject for that comparison, for three reasons.

The measured work runs in C, not in bytecode.
`target in as_list` and `target in as_set` both do their work in the interpreter's C code.
The JIT compiles only the bytecode the interpreter runs,
so it could speed up almost none of the time the listing reports.
Moving work into C is also why the advice in [Write Idiomatic Python](../../Chapters/18_Techniques--Performance.md#write-idiomatic-python)
speeds a program up.

The program is too short to get hot.
The JIT compiles a code path after the path has run enough times to cross a threshold,
and it spends time tracing and compiling every path that gets that far.
`membership.py` starts, times two kinds of lookup,
and exits before the compiled code has saved as much time as the compiling took.

The `ratio` line compares the two lookups against each other,
so anything that speeds up or slows down both of them equally leaves that ratio as it was.
On a python.org 3.15 build,
the `--numbers` lines from the two runs differ by about as much as two runs under the same setting.

A better subject runs a Python-level loop over Python objects,
long enough to cross the compiler's threshold and keep going:
`count_primes()` from the [Numba section](../../Chapters/18_Techniques--Performance.md#jit-compilation-with-numba),
at its full `limit`, timed with `min(timeit.repeat(...))`.
On a python.org 3.15 build,
one machine measured `count_primes()` about 20% faster with the JIT on,
against run-to-run noise of a few percent.
Run-to-run noise is why `pyperformance` reports a geometric mean over dozens of benchmarks instead of one number from one program.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
