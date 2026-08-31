# mixin.py
from exceptions import ignore

class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Sub(metaclass=Base):
    pass

print(Sub.helper())
#: hi

with ignore(AttributeError):  # A metamethod: class only
    Sub().helper()  # type: ignore
#: AttributeError("'Sub' object has no attribute 'helper'")
