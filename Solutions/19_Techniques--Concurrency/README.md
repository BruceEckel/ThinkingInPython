# Concurrency: Solutions

## 1. A fourth coroutine in the `gather()`

> In `async_mechanics.py`, add a fourth call, `fetch("d", 0.005)`,
> to the `gather()` line.
> Confirm that "d" starts last but resumes first,
> and that the printed list still grows to four entries in the order given,
> not the order they finish.

<details>
<summary>Where to look</summary>

[`async def`, `await`, and the Event Loop](../../Chapters/19_Techniques--Concurrency.md#asyncio-mechanics) shows each coroutine suspending at its `await` while the loop starts the next one.
Add the fourth `fetch()` to the arguments of `gather()` and compare two orders in the output.
The order in which timers fire decides the `resumed` lines, while the argument positions decide the returned list.

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
`d` resumes before the other three.

The returned list follows the argument order, not the finishing order.
`gather()` fills each position from the coroutine passed in that
position, so `'D'` is last in the list although `d` finished first.

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

[`async def`, `await`, and the Event Loop](../../Chapters/19_Techniques--Concurrency.md#asyncio-mechanics) explains that a coroutine object does nothing until something awaits it.
In `[await c for c in coroutines]`, ask what the comprehension does with the first `await` before it moves to the second `c`.
Compare that with `gather()`, which wraps every coroutine in a task before it waits on any of them.

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

**Await each coroutine in turn.** Each `started` line has its own `resumed` line directly beneath it,
the signature of no overlap. The comprehension awaits one coroutine at
a time, and `await` does not return until that coroutine finishes, so
`b` cannot start until `a` finishes. Nothing schedules the later
coroutines while the current one waits.

The timing follows from the trace. `gather()` finishes in about the
longest delay, 0.03 seconds, because all three waits overlap. This
version takes their sum, about 0.06 seconds, because the waits run one
after another.

The list comprehension is not the problem. Calling `fetch()` builds a
coroutine object and starts nothing. Only `gather()` or a `TaskGroup`
schedules every coroutine as a task before waiting on any.

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

[I/O-Bound vs CPU-Bound](../../Chapters/19_Techniques--Concurrency.md#io-bound-vs-cpu-bound) and [Overlapping the Waits](../../Chapters/19_Techniques--Concurrency.md#overlapping-the-waits) measure overlap with `meter.peak`.
A task counts as active while it sits inside the `with meter:` block, including while it is suspended.
Look at where the `await` falls relative to that block, and whether the other four tasks get a chance to start at it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type: object, exc: object,
                 tb: object) -> None:
        ...

async def mixed_price(order: int, meter: Meter) -> int:
    ...

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_3.py
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

async def mixed_price(order: int, meter: Meter) -> int:
    with meter:
        # Waiting, off the processor
        await asyncio.sleep(0.05)
        total = 0
        # Working, on the processor
        for _ in range(1_000_000):
            total += 1
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
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

**Suspend before computing.** The peak is `5`, matching the I/O-bound case rather than the CPU-bound
one. `mixed_price()` reaches its `await asyncio.sleep(0.05)` before the
CPU-heavy loop, so all five coroutines suspend at that `await` and let
their siblings start before any of them begins computing. All five are
in flight, waiting, at once.

**Count a suspended task as active.** The peak stays `5` wherever the
loop sits, because the `await` is inside the `with meter:` block. A
task suspended there still counts as active. If you remove the
`await`, as `cpu_price()` does, the peak falls to `1`. Overlap depends
on whether an `await` sits inside the measured span, not on where it
sits relative to the computation.

</details>
</details>
</details>

## 4. Blocking inside a coroutine

> In `peak_concurrency.py`,
> change `io_price()`'s `await asyncio.sleep(0.05)` to `time.sleep(0.05)` and predict how its `meter.peak` changes before running it.
> Explain the result using `blocking_the_loop.py`.

<details>
<summary>Where to look</summary>

[`time.sleep()` Stops the Loop](../../Chapters/19_Techniques--Concurrency.md#time-sleep-stops-the-loop) shows a blocking call freezing every other task.
The event loop runs on one thread, and `time.sleep()` holds that thread instead of suspending the task.
Think about whether any task can start while another one sleeps, and what that does to the count of simultaneous tasks.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

@dataclass
class Meter:
    active: int = 0
    peak: int = 0

    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type: object, exc: object,
                 tb: object) -> None:
        ...

async def io_price(order: int, meter: Meter) -> int:
    ...

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
import asyncio
import time
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
        time.sleep(0.05)  # Blocking, and never awaited
    return order * 10

type PriceTask = Callable[[int, Meter], Awaitable[int]]

async def run(price_task: PriceTask,
              orders: list[int]) -> tuple[list[int], int]:
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

**Hold the thread while waiting.** The peak falls from `5` to `1`, the
same figure the CPU-bound version produced. `time.sleep()` does here
what it does in `blocking_the_loop.py`. The call stops the thread
instead of suspending the task, and the event loop runs on that
thread. A coroutine with no `await` gives the loop no chance to start
another task, so each task runs start to finish before the next
begins.

Waiting does not create overlap. Suspending does. These five tasks
spend almost all their time waiting and still run one at a time,
and `cpu_price()` runs one at a time for the opposite reason: it has no
`await` to reach. The total run time makes the cost visible. Five
blocking sleeps of 0.05 seconds take about a quarter second, while
five awaited ones take about 0.05.

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

[Locks](../../Chapters/19_Techniques--Concurrency.md#locks) and [Semaphores](../../Chapters/19_Techniques--Concurrency.md#semaphores) show `async with` guarding a critical section.
A `Semaphore` holds a count of admitted holders, and `async with` decrements it on entry and restores it on exit.
For the stray `release()`, ask how many tasks the count now admits and whether `release()` checks that an `acquire()` came first.

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
    print(counter)

asyncio.run(main())
#: 400
```

**Admit one holder at a time.** A semaphore holds a count of how many holders it admits at once, and
`async with` decrements that count on entry and restores it on
exit. With the count initialized to `1`, the first task through
exhausts it, so every other task suspends at `async with` until that
task leaves. Only one read-modify-write runs at a time, as with
`asyncio.Lock`, and all 400 increments survive.

The equivalence is only as good as the count. If you add one stray
release before the tasks start, the semaphore admits two holders
instead of one:

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
    print(counter)

asyncio.run(main())
#: 200
```

**Admit a second holder.** Exactly half the increments survive. Two tasks now sit inside the
critical section together, both reading `counter` before either writes,
so each pair of increments collapses into one. The semaphore reports
no error, because `release()` adds one to the count whether or not an
`acquire()` came first.

That silence is the difference between a semaphore and a lock.
`asyncio.Lock` refuses a release with no matching acquire, raising
`RuntimeError: Lock is not acquired.` A semaphore does not track what it
granted, so the same mistake silently admits a second holder and
reintroduces the race the lock is there to prevent.
`asyncio.BoundedSemaphore(1)` is the semaphore that objects. The stray
`release()` raises
`ValueError: BoundedSemaphore released too many times`.

</details>
</details>
</details>

## 6. Removing the `__main__` guard

> Remove the `if __name__ == "__main__"` guard from `parallel_cpu.py`,
> so its body runs unconditionally, and run it.
> Read the error, whose useful part is the `RuntimeError` traceback each failing child process printed above the `BrokenProcessPool` at the bottom,
> then explain it with the import mechanics described in [Parallelism](../../Chapters/19_Techniques--Concurrency.md#what-a-process-pool-requires):
> what did each worker process do when it imported the module?

<details>
<summary>Where to look</summary>

[What a Process Pool Requires](../../Chapters/19_Techniques--Concurrency.md#what-a-process-pool-requires) describes how a worker process finds the function it must run.
The worker imports your module, and importing executes every top-level statement.
Read the `RuntimeError` text for what a worker tries to do during that import, and for the name `__mp_main__` that the guard tests.

<details>
<summary>Solution</summary>

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

**Build the pool at import time.** Each worker does what the chapter describes. To find `cpu_price()`, a
fresh interpreter imports this module, and importing it runs every
top-level statement, including the `with ProcessPoolExecutor()` line
that creates workers. Each worker therefore tries to build a pool of
its own, whose workers would import the module again.

The error is a guard rail rather than the real failure. Python detects
that a child process is spawning children during its own bootstrap and
refuses to start them, instead of letting the recursion consume the
machine.

The `if __name__ == "__main__"` line prevents that recursion.
A worker runs the module under the name `"__mp_main__"` rather
than `"__main__"`, so the child skips the pool-building code and only
the process you launched runs it.

The whole failure is a start-method problem. On a platform using
`fork`, the child inherits the parent's memory instead of importing the
module, and the missing guard does no damage. But no platform forks by
default anymore. Windows and macOS default to `spawn`, and since 3.14
Linux defaults to `forkserver`, which also imports the module. Every
platform's default therefore requires the guard.

</details>
</details>

## 7. Removing the `sleep` from `gil_race.py`

> In `gil_race.py`, remove the `time.sleep(0.000_001)` call and run the script several times.
> Explain, using [The GIL Does Not Prevent Races](../../Chapters/19_Techniques--Concurrency.md#the-gil-does-not-prevent-races),
> why the race becomes far less likely to show up without that sleep,
> but is not thereby fixed.

<details>
<summary>Where to look</summary>

[The GIL Does Not Prevent Races](../../Chapters/19_Techniques--Concurrency.md#the-gil-does-not-prevent-races) explains where the interpreter may switch threads.
Without the call, check whether any switch point remains between the read and the write of the shared value.
Then ask whether a missing switch point makes the read-modify-write sequence atomic, or hides the gap.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from concurrent.futures import ThreadPoolExecutor

def increment(count: int) -> None:
    ...
```

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

**Run the read and write back to back.** Running this repeatedly on the standard build prints
`lost updates: False` every time. Since 3.10, the interpreter
considers switching threads only at a function call or at the jump
that closes a loop iteration. With the `time.sleep()` call removed, the read and the
write run back to back, with no function call between them, so the
interpreter finds no scheduling point at which to hand the GIL to
another thread mid-sequence. That reliability is luck rather than a guarantee.

The race stays invisible only because this interpreter places its
switch points elsewhere. Any function call put back between the read
and the write, a blocking I/O call, a `print()`, or an innocuous-looking
helper, reopens the same gap, because the read-modify-write sequence
is still not atomic. A free-threaded interpreter has no GIL to hold
through the sequence, so there the race needs no function call. The
fix is still a lock, not the absence of an explicit sleep.

</details>
</details>
</details>

## 8. A third thread submitting jobs

> In `priority_queue.py`,
> add a third thread submitting `[(1, "zzz"), (3, "aaa")]` and confirm the drain order still respects priority first,
> then the description as a tiebreaker.

<details>
<summary>Where to look</summary>

[Coordinating Threads with Queues](../../Chapters/19_Techniques--Concurrency.md#coordinating-threads-with-queues) shows producers feeding a `PriorityQueue` that a consumer drains.
Add a third `pool.submit(enqueue, ...)` call and keep the chapter's `max_workers=3`.
Three workers cover three producers, and the consumer needs no extra worker, since the listing submits it after the producers finish.
The queue orders items by comparing tuples, so the interleaving of the producers does not affect the drain order.

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

**Add a third producer.** The one change is the third `pool.submit(enqueue, ...)`.
The chapter's `max_workers=3` stays.
Three workers cover the three producers,
and `consume()` needs no fourth, because the listing submits it after every producer finishes.
A run with `max_workers=4` prints the same six lines in the same order.

**Drain in priority order.** The pool may run the three producers on one thread or on two,
depending on whether each producer finishes before the pool picks up the next.
The order in which the six jobs enter the queue can therefore vary, but `PriorityQueue` orders its items by comparing the tuples.
The drain order is therefore always priority first, `1` before `2`
before `3`, then alphabetically by the description within a priority
(the tuple's second field): `"alert"` before `"page oncall"` before
`"zzz"`, and `"aaa"` before `"backup"`. The thread that submits a job
first has no effect on the final order, because `consume()` starts
after all three producers finish.

</details>
</details>
</details>

## 9. A task that finishes before the failures land

> In `utils/fetch_demo.py`,
> change `("e", 0.2)` in `PAIRS` to `("e", 0.005)` so `e` finishes before `c` and `d` fail,
> then run `task_group.py`.
> Predict which of the six report `cancelled` and which report a result,
> then run it and explain what a `TaskGroup` can and cannot undo.
> Change `PAIRS` back afterward,
> since `gather_with_exceptions.py` uses it too.

<details>
<summary>Where to look</summary>

[Structured Concurrency with `TaskGroup`](../../Chapters/19_Techniques--Concurrency.md#structured-concurrency-with-taskgroup) shows a failing child causing the group to cancel its siblings.
Compare each task's delay with the moment `c` and `d` fail to decide which tasks are still running when cancellation starts.
Cancellation reaches only running tasks, so consider what it cannot do to a task that has returned.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
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

async def sleep_until(when: float) -> None:
    ...

async def fetch(item: str, delay: float, t0: float) -> str:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

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

async def sleep_until(when: float) -> None:
    loop = asyncio.get_running_loop()
    woken: asyncio.Future[None] = loop.create_future()
    timer = loop.call_at(when, woken.set_result, None)
    try:
        await woken
    finally:
        timer.cancel()

async def fetch(item: str, delay: float, t0: float) -> str:
    print(f"{item}: started")
    await sleep_until(t0 + delay)
    if item in ("c", "d"):
        raise ValueError(f"fetch({item!r}) failed")
    print(f"{item}: fetched")
    return item.upper()

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {
                item: tg.create_task(fetch(item, delay, t0))
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

**Let one task finish first.** Only `f` reports `cancelled` now. With `e` at `0.005` its timer fires
long before `c` and `d` fail at `0.03`, so `e` prints `fetched`,
returns `"E"`, and has finished by the time the group starts
cancelling. `f` still sleeps for `0.3`, so the group cancels it
during that sleep and its task ends cancelled.

**Cancel what is still running.** The difference between `e` and `f` is the line between what a
`TaskGroup` can and cannot undo. A
`TaskGroup` cancels what is still running, which is why the original
`PAIRS` has both `e` and `f` cancelled. It cannot reach into a task
that has returned, and it cannot unprint `e: fetched` or undo
whatever a real `fetch()` wrote to a database on its way out.
Structured concurrency guarantees that no task outlives the block, not
that no task had an effect before the failure.

The distinction matters when the tasks do more than sleep. A group of
six writes where two fail leaves the successful writes in place, so
recovery is your problem, not the `TaskGroup`'s.
[Context Managers](../../Chapters/15_Techniques--Context_Managers.md) and the Effect chapters
address that recovery from different directions: pairing an action with the cleanup
that undoes it, so "already finished" still means "still reversible."

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

[Failures as Values with `gather()`](../../Chapters/19_Techniques--Concurrency.md#failures-as-values-with-gather) shows `return_exceptions=True` collecting every outcome.
Without it, the first child exception propagates out of the `await`, so count which timers fire before that moment.
For the remaining tasks, compare with a `TaskGroup` and ask who cancels them, and what `asyncio.run()` does at shutdown.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

If you leave out the `return` in the `except` block,
the handler prints its line and execution falls through to `print(results)`.
`results` is unbound at that point,
so the line raises an `UnboundLocalError` right after the `gather raised` line.
The type checker passes that version, so the failure shows up at run time.
The solution returns from the handler, so the code after the `try` statement runs when `gather()` returns a list.

```python
# exercise_10.py
import asyncio
from fetch_demo import PAIRS, fetch

async def main() -> None:
    t0 = asyncio.get_running_loop().time()
    try:
        results = await asyncio.gather(*(
            fetch(item, delay, t0)
            for item, delay in PAIRS))
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
before `c` fails at `0.03`. `e` and `f` print nothing, and
`print(results)` does not run, because the `await` raises the
`ValueError` instead of returning a value.

**Propagate the first failure.** Without `return_exceptions=True`, the first child exception propagates
out of the `await` immediately, and `gather()` reports that one
exception rather than a list of six outcomes. `d` fails in the same
tick, but the `gather()` future has resolved by then, so
`gather()` retrieves `d`'s failure and discards it instead of raising
it. The call loses the four results it was collecting, including `a`
and `b`, which had succeeded.

**Leave the other tasks running.** `gather()` does not cancel the unfinished tasks, `e` and `f`,
when the exception propagates, unlike a `TaskGroup`, so `e` and
`f` are still sleeping when `main()` returns. `asyncio.run()` then
cancels whatever tasks remain as it shuts the loop down, which is why
`e` and `f` print nothing further. If `main()` goes on to other work,
they run to completion in the background with nobody waiting on their
results.

That combination, results discarded and siblings left running, is why
`return_exceptions=True` and `TaskGroup` exist.
`return_exceptions=True` keeps every outcome, so partial success stays
visible. A `TaskGroup` guarantees that nothing outlives the block.
Bare `gather()` gives you neither.

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

[Context That Follows the Call Chain](../../Chapters/19_Techniques--Concurrency.md#context-that-follows-the-call-chain) shows each task running in its own copy of the context.
Move the `set()` call so it runs before the `TaskGroup` creates any task, and ask what value each copy holds at creation.
Also check what the `after:` line reads, since a child's `set()` and a parent's `set()` write to different contexts.

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

**Set the value before any task exists.** All three tasks print
`context main`. Every task starts with a copy of the context current
when `create_task()` runs, and inside `main()` that context already
carries `request_id = "main"`, so each copy inherits the same value.
No task writes to the variable afterward, so all three copies stay
identical and the original version's per-request identity disappears.

**Read the value after the group.** The `after:` line changes too. In
the chapter's version it prints `context -`, the default, because each
`set()` runs inside a task's own copy and none of them can reach
`main()`'s context. Here the `set()` is in `main()`, so it writes to
`main()`'s own context and the value is still there once the group
finishes. Copying runs one way. A child sees what the parent had at
creation, and the parent sees nothing a child did.

`current` behaves as before, reaching `req-3` everywhere, which is the
contrast the example exists to draw. A `global` is one cell shared by
every task, so the last writer wins and the other two tasks read a
value meant for someone else. A `ContextVar` is per-task storage
reachable by one name.

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

[The GIL and Free Threading](../../Chapters/19_Techniques--Concurrency.md#the-gil-and-free-threading) and [Subinterpreters](../../Chapters/19_Techniques--Concurrency.md#subinterpreters) describe where the GIL lives.
The assertion compares results, which do not depend on which executor ran the work.
The boolean compares times, so ask how many GILs a pool of threads shares and how many a pool of subinterpreters has.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_12.py
import os
import timeit
from concurrent.futures import ThreadPoolExecutor
from benchmark import report

def cpu_price(order: int) -> int:
    ...

def sequential(orders: list[int]) -> list[int]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_12.py
import os
import timeit
from concurrent.futures import ThreadPoolExecutor
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

with ThreadPoolExecutor() as pool:
    parallel = list(pool.map(cpu_price, orders))
    assert parallel == sequential(orders)
    t_thr = timeit.timeit(
        lambda: list(pool.map(cpu_price, orders)), number=5
    )

cores = os.cpu_count() or 1
target = min(1.5, cores * 0.7)  # Two cores cannot give 1.5x
report(sequential=t_seq, threads=t_thr, cores=cores)
print(f"threads run in parallel: {t_seq > t_thr * target}")
#: threads run in parallel: False
```

**Check that the results agree.** The assertion passes because
correctness does not depend on the executor. `cpu_price()` reads its
argument and returns a number, touching nothing shared, so five calls
produce the same five results whether they run one after another, in
five threads, or in five subinterpreters. Swapping the executor changes
when the work runs, not what it computes.

**Compare the timings.** The boolean flips because threads in one interpreter share one GIL.
`cpu_price()` is a counting loop with no I/O and no `sleep`, so it
holds the GIL except at the interpreter's periodic switch points. Five
such threads take turns on one processor and finish in about the time
five sequential calls take, so `t_seq` and `t_thr` come out close
together and `t_seq > t_thr * target` is `False`.

`InterpreterPoolExecutor` wins the same benchmark because each
[subinterpreter](../../Chapters/19_Techniques--Concurrency.md#subinterpreters)
has its own GIL. The work spreads across processors instead of
time-slicing on one. A free-threaded build reaches the same end by
removing the GIL instead of multiplying it, letting ordinary threads
do what this listing's threads cannot.

</details>
</details>
</details>

## 13. A lock around the loop body, not around `next()`

> In `shared_iterator.py`,
> drop `threading.serialize_iterator()` and give each worker a function that loops over the shared iterator,
> holding a `threading.Lock` around the loop *body*,
> the tempting fix in [Sharing an Iterator Between Threads](../../Chapters/19_Techniques--Concurrency.md#sharing-an-iterator-between-threads).
> Predict whether `duplicates` becomes `False` before running it,
> and explain which call the lock does and does not cover.

<details>
<summary>Where to look</summary>

[Sharing an Iterator Between Threads](../../Chapters/19_Techniques--Concurrency.md#sharing-an-iterator-between-threads) shows the race inside a shared iterator and `threading.serialize_iterator()` fixing it.
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

def report(source: Iterator[int]) -> None:
    ...
```

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

**Take each item unguarded.** `for item in source:` is the `for` statement calling
`source.__next__()`, and that call runs before control reaches the
indented block. The `with lock:` inside the body therefore starts
*after* `next()` has returned a number, and ends before the
next `next()` begins. Two threads can be inside `__next__()` at the
same moment, read the same `next_number`, and come away with the same
ticket, as they do without the lock.

**Lock the loop body.** The lock does cover `out.append(item)`, which
needs no lock. `out` is a local list, one per worker, so no other
thread can touch it.

Serializing an iterator means putting the lock where the mutation is,
inside `__next__()`, where `threading.serialize_iterator()` puts it.
The lesson generalizes past iterators. A lock protects the statements
it encloses, and a `for` loop's own call to `next()` is not one of
them.

</details>
</details>
</details>

## 14. Both tasks acquiring in the same order

> In `async_deadlock.py`,
> change the second `worker()` call to `worker(lock_a, lock_b)` so both tasks acquire in the same order,
> and add a line that prints when both finish.
> Predict what the program prints before running it, then explain,
> in terms of who waits for whom,
> why one shared acquisition order removes the cycle.

<details>
<summary>Where to look</summary>

[Deadlock](../../Chapters/19_Techniques--Concurrency.md#deadlock) shows two tasks each holding one lock and waiting for the other.
Change the second `worker()` call, then trace which task takes `lock_a` first and what the other task does at its `async with`.
Draw an arrow from each waiting task to the task it waits on and check whether those arrows can form a loop.

<details>
<summary>The shape</summary>

```python
# The shape of ch19_ordered_locks.py
import asyncio

async def worker(
    first: asyncio.Lock, second: asyncio.Lock
) -> None:
    ...

async def main() -> None:
    ...
```

<details>
<summary>Solution</summary>

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

**Acquire the locks in one order.** Follow who waits for whom. The first task takes `lock_a`, sleeps, then
takes `lock_b`, which nobody holds. Meanwhile the second task reaches
`async with lock_a` and suspends, because the first task has it. That
suspension is a wait, but a wait on a task that is waiting on nothing the second
task holds. The first task finishes and releases both locks, and the
second task then takes each lock with no other task holding it.

The deadlock version makes the waiting circular. Task one holds
`lock_a` and waits for `lock_b`, task two holds `lock_b` and
waits for `lock_a`, so each task's progress depends on the other task's
progress. A deadlock is that cycle. Acquiring the
locks in one global order makes such a cycle impossible. Every lock a
task waits for comes later in the order than every lock it holds,
and "later" never loops back to "earlier."

</details>
</details>
</details>

## 15. Awaiting `pool.submit()` directly

> In `mixed_await.py`,
> replace the body of `process_price()` with `return await pool.submit(cpu_price, order)`.
> Run `ty` on the changed file, then run it, and read the two errors.
> Explain, using [One Task, Many Backends](../../Chapters/19_Techniques--Concurrency.md#one-task-many-backends),
> why you cannot await `pool.submit()`'s return value,
> what `loop.run_in_executor()` returns instead,
> and why the runtime `TypeError` arrives wrapped in an `ExceptionGroup`.

<details>
<summary>Where to look</summary>

[One Task, Many Backends](../../Chapters/19_Techniques--Concurrency.md#one-task-many-backends) and [One `await`, Any Backend](../../Chapters/19_Techniques--Concurrency.md#one-await-any-backend) show how an executor's work becomes awaitable.
Check what type `pool.submit()` returns and whether that type defines `__await__`.
The bridge is `loop.run_in_executor()`, and the `ExceptionGroup` comes from the `TaskGroup` that runs `process_price()`.

<details>
<summary>Solution</summary>

The changed method drops the bridge:

```python
async def process_price(
    pool: ProcessPoolExecutor, order: int
) -> int:
    return await pool.submit(cpu_price, order)
```

`ty` rejects the line before anything runs:

    error[invalid-await]: `Future[int]` is not awaitable

At runtime the line raises a `TypeError` before any price comes back:

    + Exception Group Traceback (most recent call last):
      ...
    | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
    +-+---------------- 1 ----------------
      |     return await pool.submit(cpu_price, order)
      | TypeError: 'Future' object can't be awaited

`pool.submit()` hands back a `concurrent.futures.Future`, the
executor's own handle on a result a worker is still computing. Its
interface blocks. You wait by calling `result()`, which stops the
calling thread until the worker finishes. Nothing about that future
cooperates with an event loop, and it defines no `__await__`, so
`await` refuses it, first statically and then at runtime.

`loop.run_in_executor()` is the bridge the original listing uses. It
submits the call to the executor the same way `submit()` does, but
returns an `asyncio.Future` bound to the running loop, an awaitable
that resolves when the executor's own future completes. The task
suspends on the `asyncio.Future` like any other `await`, and the loop keeps running the
other two tasks in the meantime.

The wrapper around the `TypeError` is the `TaskGroup` keeping its
contract. `process_price()` fails as a task inside the group, so the
group cancels that task's two siblings, waits for them to end, and re-raises
the failure wrapped in an `ExceptionGroup`, the same packaging
`task_group.py` catches with `except*`. `main()` has no
`except*`, so the `ExceptionGroup` propagates out of `asyncio.run()` and prints
as the grouped traceback above.

</details>
</details>
