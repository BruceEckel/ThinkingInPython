# proxy_writes.py
from proxy_getattr import Proxy

class Settings:
    def __init__(self) -> None:
        self.level = "low"

settings = Settings()
p = Proxy(settings)
print(p.level)
#: low
p.level = "high"  # type: ignore
print(p.level, settings.level)
#: high low
