# proxy_setattr.py
from typing import Any

class Settings:
    def __init__(self) -> None:
        self.level = "low"

class WriteProxy:
    def __init__(self, impl: Any) -> None:
        object.__setattr__(self, "_impl", impl)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._impl, name)
    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._impl, name, value)

settings = Settings()
p = WriteProxy(settings)
p.level = "high"
print(p.level, settings.level)
#: high high
