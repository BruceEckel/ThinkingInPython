# proxy_identity.py
from typing import Protocol, runtime_checkable
from proxy_getattr import Proxy

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

class Implementation:
    def f(self) -> None: print("Implementation.f()")

p = Proxy(Implementation())
p.f()
#: Implementation.f()
print(hasattr(p, "f"))
#: True
print(isinstance(p, Implementation), isinstance(p, Service))
#: False False
