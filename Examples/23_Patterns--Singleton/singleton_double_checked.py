# singleton_double_checked.py
import threading
from typing import Final
from race_settings import Settings, distinct_objects

_lock: Final[threading.Lock] = threading.Lock()
_instance: Settings | None = None

def settings() -> Settings:
    global _instance
    if _instance is None:  # [1]
        with _lock:
            if _instance is None:  # [2]
                _instance = Settings()
    return _instance

print(distinct_objects(settings))
#: 1
