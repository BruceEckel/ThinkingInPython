# frozen_clock.py
from datetime import datetime, timedelta
from typing import Final
from stateless import handle, run
from timekeeping import Now, batch_due, stamp

LAUNCH: Final[datetime] = datetime(2026, 1, 1, 3, 0)

def frozen(request: Now) -> datetime:
    return LAUNCH

def tomorrow(request: Now) -> datetime:
    return LAUNCH + timedelta(hours=24)

print(run(handle(frozen)(stamp)("started")))
#: [2026-01-01 03:00] started
print(run(handle(frozen)(batch_due)(LAUNCH)))
#: False
print(run(handle(tomorrow)(batch_due)(LAUNCH)))
#: True
