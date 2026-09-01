# Concurrency: Solutions

## 1. A fourth coroutine in the `gather()`

```python
# exercise_1.py
import asyncio

async def fetch(item, delay):
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main():
    results = await asyncio.gather(
        fetch("a", 0.03), fetch("b", 0.02),
        fetch("c", 0.01), fetch("d", 0.005))
    print(results)

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: d: resumed
#: c: resumed
#: b: resumed
#: a: resumed
#: ['A', 'B', 'C', 'D']
```

The trace splits into two halves that run in opposite directions.
`gather()` starts its tasks in argument order, so `d` starts last. Each
task then suspends at its own `await`, and the event loop resumes them
in the order their timers fire, so the shortest delay wakes first and
`d` resumes before the other three. The returned list follows the
argument order, not the finishing order: `gather()` fills each
position from the coroutine passed in that position, so `'D'` is last
in the list even though `d` finished first.

## 2. Awaiting in a comprehension

```python
# exercise_2.py
import asyncio
import time

async def fetch(item, delay):
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main():
    coroutines = [fetch("a", 0.03), fetch("b", 0.02),
                  fetch("c", 0.01)]
    start = time.perf_counter()
    results = [await c for c in coroutines]
    elapsed = time.perf_counter() - start
    print(results)
    print(
        f"took the sum, not the longest: {elapsed > 0.055}")

asyncio.run(main())
#: a: started
#: a: resumed
#: b: started
#: b: resumed
#: c: started
#: c: resumed
#: ['A', 'B', 'C']
#: took the sum, not the longest: True
```

Each `started` line has its own `resumed` line directly beneath it,
the signature of no overlap. The comprehension awaits one coroutine at
a time, and `await` does not return until that coroutine finishes, so
`b` cannot start until `a` finishes. Nothing schedules the later
coroutines while the current one waits.

The timing follows from the trace. `gather()` finishes in about the
longest delay, 0.03 seconds, because all three waits overlap. This
version takes their sum, about 0.06 seconds, because the waits never
overlap. The list comprehension is not the problem. Calling `fetch()`
builds a coroutine object and starts nothing. Only `gather()` or a
`TaskGroup` schedules every coroutine as a task before waiting on any.

## 3. A task that mixes waiting and computing

```python
# exercise_3.py
import asyncio
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self):
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type, exc, tb):
        self.active -= 1

async def mixed_price(order, meter):
    with meter:
        # Waiting, off the processor
        await asyncio.sleep(0.05)
        total = 0
        # Working, on the processor
        for _ in range(1_000_000):
            total += 1
    return order * 10

async def run(price_task, orders):
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main():
    prices, peak = await run(mixed_price, [1, 2, 3, 4, 5])
    print(f"mixed peak={peak}, prices={prices}")

asyncio.run(main())
#: mixed peak=5, prices=[10, 20, 30, 40, 50]
```

The peak is `5`, matching the I/O-bound case rather than the CPU-bound
one. `mixed_price()` reaches its `await asyncio.sleep(0.05)` before the
CPU-heavy loop, so all five coroutines suspend at that `await` and let
their siblings start before any of them begins computing. All five are
in flight, waiting, at once.

If you move the loop above the `await`, the peak drops back to `1`. Each
coroutine then runs its full million iterations before yielding, so
the event loop never gets a chance to overlap them. Overlap depends on
where the `await` sits relative to the computation, not on whether the
function contains one somewhere.

## 4. Blocking inside a coroutine

```python
# exercise_4.py
import asyncio
import time
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self):
        self.active += 1
        self.peak = max(self.peak, self.active)

    def __exit__(self, exc_type, exc, tb):
        self.active -= 1

async def io_price(order, meter):
    with meter:
        time.sleep(0.05)  # Blocking, and never awaited
    return order * 10

async def run(price_task, orders):
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main():
    prices, peak = await run(io_price, [1, 2, 3, 4, 5])
    print(f"blocking peak={peak}, prices={prices}")

asyncio.run(main())
#: blocking peak=1, prices=[10, 20, 30, 40, 50]
```

The peak falls from `5` to `1`, the same figure the CPU-bound version
produced. `time.sleep()` is where `blocking_the_loop.py`'s lesson lands:
it stops the thread instead of suspending the task, and the event loop
runs on that thread. A coroutine that never awaits never gives the loop
a chance to start another task, so each task runs start to finish
before the next begins.

