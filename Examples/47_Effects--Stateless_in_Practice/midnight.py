# midnight.py
from datetime import datetime, timedelta
from typing import Final
from stateless import Depend, handle, run
from timekeeping import Now, now

def archive(entry: str) -> Depend[Now, tuple[str, str]]:
    opened = yield from now()
    path = f"log-{opened:%Y-%m-%d}.txt"
    stamped = yield from now()
    return path, f"[{stamped:%Y-%m-%d}] {entry}"

MIDDAY: Final[datetime] = datetime(2026, 1, 1, 12, 0)
LATE: Final[datetime] = datetime(2026, 1, 1, 23, 59, 59)
ticks = iter([LATE, LATE + timedelta(seconds=2)])

def steady(request: Now) -> datetime:
    return MIDDAY

def crossing(request: Now) -> datetime:
    return next(ticks)

print(run(handle(steady)(archive)("backup ok")))
#: ('log-2026-01-01.txt', '[2026-01-01] backup ok')
print(run(handle(crossing)(archive)("backup ok")))
#: ('log-2026-01-01.txt', '[2026-01-02] backup ok')
