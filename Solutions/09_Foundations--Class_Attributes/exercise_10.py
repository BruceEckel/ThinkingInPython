# exercise_10.py
from typing import ClassVar

class Base:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        type(self).total += 1

class Sub(Base):
    pass

Base()
print(vars(Sub).get("total"))
#: None
Sub()  # [1]
print(vars(Sub).get("total"))
#: 2
Sub()  # [2]
print(vars(Sub).get("total"))
#: 3
print(Base.total, Sub.total)
#: 1 3

class Counted:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        Counted.total += 1  # Name the class

class SubCounted(Counted):
    pass

Counted()
print(vars(SubCounted).get("total"))
#: None
SubCounted()
print(vars(SubCounted).get("total"))
#: None
SubCounted()
print(vars(SubCounted).get("total"))
#: None
print(Counted.total, SubCounted.total)
#: 3 3
