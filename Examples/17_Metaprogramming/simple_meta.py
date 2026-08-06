# simple_meta.py
from typing import Any
from display import display_object

class SimpleMeta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")

class Simple(metaclass=SimpleMeta):
    def foo(self) -> None: pass

    @staticmethod
    def bar() -> None: pass

display_object(Simple)
#: [Attributes]
#:   None
#: [Methods]
#:   • bar() -> None
#:   • foo(self) -> None
#:   • uses_metaclass(self)
print(Simple().uses_metaclass())  # type: ignore
#: Yes!
