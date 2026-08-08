# proxy_2.py
from typing import Any

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")
    def h(self) -> None:
        print("Implementation.h()")

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Implementation()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy()
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
