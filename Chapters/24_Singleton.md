# Singleton

A *singleton* is the simplest design pattern: a class with exactly one instance.
Before using a classic implementation,
ask whether the language already solves the problem,
the question [When a Pattern Dissolves](21_The_Pattern_Concept.md#when-a-pattern-dissolves)
poses for every pattern.
For the singleton, Python does.

## A Module Is Already a Singleton

Python imports each module once and caches it in `sys.modules`,
as [Modules and Packages](06_Modules_and_Packages.md) showed.
Every `import` after the first produces the same module object.
A module is a singleton, and everyone shares anything defined at module level,
with one copy for the whole interpreter.
One interpreter, not one machine.
A process pool or an [`InterpreterPoolExecutor`](19_Concurrency.md#subinterpreters)
gives each worker its own `sys.modules`,
so each builds its own copy and a write in one is invisible to the rest.
A singleton is only single inside the interpreter that holds it,
and that is true of every form in this chapter, not only the module.

Put the state in a module:

```python
# config.py
print("config body runs")
settings: dict[str, str] = {}
```

```python
# module_singleton.py
import config
import config as again

print(config is again, config.settings is again.settings)
#: config body runs
#: True True
```

Two `import` statements, one printed line.
The first one runs `config.py` top to bottom and files the resulting module object in `sys.modules` under the name `config`.
The second finds it there and skips the work,
so the body never runs twice and builds only one `settings` dict.
That is the singleton: not a rule the class enforces,
but a lookup the import system performs.

Every import of `settings`, from anywhere, hands back that same `dict`.
Mutating it through one import is visible through every other:

```python
# shared_config.py
from config import settings

settings["theme"] = "dark"
print(settings)
#: config body runs
#: {'theme': 'dark'}
```

No class, no ceremony.
For most singleton needs, a module solves the problem.

Mutation makes the sharing work.
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

Sharing also depends on the name.
`sys.modules` uses the module name as its key,
and the file you launch runs under the name `__main__`.
If that file is `config.py`, a later `import config` finds no cached entry,
runs the body again, and builds a second module object with its own `settings`.
Keep singleton state in a module you import, not in the script you run.

## When You Want a Class, Cache the Instance

Every construction should return the same object.
The simplest approach hides construction behind a cached factory.
That factory applies `functools.cache` to a *constructor function*,
which is an ordinary function that builds and returns an instance of a class.
It stands in for a direct call to the class constructor.

`functools.cache` ([Caching](18_Performance.md#caching)) *memoizes* a function.
The first call with a given set of arguments runs the function and stores the result.
Every repeat call with those arguments returns the stored result.
A constructor function with no arguments has only one possible call,
so caching it constructs the instance once and returns that same object forever:

```python
# singleton_cached_factory.py
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

### Nothing Keeps the Class Private

You can't prevent a caller from writing `Settings()` and getting a second instance.
Naming the class `_Settings` marks it internal and keeps it out of `from module import *`,
which is as far as Python goes.
A second underscore is not a stronger version of that.
At module level the compiler [mangles](11_Testing.md#white-box-and-black-box-tests)
nothing, so the second underscore hides nothing,
and inside a class body the compiler rewrites `m.__Settings` into a lookup for `_TheClass__Settings`,
which breaks the reference.

This listing keeps the bare name for a reason that outlasts the convention.
`settings()` returns a `Settings`,
so the class already appears in the module's public signature.
A caller who annotates the result must write that name,
and a type outsiders must name is not private, whatever it starts with.
Only if the type never left the module would you use `_Settings`.

Two stronger-looking moves fail the same way.
Deleting the name after building the instance leaves the class reachable,
because `type(settings())` hands it back.
Defining the class inside `settings()` also looks airtight,
and `@cache` runs that body only once,
so the body builds one instance and leaves no module-level name.
`type(settings())` still recovers it.

Nesting costs the return annotation as well.
`def settings() -> Settings` still parses and runs,
because an annotation evaluates only when something reads it,
and nothing has read this one yet.
A clean run is therefore no evidence.
When something does look, it searches the scope containing the function,
not the function's own locals, and the class is not there.
A checker reports an unresolved reference,
and `inspect.get_annotations()` raises a `NameError`.
The signature must name something reachable,
so nesting costs you either the annotation or a separate `Protocol` to name in its place.

Privacy in Python is advice, not enforcement.
An underscore asks callers to stay out, and nothing makes them.
[Rethinking Objects](20_Rethinking_Objects.md#encapsulation-leaks)
makes the same case about hidden data,
where a getter hands back a reference to the internals it should protect.
The reachable class is also useful when a test needs a fresh,
uncached `Settings`.

### Tests, Threads, and Locks

Three implementation notes:

1. A singleton holds shared state, and shared state leaks between tests.
   The cached factory has an escape hatch the classic forms lack:
   `settings.cache_clear()` discards the instance, so each test can start fresh.

2. Every lazy singleton has a first-call race under threads.
   Concurrent first calls can each run the constructor,
   and each caller can end up holding a different object,
   with only one of them staying in the cache.
   Eight threads calling `settings()` at once,
   with a constructor slow enough to widen it,
   ran that constructor eight times and handed back eight different objects.
   When threads can arrive before the singleton exists,
   create it eagerly instead: call `settings()` once at import time,
   or use the module form, which the import system builds exactly once.

3. A [lock](19_Concurrency.md#locks) is the other fix for that race,
   but not in the obvious place.
   Wrapping the cached function's body in a `threading.Lock` changes nothing,
   because every thread has already missed the cache before reaching the lock.
   They serialize, each still builds an object,
   and the cache keeps whichever finished last.
   The check must run inside the lock, as the listing below shows.

The race is easy to see with a wide enough window:

```python
# singleton_cached_race.py
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

@cache
def settings() -> Settings:
    return Settings()

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}) > 1)
#: True
```

Eight threads, more than one object.
Every thread checked the cache before any of them had filled it,
so each ran the constructor and handed its caller a different object.
Only the last one to finish stays in the cache;
the other seven are already in the hands of their callers.

`@cache` disappears below, because it no longer makes the object single:

```python
# singleton_locked_settings.py
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

In `settings()`, only one of the two module-level names carries a `global` declaration.
The chapter's opening distinction reappears here, from inside a function.
`global` governs rebinding, not use.
`with _lock:` only looks the name up,
even though acquiring and releasing changes that lock's state,
from unlocked to locked and back.
Changing an object is not rebinding a name.
`_instance` differs because the function assigns to it.
Python decides at compile time that a name a function assigns anywhere is local everywhere in that function,
so without the `global` declaration,
`if _instance is None` reads an unassigned local and raises an `UnboundLocalError`.
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

The classic escape is *double-checked locking*:
test `_instance` before taking the lock,
take it only when the test says the object is missing, then test again inside.
The second test is the one note 3 insists on;
the first exists to skip the lock once the object is there.
It works, but it asks the reader to reason about what a [free-threaded](19_Concurrency.md#free-threading)
interpreter may reorder, which is a bad trade for saving a lock acquisition.
Eager creation is a better answer when you can build the object at import time:

```python
# singleton_eager_factory.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings() -> Settings:
    return Settings()

settings()  # Build it before any thread can race for it
print(settings() is settings())
#: True
```

The priming call is safe for the same reason the module form is:
the import system runs a module body once,
so the object exists before any thread can ask for it.
The race needs laziness, and this listing gives it up on purpose.

If you need the class to hand back one instance from its own constructor,
override `__new__()`, shown below.

Modules and cached factories, primed at import time if threads are in play,
should cover your singleton needs.
The rest of this chapter is here for the techniques it demonstrates,
not because you need these forms.

## The Classic Implementations

To address languages like C++ and Java,
*GoF Design Patterns* builds the singleton with more apparatus.
Each variation shown here does more work than the module or the cached factory above.

The first controls creation by delegating to a single instance of a private nested class.
The rest reach the same guarantee by other means: a class variable,
a shared `__dict__`, and a decorator.

### Lazy Creation

The classic approach is *lazy*: it builds the inner object on the first call,
which is why it needs the `None` sentinel and the `if` guard.

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
This is name mangling.
`OnlyOne.__OnlyOne`, written from outside the class,
asks for an attribute that does not exist under that name,
so it fails at runtime with `AttributeError`, not at type-checking time.
The outer class controls creation through its constructor.
The first time you create an `OnlyOne` it initializes `instance`.
After that it reuses the one inner object,
and each construction appends its argument to that object's shared list.
`__getattr__()` delegates access.
Python calls it only when ordinary attribute lookup fails,
so a name the wrapper does not have, such as `val`,
falls through to the inner object.
The distinct `OnlyOne` instances all proxy to the same `__OnlyOne` object.

`__getattr__()` returns `Any`, and unlike `instance`,
nothing can tighten that one away.
It answers for every name Python fails to find on the wrapper,
so its return type is whatever the inner object holds under that name.
`instance` is a single declared field and can say `__OnlyOne | None`.
`__getattr__()` covers an open set of names and cannot.
Delegation trades static knowledge for reach,
which is the cost [Surrogate](26_Surrogate.md#proxy) pays throughout.

The laziness is a choice.
When the inner object needs nothing from that first call,
you can create it *eagerly* in the class body instead,
`instance: ClassVar[__OnlyOne] = __OnlyOne()`, which removes the sentinel,
the guard, and the first-call race the cached factory met under threads,
at the cost of building the object whether or not anything uses it.
(The bare `__OnlyOne()` works because the nested class exists at that point in the body; the qualified `OnlyOne.__OnlyOne()` fails, since the name `OnlyOne` stays unbound until its own class body finishes running.)
Exercise 1 makes that change.

Either way, this is a lot of code for what a module does on its own.

### One Instance in a Class Variable

The nested private class is optional.
Here you keep the single instance in a class variable.
`__new__()`, the method that creates an instance,
builds it when needed and returns it as the result of every construction:

```python
# singleton_class_variable.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        if SingletonClassVar.__instance is None:
            SingletonClassVar.__instance = object.__new__(cls)
            SingletonClassVar.__instance.val = []
        SingletonClassVar.__instance.val.append(arg)
        return SingletonClassVar.__instance

x = SingletonClassVar("sausage")
y = SingletonClassVar("eggs")
z = SingletonClassVar("spam")
print(x.val, x is y is z, isinstance(x, SingletonClassVar))
#: ['sausage', 'eggs', 'spam'] True True
```

`object.__new__(cls)` builds a `SingletonClassVar`,
so every construction hands back that same instance and `isinstance()` reports `True`.
Python honors whatever object `__new__()` returns,
and the return value decides whether `__init__()` runs:
`__init__()` runs only when `__new__()` returns an instance of the class under construction,
and then it runs on that shared instance after *every* construction,
if the class defines one.
`SingletonClassVar` defines none, so `__new__()` does all the work.
A `__new__()` that returned some other object instead would skip `__init__()`,
and fail `isinstance()` as well.

### Borg: Singleton By Inheritance

[Alex Martelli observes](http://www.aleax.it/Python/5ep.html)
that what you usually want is not one object but one shared set of state.
People can create as many objects as they like,
as long as they all share the same data.
He called this the *Borg*.^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."]
It points every instance's `__dict__` at the same storage:

![x, y, and z are three distinct objects, but every __dict__ points at the same _shared_state, so the last write wins for all three](_images/borg_shared_state)

In contrast with the previous singleton designs,
you reuse *Borg* through inheritance:

```python
# singleton_borg.py
from typing import Any, ClassVar

class Borg:
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        super().__init__()
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

Unlike the nested-class examples above,
`Singleton` should not be a `@dataclass`.
Although that still runs, it quietly stops being a `Borg`.
The shared state depends on `super().__init__` rebinding `self.__dict__` to `_shared_state`.
A dataclass generates its own `__init__` that assigns the fields and [never calls the base `__init__`](12_Data_Classes_as_Types.md#dataclass-inheritance),
so nothing rebinds `self.__dict__` and each instance keeps its own state.
Moving the rebinding into `__post_init__` does not help either.
That runs after `__init__` assigns the fields, so it discards them.
The hand-written `__init__` makes the shared state work,
and silently losing the sharing is worse than failing outright.

The sharing also reaches further than it looks.
`_shared_state` is one dict on `Borg`, so every subclass shares it,
not merely every instance of a single subclass.
A second subclass alongside `Singleton` writes into the same dict,
so constructing one of each leaves both objects reading the value set last.
A subclass that needs storage of its own declares it:
`class Singleton(Borg): _shared_state: ClassVar[dict[str, Any]] = {}`.

Testing confirms the objects differ but share one set of state:

```python
# test_singleton_borg.py
from singleton_borg import Singleton

def test_borg_shares_state_but_not_identity() -> None:
    x = Singleton("first")
    y = Singleton("second")
    assert x is not y  # Distinct objects
    assert x.val == y.val  # But sharing one set of state
    assert x.val == "second"
```

### Singleton by Class Decorator

A [class decorator](14_Decorators.md#decorating-classes)
can wrap a class so that calling it returns a cached instance:

```python
# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, constructor: type) -> None:
        self.constructor = constructor
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        if self.instance is None:
            print(f"constructing {self.constructor.__name__}")
            self.instance = self.constructor(*args, **kwargs)
        else:
            print(f"using cached {self.constructor.__name__}")
            print(f"discarding {args}, {kwargs}")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *, limit: int = 10) -> None:
        print(f"Registry.__init__({name}, {limit})")
        self.name = name
        self.limit = limit
        self.items: list[str] = []

first = Registry("primary", limit=3)
#: singleton.__call__(('primary',), {'limit': 3})
#: constructing Registry
#: Registry.__init__(primary, 3)
first.items.append("spam")
first.items.append("eggs")
second = Registry("secondary", limit=99)
#: singleton.__call__(('secondary',), {'limit': 99})
#: using cached Registry
#: discarding ('secondary',), {'limit': 99}
print(first is second, second.name, second.limit, second.items)
#: True primary 3 ['spam', 'eggs']
```

Applying `@singleton` to `Registry` runs `Registry = singleton(Registry)`.
The name `Registry` now refers to the decorated instance rather than to the class.
Why does `__call__()` intercept the constructor for a `Registry`?
A *call* is parentheses written after an expression.
That expression can produce anything: a function, a class, or an instance.
To evaluate `obj(...)`, Python looks up `__call__()` on the *type* of `obj`.
The result depends on that type.
For an ordinary class, `type(Plain)` is `type`,
and the parentheses run `type.__call__()`,
the machinery that invokes `__new__()` and then `__init__()`.
After decoration, `type(Registry)` is `singleton`,
so the same parentheses run `singleton.__call__()` instead,
and the wrapped class's constructor runs only when that method decides to call it.
`__call__()` forwards `*args` and `**kwargs` to the constructor of the wrapped class,
so `Registry("primary", limit=3)` reaches the real constructor unchanged.

Only the first call constructs a `Registry`.
Every later constructor call returns the cached instance and discards the constructor arguments,
which is why `Registry("secondary", limit=99)` does not create a new object.
A caller who believes those arguments took effect is holding an object configured by someone else.

Both `isinstance(first, Registry)` and subclassing `Registry` raise exceptions:

```python
# test_singleton_class.py
import pytest
from singleton_class import Registry

def test_isinstance_rejects_the_decorated_name() -> None:
    with pytest.raises(TypeError, match="arg 2 must be a type"):
        isinstance(Registry("primary"), Registry)  # type: ignore

def test_subclassing_the_decorated_name_fails() -> None:
    with pytest.raises(TypeError, match="takes 2 positional"):
        class Sub(Registry):  # type: ignore
            pass
```

The type checker complains that defining `Sub` raises a `TypeError` at runtime.
`singleton.__init__()` takes two positional arguments and receives four,
because a class statement hands the name, bases, and namespace to its metaclass,
and Python takes that metaclass from the type of the base, which is `singleton`.
Nothing in `class Sub(Registry)` mentions `singleton`,
so the error names a class that does not appear in the failing line.
That is the confusion a class decorator costs you.
The `__new__()` version above keeps the name pointing at a real class,
which is the reason to prefer it.

A metaclass can also intercept construction.
[Metaprogramming](17_Metaprogramming.md#intercepting-instance-creation)
shows that singleton: its metaclass overrides `__call__()`,
which skips `__init__()` on every later construction,
so the first call's arguments win.
A class that overrides `__new__()` instead,
as `singleton_class_variable.py` does, still runs on every call,
unlike the metaclass form above;
that listing puts its work inside `__new__()` itself,
so later calls append to the shared instance instead of overwriting it.
That chapter also covers `__init_subclass__()` and `__set_name__()`,
the simpler hooks that replace most metaclasses;
a singleton needs none of this machinery.

## Which Should You Use?

Use the lightest tool that fits:

- For almost everything, use a module with module-level state.
  It is the default Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`),
  or override `__new__()` as `singleton_class_variable.py` does.
  Under threads, prime the factory at import time or use the module form.
- If you really want many handles sharing one set of state, use *Borg*.
- The decorator and metaclass forms work,
  but they are more machinery than the problem usually justifies.

The elaborate *GoF Design Patterns* singleton is largely a workaround for languages where a module is not a first-class,
single-instance namespace.
In Python, most of the ceremony falls away.

## Exercises

1.  `singleton_pattern.py` waits for the first construction to build its inner object.
    Modify it to use *eager initialization*,
    creating the inner instance in the class body,
    and remove the sentinel and the guard.
    What did the change cost,
    and which failure from [Tests, Threads, and Locks](#tests-threads-and-locks)
    can no longer occur?
2.  Using `singleton_cached_factory.py` as a starting point,
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
5.  Add a `threading.Lock` *inside* `settings()` in `singleton_cached_race.py`,
    wrapping only the body of the cached function, and run it.
    Explain why the object count does not drop to one,
    then fix it without a lock.
6.  Give `singleton_borg.py` a second `Borg` subclass and construct one of each.
    Explain the value you get back,
    and change the code so the two subclasses keep separate shared state.
