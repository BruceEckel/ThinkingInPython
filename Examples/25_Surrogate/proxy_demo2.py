# proxy_demo2.py
# Simple demonstration of the Proxy pattern.
from typing import Any

class Implementation2:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")
    def h(self) -> None:
        print("Implementation.h()")

class Proxy2:
    def __init__(self) -> None:
        self.__implementation = Implementation2()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy2()
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
