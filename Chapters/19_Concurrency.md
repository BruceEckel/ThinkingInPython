# Concurrency

[Performance](18_Performance.md) makes one stream of instructions faster.
*Concurrency* runs independent tasks so they happen "at the same time" instead of waiting in line.
Performance is about the math, while concurrency is about the machine.
Both try to speed progress.

The meaning of "at the same time" depends on context.
Early machines had a single CPU, and early operating systems (OS)
were basically just program loaders.
The first step beyond that was *time-sharing*.
The CPU runs one program for a slice of time,
then the OS stops it and switches to a different program for another time slice.
Later came a finer-grained unit of scheduling that lives inside a program:
the *thread of execution*.
A modern OS schedules threads, not whole programs.
We say that each task (unit of work) is allocated its own thread,
and the OS performs *context switching* from one thread to the next.
The OS controls everything: allocating threads,
deciding how long a time slice is, performing the context switch,
and deciding which thread is ready to run next.

Each *process* (allocated to a program when you start it)
gets one thread and its own heap.
Every thread has its own stack.
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

The heap and the stack grow in opposite ways.
The heap has no space reserved for it in advance.
It starts essentially empty and grows only as the program asks for more,
one allocation at a time.
A stack is the reverse: its maximum size is fixed when its thread is created,
and that size never changes.
What varies at runtime is the amount used out of that fixed allotment.
If a chain of function calls needs more room than the maximum,
the stack overflows instead of growing to fit.
A heap allocation is reached only through a reference,
which can be redirected to a new, larger block.
A stack is addressed directly by the code running on it,
so it cannot be moved to a new location.

A context switch must preserve the state of the current thread before switching to a different thread.
It stores the CPU register set, which includes:

- The program counter (the next instruction to execute)
- The stack pointer
- Other registers and flags used by the program

The thread's stack is not copied because every thread has its own stack.
There is only a single heap, shared between all threads in that process.

Context switching between threads is as efficient as possible,
but it still has overhead.
Also, the OS must time slice fairly frequently to evenly distribute computing resources across threads.
Typically a thread only runs a few milliseconds at a time.

Using more than one thread within a program solves an immediate problem.
When a thread gets stuck (*blocked*) waiting for I/O
(e.g. disk, network, waiting on a lock),
it hands its CPU back to the operating system.
While that thread is blocked, the OS can run other threads,
producing faster overall progress.

