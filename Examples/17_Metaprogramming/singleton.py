# singleton.py
from typing import Any, ClassVar

class Singleton(type):
    # A shared dict of class objects : instances
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            print(f"building {cls.__name__}")
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        else:
            print(f"reusing {cls.__name__}")
        return Singleton._instances[cls]

class ASingleton(metaclass=Singleton):
    pass

class BSingleton(metaclass=Singleton):
    pass

a = ASingleton()
#: building ASingleton
b = ASingleton()
#: reusing ASingleton
assert a is b

c = BSingleton()
#: building BSingleton
d = BSingleton()
#: reusing BSingleton
assert c is d
assert a is not c
