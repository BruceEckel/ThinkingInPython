# new_vs_init.py
from typing import Any


class Tag:
    pass


class Meta(type):
    def __new__(mcl, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        # Before creation: these changes take effect.
        nmspc["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcl, name, bases, nmspc)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        # No effect: the class is already built.
        nmspc["added_in_init"] = 99
        # Effect: this modifies the finished class.
        setattr(cls, "patched_in_init", 3.14)


class Demo(metaclass=Meta):
    pass


print("added_in_new:", Demo.added_in_new)            # type: ignore
print("has Tag base:", Tag in Demo.__bases__)
print("added_in_init present:", hasattr(Demo, "added_in_init"))
print("patched_in_init present:", hasattr(Demo, "patched_in_init"))

""" Output:
added_in_new: 42
has Tag base: True
added_in_init present: False
patched_in_init present: True
"""
