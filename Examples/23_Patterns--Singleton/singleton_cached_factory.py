# singleton_cached_factory.py
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
print(a is b)
#: True
a.data["theme"] = "dark"
print(b)
#: Settings(data={'theme': 'dark'})
