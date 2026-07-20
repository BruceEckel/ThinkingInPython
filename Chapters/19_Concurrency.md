# Concurrency

[Performance](18_Performance.md) makes one stream of instructions faster.
*Concurrency* runs independent tasks so they happen "at the same time" instead of waiting in line.

The meaning of "at the same time" depends on context.
Early machines had a single CPU, and early operating systems (OS)
were basically just program loaders.
The first step beyond that was *time-sharing*.
The CPU runs one program for a slice of time,
then the OS stops it and switches to a different program for another time slice.
Later came a lighter unit of scheduling that lives inside a program:
the *thread of execution*.
A modern OS schedules threads, not whole programs.
We say that each task (unit of work) is allocated its own thread,
and the OS performs *context switching* from one thread to the next.
The OS controls everything: allocating threads,
deciding how long a time slice is, performing the context switch,
and deciding which thread is ready to run next.

Each *process* (allocated when you start a program)
gets one thread and its own heap.
The program can request more threads from the OS,
but all threads within a process share the same heap.
This means each thread must not corrupt parts of the heap used by other threads.

When a program requests an additional thread from the OS,
that thread gets its own function-call stack,
separate from the original process stack.
Every function call pushes arguments and the return address onto the stack.
When the function ends,
its stack frame is popped and execution jumps back to the return address.
(The return value typically travels back in a CPU register.)
Thus it is essential that each thread own its call stack.

A context switch must preserve the state of the current thread before switching to a different thread.
It stores the CPU register set, which includes:

- The program counter (the next instruction to execute)
- The stack pointer
- Other registers and flags used by the program

The thread's stack is not copied.
It sits and waits for the thread to resume.
The heap is not copied because it is shared between all threads in that process.

Although a context switch is made to be as efficient as possible,
it has overhead.
Also, the OS must time slice fairly frequently to evenly distribute computing resources across threads.
Typically a thread only runs a few milliseconds at a time.

Using more than one thread within a program solved an immediate problem:
if a thread got stuck (*blocked*) waiting for I/O
(e.g. disk, network, waiting on a lock),
it could voluntarily yield its use of the CPU to the operating system,
which could then use that CPU for another thread,
producing faster overall progress.

