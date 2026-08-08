# mixin.py
from exceptions import ignore

class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Derived(metaclass=Base):
    pass

print(Derived.helper())
#: hi

with ignore(AttributeError):  # A metamethod: class only
    Derived().helper()  # type: ignore
#: AttributeError("'Derived' object has no attribute 'helper'")
