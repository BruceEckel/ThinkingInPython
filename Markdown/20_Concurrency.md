# Concurrency

[Performance](19_Performance.md) works on making one stream of instructions faster.
*Concurrency* runs independent tasks so they overlap instead of waiting in line.
Whether this overlap helps depends on where each task spends its time.

## I/O-Bound vs CPU-Bound

A task is *I/O-bound* when it spends its time waiting on something outside the process:
a network reply, a disk read, a database query.
The processor sits idle through the wait.
A task is *CPU-bound* when it spends its time computing inside the process.
The processor is busy from start to finish.

That boundary decides the tool.
Waiting can overlap on a single thread. While one task waits, the thread runs another.
Computing cannot. One core runs one stream of instructions at a time.
So I/O-bound work needs `asyncio`, and CPU-bound work needs multiple cores.
A separate process is the traditional way to get more than one core.
Later in this chapter, we show two other approaches,
each running inside a single process.

## `async def`, `await`, and the Event Loop {#asyncio-mechanics}

Four pieces make up the `asyncio` vocabulary.
`async def` defines a *coroutine function*.
Calling it runs nothing; it returns a *coroutine object*,
a description of work that has not started.
`await` starts that work and pauses the awaiting coroutine until the result is ready.
The pause is the point.
While one coroutine waits, the *event loop* runs another.
`asyncio.gather()` awaits several coroutines at once and collects their results in order.
`asyncio.run()` starts the event loop, runs one coroutine to completion,
and shuts the loop down.
It is the entry point, called once, at the top of the program:

```python
# async_mechanics.py
import asyncio

async def fetch(item: str) -> str:
    await asyncio.sleep(0.01)  # A stand-in for a network wait
    return item.upper()

async def main() -> None:
    print(await fetch("solo"))   # Await one coroutine
    print(await asyncio.gather(  # Run several concurrently
        fetch("a"), fetch("b"), fetch("c")))

asyncio.run(main())
#: SOLO
#: ['A', 'B', 'C']
```

The single `fetch("solo")` behaves like an ordinary function call with a pause inside.
The `gather()` call is where concurrency appears.
All three `fetch()` coroutines are in flight at once,
so the total wait is one sleep, not three.
An `await` is only legal inside an `async def`,
which is why the demonstration needs `main()`.

