# state_demo.py
# Simple demonstration of the State pattern.
from typing import Any

class StateD:
    def __init__(self, imp: Any) -> None:
        self.__implementation = imp
    def change_imp(self, new_imp: Any) -> None:
        self.__implementation = new_imp
    # Delegate calls to the implementation:
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Implementation1:
    def f(self) -> None:
        print("Fiddle de dum, Fiddle de dee,")
    def g(self) -> None:
        print("Eric the half a bee.")
    def h(self) -> None:
        print("Ho ho ho, tee hee hee,")

class Implementation2:
    def f(self) -> None:
        print("We're Knights of the Round Table.")
    def g(self) -> None:
        print("We dance whene'er we're able.")
    def h(self) -> None:
        print("We do routines and chorus scenes")

def run(b: Any) -> None:
    b.f()
    b.g()
    b.h()
    b.g()

b = StateD(Implementation1())
run(b)
b.change_imp(Implementation2())
run(b)
