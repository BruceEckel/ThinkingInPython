# race_settings.py
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

def distinct_objects(factory: Callable[[], object]) -> int:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(factory) for _ in range(8)]
    return len({id(f.result()) for f in futures})
