# Singleton

A *singleton* is a class with exactly one instance,
reachable from a well-known place.
It is the simplest design pattern,
and in Python it is also the one most often written with far more machinery than it needs.

Before reaching for any classic implementation,
ask the question this part of the book keeps asking:
does the language already solve this?
For the singleton, it does.

## A Module Is Already a Singleton

Python imports each module once and caches it in `sys.modules`.
Every `import` after the first hands back the same module object.
So a module *is* a singleton, and module-level names are a single, shared,
one-and-only-one piece of state.
Put the state in a module:

```python
# config.py
settings: dict[str, str] = {}
```

Then every import of `settings`, from anywhere, hands back the same `dict`.
Mutating it through one import is visible through every other:

```python
# shared_config.py
# A module is imported once and cached in sys.modules, so its globals
# are shared. The settings you import is config's own dict, the same
# object everywhere it is imported.
import config
from config import settings

settings["theme"] = "dark"  # Write through the imported name
print(config.settings)  # The same dict
#: {'theme': 'dark'}
print(config.settings is settings)
#: True
```

No class, no ceremony.
For the large majority of "I need one shared X" cases,
the answer is a module with module-level state or functions.
This is the idiomatic Python singleton, and it is worth trying first.

A test confirms the imported `settings` is `config`'s own dict:

```python
# test_module.py
import config
import shared_config

def test_module_is_singleton() -> None:
    # shared_config did `from config import settings` and wrote to it,
    # mutating config's own dict.
    assert shared_config.settings is config.settings
    assert config.settings["theme"] == "dark"
```

## When You Want a Class: Cache the Instance

Sometimes you do want a class,
but every construction should return the same object.
The simplest way is to hide construction behind a cached factory.
`functools.cache` makes a zero-argument factory return the one instance forever:

```python
# cache_singleton.py
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
#: {'theme': 'dark'}
```

If you need the class itself to hand back one instance from its own constructor,
override `__new__()`, shown below.

A test confirms the cached factory returns the one instance:

```python
# test_cache.py
import cache_singleton

def test_cache_factory_returns_same_instance() -> None:
    assert cache_singleton.settings() is cache_singleton.settings()
```

## The Classic Implementations

*GoF Design Patterns* builds the singleton with more apparatus.
The variations below run from elaborate to simple.
They are worth seeing,
but notice that each does more work than the module or the cached factory above.

The classic approach takes control of creation by delegating to a single instance of a private nested class:

```python
# singleton_pattern.py
from typing import Any, ClassVar

class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg: str) -> None:
            self.val = arg

        def __str__(self) -> str:
            return self.val

    instance: ClassVar[Any] = None

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
#: sausage
y = OnlyOne('eggs')
print(y)
#: eggs
z = OnlyOne('spam')
print(z)
#: spam
print(x)
#: spam
print(y)
#: spam
# Distinct wrappers (x is not y), one shared inner instance:
print(x is y, x.instance is y.instance is z.instance)
#: False True
```

Because the inner class is named with a double underscore,
it is private so the user cannot directly access it.
The outer class controls creation through its constructor.
The first time you create an `OnlyOne` it initializes `instance`;
after that it reuses the one inner object.
Access is delegated through `__getattr__()`.
The distinct `OnlyOne` instances all proxy to the same `__OnlyOne` object.
This works, but it is a lot of code for what a module does on its own.

A variation uses `__new__()`, the method that actually creates an instance,
to return the same object every time:

```python
# new_singleton.py
from typing import Any, ClassVar

class OnlyOne:
    class __OnlyOne:
        def __init__(self) -> None:
            self.val: str | None = None

        def __str__(self) -> str:
            return str(self.val)

    instance: ClassVar[Any] = None

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
#: sausage
y = OnlyOne()
y.val = 'eggs'
print(y)
#: eggs
z = OnlyOne()
z.val = 'spam'
print(z)
#: spam
print(x)
#: spam
print(y)
#: spam
# __new__ returns the one instance every time, so all three are it:
print(x is y is z)
#: True
```

A test confirms `__new__()` hands back the one instance:

```python
# test_new.py
import new_singleton

def test_new_returns_same_instance() -> None:
    assert new_singleton.OnlyOne() is new_singleton.OnlyOne()
```

### Borg: Share State Instead of Identity