Another benefit of threads emerged when more CPUs became available on a single machine.
Threads were already designed to distribute computing resources,
so more CPUs simply meant more resources to distribute
(of course, it wasn't quite that easy).
By adapting the threading mechanism,
threads could also perform ad-hoc parallelism:
multiple CPUs could run multiple parts of a program simultaneously.

Although threads are adapted to these purposes,
the OS is always at a disadvantage:
it doesn't know details of the program it's running,
and therefore cannot optimize that program.
For example, the OS does not know what data is important to preserve and what isn't.
If it knew, it could perform faster context switches.
In addition, each thread reserves a stack large enough to serve virtually any program,
even though some tasks need only a fraction of that.
Engineers learned various tricks to make programs run faster despite these disadvantages,
but these tricks made the resulting programs more expensive to create and maintain.

*Asynchrony*, implemented with *coroutines*, moves the context switch out of the OS and into the program.
Engineers don't have to fight the threading system.
The programming language decides, based on its knowledge of the program,
the smallest amount of data to include in the context switch.
The programmer minimizes context switches by deciding when they happen.
This shift in control of context switching greatly simplifies writing and reasoning about the program.

The second big shift was in language-level control of parallelism.
Mapping every parallel task onto its own OS thread worked,
but it pushed all scheduling decisions onto the OS and needed extra machinery
(thread pools, pinning, tuning) to perform well.
Languages and runtimes responded by taking on more of that scheduling,
multiplexing many lightweight,
language-managed tasks onto a smaller number of OS threads.

## I/O-Bound vs CPU-Bound

A task is *I/O-bound* when it waits on something outside the process:
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

Instead of using threads for I/O-bound problems,
asynchrony allows you to create coroutines.
Each coroutine, upon encountering I/O,
suspends itself and yields control ... but not to the OS.
Instead, control is given to the *event loop* which discovers the next available task to run.
This is captured in two keywords and the `asyncio` library:

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
Note that the total wait is the longest delay (0.03 seconds),
not the sum of all three.

An `await` is only legal inside an `async def`,
which is why the demonstration needs `main()`.

Beware a list comprehension that awaits.
`[await c for c in coroutines]` becomes the sequential version of `gather()`.
Each `await` runs its coroutine to completion before the next one starts,
so nothing overlaps and the delays add.
`gather()` is concurrent because it wraps and *schedules* every coroutine as a task before it waits for any of them.

Scheduling does not mean running.
The task bodies execute only after `gather()` suspends
(the event loop drives `gather()` too).
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

The following two examples use common code:

```python
# utils/fetch_demo.py
import asyncio

PAIRS = [
    ("a", 0.01),
    ("b", 0.02),
    ("c", 0.03),
    ("d", 0.03),
    ("e", 0.2),
    ("f", 0.3),
]

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item in ("c", "d"):
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()
```

`a` and `b` have the shortest delays and succeed.
`c` and `d` share the same delay, so they fail together.
`e` and `f` are still sleeping when that happens,
with a wide gap to their own deadlines.
The gap gives cancellation time to arrive first on any platform's timer,
which keeps the trace deterministic.

`asyncio.TaskGroup` (added in 3.11) is the structured alternative.
An `async with` block owns every task started inside it and does not exit until every one is accounted for:

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
        for exc in group.exceptions:
            print(f"caught: {exc}")
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
#: f: started
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: caught: fetch('d') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: cancelled
#: f: cancelled
```

`tg.create_task()` schedules a task immediately,
so all six are in flight together.
`c` and `d` raise at the same 0.03-second mark,
and the `TaskGroup` responds by cancelling `e` and `f`,
which are still suspended with far more sleep to go,
so neither ever reaches its `fetched` print.

Only when every task has finished or been cancelled does the block exit.
As it exits, it re-raises both failures wrapped in an *exception group*,
a container for simultaneous failures,
since more than one task can fail at once.
The `except*` form catches members of a group by type,
and iterating through `group.exceptions` reaches every member.

Keeping the task objects pays off even after a partial failure.
`a` and `b` already succeeded, and their results are untouched:
`task.result()` returns `'A'` and `'B'`, as if nothing else had gone wrong.
`c` and `d` each completed with their own exception,
so `task.exception()` returns the `ValueError` instead of raising it.
`e` and `f` never reach their `fetched` print because the group cancels them,
so `task.cancelled()` is `True` for both.
A partial failure cancels whatever was still in flight.
It does not erase what already succeeded.

When failure is not termination but data,
`gather(..., return_exceptions=True)` handles the situation differently:

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
        match result:
            case BaseException():
                print(f"{item}: raised {result!r}")
            case _:
                print(f"{item}: {result}")

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: f: started
#: a: fetched
#: b: fetched
#: e: fetched
#: f: fetched
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: E
#: f: F
```

Again, `c` and `d` fail at the 0.03-second mark, but this time nothing stops.
`gather()` does not supervise its siblings the way `TaskGroup` does.
`e` and `f` are not cancelled.
Both keep sleeping and eventually print their `fetched` line.
`return_exceptions=True` catches both `ValueError`s and places them in the result list,
in argument order, alongside the successful results.
Nothing propagates, so no `try`/`except*` is needed at the call site.

This is the trade `gather()` offers instead of `TaskGroup`'s all-or-cancel contract.
For a batch where partial failure is data to examine rather than a reason to stop,
`return_exceptions=True` collects failures as values instead of cancelling whatever is still in flight.
A health check across ten services needs all the answers including the errors,
not a cancelled remainder of the batch.
`TaskGroup` has no such mode.
Its contract is all-or-cancel.
Keeping siblings alive past a failure means catching exceptions inside each task yourself.
Use `TaskGroup` where a failure should stop the batch.
`gather()` provides failure-as-data.

## Overlapping the Waits

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits, the event loop finds another task to run in the meantime.

In the following example, the same price lookup appears twice.
`io_price()` awaits `asyncio.sleep()` as a stand-in for a network call.
`cpu_price()` performs computations to represent heavy work.
A `Meter` records the peak number of tasks in flight at once.
`Meter` is a [context manager](15_Context_Managers.md):
`__enter__()` counts the task in flight, `__exit__()` counts it done,
and `__exit__()` runs even if the body raises an exception:

```python
# peak_concurrency.py
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
The I/O tasks each reach their `await`, at which point that task suspends.
All five are in flight at once: peak 5.
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

Notice that you cannot `await time.sleep()`,
which is an extra indicator that it is the wrong function to use.

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

async def offloaded_wait() -> None:
    await asyncio.to_thread(time.sleep, 0.05)  # Runs in a thread

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(*(offloaded_wait() for _ in range(5)))
    elapsed = time.perf_counter() - start
    print(f"offloaded sleeps overlap: {elapsed < 0.05 * 2}")

asyncio.run(main())
#: offloaded sleeps overlap: True
```

`offloaded_wait()` calls the same `time.sleep()` that stalled `blocking_the_loop.py`'s `blocking_wait()`,
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
just as the same race between threads needs a `threading.Lock`.

## Parallelism

A CPU-bound task cannot overlap if only a single core is available.
Give it several cores and it can.
`ProcessPoolExecutor` runs each call in its own process,
each with its own interpreter and GIL,
so the operating system can place them on different cores and run them at the same time:

```python
# parallel_cpu.py
from concurrent.futures import ProcessPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
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
But it is no longer on a single shared interpreter on a single core.
The work has been distributed across multiple interpreters,
each on its own core.
With enough cores the wall-clock time falls toward the time of a single task.

Two issues separate a process pool from every in-process tool in this chapter,
and both surface in this short listing:

1. The `if __name__ == "__main__"` guard is not decoration.
   To create a worker, the operating system starts a fresh Python interpreter,
   and that interpreter *imports* this module to find `cpu_price()`.
   During the import the module's name is not `"__main__"`,
   so the guard keeps each worker from running `main()` and building a pool of workers of its own.
   Leave it out and Python detects the runaway spawning and raises `RuntimeError`.
2. Work crosses the process boundary by *pickling*.
   Each argument and each return value is serialized in one process and rebuilt in the other.
   The function itself travels by name,
   so it must be importable from the top level of the module.
   Passing a `lambda` to `pool.map()` fails with a pickling error.
   This echoes [Performance](18_Performance.md#converting-a-slow-function-to-rust)'s coarse-interface rule:
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
    for _ in range(1_000_000):  # Processor work
        total += 1
    results.put((order, order * 10))

def main() -> None:
    orders = [1, 2, 3, 4, 5]
    results: mp.Queue = mp.Queue()
    workers = [
        mp.Process(target=cpu_price, args=(order, results))
        for order in orders
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

Everything `pool.map()` did is now explicit: starting each worker,
waiting for it to finish, and reassembling results that can arrive in any order
(`sorted()` restores the input order, since each result is tagged with its `order`).
*Draining* a queue means reading every item out of it until it is empty.
Doing that after `join()` only works here because all five results are small enough for every worker to finish writing without needing a reader first.
A queue carrying bulky data must be drained *before* joining:
each worker's feeder thread blocks until its data is consumed,
so the `join()` would deadlock.

`ProcessPoolExecutor` is built on `multiprocessing`.
It reuses a pool of workers instead of spawning one process per call,
returns ordered results without manual bookkeeping,
and shares its `submit()`/`map()`/`Future` interface with `ThreadPoolExecutor`,
so switching between processes and threads, as the next section does,
is a one-line change.

A pool fits work shaped like a function call: one call in, one result out.
Use `multiprocessing` when the job is a different shape:

- A worker that runs continuously and communicates over its own `Queue`.
- Processes that share state through a `multiprocessing.Manager`, `Value`,
  or `Array`.
  `ProcessPoolExecutor` does not expose these.

We can test the claim that wall-clock time falls toward a single task's time as we add more cores.
Split a fixed amount of work into a growing number of tasks,
keep the pool warm across every measurement,
and watch what happens once task count passes the number of cores:

```python
# task_scaling.py
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Final

TOTAL: Final[int] = 20_000_000  # Loop iterations, split across tasks
CORE_MULTIPLIER: Final[int] = 2  # Largest sweep point = cores * this

def work_chunk(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i  # CPU-intensive
    return total

def timed_split(
    pool: ProcessPoolExecutor, total_work: int, tasks: int
) -> float:
    chunk = total_work // tasks
    start = time.perf_counter()
    list(pool.map(work_chunk, [chunk] * tasks))
    return time.perf_counter() - start

if __name__ == "__main__":
    cores = os.cpu_count() or 1
    max_tasks = cores * CORE_MULTIPLIER
    doubled = {2**i for i in range(20) if 2**i <= max_tasks}
    task_counts = sorted(doubled | {cores, max_tasks})
    print(f"cores = {cores}, total = {TOTAL}")

    with ProcessPoolExecutor() as pool:
        list(pool.map(work_chunk, [1]))  # Warm up, not timed
        baseline: float | None = None
        for tasks in task_counts:
            elapsed = timed_split(pool, TOTAL, tasks)
            baseline = baseline or elapsed
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({baseline / elapsed:4.2f}x)"
            )
```

The only difference between one run and another is how finely the total work gets split.

The pool is created once and warmed up with a throwaway call before any measurement starts.
This way, process startup delays never leak into a timed result.
Each later call reuses that same pool,
so only the split changes from one line of output to the next.

Wall time drops sharply as the split grows from one task to one task per core,
then keeps dropping a little past that point as smaller,
more numerous chunks balance the load better across workers,
before flattening out.

Task counts double from 1 up to `CORE_MULTIPLIER` times the core count,
so the sweep covers well below, at, and beyond the number of cores available.
One run on a 32-core machine produced this:

    cores = 32, total = 20000000
      1 tasks:  0.600s (1.00x)
      2 tasks:  0.367s (1.64x)
      4 tasks:  0.247s (2.43x)
      8 tasks:  0.186s (3.22x)
     16 tasks:  0.145s (4.14x)
     32 tasks:  0.103s (5.85x)
     64 tasks:  0.111s (5.42x)

This is one machine's real output.
Exact timings shift with load and hardware, but the shape holds:
wall time drops sharply up to the core count,
then flattens or even reverses past it,
as doubling from 32 to 64 tasks did here.
`TOTAL` and `CORE_MULTIPLIER` are the two constants worth changing:
raise `TOTAL` for a slower, more dramatic slope on your own machine,
or lower `CORE_MULTIPLIER` to stop the sweep right at the core count instead of past it.

### Why Speedup Isn't Linear

`task_scaling.py`'s curve keeps dropping, then flattens.
This is *Amdahl's Law*.
Every parallel job carries some part that cannot be split.
Building each chunk, pickling it across the process boundary,
and reassembling the results are unavoidably serial,
whatever else runs on more cores.
If that serial part is a fraction *s* of the total work,
the best any number of cores can do is:

    speedup(n) = 1 / (s + (1 − s) / n)

As *n* → ∞, that ceiling approaches 1 / *s* and stops climbing.
A job that spends 10 percent of its time in serial overhead never speeds up more than tenfold,
on 16 cores or 1,600.

Splitting into more, smaller tasks buys real gains up to a point,
since finer chunks even out the load across workers, as described above.
Past that point, though,
each additional task adds its own slice of the same serial overhead:
one more chunk to pickle, one more result to collect.
Once that added overhead outweighs the benefit of the smaller pieces,
the curve stops falling.
This ceiling is not specific to `ProcessPoolExecutor`, or even to Python;
it applies to any system that divides work across independent workers,
which is why adding cores is not, by itself, a scaling strategy.

## The GIL and Free Threading

Threads don't help with the previous section's CPU-bound work.
The standard CPython build has a *Global Interpreter Lock* (GIL).
With the GIL, only one thread runs Python bytecode at a time,
no matter how many cores sit idle.

However, a thread waiting on I/O releases the GIL.
That release is why a thread pool helps with I/O-bound work.
The next two examples make that concrete, one for waiting and one for computing.
Both use the same harness,
which runs a price function sequentially and threaded, confirms they agree,
and times each:

```python
# thread_compare.py
import timeit
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

def compare(
    price: Callable[[int], int], orders: list[int], number: int
) -> tuple[float, float]:
    def sequential() -> list[int]:
        return [price(o) for o in orders]

    def threaded() -> list[int]:
        with ThreadPoolExecutor() as pool:
            return list(pool.map(price, orders))

    assert threaded() == sequential()
    t_seq = timeit.timeit(sequential, number=number)
    t_thr = timeit.timeit(threaded, number=number)
    return t_seq, t_thr
```

Here `time.sleep()` stands in for a blocking network call,
and five threads overlap five of those waits even with the GIL in place:

```python
# io_threads.py
import time
from thread_compare import compare

def io_price(order: int) -> int:
    time.sleep(0.05)  # Stand-in for I/O
    return order * 10

orders = [1, 2, 3, 4, 5]
t_seq, t_thr = compare(io_price, orders, number=1)
print(f"threads at least 3x faster on I/O: {t_thr * 3 < t_seq}")
#: threads at least 3x faster on I/O: True
```

Five 50-millisecond waits finish in about the time of one.
Each sleeping thread has released the GIL,
so the operating system runs another thread while it waits,
the same overlap `asyncio` achieved with suspended tasks.
This is `blocking_the_loop.py` turned inside out:
a blocking call freezes an event loop,
but a pool of threads absorbs blocking calls.
This is why `asyncio.to_thread()` hands its blocking work to this kind of pool.
Use a thread pool for I/O when the blocking calls already exist and rewriting them as coroutines is not worth the surgery.
`asyncio` pays off when you have thousands of waits,
since tasks are far lighter than threads.

In contrast, a thread that is computing never releases the GIL for another thread to run:

```python
# gil_threads.py
from thread_compare import compare

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

orders = [1, 2, 3, 4, 5]
t_seq, t_thr = compare(cpu_price, orders, number=5)
print(f"threads no faster: {t_thr > t_seq * 0.9}")
#: threads no faster: True
```

Swapping the loop for a thread pool changes nothing.
Five threads still take turns holding the one GIL,
so the threaded run costs the same as the sequential one,
sometimes a little more because of the added scheduling.
This is why [Parallelism](#parallelism) used processes instead.
Each process gets its own interpreter with its own GIL.

### Why Python Has a GIL

*(This condenses my PyCon 2026 presentation [Demystifying the GIL](https://github.com/BruceEckel/DemystifyingTheGIL), which includes a short book that covers each topic in depth.)*

The GIL is the consequence of three earlier decisions.
Each was reasonable on its own.
In 1990, Python adopted *reference counting* for memory management.
Every object carries a count of the references to it.
When the count reaches zero, the object is freed immediately.
This gave Python deterministic cleanup with no collector pauses.

It also added a cost.
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

The lock ensures that reference counts stay consistent,
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
Here the call is a one-microsecond `time.sleep()`, which is a blocking call.
Blocking calls release the GIL:

```python
# gil_race.py
import time
from concurrent.futures import ThreadPoolExecutor

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        time.sleep(0.000_001)  # Let other threads run
        counter = value + 1  # Write back

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: True
```

Eight threads each add 50, so `counter` should reach 400.
A typical run lands near 50.
Each sleep releases the GIL between a read and its write,
so all eight threads read the same value,
and their eight writes store the same result.

At full speed, with no deliberate sleep, the GIL made this race rare.
But it never made it impossible.
Threads that share mutable state need a lock,
or a queue like the one in [Coordinating Threads with Queues](#coordinating-threads-with-queues).

### Free Threading

Since 3.13, CPython also provides a *free-threaded* build,
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
Permanent objects like `None`, `True`, and small integers become *immortal*.
Their counts never change.
Immortality landed in 3.12 for every build but pays off most here,
since it removes the one atomic operation every thread would otherwise contest.
Mutable containers like dictionaries and lists carry individual locks,
so two threads contend only when they touch the same container.
Single-threaded code pays a small penalty for this machinery,
roughly five to fifteen percent depending on the workload,
but this should improve in future releases.

Removing the lock also removed three decades of accidental protection for C extensions,
which were written assuming that only one thread runs at a time.
The free-threaded build comes with a safety net.
Loading an extension that has not declared itself thread-safe re-enables the GIL for the whole process and emits a warning.
Free threading pays off only when every extension you load has been audited,
so check compatibility before switching a project.

Free threading also rewards a particular program shape.
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

## Subinterpreters

Subinterpreters work on standard Python, and do not need free threading.
The process pool in [Parallelism](#parallelism)
gets its speedup by giving each worker its own interpreter,
and thus its own GIL, but it pays with an operating-system process per worker.

Since 3.12, CPython can create additional interpreters inside the same process
([PEP 684](https://peps.python.org/pep-0684/)), each with its own GIL,
avoiding the per-worker process cost.
`InterpreterPoolExecutor` (added in 3.14)
runs each call in one of these subinterpreters.
Within a single process, multiple interpreters run in parallel:

```python
# subinterpreters.py
import timeit
from concurrent.futures import InterpreterPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [cpu_price(o) for o in orders]

orders = [1, 2, 3, 4, 5]
t_seq = timeit.timeit(lambda: sequential(orders), number=5)

with InterpreterPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)
    t_sub = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

