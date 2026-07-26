# new_singleton.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    instance: ClassVar[__OnlyOne | None] = None

    def __new__(cls) -> Any:  # __new__ is implicitly a staticmethod
        if OnlyOne.instance is None:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

x = OnlyOne()
x.val.append("sausage")
y = OnlyOne()
y.val.append("eggs")
z = OnlyOne()
z.val.append("spam")
# __new__ returns the one instance every time, so all three share val:
print(x.val, x is y is z)
#: ['sausage', 'eggs', 'spam'] True
