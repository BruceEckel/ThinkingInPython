# Concurrency

[Performance](18_Techniques--Performance.md)
makes one stream of instructions faster.
*Concurrency* runs independent tasks so they happen "at the same time" instead of waiting in line.
Performance is about the math, while concurrency is about the machine.
Both try to speed progress.

The meaning of "at the same time" depends on context.
Early machines had a single CPU, and early operating systems (OS)
were little more than program loaders.
The first step beyond that was *time-sharing*.
The CPU runs one program for a slice of time,
then the OS stops it and switches to a different program for another time slice.
Later came a finer-grained unit of scheduling that lives inside a program:
the *thread of execution*.
A modern OS schedules threads, not whole programs.
Each task (unit of work) gets its own thread,
and the OS performs *context switching* from one thread to the next.
The OS controls everything: allocating threads,
deciding how long a time slice is, switching contexts,
and deciding which thread is ready to run next.

Each *process* (allocated to a program when you start it)
gets one thread and its own heap.
Every thread has its own stack.
The program can request more threads from the OS,
but all threads within a process share the same heap.
So each thread must not corrupt parts of the heap other threads use.

When a program requests an additional thread from the OS,
that thread gets its own function-call stack,
separate from the original process stack.
Every function call pushes arguments and the return address onto the stack.
When the function ends,
its stack frame pops off and execution jumps back to the return address.
(The return value typically travels back in a CPU register.)
Thus each thread must own its call stack.

The heap and the stack grow in opposite ways.
The heap reserves no space in advance.
It starts essentially empty and grows only as the program asks for more,
one allocation at a time.
A stack is the reverse: creating the thread fixes its maximum size,
and that size never changes.
The amount used out of that fixed allotment varies at runtime.
If a chain of function calls needs more room than the maximum,
the stack overflows instead of growing to fit.
Code reaches a heap allocation only through a reference,
which can point at a new, larger block instead.
The code running on a stack addresses it directly,
so the stack cannot move to a new location.

A context switch must preserve the state of the current thread before switching to a different thread.
It stores the CPU register set, which includes:

- The program counter (the next instruction to execute)
- The stack pointer
- Other registers and flags the program uses

The context switch does not copy the thread's stack,
since every thread has its own.
All threads in that process share a single heap.

Context switching between threads is as efficient as possible,
but it still has overhead.
Also, the OS must time slice frequently to distribute computing resources evenly across threads.
Typically a thread runs only a few milliseconds at a time.

Using more than one thread within a program solves an immediate problem.
When a thread gets stuck (*blocked*) waiting for I/O
(e.g. disk, network, waiting on a lock),
it hands its CPU back to the operating system.
While that thread waits, the OS can run other threads,
producing faster overall progress.