print(f"subinterpreters at least 1.5x faster: {t_seq > t_sub * 1.5}")
#: subinterpreters at least 1.5x faster: True
```

Unlike a thread pool, this genuinely overlaps computation.
Each worker interpreter holds its own GIL,
so several of them run on separate cores at once instead of taking turns.
The interpreters share the process's memory,
but each keeps its own isolated objects.
Arguments and results cross that boundary by copying.

A subinterpreter needs no separate build and no separate install,
which makes it the first thing to try for CPU-bound work,
before a process pool or a free-threaded interpreter.
The one compatibility check mirrors free threading's: pure Python always works,
but a C extension must support per-interpreter isolation to be imported in a subinterpreter.

## Coordinating Threads with Queues

When threads divide up work, the danger is shared mutable state.
The standard solution is a thread-safe queue that hands each item to a single consumer,
with built-in locking.
`queue.Queue` is first-in, first-out, while `queue.PriorityQueue`
(the threaded form of `heapq` seen in [Performance](18_Performance.md))
always produces the smallest item:

```python
# priority_queue.py
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue

type Job = tuple[int, str]  # (priority, description)

tasks: PriorityQueue[Job] = PriorityQueue()

def enqueue(jobs: list[Job]) -> None:
    for job in jobs:
        tasks.put(job)

