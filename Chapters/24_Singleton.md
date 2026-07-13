# Singleton

A *singleton* is the simplest design pattern: a class with exactly one instance.
Before using a classic implementation,
ask whether the language already provides a solution.
For the singleton, Python does.

## A Module Is Already a Singleton

Python imports each module once and caches it in `sys.modules`.
Every `import` after the first produces the same module object.
A module is a singleton, and module-level names are a single, shared,
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
# A module's globals are shared.
from config import settings

settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
```

No class, no ceremony.
For the large majority of singleton needs,
the module approach solves the problem.
The idiomatic Python singleton is worth trying first.

## When You Want a Class: Cache the Instance

Sometimes you do want a class,
but every construction should return the same object.
The simplest way is to hide construction behind a cached factory.
A cached factory applies `functools.cache` to a *constructor function*,
an ordinary function whose only job is to build and return an instance of a class,
standing in for a direct call to it.
`functools.cache` *memoizes* a function.
The first call with a given set of arguments runs the function and stores the result.
Every repeat call with those arguments returns the stored result.
A constructor function with no arguments has only one possible call,
so caching it constructs the instance once and returns that same object forever:

```python
# cached_factory_singleton.py
from functools import cache

class Settings:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

@cache
def settings() -> Settings:
    return Settings()

a = settings()
b = settings()
assert a is b
a.data["theme"] = "dark"
print(b.data)
#: {'theme': 'dark'}
```

```python
# test_cache.py
import cached_factory_singleton

def test_cache_factory_returns_same_instance() -> None:
    assert (cached_factory_singleton.settings() is
        cached_factory_singleton.settings())
```

If you need the class to hand back one instance from its own constructor,
override `__new__()`, shown below.

Modules and cached factories should cover your singleton needs.
The rest of this chapter exists only because it demonstrates interesting techniques and insights.

## The Classic Implementations

*GoF Design Patterns* builds the singleton with more apparatus,
because it addresses languages like C++ and Java.
The variations shown here are worth understanding,
but notice that each does more work than the module or the cached factory above.

The classic approach takes control of creation by delegating to a single instance of a private nested class.

### Lazy Creation

This version builds the inner instance on the first call:

```python
# singleton_pattern.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    instance: ClassVar[Any] = None

    def __init__(self, arg: str) -> None:
        if OnlyOne.instance is None:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        OnlyOne.instance.val.append(arg)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

x = OnlyOne("sausage")
print(x.val)
#: ['sausage']
y = OnlyOne("eggs")
print(y.val)
#: ['sausage', 'eggs']
z = OnlyOne("spam")
print(z.val)
#: ['sausage', 'eggs', 'spam']
# Distinct wrappers (x is not y), one shared inner instance:
print(x is y, x.instance is y.instance is z.instance)
#: False True
```

Because the inner class's name starts with a double underscore,
Python's compiler rewrites it to `_OnlyOne__OnlyOne` wherever it appears inside `OnlyOne`'s body,
a rewriting called *name mangling* (see [Testing](11_Testing.md#white-box-and-black-box-tests)).
`OnlyOne.__OnlyOne`, written from outside the class,
names an attribute that was never stored under that spelling,
so it fails at runtime with `AttributeError`, not at type-checking time.
The outer class controls creation through its constructor.
The first time you create an `OnlyOne` it initializes `instance`.
After that it reuses the one inner object,
and each construction appends its argument to that object's shared list.
`__getattr__()` delegates access.
The distinct `OnlyOne` instances all proxy to the same `__OnlyOne` object.
It is *lazy*.
It builds the inner object on the first call,
which is why it needs the `None` sentinel and the `if` guard.

### Eager Creation

When the object needs nothing from that first call,
you can create the inner instance *eagerly* in the class body instead,
which removes the sentinel and the guard:

```python
# singleton_eager.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    # Created once, when the class is defined:
    instance: ClassVar[Any] = __OnlyOne()

    def __init__(self, arg: str) -> None:
        OnlyOne.instance.val.append(arg)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

x = OnlyOne("sausage")
y = OnlyOne("eggs")
# Distinct wrappers (x is not y), one shared inner list:
print(x.val, x is y, x.instance is y.instance)
#: ['sausage', 'eggs'] False True
```

The bare `__OnlyOne()` works because the nested class is already defined at that point in the body.
The qualified `OnlyOne.__OnlyOne()` would fail,
because the name `OnlyOne` stays unbound until its own class body finishes running.

The two differ only in *when* they create the inner object.
The lazy form defers it to the first `OnlyOne(...)` call,
so it can wait for data not available at import time,
but it carries the sentinel and the guard,
and two threads racing on that first call can both see `None`.
The eager form creates the object once, at module import: no sentinel, no guard,
and no race, at the cost of building it whether or not anything uses it.

Either way, this is a lot of code for what a module does on its own.

### Overriding `__new__`

A variation uses `__new__()`, the method that actually creates an instance,
to return the same object every time:

```python
# new_singleton.py
from dataclasses import dataclass
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: str | None = None

    instance: ClassVar[Any] = None

    def __new__(cls) -> Any:  # __new__ is implicitly a staticmethod
        if OnlyOne.instance is None:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

x = OnlyOne()
x.val = "sausage"
y = OnlyOne()
y.val = "eggs"
z = OnlyOne()
z.val = "spam"
# __new__ returns the one instance every time, so x.val is now spam:
print(x.val, x is y is z)
#: spam True
```

```python
# test_new.py
import new_singleton

