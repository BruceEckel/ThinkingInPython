# mixin.py
from exceptions import expected

class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Sub(metaclass=Base):
    pass

print(Sub.helper())
#: hi

with expected(AttributeError):  # A metamethod: class only
    Sub().helper()  # type: ignore
#: [AttributeError] 'Sub' object has no attribute 'helper'
