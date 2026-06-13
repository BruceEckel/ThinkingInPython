# Singleton/NewSingleton.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self) -> None:
            self.val: str | None = None

        def __str__(self) -> str:
            return repr(self) + str(self.val)

    instance: Any = None

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
y = OnlyOne()
y.val = 'eggs'
print(y)
z = OnlyOne()
z.val = 'spam'
print(z)
print(x)
print(y)
