# singleton_class_variable.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        if SingletonClassVar.__instance is None:
            SingletonClassVar.__instance = object.__new__(cls)
            SingletonClassVar.__instance.val = []
        SingletonClassVar.__instance.val.append(arg)
        return SingletonClassVar.__instance

x = SingletonClassVar("sausage")
y = SingletonClassVar("eggs")
z = SingletonClassVar("spam")
print(x.val, x is y is z, isinstance(x, SingletonClassVar))
#: ['sausage', 'eggs', 'spam'] True True
