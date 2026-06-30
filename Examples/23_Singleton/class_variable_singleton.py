# class_variable_singleton.py
from typing import Any, ClassVar

class SingleTone:
    val: Any
    __instance: ClassVar[SingleTone | None] = None

    def __new__(cls, val: Any) -> SingleTone:
        instance = SingleTone.__instance
        if instance is None:
            instance = object.__new__(cls)
            SingleTone.__instance = instance
        instance.val = val
        return instance

x = SingleTone('sausage')
y = SingleTone('eggs')
z = SingleTone('spam')
# Every construction returns the one instance; x.val is now spam:
print(x.val, x is y is z)
#: spam True
