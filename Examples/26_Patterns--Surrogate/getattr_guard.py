# getattr_guard.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self._implementation = impl
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):  # The guard
            raise AttributeError(name)
        return getattr(self._imp, name)  # Deliberate typo

class Implementation:
    def f(self) -> None: print("Implementation.f()")

try:
    Proxy(Implementation()).f()
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError _imp
