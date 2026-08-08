# singleton_eager_factory.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings() -> Settings:
    return Settings()

settings()  # Build it before any thread can race for it
print(settings() is settings())
#: True
