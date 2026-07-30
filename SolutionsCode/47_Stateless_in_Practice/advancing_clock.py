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