Waiting is not what creates overlap. Suspending is. These five tasks
spend almost all their time waiting and still never overlap, while
`cpu_price()` never overlaps for the opposite reason: it has no
`await` to reach. The total run time makes the cost visible: five
blocking sleeps of 0.05 seconds take about a quarter second, while
five awaited ones take about 0.05.

## 5. A semaphore of one, and a stray release

```python
# exercise_5.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count):
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main():
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
```

A semaphore holds a count of how many holders it admits at once, and
`async with` decrements that count on the way in and restores it on the
way out. With the count initialized to `1`, the first task through
exhausts it, so every other task suspends at `async with` until that
task leaves. Only one read-modify-write runs at a time, exactly as with
`asyncio.Lock`, and all 400 increments land.

The equivalence is only as good as the count. If you add one stray
release before the tasks start, the semaphore admits two holders
instead of one:

```python
# exercise_5_stray_release.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count):
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main():
    semaphore.release()  # Nothing was acquired
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 200
```

Exactly half the increments survive. Two tasks now sit inside the
critical section together, both reading `counter` before either writes,
so each pair of increments collapses into one. The semaphore reports
no error, because raising the limit is exactly what `release()` does.

That silence is the difference between the two objects. `asyncio.Lock`
refuses a release it never granted, raising `RuntimeError: Lock is not
acquired.` A semaphore has no such notion of ownership, so the same
mistake silently widens the gate and reintroduces the race the lock was
there to prevent.

## 6. Removing the `__main__` guard

With the guard gone, `parallel_cpu.py` builds its pool at import time:

```python
from concurrent.futures import ProcessPoolExecutor

def cpu_price(order):
    total = 0
    for _ in range(1_000_000):
        total += 1
    return order * 10

orders = [1, 2, 3, 4, 5]
with ProcessPoolExecutor() as pool:  # No longer guarded
    prices = list(pool.map(cpu_price, orders))
print(prices)
```

Running it prints a stack of tracebacks, one per worker, each ending in
the same `RuntimeError`:

    An attempt has been made to start a new process before the
    current process has finished its bootstrapping phase.

    This probably means that you are not using fork to start your
    child processes and you have forgotten to use the proper idiom
    in the main module

Each worker did what the chapter describes. To find `cpu_price()`, a
fresh interpreter imported this module, and importing it ran every
top-level statement, including the `with ProcessPoolExecutor()` line
that creates workers. Each worker therefore tried to build a pool of
its own, whose workers would import the module again.

The error is a guard rail rather than the real failure. Python detects
that a child process is spawning children during its own bootstrap and
refuses to start them, instead of letting the recursion consume the
machine. The `if __name__ == "__main__"` line prevents that recursion.
A spawned worker imports the module under its real name,
`parallel_cpu`, rather than `"__main__"`, so the child skips the
pool-building code and only the process you launched runs it.

The whole failure is a start-method problem. On a platform using
`fork`, the child inherits the parent's memory instead of importing the
module, and the missing guard does no damage. But no platform forks by
default anymore. Windows and macOS default to `spawn`, and since 3.14
Linux defaults to `forkserver`, which also imports the module. Every
platform's default therefore requires the guard.

## 7. Removing the `sleep` from `gil_race.py`

```python
import threading

counter = 0

def increment(count):
    global counter
    for _ in range(count):
        value = counter   # Read
        # Write back, with nothing in between
        counter = value + 1

threads = [threading.Thread(target=increment, args=(50,))
           for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter, counter == 400)
```

Running this repeatedly on CPython 3.11 or later prints `400 True`
every time. Since 3.11, the interpreter only considers switching
threads at a function call or at the jump that closes a loop
iteration. With the `time.sleep()` call removed, the read and the
write run back to back, with no function call between them, so the
interpreter finds no scheduling point at which to hand the GIL to
another thread mid-sequence. That reliability is luck rather than a
guarantee: the race stays invisible only because this interpreter
happens to place its switch points elsewhere. Put any function call
back between the read and the write, a blocking I/O call, a `print()`,
even an innocuous-looking helper, and the same gap reopens, because
`counter += 1`'s underlying bytecode sequence never became atomic. The
fix is still a lock, not the absence of an explicit sleep.

