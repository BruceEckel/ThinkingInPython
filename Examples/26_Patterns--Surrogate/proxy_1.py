# proxy_1.py

class Proxy:
    def __init__(self, impl: Implementation) -> None:
        self.__implementation = impl
    # Pass method calls to the implementation:
    def f(self) -> None: self.__implementation.f()
    def g(self) -> None: self.__implementation.g()

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")

p = Proxy(Implementation())
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
