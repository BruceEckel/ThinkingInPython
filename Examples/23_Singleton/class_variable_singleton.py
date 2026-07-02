# class_variable_singleton.py
from typing import Any, ClassVar

class CVSingleton:
    val: Any
    __instance: ClassVar[CVSingleton | None] = None

    def __new__(cls, val: Any) -> CVSingleton:
        instance = CVSingleton.__instance
        if instance is None:
            instance = object.__new__(cls)
            CVSingleton.__instance = instance
        instance.val = val
        return instance

x = CVSingleton("sausage")
y = CVSingleton("eggs")
z = CVSingleton("spam")
# Every construction returns the one instance; x.val is now spam:
print(x.val, x is y is z)
#: spam True
