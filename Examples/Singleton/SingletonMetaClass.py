# Singleton/SingletonMetaClass.py
from typing import Any


class SingletonMetaClass(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        klass: Any = cls
        original_new = klass.__new__

        def my_new(c: Any, *args: Any, **kwds: Any) -> Any:
            if c.instance is None:
                c.instance = original_new(c)
            return c.instance

        klass.instance = None
        klass.__new__ = staticmethod(my_new)


class Bar(metaclass=SingletonMetaClass):
    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return repr(self) + self.val


x = Bar('sausage')
y = Bar('eggs')
z = Bar('spam')
print(x)
print(y)
print(z)
print(x is y is z)
