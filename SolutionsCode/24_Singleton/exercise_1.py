# exercise_1.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    instance: ClassVar[Any] = None  # Nothing built yet

    def __init__(self, arg: str) -> None:
        if OnlyOne.instance is None:
            # Built on first use:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        OnlyOne.instance.val.append(arg)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

x = OnlyOne("sausage")
y = OnlyOne("eggs")
print(x.val, x is y, x.instance is y.instance)
#: ['sausage', 'eggs'] False True