def test_new_returns_same_instance() -> None:
    assert new_singleton.OnlyOne() is new_singleton.OnlyOne()
```

Because `__new__()` returns the inner `__OnlyOne` object,
that is what `OnlyOne()` hands back, so `x` is the shared instance itself,
not a wrapper around it.
No delegating `__getattr__()` or `__setattr__()` methods exist here.
Attribute access goes straight to the one object.

### Borg: Share State Instead of Identity

[Alex Martelli observes](http://www.aleax.it/Python/5ep.html) that what you usually want is not one *object* but one shared set of *state*.
You can let people create as many objects as they like,
as long as they all share the same data.
He called this the *Borg*^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."],
and it points every instance's `__dict__` at the same storage:

![x, y, and z are three distinct objects, but every __dict__ points at the same _shared_state, so the last write wins for all three](_images/borg_shared_state)

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

x = Singleton("sausage")
y = Singleton("eggs")
z = Singleton("spam")
# Last write wins on the shared state; distinct objects, one __dict__:
print(x.val, x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: spam False True
```

This has the same effect as the singleton,
but where the singleton wires one-instance behavior into each class,
you reuse *Borg* through inheritance.

Unlike the nested-class examples above,
`Singleton` should not be a `@dataclass`.
Making it one still runs, but it quietly stops being a `Borg`.
The shared state depends on `Borg.__init__` rebinding `self.__dict__` to `_shared_state`.
A dataclass generates its own `__init__` that assigns the fields and [never calls the base `__init__`](12_Data_Classes_as_Types.md#dataclass-inheritance),
so `self.__dict__` is never rebound and each instance keeps its own state.
Moving the rebinding into `__post_init__` does not help either.
It runs after `__init__` assigns the fields, so it discards them.
The hand-written `__init__` is what makes the shared state work,
and silently losing the sharing is worse than failing outright.

Testing confirms the objects differ but share one set of state:

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

A simpler version relies on a class variable holding a single shared value:

```python
# class_variable_singleton.py
from typing import Any, ClassVar

class CVSingleton:
    val: Any
    __instance: ClassVar[CVSingleton | None] = None

    def __new__(cls, val: Any) -> CVSingleton:
        instance = CVSingleton.__instance
        if instance is None:
            instance = object.__new__(cls)
            CVSingleton.__instance = instance
        instance.val = val
        return instance

x = CVSingleton("sausage")
y = CVSingleton("eggs")
z = CVSingleton("spam")
# Every construction returns the one instance; x.val is now spam:
print(x.val, x is y is z)
#: spam True
```

```python
# test_class_variable.py
import class_variable_singleton

def test_class_variable_returns_same_instance() -> None:
    a = class_variable_singleton.CVSingleton("a")
    b = class_variable_singleton.CVSingleton("b")
    assert a is b
    assert a.val == "b"  # Last write wins on the shared instance
```

### Singleton Classes

You can wrap a class so that calling it returns a cached instance.
This is a *class decorator* (see [Decorators](14_Decorators.md#decorating-classes)):

```python
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
```

```python
# test_decorator.py
import class_singleton

def test_decorator_returns_same_instance() -> None:
    assert class_singleton.Foo() is class_singleton.Foo()
```

Applying `@ClassSingleton` to `Foo` runs `Foo = ClassSingleton(Foo)`,
so the name `Foo` now refers to the decorated instance rather than to the class.
Calling `Foo()` returns the cached instance, which is what we want.
But the name no longer points at a class.
`isinstance(x, Foo)` and subclassing `Foo` no longer work.
The `__new__()` versions above and the metaclass version below keep the name pointing at a real class,
which is the reason to prefer them when you need that.

### Singleton Using Metaclasses

Finally, a metaclass can intercept construction itself.
[Here](17_Metaprogramming.md#intercepting-instance-creation),
a similar metaclass singleton appears next to the simpler hooks that usually replace it.
It appears here for completeness:

```python
# singleton_metaclass.py
from collections.abc import Callable
from typing import Any

class SingletonMetaClass(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        klass: Any = cls
        original_new: Callable[..., Any] = klass.__new__

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

x = Bar("sausage")
y = Bar("eggs")
z = Bar("spam")
# Each Bar(...) reruns __init__ on the one instance, so val is spam:
print(x, x is y is z)
#: spam True
```

```python
# test_singleton_metaclass.py
import singleton_metaclass

def test_metaclass_returns_same_instance() -> None:
    assert (singleton_metaclass.Bar("x")
            is singleton_metaclass.Bar("y"))
```

## Which Should You Use?

Use the lightest tool that fits:

- For almost everything, use a *module* with module-level state.
  It is the default Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`),
  or override `__new__()`.
- If you really want many handles sharing one set of state, use *Borg*.
- The decorator and metaclass versions work,
  but they are more machinery than the problem usually justifies.

The elaborate *GoF Design Patterns* singleton is largely a workaround for languages where a module is not a first-class,
single-instance namespace.
Python has that already, so most of the ceremony falls away.

## Exercises

1.  `singleton_eager.py` always creates its inner object,
    even if nothing ever uses it.
    Modify it to use *lazy initialization*,
    then compare your result with `singleton_pattern.py`.
2.  Using `cached_factory_singleton.py` as a starting point,
    create a factory that manages a fixed pool of objects (say, database connections) and hands them out,
    rather than a single instance.
3.  Rewrite one of the class-based singletons above as a module,
    and argue which you would use in real code.