## 8. A third thread submitting jobs

```python
# exercise_8.py
import threading
from queue import PriorityQueue

tasks: PriorityQueue = PriorityQueue()

def submit(jobs):
    for job in jobs:
        tasks.put(job)

threads = [
    threading.Thread(
        target=submit,
        args=([(3, "backup"), (1, "page oncall")],)),
    threading.Thread(
        target=submit,
        args=([(2, "rotate logs"), (1, "alert")],)),
    threading.Thread(
        target=submit,
        args=([(1, "zzz"), (3, "aaa")],)),
]
for t in threads:
    t.start()
for t in threads:
    t.join()

while not tasks.empty():
    print(tasks.get())
#: (1, 'alert')
#: (1, 'page oncall')
#: (1, 'zzz')
#: (2, 'rotate logs')
#: (3, 'aaa')
#: (3, 'backup')
```

The six jobs still arrive in an unpredictable interleaving from three
racing threads, but `PriorityQueue` sorts strictly by the tuple's
value. The drain order is therefore always priority first, `1` before
`2` before `3`, then alphabetically by the description within a
priority (the tuple's second field): `"alert"` before `"page oncall"`
before `"zzz"`, and `"aaa"` before `"backup"`. Which thread happened to
submit a job first never affects the final order.

## 9. A task that finishes before the failures land

```python
# exercise_9.py
import asyncio
from typing import Final

PAIRS: Final[list[tuple[str, float]]] = [
    ("a", 0.01),
    ("b", 0.02),
    ("c", 0.03),
    ("d", 0.03),
    ("e", 0.005),  # Was 0.2, so e now finishes first
    ("f", 0.3),
]

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    if item in ("c", "d"):
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

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
#: e: fetched
#: a: fetched
#: b: fetched
#: caught: fetch('c') failed
#: caught: fetch('d') failed
#: a: A
#: b: B
#: c: raised ValueError("fetch('c') failed")
#: d: raised ValueError("fetch('d') failed")
#: e: E
#: f: cancelled
```

Only `f` reports `cancelled` now. With `e` at `0.005` its timer fires
long before `c` and `d` fail at `0.03`, so `e` prints `fetched`,
returns `"E"`, and has finished by the time the group starts
cancelling. `f` still sleeps for `0.3`, so cancellation reaches it
during that sleep and its task ends cancelled.

That is the line between what a `TaskGroup` can and cannot undo. A
`TaskGroup` cancels what is still running, which is why the original
`PAIRS` had both `e` and `f` cancelled. It cannot reach into a task
that already returned, and it cannot unprint `e: fetched` or undo
whatever a real `fetch()` wrote to a database on its way out.
Structured concurrency guarantees that no task outlives the block, not
that no task had an effect before the failure.

The distinction matters when the tasks do more than sleep. A group of
six writes where two fail leaves the successful writes in place, so
recovery is your problem, not the `TaskGroup`'s. That is what
[Context Managers](../Chapters/15_Techniques--Context_Managers.md) and the Effect chapters
address from different directions: pairing an action with the cleanup
that undoes it, so "already finished" still means "still reversible."

## 10. `gather()` without `return_exceptions`

```python
# exercise_10.py
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

async def main() -> None:
    try:
        results = await asyncio.gather(
            *(fetch(item, delay) for item, delay in PAIRS),
        )
    except ValueError as e:
        print(f"gather raised {e!r}")
        return
    print(results)

asyncio.run(main())
#: a: started
#: b: started
#: c: started
#: d: started
#: e: started
#: f: started
#: a: fetched
#: b: fetched
#: gather raised ValueError("fetch('c') failed")
```

Two `fetched` lines print, `a` and `b`, the two whose timers fire
before `c` fails at `0.03`. `e` and `f` never print one, and
`print(results)` never runs, because the `await` raises instead of
returning a value.

Without `return_exceptions=True`, the first child exception propagates
out of the `await` immediately, and `gather()` reports that one
exception rather than a list of six outcomes. `d` fails in the same
tick, but the `gather()` future has already resolved by then, so
`gather()` retrieves `d`'s failure and discards it instead of raising
it. The call loses the four results it was collecting, including `a`
and `b`, which had already succeeded.

The other tasks are the interesting part. `gather()` does not cancel
them when the exception propagates, unlike a `TaskGroup`, so `e` and
`f` are still sleeping when `main()` returns. `asyncio.run()` then
cancels whatever tasks remain as it shuts the loop down, which is why
`e` and `f` print nothing further. Had `main()` gone on to other work,
they would have run to completion in the background with nobody
waiting on their results.

That combination, results discarded and siblings left running, is why
`return_exceptions=True` and `TaskGroup` exist.
`return_exceptions=True` keeps every outcome, so partial success stays
visible. A `TaskGroup` guarantees that nothing outlives the block.
Bare `gather()` gives you neither.

## 11. Setting the `ContextVar` in the parent

```python
# exercise_11.py
import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id",
                                         default="-")
current = "-"  # The same idea as a plain global

async def handle(name: str) -> None:
    global current
    current = name
    await asyncio.sleep(0)  # Stand-in for a database call
    print(f"context {request_id.get()}, global {current}")

async def main() -> None:
    # Set once, before any task exists
    request_id.set("main")
    async with asyncio.TaskGroup() as group:
        for name in ("req-1", "req-2", "req-3"):
            group.create_task(handle(name))
    print(f"after: context {request_id.get()}, "
          f"global {current}")

asyncio.run(main())
#: context main, global req-3
#: context main, global req-3
#: context main, global req-3
#: after: context main, global req-3
```

All three tasks print `context main`. Every task starts with a copy of
the context that created it, and that context already carried
`request_id = "main"`, so each copy inherits the same value. No task
writes to the variable afterward, so all three copies stay identical
and the original version's per-request identity disappears.

The `after:` line changes too. In the chapter's version it printed
`context -`, the default, because each `set()` happened inside a task's
own copy and none of them could reach `main()`'s context. Here the
`set()` is in `main()`, so it lands in `main()`'s own context and is
still there once the group finishes. Copying runs one way: a child sees
what the parent had at creation, and the parent sees nothing a child
did.

`current` behaves as before, reaching `req-3` everywhere, which is the
contrast the example exists to draw. A `global` is one cell shared by
every task, so the last writer wins and the other two tasks read a
value meant for someone else. A `ContextVar` is per-task storage that
happens to be reachable by one name.

## 12. Threads in place of subinterpreters

```python
# exercise_12.py
import os
import sys
import timeit
from concurrent.futures import ThreadPoolExecutor

def cpu_price(order: int) -> int:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10

def sequential(orders: list[int]) -> list[int]:
    return [cpu_price(o) for o in orders]

orders = [1, 2, 3, 4, 5]
t_seq = timeit.timeit(lambda: sequential(orders), number=5)

with ThreadPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)
    t_thr = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

cores = os.cpu_count() or 1
# The chapter's scaled target
target = min(1.5, cores * 0.7)
if "--numbers" in sys.argv:  # Exact times on your machine
    print(f"sequential {t_seq:.6f}, threaded {t_thr:.6f}")
print(f"threads run in parallel: {t_seq > t_thr * target}")
#: threads run in parallel: False
```

The assertion passes because correctness never depended on the
executor. `cpu_price()` reads its argument and returns a number,
touching nothing shared, so five of them produce the same five results
whether they run one after another, in five threads, or in five
subinterpreters. Swapping the executor changes when the work runs, not
what it computes.

The boolean flips because threads in one interpreter share one GIL.
`cpu_price()` is a counting loop with no I/O and no `sleep`, so it
holds the GIL except at the interpreter's periodic switch points. Five
such threads take turns on one processor and finish in about the time
five sequential calls take, so `t_seq` and `t_thr` come out close
together and `t_seq > t_thr * 1.5` is `False`.

`InterpreterPoolExecutor` wins the same benchmark because each
subinterpreter has its own GIL. The work spreads across processors
instead of time-slicing on one.
[The GIL and Free Threading](../Chapters/19_Techniques--Concurrency.md#the-gil-and-free-threading)
gives the reason: the GIL is per interpreter, not per process, so more
interpreters mean more locks and real parallelism. A free-threaded
build reaches the same end by removing the GIL instead of multiplying
it, letting ordinary threads do what this listing's threads cannot.

## 13. A lock around the loop body, not around `next()`

```python
# ch19_body_lock.py
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Final

LIMIT: Final[int] = 200
lock = threading.Lock()

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

def drain(source: Iterator[int]) -> list[int]:
    out: list[int] = []
    for item in source:  # next() runs here, unguarded
        with lock:
            out.append(item)  # Only the body is protected
    return out

def report(source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(drain, source)
                   for _ in range(8)]
        taken = [*f.result() for f in futures]
    print(f"{len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

report(Tickets(LIMIT))
#: 200 distinct, duplicates True
```

`duplicates` stays `True`. The lock changes nothing about the race,
because the race is not in the loop body.

`for item in source:` is the `for` statement calling
`source.__next__()`, and that call happens before control reaches the
indented block. The `with lock:` inside the body therefore starts
*after* `next()` has already returned a number, and ends before the
next `next()` begins. Two threads can be inside `__next__()` at the
same moment, read the same `next_number`, and come away with the same
ticket, exactly as they did without the lock.

The lock does cover `out.append(item)`, which never needed covering:
`out` is a local list, one per worker, so no other thread can touch
it.

Serializing an iterator means putting the lock where the mutation is,
inside `__next__()`, exactly where `threading.serialize_iterator()`
puts it. The lesson generalizes past iterators: a lock protects the
statements it encloses, and a `for` loop's own call to `next()` is not
one of them.

## 14. Both tasks acquiring in the same order

```python
# ch19_ordered_locks.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(
    first: asyncio.Lock, second: asyncio.Lock
) -> None:
    async with first:
        await asyncio.sleep(0.01)  # Let the other task run
        async with second:
            pass

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker(lock_a, lock_b),
                worker(lock_a, lock_b),  # The same order
            ),
            timeout=0.5,
        )
        print("both workers finished")
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: both workers finished
```

The program prints `both workers finished`, and finishes in about
twenty milliseconds rather than waiting out the half-second timeout.

Follow who waits for whom. The first task takes `lock_a`, sleeps, then
takes `lock_b`, which nobody holds. Meanwhile the second task reaches
`async with lock_a` and suspends, because the first task has it. That
is a wait, but a wait on a task that is not itself waiting on anything
the second task holds. The first task finishes, releases both locks,
and the second task walks the same path through an empty field.

The deadlock version made the waiting circular: task one held `lock_a`
and wanted `lock_b`, task two held `lock_b` and wanted `lock_a`, so
each task's progress depended on the other task's progress. A deadlock
is exactly that cycle. Ordering the acquisitions globally makes such a
cycle impossible. A task can only ever wait on a lock that comes later
in the order than every lock it already holds, and "later" never loops
back to "earlier."

## 15. Awaiting `pool.submit()` directly

The changed method drops the bridge:

```python
async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> int:
    return await pool.submit(cpu_price, order)
```

`ty` rejects the line before anything runs:

    error[invalid-await]: `Future[int]` is not awaitable

Running it anyway raises before any price comes back:

    + Exception Group Traceback (most recent call last):
      ...
    | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
    +-+---------------- 1 ----------------
      |     return await pool.submit(cpu_price, order)
      | TypeError: 'Future' object can't be awaited

`pool.submit()` hands back a `concurrent.futures.Future`, the
executor's own handle on a result a worker is still computing. Its
interface blocks: you wait by calling `result()`, which stops the
calling thread until the worker finishes. Nothing about that future
cooperates with an event loop, and it defines no `__await__`, so
`await` refuses it, first statically and then at runtime.

`loop.run_in_executor()` is the bridge the original listing used. It
submits the call to the executor the same way `submit()` does, but
returns an `asyncio.Future` bound to the running loop, an awaitable
that resolves when the executor's own future completes. The task
suspends on it like any other `await`, and the loop keeps running the
other two tasks in the meantime.

The wrapper around the `TypeError` is the `TaskGroup` keeping its
contract. `process_price()` failed as a task inside the group, so the
group cancelled its two siblings, waited for them to end, and
re-raised the failure wrapped in an `ExceptionGroup`, the same
packaging `task_group.py` caught with `except*`. `main()` has no
`except*`, so the group propagates out of `asyncio.run()` and prints
as the grouped traceback above.
