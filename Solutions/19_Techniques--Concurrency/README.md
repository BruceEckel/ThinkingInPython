# Concurrency: Solutions

## 1. A fourth coroutine in the `gather()`

> In `async_mechanics.py`, add a fourth call, `fetch("d", 0.005)`,
> to the `gather()` line.
> Confirm that "d" starts last but resumes first,
> and that the printed list still grows to four entries in the order given,
> not the order they finish.

<details>
<summary>Where to look</summary>

[`async def`, `await`, and the Event Loop](../../Chapters/19_Techniques--Concurrency.md#asyncio-mechanics)
shows each coroutine suspending at its `await` while the loop starts the next one.
Add the fourth `fetch()` to the arguments of `gather()` and compare two orders in the output.
The order in which timers fire decides the `resumed` lines,
while the argument positions decide the returned list.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `async_mechanics.py` prints `d: started` as the fourth `started` line and `d: resumed` as the first `resumed` line,
and the final list reads `['A', 'B', 'C', 'D']`, in argument order.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
import asyncio

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
    pending = fetch("a", 0.03)
    print(type(pending).__name__)
    results = await asyncio.gather(
        pending, fetch("b", 0.02),
        fetch("c", 0.01), fetch("d", 0.005))
    print(results)

asyncio.run(main())
#: coroutine
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

The trace splits into two halves that list the tasks in opposite orders.
`gather()` starts its tasks in argument order, so `d` starts last.
Each task then suspends at its own `await`.
The event loop resumes the tasks in the order their timers fire,
so the shortest delay wakes first and `d` resumes before the other three.

The returned list follows the argument order, not the finishing order.
`gather()` fills each position from the coroutine passed in that position,
so `'D'` is last in the list although `d` finished first.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Awaiting in a comprehension

> In `async_mechanics.py`,
> replace the `gather()` call with `[await c for c in coroutines]`,
> where `coroutines` is a list of the same three `fetch()` calls.
> Predict the started/resumed trace and the total run time before running it,
> and explain why this version takes the sum of the three delays.

<details>
<summary>Where to look</summary>

[`async def`, `await`, and the Event Loop](../../Chapters/19_Techniques--Concurrency.md#asyncio-mechanics)
explains that a coroutine object describes pending work,
which starts when something awaits it.
In `[await c for c in coroutines]`,
ask what the comprehension does with the first `await` before it moves to the second `c`.
Compare that with `gather()`,
which wraps every coroutine in a task before it waits on any of them.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
import asyncio
import time

async def fetch(item: str, delay: float) -> str:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `async_mechanics.py` prints each `started` line directly above its own `resumed` line,
`a` then `b` then `c`, and ends with `['A', 'B', 'C']`.
A timing around the comprehension shows about 0.06 seconds,
where the `gather()` version takes about 0.03.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
import asyncio
import time

async def fetch(item: str, delay: float) -> str:
    print(f"{item}: started")
    await asyncio.sleep(delay)
    print(f"{item}: resumed")
    return item.upper()

async def main() -> None:
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

**Await each coroutine in turn.**
The comprehension awaits one coroutine at a time.
`await` waits for that coroutine to finish, so `b` starts once `a` finishes.
The later coroutines stay unscheduled while the current one waits.

`gather()` finishes in about the longest delay, 0.03 seconds,
because all three waits overlap.
This version takes their sum, about 0.06 seconds,
because the waits run one after another.

The slowdown comes from when each coroutine starts,
not from the list comprehension.
Calling `fetch()` builds a coroutine object,
and the coroutine runs when something awaits it.
`gather()` and a `TaskGroup` schedule every coroutine as a task before waiting on any,
so all three sleeps start together.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A task that mixes waiting and computing

> In `peak_concurrency.py`, add a third task function, `mixed_price()`,
> that awaits `asyncio.sleep(0.05)` and then also runs the 1,000,000-iteration loop from `cpu_price()`.
> Run it through `run()` and predict its `meter.peak` before checking:
> is it closer to the I/O peak or the CPU peak?

<details>
<summary>Where to look</summary>

[Overlapping the Waits](../../Chapters/19_Techniques--Concurrency.md#overlapping-the-waits)
measures overlap with `meter.peak`,
and [I/O-Bound vs CPU-Bound](../../Chapters/19_Techniques--Concurrency.md#io-bound-vs-cpu-bound)
describes the two kinds of work `mixed_price()` combines.
A task counts as active while it sits inside the `with meter:` block,
including while it waits at an `await` there.
Look at where the `await` falls relative to that block,
and whether the other four tasks get a chance to start at that `await`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import asyncio
from collections.abc import Awaitable, Callable
from meter import Meter, Peak
from pricing import Price

async def mixed_price(order: int, meter: Meter) -> Price:
    ...

type PriceTask = Callable[[int, Meter], Awaitable[Price]]

async def run(
    price_task: PriceTask, orders: list[int]
) -> tuple[list[Price], Peak]:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

running `mixed_price()` through `run()` in your edited `peak_concurrency.py` reports a `meter.peak` of `5`,
with prices `[10, 20, 30, 40, 50]`.
You can say why moving the loop above the `await`,
still inside the `with meter:` block, leaves the peak at `5`.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
import asyncio
from collections.abc import Awaitable, Callable
from meter import Meter, Peak
from pricing import Price

async def mixed_price(order: int, meter: Meter) -> Price:
    with meter:
        # Waiting, off the processor
        await asyncio.sleep(0.05)
        total = 0
        # Working, on the processor
        for _ in range(1_000_000):
            total += 1
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[Price]]

async def run(
    price_task: PriceTask, orders: list[int]
) -> tuple[list[Price], Peak]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main() -> None:
    prices, peak = await run(mixed_price, [1, 2, 3, 4, 5])
    print(f"mixed peak={peak}, prices={prices}")

asyncio.run(main())
#: mixed peak=5, prices=[10, 20, 30, 40, 50]
```

**Suspend before computing.**
The peak is `5`, matching the I/O-bound case rather than the CPU-bound one.
`mixed_price()` reaches its `await asyncio.sleep(0.05)` before the CPU-heavy loop,
so all five coroutines suspend at that `await` and let their siblings start before any of them begins computing.
All five are in flight, waiting, at once.

**Count a suspended task as active.**
The peak stays `5` wherever the loop sits,
because the `await` is inside the `with meter:` block.
A task suspended there counts as active.
If you remove the `await`, as `cpu_price()` does, the peak falls to `1`.
Overlap depends on whether an `await` sits inside the measured span,
not on where it sits relative to the computation.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Blocking inside a coroutine

> In `peak_concurrency.py`,
> change `io_price()`'s `await asyncio.sleep(0.05)` to `time.sleep(0.05)` and predict how its `meter.peak` changes before running it.
> Explain the result using `blocking_the_loop.py`.

<details>
<summary>Where to look</summary>

[`time.sleep()` Stops the Loop](../../Chapters/19_Techniques--Concurrency.md#time-sleep-stops-the-loop)
shows a blocking call freezing every other task.
The event loop runs on one thread,
and `time.sleep()` blocks that thread instead of suspending the task.
Think about whether any task can start while another one sleeps,
and what that does to the count of simultaneous tasks.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import asyncio
import time
from collections.abc import Awaitable, Callable
from meter import Meter, Peak
from pricing import Price

async def io_price(order: int, meter: Meter) -> Price:
    ...

type PriceTask = Callable[[int, Meter], Awaitable[Price]]

async def run(
    price_task: PriceTask, orders: list[int]
) -> tuple[list[Price], Peak]:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `peak_concurrency.py` reports `peak=1` for `io_price()`,
the figure `cpu_price()` reports, with the prices unchanged,
and the five calls take about a quarter second instead of about 0.05.
You can say which thread `time.sleep()` holds and why the other tasks wait for it.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
import asyncio
import time
from collections.abc import Awaitable, Callable
from meter import Meter, Peak
from pricing import Price

async def io_price(order: int, meter: Meter) -> Price:
    with meter:
        time.sleep(0.05)  # Blocking, and never awaited
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[Price]]

async def run(
    price_task: PriceTask, orders: list[int]
) -> tuple[list[Price], Peak]:
    meter = Meter()
    coroutines = [price_task(o, meter) for o in orders]
    prices = await asyncio.gather(*coroutines)
    return prices, meter.peak

async def main() -> None:
    prices, peak = await run(io_price, [1, 2, 3, 4, 5])
    print(f"blocking peak={peak}, prices={prices}")

asyncio.run(main())
#: blocking peak=1, prices=[10, 20, 30, 40, 50]
```

**Hold the thread while waiting.**
The peak falls from `5` to `1`, the same figure the CPU-bound version produces.
As in `blocking_the_loop.py`,
`time.sleep()` stops the event loop's thread instead of suspending the task.
A coroutine with no `await` returns control to the loop when it finishes,
so each task runs start to finish before the next begins.

Waiting does not create overlap.
Suspending does.
These five tasks spend almost all their time waiting and still run one at a time.
`cpu_price()` spends its time computing and runs one at a time for the same reason:
it has no `await` to reach.

The total run time shows the blocking tasks running in turn.
Five blocking sleeps of 0.05 seconds take about a quarter second,
while five awaited ones take about 0.05.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A semaphore of one, and a stray release

> In `async_locks.py`,
> replace `lock = asyncio.Lock()` with `semaphore = asyncio.Semaphore(1)`,
> renaming its uses to match.
> Confirm `counter` still reaches `400`,
> and explain why a semaphore initialized to `1` stands in for a lock here.
> Then add one stray `semaphore.release()` before the `gather()` call and explain the result.

<details>
<summary>Where to look</summary>

[Locks](../../Chapters/19_Techniques--Concurrency.md#locks)
and [Semaphores](../../Chapters/19_Techniques--Concurrency.md#semaphores)
show `async with` guarding a critical section,
the read-modify-write that one task at a time may enter.
A `Semaphore` holds a count of admitted holders,
and `async with` decrements it on entry and restores it on exit.
For the stray `release()`,
ask how many tasks the count now admits and whether `release()` checks that an `acquire()` came first.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import asyncio

async def increment(count: int) -> None:
    ...

async def main() -> None:
    ...
```

```python
# The shape of exercise_5_stray_release.py
import asyncio

async def increment(count: int) -> None:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your semaphore version of `async_locks.py` prints `counter: 400 of 400`,
and with the stray `semaphore.release()` before `gather()` it prints `counter: 200 of 400` and runs to the end with no error.
You can say why `asyncio.Lock` raises a `RuntimeError` for the same stray release.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main() -> None:
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(f"counter: {counter} of {8 * 50}")

asyncio.run(main())
#: counter: 400 of 400
```

**Admit one holder at a time.**
A semaphore holds a count of how many holders it admits at once.
`async with` decrements that count on entry and restores it on exit.
With the count initialized to `1`, the first task through exhausts it,
so every other task suspends at `async with` until that task leaves.
The read-modify-writes run one at a time, as with `asyncio.Lock`,
and all 400 increments survive.

The equivalence holds while the count stays at one.
If you add one stray release before the tasks start,
the semaphore admits two holders instead of one:

```python
# exercise_5_stray_release.py
import asyncio

counter = 0
semaphore = asyncio.Semaphore(1)

async def increment(count: int) -> None:
    global counter
    for _ in range(count):
        async with semaphore:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main() -> None:
    semaphore.release()  # Nothing was acquired
    await asyncio.gather(*(increment(50) for _ in range(8)))
    print(f"counter: {counter} of {8 * 50}")

asyncio.run(main())
#: counter: 200 of 400
```

**Admit a second holder.**
Two tasks now sit inside the critical section together,
both reading `counter` before either writes,
so each pair of increments adds one to `counter` instead of two.

The semaphore accepts the stray call,
because `release()` adds one to the count whether or not an `acquire()` came first.
That missing error is the difference between a semaphore and a lock.
`asyncio.Lock` checks for a matching acquire,
so a release without one raises `RuntimeError: Lock is not acquired.` A semaphore's count can climb past its starting value,
so the same mistake lifts the count to two and silently admits a second holder.
That second holder reintroduces the race the lock is there to prevent.
`asyncio.BoundedSemaphore(1)` checks the count against its initial value,
so the stray `release()` raises `ValueError: BoundedSemaphore released too many times`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Removing the `__main__` guard

> Remove the `if __name__ == "__main__"` guard from `parallel_cpu.py`,
> so its body runs unconditionally, and run it.
> Read the error, whose useful part is the `RuntimeError` traceback each failing child process printed above the `BrokenProcessPool` at the bottom,
> then explain it with the import mechanics described in [What a Process Pool Requires](../../Chapters/19_Techniques--Concurrency.md#what-a-process-pool-requires):
> what did each worker process do when it imported the module?

<details>
<summary>Where to look</summary>

[What a Process Pool Requires](../../Chapters/19_Techniques--Concurrency.md#what-a-process-pool-requires)
describes how a worker process finds the function it must run.
The worker imports your module,
and importing executes every top-level statement.
Read the `RuntimeError` traceback for what a worker tries to do during that import,
and for the name `__mp_main__`, which `__name__` holds in a worker.

<details>
<summary>Done when</summary>

running `parallel_cpu.py` without its guard prints at least one `RuntimeError` traceback beginning `An attempt has been made to start a new process`,
above a `BrokenProcessPool` at the bottom.
You can say which top-level statement each worker runs during its import,
and what `__name__` holds in a worker.

<details>
<summary>Solution</summary>

With the guard gone, `parallel_cpu.py` builds its pool at import time:

```python
from concurrent.futures import ProcessPoolExecutor
from pricing import cpu_price

orders = [1, 2, 3, 4, 5]
with ProcessPoolExecutor() as pool:  # No longer guarded
    prices = list(pool.map(cpu_price, orders))
print(prices)
```

Running it prints one or more tracebacks, one per failing worker,
each ending in the same `RuntimeError`,
above the `BrokenProcessPool` at the bottom:

    An attempt has been made to start a new process before the
    current process has finished its bootstrapping phase.

    This probably means that you are not using fork to start your
    child processes and you have forgotten to use the proper idiom
    in the main module

**Build the pool at import time.**
As the chapter describes,
each worker starts as a fresh interpreter that imports this module,
the program's main module, before it runs any work.
Importing the module runs every top-level statement,
including the `with ProcessPoolExecutor()` line that creates workers.
Each worker therefore tries to build a pool of its own,
whose workers import the module again.

The recursion is the failure.
The `RuntimeError` comes from a safety check against it.
Python detects that a child process is spawning children during its own bootstrap and raises the error instead of starting them.
The recursion therefore ends with the first generation of workers.

The `if __name__ == "__main__"` line prevents that recursion.
A worker runs the module under the name `"__mp_main__"` rather than `"__main__"`,
so the test is `False` in every worker and `True` in the process you launched.
That process alone builds the pool.

The whole failure is a start-method problem.
On a platform using `fork`,
the child inherits the parent's memory instead of importing the module,
so the pool-building code runs once, in the parent.
But every platform's default start method now imports the module.
Windows and macOS default to `spawn`,
and since 3.14 Linux defaults to `forkserver`.
Every platform's default therefore requires the guard.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Removing the `sleep` from `gil_race.py`

> In `gil_race.py`, remove the `time.sleep(0.000_001)` call and run the script several times.
> Explain, using [The GIL Does Not Prevent Races](../../Chapters/19_Techniques--Concurrency.md#the-gil-does-not-prevent-races),
> why the race becomes far less likely to show up without that sleep,
> but is not thereby fixed.

<details>
<summary>Where to look</summary>

[The GIL Does Not Prevent Races](../../Chapters/19_Techniques--Concurrency.md#the-gil-does-not-prevent-races)
explains where the interpreter may switch threads.
Without the call, check whether any switch point remains between the read and the write of the shared value.
Then ask whether removing the call makes the read-modify-write sequence atomic,
or leaves a read and a write that run back to back because of where the interpreter places its switch points.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from concurrent.futures import ThreadPoolExecutor

def increment(count: int) -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `gil_race.py` prints `lost updates: False` on each of several runs on the standard build,
and you can name the kind of statement that,
placed between the read and the write,
makes it print `lost updates: True` again.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from concurrent.futures import ThreadPoolExecutor

counter = 0

def increment(count: int) -> None:
    global counter
    for _ in range(count):
        value = counter  # Read
        # Write back, with nothing in between
        counter = value + 1

with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(increment, [50] * 8))
print(f"lost updates: {counter < 8 * 50}")
#: lost updates: False
```

**Run the read and write back to back.**
Running this repeatedly on the standard build prints `lost updates: False` every time.
Since 3.10, the interpreter considers switching threads only at a function call or at the jump that closes a loop iteration.
With the `time.sleep()` call removed, the read and the write run back to back.
The next switch point is the jump after the write,
so every handoff of the GIL falls between one increment and the next.

That reliability is luck rather than a guarantee.
This run keeps every update because the interpreter places its switch points elsewhere.
A function call between the read and the write restores a switch point inside the sequence,
whether it is a blocking I/O call, a `print()`, or an innocuous-looking helper.
The counter then loses updates again,
because the read-modify-write sequence is still not atomic.

A free-threaded interpreter has no GIL,
so its threads run at the same moment and can interleave any read and write.
The fix is a lock around the read and the write.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. A third thread submitting jobs

> In `priority_queue.py`,
> add a third thread submitting `[(1, "zzz"), (3, "aaa")]` and confirm the drain order still respects priority first,
> then the description as a tiebreaker.

<details>
<summary>Where to look</summary>

[Coordinating Threads with Queues](../../Chapters/19_Techniques--Concurrency.md#coordinating-threads-with-queues)
shows producers feeding a `PriorityQueue` that a consumer drains.
Add a third `pool.submit(enqueue, ...)` call and keep the chapter's `max_workers=3`.
Three workers cover three producers, and the consumer reuses one of them,
since the listing submits the consumer after the producers finish.
The queue orders items by comparing tuples,
so the drain order is the same for every interleaving of the producers.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, ShutDown

type Job = tuple[int, str]  # (priority, description)

def enqueue(jobs: list[Job]) -> None:
    ...

def consume() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `priority_queue.py` prints six tuples in the same order on every run,
opening with `(1, 'alert')`, `(1, 'page oncall')`,
`(1, 'zzz')` and closing with `(3, 'aaa')`, `(3, 'backup')`.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
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
        pool.submit(enqueue,  # The third producer
                    [(1, "zzz"), (3, "aaa")]),
    ]
    for p in producers:
        p.result()  # Surface any producer failure
    consumer = pool.submit(consume)
    tasks.shutdown()
    consumer.result()
#: (1, 'alert')
#: (1, 'page oncall')
#: (1, 'zzz')
#: (2, 'rotate logs')
#: (3, 'aaa')
#: (3, 'backup')
```

**Add a third producer.**
The one change is the third `pool.submit(enqueue, ...)`.
The chapter's `max_workers=3` stays.
Three workers cover the three producers, and `consume()` reuses one of them,
because the listing submits `consume()` after every producer finishes.
A run with `max_workers=4` prints the same six lines in the same order.

**Drain in priority order.**
The pool may run the three producers on one, two, or three threads,
depending on whether each producer finishes before the pool picks up the next.
The order in which the six jobs enter the queue can therefore vary,
but `PriorityQueue` orders its items by comparing the tuples.
The drain order is always priority first, `1` before `2` before `3`,
then alphabetically by the description within a priority
(the tuple's second field).
The final order is the same whichever thread submits a job first,
because `consume()` starts after all three producers finish.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. A task that finishes before the failures arrive

> In `utils/fetch_demo.py`,
> change `Fetch("e", 0.2)` in `FETCHES` to `Fetch("e", 0.005)` so `e` finishes before `c` and `d` fail,
> then run `task_group.py`.
> Predict which of the six report `cancelled` and which report a result,
> then run it and explain what a `TaskGroup` can and cannot undo.
> Change `FETCHES` back afterward,
> since `gather_with_exceptions.py` uses it too.

<details>
<summary>Where to look</summary>

[Structured Concurrency with `TaskGroup`](../../Chapters/19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup)
shows a failing child causing the group to cancel its siblings.
Compare each task's delay with the moment `c` and `d` fail to decide which tasks are still running when cancellation starts.
The group cancels the tasks still running,
so consider what becomes of a task that has returned.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
import asyncio
from typing import Final
from record import record

@record
class Fetch:
    item: str
    delay: float
    fails: bool = False

FETCHES: Final[list[Fetch]] = [
    Fetch("a", 0.01),
    Fetch("b", 0.02),
    Fetch("c", 0.03, fails=True),
    Fetch("d", 0.03, fails=True),
    Fetch("e", 0.005),  # Was 0.2, so e now finishes first
    Fetch("f", 0.3),
]

async def sleep_until(when: float) -> None:
    ...

async def fetch(job: Fetch, t0: float) -> str:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

`task_group.py` with the changed `FETCHES` prints `e: fetched` before `a: fetched`,
reports `e: E` among its final lines,
and shows `f: cancelled` as the one cancelled task.
You can name an effect of `e` that the group's cancellation leaves in place,
and `FETCHES` holds `Fetch("e", 0.2)` again afterward.

<details>
<summary>Solution</summary>

```python
# exercise_9.py
import asyncio
from typing import Final
from record import record

@record
class Fetch:
    item: str
    delay: float
    fails: bool = False

FETCHES: Final[list[Fetch]] = [
    Fetch("a", 0.01),
    Fetch("b", 0.02),
    Fetch("c", 0.03, fails=True),
    Fetch("d", 0.03, fails=True),
    Fetch("e", 0.005),  # Was 0.2, so e now finishes first
    Fetch("f", 0.3),
]

async def sleep_until(when: float) -> None:
    loop = asyncio.get_running_loop()
    woken: asyncio.Future[None] = loop.create_future()
    timer = loop.call_at(when, woken.set_result, None)
    try:
        await woken
    finally:
        timer.cancel()

async def fetch(job: Fetch, t0: float) -> str:
    await sleep_until(t0 + job.delay)
    if job.fails:
        raise ValueError(f"fetch({job.item!r}) failed")
    print(f"{job.item}: fetched")
    return job.item.upper()

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                job.item: tg.create_task(fetch(job, t0))
                for job in FETCHES
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

**Let one task finish first.**
With `e` at `0.005` its timer fires long before `c` and `d` fail at `0.03`,
so `e` has finished by the time the group starts cancelling.
`f` still sleeps for `0.3`,
so the group cancels it during that sleep and its task ends cancelled.

**Cancel what is still running.**
The original `FETCHES` has both `e` and `f` cancelled because both are still sleeping when `c` and `d` fail.
The group cannot cancel a task that has returned,
and it cannot unprint `e: fetched` or undo whatever a real `fetch()` wrote to a database before it returned.
Structured concurrency guarantees that every task has ended when the block exits.
Every effect a task had before the failure stays in place.

When the tasks write to a database instead of sleeping,
a group of six writes where two fail leaves the successful writes in place.
Undoing those writes is the job of your own code, not of the `TaskGroup`.
[Context Managers](../../Chapters/15_Techniques--Context_Managers.md)
pairs an action with its cleanup.
That cleanup releases resources, but it cannot reverse a write that succeeded.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. `gather()` without `return_exceptions`

> In `gather_with_exceptions.py`,
> delete `return_exceptions=True` and wrap the `await` in `try`/`except ValueError`.
> Predict how many `fetched` lines still print,
> and explain what became of the tasks whose outcomes the `gather()` call left unreported.

<details>
<summary>Where to look</summary>

[Failures as Values with `gather()`](../../Chapters/19_Techniques--Concurrency.md#failures-as-values-with-gather)
shows `return_exceptions=True` collecting every outcome.
Without it, the first child exception propagates out of the `await`,
so count which timers fire before that moment.
For the remaining tasks, compare with a `TaskGroup` and ask who cancels them,
and what `asyncio.run()` does at shutdown.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
import asyncio
from fetch_demo import FETCHES, fetch

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `gather_with_exceptions.py` prints two `fetched` lines, `a` and `b`,
then your handler's line naming `fetch('c') failed`,
and nothing more from `e` or `f`.
You can say what becomes of `e` and `f` after the `ValueError` reaches your handler.

<details>
<summary>Solution</summary>

```python
# exercise_10.py
import asyncio
from fetch_demo import FETCHES, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        results = await asyncio.gather(*(
            fetch(job, t0) for job in FETCHES))
    except ValueError as e:
        print(f"gather raised {e!r}")
        return
    print(results)

asyncio.run(main())
#: a: fetched
#: b: fetched
#: gather raised ValueError("fetch('c') failed")
```

Two `fetched` lines print, `a` and `b`,
the two whose timers fire before `c` fails at `0.03`.
Control passes from the `await` to the `except` block,
because the `await` raises `ValueError` instead of returning a value.

If you leave out the `return` in the `except` block,
the handler prints its line and execution falls through to `print(results)`.
`results` is unbound at that point,
so the line raises an `UnboundLocalError` right after the `gather raised` line.
The type checker passes that version, so the mistake shows up only at run time.

**Propagate the first failure.**
With `return_exceptions` at its default, `False`,
the first child exception propagates out of the `await` immediately.
`gather()` reports that one exception rather than a list of six outcomes,
and loses the four results it was collecting, including `a` and `b`,
which had succeeded.
`d` fails in the same tick, but the `gather()` future has resolved by then.
`gather()` therefore retrieves `d`'s failure and discards it instead of raising it.

**Leave the other tasks running.**
Unlike a `TaskGroup`,
`gather()` leaves the other tasks running when the exception propagates,
so `e` and `f` are still sleeping when `main()` returns.
`asyncio.run()` then cancels the tasks that remain as it shuts the loop down,
which is why the trace ends at the `gather raised` line.
If `main()` goes on to other work,
they run to completion in the background with no code awaiting their results.

That combination, results discarded and siblings left running,
is why `return_exceptions=True` and `TaskGroup` exist.
`return_exceptions=True` keeps every outcome, so partial success stays visible.
A `TaskGroup` guarantees that every task has ended when the block exits.
Bare `gather()` gives you neither.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 11. Setting the `ContextVar` in the parent

> In `context_var.py`,
> move the `request_id.set()` call out of `handle()` and into `main()` above the `TaskGroup`,
> setting it to `"main"`.
> Predict what each task prints,
> then explain the result with "every task starts with a copy of the context current when `create_task()` runs."

<details>
<summary>Where to look</summary>

[Context That Follows the Call Chain](../../Chapters/19_Techniques--Concurrency.md#context-that-follows-the-call-chain)
shows each task running in its own copy of the context.
Move the `set()` call so it runs before the `TaskGroup` creates any task,
and ask what value each copy holds at creation.
Also check what the `after:` line reads,
since a child's `set()` and a parent's `set()` write to different contexts.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_11.py
import asyncio
from contextvars import ContextVar

async def handle(name: str) -> None:
    ...

async def main() -> None:
    # Set once, before any task exists
    ...
```

<details>
<summary>Done when</summary>

your edited `context_var.py` prints `context main` on all four lines,
the `after:` line included, with `global req-3` on each.
You can say why the `after:` line now reads `main` where the chapter's version reads `-`.

<details>
<summary>Solution</summary>

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

**Set the value before any task exists.**
All three tasks print `context main`,
where each task in the original version printed the name of its own request.
Every task starts with a copy of the context current when `create_task()` runs,
and inside `main()` that context already carries `request_id = "main"`,
so each copy inherits the same value.
The tasks leave the variable as it was, so all three copies stay identical.

**Read the value after the group.**
The `after:` line changes too.
In the chapter's version it prints `context -`, the default,
because each `set()` writes to a task's own copy and leaves `main()`'s context as it was.
Here the `set()` is in `main()`,
so it writes to `main()`'s own context and the value is still there once the group finishes.
Copying runs one way.
A child reads the values the parent had at creation,
and the values a child sets stay in the child.

`current` behaves as before, reading `req-3` everywhere,
which is the contrast the example exists to draw.
A `global` is one cell shared by every task,
so the last writer wins and the other two tasks read a value another task set.
A `ContextVar` is per-task storage reachable by one name.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 12. Threads in place of subinterpreters

> In `subinterpreters.py`,
> replace `InterpreterPoolExecutor` with `ThreadPoolExecutor`.
> The assertion still passes and the printed boolean flips.
> Explain both, using [The GIL and Free Threading](../../Chapters/19_Techniques--Concurrency.md#the-gil-and-free-threading).

<details>
<summary>Where to look</summary>

[The GIL and Free Threading](../../Chapters/19_Techniques--Concurrency.md#the-gil-and-free-threading)
and [Subinterpreters](../../Chapters/19_Techniques--Concurrency.md#subinterpreters)
describe where the GIL lives.
The assertion compares results,
which are the same whichever executor ran the work.
The boolean compares times,
so ask how many GILs a pool of threads shares and how many a pool of subinterpreters has.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_12.py
import os
import timeit
from concurrent.futures import ThreadPoolExecutor
from benchmark import report
from pricing import Price, cpu_price

def sequential(orders: list[int]) -> list[Price]:
    ...
```

<details>
<summary>Done when</summary>

your edited `subinterpreters.py` runs with the assertion passing and prints `False` for the parallel check,
where the chapter's version prints `True`.
You can say which of the two comparisons depends on how many GILs the workers share,
and why the other comparison stays the same.

<details>
<summary>Solution</summary>

```python
# exercise_12.py
import os
import timeit
from concurrent.futures import ThreadPoolExecutor
from benchmark import report
from pricing import Price, cpu_price

def sequential(orders: list[int]) -> list[Price]:
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
target = min(1.5, cores * 0.7)  # Lower on one or two cores
report(sequential=t_seq, threads=t_thr, cores=cores)
print(f"threads run in parallel: {t_seq > t_thr * target}")
#: threads run in parallel: False
```

**Check that the results agree.**
The assertion passes because every executor computes the same results.
`cpu_price()` reads its argument and returns a number,
and each call works on its own local variables.
Five calls therefore produce the same five results whether they run one after another,
in five threads, or in five subinterpreters.
Swapping the executor changes when the work runs, not what it computes.

**Compare the timings.**
The boolean flips because threads in one interpreter share one GIL.
`cpu_price()` is a counting loop with no I/O and no `sleep`,
so it holds the GIL except at the interpreter's periodic switch points.
Five such threads take turns on one processor and finish in about the time five sequential calls take.
`t_seq` and `t_thr` therefore come out close together,
and `t_seq > t_thr * target` is `False`.

`InterpreterPoolExecutor` wins the same benchmark because each [subinterpreter](../../Chapters/19_Techniques--Concurrency.md#subinterpreters)
has its own GIL.
The work spreads across processors instead of time-slicing on one.
A free-threaded build reaches the same end by removing the GIL instead of multiplying it,
so its ordinary threads run on several processors at once.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 13. A lock around the loop body, not around `next()`

> In `shared_iterator.py`,
> drop `threading.serialize_iterator()` and give each worker a function that loops over the shared iterator,
> holding a `threading.Lock` around the loop body,
> the tempting fix in [Sharing an Iterator Between Threads](../../Chapters/19_Techniques--Concurrency.md#sharing-an-iterator-between-threads).
> Predict whether `duplicates` becomes `False` before running it,
> and explain which call the lock does and does not cover.

<details>
<summary>Where to look</summary>

[Sharing an Iterator Between Threads](../../Chapters/19_Techniques--Concurrency.md#sharing-an-iterator-between-threads)
shows the race inside a shared iterator and `threading.serialize_iterator()` fixing it.
A `for` statement calls `__next__()` before it enters the indented body.
Place a `with lock:` in the body and ask whether any thread still enters `__next__()` while another is inside it.

<details>
<summary>The shape</summary>

```python
# The shape of ch19_body_lock.py
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
        ...

    def __next__(self) -> int:
        ...

def drain(source: Iterator[int]) -> list[int]:
    ...

def distribute(source: Iterator[int]) -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `shared_iterator.py`, with the lock around the loop body,
still reports `200 distinct, duplicates True`.
You can name the call the `for` header makes outside the lock,
and say what the lock covers instead.

<details>
<summary>Solution</summary>

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

def distribute(source: Iterator[int]) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(drain, source)
                   for _ in range(8)]
        taken = [*f.result() for f in futures]
    print(f"{len(set(taken))} distinct, "
          f"duplicates {len(taken) > len(set(taken))}")

distribute(Tickets(LIMIT))
#: 200 distinct, duplicates True
```

The lock leaves the race in place, because the race is in `__next__()`,
outside the loop body.

**Take each item unguarded.**
`for item in source:` is the `for` statement calling `source.__next__()`,
and that call runs before control reaches the indented block.
The `with lock:` inside the body therefore starts after `next()` has returned a number,
and ends before the next `next()` begins.
Two threads can be inside `__next__()` at the same moment,
read the same `next_number`, and return the same ticket,
as they do without the lock.

**See what the lock does cover.**
It covers `out.append(item)`, which is safe outside the lock.
`out` is a local list, one per worker,
so the worker's own thread alone touches it.

Serializing an iterator means putting the lock where the mutation is,
inside `__next__()`, where `threading.serialize_iterator()` puts it.
A lock protects the statements it encloses.
A `for` loop calls `next()` in its header, outside them.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 14. Both tasks acquiring in the same order

> In `async_deadlock.py`,
> change the second `worker()` call to `worker("task 2", lock_a, lock_b)` so both tasks acquire in the same order,
> and add a line that prints when both finish.
> Predict what the program prints before running it, then explain,
> in terms of who waits for whom,
> why one shared acquisition order removes the cycle.

<details>
<summary>Where to look</summary>

[Deadlock](../../Chapters/19_Techniques--Concurrency.md#deadlock)
shows two tasks each holding one lock and waiting for the other.
Change the second `worker()` call,
then trace which task takes `lock_a` first and what the other task does at its `async with`.
Draw an arrow from each waiting task to the task it waits on and check whether those arrows can form a loop.

<details>
<summary>The shape</summary>

```python
# The shape of ch19_ordered_locks.py
import asyncio

async def worker(
    name: str, first: asyncio.Lock, second: asyncio.Lock
) -> None:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Done when</summary>

your edited `async_deadlock.py` prints `task 1: holds both` before `task 2: holds its first lock`,
ends with your line saying both workers finished,
and returns in about 20 milliseconds, well inside the 0.5-second timeout.
You can draw who waits for whom and show the arrows form no loop.

<details>
<summary>Solution</summary>

```python
# ch19_ordered_locks.py
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def worker(
    name: str, first: asyncio.Lock, second: asyncio.Lock
) -> None:
    async with first:
        print(f"{name}: holds its first lock")
        await asyncio.sleep(0.01)  # Let the other task run
        async with second:
            print(f"{name}: holds both")

async def main() -> None:
    try:
        await asyncio.wait_for(
            asyncio.gather(
                worker("task 1", lock_a, lock_b),
                # The same order as task 1
                worker("task 2", lock_a, lock_b),
            ),
            timeout=0.5,
        )
        print("both workers finished")
    except TimeoutError:
        print("deadlock detected")

asyncio.run(main())
#: task 1: holds its first lock
#: task 1: holds both
#: task 2: holds its first lock
#: task 2: holds both
#: both workers finished
```

The program finishes in about twenty milliseconds rather than waiting out the half-second timeout.

**Acquire the locks in one order.**
Follow who waits for whom.
The first task takes `lock_a`, sleeps, then takes `lock_b`, which is free.
Meanwhile the second task reaches `async with lock_a` and suspends,
because the first task has it.
That suspension is a wait,
but every lock the first task needs is either its own or free.
The first task finishes and releases both locks.
The second task then finds both locks free.

The deadlock version makes the waiting circular.
Task one holds `lock_a` and waits for `lock_b`,
while task two holds `lock_b` and waits for `lock_a`,
so each task's progress depends on the other task's progress.
A deadlock is that cycle.
Acquiring the locks in one global order makes such a cycle impossible.
Every lock a task waits for comes later in the order than every lock it holds.
"Later" never loops back to "earlier."

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 15. Awaiting `pool.submit()` directly

> In `mixed_await.py`,
> replace the body of `process_price()` with `return await pool.submit(cpu_price, order)`.
> Run `ty` on the changed file, then run the file, and read the two errors.
> Explain, using [One Task, Many Backends](../../Chapters/19_Techniques--Concurrency.md#one-task-many-backends),
> why you cannot await `pool.submit()`'s return value,
> what `loop.run_in_executor()` returns instead,
> and why the runtime `TypeError` arrives wrapped in an `ExceptionGroup`.

<details>
<summary>Where to look</summary>

[One Task, Many Backends](../../Chapters/19_Techniques--Concurrency.md#one-task-many-backends)
and [One `await`, Any Backend](../../Chapters/19_Techniques--Concurrency.md#one-await-any-backend)
show how an executor's work becomes awaitable.
Check what type `pool.submit()` returns and whether that type defines `__await__`.
The bridge is `loop.run_in_executor()`.
The `ExceptionGroup` comes from the `TaskGroup` that runs `process_price()`.

<details>
<summary>Done when</summary>

`uv run ty check` on your edited `mixed_await.py` reports `invalid-await` on the `await`,
and running the file ends in an `ExceptionGroup` whose one sub-exception is `TypeError: 'Future' object can't be awaited`.
You can name what `loop.run_in_executor()` returns and which construct wraps the `TypeError`.

<details>
<summary>Solution</summary>

The changed function drops the bridge:

```python
async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> Price:
    return await pool.submit(cpu_price, order)
```

`ty` rejects the line before anything runs:

    error[invalid-await]: `Future[Price]` is not awaitable

At runtime the line raises a `TypeError` before any price comes back:

    + Exception Group Traceback (most recent call last): ...
    | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
    +-+---------------- 1 ----------------
      |     return await pool.submit(cpu_price, order)
      | TypeError: 'Future' object can't be awaited

`pool.submit()` returns a `concurrent.futures.Future`,
the executor's own handle on a result a worker is still computing.
The `Future`'s interface blocks.
You wait by calling `result()`,
which stops the calling thread until the worker finishes.
That future holds no reference to an event loop and defines no `__await__`.
The type checker therefore reports the `await`,
and Python raises `TypeError` at runtime.

`loop.run_in_executor()` is the bridge the original listing uses.
It submits the call to the executor the same way `submit()` does,
but returns an `asyncio.Future` bound to the running loop,
an awaitable that resolves when the executor's own future completes.
The task suspends on the `asyncio.Future` like any other `await`.
In the meantime the loop keeps running the other two tasks.

The `TaskGroup` puts the wrapper around the `TypeError`.
`process_price()` fails as a task inside the group,
so the group cancels that task's two siblings, waits for them to end,
and re-raises the failure wrapped in an `ExceptionGroup`.
`task_group.py` catches the same wrapper with `except*`.
`mixed_await.py`'s `main()` has no `except*`,
so the `ExceptionGroup` propagates out of `asyncio.run()` and prints as the grouped traceback above.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
