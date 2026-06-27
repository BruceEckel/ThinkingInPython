# borg_singleton.py
# Alex Martelli's 'Borg'
from typing import Any, ClassVar

class Borg:
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        Borg.__init__(self)
        self.val = arg

    def __str__(self) -> str:
        return self.val

x = Singleton('sausage')
print(x)
#: sausage
y = Singleton('eggs')
print(y)
#: eggs
z = Singleton('spam')
print(z)
#: spam
print(x)
#: spam
print(y)
#: spam
# Distinct objects (x is not y), but one shared __dict__:
print(x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: False True
