# new_singleton.py
from typing import Any, ClassVar

class OnlyOne:
    class __OnlyOne:
        def __init__(self) -> None:
            self.val: str | None = None

        def __str__(self) -> str:
            return str(self.val)

    instance: ClassVar[Any] = None

    def __new__(cls) -> Any:  # __new__ is always a classmethod
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.instance, name, value)

x = OnlyOne()
x.val = 'sausage'
print(x)
#: sausage
y = OnlyOne()
y.val = 'eggs'
print(y)
#: eggs
z = OnlyOne()
z.val = 'spam'
print(z)
#: spam
print(x)
#: spam
print(y)
#: spam
# __new__ returns the one instance every time, so all three are it:
print(x is y is z)
#: True
