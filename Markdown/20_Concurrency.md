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

## The GIL and Free Threading

Threads would not have helped in the previous section.
The standard CPython build has a *Global Interpreter Lock* (GIL):
only one thread runs Python bytecode at a time, no matter how many
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

Swapping the loop for a thread pool changes nothing:
five threads still take turns holding the one GIL,
so `threaded()` costs the same as `sequential()`,
sometimes a little more, from the added scheduling.
This is exactly why [Parallelism](#parallelism) used processes instead:
each process gets its own interpreter, and so its own GIL.

Since 3.13, CPython also ships as a *free-threaded* build,
tracked by [PEP 703](https://peps.python.org/pep-0703/)
and installed separately (`python3.15t` rather than `python3.15`).
It removes the GIL, so threads run Python bytecode
on separate cores at the same time.
Running the identical `sequential()`/`threaded()` pair above
under a free-threaded interpreter turns the ratio around:

    threads speedup: 3.8x

On a free-threaded interpreter, threads alone are enough for CPU-bound
work, and they share memory directly,
without a process pool's pickling between processes.
The free-threaded build is newer,
and some C extensions still assume a GIL,
so check compatibility before switching a project to it.
A free-threaded interpreter is one way off the standard build's limits.
The next section covers another,
and it runs on the standard build you already have.
(The speedup above needs a free-threaded interpreter,
which is not the book's default build,
so the build does not run that second measurement.
The number is one machine's actual output.)

## Subinterpreters

Each worker in a process pool gets its own interpreter,
and so its own GIL.
That is where the parallelism comes from.
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

Unlike a thread pool, this genuinely overlaps computation:
each worker interpreter holds its own GIL,
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
`queue.Queue` is first-in, first-out;
`queue.PriorityQueue`, the threaded form of
[Performance](19_Performance.md)'s `heapq`,
always hands out the smallest item present:

```python
# priority_queue.py
import threading
from queue import PriorityQueue

tasks: PriorityQueue[tuple[int, str]] = PriorityQueue()

def submit(jobs: list[tuple[int, str]]) -> None:
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
