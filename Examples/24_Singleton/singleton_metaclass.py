# singleton_metaclass.py
from collections.abc import Callable
from typing import Any

class SingletonMetaClass(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        klass: Any = cls
        original_new: Callable[..., Any] = klass.__new__

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
        return self.val

x = Bar("sausage")
y = Bar("eggs")
z = Bar("spam")
# Each Bar(...) reruns __init__ on the one instance, so val is spam:
print(x, x is y is z)
#: spam True
