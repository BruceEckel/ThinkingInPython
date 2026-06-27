# singleton.py
from typing import Any

class Singleton:
    def __init__(self, klass: type) -> None:
        self.klass = klass
        self.instance: Any = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance

@Singleton
class Foo:
    pass

x = Foo()
y = Foo()
z = Foo()
x.val = 'sausage'
y.val = 'eggs'
z.val = 'spam'
print(x.val)
#: spam
print(y.val)
#: spam
print(z.val)
#: spam
print(x is y is z)
#: True
