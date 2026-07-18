# Concurrency

[Performance](18_Performance.md)
works on making one stream of instructions faster.
*Concurrency* runs independent tasks so they overlap instead of waiting in line.
Whether this overlap helps depends on where each task spends its time.

## I/O-Bound vs CPU-Bound

A task is *I/O-bound* when it spends its time waiting on something outside the process:
a network reply, a disk read, a database query.
The processor sits idle through the wait.
A task is *CPU-bound* when it spends its time computing inside the process.
The processor is busy from start to finish.

That boundary decides the tool to use.
Waiting can overlap on a single thread.
While one task waits, the thread runs another.
Computing cannot.
One core runs one stream of instructions at a time.
I/O-bound work overlaps within a single process,
with `asyncio` or a thread pool.
CPU-bound work needs multiple cores.
A separate process is the traditional way to get more than one core.
Later in this chapter, we show two other approaches,
each running inside a single process.

## `async def`, `await`, and the Event Loop {#asyncio-mechanics}

Four pieces make up the `asyncio` vocabulary.

1. `async def` defines a *coroutine function*.
   Calling it runs nothing.
   It returns a *coroutine object*, a description of work that has not started.
2. `await` starts that work and pauses the awaiting coroutine until the result is ready.
   The pause is the point.
   While one coroutine waits,
   the *event loop* finds other coroutines that are ready to run.
3. `asyncio.gather()` awaits several coroutines at once and collects their results in order.
4. `asyncio.run()` starts the event loop, runs one coroutine to completion,
   and shuts the loop down.
   It is the entry point, called once to run the program:

```python
# async_mechanics.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)  # A stand-in for a network wait
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    x = fetch("a", 0.03)  # Nothing runs yet
    print(type(x).__name__)
    results = await asyncio.gather(  # Run all three concurrently
        x, fetch("b", 0.02), fetch("c", 0.01))
    print(results)

asyncio.run(main())
#: coroutine
#: a: started
#: b: started
#: c: started
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C']
```

The first printed line is proof that calling a coroutine runs nothing.
`fetch("a", 0.03)` is called on `main()`'s first line,
yet no started line appears, only the name of the object that the call built:
`coroutine`.
The work begins when `gather()` receives that object.
If you forget the `await gather()`, the work doesn't happen.
Python points this out with a `RuntimeWarning: coroutine 'fetch' was never awaited` when the forgotten object is garbage-collected.

The trace shows the event loop's schedule.
`gather()` wraps each coroutine in a *task*,
the event loop's unit of scheduling, and starts the tasks in the order given.
Each runs until it reaches its `await`, so the started lines print as a, b, c.
At the `await` each task *suspends*.
It stops executing, remembers its place in the function,
and hands control back to the event loop.

A suspended task runs no bytecode and holds no processor; it is a paused frame,
local variables intact, waiting to continue.
The event loop starts the next coroutine,
which is how all three are in flight during the first wait.
Suspending also registers a wake-up condition with the event loop.

`asyncio.sleep()` asks for a timer;
a real network request would ask the loop to watch a socket for the reply.
When a timer fires, the loop resumes that task exactly where it paused,
just after the `await`.
The three delays make the resumptions visible: c sleeps shortest,
so its timer fires first, and the resumed lines print as c, b, a,
the reverse of the starting order.
`gather()` returns `['A', 'B', 'C']`,
showing that the results follow the argument order, not the finishing order.
The total wait is one 0.03-second sleep, not the sum of all three.

An `await` is only legal inside an `async def`,
which is why the demonstration needs `main()`.

Beware a list comprehension that awaits:
`[await c for c in coroutines]` returns the same list as `gather()` but is the sequential version.
Each `await` runs its coroutine to completion before the next one starts,
so nothing overlaps and the waits add up.
`gather()` is concurrent because it wraps and *schedules* every coroutine as a task before it waits for any of them.
Scheduling is not yet running.
The task bodies execute only after `gather()` itself suspends,
each in turn up to its first `await`, which is exactly what the a, b,
c started lines in the trace show.
The comprehension never reaches that state:
it does not even wrap the next coroutine until the previous one has finished entirely.

## Structured Concurrency with `TaskGroup`

