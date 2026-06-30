# singleton_eager.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    # Created once, when the class is defined:
    instance: ClassVar[Any] = __OnlyOne()

    def __init__(self, arg: str) -> None:
        OnlyOne.instance.val.append(arg)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

x = OnlyOne('sausage')
print(x.val)
#: ['sausage']
y = OnlyOne('eggs')
print(y.val)
#: ['sausage', 'eggs']
# Distinct wrappers (x is not y), one shared inner instance:
print(x is y, x.instance is y.instance)
#: False True
