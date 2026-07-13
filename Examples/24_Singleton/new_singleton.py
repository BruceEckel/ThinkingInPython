# new_singleton.py
from dataclasses import dataclass
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: str | None = None

    instance: ClassVar[Any] = None

    def __new__(cls) -> Any:  # __new__ is implicitly a staticmethod
        if OnlyOne.instance is None:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

x = OnlyOne()
x.val = "sausage"
y = OnlyOne()
y.val = "eggs"
z = OnlyOne()
z.val = "spam"
# __new__ returns the one instance every time, so x.val is now spam:
print(x.val, x is y is z)
#: spam True
