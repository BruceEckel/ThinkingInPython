# Metaprogramming/Singleton.py
# A Singleton metaclass: intercept instance creation through __call__.
from typing import Any


class Singleton(type):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ASingleton(metaclass=Singleton):
    pass


class BSingleton(metaclass=Singleton):
    pass


a = ASingleton()
b = ASingleton()
assert a is b

c = BSingleton()
d = BSingleton()
assert c is d
assert a is not c
print(a.__class__.__name__, c.__class__.__name__)

""" Output:
ASingleton BSingleton
"""
