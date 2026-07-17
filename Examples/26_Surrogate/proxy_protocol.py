# proxy_protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance() against a Protocol
class Service(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...

class Complete:  # Conforms without inheriting Service
    def f(self) -> None: print("Complete.f()")
    def g(self) -> None: print("Complete.g()")

class Partial:  # Missing g()
    def f(self) -> None: print("Partial.f()")

print(isinstance(Complete(), Service))
#: True
print(isinstance(Partial(), Service))
#: False
