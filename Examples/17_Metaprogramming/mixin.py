# mixin.py
class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Derived(metaclass=Base):
    pass

print(Derived.helper())
#: hi
