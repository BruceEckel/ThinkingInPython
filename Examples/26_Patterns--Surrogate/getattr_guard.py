# getattr_guard.py
from typing import Any
from exceptions import ignore

class Proxy:
    def __init__(self, impl: Any) -> None:
        self._implementation = impl
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):  # The guard
            raise AttributeError(name)
        return getattr(self._imp, name)  # Deliberate typo

class Implementation:
    def f(self) -> None: print("Implementation.f()")

with ignore(AttributeError):
    Proxy(Implementation()).f()
#: AttributeError('_imp')
