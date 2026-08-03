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
`d` resumes before the other three. The returned list ignores both
orders. `gather()` fills each position from the argument that occupied
it, which is why `'D'` is last in the list even though `d` finished
first.

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
    print(f"took the sum, not the longest: {elapsed > 0.055}")

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

Each `started` line is immediately followed by its own `resumed` line,
which is the signature of no overlap. The comprehension awaits one
coroutine at a time, and `await` does not return until that coroutine
finishes, so `b` cannot start until `a` is done. Nothing schedules the
later coroutines while the current one waits.

The timing follows from the trace. `gather()` finishes in about the
longest delay, 0.03 seconds, because all three waits overlap. This
version takes their sum, about 0.06 seconds, because no two waits ever
happen at the same time. The list comprehension is not the problem.
Building the coroutine objects created work that had not started, and
only `gather()` or `TaskGroup` schedules every one of them as a task
before waiting on any.

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
        await asyncio.sleep(0.05)   # Waiting, off the processor
        total = 0
        for _ in range(1_000_000):  # Working, on the processor
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

Move the loop above the `await` and the peak drops back to `1`. Each
coroutine then runs its full million iterations before yielding,
and the event loop never gets the chance to overlap them. What
decides overlap is where the `await` sits relative to the computation,
not that the function contains one somewhere.

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
a chance to start another, so each task runs start to finish before the
next begins.

Waiting is not what creates overlap. Suspending is. These five tasks
spend almost all their time waiting and still overlap not at all, while
`cpu_price()` overlapped not at all for the opposite reason, having no
`await` to reach. The total run time makes the cost visible: five
blocking sleeps of 0.05 seconds take about a quarter second, where five
awaited ones took about 0.05.

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
way out. Initialized to `1`, the count is exhausted by the first task
through, so every other task suspends at `async with` until that task
leaves. One read-modify-write is in progress at a time, exactly as with
`asyncio.Lock`, and all 400 increments land.

The equivalence is only as good as the count. Add one stray release
before the tasks start and the semaphore admits two holders instead of
one:

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
so each pair of increments collapses into one. The count reports no
error, because raising the limit is what `release()` is defined to do.

This is the difference between the two objects. `asyncio.Lock` refuses
a release it never granted, raising `RuntimeError: Lock is not
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
refuses, instead of letting the recursion consume the machine. The
`if __name__ == "__main__"` line prevents it because a spawned worker
imports the module under its real name, `parallel_cpu`, not
`"__main__"`, so the pool-building code is skipped in the child and
runs only in the process you launched.

This is a `spawn` problem, not a universal one. On a platform using
`fork`, the child inherits the parent's memory instead of importing the
module, and the missing guard does no damage. Windows and macOS both
default to `spawn`, so code written without the guard breaks when it
moves between machines.

## 7. Removing the `sleep` from `gil_race.py`

```python
import threading

counter = 0

def increment(count):
    global counter
    for _ in range(count):
        value = counter   # Read
        counter = value + 1  # Write back, with nothing in between

threads = [threading.Thread(target=increment, args=(50,)) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter, counter == 400)
```

Running this repeatedly on CPython 3.11 or later reliably prints `400
True`, every time. Since 3.11, the interpreter only considers
switching threads at a function call or at the jump that closes a loop
iteration. With the `time.sleep()` call removed, the read and the
write happen back to back with no function call between them, so
there is no longer a scheduling point where the GIL can hand off to
another thread in the middle of the sequence. That absence of a
visible race is scheduling luck tied to how the current interpreter
happens to schedule switches, not a guarantee. Any function call
reintroduced between the read and the write, a blocking I/O call, a
`print()`, even an innocuous-looking helper function, reopens exactly
the same gap, because nothing about `counter += 1`'s underlying
bytecode sequence became atomic. The fix is still a lock, not the
absence of an explicit sleep.

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
value, so the drain order is always priority first, `1` before `2`
before `3`, and within a priority, alphabetically by the description
(the tuple's second field): `"alert"` before `"page oncall"` before
`"zzz"`, and `"aaa"` before `"backup"`. Which thread happened to submit
a job first never affects the final order.
