# exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ASingleton(metaclass=Singleton):
    pass
class CSingleton(metaclass=Singleton):
    pass

a = ASingleton()
c1 = CSingleton()
c2 = CSingleton()
print(c1 is c2)
#: True
print(c1 is a)
#: False
