# classvar_fork.py
from typing import ClassVar

class Base:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        type(self).total += 1  # Looks like Base.total += 1

class Sub(Base):
    pass

Base()
Sub()
Sub()
print(Base.total, Sub.total)
#: 1 3
