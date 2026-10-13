# state_demo.py
from typing import Any, Protocol
from state_surrogate import Surrogate

class Behavior(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...
    def h(self) -> None: ...

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

def run(surrogate: Any) -> None:
    surrogate.f()
    surrogate.g()
    surrogate.h()
    surrogate.g()

first: Behavior = Implementation1()
second: Behavior = Implementation2()
surrogate = Surrogate(first)
run(surrogate)
#: Fiddle de dum, Fiddle de dee,
#: Eric the half a bee.
#: Ho ho ho, tee hee hee,
#: Eric the half a bee.
surrogate.change_to(second)
run(surrogate)
#: We're Knights of the Round Table.
#: We dance whene'er we're able.
#: We do routines and chorus scenes
#: We dance whene'er we're able.
