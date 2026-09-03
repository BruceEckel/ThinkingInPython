# iterable_class.py
from collections.abc import Iterator
from typing import Any

class IterableMeta(type):
    def __iter__(cls) -> Iterator[Any]:
        return (
            v for k, v in vars(cls).items()
            if not k.startswith("_")
        )

class Color(metaclass=IterableMeta):
    red = "red"
    green = "green"
    blue = "blue"

for c in Color:
    print(c)
#: red
#: green
#: blue
