# set_name.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        print(f"{self.name}.__get__({type(obj).__name__})")
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        print(f"{self.name}.__set__({type(obj).__name__}, {value})")
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()

p = Point()
p.x = 3
#: x.__set__(Point, 3)
p.y = 4
#: y.__set__(Point, 4)
print(p.x, p.y)
#: x.__get__(Point)
#: y.__get__(Point)
#: 3 4
print(isinstance(Point.x, Field))
#: x.__get__(NoneType)
#: True
