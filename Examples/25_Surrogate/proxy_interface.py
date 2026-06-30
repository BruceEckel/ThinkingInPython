# proxy_interface.py
from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def f(self) -> None: ...
    @abstractmethod
    def g(self) -> None: ...

class Complete(Service):
    def f(self) -> None: print("Complete.f()")
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    def f(self) -> None: print("Partial.f()")

Complete().f()
#: Complete.f()
try:
    Partial()
except TypeError as e:
    print(type(e).__name__)
#: TypeError
