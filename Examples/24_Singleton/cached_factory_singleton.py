# cached_factory_singleton.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings() -> Settings:
    return Settings()

a = settings()
b = settings()
assert a is b
a.data["theme"] = "dark"
print(b.data)
#: {'theme': 'dark'}
