# Concurrency: Solutions

## 1. A fourth coroutine in the `gather()`

```python
# exercise_1.py
import asyncio

async def fetch(item):
    await asyncio.sleep(0.01)
    return item.upper()

async def main():
    print(await asyncio.gather(
        fetch("a"), fetch("b"), fetch("c"), fetch("d")))

asyncio.run(main())
#: ['A', 'B', 'C', 'D']
```

`gather()` returns results in the order its arguments were given, no
matter which coroutine's `asyncio.sleep()` finishes first. Adding a
fourth call only adds a fourth position to that ordered result; it
does not change how `gather()` matches coroutines to positions.

## 2. A task that mixes waiting and computing

```python
# exercise_2.py
import asyncio

class Meter:
    def __init__(self):
        self.active = 0
        self.peak = 0

    def enter(self):
        self.active += 1
        self.peak = max(self.peak, self.active)

    def leave(self):
        self.active -= 1

async def run(task, orders):
    meter = Meter()
    coros = [task(o, meter) for o in orders]
    prices = await asyncio.gather(*coros)
    return prices, meter.peak

async def mixed_price(order, meter):
    meter.enter()
    await asyncio.sleep(0.05)   # Waiting outside the processor
    total = 0
    for _ in range(1_000_000):  # Working inside the processor
        total += 1
    meter.leave()
    return order * 10

async def main():
    orders = [1, 2, 3, 4, 5]
    prices, peak = await run(mixed_price, orders)
    print(f"mixed peak={peak}, prices={prices}")

asyncio.run(main())
#: mixed peak=5, prices=[10, 20, 30, 40, 50]
```

The peak is `5`, matching the I/O-bound case, not the CPU-bound one.
`mixed_price()` hits its `await asyncio.sleep(0.05)` *before* running
the CPU-heavy loop, so every one of the five coroutines suspends at
that `await` and lets its siblings start, before any of them reaches
the computing part. All five are "in flight," waiting, at once. Had
the CPU loop come *before* the `await` instead, each coroutine would
run its full million iterations to completion before yielding, and the
peak would drop back to `1`, since the event loop never gets a chance
to overlap them. The order of `await` relative to the computation, not
just its presence somewhere in the function, decides whether tasks
actually overlap.

## 3. Fixing the race with `asyncio.Lock`

```python
# exercise_3.py
import asyncio

counter = 0

async def increment(count, lock):
    global counter
    for _ in range(count):
        async with lock:
            value = counter
            await asyncio.sleep(0)
            counter = value + 1

async def main():
    lock = asyncio.Lock()
    await asyncio.gather(*(increment(50, lock) for _ in range(8)))
    print(counter)

asyncio.run(main())
#: 400
```

`async with lock:` wraps the read, the `await`, and the write in one
critical section. Only one coroutine can hold the lock at a time, so
even though `await asyncio.sleep(0)` still hands control to the event
loop mid-increment, no other coroutine can read `counter` until the
current holder finishes writing it back and releases the lock. The
eight coroutines now run their read-modify-write sequences one at a
time instead of interleaved, so all 400 increments land, matching the
shape of a threading fix but using `asyncio.Lock` instead of
`threading.Lock`.

## 4. Removing the `sleep` from `gil_race.py`

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

## 5. A third thread submitting jobs

```python
# exercise_5.py
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