Alex Martelli [observed](http://www.aleax.it/Python/5ep.html) that what you usually want is not one *object* but one shared set of *state*.
You can let people create as many objects as they like,
as long as they all share the same data.
He called this the *Borg*^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."],
and it points every instance's `__dict__` at the same storage:

```python
# borg_singleton.py
# Alex Martelli's 'Borg'
from typing import Any, ClassVar

class Borg:
    _shared_state: ClassVar[dict[str, Any]] = {}

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
#: sausage
y = Singleton('eggs')
print(y)
#: eggs
z = Singleton('spam')
print(z)
#: spam
print(x)
#: spam
print(y)
#: spam
# Distinct objects (x is not y), but one shared __dict__:
print(x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: False True
```

This has the same effect as the singleton,
but where the singleton wires one-instance behavior into each class,
*Borg* is reused through inheritance.
It is a genuinely Pythonic idiom when "shared state,
many handles" is what you actually want.

A test confirms the objects differ but share one set of state:

```python
# test_borg.py
import borg_singleton

def test_borg_shares_state_but_not_identity() -> None:
    x = borg_singleton.Singleton("first")
    y = borg_singleton.Singleton("second")
    assert x is not y      # Distinct objects...
    assert x.val == y.val  # ...sharing one set of state
    assert x.val == "second"
```

A simpler version relies on the fact that a class variable has a single shared value:

```python
# class_variable_singleton.py
from typing import Any, ClassVar

class SingleTone:
    val: Any
    __instance: ClassVar[SingleTone | None] = None

    def __new__(cls, val: Any) -> SingleTone:
        instance = SingleTone.__instance
        if instance is None:
            instance = object.__new__(cls)
            SingleTone.__instance = instance
        instance.val = val
        return instance

x = SingleTone('sausage')
print(x.val)
#: sausage
y = SingleTone('eggs')
print(y.val)
#: eggs
z = SingleTone('spam')
print(z.val)
#: spam
# Every construction returns the one instance; x.val is now spam:
print(x.val, x is y is z)
#: spam True
```

A test confirms every construction returns the one instance:

```python
# test_class_variable.py
import class_variable_singleton

def test_class_variable_returns_same_instance() -> None:
    a = class_variable_singleton.SingleTone("a")
    b = class_variable_singleton.SingleTone("b")
    assert a is b
    assert a.val == "b"  # Last write wins on the shared instance
```

### Singleton Class Decorator

You can wrap a class so that calling it returns a cached instance.
This is a *class decorator* (see [Decorators](15_Decorators.md#decorating-classes)):

```python
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
```

Applying `@Singleton` to `Foo` runs `Foo = Singleton(Foo)`,
so the name `Foo` now refers to the decorated instance rather than to the class.
Calling `Foo()` returns the cached instance, which is what we want.
But the name no longer points at a class.
`isinstance(x, Foo)` and subclassing `Foo` no longer work.
The `__new__()` and metaclass versions below keep the name pointing at a real class,
which is the reason to prefer them when you need that.

A test confirms the decorated class returns its cached instance:

```python
# test_decorator.py
import singleton

def test_decorator_returns_same_instance() -> None:
    assert singleton.Foo() is singleton.Foo()
```

### Singleton Using Metaclasses

Finally, a metaclass can intercept construction itself.
Metaclasses are covered in [Metaprogramming](18_Metaprogramming.md#intercepting-instance-creation),
where this same singleton appears next to the simpler hooks that usually replace them.
It is included here for completeness:

```python
# singleton_metaclass.py
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
        return self.val

x = Bar('sausage')
y = Bar('eggs')
z = Bar('spam')
# Each Bar(...) reruns __init__ on the one instance, so val is spam:
print(x)
#: spam
print(y)
#: spam
print(z)
#: spam
print(x is y is z)
#: True
```

A test confirms the metaclass returns the one instance:

```python
# test_metaclass.py
import singleton_metaclass

def test_metaclass_returns_same_instance() -> None:
    assert (singleton_metaclass.Bar("x")
            is singleton_metaclass.Bar("y"))
```

## Which Should You Use?

Use the lightest tool that fits:

- For almost everything, use a *module* with module-level state.
  It is the truest Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`),
  or override `__new__()`.
- If you really want many handles sharing one set of state, use *Borg*.
- The decorator and metaclass versions work,
  but they are more machinery than the problem usually justifies.

The elaborate *GoF Design Patterns* singleton is largely a workaround for languages where a module is not a first-class,
single-instance namespace.
Python has that for free, so most of the ceremony falls away.

## Exercises

1.  `singleton_pattern.py` always creates an object, even if it's never used.
    Modify it to use *lazy initialization*,
    so the singleton object is created only the first time it is needed.
2.  Using `cache_singleton.py` as a starting point,
    create a factory that manages a fixed pool of objects (say, database connections) and hands them out,
    rather than a single instance.
3.  Rewrite one of the class-based singletons above as a module,
    and argue which you would use in real code.