What happens if `gather()` encounters a failure?
If one of its coroutines raises an exception,
`gather()` re-raises that exception into the awaiting code,
but the other tasks it started keep running.
Now these tasks are unsupervised and their results and errors are discarded.
`asyncio.TaskGroup` (added in 3.11) is the structured alternative:
an `async with` block that owns every task started inside it and refuses to be exited until all of them are accounted for:

```python
# task_group.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    await asyncio.sleep(delay)
    if item == "b":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    pairs = [("a", 0.25), ("b", 0.05), ("c", 0.01)]
    try:
        async with asyncio.TaskGroup() as tg:
            for item, delay in pairs:
                tg.create_task(fetch(item, delay))
    except* ValueError as group:
        print(f"caught: {group.exceptions[0]}")

asyncio.run(main())
#: c: fetched
#: caught: fetch('b') failed
```

`tg.create_task()` schedules a task immediately,
so all three are in flight together, exactly as under `gather()`.
The trace shows the failure discipline. c, with the shortest delay,
completes and prints. b raises at 0.05 seconds,
and the group responds by cancelling a,
which is still suspended with 0.2 seconds of sleep to go,
so a's fetched line never appears.
(The wide gap between b's failure and a's deadline is deliberate: it gives the cancellation room to land on any platform's timer, so the trace stays deterministic.)
Only when every task has finished or been cancelled does the block exit,
re-raising the failure wrapped in an *exception group*,
a container for simultaneous failures,
since more than one task can go down at once.
The `except*` form catches members of a group by type.

`TaskGroup` can also produce `gather()`'s ordered result list.
Keep the task objects and harvest them after the block,
which is safe because the block cannot exit until every task has finished:

```python
# task_group_results.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return item.upper()

async def main() -> None:
    pairs = [("a", 0.03), ("b", 0.02), ("c", 0.01)]
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(i, d)) for i, d in pairs]
    print([t.result() for t in tasks])

asyncio.run(main())
#: ['A', 'B', 'C']
```

The comprehension keeps the tasks in argument order,
so the harvested results come out exactly as `gather()`'s would,
no matter which task finished first.
Given that, why does `gather()` survive?
Weight, and one genuinely different mode.
For a batch expected to succeed, `await gather(...)` is a single expression:
no `async with`, no task list, no harvest step.
And `gather(..., return_exceptions=True)` collects failures *as values* in the result list,
for batches where partial failure is data to examine rather than a reason to stop.
A health check across ten services wants the nine answers and the one error.
`TaskGroup` has no such mode.
Its contract is all-or-cancel,
and keeping siblings alive past a failure means catching inside each task yourself.
For new code where a failure should stop the batch,
`TaskGroup` is the sound default.
`gather()` remains the compact happy-path form,
and the only form for failure-as-data.

## Overlapping the Waits

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits, the loop runs another task in the meantime.
In the following example, the same price lookup appears twice.
`io_price` waits using `asyncio.sleep` as a stand-in for a network call.
`cpu_price` performs computations to represent heavy work.
A `Meter` records the peak number of tasks in flight at once:

```python
# event_loop_boundary.py
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self) -> None:
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type: object, exc: object,
                 tb: object) -> None:
        self.active -= 1

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def io_price(order: int, meter: Meter) -> int:
    with meter:  # In flight for the span of the block
        await asyncio.sleep(0.05)  # Waiting outside the processor
    return order * 10

async def cpu_price(order: int, meter: Meter) -> int:
    with meter:
        total = 0
        for _ in range(1_000_000):  # Working inside the processor
            total += 1
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

Both runs use the same `asyncio.gather()`, yet the peaks differ.
The I/O tasks each reach their `await` and suspend,
so all five are in flight at once: peak 5.
The CPU tasks never `await`, so each runs to the end before the next starts:
peak 1.
The event loop overlaps waiting, not computing.
Async did not fail.
It overlapped the part that runs outside the processor,
which for `cpu_price` is nothing.

The `asyncio.sleep()` in `io_price` is not `time.sleep()`.
Awaiting `asyncio.sleep()` suspends only the current task and hands the wait to the event loop,
which is what let all five `io_price` tasks overlap.
`time.sleep()` is a blocking call: it stops the whole thread,
and the event loop runs on that thread,
so a coroutine that calls it freezes every task in the program, not just itself:

```python
# blocking_the_loop.py
import asyncio
import time
from collections.abc import Awaitable, Iterable

async def yielding_wait() -> None:
    await asyncio.sleep(0.05)  # Suspends this task only

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the whole event loop

async def elapsed(tasks: Iterable[Awaitable[None]]) -> float:
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    return time.perf_counter() - start

async def main() -> None:
    t_yield = await elapsed(yielding_wait() for _ in range(5))
    t_block = await elapsed(blocking_wait() for _ in range(5))
    print(f"awaited sleeps overlap: {t_yield < 0.05 * 2}")
    print(f"blocking sleeps serialize: {t_block >= 0.05 * 5}")

asyncio.run(main())
#: awaited sleeps overlap: True
#: blocking sleeps serialize: True
```

Five awaited sleeps finish together in about the time of one.
Five blocking sleeps cannot overlap at all:
each stalls the loop for its full duration,
so the total is never less than their sum.
To the event loop, a blocking call is `cpu_price` all over again,
work that never yields.
The rule inside `async def` is to await, never block.
A blocking call you cannot rewrite,
a library function that reads a file or talks to a database,
belongs in a thread,
and `await asyncio.to_thread(blocking_call)` moves it there while the loop keeps running.

[Simulation](38_Simulation.md) builds a full program on these mechanics:
a pack of rats exploring a maze as cooperating tasks,
and [Observer](30_Observer.md#observer-and-io)
uses `gather()` to notify slow observers together instead of one at a time.

## A Single Thread Still Races

`asyncio` runs one coroutine at a time, never two at once.
It is tempting to conclude that shared state needs no locking there.
But "one at a time" only protects the instructions between two `await`s,
not a value that lives across one.
Two coroutines that read a shared value, `await`,
then write it back can lose an update with no thread and no GIL in sight:

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
Every `await asyncio.sleep(0)` hands control to the event loop before the write happens.
The sleep is not the cause, only the smallest possible stand-in:
in real code that middle `await` is a database query or an HTTP call,
and the same update is lost while it waits.
In each round all eight coroutines read the same value before any of them writes,
so eight additions collapse into one.
[The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races)
shows the identical failure with threads.
The mechanism differs.
A thread switch is preemptive,
landing at points the interpreter picks and you did not choose,
while a coroutine switch happens only at an `await` you chose to write.
That makes the gap easier to find, not safer to leave unguarded.
A read-modify-write that spans an `await` needs `asyncio.Lock`,
the same shape of fix a lock gives across threads.

## Parallelism

The CPU-bound task cannot overlap on one core.
Give it several cores and it can.
`ProcessPoolExecutor` runs each call in its own process,
each with its own interpreter,
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

`pool.map()` sends each order to a worker process and gathers the results in order,
printing `[10, 20, 30, 40, 50]`, the same answer as the other versions.
The computation is the same `cpu_price` as before.
Only its home changed, from one shared interpreter to several.
With enough cores the wall-clock time falls toward the time of a single task,
not their sum.

Two mechanics separate a process pool from every in-process tool in this chapter,
and both surface in this short listing.
First, the `if __name__ == "__main__"` guard is not decoration.
To create a worker, the operating system starts a fresh Python interpreter,
and that interpreter *imports* this module to find `cpu_price()`.
During the import the module's name is not `"__main__"`,
so the guard keeps each worker from running `main()` and building a pool of workers of its own;
leave it out and Python detects the runaway spawning and raises `RuntimeError`.
Second, work crosses the process boundary by *pickling*.
Each argument and each return value is serialized in one process and rebuilt in the other,
and the function itself travels by name,
so it must be importable from the top level of the module:
passing a `lambda` to `pool.map()` fails with a pickling error.
This is also [Performance](18_Performance.md#converting-a-slow-function-to-rust)'s coarse-interface rule in another costume:
a million tiny results can cost more to pickle than the parallelism saved.

`ProcessPoolExecutor` is not the only way to get separate processes.
The `multiprocessing` module underneath it exposes the raw pieces:
a `Process` you start and `join()`, and a `Queue` to carry results back,
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
    pairs: list[tuple[int, int]] = sorted(
        results.get() for _ in workers)
    print([price for _, price in pairs])

if __name__ == "__main__":
    main()
```

This prints the same `[10, 20, 30, 40, 50]`,
but everything `pool.map` did is now explicit: starting each worker,
waiting for it to finish, and reassembling results that can arrive in any order
(`sorted()` restores the input order, since each result is tagged with its `order`).
Draining after `join()` is safe here because five small tuples fit in the queue's internal buffer.
A queue carrying bulky data must be drained *before* joining:
each worker's feeder thread blocks until its data is consumed,
so the `join()` would deadlock.
`ProcessPoolExecutor` is built on `multiprocessing`.
It reuses a pool of workers instead of spawning one process per call,
returns ordered results without manual bookkeeping,
and shares its `submit()`/`map()`/`Future` interface with `ThreadPoolExecutor`,
so switching between processes and threads, as the next section does,
is a one-line change.
Drop to `multiprocessing` directly for a job that is not one call returning one value:
a worker that runs continuously and communicates over its own `Queue`,
or state shared between processes through a `multiprocessing.Manager`, `Value`,
or `Array`.
`ProcessPoolExecutor` does not expose any of those.

The claim that wall-clock time falls toward a single task's time, not their sum,
is worth checking rather than trusting.
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
        baseline: float | None = None
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
The pool is created once and warmed with a throwaway call before any measurement starts,
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
Only one thread runs Python bytecode at a time,
no matter how many cores sit idle.
A thread releases the GIL while it waits on I/O. That single fact decides what a thread pool is good for,
and both halves of the claim are worth demonstrating.
The waiting half first.
Here `time.sleep()` stands in for a blocking network call,
and five threads overlap five of those waits even with the GIL in place:

```python
# io_threads.py
import time
import timeit
from concurrent.futures import ThreadPoolExecutor

def io_price(order: int) -> int:
    time.sleep(0.05)  # Waiting outside the processor
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [io_price(o) for o in orders]

def threaded(orders: list[int]) -> list[int]:
    with ThreadPoolExecutor() as pool:
        return list(pool.map(io_price, orders))

orders = [1, 2, 3, 4, 5]
assert threaded(orders) == sequential(orders)
t_seq = timeit.timeit(lambda: sequential(orders), number=1)
t_thr = timeit.timeit(lambda: threaded(orders), number=1)
print(f"threads at least 3x faster on I/O: {t_thr * 3 < t_seq}")
#: threads at least 3x faster on I/O: True
```

Five 50-millisecond waits finish in about the time of one.
Each sleeping thread has released the GIL,
so the operating system runs another thread while it waits,
the same overlap `asyncio` achieved with suspended tasks.
This is `blocking_the_loop.py` turned inside out:
a blocking call freezes an event loop,
but a pool of threads absorbs blocking calls comfortably,
which is why `asyncio.to_thread()` hands its blocking work to exactly this kind of pool.
Use a thread pool for I/O when the blocking calls already exist and rewriting them as coroutines is not worth the surgery;
`asyncio` earns its keep when the waits number in the thousands,
since tasks are far lighter than threads.

Computing is the other half, and it turns the result around.
A thread that is computing never releases the GIL for another thread to run:

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
so `threaded()` costs the same as `sequential()`, sometimes a little more,
from the added scheduling.
This is why [Parallelism](#parallelism) used processes instead.
Each process gets its own interpreter, and so its own GIL.

The GIL needs more than a definition,
because it is misunderstood in both directions.
It is not a design mistake, and it does not make threaded code safe.
The rest of this section condenses my PyCon 2026 presentation [Demystifying the GIL](https://github.com/BruceEckel/DemystifyingTheGIL).
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
In 1991, the C API exposed those counts directly to extension authors.
Easy extensions made Python a coordination language for C libraries and eventually produced the scientific Python stack.
In exchange, reference counting became part of the compiled binary interface.
Changing how it works breaks every extension.
In 1992, threads arrived, for I/O concurrency rather than for multi-core speed.
Now two threads could update the same count at once and lose one of the updates,
freeing an object still in use or leaking it forever.

One interpreter-wide lock was the cheapest fix that fit the three earlier decisions.
It made every count update, every dict and list mutation,
and every existing extension safe at once.
Single-threaded code paid almost nothing.
Every alternative undid one of the earlier decisions.
Atomic count updates slow every program to benefit a few.
A 1996 patch tried fine-grained locks and ran single-threaded code about twice as slow.
A tracing garbage collector would have broken every extension.
In rejecting that 1996 patch,
Guido van Rossum set the bar that stood for three decades:
remove the GIL without slowing single-threaded code.
Attempts kept failing to clear it, so workarounds shipped instead.
`multiprocessing` arrived in 2008, `asyncio` in 2014,
and the per-interpreter GIL of the next section in 2023.

### The GIL Does Not Prevent Races

The lock protects the interpreter, not your program.
Reference counts stay consistent,
dictionaries never corrupt their internal structure, and imports do not collide.
Your shared state gets no such protection.
The statement `counter += 1` compiles to separate bytecode instructions:

```
LOAD_GLOBAL     counter  # Read the current value
LOAD_SMALL_INT  1        # Push the constant 1
BINARY_OP       13 (+=)  # Compute counter + 1
STORE_GLOBAL    counter  # Write the result back
```

The GIL can move to another thread between instructions.
When two threads both read before either writes, they compute the same result,
and one increment vanishes.
Since 3.11 the interpreter only switches threads at a function call or at the jump that closes a loop iteration,
so this particular sequence is no longer interrupted in practice.
That is scheduling luck, not safety.
Any function call between the read and the write reopens the gap.
Here the call is a one-microsecond `time.sleep()`, a blocking call,
and blocking calls release the GIL:

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
Threads that share mutable state need a lock,
or a queue like the one in [Coordinating Threads with Queues](#coordinating-threads-with-queues),
on every build of Python.

### Free Threading

Since 3.13, CPython also ships as a *free-threaded* build,
tracked by [PEP 703](https://peps.python.org/pep-0703/) and installed separately
(`python3.15t` rather than `python3.15`).
It removes the GIL, so threads run Python bytecode on separate cores at the same time.
Running `gil_threads.py`'s CPU-bound `sequential()`/`threaded()` pair under a free-threaded interpreter turns the ratio around:

    threads speedup: 3.8x

(The speedup needs a free-threaded interpreter, which is not the book's default build, so the build does not run that second measurement.
The number is one machine's actual output.)

<!-- TODO(free-threaded-default): if free threading ever becomes
CPython's default build, convert this indented block to a real, fenced,
tested example. -->

Free threading finally cleared the 1996 bar by making reference counting cheap without a global lock.
Most objects are only ever touched by the thread that created them.
*Biased reference counting* lets that owning thread update the count with arithmetic.
Only other threads pay for an atomic operation.
Permanent objects like `None`, `True`, and small integers become *immortal*,
a change that landed in 3.12 for every build but pays off most here,
since it removes the one atomic operation every thread would otherwise contest.
Their counts never change.
Mutable containers like dictionaries and lists carry individual locks,
so two threads contend only when they touch the same container.
Single-threaded code still pays a small penalty for this machinery,
roughly five to fifteen percent depending on the workload,
and each release narrows it.

Removing the lock also removed three decades of accidental protection for C extensions,
which were written assuming that only one thread runs at a time.
The free-threaded build ships with a safety net.
Loading an extension that has not declared itself thread-safe re-enables the GIL for the whole process and emits a warning.
Free threading pays off only when every extension you load has been audited,
so check compatibility before switching a project.

It also rewards a particular shape of program.
Threads that mostly work on data they do not share, like `threaded()` above,
scale across cores.
The same is true of threads that accumulate results locally and merge them once at the end,
caches that are read far more often than written,
and pipeline stages connected by queues.
Fine-grained sharing loses.
A counter with a lock around every increment serializes the threads all over again,
and adds lock overhead the GIL never charged.
On a free-threaded interpreter, threads alone are enough for CPU-bound work,
and they share memory directly,
without a process pool's pickling between processes.
A free-threaded interpreter is one way off the standard build's limits.
The next section covers another,
and it runs on the standard build you already have.

## Subinterpreters

Each worker in a process pool gets its own interpreter, and so its own GIL.
That is the source of the parallelism.
The cost is a whole operating-system process per worker.
Since 3.12, CPython can create additional interpreters inside the same process
([PEP 684](https://peps.python.org/pep-0684/)), each with its own GIL.
`InterpreterPoolExecutor` (added in 3.14) runs each call in one of these,
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
so starting a worker is cheaper than starting a new interpreter process.
The interpreters share the process's memory,
but each keeps its own isolated objects,
so arguments and results still cross that boundary by copying.
A subinterpreter needs no separate build and no separate install,
which makes it the first thing to try for CPU-bound work,
before a process pool or a free-threaded interpreter.
The one compatibility check mirrors free threading's: pure Python always works,
but a C extension must support per-interpreter isolation to be imported in a subinterpreter.

![The same cpu_price workload under all four models: asyncio and threads never overlap the computing (one GIL, taking turns), while processes and subinterpreters genuinely run at once (five separate GILs)](_images/concurrency_models)

## Coordinating Threads with Queues

When threads divide up work, the danger is shared mutable state.
The `queue` module packages the standard answer:
a thread-safe queue that hands each item to a single consumer,
with the locking built in.
`queue.Queue` is first-in, first-out, while `queue.PriorityQueue`,
the threaded form of [Performance](18_Performance.md)'s `heapq`,
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
This producer-consumer shape,
producers calling `put()` and consumers calling `get()`,
is how thread pools distribute work,
and `get()` blocks until an item is available, so an idle consumer simply waits.
The [Object Pool](15_Context_Managers.md#an-object-pool)
in Context Managers uses the same `Queue` as a throttle.

One caution before copying the drain loop:
`while not tasks.empty()` is trustworthy here only because both producers have already been joined,
so nothing can add or remove an item after `empty()` answers.
While other threads are still running,
`empty()` reports a moment that may already be over.
A live consumer does not poll `empty()`;
it calls `get()` and lets the block do the waiting.

This chapter has now used two queues that share an interface but not a home,
and a third exists.
`queue.Queue` locks between threads in one interpreter.
`multiprocessing.Queue`, in `multiprocessing_raw.py`,
pickles items across process boundaries.
`asyncio.Queue` belongs on the event loop:
`await queue.get()` suspends the task instead of blocking the thread,
and it is not thread-safe at all,
because the single-threaded loop needs no locking.
Match the queue to the concurrency model.
The interfaces look alike,
but the first two block the calling thread while the third suspends a task,
and as `blocking_the_loop.py` showed,
a blocked thread and a suspended task are very different events on an event loop.

## Exercises

1.  In `async_mechanics.py`, add a fourth call, `fetch("d", 0.005)`,
    to the `gather()` line.
    Confirm that "d" starts last but resumes first,
    and that the printed list still grows to four entries in the order given,
    not the order they finish.
2.  In `async_mechanics.py`,
    replace the `gather()` call with `[await c for c in coroutines]`,
    where `coroutines` is a list of the same three `fetch()` calls.
    Predict the started/resumed trace and the total run time before running it,
    and explain why this version takes the sum of the three delays.
3.  In `event_loop_boundary.py`, add a third task function, `mixed_price()`,
    that awaits `asyncio.sleep(0.05)` and then also runs the 1,000,000-iteration loop from `cpu_price()`.
    Run it through `run()` and predict its `meter.peak` before checking:
    is it closer to the I/O peak or the CPU peak?
4.  In `event_loop_boundary.py`,
    change `io_price()`'s `await asyncio.sleep(0.05)` to `time.sleep(0.05)` and predict what happens to its `meter.peak` before running it.
    Explain the result using `blocking_the_loop.py`.
5.  In `async_race.py`, add an `asyncio.Lock()` around the read-modify-write in `increment()`
    (acquire before reading `counter`, release after writing it back)
    and confirm `counter` now reaches `400`.
6.  Remove the `if __name__ == "__main__"` guard from `parallel_cpu.py`,
    calling `main()` unconditionally, and run it.
    Read the error, then explain it with the import mechanics described in [Parallelism](#parallelism):
    what did each worker process do when it imported the module?
7.  In `gil_race.py`, remove the `time.sleep(0.000_001)` call and run the script several times.
    Explain, using [The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races),
    why the race becomes far less likely to show up without that sleep,
    but is not thereby fixed.
8.  In `priority_queue.py`,
    add a third thread submitting `[(1, "zzz"), (3, "aaa")]` and confirm the drain order still respects priority first,
    then the description as a tiebreaker.
