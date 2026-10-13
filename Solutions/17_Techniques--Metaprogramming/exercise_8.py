# exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        bases += (Tag,)
        super().__init__(name, bases, namespace)

class Demo(metaclass=Meta):
    pass

print(Demo.__bases__)
#: (<class 'object'>,)
print(Tag in Demo.__bases__)
#: False
