# new_singleton.py
from dataclasses import dataclass
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: str | None = None

    instance: ClassVar[Any] = None

    def __new__(cls) -> Any:  # __new__ is always a classmethod
        if OnlyOne.instance is None:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

x = OnlyOne()
x.val = 'sausage'
print(x.val)
#: sausage
y = OnlyOne()
y.val = 'eggs'
print(y.val)
#: eggs
z = OnlyOne()
z.val = 'spam'
print(z.val)
#: spam
print(x.val)
#: spam
print(y.val)
#: spam
# __new__ returns the one instance every time, so all three are it:
print(x is y is z)
#: True
