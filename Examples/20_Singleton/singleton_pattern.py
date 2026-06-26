# singleton_pattern.py
from typing import Any, ClassVar

class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg: str) -> None:
            self.val = arg

        def __str__(self) -> str:
            return self.val

    instance: ClassVar[Any] = None

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
## sausage
y = OnlyOne('eggs')
print(y)
## eggs
z = OnlyOne('spam')
print(z)
## spam
print(x)
## spam
print(y)
## spam
# Distinct wrappers (x is not y), one shared inner instance:
print(x is y, x.instance is y.instance is z.instance)
## False True
