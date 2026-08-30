# proxy_interface.py
from abc import ABC, abstractmethod
from typing import override

class Service(ABC):
    @abstractmethod
    def f(self) -> None: ...
    @abstractmethod
    def g(self) -> None: ...

class Proxy:
    def __init__(self, service: Service) -> None:
        self.__service = service
    def f(self) -> None: self.__service.f()
    def g(self) -> None: self.__service.g()

class Complete(Service):
    @override
    def f(self) -> None: print("Complete.f()")
    @override
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    @override
    def f(self) -> None: print("Partial.f()")

p = Proxy(Complete())
p.f()
#: Complete.f()
p.g()
#: Complete.g()
try:
    Proxy(Partial())
except TypeError as e:
    print(str(e).partition(" without")[0])
#: Can't instantiate abstract class Partial
