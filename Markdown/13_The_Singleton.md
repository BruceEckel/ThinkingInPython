# The Singleton

A *singleton* is a class with exactly one instance, reachable from a well-known
place. It is the simplest design pattern, and in Python it is also the one most
often written with far more machinery than it needs.

Before reaching for any classic implementation, ask the question this part of
the book keeps asking: does the language already solve this? For the singleton,
it does.

## A Module Is Already a Singleton

Python imports each module once and caches it in `sys.modules`. Every `import`
after the first hands back the same module object. So a module *is* a singleton,
and module-level names are a single, shared, one-and-only-one piece of state:

    # config.py
    settings: dict[str, str] = {}

    # anywhere.py
    from config import settings   # the same dict, everywhere

No class, no ceremony. For the large majority of "I need one shared X" cases,
the answer is a module with module-level state or functions. This is the
idiomatic Python singleton, and it is worth trying first.

## When You Want a Class: Cache the Instance

Sometimes you do want a class, but every construction should return the same
object. The simplest way is to hide construction behind a cached factory.
`functools.cache` makes a zero-argument factory return the one instance forever:

```python
# Singleton/cache_singleton.py
# The simplest class-based singleton: a cached factory.
from functools import cache


class Settings:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}


@cache
def settings() -> Settings:
    "Always returns the same Settings instance."
    return Settings()


a = settings()
b = settings()
assert a is b
a.data["theme"] = "dark"
print(b.data)
```

This is small and obvious. If you need the class itself to hand back one instance
from its own constructor, override `__new__`, shown below.

## The Classic Implementations

The *Design Patterns* book builds the singleton with more apparatus. The
variations below run from elaborate to simple. They are worth seeing, but notice
that each does more work than the module or the cached factory above.

The classic approach takes control of creation by delegating to a single
instance of a private nested class:

```python
# Singleton/SingletonPattern.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg: str) -> None:
            self.val = arg

        def __str__(self) -> str:
            return repr(self) + self.val

    instance: Any = None

    def __init__(self, arg: str) -> None:
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne(arg)
        else:
            OnlyOne.instance.val = arg

    def __str__(self) -> str:
        return str(self.instance)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)


x = OnlyOne('sausage')
print(x)
y = OnlyOne('eggs')
print(y)
z = OnlyOne('spam')
print(z)
print(x)
print(y)
print(repr(x))
print(repr(y))
print(repr(z))
```

Because the inner class is named with a double underscore, it is private so the
user cannot directly access it. The outer class controls creation through its
constructor. The first time you create an `OnlyOne` it initializes `instance`;
after that it just reuses the one inner object. Access is delegated through
`__getattr__()`. The distinct `OnlyOne` instances all proxy to the same
`__OnlyOne` object. This works, but it is a lot of code for what a module does
on its own.

A variation uses `__new__`, the method that actually creates an instance, to
return the same object every time:

```python
# Singleton/NewSingleton.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self) -> None:
            self.val: str | None = None

        def __str__(self) -> str:
            return repr(self) + str(self.val)

    instance: Any = None

    def __new__(cls) -> Any:  # __new__ is always a classmethod
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.instance, name, value)


x = OnlyOne()
x.val = 'sausage'
print(x)
y = OnlyOne()
y.val = 'eggs'
print(y)
z = OnlyOne()
z.val = 'spam'
print(z)
print(x)
print(y)
```

### Borg: Share State Instead of Identity

Alex Martelli [observed](http://www.aleax.it/Python/5ep.html) that what you
usually want is not one *object* but one shared set of *state*. You can let
people create as many objects as they like, as long as they all share the same
data. He called this the *Borg*^[From the television show *Star Trek: The Next
Generation*. The Borg are a hive-mind collective: "we are all one."], and it
points every instance's `__dict__` at the same storage:

```python
# Singleton/BorgSingleton.py
# Alex Martelli's 'Borg'
from typing import Any


class Borg:
    _shared_state: dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        Borg.__init__(self)
        self.val = arg

    def __str__(self) -> str:
        return self.val


x = Singleton('sausage')
print(x)
y = Singleton('eggs')
print(y)
z = Singleton('spam')
print(z)
print(x)
print(y)
print(repr(x))
print(repr(y))
print(repr(z))
```

This has the same effect as the singleton, but where the singleton wires
one-instance behavior into each class, *Borg* is reused through inheritance. It
is a genuinely Pythonic idiom when "shared state, many handles" is what you
actually want.

A simpler version relies on the fact that a class variable has a single shared
value:

```python
# Singleton/ClassVariableSingleton.py
from typing import Any


class SingleTone:
    val: Any
    __instance: "SingleTone | None" = None

    def __new__(cls, val: Any) -> "SingleTone":
        instance = SingleTone.__instance
        if instance is None:
            instance = object.__new__(cls)
            SingleTone.__instance = instance
        instance.val = val
        return instance
```

### As a Class Decorator

You can wrap a class so that calling it returns a cached instance. This is a
*class decorator* (see [the Decorators chapter](08_Decorators.md)):

```python
# Singleton/Singleton.py
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
print(y.val)
print(z.val)
print(x is y is z)
```

Applying `@Singleton` to `Foo` runs `Foo = Singleton(Foo)`, so
the name `Foo` now refers to the decorated instance rather than to the class.
Calling `Foo()` returns the cached instance, which is what we want. But the name
no longer points at a class. `isinstance(x, Foo)` and subclassing `Foo` no longer
work. The `__new__` and metaclass versions below keep the name pointing at a real
class, which is the reason to prefer them when you need that.

### As a Metaclass

Finally, a metaclass can intercept construction itself. Metaclasses are covered
in [the Metaprogramming chapter](09_Metaprogramming.md), where this same singleton appears next to the
simpler hooks that usually replace them. It is included here for completeness:

```python
# Singleton/SingletonMetaClass.py
from typing import Any


class SingletonMetaClass(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        klass: Any = cls
        original_new = klass.__new__

        def my_new(c: Any, *args: Any, **kwds: Any) -> Any:
            if c.instance is None:
                c.instance = original_new(c)
            return c.instance

        klass.instance = None
        klass.__new__ = staticmethod(my_new)


class Bar(metaclass=SingletonMetaClass):
    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return repr(self) + self.val


x = Bar('sausage')
y = Bar('eggs')
z = Bar('spam')
print(x)
print(y)
print(z)
print(x is y is z)
```

## Which Should You Use?

Reach for the lightest tool that fits:

- For almost everything, use a *module* with module-level state. It is the
  truest Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`), or
  override `__new__`.
- If you really want many handles sharing one set of state, use *Borg*.
- The decorator and metaclass versions work, but they are more machinery than
  the problem usually justifies.

The elaborate GoF singleton is largely a workaround for languages where a module
is not a first-class, single-instance namespace. Python has that for free, so
most of the ceremony falls away.

## Exercises

1.  `SingletonPattern.py` always creates an object, even if it's never used.
    Modify it to use *lazy initialization*, so the singleton object is created
    only the first time it is needed.
2.  Using `cache_singleton.py` as a starting point, create a factory that
    manages a fixed pool of objects (say, database connections) and hands them
    out, rather than a single instance.
3.  Rewrite one of the class-based singletons above as a module, and argue which
    you would use in real code.
