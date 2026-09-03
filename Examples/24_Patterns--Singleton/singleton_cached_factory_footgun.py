# singleton_cached_factory_footgun.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings(env: str = "prod") -> Settings:
    return Settings()

print(settings("prod") is settings("dev"))
#: False