## Overlapping the Waits

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits something outside the processor, the loop runs another task in the meantime.
Here the same price lookup appears twice.
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
[Simulation](39_Simulation.md) builds a full program on these mechanics:
a pack of rats exploring a maze as cooperating tasks,
and [Observer](32_Observer.md#observer-and-io) uses `gather()` to notify
slow observers together instead of one at a time.

## A Single Thread Still Races

`asyncio` runs one coroutine at a time, never two at once.
It is tempting to conclude that shared state needs no locking there.
But "one at a time" only protects the instructions between two `await`s,
not a value that lives across one.
Two coroutines that read a shared value, `await`, then write it back
can lose an update with no thread and no GIL in sight:

```python
# async_race.py
import asyncio

counter = 0

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        await asyncio.sleep(0)  # Hand control to the event loop
        counter = value + 1  # Write back

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 50
```

Eight coroutines each add 50, so `counter` should reach 400.
Instead it stops at 50.
Every `await asyncio.sleep(0)` hands control to the event loop
before the write happens.
In each round all eight coroutines read the same value before any of
them writes, so eight additions collapse into one.
[The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races)
shows the identical failure with threads.
The mechanism differs.
A thread switch is preemptive and can land between any two bytecode
instructions, while a coroutine switch happens only at an `await`
you chose to write.
That makes the gap easier to find, not safer to leave unguarded.
A read-modify-write that spans an `await` needs `asyncio.Lock`,
the same shape of fix a lock gives across threads.

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

`ProcessPoolExecutor` is not the only way to get separate processes.
The `multiprocessing` module underneath it exposes the raw pieces:
a `Process` you start and `join()`,
and a `Queue` to carry results back,
since a process cannot return a value the way a function call does:

```python
# multiprocessing_raw.py
import multiprocessing as mp

def cpu_price(order: int, results: mp.Queue) -> None:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    results.put((order, order * 10))

def main() -> None:
    orders = [1, 2, 3, 4, 5]
    results: mp.Queue = mp.Queue()
    workers = [
        mp.Process(target=cpu_price, args=(o, results))
        for o in orders
    ]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    pairs = sorted(results.get() for _ in workers)
    print([price for _, price in pairs])

if __name__ == "__main__":
    main()
```

This prints the same `[10, 20, 30, 40, 50]`,
but everything `pool.map` did for free is now explicit:
starting each worker, waiting for it to finish,
and reassembling results that can arrive in any order
(`sorted()` restores the input order,
since each result is tagged with its `order`).
`ProcessPoolExecutor` is built on `multiprocessing`.
It reuses a pool of workers instead of spawning one process per call,
returns ordered results without manual bookkeeping,
and shares its `submit()`/`map()`/`Future` interface with
`ThreadPoolExecutor`,
so switching between processes and threads,
as the next section does,
is a one-line change.
Drop to `multiprocessing` directly for a job that is not one call
returning one value: a worker that runs continuously and
communicates over its own `Queue`,
or state shared between processes through a
`multiprocessing.Manager`, `Value`, or `Array`.
`ProcessPoolExecutor` does not expose any of those.

The claim that wall-clock time falls toward a single task's time,
not their sum, is worth checking rather than trusting.
Split a fixed amount of work into a growing number of tasks,
keep the pool warm across every measurement,
and watch what happens once task count passes the number of cores:

```python
# task_scaling.py
"""Split a fixed workload across a growing number of tasks and
time each split on a warm pool.

    python task_scaling.py
    python task_scaling.py --total 200_000_000 --max-tasks 128
"""
import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor

def work_chunk(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total

def timed_split(
    pool: ProcessPoolExecutor, total_work: int, tasks: int
) -> float:
    chunk = total_work // tasks
    start = time.perf_counter()
    list(pool.map(work_chunk, [chunk] * tasks))
    return time.perf_counter() - start

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--total", type=int, default=10_000_000,
        help="total loop iterations, split across tasks",
    )
    parser.add_argument(
        "--max-tasks", type=int, default=None,
        help="largest task count to try (default: 2 * cores)",
    )
    args = parser.parse_args()

    cores = os.cpu_count() or 1
    max_tasks = args.max_tasks or cores * 2
    task_counts = sorted({1, 2, cores, max_tasks})
    print(f"cores = {cores}, total = {args.total}")

    with ProcessPoolExecutor() as pool:
        list(pool.map(work_chunk, [1]))  # Warm up, not timed
        baseline = None
        for tasks in task_counts:
            elapsed = timed_split(pool, args.total, tasks)
            baseline = baseline or elapsed
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({baseline / elapsed:4.2f}x)"
            )

if __name__ == "__main__":
    main()
```

`work_chunk()` is deliberately dumb, pure looping,
so the only variable across a run is how finely the total work gets split.
The pool is created once and warmed with a throwaway call
before any measurement starts,
so process startup never leaks into a timed result,
the same discipline `timeit` needs around any one-time setup cost.
Each later call reuses that same pool,
so only the split changes from one line of output to the next.
Wall time drops sharply between one task and a task for every core,
then keeps dropping a little past that point as smaller,
more numerous chunks balance the load better across workers,
before flattening out.
The defaults above finish in about a second,
small enough for a full `make verify` run.
Raise `--total` and `--max-tasks` to push the curve onto a slower,
more dramatic slope on your own machine.

## The GIL and Free Threading

Threads would not have helped in the previous section.
The standard CPython build has a *Global Interpreter Lock* (GIL).
Only one thread runs Python bytecode at a time, no matter how many
cores sit idle. A thread releases the GIL while it waits on I/O,
which is why `asyncio` and a thread pool both help I/O-bound work.
Neither helps CPU-bound work,
because a thread that is computing never releases the GIL
for another thread to run:

```python
# gil_threads.py
import timeit
from concurrent.futures import ThreadPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [cpu_price(o) for o in orders]

def threaded(orders: list[int]) -> list[int]:
    with ThreadPoolExecutor() as pool:
        return list(pool.map(cpu_price, orders))

orders = [1, 2, 3, 4, 5]
assert threaded(orders) == sequential(orders)

t_seq = timeit.timeit(lambda: sequential(orders), number=5)
t_thr = timeit.timeit(lambda: threaded(orders), number=5)
print(f"threads no faster: {t_thr > t_seq * 0.9}")
#: threads no faster: True
```

Swapping the loop for a thread pool changes nothing.
Five threads still take turns holding the one GIL,
so `threaded()` costs the same as `sequential()`,
sometimes a little more, from the added scheduling.
This is exactly why [Parallelism](#parallelism) used processes instead.
Each process gets its own interpreter, and so its own GIL.

The GIL deserves more than a definition,
because it is misunderstood in both directions.
It is not a design mistake, and it does not make threaded code safe.
The rest of this section condenses my PyCon 2026 presentation
[Demystifying the GIL](https://github.com/BruceEckel/DemystifyingTheGIL).
That repository includes a short book that covers each topic in depth.

### Why Python Has a GIL

The GIL is the consequence of three earlier decisions.
Each was reasonable on its own.
In 1990, Python adopted *reference counting* for memory management.
Every object carries a count of the references to it.
When the count reaches zero, the object is freed immediately.
This gave Python deterministic cleanup with no collector pauses.
It also planted a cost.
Every count update is a read-modify-write sequence,
and updates happen millions of times per second.
In 1991, the C API exposed those counts directly to
extension authors.
Easy extensions made Python a coordination language for C libraries
and eventually produced the scientific Python stack.
In exchange, reference counting became part of the compiled
binary interface.
Changing how it works breaks every extension.
In 1992, threads arrived, for I/O concurrency rather than for
multi-core speed.
Now two threads could update the same count at once and lose
one of the updates,
freeing an object still in use or leaking it forever.

One interpreter-wide lock was the cheapest fix that fit the
three earlier decisions.
It made every count update, every dict and list mutation,
and every existing extension safe at once.
Single-threaded code paid almost nothing.
Every alternative undid one of the earlier decisions.
Atomic count updates slow every program to benefit a few.
A 1996 patch tried fine-grained locks and ran single-threaded
code about twice as slow.
A tracing garbage collector would have broken every extension.
In rejecting that 1996 patch, Guido van Rossum set the bar that
stood for three decades:
remove the GIL without slowing single-threaded code.
Attempts kept failing to clear it, so workarounds shipped instead.
`multiprocessing` arrived in 2008, `asyncio` in 2014,
and the per-interpreter GIL of the next section in 2023.

### The GIL Does Not Prevent Races

The lock protects the interpreter, not your program.
Reference counts stay consistent, dictionaries never corrupt
their internal structure, and imports do not collide.
Your shared state gets no such protection.
The statement `counter += 1` compiles to separate bytecode
instructions:

```
LOAD_GLOBAL     counter  # Read the current value
LOAD_SMALL_INT  1        # Push the constant 1
BINARY_OP       13 (+=)  # Compute counter + 1
STORE_GLOBAL    counter  # Write the result back
```

The GIL can move to another thread between instructions.
When two threads both read before either writes,
they compute the same result, and one increment vanishes.
Since 3.11 the interpreter only switches threads at a function
call or at the jump that closes a loop iteration,
so this particular sequence is no longer interrupted in practice.
That is scheduling luck, not safety.
Any function call between the read and the write reopens the gap.
Here the call is a one-microsecond `time.sleep()`,
a blocking call, and blocking calls release the GIL:

```python
# gil_race.py
import threading
import time

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        time.sleep(0.000_001)  # Let other threads run
        counter = value + 1  # Write back

threads = [
    threading.Thread(target=increment, args=(50,))
    for _ in range(8)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: True
```

Eight threads each add 50, so `counter` should reach 400.
A typical run lands near 50.
Each sleep releases the GIL between a read and its write,
so all eight threads read the same value,
and their eight writes store the same result.
The GIL made this race rare at machine speed.
It never made it impossible.
Threads that share mutable state need a lock, or a queue like the
one in [Coordinating Threads with Queues](#coordinating-threads-with-queues),
on every build of Python.

### Free Threading

Since 3.13, CPython also ships as a *free-threaded* build,
tracked by [PEP 703](https://peps.python.org/pep-0703/)
and installed separately (`python3.15t` rather than `python3.15`).
It removes the GIL, so threads run Python bytecode
on separate cores at the same time.
Running the identical `sequential()`/`threaded()` pair above
under a free-threaded interpreter turns the ratio around:

    threads speedup: 3.8x

(The speedup needs a free-threaded interpreter,
which is not the book's default build,
so the build does not run that second measurement.
The number is one machine's actual output.)

Free threading finally cleared the 1996 bar by making reference
counting cheap without a global lock.
Most objects are only ever touched by the thread that created them.
*Biased reference counting* lets that owning thread update the
count with plain arithmetic.
Only other threads pay for an atomic operation.
Permanent objects like `None`, `True`, and small integers
become *immortal*, a change that landed in 3.12 for every build
but pays off most here, since it removes the one atomic operation
every thread would otherwise contest.
Their counts never change at all.
Mutable containers like dictionaries and lists carry individual
locks, so two threads contend only when they touch the same
container.
Single-threaded code still pays a small penalty for this machinery,
roughly five to fifteen percent depending on the workload,
and each release narrows it.

Removing the lock also removed three decades of accidental
protection for C extensions,
which were written assuming that only one thread runs at a time.
The free-threaded build ships with a safety net.
Loading an extension that has not declared itself thread-safe
re-enables the GIL for the whole process and emits a warning.
Free threading pays off only when every extension you load has
been audited, so check compatibility before switching a project.

It also rewards a particular shape of program.
Threads that mostly work on data they do not share,
like `threaded()` above, scale across cores.
So do threads that accumulate results locally and merge them
once at the end, caches that are read far more often than written,
and pipeline stages connected by queues.
Fine-grained sharing loses.
A counter with a lock around every increment serializes the
threads all over again,
and adds lock overhead the GIL never charged.
On a free-threaded interpreter, threads alone are enough for
CPU-bound work, and they share memory directly,
without a process pool's pickling between processes.
A free-threaded interpreter is one way off the standard build's
limits.
The next section covers another,
and it runs on the standard build you already have.

## Subinterpreters

Each worker in a process pool gets its own interpreter,
and so its own GIL.
That is the source of the parallelism.
The cost is a whole operating-system process per task.
Since 3.12, CPython can create additional interpreters
inside the same process ([PEP 684](https://peps.python.org/pep-0684/)),
each with its own GIL.
`InterpreterPoolExecutor` runs each call in one of these,
so multiple interpreters, each locked on its own, run truly at once,
without leaving the process:

```python
# subinterpreters.py
import timeit
from concurrent.futures import InterpreterPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [cpu_price(o) for o in orders]

orders = [1, 2, 3, 4, 5]
t_seq = timeit.timeit(lambda: sequential(orders), number=5)

with InterpreterPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)  # Also starts the workers
    t_sub = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

print(f"subinterpreters at least 2x faster: {t_seq > t_sub * 2}")
#: subinterpreters at least 2x faster: True
```

Unlike a thread pool, this genuinely overlaps computation.
Each worker interpreter holds its own GIL,
so five of them run on five cores at once instead of taking turns.
Unlike a process pool, there is only one process,
so starting a worker is cheaper than starting a new interpreter
process, though each interpreter still runs in its own memory space,
and arguments and results still cross that boundary by copying.
A subinterpreter needs no separate build and no separate install,
which makes it the first thing to try for CPU-bound work,
before a process pool or a free-threaded interpreter.

## Coordinating Threads with Queues

When threads divide up work, the danger is shared mutable state.
The `queue` module packages the standard answer:
a thread-safe queue that hands each item to exactly one consumer,
with the locking built in.
`queue.Queue` is first-in, first-out,
while `queue.PriorityQueue`, the threaded form of
[Performance](19_Performance.md)'s `heapq`,
always hands out the smallest item present:

```python
# priority_queue.py
import threading
from queue import PriorityQueue

type Job = tuple[int, str]  # (priority, description)

tasks: PriorityQueue[Job] = PriorityQueue()

def submit(jobs: list[Job]) -> None:
    for job in jobs:
        tasks.put(job)

threads = [
    threading.Thread(
        target=submit,
        args=([(3, "backup"), (1, "page oncall")],),
    ),
    threading.Thread(
        target=submit,
        args=([(2, "rotate logs"), (1, "alert")],),
    ),
]
for t in threads:
    t.start()
for t in threads:
    t.join()

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (2, 'rotate logs')
#: (3, 'backup')
```

The four jobs arrive from two threads in an unpredictable interleaving,
but the drain comes out in priority order no matter who won each race,
with equal priorities ordered by the tuple's second field.
This producer-consumer shape, producers calling `put()` and consumers
calling `get()`, is how thread pools distribute work,
and `get()` blocks until an item is available,
so an idle consumer simply waits.
The [Object Pool](16_Context_Managers.md#an-object-pool) in
Context Managers uses the same `Queue` as a throttle.

## Exercises

1.  In `async_mechanics.py`, add a fourth call, `fetch("d")`, to the `gather()` line,
    and confirm the printed list grows to four entries in the order given, not the order they finish.
2.  In `event_loop_boundary.py`, add a third task function, `mixed_price()`, that awaits
    `asyncio.sleep(0.05)` and then also runs the 1,000,000-iteration loop from `cpu_price()`.
    Run it through `run()` and predict its `meter.peak` before checking:
    is it closer to the I/O peak or the CPU peak?
3.  In `async_race.py`, add an `asyncio.Lock()` around the read-modify-write in `increment()`
    (acquire before reading `counter`, release after writing it back)
    and confirm `counter` now reaches `400`.
4.  In `gil_race.py`, remove the `time.sleep(0.000_001)` call entirely and run the script several times.
    Explain, using [The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races),
    why the race becomes far less likely to show up without that sleep, but is not thereby fixed.
5.  In `priority_queue.py`, add a third thread submitting `[(1, "zzz"), (3, "aaa")]`
    and confirm the drain order still respects priority first, then the description as a tiebreaker.
