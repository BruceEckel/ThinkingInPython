# exercise_4.py
from typing import Any
from exceptions import ignore

class Implementation:
    def f(self) -> None: print("f()")

class BrokenProxy:
    def __init__(self, impl: Any) -> None:
        self._impl = impl
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._imp, name)  # Deliberate typo
        if callable(attr):
            def counted(*args: Any, **kwargs: Any) -> Any:
                self.calls += 1
                return attr(*args, **kwargs)
            return counted
        return attr

p = BrokenProxy(Implementation())
with ignore(RecursionError):
    p.f()
#: RecursionError('maximum recursion depth exceeded')
