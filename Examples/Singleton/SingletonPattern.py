# Singleton/SingletonPattern.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg: str) -> None:
            self.val = arg

        def __str__(self) -> str:
            return repr(self) + self.val

    instance: Any = None

    def __init__(self, arg: str) -> None:
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne(arg)
        else:
            OnlyOne.instance.val = arg

    def __str__(self) -> str:
        return str(self.instance)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)


x = OnlyOne('sausage')
print(x)
y = OnlyOne('eggs')
print(y)
z = OnlyOne('spam')
print(z)
print(x)
print(y)
print(repr(x))
print(repr(y))
print(repr(z))