Another benefit of threads emerged when more CPUs became available on a single machine.
Threads were already designed to distribute computing resources,
so more CPUs simply meant more resources to distribute
(of course, it wasn't quite that easy).
Adapting the threading mechanism let threads also perform ad-hoc parallelism:
multiple CPUs could run multiple parts of a program simultaneously.

Although threads serve these purposes, the OS is always at a disadvantage:
it doesn't know details of the program it's running,
and therefore cannot optimize that program.
For example, the OS does not know what data is important to preserve and what isn't.
If it knew, it could switch contexts faster.
In addition, each thread reserves a stack large enough to serve virtually any program,
even though some tasks need only a fraction of that.
Engineers learned tricks to make programs run faster despite these disadvantages,
but these tricks made the resulting programs more expensive to create and maintain.

*Asynchrony*, implemented with *coroutines*,
moves the context switch out of the OS and into the program.
Engineers don't have to fight the threading system.
The programming language decides, based on its knowledge of the program,
the smallest amount of data to include in the context switch.
The programmer minimizes context switches by deciding when they happen.
Moving that control into the program simplifies both writing the program and reasoning about it.

The second big shift changed who decides to use parallelism.
Mapping every parallel task onto its own OS thread worked,
but it pushed all scheduling decisions onto the OS and needed extra machinery
(thread pools, pinning, tuning) to perform well.
Languages and runtimes responded by taking scheduling back:
Go and Java multiplex lightweight tasks onto a pool of OS threads,
while Python gives each parallel worker its own interpreter,
in a separate process or, since 3.12, inside the current process.

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
Two other approaches appear later in this chapter,
each running inside a single process.

## `async def`, `await`, and the Event Loop {#asyncio-mechanics}

Instead of using threads for I/O-bound problems,
asynchrony lets you create coroutines.
Each coroutine, upon encountering I/O,
suspends itself and yields control ... but not to the OS.
Instead, control goes to the *event loop*,
which discovers the next available task to run.
Two keywords and the `asyncio` library capture this:

1. `async def` defines a *coroutine function*.
   Calling it returns a *coroutine object*,
   a description of work that has not started, and runs nothing.
2. `await` starts that work and pauses the awaiting coroutine until the result is ready.
   While that coroutine waits,
   the *event loop* finds other coroutines ready to run.
3. `asyncio.gather()` awaits several coroutines at once and collects their results in order.
4. `asyncio.run()` starts the event loop, runs one coroutine to completion,
   and shuts the loop down.
   This is the entry point, called once to run the program.
   Calling it from inside a coroutine raises `RuntimeError: asyncio.run() cannot be called from a running event loop`.
   Inside an `async def`, `await` the coroutine directly:

```python
# async_mechanics.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    # Stand-in for a network request
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    x = fetch("a", 0.03)  # Nothing runs yet
    print(type(x).__name__)
    # Run all three concurrently
    results = await asyncio.gather(
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

The first printed line proves that calling a coroutine runs nothing.
`main()`'s first line calls `fetch("a", 0.03)`, yet no "started" line appears,
only the type of object the call built: `coroutine`.
The work begins when `gather()` receives that object.
If you forget `await gather()`, nothing runs.
Python points this out with a `RuntimeWarning: coroutine 'fetch' was never awaited` when the garbage collector reclaims the forgotten object.

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
so all three are in flight during the first wait.

Suspending also registers a wake-up condition with the event loop.
`asyncio.sleep()` asks for a timer,
but a real network request asks the loop to watch a socket for the reply.
When the timer fires, the loop resumes that task where it paused,
just after the `await`.

The three delays make the resumptions visible: c sleeps shortest,
so its timer fires first, and the resumed lines print as c, b, a,
the reverse of the starting order.
`gather()` returns `['A', 'B', 'C']`,
showing that the results follow the argument order, not the finishing order.
The total wait is the longest delay (0.03 seconds), not the sum of all three.

An `await` is legal only inside an `async def`,
and that is why the demonstration needs `main()`.

Beware a list comprehension that awaits.
`[await c for c in coroutines]` becomes the sequential version of `gather()`.
Each `await` runs its coroutine to completion before the next one starts,
so nothing overlaps and the delays add.
`gather()` is concurrent because it wraps and schedules every coroutine as a task before it waits for any of them.

Scheduling does not mean running.
The task bodies execute only after `gather()` suspends
(the event loop drives `gather()` too).
Each runs until its first `await`, which the trace's `started` lines record.
The comprehension never has more than one coroutine in flight:
it starts the next coroutine only after the previous one has finished.

## Structured Concurrency with `TaskGroup`

What happens if `gather()` encounters a failure?
If one of its coroutines raises an exception,
`gather()` re-raises that exception into the awaiting code,
but the other tasks it started keep running.
Those other tasks become unsupervised, and their results and errors vanish.

The following two examples use common code:

```python
# utils/fetch_demo.py
import asyncio
from typing import Final

PAIRS: Final[list[tuple[str, float]]] = [
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
and that margin keeps the trace deterministic.

`asyncio.TaskGroup` (added in 3.11) is the structured alternative.
An `async with` block owns every task started inside it and exits only after it has accounted for every one:

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
Holding the task objects is essential bookkeeping.
The event loop keeps only weak references to its tasks,
so a task that loses its last strong reference can disappear mid-execution,
printing nothing and raising no exception.
A `TaskGroup` holds its own references until the block exits.
Outside one, keep the returned task in a variable or a set that outlives it.
`c` and `d` raise exceptions at the same 0.03-second mark,
and the `TaskGroup` responds by cancelling `e` and `f`,
which are still suspended with far more sleep to go,
so neither ever reaches its `fetched` print.

The block exits once every task has either finished or ended in cancellation.
As it exits, it re-raises both failures wrapped in an *exception group*,
a container for simultaneous failures,
since more than one task can fail at once.
The `except*` form catches members of a group by type,
and iterating through `group.exceptions` reaches every member.

The `except*` form matters.
A `TaskGroup` always wraps what it re-raises, even when exactly one task failed,
so a plain `except ValueError:` around the `async with` block catches nothing,
and the `ExceptionGroup` travels past it uncaught.

Keeping the task objects pays off even after a partial failure.
`a` and `b` already succeeded, and their results stay untouched:
`task.result()` returns `'A'` and `'B'`, as if nothing else had gone wrong.
`c` and `d` each completed with their own exception,
so `task.exception()` returns the `ValueError` instead of raising it.
`e` and `f` never reach their `fetched` print because the group cancels them,
so `task.cancelled()` is `True` for both.
A partial failure cancels whatever was still in flight.
It does not erase what already succeeded.

Cancellation reaches a task by raising `asyncio.CancelledError` inside it,
at whichever `await` currently suspends it.
That exception derives from `BaseException` rather than `Exception`,
and the choice is deliberate.
A `try`/`except Exception` written inside a task to log and continue does not catch cancellation,
so the task still stops the way the group intended.
The mistake runs the other way:
a bare `except:` or an `except BaseException:` around an `await` catches the cancellation and keeps the task running,
and then the `TaskGroup` block waits on a task it ordered to stop.
If a task must clean up as it stops, catch `asyncio.CancelledError` by name,
do the cleanup, and re-raise it.

When failure is not termination but data,
`gather(..., return_exceptions=True)` handles the situation differently:

```python
# gather_with_exceptions.py
import asyncio
from typing import assert_never
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
            case str():
                print(f"{item}: {result}")
            case _:
                assert_never(result)

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

Again, `c` and `d` fail at the 0.03-second mark,
but this time the rest continue.
`gather()` leaves its siblings unsupervised, where `TaskGroup` cancels them,
so `e` and `f` keep sleeping and eventually print their `fetched` line.
`return_exceptions=True` catches both `ValueError`s and places them in the result list,
in argument order, alongside the successful results.
Nothing propagates, so the call site needs no `try`/`except*`.

That behavior is the trade `gather()` offers in place of `TaskGroup`'s all-or-cancel contract.
For a batch where partial failure is data to examine rather than a reason to stop,
`return_exceptions=True` collects failures as values instead of cancelling whatever is still in flight.
A health check across ten services needs all the answers including the errors,
not a cancelled remainder of the batch.
`TaskGroup` has no such mode.
Keeping siblings alive past a failure means catching exceptions inside each task yourself.

You can also stop a `TaskGroup` deliberately.
`tg.cancel()` (3.15) cancels every task in the group,
for the case where the answer arrives before the batch finishes and the remaining work has lost its value.

### Bounding a Wait with `asyncio.timeout()`

Every delay in this chapter so far is a fixed `asyncio.sleep()`,
so nothing has needed a time limit.
A real network call carries no such guarantee.
`asyncio.timeout()` (3.11) bounds how long a block of code may run,
and it composes with `TaskGroup` the way a `with` block composes with anything inside it:

```python
# async_timeout.py
import asyncio

async def slow(delay: float) -> str:
    await asyncio.sleep(delay)
    return "done"

async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(slow(0.01))
                tg.create_task(slow(0.5))
    except TimeoutError:
        print("timed out")

asyncio.run(main())
#: timed out
```

The group holds a fast task and a slow one.
`asyncio.timeout()`'s deadline passes well before the slow task's,
so it cancels the task running `main()`.
The resulting `asyncio.CancelledError` reaches the `TaskGroup`,
which cancels both children and re-raises as it exits.
Because the cancellation traces back to its own deadline,
`asyncio.timeout()` converts that `CancelledError` into a `TimeoutError` on its way out,
so the caller sees an ordinary exception instead of a bare cancellation.
`asyncio.wait_for()` bounds one awaitable the same way;
[`async_deadlock.py`](#deadlock)
uses it as an escape hatch so that demo doesn't hang forever.
`asyncio.timeout()` is the newer, composable form,
scoping the deadline over an entire block, `TaskGroup` included,
instead of one call.

## Overlapping the Waits

`asyncio` runs many tasks on one thread by switching between them at each `await`.
When a task awaits, the event loop finds another task to run in the meantime.

In the following example, the same price lookup appears twice.
`io_price()` awaits `asyncio.sleep()` as a stand-in for a network call.
`cpu_price()` counts through a million iterations as a stand-in for heavy computing.
A `Meter` records the peak number of tasks in flight at once.
`Meter` is a [context manager](15_Techniques--Context_Managers.md):
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
Each I/O task reaches its `await` and suspends there.
All five are in flight at once: peak 5.
The CPU tasks never `await`, so each runs to the end before the next starts:
peak 1.

The event loop overlaps waiting, not computing.

`asyncio.sleep()` in `io_price` is not `time.sleep()`.
Awaiting `asyncio.sleep()` suspends only the current task and hands control to the event loop,
which lets all five `io_price` tasks overlap.
`time.sleep()` is a blocking call: it stops the whole thread,
so a coroutine that calls it freezes every task in the program, not just itself:

```python
# blocking_the_loop.py
import asyncio
import time
from collections.abc import Awaitable, Iterable
from benchmark import report

async def yielding_wait() -> None:
    await asyncio.sleep(0.05)  # Suspends this task only

async def blocking_wait() -> None:
    time.sleep(0.05)  # Stops the event loop

async def elapsed(
    tasks: Iterable[Awaitable[None]]
) -> float:
    start = time.perf_counter()
    await asyncio.gather(*tasks)
    return time.perf_counter() - start

async def main() -> None:
    t_yield = await elapsed(
        yielding_wait() for _ in range(5))
    t_block = await elapsed(
        blocking_wait() for _ in range(5))
    report(awaited=t_yield, blocking=t_block)
    print(f"awaited sleeps overlap: {t_yield < 0.05 * 2}")
    print(
        f"blocking sleeps serialize: {t_block >= 0.05 * 5}")

asyncio.run(main())
#: awaited sleeps overlap: True
#: blocking sleeps serialize: True
```

Five awaited sleeps finish together in about the time of one.
Five blocking sleeps run one after another:
each stalls the loop for its full duration, so the total is at least their sum.

`await time.sleep()` raises a `TypeError`,
since the call returns `None` and `None` is not awaitable:
another sign that `time.sleep()` is the wrong function here.

### A Real Socket

Every listing so far stands in for network I/O with `asyncio.sleep()`.
[`async def`, `await`, and the Event Loop](#asyncio-mechanics)
claimed that a real request "asks the loop to watch a socket for the reply,"
and every example since has left that claim untested.
`asyncio.start_server()` and `asyncio.open_connection()` are the real thing,
a listening socket and a client connecting to it, both on `localhost`:

```python
# network_io.py
import asyncio

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    line = await reader.readline()
    writer.write(b"echo: " + line)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def request(port: int, message: str) -> str:
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", port)
    writer.write(message.encode() + b"\n")
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()

async def main() -> None:
    server = await asyncio.start_server(
        handle_client, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    async with server:
        replies = await asyncio.gather(
            request(port, "a"), request(port, "b"))
    print(replies)

asyncio.run(main())
#: ['echo: a', 'echo: b']
```

`start_server()` opens a listening socket on an OS-assigned port
(port `0` asks the OS to choose one)
and hands each new connection to `handle_client()`.
`open_connection()` opens the client side of that same socket.
Both awaits suspend their task exactly the way `asyncio.sleep()` did,
except the wake-up condition is now "the socket has bytes to read," not a timer.
Two clients connect at once,
and `gather()` returns their replies in argument order, `a` then `b`,
the same guarantee `async_mechanics.py` made for sleeps.
`async with server:` closes the listening socket once both requests finish.

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
from benchmark import report

async def offloaded_wait() -> None:
    # Runs in a thread
    await asyncio.to_thread(time.sleep, 0.05)

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(
        *(offloaded_wait() for _ in range(5)))
    elapsed = time.perf_counter() - start
    report(elapsed=elapsed)
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

[Simulation](38_Patterns--Simulation.md)
builds a full program on these mechanics:
a pack of rats exploring a maze as cooperating tasks,
and [Observer](30_Patterns--Observer.md#observer-and-io)
uses `gather()` to notify slow observers together instead of one at a time.

## A Single Thread Still Races

`asyncio` runs one coroutine at a time, never two at once,
and that fact tempts you to conclude that shared state needs no locking.
But "one at a time" protects only the instructions between two `await`s,
not a value that lives across one.
Two coroutines that read a shared value, `await`,
then write it back can lose an update with no thread and no [GIL](#the-gil-and-free-threading)
in sight:

```python
# async_race.py
import asyncio

counter = 0

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        # Release control to the event loop
        await asyncio.sleep(0)
        counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 50
```

Eight coroutines each add 50, so `counter` should reach 400.
Instead it stops at 50.
Every `await asyncio.sleep(0)` releases control to the event loop before the write.
(The `sleep(0)` is a stand-in for a database query or an HTTP call.)
In each round all eight coroutines read the same value before any of them writes,
so eight additions collapse into one.

[The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races)
shows the identical failure with threads.
A thread switch is preemptive,
occurring at points the interpreter picks and you did not choose,
while a coroutine yields only at an `await` you chose to write.
That makes the gap easier to find, not safer to leave unguarded.
A read-modify-write that spans an `await` needs `asyncio.Lock`,
just as the same race between threads needs a `threading.Lock`.

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
            # Yield to the event loop
            await asyncio.sleep(0)
            counter = value + 1  # Write

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
```

The only change from `async_race.py` is `async with lock`.
The block protects the read, the yielding `await`, and the write.
If a task reaches `async with lock` while another task already holds the lock,
it suspends itself until that lock becomes available.
This way, only one task runs its read-modify-write at a time,
no matter how many times the event loop switches to another task in between.
The counter now reaches 400, the same fix `threading.Lock` produces for threads.
An `asyncio.Lock` orders tasks on one event loop and gives no protection across threads.
A worker thread reached through `asyncio.to_thread()` needs a `threading.Lock`.
[Locks, Semaphores, and Failure Modes](#locks-semaphores-and-failure-modes)
takes up the rest of the coordination primitives, and the ways they fail.

## Context That Follows the Call Chain {#context-that-follows-the-call-chain}

Some values are not the subject of the work but the circumstances of it:
which request the code is serving, which user authorized it,
which trace to use for logging.
Everything deep in the call chain needs them and nothing in the middle uses them.
Threading such a value through as a parameter puts it in signatures that have no business knowing about it,
and every new caller must remember to pass it along.

A module-level global is the obvious shortcut,
and it fails as soon as anything overlaps.
`async_race.py` showed why: whatever wrote last wins,
and the readers resume to find a value that belongs to somebody else.
A `ContextVar` is the same convenience without that failure.
It holds a value per *context*,
and every task starts with a copy of the context that created it,
so one task's `set()` is invisible to its siblings and to its parent:

```python
# context_var.py
import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id",
                                         default="-")
current = "-"  # The same idea as a plain global

async def handle(name: str) -> None:
    global current
    current = name
    request_id.set(name)
    await asyncio.sleep(0)  # Stand-in for a database call
    print(f"context {request_id.get()}, global {current}")

async def main() -> None:
    async with asyncio.TaskGroup() as group:
        for name in ("req-1", "req-2", "req-3"):
            group.create_task(handle(name))
    print(f"after: context {request_id.get()}, "
          f"global {current}")

asyncio.run(main())
#: context req-1, global req-3
#: context req-2, global req-3
#: context req-3, global req-3
#: after: context -, global req-3
```

The listing puts the global and the `ContextVar` side by side because they behave differently for the same code.
All three tasks assign both, then suspend at the `await`,
then resume to read them back.
Each task reads its own `request_id` and every task reads the same `current`,
because by the time any of them resumes, the global holds `req-3`.
The last line shows the other direction: `main()` created the tasks,
so their contexts are copies of `main()`'s,
and nothing they set flows back to it.
`request_id` returns to its default while the global stays clobbered.

Deleting the global and writing `handle(name)`'s value into a parameter would work here,
and would keep working until a logging helper four calls down needs the value.
That is the problem a `ContextVar` solves.

You often set a variable for part of a call and restore it afterward,
so the token `set()` returns also works as a context manager (3.14):

```python
# context_scope.py
import asyncio
import threading
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id",
                                         default="-")

def audit(step: str) -> str:
    main = (threading.current_thread()
            is threading.main_thread())
    where = "main thread" if main else "worker thread"
    return f"[{request_id.get()}] {step} on the {where}"

async def handle(name: str) -> None:
    with request_id.set(name):
        print(audit("start"))
        print(await asyncio.to_thread(audit, "offloaded"))
    print(audit("after the scope"))

asyncio.run(handle("req-7"))
#: [req-7] start on the main thread
#: [req-7] offloaded on the worker thread
#: [-] after the scope on the main thread
```

Leaving the `with` block calls `reset()` on the token,
which puts back whatever the variable held before, not the default.
That distinction matters when scopes nest.
Before 3.14 you wrote `token = var.set(x)` and a matching `var.reset(token)` in a `finally`,
which is the same code the context manager now writes for you.

The `offloaded` line is the reason `ContextVar`, rather than `threading.local`,
is the modern answer.
`threading.local` gives each *thread* its own value,
and a thread is the wrong unit twice over.
Thousands of tasks share one event-loop thread, so they would share one value.
And a value stored on a thread does not travel when work moves,
while `asyncio.to_thread()` copies the current context into the worker,
so the offloaded `audit()` still knows which request it is serving.
`contextvars.copy_context()` is the general form,
letting you capture a context and run something else inside it later.

## Parallelism

Everything so far has overlapped waiting on one thread.
Computing is the other half, and it needs a second mechanism.
A CPU-bound task cannot overlap if only a single core is available.
With several cores, it can.
`ProcessPoolExecutor` runs each call in its own process,
each with its own interpreter and its own *Global Interpreter Lock* (GIL),
the interpreter-wide lock that lets only one thread run Python bytecode at a time.
[The GIL and Free Threading](#the-gil-and-free-threading) takes the lock apart.
Here, each interpreter has its own,
so the operating system can place these processes on different cores and run them at the same time:

```python
# parallel_cpu.py
from concurrent.futures import ProcessPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor() as pool:
        prices = list(pool.map(cpu_price, orders))
    print(prices)
```

`pool.map()` sends each order to a worker process and gathers the results in order,
printing `[10, 20, 30, 40, 50]`, the same answer as the other versions.
The computation is the same `cpu_price()` as before.
The work now spreads across multiple interpreters, each on its own core,
instead of one interpreter on one core.
With enough cores the wall-clock time falls toward the time of a single task.

Three issues separate a process pool from the in-process tools in this chapter,
and all three surface in this short listing:

1. The `if __name__ == "__main__"` guard keeps each worker from building a pool of its own.
   To create a worker, the operating system starts a fresh Python interpreter,
   and that interpreter *imports* this module to find `cpu_price()`.
   During the import the module's name is not `"__main__"`,
   so the guarded block stays skipped.
   If you leave it out, each worker re-runs the block,
   tries to build a pool of its own,
   and dies with `RuntimeError: An attempt has been made to start a new process before the current process has finished its bootstrapping phase`.
   The parent sees the worker's death as `BrokenProcessPool`,
   with the worker's `RuntimeError` nested in the traceback above it.
   This used to be a Windows and macOS concern only,
   because Linux forked the parent process instead of importing anything.
   Since 3.14 no platform forks by default,
   so every platform requires the guard.
2. Work crosses the process boundary by *pickling*.
   One process serializes each argument and each return value,
   and the other rebuilds it.
   The function itself travels by name,
   so it must be importable from the top level of the module.
   Passing a `lambda` to `pool.map()` fails with a pickling error.
   That boundary crossing echoes [Performance](18_Techniques--Performance.md#converting-a-slow-function-to-rust)'s coarse-interface rule:
   a million tiny results can cost more to pickle than the parallelism saved.
3. `pool.map()` raises nothing itself.
   It returns a generator,
   and consuming a worker's result re-raises that worker's exception in the calling process.
   The `list(...)` around the call turns a failure in any worker into an exception here,
   at a point you can catch it.
   That third point is true of every `Executor`, not only a process pool.

The `multiprocessing` module underneath `ProcessPoolExecutor` exposes the raw pieces of a separate process:
a `Process` you start and `join()`, and a `Queue` to carry results back,
since a process cannot return a value the way a function call does:

```python
# multiprocessing_raw.py
import multiprocessing as mp

def cpu_price(
    order: int, results: mp.Queue[tuple[int, int]]
) -> None:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    results.put((order, order * 10))

if __name__ == "__main__":
    orders = [1, 2, 3, 4, 5]
    results: mp.Queue[tuple[int, int]] = mp.Queue()
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
```

Everything `pool.map()` did is now explicit: starting each worker,
waiting for it to finish, and reassembling results that can arrive in any order
(`sorted()` restores the input order, since each result carries its `order`).
*Draining* a queue means reading every item out of it until it is empty.
Draining after `join()` works here because all five results are small enough for every worker to finish writing with no reader waiting.
Bulky data changes that:
each worker's feeder thread blocks until a reader consumes its output,
so `join()` deadlocks.
Drain a queue carrying bulky data before joining.

`ProcessPoolExecutor` builds on `multiprocessing`.
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

You can test the claim that wall-clock time falls toward a single task's time as you add more cores.
Split a fixed amount of work into a growing number of tasks,
keep the pool warm across every measurement,
and watch what happens once task count passes the number of cores:

```python
# task_scaling.py
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Final

# Loop iterations, split across tasks
TOTAL: Final[int] = 20_000_000
# Largest sweep point = cores * this
CORE_MULTIPLIER: Final[int] = 2

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
        # Warm up, not timed
        list(pool.map(work_chunk, [1]))
        baseline: float | None = None
        for tasks in task_counts:
            elapsed = timed_split(pool, TOTAL, tasks)
            baseline = baseline or elapsed
            print(
                f"{tasks:>3} tasks: {elapsed:6.3f}s "
                f"({baseline / elapsed:4.2f}x)"
            )
```

The only difference between one run and another is how finely the listing splits the total work.

The listing creates the pool once and warms it up with a throwaway call before any measurement starts,
so process startup never lands in a timed result.
Each later call reuses that same pool,
so only the split changes from one line of output to the next.

Wall time drops sharply as the split grows toward one task per core.
Past that point the curve flattens,
and can turn back upward once pickling one more chunk costs more than the better load balancing saves.

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
or lower `CORE_MULTIPLIER` to stop the sweep at the core count instead of past it.

### Why Speedup Isn't Linear

`task_scaling.py`'s curve keeps dropping, then flattens.
That shape is *Amdahl's Law*.
Every parallel job carries some part that does not split.
Building each chunk, pickling it across the process boundary,
and reassembling the results are unavoidably serial,
whatever else runs on more cores.
If that serial part is a fraction *s* of the total work,
the best any number of cores can do is:

    speedup(n) = 1 / (s + (1 − s) / n)

As *n* → ∞, that ceiling approaches 1 / *s* and stops climbing.
A job that spends 10 percent of its time in serial overhead never speeds up more than tenfold,
on 16 cores or 1,600.

Splitting into more, smaller tasks yields real gains up to a point,
since finer chunks even out the load across workers.
Past that point, though,
each additional task adds its own slice of the same serial overhead:
one more chunk to pickle, one more result to collect.
Once that added overhead outweighs the benefit of the smaller pieces,
the curve stops falling.
The ceiling applies to any system that divides work across independent workers,
in Python or anywhere else, and that is why adding cores is not, by itself,
a scaling strategy.

## The GIL and Free Threading

Threads don't help with the previous section's CPU-bound work.
The standard CPython build has one GIL for the whole process,
so only one thread runs Python bytecode at a time,
no matter how many cores sit idle.

However, a thread waiting on I/O releases the GIL.
That release is why a thread pool helps with I/O-bound work.
The next two examples make that concrete, one for waiting and one for computing.
Both use the same harness,
which runs a price function sequentially and threaded, confirms they agree,
and times each.
Each variant is timed five times,
alternating between the two so a stray background load spike lands on both,
and `min` keeps each variant's best:

```python
# thread_compare.py
import timeit
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple

class Times(NamedTuple):
    sequential: float
    threaded: float

def compare(
    price: Callable[[int], int], orders: list[int],
    number: int
) -> Times:
    def sequential() -> list[int]:
        return [price(o) for o in orders]

    def threaded() -> list[int]:
        with ThreadPoolExecutor() as pool:
            return list(pool.map(price, orders))

    assert threaded() == sequential()
    seq: list[float] = []
    thr: list[float] = []
    for _ in range(5):  # Alternate: a load spike hits both
        seq.append(timeit.timeit(sequential, number=number))
        thr.append(timeit.timeit(threaded, number=number))
    return Times(min(seq), min(thr))
```

Two timings of the same type come back from one call,
so returning them as a bare `tuple[float, float]` leaves every caller remembering which float came first.
`Times` names them, as [Data Transfer Objects](22_Patterns--Data_Transfer_Objects.md#returning-multiple-values)
describes.
The two callers below use the two styles a `NamedTuple` allows,
access by field name and positional unpacking.

Here `time.sleep()` stands in for a blocking network call,
and five threads overlap five of those waits even with the GIL in place:

```python
# io_threads.py
import time
from benchmark import report
from thread_compare import compare

def io_price(order: int) -> int:
    time.sleep(0.05)  # Stand-in for I/O
    return order * 10

orders = [1, 2, 3, 4, 5]
times = compare(io_price, orders, number=1)
report(sequential=times.sequential, threaded=times.threaded)
print("threads at least 3x faster on I/O: "
      f"{times.threaded * 3 < times.sequential}")
#: threads at least 3x faster on I/O: True
```

Five 50-millisecond waits finish in about the time of one.
Each sleeping thread releases the GIL,
so the operating system runs another thread while it waits,
the same overlap `asyncio` achieved with suspended tasks.
That overlap is `blocking_the_loop.py` turned inside out:
a blocking call freezes an event loop,
but a pool of threads absorbs blocking calls.
That absorption is why `asyncio.to_thread()` hands its blocking work to this kind of pool.
Use a thread pool for I/O when the blocking calls already exist and rewriting them as coroutines is not worth the surgery.
`asyncio` pays off when you have thousands of waits,
since tasks are far lighter than threads.

In contrast, a thread that is computing gains nothing when the GIL changes hands:

```python
# gil_threads.py
from benchmark import report
from thread_compare import compare

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

orders = [1, 2, 3, 4, 5]
seq, thr = compare(cpu_price, orders, number=5)
report(sequential=seq, threaded=thr)
print(f"threads no faster: {thr > seq * 0.9}")
#: threads no faster: True
```

Swapping the loop for a thread pool changes nothing.
Five threads still take turns holding the one GIL,
so the threaded run costs the same as the sequential one,
sometimes a little more because of the added scheduling.
That is why [Parallelism](#parallelism) used processes instead.
Each process gets its own interpreter with its own GIL.

### Why Python Has a GIL

*(This condenses my PyCon 2026 presentation [Demystifying the GIL](https://github.com/BruceEckel/DemystifyingTheGIL), which includes a short book that covers each topic in depth.)*

The GIL is the consequence of three earlier decisions.
Each was reasonable on its own.
In 1990, Python adopted *reference counting* for memory management.
Every object carries a count of the references to it.
When the count reaches zero, the interpreter frees the object immediately.
This gave Python deterministic cleanup with no collector pauses.

It also added a cost.
Every count update is a read-modify-write sequence,
and the interpreter runs millions of them per second.

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
Attempts kept failing to clear it, so workarounds appeared instead.
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

Since 3.10 the interpreter switches threads only at a function call or at the jump that closes a loop iteration,
so nothing interrupts this particular sequence in practice.
That is scheduling luck, not safety.

Any function call between the read and the write reopens the gap.
Here the call is a one-microsecond `time.sleep()`, a blocking call.
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
A typical run settles near 50.
Each sleep releases the GIL between a read and its write,
so all eight threads read the same value,
and their eight writes store the same result.

At full speed, with no deliberate sleep, the GIL makes this race rare.
But it never makes it impossible.
Threads that share mutable state need a lock,
or a queue like the one in [Coordinating Threads with Queues](#coordinating-threads-with-queues).
The fix mirrors `async_locks.py`'s: wrap the read, the sleep,
and the write in a `threading.Lock`:

```python
# gil_locks.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor

counter = 0
lock = threading.Lock()

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        with lock:
            value = counter  # Read
            time.sleep(0.000_001)  # Let others run
            counter = value + 1  # Write back

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lock preserves every update: "
      f"{counter == 8 * 50}")
#: lock preserves every update: True
```

The only change from `gil_race.py` is the `with lock:` block wrapped around the read-modify-write.
Eight threads still take turns,
but now no two of them ever read the same value before either writes,
so `counter` reaches 400 every time,
the same fix `asyncio.Lock` gave the coroutines in `async_locks.py`.

### Free Threading

Since 3.13, CPython also provides a *free-threaded* build,
tracked by [PEP 703](https://peps.python.org/pep-0703/) and installed separately
(`python3.15t` rather than `python3.15`).
[PEP 779](https://peps.python.org/pep-0779/)
removed its "experimental" label in 3.14,
so it is a supported build now rather than a preview,
still optional and still installed alongside the default one.
It removes the GIL, so threads run Python bytecode on separate cores at the same time.
Under a free-threaded interpreter `gil_threads.py`'s boolean flips to `False`.
Replacing its last line with `print(f"threads speedup: {seq / thr:.1f}x")` reports the size of the win instead of the fact of it:

    threads speedup: 3.8x

(The speedup needs a free-threaded interpreter, which the book's build does not use, so that measurement does not run during verification.
The number is one machine's actual output.)

<!-- TODO(free-threaded-default): if free threading ever becomes
CPython's default build, convert this indented block to a real, fenced,
tested example. -->

Free threading finally cleared the 1996 bar by making reference counting cheap without a global lock.
Usually only one thread touches an object, the one that created it.
*Biased reference counting* lets that owning thread update the count with ordinary,
non-atomic arithmetic.
Only other threads pay for an atomic operation.
Permanent objects like `None`, `True`, and small integers become *immortal*.
Their counts never change.
Immortality arrived in 3.12 for every build but pays off most here,
since it removes the one atomic operation every thread would otherwise contest.
Mutable containers like dictionaries and lists carry individual locks,
so two threads contend only when they touch the same container.
Single-threaded code pays a small penalty for this machinery,
roughly five to fifteen percent depending on the workload,
but this should improve in future releases.

Removing the lock also removed three decades of accidental protection for C extensions,
whose authors assumed that only one thread runs at a time.
The free-threaded build comes with a safety net.
Loading an extension that has not declared itself thread-safe re-enables the GIL for the whole process and emits a warning.
Free threading pays off only when every extension you load has passed an audit,
so check compatibility before switching a project.

Free threading also rewards a particular program shape.
Threads that mostly work on data they do not share, like `threaded()` above,
scale across cores.
The same is true of threads that accumulate results locally and merge them once at the end,
caches read far more often than written,
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
import os
import timeit
from concurrent.futures import InterpreterPoolExecutor
from benchmark import report

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

cores = os.cpu_count() or 1
target = min(1.5, cores * 0.7)  # Two cores cannot give 1.5x
report(sequential=t_seq, subinterpreters=t_sub, cores=cores)
print(f"subinterpreters run in parallel: "
      f"{t_seq > t_sub * target}")
#: subinterpreters run in parallel: True
```

Unlike a thread pool, subinterpreters genuinely overlap computing.
Each worker interpreter holds its own GIL,
so several of them run on separate cores at once instead of taking turns.
The interpreters share the process's memory,
but each keeps its own isolated objects.
Arguments and results cross that boundary by copying.

A subinterpreter needs no separate build and no separate install,
and that makes it the first thing to try for CPU-bound work,
before a process pool or a free-threaded interpreter.
The one compatibility check mirrors free threading's: pure Python always works,
but a C extension must support per-interpreter isolation before a subinterpreter can import it.

## Coordinating Threads with Queues

When threads divide work, the danger comes from shared mutable state.
The standard solution is a thread-safe queue that hands each item to a single consumer,
with built-in locking.
`queue.Queue` is first-in, first-out, while `queue.PriorityQueue`
(the threaded form of `heapq` seen in [Performance](18_Techniques--Performance.md))
always produces the smallest item.
A live consumer thread calls `get()` and lets the block do the waiting,
rather than polling whether the queue is empty:

```python
# priority_queue.py
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, ShutDown

type Job = tuple[int, str]  # (priority, description)

tasks: PriorityQueue[Job] = PriorityQueue()

def enqueue(jobs: list[Job]) -> None:
    for job in jobs:
        tasks.put(job)

def consume() -> None:
    while True:
        try:
            print(tasks.get())
        except ShutDown:
            return

with ThreadPoolExecutor(max_workers=3) as pool:
    producers = [
        pool.submit(enqueue,
                    [(3, "backup"), (1, "page oncall")]),
        pool.submit(enqueue,
                    [(2, "rotate logs"), (1, "alert")]),
    ]
    for p in producers:
        p.result()  # Surface any producer failure
    consumer = pool.submit(consume)
    tasks.shutdown()
    consumer.result()
#: (1, 'alert')
#: (1, 'page oncall')
#: (2, 'rotate logs')
#: (3, 'backup')
```

The four jobs arrive from two threads in an unpredictable interleaving.
Waiting for both producer futures before submitting the consumer guarantees every job is already in the queue once `consume()` starts,
so the drain still comes out in priority order no matter who won each race.
Collecting the producer futures and calling `result()` turns a producer's exception into one you can see,
as [Parallelism](#parallelism)'s third point describes.
When two jobs share a priority,
tuple comparison falls through to the second field, the description string.

`consume()` calls `get()` in a loop, the way a live consumer should:
parked there, it costs nothing while it waits,
and it wakes the instant `put()` adds an item, with no polling in between.
This listing's queue already holds every job by the time `consume()` starts,
so its first `get()` returns immediately,
but the same code runs unchanged whether the queue is empty or already stocked.
The [Object Pool](15_Techniques--Context_Managers.md#an-object-pool)
in Context Managers uses the same `Queue` as a throttle.

A consumer parked in `get()` still needs a way to stop.
`tasks.shutdown()` (3.13) answers that: once the queue runs empty,
every blocked or future `get()` raises `queue.ShutDown` instead of waiting forever.
`consume()` catches it and returns,
so `consumer.result()` completes instead of hanging.
Calling `shutdown()` before every item is drained is safe too;
items already in the queue still come out through `get()` normally,
and only a `get()` against an empty, shut-down queue raises.
A `put()` after `shutdown()` raises the same exception immediately,
which is how a producer discovers that its consumers have already left.

Python provides three queue classes with near-identical interfaces,
the first two of which already appeared in this chapter:

- `queue.Queue` (and its sibling `PriorityQueue`)
  coordinates threads within one interpreter,
  protecting its internals with locks.
- `multiprocessing.Queue`, seen in `multiprocessing_raw.py`,
  carries items across process boundaries by pickling them.
- `asyncio.Queue` coordinates tasks on an event loop.

`asyncio.Queue` has an `await queue.get()` that suspends the calling task instead of blocking the thread:

```python
# async_queue.py
import asyncio

async def consumer(queue: asyncio.Queue[str]) -> None:
    # Suspends until an item arrives
    item = await queue.get()
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
That guarantee holds within the event loop's own thread alone:
a call from another thread has no protection, so the class is not thread-safe.

The similar queue interfaces hide a consequential difference.
`queue.Queue` and `multiprocessing.Queue` block the calling thread while they wait.
`asyncio.Queue` suspends a task instead.
As `blocking_the_loop.py` showed,
a blocked thread freezes every task on an event loop,
while a suspended task lets the rest keep running.
Match the queue to the concurrency model.

## Sharing an Iterator Between Threads {#sharing-an-iterator-between-threads}

A queue is the push half of distributing work:
a producer decides what each consumer gets.
The pull half looks simpler.
Hand every worker the same iterator and let each one take the next item when it is ready.
Nothing in the language stops you, and nothing in the language makes it work.
An iterator has never been thread-safe
([Iterators](23_Patterns--Iterators.md) covers the protocol):

```python
# shared_iterator.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Final

LIMIT: Final[int] = 200

@dataclass
class Tickets:
    limit: int
    next_number: int = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        if self.next_number >= self.limit:
            raise StopIteration
        current = self.next_number
        time.sleep(0.000_001)  # Let other threads run
        self.next_number = current + 1
        return current

def report(label: str, source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(list, source)
                   for _ in range(8)]
        taken = [*f.result() for f in futures]
    print(f"{label}: {len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

report("shared", Tickets(LIMIT))
#: shared: 200 distinct, duplicates True
report("serialized",
       threading.serialize_iterator(Tickets(LIMIT)))
#: serialized: 200 distinct, duplicates False
```

`Tickets` hands out each number once: read, pause, write back.
`Tickets.__next__()` is `gil_race.py` wearing a different hat.
Read the counter, do something that releases the GIL, write the counter back.
Eight threads read the same number and all eight receive it,
so a ticket meant to go to one worker goes to several.
The count of distinct values is still 200, which makes this dangerous:
nothing is missing, so nothing looks wrong until you notice the same work ran eight times.

`threading.serialize_iterator()` wraps an iterator so that `__next__()` runs under a lock,
one thread at a time.
The wrapped object is an iterator like any other,
and the workers need no changes.
If the iterator also defines `send()`, `throw()`, or `close()`,
the wrapper serializes those too.

A generator ([Iterators](23_Patterns--Iterators.md#generators) covers them)
fails differently, and louder:

```python
# shared_generator.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Final

LIMIT: Final[int] = 200

def numbers(limit: int) -> Iterator[int]:
    for n in range(limit):
        time.sleep(0.000_001)  # Let other threads run
        yield n

guarded = threading.synchronized_iterator(numbers)

def outcome(source: Iterator[int]) -> str:
    def take(_: int) -> int | None:
        try:
            return len(list(source))
        except ValueError:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(take, range(8)))
    taken = sum(r for r in results if r is not None)
    failed = sum(r is None for r in results)
    return f"{taken} taken, any thread failed: {failed > 0}"

print("plain:      ", outcome(numbers(LIMIT)))
#: plain:       200 taken, any thread failed: True
print("synchronized:", outcome(guarded(LIMIT)))
#: synchronized: 200 taken, any thread failed: False
```

A generator refuses to resume while already running,
so the second thread through gets `ValueError: generator already executing`.
A typical run loses seven of the eight workers to it while the first drains the whole sequence.
That is better than silent duplication,
but only in the way a crash is better than corruption.

`threading.synchronized_iterator()` takes the generator *function*,
not a generator, and returns a function that serializes every generator it creates.
It also works as a decorator on the `def`,
the right form when the serializing belongs to the function rather than to each caller.
Keep the pairing straight:
`serialize_iterator()` wraps one iterator you already have,
and `synchronized_iterator()` wraps the callable that makes them.

Serializing solves the case where the workers divide one stream.
When each worker needs the whole stream,
`itertools.tee()` looks like the answer and is not:
tee'd iterators share an internal buffer with no locking.
`threading.concurrent_tee()` is the answer:

```python
# concurrent_tee.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Final

READERS: Final[int] = 4

def numbers(limit: int) -> Iterator[int]:
    for n in range(limit):
        time.sleep(0.000_001)  # Let other threads run
        yield n

streams = threading.concurrent_tee(numbers(100), READERS)
with ThreadPoolExecutor(max_workers=READERS) as pool:
    print(list(pool.map(sum, streams)))
#: [4950, 4950, 4950, 4950]
```

Each of the four threads sees all one hundred values,
and the underlying generator advances once per value, not four times.
One caution carries over:
a `concurrent_tee()` iterator is safe to hand to one thread,
and that is why the listing makes four of them.
Sharing a single one across several threads needs `serialize_iterator()` on top.

These three arrived in 3.15.
Before that, you wrote the lock wrapper yourself,
and that wrapper is easy to get subtly wrong.
The tempting fix is a lock inside the loop:

```
for item in shared:       # next() runs here, unguarded
    with lock:
        process(item)
```

That guards the work and leaves the race untouched,
because the `for` statement calls `next()`, outside the block the lock protects.
Serializing an iterator means putting the lock inside `__next__()`,
and that is where these three wrappers put it.

## One Task, Many Backends

Every section so far has kept threads, processes, subinterpreters,
and `asyncio` apart.
Blending them without knowing which parts are compatible produces races and pickling errors.
Two real points of convergence exist in the standard library, though,
not because the models are secretly the same,
but because two small pieces of them genuinely are.

The first is `concurrent.futures.Executor`.
`ThreadPoolExecutor`, `ProcessPoolExecutor`,
and `InterpreterPoolExecutor` share more than a resemblance:
all three subclass `Executor` and present its `submit()` and `map()` interface.
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

def run_on(
    executor: Executor, orders: list[int]
) -> list[int]:
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
It prints `[10, 20, 30, 40, 50]` and `True`: three unrelated kinds of worker,
one set of answers.

`asyncio` does not fit here.
An `Executor` blocks a worker and hands back a result.
A coroutine does the opposite.
It is a suspended function that runs only when the event loop resumes it.

The two models give their result-that-arrives-later the same name,
and the shared name invites one specific mistake.
`pool.submit()` hands back a `concurrent.futures.Future`,
and you wait on it by calling `result()`, which blocks the calling thread.
Awaiting it raises `TypeError: 'Future' object can't be awaited`.
`asyncio` has its own `Future`, and `Task` is a subclass of it,
so both are awaitable and neither blocks anything.
`loop.run_in_executor()` is the bridge between the two:
it submits to the executor and returns an `asyncio.Future` that resolves when the executor's own future does.
That is why `process_price()` below calls it instead of `pool.submit()`.

The second point of convergence is `await`.
A native coroutine, a `to_thread()` call,
and a `run_in_executor()` call all produce an *awaitable*.
[`TaskGroup`](#structured-concurrency-with-taskgroup) holds any of them:

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
    return await loop.run_in_executor(pool,
                                      cpu_price, order)

async def main(pool: ProcessPoolExecutor) -> None:
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(io_price(1)),
            tg.create_task(
                asyncio.to_thread(blocking_price, 2)),
            tg.create_task(process_price(pool, 3)),
        ]
    print([t.result() for t in tasks])

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        asyncio.run(main(pool))
```

Three different backends run inside one `TaskGroup`.
`io_price()` suspends and resumes on the event loop the way `fetch()` did in this chapter's first listing.
`to_thread()` hands `blocking_price()` to a worker thread the way it did in `to_thread.py`.
`process_price()` hands `cpu_price()` to a worker process the way `parallel_cpu.py` did,
wrapped in one `async def` so `TaskGroup` can hold it alongside the others.
All three start together, and the block does not exit until all three finish,
so the printed `[10, 20, 30]` holds one result from each backend.
The event loop is doing the job it has done all chapter:
it schedules awaitables, whatever runs underneath, a coroutine, a thread,
or a process.

`main()` receives an already-built `pool` instead of creating one itself.
`ProcessPoolExecutor.__enter__` can spawn worker processes,
and `__exit__` joins them: both are ordinary blocking calls.
Running either on the thread driving the event loop would freeze every task on it,
the same failure `blocking_the_loop.py` demonstrated with `time.sleep()`.
Building the pool before `asyncio.run()` and tearing it down after keeps that cost off the loop entirely.

Each of these two interfaces unifies one small piece of the backends,
not the whole.
`Executor` unifies backends that share a blocking, submit-and-wait shape.
`await` unifies backends that share only a result that arrives later.
Everything else about the backends stays different.

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

Threads remain for one job:
reaching code that doesn't cooperate with an event loop.
Most database drivers, most GUI toolkits,
and plenty of C extensions block the calling thread and expose no `async` entry point.

If Python had always supported coroutines,
you could expect every library to conform.
But rewriting all existing libraries to use `asyncio` instead of threads is not realistic.
`asyncio.to_thread()`, from [Escaping to a Thread](#escaping-to-a-thread),
is the standard library solution.
Thus, even a program written as `asyncio` from top to bottom keeps a thread pool underneath,
because the libraries it calls still block.

Free threading leaves I/O-bound work as it was and solves a narrower problem:
without the GIL, a thread can genuinely parallelize CPU-bound work from inside one process while sharing memory directly,
paying no pickling cost.
This is something neither a GIL-bound thread nor a process pool offers.

Under the standard build, then, a thread no longer structures your concurrency.
`asyncio` does that.
A thread's remaining job is to absorb a blocking call,
so the wait cannot freeze the event loop.

The GIL [does not prevent races](#the-gil-does-not-prevent-races).
It doesn't protect a read-modify-write spanning a function call.
With free threading,
two threads can execute at the same instant on separate cores.
Race conditions become even easier to hit.

`asyncio` switches only at an `await`,
and that makes it easier to [reason about interleaving](#a-single-thread-still-races).
A thread costs an OS stack and an OS scheduling entity that free threading does not remove,
while an `asyncio` task is cheap enough to run in the thousands.
[`TaskGroup`](#structured-concurrency-with-taskgroup)'s structured,
cancellable batches have no thread equivalent.
Python still offers no safe way to cancel a running thread.
Free threading changes a thread's job.
It does not change `asyncio`'s.

### Measuring the Difference

You can support the claim that a thread costs far more memory than a task.
`threading.stack_size()` reports and sets the stack CPython reserves for each new thread.
A common default across platforms is on the order of one mebibyte.^[A mebibyte (MiB) is 2<sup>20</sup> while a megabyte (MB) is 10<sup>6</sup>.]
`tracemalloc` measures a task's actual heap footprint directly,
since a task consists of ordinary Python objects.
You can calculate the ratio between the two:

```python
# task_vs_thread_memory.py
import asyncio
import threading
import tracemalloc
from typing import Final
from benchmark import report

TASKS: Final[int] = 5_000
# 1 MiB, a common thread stack reservation:
STACK_SIZE: Final[int] = 1024 * 1024

async def parked() -> None:
    await asyncio.sleep(999)  # Suspended, never resumes

async def bytes_per_task() -> float:
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    tasks = [asyncio.create_task(parked())
             for _ in range(TASKS)]
    # Let every task reach its own await
    await asyncio.sleep(0)
    after = tracemalloc.take_snapshot()
    grown = sum(
        stat.size_diff
        for stat in after.compare_to(before, "lineno")
        if stat.size_diff > 0
    )
    for t in tasks:
        t.cancel()
    # Without "return_exceptions=True", the first
    # CancelledError raises and exits the function:
    await asyncio.gather(*tasks, return_exceptions=True)
    tracemalloc.stop()
    return grown / TASKS

default_stack = threading.stack_size()
threading.stack_size(STACK_SIZE)  # A real, settable cost
configured_stack = threading.stack_size()
# Restore the previous setting
threading.stack_size(default_stack)

task_cost = asyncio.run(bytes_per_task())
tasks_per_stack = configured_stack / task_cost
report(bytes_per_task=task_cost,
       tasks_per_stack=tasks_per_stack)
print(f"one thread's stack reservation: "
      f"{configured_stack:,} bytes")
#: one thread's stack reservation: 1,048,576 bytes
print(f"bytes per task under 4 KiB: {task_cost < 4096}")
#: bytes per task under 4 KiB: True
print(f"holds over 200 tasks: {tasks_per_stack > 200}")
#: holds over 200 tasks: True
```

`bytes_per_task()` creates 5,000 tasks that immediately suspend on `asyncio.sleep(999)`,
so they stay alive doing nothing.
The two `tracemalloc` snapshots capture the heap they add.
The listing reads `threading.stack_size()`, sets it, reads it again,
then restores it, so the measurement leaves the rest of the program untouched.
That stack figure is stipulated, not measured:
`STACK_SIZE` is a constant this listing sets and reads back,
standing for a common one-mebibyte default,
not a number the OS reports for a thread it actually ran.
A single thread's reserved stack,
paid before it runs one line of its target function,
could instead hold hundreds of suspended tasks.
The stack figure is address space set aside whether the thread touches every byte or not.
The task figure is heap measured by `tracemalloc`.
The comparison favors tasks over threads by hundreds to one,
against that stipulated reservation rather than a measured thread footprint.
The exact figures move from machine to machine,
so the listing asserts the two bounds that hold anywhere and prints what it measured under `--numbers`
(see [Numbers on Your Machine](18_Techniques--Performance.md#numbers-on-your-machine)).

A similar difference shows up in time:

```python
# thread_vs_task_speed.py
import asyncio
import threading
import time
from typing import Final
from benchmark import report

COUNT: Final[int] = 3000

def noop() -> None:
    pass

async def async_noop() -> None:
    pass

def spawn_threads() -> float:
    start = time.perf_counter()
    threads = [threading.Thread(target=noop)
               for _ in range(COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

async def spawn_async_tasks() -> float:
    start = time.perf_counter()
    await asyncio.gather(
        *(async_noop() for _ in range(COUNT)))
    return time.perf_counter() - start

t_threads = spawn_threads()
t_tasks = asyncio.run(spawn_async_tasks())
report(threads=t_threads, tasks=t_tasks)
print(f"tasks at least 5x faster to spawn: "
      f"{t_tasks * 5 < t_threads}")
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

`async_race.py` in [A Single Thread Still Races](#a-single-thread-still-races)
lost updates to shared mutable state, and an `asyncio.Lock` restored them,
with no thread involved either time.
Shared mutable state, not threads, is the source of deadlock and livelock,
and `asyncio` shares it just as readily as threads do.
Removing the OS thread scheduler moves where these failures arise and leaves the failures themselves in place.
With threads, that point is anywhere the OS decides to preempt you.
`asyncio` narrows this to the `await` points you wrote yourself.

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
A threaded equivalent of this worker needs its own lock around `active += 1` and `peak = max(peak, active)`,
since a preemptive switch could fall between them.
Here, the first `await` comes after both updates,
so the task keeps control through them and needs no lock.

A semaphore initialized to one behaves like a lock, with one difference.
A `Lock` refuses a release it never granted,
raising `RuntimeError: Lock is not acquired`.
An over-released `Semaphore` quietly raises its own limit instead,
so a stray `release()` turns a semaphore of one into a semaphore of two.
Raising the count deliberately turns it into a throttle on a limited resource,
such as a fixed number of database connections.

### Deadlock

In a *deadlock*, two or more tasks each hold a resource the other needs,
so neither can proceed.
Four conditions must all hold at once:

1. Exclusive access to each resource
2. Holding one resource while waiting for another
3. No way to force a task to give up what it holds
4. A cycle of tasks each waiting on the next

If you break any one of the four, deadlock becomes impossible.
None of these conditions mentions threads or an OS scheduler,
so `asyncio` can also produce deadlock.
This example has two tasks and two `asyncio.Lock` objects.
The two tasks acquire the locks in opposite order:

```python
# async_deadlock.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(
    first: asyncio.Lock, second: asyncio.Lock
) -> None:
    async with first:
        # Let the other task grab its lock
        await asyncio.sleep(0.01)
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

The first task takes `lock_a` then tries to acquire `lock_b`.
The second takes `lock_b` then tries to acquire `lock_a`.
The `sleep(0.01)` gives each task time to grab its first lock before either asks for its second.
Tasks, unlike threads, run one at a time,
so no OS scheduler can interleave the two tasks' first lines in an unlucky order.

Once both hold their first lock,
each task's `async with second:` suspends on a lock the other holds and never releases.
A real deadlock has no `timeout` and never resolves.
Both tasks wait forever, the event loop included,
since nothing remains that can wake them.
Here, `asyncio.wait_for()` bounds the wait: when its deadline passes,
it cancels the `gather()` and raises a `TimeoutError`,
so the example reports the deadlock instead of hanging.

The fix is the same one that works for threads:
have every task acquire shared locks in the same global order.
If both tasks acquire `lock_a` first,
whichever gets there first finishes and releases that lock before the other waits.

### Livelock

A *livelock* blocks nothing.
Tasks keep running and keep changing state, but none of them makes progress,
the way two people in a hallway each step aside for the other, forever.
No lock takes part, no task waits to acquire anything, so no timeout can fix it:

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
Two equally polite tasks make no progress,
even though the event loop keeps both tasks busy the whole time.

A real livelock looks busy on a monitor,
with CPU time spent and state visibly changing.
A deadlock looks idle, with tasks parked and waiting.
In both cases, nothing finishes.
The usual fix is to break the symmetry,
for example letting only the task with the lower ID give.

## Guidelines

- **Concurrency is a performance tool.**
  Explore [Performance](18_Techniques--Performance.md)
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
  Splitting past the number of cores sometimes yields a little more.
  Then the per-task cost of pickling and reassembling catches up,
  and the gains flatten (Amdahl's Law).
- **For CPU-bound work, try a subinterpreter first, a process pool second,
  and a free-threaded build only once you know every extension you use supports it.**
- **Match the queue to the concurrency model.**
  `queue.Queue` blocks a thread,
  `multiprocessing.Queue` pickles across processes,
  `asyncio.Queue` suspends a task and needs no locking.
- **An iterator handed to several threads is not thread-safe,
  and it fails quietly.**
  Wrap one you have with `threading.serialize_iterator()`,
  wrap the generator function that makes them with `threading.synchronized_iterator()`,
  and use `threading.concurrent_tee()` when every worker needs the whole stream.
  A lock inside the loop body guards the wrong thing:
  the `for` statement calls `next()` outside it.
- **Pass request-scoped values in a `ContextVar`, not a global.**
  Each task starts from a copy of the context that created it,
  and `asyncio.to_thread()` carries that copy into the worker thread.
- **A `TaskGroup` failure arrives as an `ExceptionGroup`.**
  Catch it with `except*`.
  A plain `except ValueError:` around the `async with` block misses it,
  even when only one task failed.
- **Cancellation is a `BaseException`, not an `Exception`.**
  `except Exception:` inside a task lets it through, and that is what you want.
  Catching `asyncio.CancelledError` and not re-raising it strands the `TaskGroup` that asked the task to stop.
- **A shared lock only prevents deadlock if every user agrees on the order.**
  Acquire shared locks in the same sequence everywhere.
  When two units keep yielding to each other instead,
  break the symmetry so only one of them gives way.

## Concurrency is Not Easy

People still argue about what the term means.
Rob Pike, creator of the Go language, famously muddied the waters by declaring,
"concurrency is not parallelism"
(I'm hoping he meant to say "concurrency is not **only** parallelism").[^concurrency-def]
As this chapter has shown,
concurrency means "operating or occurring at the same time."
This works for both asynchrony and parallelism.

Also, notice how much this chapter has talked about the OS.
Concurrency tears through the comfortable abstraction that normal programming provides.
Sometimes you even need to go beyond the OS-level abstraction,
all the way to hardware, to understand a particular bug.

Someone who declares "concurrency is easy!" has dipped their toes in it and never encountered a tricky problem.
This chapter makes concurrency look (somewhat)
easy because it has only touched the surface of shared mutable state problems.

Even when you understand the problems produced by shared mutable state,
you might not have a choice.
Some problems preclude immutability.
For example, a solution might require packing as much data as possible into RAM.
In those cases you almost inevitably share mutable state.
These are the kinds of decisions you must make when you move from the examples in this chapter into serious real-world concurrency.

People continue to work toward better ways of concurrent programming.[^libraries]
Only in the last decade or so have programmers widely adopted advances such as async/await and structured concurrency.
The vocabulary this chapter built,
from processes and threads to tasks and coroutines,
is a small corner of the territory.
Here are a few of the topics beyond it:

- **Barriers:** Make a group of threads or tasks wait until every one of them arrives,
  then release them together.
  Unlike `gather()` or `TaskGroup`,
  a barrier is a rendezvous point where the running code arrives and blocks,
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
  Elixir is newer and built on Erlang's BEAM virtual machine.
- **Communicating Sequential Processes
  (CSP):** Independent processes that communicate only over explicit,
  shared channels, rather than an actor's private mailbox.
  This is the approach behind Go's goroutines and channels.
- **Software transactional memory
  (STM):** Runs a block of code as an atomic transaction against shared memory,
  retrying automatically if another thread interferes.[^stm-status]
- **Memory models and data races:** Define which writes by one thread another thread sees for certain,
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
    replace `lock = asyncio.Lock()` with `semaphore = asyncio.Semaphore(1)`,
    renaming its uses to match.
    Confirm `counter` still reaches `400`,
    and explain why a semaphore initialized to `1` stands in for a lock here.
    Then add one stray `semaphore.release()` before the `gather()` call and explain the result.
6.  Remove the `if __name__ == "__main__"` guard from `parallel_cpu.py`,
    so its body runs unconditionally, and run it.
    Read the error, whose useful part is the nested `RuntimeError` rather than the `BrokenProcessPool` at the bottom,
    then explain it with the import mechanics described in [Parallelism](#parallelism):
    what did each worker process do when it imported the module?
7.  In `gil_race.py`, remove the `time.sleep(0.000_001)` call and run the script several times.
    Explain, using [The GIL Does Not Prevent Races](#the-gil-does-not-prevent-races),
    why the race becomes far less likely to show up without that sleep,
    but is not thereby fixed.
8.  In `priority_queue.py`,
    add a third thread submitting `[(1, "zzz"), (3, "aaa")]` and confirm the drain order still respects priority first,
    then the description as a tiebreaker.
9.  In `utils/fetch_demo.py`,
    change `("e", 0.2)` in `PAIRS` to `("e", 0.005)` so `e` finishes before `c` and `d` fail,
    then run `task_group.py`.
    Predict which of the six report `cancelled` and which report a result,
    then run it and explain what a `TaskGroup` can and cannot undo.
    Change `PAIRS` back afterward,
    since `gather_with_exceptions.py` uses it too.
10. In `gather_with_exceptions.py`,
    delete `return_exceptions=True` and wrap the `await` in `try`/`except ValueError`.
    Predict how many `fetched` lines still print,
    and explain what became of the tasks on which the `gather()` call never reported.
11. In `context_var.py`,
    move the `request_id.set()` call out of `handle()` and into `main()` above the `TaskGroup`,
    setting it to `"main"`.
    Predict what each task prints,
    then explain the result with "every task starts with a copy of the context that created it."
12. In `subinterpreters.py`,
    replace `InterpreterPoolExecutor` with `ThreadPoolExecutor`.
    The assertion still passes and the printed boolean flips.
    Explain both, using [The GIL and Free Threading](#the-gil-and-free-threading).
13. In `shared_iterator.py`,
    drop `threading.serialize_iterator()` and give each worker a function that loops over the shared iterator,
    holding a `threading.Lock` around the loop *body*,
    the tempting fix in [Sharing an Iterator Between Threads](#sharing-an-iterator-between-threads).
    Predict whether `duplicates` becomes `False` before running it,
    and explain which call the lock does and does not cover.
14. In `async_deadlock.py`,
    change the second `worker()` call to `worker(lock_a, lock_b)` so both tasks acquire in the same order,
    and add a line that prints when both finish.
    Predict what the program prints before running it, then explain,
    in terms of who waits for whom,
    why one shared acquisition order removes the cycle.
15. In `mixed_await.py`,
    replace the body of `process_price()` with `return await pool.submit(cpu_price, order)`.
    Run `ty` on the changed file, then run it, and read the two errors.
    Explain, using [One Task, Many Backends](#one-task-many-backends),
    why you cannot await `pool.submit()`'s return value,
    what `loop.run_in_executor()` returns instead,
    and why the runtime `TypeError` arrives wrapped in an `ExceptionGroup`.

[^concurrency-def]: Pike's definition from that talk clarifies what he meant.
    Concurrency is the composition of independently executing computations.
    Parallelism is running those computations at the same time.
    You can have concurrency without parallelism.
    The `asyncio` examples in this chapter show it.
    Coroutines interleave on a single thread, and no two of them ever execute at the same instant.

    The distinction goes back further than
    [Pike's 2012 talk](https://go.dev/blog/waza-talk) at Heroku's Waza conference.
    Edsger Dijkstra's 1965 paper,
    "[Solution of a Problem in Concurrent Programming Control](https://repositories.lib.utexas.edu/items/84831631-07fe-484b-a45c-3cff9f6b1f43),"
    started the formal study of concurrent programs.
    Leslie Lamport's 2015 Turing Lecture,
    "[The Computer Science of Concurrency: The Early Years](https://lamport.azurewebsites.net/pubs/turing.pdf),"
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
    are where STM succeeded as a practical, widely used tool.

[^libraries]: Libraries worth exploring:

    - [BOCPY](https://microsoft.github.io/bocpy/):
      Behavior-Oriented Concurrency.
    - [Trio](https://trio.readthedocs.io/): Origin of structured concurrency.
    - [AnyIO](https://pypi.org/project/anyio/): Bridge between Trio and asyncio.
    - [uvloop](https://github.com/MagicStack/uvloop):
      Fast drop-in replacement for the standard event loop.
      See also [rsloop](https://github.com/RustedBytes/rsloop).
    - [MPIRE](https://github.com/sybrenjansen/mpire):
      Makes `multiprocessing` easier and faster.
    - [RAY](https://www.ray.io/): Distribute tasks across multiple CPUs, GPUs,
      and clusters.
    - [Dask](https://www.dask.org/): Parallelizes tools like NumPy, Pandas,
      and Scikit-Learn.
