# exercise_5.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache
from typing import Final

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

_lock: Final[threading.Lock] = threading.Lock()

@cache
def settings() -> Settings:
    with _lock:  # Too late: the cache miss already happened
        return Settings()

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}) > 1)
#: True

@cache
def primed() -> Settings:
    return Settings()

primed()  # Built once, before any thread asks

with ThreadPoolExecutor(max_workers=8) as pool:
    shared = list(pool.map(lambda _: primed(), range(8)))
print(len({id(s) for s in shared}))
#: 1
