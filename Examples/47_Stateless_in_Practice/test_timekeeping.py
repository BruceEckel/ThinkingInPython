# test_timekeeping.py
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final
import pytest
from stateless import handle, run
from timekeeping import Now, batch_due, stamp

MOMENT: Final[datetime] = datetime(2026, 3, 14, 9, 30)

def at(moment: datetime) -> Callable[[Now], datetime]:
    def fixed(request: Now) -> datetime:
        return moment
    return fixed

def test_stamp_names_the_supplied_moment() -> None:
    stamped = run(handle(at(MOMENT))(stamp)("started"))
    assert stamped == "[2026-03-14 09:30] started"

@pytest.mark.parametrize("elapsed, due", [
    (timedelta(hours=23, minutes=59), False),
    (timedelta(hours=24), True),
])
def test_batch_due(elapsed: timedelta, due: bool) -> None:
    moment = MOMENT + elapsed
    is_due = run(handle(at(moment))(batch_due)(MOMENT))
    assert is_due is due