with ThreadPoolExecutor(max_workers=2) as pool:
    pool.submit(enqueue, [(3, "backup"), (1, "page oncall")])
    pool.submit(enqueue, [(2, "rotate logs"), (1, "alert")])

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (2, 'rotate logs')
#: (3, 'backup')
```

The four jobs arrive from two threads in an unpredictable interleaving,
but the drain comes out in priority order no matter who won each race.
When two jobs share a priority,
tuple comparison falls through to the second field, the description string.

Producers calling `put()` and consumers calling `get()` is how thread pools distribute work.
`get()` blocks until an item is available, so an idle consumer simply waits.
The [Object Pool](15_Context_Managers.md#an-object-pool)
in Context Managers uses the same `Queue` as a throttle.

`while not tasks.empty()` is trustworthy here only because the `with` block already waited for both producers to finish before it exited,
so nothing can add or remove an item while this loop runs.

That guarantee is specific to this listing.
While other threads are still adding or removing items,
`empty()`'s answer can be true the instant it returns and already wrong by the time the loop acts on it.
A live consumer does not poll `empty()` at all;
it calls `get()` directly and lets the block do the waiting.

Python provides three queue classes with near-identical interfaces,
the first two of which we've already seen:

- `queue.Queue` (and its sibling `PriorityQueue`)
  coordinates threads within one interpreter,
  protecting its internals with locks.
- `multiprocessing.Queue`, seen in `multiprocessing_raw.py`,
  carries items across process boundaries by pickling them.
- `asyncio.Queue`, which coordinates tasks on an event loop.

`asyncio.Queue` has an `await queue.get()` that suspends the calling task instead of blocking the thread:

```python
# async_queue.py
import asyncio