Another benefit of threads was seen when more CPUs became available on a single machine.
Threads were already designed to distribute computing resources,
so more CPUs simply meant more resources to distribute
(of course, it wasn't quite that easy).
Threads could also be made to do ad-hoc parallelism:
some CPUs could be dedicated to running parallel parts of a program by adapting the threading mechanism.

Although threads have been adapted to these purposes,
the OS is always at a disadvantage:
it doesn't know details of the program it's running,
and therefore cannot optimize that program.
The OS cannot, for example,
perform faster context switches by knowing what data is important to preserve and what isn't.
In addition, each thread requires enough resources to work for every program,
even though some tasks might only require a fraction of those resources.
Engineers learned various tricks to make programs run faster despite these disadvantages,
but these tricks made the resulting programs more expensive to create and maintain.

The answer was to move the context switch out of the OS and into the program.
This way engineers are not fighting the threading system.
This is called *asynchrony*, implemented with *coroutines*.
The programming language decides, based on its knowledge of the program,
the minimum necessary data to include in the context switch.
The programmer minimizes context switches by deciding when they happen.
This shift in control of context switching greatly simplifies writing and reasoning about the program.

The second big shift was in language-level control of parallelism.
Mapping every parallel task onto its own OS thread worked,
but it pushed all scheduling decisions onto the OS and needed extra machinery
(thread pools, pinning, tuning) to perform well.
Languages and runtimes responded by taking on more of that scheduling,
multiplexing many lightweight,
language-managed tasks onto a smaller number of OS threads.
In special, latency-sensitive domains
(real-time control, high-frequency trading, packet processing)
specific CPUs are even isolated from ordinary OS activity altogether,
so a task can run with minimal interference.

## I/O-Bound vs CPU-Bound

A task is *I/O-bound* when it spends its time waiting on something outside the process:
a network reply, a disk read, a database query.
Given nothing else to do, the processor sits idle through the wait.
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

Instead of using threads for I/O bound problems,
asynchrony allows you to create coroutines.
Each coroutine, upon encountering I/O,
suspends itself and yields control ... but not to the OS.
Instead, control is given to the *event loop* which discovers the next task which is available to run.
This is captured in two keywords and the `asyncio` library.

Four pieces make up the `asyncio` vocabulary.

1. `async def` defines a *coroutine function*.
   Calling it doesn't run anything but instead returns a *coroutine object*.
   This is a description of work that has not started.
2. `await` starts that work and pauses the awaiting coroutine until the result is ready.
   While that coroutine waits,
   the *event loop* finds other coroutines that are ready to run.
3. `asyncio.gather()` awaits several coroutines at once and collects their results in order.
4. `asyncio.run()` starts the event loop, runs one coroutine to completion,
   and shuts the loop down.
   This is the entry point, called once to run the program:

```python
# async_mechanics.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)  # Stand-in for a network request
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
yet no "started" line appears, only the type of object the call built:
`coroutine`.
The work begins when `gather()` receives that object.
If you forget `await gather()`, the work doesn't happen.
Python points this out with a `RuntimeWarning: coroutine 'fetch' was never awaited` when the forgotten object is garbage-collected.

The trace shows the event loop's schedule.
`gather()` wraps each coroutine in a *task*,
the event loop's unit of scheduling, and starts the tasks in the order given.
Each runs until it reaches its `await`, so the started lines print as a, b, c.
At the `await` each task *suspends*.
It stops executing, remembers its place in the function,
and hands control back to the event loop.

A suspended task is a paused frame that runs no bytecode and uses no processor time.
Local variables remain intact, waiting to continue.
The event loop starts the next coroutine,
which is how all three are in flight during the first wait.

Suspending also registers a wake-up condition with the event loop.
`asyncio.sleep()` asks for a timer,
but a real network request would ask the loop to watch a socket for the reply.
When the timer fires, the loop resumes that task where it paused,
just after the `await`.
The three delays make the resumptions visible: c sleeps shortest,
so its timer fires first, and the resumed lines print as c, b, a,
the reverse of the starting order.
`gather()` returns `['A', 'B', 'C']`,
showing that the results follow the argument order, not the finishing order.
Note that the total wait is the longest delay (0.03-second),
not the sum of all three.

An `await` is only legal inside an `async def`,
which is why the demonstration needs `main()`.

Beware a list comprehension that awaits.
`[await c for c in coroutines]` becomes the sequential version of `gather()`.
Each `await` runs its coroutine to completion before the next one starts,
so nothing overlaps and the delays add instead of overlapping.
`gather()` is concurrent because it wraps and *schedules* every coroutine as a task before it waits for any of them.

Scheduling does not mean running.
The task bodies execute only after `gather()` suspends
(`gather()` is itself fueled by the event loop).
Each runs until its first `await`, which is what the `a: started`, etc.,
lines in the trace show.
The comprehension doesn't achieve multiple coroutines in flight:
it does not start the next coroutine until the previous one has finished.

## Structured Concurrency with `TaskGroup`

What happens if `gather()` encounters a failure?
If one of its coroutines raises an exception,
`gather()` re-raises that exception into the awaiting code,
but the other tasks it started keep running.
Those other tasks become unsupervised and their results and errors are discarded.

`asyncio.TaskGroup` (added in 3.11) is the structured alternative.
An `async with` block owns every task started inside it and does not exit until every one is accounted for.
The `TaskGroup` version and the `gather()` version that follows it run the same five fetches,
so `fetch()` and its `(item, delay)` pairs are worth sharing between them:

```python
# utils/fetch_demo.py
import asyncio

PAIRS = [
    ("a", 0.01),
    ("b", 0.02),
    ("c", 0.03),
    ("d", 0.2),
    ("e", 0.3),
]

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item == "c":
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()
```

`a` and `b` have the shortest delays,
`c` fails partway through,
and `d` and `e` are still sleeping when that happens,
with a wide gap to their own deadlines
(deliberate: it gives cancellation room to land on any platform's timer,
so the trace stays deterministic).
Wired into a `TaskGroup`:

```python
# task_group.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                item: tg.create_task(fetch(item, delay))
                for item, delay in PAIRS
            }
    except* ValueError as group:
        print(f"caught: {group.exceptions[0]}")
    for item, task in tasks.items():
        if task.cancelled():
            print(f"{item}: cancelled")
        elif (exc := task.exception()) is not None:
            print(f"{item}: raised {exc!r}")
        else:
            print(f"{item}: {task.result()}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: cancelled
#: e: cancelled
```

`tg.create_task()` schedules a task immediately,
so all five are in flight together, just as under `gather()`.
`c` raises an exception at 0.03 seconds,
and the `TaskGroup` responds by cancelling `d` and `e`,
which are still suspended with far more sleep to go,
so neither ever reaches its `fetched` print.
Only when every task has finished or been cancelled does the block exit.
As it exits, it re-raises the failure wrapped in an *exception group*.
This is a container for simultaneous failures,
since more than one task can go down at once.
The `except*` form catches members of a group by type.

Keeping the task objects pays off even after a partial failure.
`a` and `b` already succeeded, and their results are untouched:
`task.result()` returns `'A'` and `'B'`,
exactly as if nothing else had gone wrong.
`c` completed, but with an exception,
so `task.exception()` returns the `ValueError` instead of raising it.
`d` and `e` never reach their `fetched` print because the group cancels them,
so `task.cancelled()` is `True` for both.
A partial failure cancels whatever was still in flight.
It does not erase what already succeeded.

When a failure is data to examine rather than a reason to stop,
`gather(..., return_exceptions=True)` handles the same five fetches differently:

```python
# gather_with_exceptions.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    results = await asyncio.gather(
        *(fetch(item, delay) for item, delay in PAIRS),
        return_exceptions=True,
    )
    for (item, _), result in zip(PAIRS, results):
        if isinstance(result, BaseException):
            print(f"{item}: raised {result!r}")
        else:
            print(f"{item}: {result}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: a: fetched
#: b: fetched
#: d: fetched
#: e: fetched
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: D
#: e: E
```

`c` fails at the same 0.03-second mark as before,
but this time nothing stops.
`d` and `e` are not cancelled: `gather()` does not supervise its siblings the way `TaskGroup` does,
so both keep sleeping and print their `fetched` line right on schedule.
`return_exceptions=True` catches `c`'s `ValueError` and places it in the result list,
in argument order, alongside the three successful results.
Nothing propagates, so no `try`/`except*` is needed at the call site.

This is the trade `gather()` offers instead of `TaskGroup`'s all-or-cancel contract.
For a batch expected to succeed, `await gather(...)` is a single expression:
no `async with`, no task list, no harvest step.
For a batch where partial failure is data to examine rather than a reason to stop,
`return_exceptions=True` collects failures *as values*, as shown above,
instead of cancelling whatever is still in flight.
A health check across ten services wants the nine answers and the one error, not a cancelled nine-tenths of a batch.
`TaskGroup` has no such mode.
Its contract is all-or-cancel,
and keeping siblings alive past a failure means catching exceptions inside each task yourself.
For new code where a failure should stop the batch,
`TaskGroup` is the sound default.
`gather()` remains the compact happy-path form,
and the only form for failure-as-data.

## Overlapping the Waits

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits, the event loop finds another task to run in the meantime.

In the following example, the same price lookup appears twice.
`io_price()` awaits `asyncio.sleep()` as a stand-in for a network call.
`cpu_price()` performs computations to represent heavy work.
A `Meter` records the peak number of tasks in flight at once.
It is a [context manager](15_Context_Managers.md):
`__enter__()` counts the task in flight, `__exit__()` counts it done,
and `__exit__()` runs even if the body raises an exception:

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

async def io_price(order: int, meter: Meter) -> int:
    with meter:
        await asyncio.sleep(0.05)  # Off-processor work
    return order * 10

async def cpu_price(order: int, meter: Meter) -> int:
    with meter:
        total = 0
        for _ in range(1_000_000):  # On-processor work
            total += 1
    return order * 10

# The type of an async price function:
type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
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

`run()` creates the `Meter` object, then passes it to each task.
A task uses that object as a context manager,
writing `with meter:` around its own active span.

Both runs use the same `asyncio.gather()`, yet the peaks differ.
The I/O tasks each reach their `await` and suspend,
so all five are in flight at once: peak 5.
The CPU tasks never `await`, so each runs to the end before the next starts:
peak 1.
The event loop overlaps waiting, not computing.

Notice that `asyncio.sleep()` in `io_price` is different from `time.sleep()`.
Awaiting `asyncio.sleep()` suspends only the current task and hands control to the event loop,
which is what let all five `io_price` tasks overlap.
`time.sleep()` is a blocking call: it stops the whole thread,
so a coroutine that calls it freezes every task in the program, not just itself:

```python
# blocking_the_loop.py
import asyncio
import time
from collections.abc import Awaitable, Iterable

async def yielding_wait() -> None:
    await asyncio.sleep(0.05)  # Suspends this task only

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the event loop

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

## Escaping to a Thread

The rule inside `async def` is to `await`, never block.
If you cannot rewrite a blocking call,
for example a library function that reads a file or talks to a database,
you can put it in a thread.
`await asyncio.to_thread(blocking_call)` moves `blocking_call` into a thread,
allowing the event loop to keep running:

```python
# to_thread.py
import asyncio
import time
from collections.abc import Awaitable, Iterable

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the event loop

async def offloaded_wait() -> None:
    await asyncio.to_thread(time.sleep, 0.05)  # Runs in a thread

async def elapsed(tasks: Iterable[Awaitable[None]]) -> float:
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    return time.perf_counter() - start

async def main() -> None:
    t_block = await elapsed(blocking_wait() for _ in range(5))
    t_offload = await elapsed(offloaded_wait() for _ in range(5))
    print(f"blocking sleeps serialize: {t_block >= 0.05 * 5}")
    print(f"offloaded sleeps overlap: {t_offload < 0.05 * 2}")

asyncio.run(main())
#: blocking sleeps serialize: True
#: offloaded sleeps overlap: True
```

`blocking_wait()` is the same stalled call as before.
`offloaded_wait()` calls the identical `time.sleep()`,
but through `asyncio.to_thread()`,
which hands the call to a worker thread and awaits its completion.
`time.sleep()` itself still blocks, but it blocks a worker thread,
not the one running the event loop,
so the loop stays free to run the other four tasks while each sleep finishes.
Five offloaded sleeps overlap and finish together,
the same shape of result `asyncio.sleep()` gave the loop directly.

[Simulation](38_Simulation.md) builds a full program on these mechanics:
a pack of rats exploring a maze as cooperating tasks,
and [Observer](30_Observer.md#observer-and-io)
uses `gather()` to notify slow observers together instead of one at a time.

## A Single Thread Still Races

`asyncio` runs one coroutine at a time, never two at once.
This makes it tempting to conclude that shared state needs no locking.
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
        await asyncio.sleep(0)  # Release control to the event loop
        counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 50
```

Eight coroutines each add 50, so `counter` should reach 400.
Instead it stops at 50.
Every `await asyncio.sleep(0)` releases control to the event loop before the write happens.
(The `sleep(0)` is a stand-in for a database query or an HTTP call.)
In each round all eight coroutines read the same value before any of them writes,
so eight additions collapse into one.

[The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races)
shows the identical failure with threads.
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
each with its own interpreter and GIL,
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
The computation is the same `cpu_price()` as before.
Only its home changed, from one shared interpreter to several.
With enough cores the wall-clock time falls toward the time of a single task,
not their sum.

Two issues separate a process pool from every in-process tool in this chapter,
and both surface in this short listing:

1. The `if __name__ == "__main__"` guard is not decoration.
   To create a worker, the operating system starts a fresh Python interpreter,
   and that interpreter *imports* this module to find `cpu_price()`.
   During the import the module's name is not `"__main__"`,
   so the guard keeps each worker from running `main()` and building a pool of workers of its own.
   Leave it out and Python detects the runaway spawning and raises `RuntimeError`.
2. Work crosses the process boundary by *pickling*.
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
but everything `pool.map()` did is now explicit: starting each worker,
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

Use `multiprocessing` for a job that is not one call returning one value:

- A worker that runs continuously and communicates over its own `Queue`.
- State shared between processes through a `multiprocessing.Manager`, `Value`,
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

`work_chunk()` is deliberately simple, pure looping.
The only difference between one run and another is how finely the total work gets split.
The pool is created once and warmed up with a throwaway call before any measurement starts,
the same discipline `timeit` needs around any one-time setup cost.
This way, process startup never leaks into a timed result.

Each later call reuses that same pool,
so only the split changes from one line of output to the next.
Wall time drops sharply as the split grows from one task to one task per core,
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
A thread releases the GIL while it waits on I/O. That single fact decides what a thread pool is good for.
Both halves, the waiting and the computing, are worth demonstrating.
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
but a pool of threads absorbs blocking calls,
which is why `asyncio.to_thread()` hands its blocking work to this kind of pool.
Use a thread pool for I/O when the blocking calls already exist and rewriting them as coroutines is not worth the surgery;
`asyncio` pays off when you have thousands of waits,
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
At full speed, with no deliberate sleep, the GIL made this race rare.
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

(The speedup needs a free-threaded interpreter, which the book's build does not use, so that measurement does not run during verification.
The number is one machine's actual output.)

<!-- TODO(free-threaded-default): if free threading ever becomes
CPython's default build, convert this indented block to a real, fenced,
tested example. -->

Free threading finally cleared the 1996 bar by making reference counting cheap without a global lock.
Most objects are only ever touched by the thread that created them.
*Biased reference counting* lets that owning thread update the count with ordinary,
non-atomic arithmetic.
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
so multiple interpreters, each with its own lock, truly run at once,
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

print(f"subinterpreters at least 1.5x faster: {t_seq > t_sub * 1.5}")
#: subinterpreters at least 1.5x faster: True
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

## One Task, Many Backends

Every section so far has kept threads, processes, subinterpreters,
and `asyncio` apart on purpose.
Blending them without knowing which parts are compatible is how races and pickling errors happen.
Two real points of convergence exist in the standard library, though,
not because the models are secretly the same,
but because two small pieces of them genuinely are.

The first is `concurrent.futures.Executor`.
`ThreadPoolExecutor`, `ProcessPoolExecutor`,
and `InterpreterPoolExecutor` are not just similar.
They all subclass `Executor` and inherit `submit()` and `map()` from it.
A function written against that base class runs unmodified on any of them:

```python
# any_executor.py
from concurrent.futures import (
    Executor,
    InterpreterPoolExecutor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    return order * 10

def run_on(executor: Executor, orders: list[int]) -> list[int]:
    with executor:
        return list(executor.map(cpu_price, orders))

def main() -> None:
    orders = [1, 2, 3, 4, 5]
    backends: list[Executor] = [
        ThreadPoolExecutor(),
        ProcessPoolExecutor(),
        InterpreterPoolExecutor(),
    ]
    results = [run_on(b, orders) for b in backends]
    print(results[0])
    print(all(r == results[0] for r in results))

if __name__ == "__main__":
    main()
```

`run_on()` never mentions which backend it received,
only the shape every `Executor` shares.
Passing the same five orders through all three prints the identical `[10, 20, 30, 40, 50]`,
then `True` for the check that all three answers matched.
Underneath, the three workers could not be more different, an OS thread,
an OS process, a subinterpreter, but `run_on()` cannot see that,
and does not need to.

`asyncio` has no seat at that table.
An `Executor` blocks a worker and hands back a result.
A coroutine is the opposite shape,
a suspended function the event loop resumes on its own schedule.
The second point of convergence is `await`.
A native coroutine, a `to_thread()` call,
and a `run_in_executor()` call all produce the same thing an `async def` can wait on,
so `TaskGroup`, from [Structured Concurrency with TaskGroup](#structured-concurrency-with-taskgroup),
does not care which kind of task it is holding either:

```python
# mixed_await.py
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

async def io_price(order: int) -> int:
    await asyncio.sleep(0.05)  # A native coroutine
    return order * 10

def blocking_price(order: int) -> int:
    time.sleep(0.05)  # A blocking call, needs a thread
    return order * 10

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Needs its own process
        total += 1
    return order * 10

async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool, cpu_price, order)

async def main() -> None:
    with ProcessPoolExecutor() as pool:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(io_price(1)),
                tg.create_task(asyncio.to_thread(blocking_price, 2)),
                tg.create_task(process_price(pool, 3)),
            ]
    print([t.result() for t in tasks])

if __name__ == "__main__":
    asyncio.run(main())
```

Three different backends are running inside that one `TaskGroup`.
`io_price()` suspends and resumes on the event loop the way `fetch()` did in this chapter's first listing.
`to_thread()` hands `blocking_price()` to a worker thread the way it did in `to_thread.py`.
`process_price()` hands `cpu_price()` to a worker process the way `parallel_cpu.py` did,
wrapped in one `async def` so `TaskGroup` can hold it alongside the others.
All three start together, and the block does not exit until all three finish,
printing `[10, 20, 30]`.
The event loop is doing the same job it did in the chapter's first listing.
It schedules awaitables,
and it no longer cares whether the work underneath is a coroutine, a thread,
or a process.

Neither of these is a single `Task` class hiding three incompatible `run()` methods behind one name,
the shortcut that looks tempting and soon breaks.
`Executor` unifies backends that share a blocking, submit-and-wait shape.
`await` unifies backends that share nothing but a promised result.
Knowing which kind of sameness a piece of code relies on,
and which real differences it does not erase,
is most of what concurrency asks of you.

![Asyncio and threads share a single GIL and take turns.
Processes and subinterpreters genuinely run at once
(five separate GILs)](_images/concurrency_models)

## Concurrency is Not Easy

Concurrency is neither simple nor solved.

This is how confused we are about concurrency:
there are ongoing arguments about what the term even means!
Rob Pike, creator of the Go language, famously muddied the waters by declaring,
"concurrency is not parallelism"
(I'm hoping he meant to say "concurrency is not **only** parallelism").[^concurrency-def]
In everyday English,
*concurrent* means "operating or occurring at the same time."
By that definition, concurrency and parallelism are the same thing.

The people who declare "concurrency is easy!" have dipped their toes in it and never encountered a tricky problem.
I've made concurrency look easy in this chapter only because I haven't done much with the issue of shared mutable state other than demonstrating the danger and saying "avoid it,
your life will be simpler."

Even when you understand the problems produced by shared mutable state,
you might not have a choice.
Some systems need as much data as possible packed into RAM,
and in those cases you almost inevitably share mutable state.
Some problems allow immutability.
Others require memory efficiency over everything.
These are the kinds of decisions you must make when you move from the examples presented in this chapter into serious real-world concurrency.

People have worked tirelessly to find better ways to program concurrently.
Only in the last decade or so have advances such as async/await and structured concurrency become widely accepted.
The vocabulary this chapter built,
from processes and threads to tasks and coroutines,
is a small corner of the territory.
Here are a few of the topics beyond it:

- **Locks:** Grant exclusive access to a shared resource so only one thread or task touches it at a time.
- **Semaphores:** Limit how many threads or tasks may hold a resource at once,
  generalizing a lock from one holder to a fixed count.
- **Barriers:** Make a group of threads or tasks wait until every one of them arrives,
  then release them together.
- **Message passing and channels:** Let concurrent units exchange data by sending values through a queue-like channel instead of sharing memory directly.
- **Software transactional memory
  (STM):** Runs a block of code as an atomic transaction against shared memory,
  retrying automatically if another thread interfered.
- **Deadlocks:** Happen when two or more threads each wait forever for a resource the other one holds.
- **Livelocks:** Happen when threads keep reacting to each other and changing state,
  but none of them makes progress.
- **Memory models and data races:** Define which writes by one thread are guaranteed visible to another,
  and what happens when two threads touch the same memory with no synchronization between them.
- **Actor languages:** Give each unit of concurrency the shape of an actor,
  an isolated object that reacts only to messages, never shares state directly,
  and can spawn more actors.
- **Communicating Sequential Processes
  (CSP):** Models concurrency as independent processes that communicate only over explicit channels,
  the approach Go's goroutines and channels are built on.
- **Erlang and Elixir:** Treat each unit of concurrency as an isolated process that shares nothing and talks only through messages.
  Erlang was built at Ericsson for telephone switches.
  Elixir is newer, built on the same BEAM virtual machine.
- The list goes on...

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

[^concurrency-def]: Pike's own definition, from the same talk,
clarifies what he meant.
    Concurrency is the composition of independently executing computations.
    Parallelism is running those computations at the same time.
    You can have concurrency without parallelism.
    The `asyncio` examples in this chapter show it.
    Coroutines interleave on a single thread, and no two of them ever execute at the same instant.

    The distinction goes back further than Pike's 2012 talk at Heroku's Waza conference.
    Edsger Dijkstra's 1965 paper, "Solution of a Problem in Concurrent Programming Control,"
    started the formal study of concurrent programs.
    Leslie Lamport's 2015 Turing Lecture,
    "The Computer Science of Concurrency: The Early Years,"
    surveys the decades since.
