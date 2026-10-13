# new_vs_init.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...],
                namespace: dict[str, Any]) -> type:
        # Before creation: these changes take effect
        namespace["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcls, name, bases, namespace)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        # No effect: the class is already built
        namespace["added_in_init"] = 99
        # Effect: this modifies the finished class
        setattr(cls, "patched_in_init", 3.14)

class Built(metaclass=Meta):
    pass

for attr in ("added_in_new", "added_in_init",
             "patched_in_init"):
    print(attr, hasattr(Built, attr))
#: added_in_new True
#: added_in_init False
#: patched_in_init True
print("has Tag base:", Tag in Built.__bases__)
#: has Tag base: True
