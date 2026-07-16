# set_name.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"{name}.__set_name__ on {owner.__name__}")
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        via = "class" if obj is None else "instance"
        print(f"{self.name}.__get__ via {via}")
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        print(f"{self.name}.__set__ = {value}")
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()
#: x.__set_name__ on Point
#: y.__set_name__ on Point

p = Point()
p.x = 3
#: x.__set__ = 3
p.y = 4
#: y.__set__ = 4
print(p.x, p.y)
#: x.__get__ via instance
#: y.__get__ via instance
#: 3 4
print(isinstance(Point.x, Field))
#: x.__get__ via class
#: True
