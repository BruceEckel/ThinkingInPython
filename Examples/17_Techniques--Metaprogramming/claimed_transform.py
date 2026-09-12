# claimed_transform.py
from typing import dataclass_transform
from exceptions import expect

@dataclass_transform()
def model[T](cls: type[T]) -> type[T]:
    return cls  # The claim, with nothing behind it

@model
class User:
    name: str
    age: int = 0

# The checker accepts this call:
expect(TypeError, User, "Guido", 30)
#: [TypeError] User() takes no arguments
