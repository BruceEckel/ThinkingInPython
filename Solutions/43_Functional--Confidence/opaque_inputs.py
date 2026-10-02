# opaque_inputs.py
import os
from collections.abc import Mapping
from datetime import datetime, timedelta

def stale(created: datetime, limit: timedelta) -> bool:
    return datetime.now() - created > limit

def timeout() -> int:
    return int(os.environ.get("TIMEOUT", "30"))

def stale_pure(
    created: datetime, limit: timedelta, now: datetime
) -> bool:
    return now - created > limit

def timeout_pure(env: Mapping[str, str]) -> int:
    return int(env.get("TIMEOUT", "30"))

made = datetime(2020, 1, 1)
noon = datetime(2020, 1, 1, 12)
print(stale_pure(made, timedelta(days=1), noon))
#: False
print(timeout_pure({"TIMEOUT": "5"}), timeout_pure({}))
#: 5 30
