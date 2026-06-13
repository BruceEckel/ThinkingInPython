# Singleton/SingletonDecorator.py
from typing import Any


class SingletonDecorator:
    def __init__(self, klass: type) -> None:
        self.klass = klass
        self.instance: Any = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


class Foo:
    pass


foo = SingletonDecorator(Foo)

x = foo()
y = foo()
z = foo()
x.val = 'sausage'
y.val = 'eggs'
z.val = 'spam'
print(x.val)
print(y.val)
print(z.val)
print(x is y is z)
