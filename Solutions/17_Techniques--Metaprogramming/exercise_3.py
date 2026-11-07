# exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
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
class CSingleton(metaclass=Singleton):
    pass

a = ASingleton()
#: building ASingleton
c1 = CSingleton()
#: building CSingleton
c2 = CSingleton()
#: reusing CSingleton
print(c1 is c2)
#: True
print(c1 is a)
#: False
