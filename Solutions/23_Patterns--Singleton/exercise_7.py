# exercise_7.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        if SingletonClassVar.__instance is None:
            SingletonClassVar.__instance = (
                object.__new__(cls))
        return SingletonClassVar.__instance

    def __init__(self, arg: str) -> None:
        print(f"__init__({arg})")
        self.val = [arg]

x = SingletonClassVar("sausage")
#: __init__(sausage)
y = SingletonClassVar("eggs")
#: __init__(eggs)
z = SingletonClassVar("spam")
#: __init__(spam)
print(x.val, x is y is z)
#: ['spam'] True
