# singleton.py
from typing import Any, ClassVar

class Singleton(type):
    # A shared dict of class objects : instances
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        return Singleton._instances[cls]

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
#: ASingleton BSingleton
