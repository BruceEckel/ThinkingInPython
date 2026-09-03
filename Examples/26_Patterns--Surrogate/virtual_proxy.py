# virtual_proxy.py
from typing import Any

class Expensive:
    def __init__(self) -> None:
        print("Expensive built")
    def query(self) -> str:
        return "result"

class Lazy:
    def __init__(self) -> None:
        self._real: Expensive | None = None
    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            self._real = Expensive()
        return getattr(self._real, name)

p = Lazy()
print("proxy ready")
#: proxy ready
print(p.query())
#: Expensive built
#: result
