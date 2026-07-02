# class_singleton.py
from typing import Any

class ClassSingleton:
    def __init__(self, klass: type) -> None:
        self.klass = klass
        self.instance: Any = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance

@ClassSingleton
class Foo:
    pass

x = Foo()
y = Foo()
z = Foo()
x.val = "sausage"
y.val = "eggs"
z.val = "spam"
# One cached instance, so x.val is now spam:
print(x.val, x is y is z)
#: spam True
