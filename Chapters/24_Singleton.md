# Singleton

A *singleton* is the simplest design pattern: a class with exactly one instance.
Before using a classic implementation,
ask whether the language already provides a solution.
For the singleton, Python does.

## A Module Is Already a Singleton

Python imports each module once and caches it in `sys.modules`.
Every `import` after the first produces the same module object.
A module is a singleton, and anything defined at module level is shared,
with one copy for the whole program.
Put the state in a module:

```python
# config.py
settings: dict[str, str] = {}
```

Then every import of `settings`, from anywhere, hands back the same `dict`.
Mutating it through one import is visible through every other:

```python
# shared_config.py
from config import settings

settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
```

No class, no ceremony.
For the majority of singleton needs, the module approach solves the problem.

Mutation is what makes the sharing work.
Rebinding is the mistake that quietly ends it.
`from config import settings` gives your module its own name for the same `dict` object named by `config.settings`.
Mutating through your name, `settings["theme"] = "dark"`,
changes that shared object, so every module sees it.
But `settings = {}` in your module rebinds only your module's name,
and the two modules silently diverge:
`config.settings` still holds the old dict,
while your code now talks to a private one.
To replace the whole value, go through the module: `import config`,
then `config.settings = {...}`.
Mutate through any name.
Rebind only through the module.

## When You Want a Class, Cache the Instance

Sometimes you do want a class,
but every construction should return the same object.
The simplest solution is to hide construction behind a cached factory.
This applies `functools.cache` to a *constructor function*,
which is an ordinary function whose only job is to build and return an instance of a class.
It stands in for a direct call to the class constructor.

`functools.cache` *memoizes* a function.
The first call with a given set of arguments runs the function and stores the result.
Every repeat call with those arguments returns the stored result.
A constructor function with no arguments has only one possible call,
so caching it constructs the instance once and returns that same object forever:

```python
# cached_factory_singleton.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings() -> Settings:
    return Settings()

a = settings()
b = settings()
assert a is b
a.data["theme"] = "dark"
print(b)
#: Settings(data={'theme': 'dark'})
```

You can't prevent a caller from writing `Settings()` and getting a second instance.
Naming the class `_Settings` marks it internal and keeps it out of `from module import *`,
which is the extent that Python offers.
A second underscore is not a stronger version of that.
At module level nothing is mangled, so it buys no privacy,
and it breaks any reference written inside a class body,
which rewrites `m.__Settings` into a lookup for `_TheClass__Settings`.

This listing keeps the bare name for a reason that outlasts the convention.
`settings()` returns a `Settings`,
so the class already appears in the module's public signature.
A caller who annotates the result must write that name,
and a type outsiders must name is not private, whatever it starts with.
Only if the type never left the module would we use `_Settings`.

Two stronger-looking moves fail the same way.
Deleting the name after building the instance leaves the class reachable,
because `type(settings())` hands it back.
Defining the class inside `settings()` also looks airtight,
and `@cache` runs that body only once,
so there is exactly one instance and no module-level name at all.
`type(settings())` recovers it anyway.

Nesting costs the return annotation as well.
Quoting the name, `def settings() -> "Settings"`, is the obvious approach.
It parses and runs because an annotation is evaluated only when something reads it.
A clean run is therefore no evidence, since nothing has looked the name up yet.
When something does look, it searches the scope containing the function,
not the function's own locals, and the class is not there.
A checker reports an unresolved reference,
and `inspect.get_annotations(eval_str=True)` raises a `NameError`.
The signature must name something reachable, which means a `Protocol`.

