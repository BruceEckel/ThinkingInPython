# claimed_transform.py
from typing import dataclass_transform

@dataclass_transform()
def model[T](cls: type[T]) -> type[T]:
    return cls  # The claim, with nothing behind it

@model
class User:
    name: str
    age: int = 0

try:
    User("Guido", 30)  # The checker accepts this call
except TypeError as e:
    print(e)
#: User() takes no arguments
