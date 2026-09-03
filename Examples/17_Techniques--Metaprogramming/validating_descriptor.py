# validating_descriptor.py
from exceptions import ignore

class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.storage = f"_{name}"

    def __get__(self, obj: object,
                owner: type | None = None) -> float:
        return getattr(obj, self.storage)

    def __set__(self, obj: object, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{value} is not positive")
        setattr(obj, self.storage, value)

class Rectangle:
    width = Positive()
    height = Positive()

    def __init__(
        self, width: float, height: float
    ) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

r = Rectangle(3.0, 4.0)
print(r.area())
#: 12.0

with ignore(ValueError):
    r.width = -1.0
#: ValueError('-1.0 is not positive')

print(r.area())
#: 12.0
