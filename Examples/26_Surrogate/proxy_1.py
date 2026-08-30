# proxy_1.py

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Implementation()
    # Pass method calls to the implementation:
    def f(self) -> None: self.__implementation.f()
    def g(self) -> None: self.__implementation.g()

p = Proxy()
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
