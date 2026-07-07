# exercise_2.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = "_" + name

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()
    z = Field()

p = Point()
p.x = 3
p.y = 4
p.z = 9
print(p.x, p.y, p.z)
#: 3 4 9
print(p.__dict__)
#: {'_x': 3, '_y': 4, '_z': 9}
