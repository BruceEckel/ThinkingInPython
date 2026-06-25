# counting_proxy.py
from typing import Any

class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")

class CountingProxy:
    def __init__(self, impl: Any) -> None:
        self._impl = impl
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._impl, name)
        if callable(attr):
            def counted(*args: Any, **kwargs: Any) -> Any:
                self.calls += 1
                return attr(*args, **kwargs)
            return counted
        return attr

p = CountingProxy(Implementation())
p.f()
## f()
p.g()
## g()
p.f()
## f()
print("calls:", p.calls)
## calls: 3
