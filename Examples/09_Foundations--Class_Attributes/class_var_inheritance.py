# class_var_inheritance.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Left.shared, Right.shared)
#: 0 100
# Only affects subclasses that haven't overridden
Base.shared = 9
print(Left.shared, Right.shared)
#: 9 100
# Creates Left's own attribute, doesn't touch Base
Left.shared = 5
print(Base.shared, Left.shared, Right.shared)
#: 9 5 100