async def consumer(queue: asyncio.Queue[str]) -> None:
    item = await queue.get()  # Suspends until an item arrives
    print(f"consumed {item}")

async def producer(queue: asyncio.Queue[str]) -> None:
    await asyncio.sleep(0.01)  # Stand-in for slow work
    await queue.put("data")

async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(consumer(queue))
        tg.create_task(producer(queue))

asyncio.run(main())
#: consumed data
```

`consumer` starts first and finds the queue empty,
so `get()` suspends it rather than blocking the thread underneath it.
`producer` then runs, sleeps to stand in for slow work, and puts an item,
which wakes the waiting `consumer`.
`asyncio.Queue` needs no locks,
since the event loop lets only one coroutine touch it at a time.
That guarantee holds only within the event loop's own thread.
Call it from another thread and nothing protects it,
which is why the class is not thread-safe.

The similar queue interfaces hide a consequential difference.
`queue.Queue` and `multiprocessing.Queue` block the calling thread while they wait.
`asyncio.Queue` suspends a task instead.
As `blocking_the_loop.py` showed,
a blocked thread freezes every task on an event loop,
while a suspended task lets the rest keep running.
Match the queue to the concurrency model.

## One Task, Many Backends

Every section so far has kept threads, processes, subinterpreters,
and `asyncio` apart.
Blending them without knowing which parts are compatible produces races and pickling errors.
Two real points of convergence exist in the standard library, though,
not because the models are secretly the same,
but because two small pieces of them genuinely are.

The first is `concurrent.futures.Executor`.
`ThreadPoolExecutor`, `ProcessPoolExecutor`,
and `InterpreterPoolExecutor` are not just similar.
They all subclass `Executor` and inherit `submit()` and `map()` from it.
A function written against that base class runs unmodified on all three:

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
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def run_on(executor: Executor, orders: list[int]) -> list[int]:
    with executor:
        return list(executor.map(cpu_price, orders))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    backends: list[Executor] = [
        ThreadPoolExecutor(),
        ProcessPoolExecutor(),
        InterpreterPoolExecutor(),
    ]
    results = [run_on(b, orders) for b in backends]
    print(results[0])
    print(all(r == results[0] for r in results))
```

`run_on()` accepts the base type `Executor`, so it takes all three subtypes,
whose workers could not be more different: an OS thread, an OS process,
a subinterpreter.

`asyncio` does not fit here.
An `Executor` blocks a worker and hands back a result.
A coroutine does the opposite.
It is a suspended function that runs only when the event loop resumes it.

