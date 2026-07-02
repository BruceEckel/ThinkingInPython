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

## Concurrency: I/O-Bound vs CPU-Bound

*Concurrency* runs independent tasks so they overlap instead of waiting in line.
Whether overlap helps at all depends on where each task spends its time.

A task is *I/O-bound* when it spends its time waiting on something outside the process:
a network reply, a disk read, a database query.
The processor sits idle through the wait.
A task is *CPU-bound* when it spends its time computing inside the process.
The processor is busy from start to finish.

That boundary decides the tool.
Waiting can overlap on a single thread: while one task waits, the thread runs another.
Computing cannot: one core runs one stream of instructions at a time.
So I/O-bound work needs `asyncio`, and CPU-bound work needs separate processes.

The next two sections run one task both ways.
The task returns `order * 10` for an order number.
In the I/O version the time goes to a wait, outside the processor.
In the CPU version the identical result comes from computing, inside the processor.
Only that boundary changes, and it decides which tool overlaps the work.

## `asyncio`

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits something outside the processor, the loop runs another task in the meantime.
Here the same price lookup is written twice.
`io_price` waits with `asyncio.sleep`, a stand-in for a network call.
`cpu_price` computes, a stand-in for heavy work.
A `Meter` records the peak number of tasks in flight at once:

```python
# event_loop_boundary.py
import asyncio
from collections.abc import Awaitable, Callable

class Meter:
    "Counts how many tasks are active at once."
    def __init__(self) -> None:
        self.active = 0
        self.peak = 0

    def enter(self) -> None:
        self.active += 1
        self.peak = max(self.peak, self.active)

    def leave(self) -> None:
        self.active -= 1

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def io_price(order: int, meter: Meter) -> int:
    meter.enter()
    await asyncio.sleep(0.05)   # Waiting outside the processor
    meter.leave()
    return order * 10

async def cpu_price(order: int, meter: Meter) -> int:
    meter.enter()
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    meter.leave()
    return order * 10

async def run(task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    meter = Meter()
    coros = [task(o, meter) for o in orders]
    prices = await asyncio.gather(*coros)
    return prices, meter.peak

async def main() -> None:
    orders = [1, 2, 3, 4, 5]
    io_prices, io_peak = await run(io_price, orders)
    cpu_prices, cpu_peak = await run(cpu_price, orders)
    print(f"io : peak={io_peak}, prices={io_prices}")
    print(f"cpu: peak={cpu_peak}, prices={cpu_prices}")

asyncio.run(main())
#: io : peak=5, prices=[10, 20, 30, 40, 50]
#: cpu: peak=1, prices=[10, 20, 30, 40, 50]
```

Both runs use the same `asyncio.gather`, yet the peaks differ.
The I/O tasks each reach their `await` and suspend, so all five are in flight at once: peak 5.
The CPU tasks never `await`, so each runs to the end before the next starts: peak 1.
The event loop overlaps waiting, not computing.
Async did not fail. It overlapped the part that runs outside the processor, which for `cpu_price` is nothing.
The `asyncio` mechanics (`async def`, `await`, `gather`, `run`) are covered in [Simulation](35_Simulation.md).

## Parallelism

The CPU-bound task cannot overlap on one core.
Give it several cores and it can.
`ProcessPoolExecutor` runs each call in its own process, each with its own interpreter,
so the operating system can place them on different cores and run them at the same time:

```python
# parallel_cpu.py
from concurrent.futures import ProcessPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    return order * 10

def main() -> None:
    orders = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor() as pool:
        prices = list(pool.map(cpu_price, orders))
    print(prices)

if __name__ == "__main__":
    main()
```

`pool.map` sends each order to a worker process and gathers the results in order,
printing `[10, 20, 30, 40, 50]`, the same answer as the other versions.
The computation is the same `cpu_price` as before.
Only its home changed, from one shared interpreter to several.
With enough cores the wall-clock time falls toward the time of a single task, not their sum.
Threads would not have helped: CPython runs only one thread of Python at a time,
which the next section explains.

## The GIL and Free Threading

[[The GIL serializes CPU-bound threads, which is why the parallelism above reaches for processes. The free-threaded (no-GIL) builds available since 3.13 lift this and change when threads alone are enough]]

## Converting a Slow Function to Rust

## Choosing a Strategy

[[Recap: measure first, then work down this list from the cheapest change to the most involved, stopping as soon as the program is fast enough]]
