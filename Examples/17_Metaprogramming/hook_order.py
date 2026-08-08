# hook_order.py
from typing import Any

class Watched:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"__set_name__({owner.__name__}, {name})")

class Meta(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> dict[str, Any]:
        print(f"__prepare__ {name}")
        return {}

    def __new__(mcls, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        print(f"__new__ {name} enter")
        cls = super().__new__(mcls, name, bases, nmspc)
        print(f"__new__ {name} exit")
        return cls

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        print(f"__init__ {name}")

def tag[T: type](cls: T) -> T:
    print(f"decorator {cls.__name__}")
    return cls

class Base(metaclass=Meta):
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        print(f"__init_subclass__ {cls.__name__}")
#: __prepare__ Base
#: __new__ Base enter
#: __new__ Base exit
#: __init__ Base

@tag
class Derived(Base):
    field = Watched()
    print("class body")
#: __prepare__ Derived
#: class body
#: __new__ Derived enter
#: __set_name__(Derived, field)
#: __init_subclass__ Derived
#: __new__ Derived exit
#: __init__ Derived
#: decorator Derived