The second point of convergence is `await`.
A native coroutine, a `to_thread()` call,
and a `run_in_executor()` call all produce an *awaitable*.
[`TaskGroup`](#structured-concurrency-with-taskgroup)
does not care which kind of task it is holding:

```python
# mixed_await.py
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

async def io_price(order: int) -> int:
    await asyncio.sleep(0.05)  # Native coroutine
    return order * 10

def blocking_price(order: int) -> int:
    time.sleep(0.05)  # Blocking call, needs a thread
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

Three different backends are running inside one `TaskGroup`.
`io_price()` suspends and resumes on the event loop the way `fetch()` did in this chapter's first listing.
`to_thread()` hands `blocking_price()` to a worker thread the way it did in `to_thread.py`.
`process_price()` hands `cpu_price()` to a worker process the way `parallel_cpu.py` did,
wrapped in one `async def` so `TaskGroup` can hold it alongside the others.
All three start together, and the block does not exit until all three finish.
The event loop is doing the same job it did in the chapter's first listing.
It schedules awaitables,
and it no longer cares whether the work underneath is a coroutine, a thread,
or a process.

Each of these two interfaces unifies one small piece of the backends,
not the whole.
`Executor` unifies backends that share a blocking, submit-and-wait shape.
`await` unifies backends that share nothing but a promised result.
Everything else about the backends stays different.
Most of what concurrency asks of you is knowing what a shared interface hides,
and what it leaves different underneath.

![Asyncio and threads share a single GIL and take turns.
Processes and subinterpreters genuinely run at once
(five separate GILs)](_images/concurrency_models)

### Are Threads Still Necessary?

`asyncio` handles I/O-bound work.
Processes and subinterpreters handle CPU-bound work.
With both halves covered, does new code ever need threads?

It does, but not for the reason threads were once the default choice.
[I/O-Bound vs CPU-Bound](#io-bound-vs-cpu-bound)
divides concurrent work into two kinds, and neither kind needs threads.
`asyncio` overlaps waits on external operations.
A process pool or [subinterpreter](#subinterpreters)
overlaps CPU-bound computing.

What role remains for threads?
Creating bridges to code that doesn't cooperate with an event loop.
Most database drivers, most GUI toolkits,
and plenty of C extensions block the calling thread and expose no `async` entry point.

If Python had always supported coroutines,
all libraries could be expected to conform.
But rewriting all existing libraries to use `asyncio` instead of threads is not realistic.
`asyncio.to_thread()`, from [Escaping to a Thread](#escaping-to-a-thread),
is the standard library solution.
Thus, even a program written as `asyncio` from top to bottom keeps a thread pool underneath,
because the libraries it calls still block.

Free threading, however, does not affect I/O-bound work.
It solves a narrower problem: without the GIL,
a thread can genuinely parallelize CPU-bound work from inside one process while sharing memory directly,
paying no pickling cost at all.
This is something neither a GIL-bound thread nor a process pool offers.
With the GIL, a thread no longer structures your concurrency.
`asyncio` does that.
A thread's remaining job is to absorb a blocking call,
so the wait cannot freeze the event loop.

The GIL [does not prevent races](#the-gil-does-not-prevent-races).
It doesn't protect a read-modify-write spanning a function call.
With free threading,
two threads can execute at the same instant on separate cores.
Race conditions become even easier.

`asyncio` only switches at an `await`,
which makes it easier to [reason about interleaving](#a-single-thread-still-races).
A thread costs an OS stack and an OS scheduling entity that free threading does not remove,
while an `asyncio` task is cheap enough to run in the thousands.
[`TaskGroup`](#structured-concurrency-with-taskgroup)'s structured,
cancellable batches have no thread equivalent.
There is still no safe way to cancel a running thread.
Free threading changes what a thread is for.
It does not change what `asyncio` is for.

### Measuring the Difference

We can support the claim that a thread costs real memory while a task costs much less.
`threading.stack_size()` reports and sets the stack CPython reserves for each new thread.
A common default across platforms is on the order of one mebibyte.^[A mebibyte (MiB) is 2<sup>20</sup> while a megabyte (MB) is 10<sup>6</sup>.]
`tracemalloc` can measure a task's actual heap footprint directly,
since a task is made of ordinary Python objects.
We can calculate the ratio between the two:

```python
# task_vs_thread_memory.py
import asyncio
import threading
import tracemalloc

TASKS = 5_000
STACK_SIZE = 1024 * 1024  # 1 MiB, a common thread stack reservation

async def parked() -> None:
    await asyncio.sleep(999)  # Suspended, never resumes

async def bytes_per_task() -> float:
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    tasks = [asyncio.create_task(parked()) for _ in range(TASKS)]
    await asyncio.sleep(0)  # Let every task reach its own await
    after = tracemalloc.take_snapshot()
    grown = sum(
        stat.size_diff
        for stat in after.compare_to(before, "lineno")
        if stat.size_diff > 0
    )
    for t in tasks:
        t.cancel()
    # Without "return_exceptions=True", the first CancelledError
    # would raise an exception and exit the function:
    await asyncio.gather(*tasks, return_exceptions=True)
    tracemalloc.stop()
    return grown / TASKS

default_stack = threading.stack_size()
threading.stack_size(STACK_SIZE)  # A real, settable cost
configured_stack = threading.stack_size()
threading.stack_size(default_stack)  # Restore the previous setting

task_cost = asyncio.run(bytes_per_task())
tasks_per_stack = configured_stack / task_cost
print(f"one thread's stack reservation: {configured_stack:,} bytes")
print(f"average bytes per task: {task_cost:.0f}")
print(f"tasks fitting in one thread's stack: {tasks_per_stack:.0f}")
print(f"holds over 200 tasks: {tasks_per_stack > 200}")
#: one thread's stack reservation: 1,048,576 bytes
#: average bytes per task: 1350
#: tasks fitting in one thread's stack: 777
#: holds over 200 tasks: True
```

`bytes_per_task()` creates 5,000 tasks that immediately suspend on `asyncio.sleep(999)`,
so they stay alive doing nothing.
The two `tracemalloc` snapshots capture the heap they add.
`threading.stack_size()` is read, set, read again, then restored,
so the measurement leaves the rest of the program untouched.
A single thread's reserved stack,
paid before it runs one line of its target function,
could instead hold roughly 777 suspended tasks.
The stack figure is address space set aside whether every byte is touched or not.
The task figure is heap measured by `tracemalloc`.
The comparison favors tasks over threads by hundreds to one.

We see a similar difference in time:

```python
# thread_vs_task_speed.py
import asyncio
import threading
import time

COUNT = 3000

def noop() -> None:
    pass

async def async_noop() -> None:
    pass

def spawn_threads() -> float:
    start = time.perf_counter()
    threads = [threading.Thread(target=noop) for _ in range(COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

async def spawn_async_tasks() -> float:
    start = time.perf_counter()
    await asyncio.gather(*(async_noop() for _ in range(COUNT)))
    return time.perf_counter() - start

t_threads = spawn_threads()
t_tasks = asyncio.run(spawn_async_tasks())
print(f"tasks at least 5x faster to spawn: {t_tasks * 5 < t_threads}")
#: tasks at least 5x faster to spawn: True
```

Starting and joining 3,000 threads does OS-level work for each one,
allocating a stack, registering with the scheduler, tearing it down again.
Scheduling 3,000 tasks skips all of that.
`gather()` only builds Python objects and steps the event loop through them.

How many threads can one machine support before `Thread.start()` raises `RuntimeError: can't start new thread`?
That number belongs to the machine, not to Python.
On one well-provisioned machine,
60,000 threads parked on a never-set `threading.Event` started in about four seconds with room to spare.
A laptop with far less memory can fail at a fraction of that.
To find your own machine's number,
raise `COUNT` in `thread_vs_task_speed.py` until thread creation raises an exception.
Tasks have no equivalent ceiling,
because a task consumes none of the OS resources that limit threads.

## Locks, Semaphores, and Failure Modes

`async_race.py` showed shared mutable state losing updates with no coordination in place,
but using tasks instead of threads.
Threads are not the source of deadlock and livelock.
That source is shared mutable state,
and `asyncio` shares it just as readily as threads do.
Removing the OS thread scheduler does not remove these failure modes.
It only moves where they can happen.
With threads, that point is anywhere the OS decides to preempt you.
`asyncio` narrows this to the `await` points you wrote yourself.

### Locks

A *lock* grants exclusive access to a shared resource so only one task holds it at a time.
Wrapping the read-modify-write from `async_race.py` in an `asyncio.Lock` restores the missing updates by serializing access to `counter`:

```python
# async_locks.py
import asyncio

counter = 0
lock = asyncio.Lock()

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        async with lock:
            value = counter  # Read
            await asyncio.sleep(0)  # Yield to the event loop
            counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
```

The only change from `async_race.py` is the addition of `async with lock`.
This protects the read, the yielding `await`, and the write.
If a task reaches `async with lock` while another task already holds the lock,
it suspends itself until that lock becomes available.
This way, only one task's read-modify-write is ever in progress,
no matter how many times the event loop switches to another task in between.
All 400 increments now occur,
the same fix `threading.Lock` produces for threads.

### Semaphores

A *semaphore* generalizes a lock from a single lock-holder to a fixed number of them.
Where a lock admits one task,
`asyncio.Semaphore(n)` admits up to `n` at once and suspends the rest:

```python
# async_semaphore.py
import asyncio

active = 0
peak = 0
semaphore = asyncio.Semaphore(2)

async def worker() -> None:
    global active, peak
    async with semaphore:
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.05)
        active -= 1

async def main() -> None:
    await asyncio.gather(*(worker() for _ in range(5)))
    print(f"peak concurrent workers: {peak}")

asyncio.run(main())
#: peak concurrent workers: 2
```

Five tasks start together, but `semaphore` admits only two at a time.
`peak` tracks the same live-count idea as `Meter` in [Overlapping the Waits](#overlapping-the-waits).
A threaded equivalent of this worker would need its own lock around `active += 1` and `peak = max(peak, active)`,
since a preemptive switch could land between them.
Here, the first `await` comes after both updates,
so the task keeps control through them and needs no lock.

A semaphore initialized to one behaves exactly like a lock.
Raising the count turns it into a throttle on a limited resource,
such as a fixed number of database connections.

### Deadlock

*Deadlock* happens when two or more tasks each hold a resource the other needs,
so neither can proceed.
Four conditions must all hold at once:

1. Exclusive access to each resource
2. A task holds one resource while it waits for another
3. No way to force a task to give up what it holds
4. A cycle of tasks each waiting on the next

Break any one of the four and deadlock becomes impossible.
None of these conditions mentions threads or an OS scheduler,
which means we can also produce deadlock with `asyncio`.
This example has two tasks and two `asyncio.Lock` objects.
The two locks are acquired in opposite order:

```python
# async_deadlock.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(first: asyncio.Lock, second: asyncio.Lock) -> None:
    async with first:
        await asyncio.sleep(0.01)  # Let the other task grab its lock
        async with second:
            pass  # Never reached

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker(lock_a, lock_b),
                worker(lock_b, lock_a),
            ),
            timeout=0.5,
        )
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: deadlock detected
```

The first task takes `lock_a` then reaches for `lock_b`.
The second takes `lock_b` then reaches for `lock_a`.
The `sleep(0.01)` gives each task time to grab its first lock before either reaches for its second.
Tasks, unlike threads, run one at a time,
so no OS scheduler can interleave the two tasks' first lines in an unlucky order.

Once both hold their first lock,
each task's `async with second:` suspends on a lock the other holds and will never release.
A real deadlock has no `timeout` and never resolves.
Both tasks wait forever, the event loop included,
since nothing remains that can wake them.
Here, the timeout ensures that the example terminates.

The fix is the same one that works for threads:
have every task acquire shared locks in the same global order.
If both tasks had reached for `lock_a` first,
whichever got there first would finish and release that lock before the other waited.

### Livelock

A *livelock* blocks nothing.
Tasks keep running and keep changing state, but none of them makes progress,
the way two people in a hallway each step aside for the other, forever.
No lock is involved, so no timeout can fix it, and there is nothing to acquire:

```python
# async_livelock.py
import asyncio

a_wants = True
b_wants = True

async def giver(name: str) -> None:
    global a_wants, b_wants
    for _ in range(3):
        other_wants = b_wants if name == "a" else a_wants
        if other_wants:
            print(f"{name}: gives")
        else:
            print(f"{name}: proceeds")
            if name == "a":
                a_wants = False
            else:
                b_wants = False
        await asyncio.sleep(0)

async def main() -> None:
    await asyncio.gather(giver("a"), giver("b"))
    print(f"resolved: {not (a_wants or b_wants)}")

asyncio.run(main())
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: a: gives
#: b: gives
#: resolved: False
```

Each round, `a` checks `b_wants` and `b` checks `a_wants`,
and both still see the other wanting the resource, so both give.
Thus both still want it on the next round.
Being polite when interacting with a task that is equally polite produces no progress at all,
even though the event loop keeps both tasks busy the whole time.

A real livelock looks busy on a monitor,
with CPU time spent and state visibly changing.
A deadlock looks idle, with tasks parked and waiting.
In both cases, nothing gets done.
The usual fix is to break the symmetry,
for example letting only the task with the lower ID give.

## Guidelines

- **Remember that concurrency is a performance tool.**
  Explore [Performance](18_Performance.md)
  before deciding you require a concurrent solution.
- **Don't wrap a lone wait in `async`/`await` machinery.**
  `asyncio` pays off once you have multiple waits that overlap.
- **A comprehension that awaits is not concurrent.**
  `[await c for c in coroutines]` runs one coroutine at a time.
  Only `gather()` or `TaskGroup` schedule every coroutine as a task before waiting on any of them.
- **Choose `TaskGroup` when a failure should stop the batch,
  `gather(return_exceptions=True)` when it shouldn't.**
  `TaskGroup`'s contract is all-or-cancel.
  `gather()` can hand back errors as data alongside the successes.
- **A read-modify-write that spans an `await` still races,
  with no thread in sight.**
  Guard it with `asyncio.Lock`, the same fix a lock gives for threads.
- **Never call a blocking function inside a coroutine.**
  `time.sleep()` freezes every task on the loop, not just its own.
  Use `asyncio.sleep()`, or hand the blocking call to `asyncio.to_thread()`.
- **Prefer `ProcessPoolExecutor` over raw `multiprocessing`.**
  A pool fits work shaped like a function call: one call in, one result out.
  Use raw `multiprocessing` when the job is a different shape:
  a worker that runs continuously,
  or processes that share state through a `Manager`.
- **More cores only speed up the parallel fraction of the work.**
  Splitting past the number of cores sometimes buys a little more.
  Then the per-task cost of pickling and reassembling catches up,
  and the gains flatten (Amdahl's Law).
- **For CPU-bound work, try a subinterpreter first, a process pool second,
  and a free-threaded build only once every extension you use is known to support it.**
- **Match the queue to the concurrency model.**
  `queue.Queue` blocks a thread,
  `multiprocessing.Queue` pickles across processes,
  `asyncio.Queue` suspends a task and needs no locking.
- **A shared lock only prevents deadlock if every user agrees on the order.**
  Acquire shared locks in the same sequence everywhere.
  When two units keep yielding to each other instead,
  break the symmetry so only one of them gives way.

## Concurrency is Not Easy

Concurrency is neither simple nor solved.

There are ongoing arguments about what the term even means.
Rob Pike, creator of the Go language, famously muddied the waters by declaring,
"concurrency is not parallelism"
(I'm hoping he meant to say "concurrency is not **only** parallelism").[^concurrency-def]
As we've seen in this chapter,
concurrency means "operating or occurring at the same time."
This works for both asynchrony and parallelism.

Also, notice how much we've talked about the OS in this chapter.
The comfortable abstraction provided by normal programming is pierced to tatters by concurrency.
Sometimes you need to go beyond the OS-level abstraction all the way to hardware,
in order to understand a particular bug.

Someone who declares "concurrency is easy!" has dipped their toes in it and never encountered a tricky problem.
This chapter makes concurrency look (somewhat)
easy because it has only touched the surface of shared mutable state problems.

Even when you understand the problems produced by shared mutable state,
you might not have a choice.
Some problems preclude immutability.
For example, a solution might require packing as much data as possible into RAM.
In those cases you almost inevitably share mutable state.
These are the kinds of decisions you must make when you move from the examples presented in this chapter into serious real-world concurrency.

People continue to work toward better ways of concurrent programming.[^libraries]
Only in the last decade or so have advances such as async/await and structured concurrency become widely accepted.
The vocabulary this chapter built,
from processes and threads to tasks and coroutines,
is a small corner of the territory.
Here are a few of the topics beyond it:

- **Barriers:** Make a group of threads or tasks wait until every one of them arrives,
  then release them together.
  Unlike `gather()` or `TaskGroup`,
  a barrier is a rendezvous point the running code reaches and blocks on itself,
  often reused across repeated phases,
  not a supervisor waiting from outside for everything to finish.
- **Message passing and channels:** Let concurrent units exchange data by sending values instead of sharing memory directly.
  Actor languages and CSP, below,
  are two different disciplines built on this same idea.
- **Actor languages:** Give each unit of concurrency the shape of an actor,
  an isolated object that reacts only to messages sent to its own mailbox,
  never shares state directly, and can spawn more actors.
  The most established production examples include Erlang,
  built at Ericsson for telephone switches.
  Elixir is newer and built on the Erlang's BEAM virtual machine.
- **Communicating Sequential Processes
  (CSP):** Independent processes that communicate only over explicit,
  shared channels, rather than an actor's private mailbox.
  This is the approach Go's goroutines and channels are built on.
- **Software transactional memory
  (STM):** Runs a block of code as an atomic transaction against shared memory,
  retrying automatically if another thread interferes.[^stm-status]
- **Memory models and data races:** Define which writes by one thread are guaranteed visible to another,
  and what happens when two threads touch the same memory with no synchronization between them.

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
3.  In `peak_concurrency.py`, add a third task function, `mixed_price()`,
    that awaits `asyncio.sleep(0.05)` and then also runs the 1,000,000-iteration loop from `cpu_price()`.
    Run it through `run()` and predict its `meter.peak` before checking:
    is it closer to the I/O peak or the CPU peak?
4.  In `peak_concurrency.py`,
    change `io_price()`'s `await asyncio.sleep(0.05)` to `time.sleep(0.05)` and predict what happens to its `meter.peak` before running it.
    Explain the result using `blocking_the_loop.py`.
5.  In `async_locks.py`,
    replace `lock = asyncio.Lock()` with `lock = asyncio.Semaphore(1)`.
    Confirm `counter` still reaches `400`,
    and explain why a semaphore initialized to `1` behaves exactly like a lock.
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

[^concurrency-def]: Pike's definition from that talk clarifies what he meant.
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

[^stm-status]: Python has no mainstream STM library today.
    PyPy-STM, an experimental PyPy variant from 2012 to 2015,
    used STM internally to remove the GIL and exposed a
    `with __pypy__.thread.atomic:` block for ordinary Python code.
    PyPy's own documentation now treats it as discontinued.
    GIL-removal research moved instead to [fine-grained locking](#free-threading).
    A couple of academic prototypes exist (PSTM, TraM),
    but neither is a maintained library suited to real code.
    Haskell's `Control.Concurrent.STM` and Clojure's `ref`/`dosync`
    are where STM actually succeeded as a practical, widely used tool.

[^libraries]: Libraries worth exploring:

    - [BOCPY](https://microsoft.github.io/bocpy/): Behavior-Oriented Concurrency
    - [Trio](https://trio.readthedocs.io/): Origin of structured concurrency
    - [AnyIO](https://pypi.org/project/anyio/): Bridge between Trio and asyncio
    - [uvloop](https://github.com/MagicStack/uvloop):
      Fast drop-in replacement for the standard event loop.
      See also [rsloop](https://github.com/RustedBytes/rsloop).
