# class_variable_singleton.py
from typing import Any

class SingleTone:
    val: Any
    __instance: SingleTone | None = None

    def __new__(cls, val: Any) -> SingleTone:
        instance = SingleTone.__instance
        if instance is None:
            instance = object.__new__(cls)
            SingleTone.__instance = instance
        instance.val = val
        return instance
