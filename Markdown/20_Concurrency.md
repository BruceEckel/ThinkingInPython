# Concurrency

[Performance](19_Performance.md) works on making one stream of instructions faster.
This chapter reaches for the other lever.
*Concurrency* runs independent tasks so they overlap instead of waiting in line.
Whether overlap helps at all depends on where each task spends its time.

## I/O-Bound vs CPU-Bound

A task is *I/O-bound* when it spends its time waiting on something outside the process:
a network reply, a disk read, a database query.
The processor sits idle through the wait.
A task is *CPU-bound* when it spends its time computing inside the process.
The processor is busy from start to finish.

That boundary decides the tool.
Waiting can overlap on a single thread. While one task waits, the thread runs another.
Computing cannot. One core runs one stream of instructions at a time.
So I/O-bound work needs `asyncio`, and CPU-bound work needs separate processes.

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
Threads would not have helped. CPython runs only one thread of Python at a time,
which the next section explains.

## The GIL and Free Threading

[[The GIL serializes CPU-bound threads, which is why the parallelism above reaches for processes. The free-threaded (no-GIL) builds available since 3.13 lift this and change when threads alone are enough]]

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
