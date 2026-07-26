# locked_settings.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

_lock: Final[threading.Lock] = threading.Lock()
_instance: Settings | None = None

def settings() -> Settings:
    global _instance
    with _lock:
        if _instance is None:
            _instance = Settings()
    return _instance

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}))
#: 1
