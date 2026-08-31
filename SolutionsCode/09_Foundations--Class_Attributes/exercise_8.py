# exercise_8.py
from typing import ClassVar

class Base:
    shared: ClassVar[list[int]] = []

class Left(Base):
    pass

class Right(Base):
    pass

Left.shared.append(1)
Right.shared.append(2)
print(Base.shared, Left.shared, Right.shared)
#: [1, 2] [1, 2] [1, 2]
print(Left.shared is Base.shared)
#: True

class Base2:
    shared: ClassVar[list[int]] = []

class Left2(Base2):
    pass

class Right2(Base2):
    shared = []  # Its own list, separate from Base2's

Left2.shared.append(1)
Right2.shared.append(2)
print(Base2.shared, Left2.shared, Right2.shared)
#: [1] [1] [2]
