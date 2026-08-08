# proxy_interface.py
from abc import ABC, abstractmethod
from typing import override

class Service(ABC):
    @abstractmethod
    def f(self) -> None: ...
    @abstractmethod
    def g(self) -> None: ...

class Complete(Service):
    @override
    def f(self) -> None: print("Complete.f()")
    @override
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    @override
    def f(self) -> None: print("Partial.f()")

class Proxy:
    def __init__(self, service: Service) -> None:
        self.__service = service
    def f(self) -> None: self.__service.f()
    def g(self) -> None: self.__service.g()

p = Proxy(Complete())
p.f()
#: Complete.f()
p.g()
#: Complete.g()
try:
    Partial()
except TypeError as e:
    print(type(e).__name__)
#: TypeError
