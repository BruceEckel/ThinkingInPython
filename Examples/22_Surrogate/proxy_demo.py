# proxy_demo.py
# Simple demonstration of the Proxy pattern.

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
    # Pass method calls to the implementation:
    def f(self) -> None: self.__implementation.f()
    def g(self) -> None: self.__implementation.g()
    def h(self) -> None: self.__implementation.h()

p = Proxy()
p.f()
## Implementation.f()
p.g()
## Implementation.g()
p.h()
## Implementation.h()
