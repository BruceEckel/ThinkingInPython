# new_vs_init.py
from typing import Any
from display import display_object

class Tag:
    pass

class Meta(type):
    def __new__(mcl, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        # Before creation: these changes take effect
        nmspc["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcl, name, bases, nmspc)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        # No effect: the class is already built
        nmspc["added_in_init"] = 99
        # Effect: this modifies the finished class
        setattr(cls, "patched_in_init", 3.14)

class Demo(metaclass=Meta):
    pass

print("added_in_new:", Demo.added_in_new)            # type: ignore
## added_in_new: 42
print("has Tag base:", Tag in Demo.__bases__)
## has Tag base: True
print("added_in_init present:", hasattr(Demo, "added_in_init"))
## added_in_init present: False
print("patched_in_init present:", hasattr(Demo, "patched_in_init"))
## patched_in_init present: True
display_object(Demo(), dunder=["__new__", "__init__"])
## === Demo ===
## [Attributes]
##   • added_in_new = 42
##   • patched_in_init = 3.14
## [Methods]
##   • __init__(self, /, *args, **kwargs)
##   • __new__(*args, **kwargs)
