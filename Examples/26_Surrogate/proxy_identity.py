# proxy_identity.py
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

class Implementation3:
    def f(self) -> None: print("Implementation.f()")

class Proxy3:
    def __init__(self) -> None:
        self.__implementation = Implementation3()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy3()
p.f()
#: Implementation.f()
print(hasattr(p, "f"))
#: True
print(isinstance(p, Implementation3), isinstance(p, Service))
#: False False
