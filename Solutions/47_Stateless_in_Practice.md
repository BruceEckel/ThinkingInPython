# Stateless in Practice: Solutions

## 1. An advancing handler, and the fix it cannot break

```python
# advancing_clock.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
from stateless import Ability, Depend, handle, run

class Now(Ability[datetime]):
    pass

def now() -> Depend[Now, datetime]:
    moment: datetime = yield from Now()
    return moment

def ticking(
    start: datetime, step: timedelta
) -> Callable[[Now], datetime]:
    moment = start
    def advancing(request: Now) -> datetime:
        nonlocal moment
        current = moment
        moment += step
        return current
    return advancing

def archive_twice(entry: str) -> Depend[Now, tuple[str, str]]:
    opened = yield from now()
    path = f"log-{opened:%Y-%m-%d}.txt"
    stamped = yield from now()
    return path, f"[{stamped:%Y-%m-%d}] {entry}"

def archive_once(entry: str) -> Depend[Now, tuple[str, str]]:
    moment = yield from now()
    path = f"log-{moment:%Y-%m-%d}.txt"
    return path, f"[{moment:%Y-%m-%d}] {entry}"

LATE: Final[datetime] = datetime(2026, 1, 1, 23, 59, 59)
SECOND: Final[timedelta] = timedelta(seconds=1)

print(run(handle(ticking(LATE, SECOND))(archive_twice)("ok")))
#: ('log-2026-01-01.txt', '[2026-01-02] ok')
print(run(handle(ticking(LATE, SECOND))(archive_once)("ok")))
#: ('log-2026-01-01.txt', '[2026-01-01] ok')
```

`ticking()` is a handler factory.
It stores a moment, and each request returns the current value and advances the stored one by `step`.
`nonlocal` is what makes the handler stateful.
Without it, `moment += step` would bind a local name,
and every request would answer the same instant.
`crossing` in `midnight.py` walks a two-element list and stops there,
while `ticking()` answers any number of requests,
so the same handler serves an Effect that reads the clock three times or thirty.
Each call to `ticking()` builds a fresh handler with its own stored moment,
which is why the two runs below both start at 23:59:59.

`archive_twice()` is the original function.
The first request names the file for January 1 and the second stamps the entry January 2,
so the bug survives the change of handler.
It should.
Nothing about the handler caused it.

`archive_once()` reads the clock one time and derives both strings from that value.
The mismatch needed two readings that could differ.
With one reading there is nothing to disagree.
A handler still chooses the moment, and it can choose 23:59:59,
but both strings then carry that moment.
No handler can reproduce the bug, because the bug was not in the handler.
It was in a function that asked twice and treated the answers as one.

That is the general shape of a clock bug.
Reading a clock twice reads a changing value twice,
and two readings are two facts rather than one.
Naming the clock as an ability made the failure reproducible.
Deriving both strings from a single reading removed it.
