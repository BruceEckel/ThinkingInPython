# cached_factory_singleton.py
from functools import cache

class Settings:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

@cache
def settings() -> Settings:
    "Always returns the same Settings instance."
    return Settings()

a = settings()
b = settings()
assert a is b
a.data["theme"] = "dark"
print(b.data)
#: {'theme': 'dark'}
