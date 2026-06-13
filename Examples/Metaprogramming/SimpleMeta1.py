# Metaprogramming/SimpleMeta1.py
# Writing a metaclass and applying it with the `metaclass=` keyword.
from typing import Any


class SimpleMeta1(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")


class Simple1(metaclass=SimpleMeta1):
    def foo(self) -> None: pass

    @staticmethod
    def bar() -> None: pass


simple = Simple1()
print([m for m in dir(simple) if not m.startswith("__")])
# A method injected by the metaclass:
print(simple.uses_metaclass())  # type: ignore

""" Output:
['bar', 'foo', 'uses_metaclass']
Yes!
"""