Privacy in Python is advice, not enforcement.
An underscore asks callers to stay out, and nothing makes them.
[Rethinking Objects](20_Rethinking_Objects.md#encapsulation-leaks)
makes the same case about hidden data,
where a getter hands back a reference to the internals it was meant to protect.
It also turns out that the reachable class is useful when a test needs a fresh,
uncached `Settings`.

Three implementation notes:

1. A singleton is shared state, and shared state leaks between tests.
   The cached factory has an escape hatch the classic forms lack:
   `settings.cache_clear()` discards the instance, so each test can start fresh.

2. Every lazy singleton has a first-call race under threads.
   Concurrent first calls can each run the constructor,
   and each caller can end up holding a different object,
   with only one of them staying in the cache.
   This is not a narrow window.
   Eight threads calling `settings()` at once,
   with a constructor slow enough to widen it,
   ran that constructor eight times and handed back eight different objects.
   When threads can arrive before the singleton exists,
   create it eagerly instead: call `settings()` once at import time,
   or use the module form, which the import system builds exactly once.

3. A [lock](19_Concurrency.md#locks) is the other fix for that race,
   and not the obvious one.
   Wrapping the cached function's body in a `threading.Lock` changes nothing,
   because every thread has already missed the cache before reaching the lock.
   They serialize, each still builds an object,
   and the cache keeps whichever finished last.
   The check must happen inside the lock, shown in the listing below.

`@cache` is gone, because it is no longer what makes the object single:

```python
# locked_settings.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

_lock: Final[threading.Lock] = threading.Lock()
_instance: Settings | None = None

def settings() -> Settings:
    global _instance
    with _lock:
        if _instance is None:
            _instance = Settings()
    return _instance

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}))
#: 1
```

In `settings()`, only one of the two module-level names is declared `global`.
This is the chapter's opening distinction seen from inside a function.
`global` governs rebinding, not use.
`with _lock:` only looks the name up,
even though acquiring and releasing genuinely changes that lock's state,
from unlocked to locked and back.
Changing an object is not rebinding a name.
`_instance` differs because the function assigns to it.
Python decides at compile time that a name a function assigns anywhere is local everywhere in that function,
so without the `global` declaration,
`if _instance is None` would read an unassigned local and raise `UnboundLocalError`.
Mutate through any name.
Declare only what you rebind.

One thread finds `_instance` empty and builds it.
The rest wait on the lock, and each finds `_instance` already filled.
The eight-thread race that produced eight objects from the cached version produces one here,
which the printed count confirms.
The sleep stands in for a constructor that does real work,
such as opening a file or a connection.
Without it, the cached version showed no duplicates across twenty trials,
which is the more dangerous case.
A window too narrow to reproduce is still a window.

Every call now acquires the lock,
including the thousands that arrive long after the object exists.
That is the price of laziness under threads.
Eager creation is a better answer when the object can be built at import time.

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

    instance: ClassVar[__OnlyOne | None] = None

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
Python's compiler rewrites it to `_OnlyOne__OnlyOne` wherever it appears inside `OnlyOne`'s body.
This is [name mangling](11_Testing.md#white-box-and-black-box-tests).
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
    instance: ClassVar[__OnlyOne] = __OnlyOne()

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

    instance: ClassVar[__OnlyOne | None] = None

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

A rule governs what happens after `__new__()`:
Python calls `__init__()` only when `__new__()` returns an instance of the class being constructed.
Here it returns something else, the inner object, so no `__init__()` ever runs.
That has a second consequence: `x` is not an `OnlyOne` at all,
so `isinstance(x, OnlyOne)` is `False`.
The metaclass version at the end of this chapter returns the class's own instance,
which puts it on the other side of the rule,
with a behavior worth comparing when you get there.

### One Instance in a Class Variable

The nested private class is not required.
This version keeps the single instance in a class variable and builds it,
when needed, out of the class being constructed:

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

`object.__new__(cls)` builds an instance of `CVSingleton` rather than a foreign object,
which lands this version on the far side of the rule from `new_singleton.py`.
`isinstance(x, CVSingleton)` is `True`,
and if the class defined an `__init__()`,
Python would run it on the shared instance after every construction.
`CVSingleton` defines none, and assigns `val` inside `__new__()` instead,
which is why the last construction's value is the one that survives.

### Borg: Share State Instead of Identity

[Alex Martelli observes](http://www.aleax.it/Python/5ep.html)
that what you usually want is not one *object* but one shared set of *state*.
You can let people create as many objects as they like,
as long as they all share the same data.
He called this the *Borg*^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."],
and it points every instance's `__dict__` at the same storage:

![x, y, and z are three distinct objects, but every __dict__ points at the same _shared_state, so the last write wins for all three](_images/borg_shared_state)

```python
# borg_singleton.py
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
    assert x is not y  # Distinct objects...
    assert x.val == y.val  # ...sharing one set of state
    assert x.val == "second"
```

### Singleton Classes

You can wrap a class so that calling it returns a cached instance.
This is a *class decorator*
(see [Decorators](14_Decorators.md#decorating-classes)):

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
[Metaprogramming](17_Metaprogramming.md#intercepting-instance-creation)
places a similar metaclass singleton beside the simpler hooks that usually replace it.
This version is here for completeness:

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

This is the other side of the `__new__()` rule.
`my_new()` returns an instance of `Bar` itself,
so Python calls `__init__()` after every construction,
on the same shared object.
Each `Bar(...)` call therefore overwrites `val`,
which is why `x` prints as `spam`.
The [Overriding `__new__`](#overriding-__new__)
version returned a foreign object, so its `__init__()` never ran at all.
Same pattern, opposite `__init__()` behavior,
and the difference is only what `__new__()` returns.

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
    create a factory that manages a fixed pool of objects
    (say, database connections) and hands them out,
    rather than a single instance.
3.  Rewrite one of the class-based singletons above as a module,
    and argue which you would use in real code.
4.  In `shared_config.py`, replace the mutation with a rebinding,
    `settings = {"theme": "dark"}`,
    and add `import config` plus `print(config.settings)` at the end.
    Predict both printed values before running it,
    and explain the difference using the binding-versus-mutation distinction from [A Module Is Already a Singleton](#a-module-is-already-a-singleton).
