# exercise_2.py
from typing import ClassVar

class Base:
    shared: ClassVar[int] = 0

class Left(Base):
    pass

class Middle(Base):
    pass

class Right(Base):
    shared = 100  # Its own class attr, separate from Base's

print(Left.shared, Middle.shared, Right.shared)
#: 0 0 100
Base.shared = 9
print(Left.shared, Middle.shared, Right.shared)
#: 9 9 100
Left.shared = 5
print(Base.shared, Left.shared, Middle.shared, Right.shared)
#: 9 5 9 100
