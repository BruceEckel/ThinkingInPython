# Singleton

> A program has one configuration, one log, one registry of plugins,
> and every part of the program must see the same one.
> A *Singleton* creates that one instance and shares it.

The classic form is a class that refuses a second instance.
Before writing one, ask whether the language solves the problem for you,
the question [When a Pattern Dissolves](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
poses for every pattern.
For *Singleton*, the language has an answer.

## A Module Is Already a Singleton

Python [imports each module once](06_Foundations--Modules_and_Packages.md)
and caches it in `sys.modules`.
Every `import` after the first produces the same module object.
A module is a singleton.
Everything it defines at module level exists once per interpreter,
and every importer shares it.

One interpreter, not one machine.
A process pool or an [`InterpreterPoolExecutor`](19_Techniques--Concurrency.md#subinterpreters)
gives each worker its own `sys.modules`, so each worker builds its own copy.
A write in one copy leaves the other copies unchanged.
A singleton is single within the interpreter that holds it,
and every form in this chapter, the module included, has that limit.

Put the state in a module:

```python
# config.py
print("config body runs")
settings: dict[str, str] = {}
```

```python
# module_singleton.py
import sys
import config  # [1]
import config as again  # [2]

#: config body runs
print(config is again is sys.modules["config"])
#: True
```

The first import of `config` (`[1]`)
creates a new module object and stores it in `sys.modules` under the name `config`.
Then Python runs `config.py` top to bottom,
defining each module-level name in that module object.
The second import (`[2]`)
finds the entry and binds `again` to the stored module,
so the body runs once and builds one `settings` dict.
The singleton here is not a rule a class enforces,
but a lookup the import system performs.

Every import of `settings`, from anywhere,
binds the importer's name to that same `dict`.
Mutating that `dict` through one import is visible through every other:

```python
# shared_config.py
import config
from config import settings

#: config body runs
settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
print(config.settings)
#: {'theme': 'dark'}
```

No class, no ceremony.
For most singleton needs, a module solves the problem.

The three listings come down to three steps through `sys.modules`.
A fourth step shows the mistake that undoes the sharing:

![](_images/singleton_story)

Steps 3 and 4 look alike in code but differ in where the arrow points.
A mutation follows the name's arrow into the dict that `config` holds,
so every importer sees the change.
A rebinding moves the arrow to a new dict and leaves the module's dict as it was.

`from config import settings` gives your module its own name for the same `dict` object named by `config.settings`.
Mutating through your name, `settings["theme"] = "dark"`,
changes that shared object, so every module sees it.
But `settings = {}` in your module rebinds your module's name.
Your module and `config` silently diverge.
`config.settings` still holds the old dict,
while your module's name now refers to a new, unshared dict.

To replace the whole value, go through the module: `import config`,
then `config.settings = {...}`.
Code that reads `config.settings` then gets the new dict.
In a module that ran `from config import settings` earlier,
that module's `settings` still refers to the old dict.
When such modules exist,
replace the contents in place with `settings.clear()` and `settings.update()`.
Mutate through any name.
Rebind only through the module.

Sharing also depends on the module's name.
`sys.modules` uses the module name as its key,
and the file you launch runs under the name `__main__`.
If that file is `config.py`, a later `import config` finds no cached entry,
runs the body again, and builds a second module object with its own `settings`.
Keep singleton state in a module you import, not in the script you run.

## When You Want a Class, Cache the Instance

A module's state is a set of loose names.
When the shared state has fields and methods that belong together,
or other code needs a type to name in an annotation, you need a class.
Every construction should then return the same object.

The simplest approach hides construction behind a cached factory,
which applies `functools.cache` to a *constructor function*.
A constructor function is an ordinary function that builds and returns an instance of a class,
and it stands in for a direct call to the class constructor.

[`functools.cache`](18_Techniques--Performance.md#caching)
*memoizes* a function.
The first call with a given set of arguments runs the function and stores the result.
Every repeat call with those arguments returns the stored result.
A constructor function with no parameters has only one possible call,
so caching it constructs the instance once and returns that same object on every later call:

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
print(a is b)
#: True
a.data["theme"] = "dark"
print(b)
#: Settings(data={'theme': 'dark'})
```

A constructor function with a parameter can return more than one instance.
`functools.cache` keys its cache on the arguments,
so each distinct set of arguments gets its own entry and its own instance:

```python
# singleton_cached_factory_footgun.py
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

@cache
def settings(env: str = "prod") -> Settings:
    return Settings()

print(len({id(settings()), id(settings("prod")),
           id(settings(env="prod"))}))
#: 3
```

One parameter turns "one singleton" into one singleton per argument value.
A default does not help.
The cache looks up its entry by the arguments as the call writes them,
before Python fills in any default.
The three calls in the listing therefore build three objects for one environment.
Keep the constructor function's signature empty,
or accept that you built a cache, not a singleton.

### Nothing Keeps the Class Private

A caller can write `Settings()` and get a second instance.
Naming the class `_Settings` marks it internal and keeps it out of `from module import *`.
Any caller can still import `_Settings` by name and call it.

A second underscore adds no protection.
The compiler [mangles](11_Techniques--Testing.md#white-box-and-black-box-tests)
names only inside a class body,
so at module level `__Settings` keeps its name as written,
as reachable as any other.
The second underscore has one effect:
it breaks a reference written inside a class body.
Inside the body of a class `Client`, the compiler rewrites `m.__Settings`,
a lookup in module `m`, into a lookup for `m._Client__Settings`.
That lookup fails.

The cached-factory listings name the class `Settings`, with no underscore,
because the name is public.
`settings()` returns a `Settings`,
so the class appears in the module's public signature.
A caller who annotates the result must write that name.
A type outsiders must name is public, whatever its first character.
`_Settings` fits a type that stays inside the module.

Two stronger-looking moves also leave the class reachable.
Deleting the class name after `settings()` builds the instance removes the name alone,
since `type(settings())` still returns the class.
Defining the class inside `settings()` puts its name in the function's locals,
and `@cache` runs that body once.
`type(settings())` still recovers the class.

Nesting also breaks the return annotation.
`def settings() -> Settings` still parses and runs,
because an annotation evaluates only when something reads it.
A clean run therefore leaves the name untested.
Any code that reads the annotation searches the scope containing the function,
while the class lives in the function's own locals.
A type checker reports an unresolved reference,
and `inspect.get_annotations()` raises a `NameError`.
The annotation must name a type that code outside the function can reach,
so a nested class forces a choice between dropping the annotation and defining a separate `Protocol` to name in its place.

Privacy in Python is advice, not enforcement.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#encapsulation-leaks)
shows the same limit for data:
a read-only property over an underscore-named field still hands the caller a mutable reference.
The reachable class is also useful when a test needs a fresh `Settings`,
built outside the cache.

### Tests, Threads, and Locks

1. A singleton holds shared state, and shared state leaks between tests.
   The cached factory offers a reset the classic forms lack.
   `settings.cache_clear()` discards the instance, so each test can start fresh.

2. Every *lazy* singleton builds its object on the first call,
   so it has a first-call race under threads.
   Concurrent first calls can each run the constructor.
   Each caller can end up holding a different object.
   The cache keeps one of those objects.
   With a constructor slow enough to widen that race,
   eight threads calling `settings()` at once usually run the constructor eight times and return eight different objects.
   When threads can arrive before the singleton exists,
   create it *eagerly* instead.
   Call `settings()` once at import time, or use the module form,
   which the import system builds once.

3. A [lock](19_Techniques--Concurrency.md#the-gil-does-not-prevent-races)
   is the other fix for that race.
   A `threading.Lock` around the constructor function's body leaves the race in place,
   because every thread misses the cache before reaching the lock.
   The threads serialize, but each still builds an object.
   The cache keeps whichever finished last.
   The check must run inside the lock, as `singleton_locked_settings.py` shows.

### The First-Call Race

The first-call race is easy to see with a wide enough window.
The four race listings in this chapter share a slow `Settings` and a `distinct_objects()` helper.
The helper calls a factory from eight threads at once and counts the distinct objects they get back:

```python
# race_settings.py
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

def distinct_objects(factory: Callable[[], object]) -> int:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(factory) for _ in range(8)]
    return len({id(f.result()) for f in futures})
```

The sleep stands in for a constructor that does real work,
such as opening a file or a connection.
Without the sleep, the cached version below returned one object in each of twenty trials.
A race that testing misses is the more dangerous case.
A window too narrow to reproduce is still a window.

```python
# singleton_cached_race.py
from functools import cache
from race_settings import Settings, distinct_objects

@cache
def settings() -> Settings:
    return Settings()

print(distinct_objects(settings) > 1)
#: True
```

Every thread checks the cache before any of them has filled it,
so each runs the constructor and returns a different object to its caller.
The object from the last thread to finish stays in the cache.
The other seven stay with the callers that received them.

The listing prints a comparison instead of the count because the count depends on timing.
The count is eight when every thread misses the cache,
and the sleep makes that result likely.

The fix puts the check inside a lock.
`@cache` runs its check inside its own wrapper,
where your code cannot put a lock around it.
So the locked version drops `@cache` and puts its own check inside the lock:

```python
# singleton_locked_settings.py
import threading
from typing import Final
from race_settings import Settings, distinct_objects

_lock: Final[threading.Lock] = threading.Lock()
_instance: Settings | None = None

def settings() -> Settings:
    global _instance
    with _lock:
        if _instance is None:
            _instance = Settings()
    return _instance

print(distinct_objects(settings))
#: 1
```

One thread finds `_instance` empty and builds it.
The rest wait on the lock, and each finds `_instance` filled.

`settings()` declares `global` for `_instance` and leaves `_lock` undeclared.
The [mutate-versus-rebind distinction](#a-module-is-already-a-singleton)
reappears here, from inside a function.
`global` [governs rebinding](05_Foundations--Functions.md#names-inside-a-function),
not use.
`with _lock:` reads the name,
although acquiring and releasing changes that lock's state,
from unlocked to locked and back.
Changing an object is not rebinding a name.
`_instance` differs because the function assigns to it.
Python decides at compile time that a name a function assigns anywhere is local everywhere in that function.
Without the `global` declaration,
`if _instance is None` reads an unassigned local and raises an `UnboundLocalError`.
Mutate through any name.
Declare only what you rebind.

### Double-Checked Locking and Eager Creation

Every call to the locked `settings()` acquires the lock,
including the thousands that arrive long after the object exists.

The classic workaround is *double-checked locking*:
test `_instance` before taking the lock,
take it when the test finds the object missing, then test again inside:

```python
# singleton_double_checked.py
import threading
from typing import Final
from race_settings import Settings, distinct_objects

_lock: Final[threading.Lock] = threading.Lock()
_instance: Settings | None = None

def settings() -> Settings:
    global _instance
    if _instance is None:  # [1]
        with _lock:
            if _instance is None:  # [2]
                _instance = Settings()
    return _instance

print(distinct_objects(settings))
#: 1
```

The inner test (`[2]`)
is the check inside the lock from `singleton_locked_settings.py`.
The outer test (`[1]`) exists to skip the lock when the object is there.

Double-checked locking works, but it depends on two details.
If you drop the inner test,
every thread that passed the outer test before the first assignment builds its own object,
one after another.
And the assignment to `_instance` must be the last step of construction.
The outer test runs outside the lock,
so a thread can read `_instance` while another thread is still inside the `with` block.
In a version that assigns `_instance = Settings()` and then fills in `data`,
that reader's `settings()` returns a half-built object.
Skipping one lock acquisition per call rarely justifies two details that must both stay right.

Eager creation is a better answer when you can build the object at import time:

```python
# singleton_eager_factory.py
from functools import cache
from race_settings import Settings, distinct_objects

@cache
def settings() -> Settings:
    return Settings()

settings()  # Build it before any thread can race for it
print(distinct_objects(settings))
#: 1
```

Apart from the line it prints,
the listing is `singleton_cached_race.py` plus the priming call.
The priming call runs in the module body,
so the call is safe for the same reason the module form is.
The import system runs a module body once,
so the object exists before any thread can ask for it.
The race needs laziness, and this listing gives it up on purpose.

If you need the class to hand back one instance from its own constructor,
override `__new__()`, as `singleton_class_variable.py` does.

Modules and cached factories should cover your singleton needs.
Prime a cached factory at import time if threads are in play.

## The Classic Implementations

*GoF Design Patterns* writes its examples in C++ and Smalltalk,
and it builds the singleton with more apparatus.
Its class blocks direct construction and hands out the sole instance through a class operation,
`Instance()`, which builds the object on the first call.
The cached factory's `settings()` is that operation written as a function.
Python [cannot block construction](#nothing-keeps-the-class-private),
so the class-based forms here keep the constructor public and route every construction to the same shared state.
Each takes more code than a module or a cached factory.

The first form wraps a single instance of a private nested class.
The second form keeps the instance in a class variable.
Alex Martelli's *Borg* replaces the one object with many objects that share one set of state.
The last form is a class decorator.

### Lazy Creation

The classic approach is lazy.
It builds the inner object on the first call,
so it needs the `None` sentinel and the `if` guard.

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
y = OnlyOne("eggs")
z = OnlyOne("spam")
print(x.val)
#: ['sausage', 'eggs', 'spam']
# Distinct wrappers (x is not y), one shared inner instance:
print(x is y, x.instance is y.instance is z.instance)
#: False True
```

Because the inner class's name starts with a double underscore,
the compiler mangles it to `_OnlyOne__OnlyOne` wherever it appears inside `OnlyOne`'s body.
Code outside the class that writes `OnlyOne.__OnlyOne` asks for `__OnlyOne`,
while the class stores the attribute as `_OnlyOne__OnlyOne`.
That lookup fails at runtime with an `AttributeError`,
not at type-checking time.

`__getattr__()` delegates access.
Python calls it only when ordinary attribute lookup fails,
so a name the wrapper does not have, such as `val`,
falls through to the inner object.

The proxying covers reads.
An assignment such as `x.val = []` goes into the wrapper's own `__dict__`.
The shared list stays as it was,
and later reads of `x.val` find the wrapper's copy.
[Forwarding Writes](25_Patterns--Surrogate.md#forwarding-writes)
adds the `__setattr__()` that forwards assignments.

`__getattr__()` returns `Any`, and that `Any` stays.
`instance` is one declared field, so its annotation can say `__OnlyOne | None`.
Python calls `__getattr__()` for every name it fails to find on the wrapper,
an open set of names.
The method's return type is whatever the inner object holds under each name,
so `Any` is the one annotation that fits every name and still lets the caller use the result.
Delegation gives up static knowledge to forward every name,
as it does throughout [*Surrogate*](25_Patterns--Surrogate.md#forwarding-with-getattr).

When the inner object is ready to build before the first call,
you can create it eagerly in the class body instead,
`instance: ClassVar[__OnlyOne] = __OnlyOne()`.
Eager creation removes the sentinel, the guard,
and the first-call race that every lazy singleton has under threads.
The class then builds the object whether or not anything uses it
(see exercise 1).
(The bare `__OnlyOne()` works because the nested class exists at that point in the body.
The qualified `OnlyOne.__OnlyOne()` fails,
since the name `OnlyOne` stays unbound until its own class body finishes running.)

Either way, `OnlyOne` takes a nested class, a class variable,
and a `__getattr__()` to share one object,
while a module shares its state with no class.

### One Instance in a Class Variable

The nested private class is optional.
`SingletonClassVar` keeps the single instance in a class variable.
`__new__()` is the method that creates an instance.

```python
# singleton_class_variable.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        if SingletonClassVar.__instance is None:
            SingletonClassVar.__instance = (
                object.__new__(cls))
            SingletonClassVar.__instance.val = []
        SingletonClassVar.__instance.val.append(arg)
        return SingletonClassVar.__instance

x = SingletonClassVar("sausage")
y = SingletonClassVar("eggs")
z = SingletonClassVar("spam")
print(x.val, x is y is z, isinstance(x, SingletonClassVar))
#: ['sausage', 'eggs', 'spam'] True True
```

`object.__new__(cls)` builds a real `SingletonClassVar`,
so `isinstance()` reports `True` for the instance every construction hands back.
Python uses the object `__new__()` returns as the result of the construction.
The type of that object determines whether `__init__()` runs.
When `__new__()` returns an instance of the class under construction,
Python runs `__init__()` on it.
A `__new__()` that returns some other object skips `__init__()` and fails `isinstance()` as well.
A singleton `__new__()` returns an instance of the class on every construction,
so Python runs `__init__()` on the shared instance after every construction
(see exercise 7).
`SingletonClassVar` defines no `__init__()`,
so `__new__()` both creates the shared list and appends each argument.

### Borg: Singleton by Inheritance

[Alex Martelli observes](http://www.aleax.it/Python/5ep.html)
that what you usually want is not one object but one shared set of state.
People can create as many objects as they like,
as long as they all share the same data.
He called that design the *Borg*.^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."]
A *Borg* points every instance's `__dict__` at the same storage:

![Three distinct instances share one `__dict__`](_images/borg_shared_state)

Each previous design manages one specific class,
but *Borg* is a base class that any class reuses through inheritance:

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
```

```python
# singleton_borg_demo.py
from singleton_borg import Singleton

x = Singleton("sausage")
y = Singleton("eggs")
z = Singleton("spam")
# Last write wins: distinct objects, one shared __dict__:
print(x.val, x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: spam False True
```

`Singleton` defines its own `__init__()`, and it cannot be a `@dataclass`.
The sharing depends on `super().__init__()` rebinding `self.__dict__` to `_shared_state`.
A dataclass generates its own `__init__()`,
which assigns the fields and [skips the base `__init__()`](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance),
so each instance keeps its own `__dict__`.
The dataclass version still runs,
but the class has quietly stopped being a `Borg`.
A `__post_init__()` that does the rebinding fails differently.
It runs after `__init__()` has assigned the fields,
so the rebinding discards them, and reading `val` raises an `AttributeError`.
Silently losing the sharing is worse than failing outright.
The hand-written `__init__()` keeps the sharing.

The sharing also spans subclasses.
`_shared_state` is one dict on `Borg`,
so every instance of every subclass shares it.
A second subclass alongside `Singleton` writes into the same dict,
so constructing one of each leaves both objects reading the value set last.
A subclass that needs storage of its own declares it:
`class Singleton(Borg): _shared_state: ClassVar[dict[str, Any]] = {}`.
The lookup through `self` finds the subclass's dict first.
Martelli wrote `self._shared_state` instead of `Borg._shared_state` to allow that override.

*Borg* has no `cache_clear()`,
so whatever one test leaves in `_shared_state` stays there for the next.
A pytest fixture that clears the dict before each test gives every test empty shared state:

```python
# test_singleton_borg.py
import pytest
from singleton_borg import Borg, Singleton

@pytest.fixture(autouse=True)
def reset_shared_state() -> None:
    Borg._shared_state.clear()

def test_borg_shares_state_but_not_identity() -> None:
    x = Singleton("first")
    y = Singleton("second")
    assert x is not y  # Distinct objects
    assert x.__dict__ is y.__dict__
    assert x.val == "second"

def test_leaves_an_attribute_behind() -> None:
    setattr(Singleton("first"), "extra", "leftover")

def test_fixture_clears_shared_state() -> None:
    y = Singleton("second")
    assert not hasattr(y, "extra")  # Reset ran
```

`test_leaves_an_attribute_behind` writes an attribute into the shared dict,
and `test_fixture_clears_shared_state` confirms that the next test finds it gone.

### Singleton by Class Decorator

A [class decorator](14_Techniques--Decorators.md#decorating-classes)
can wrap a class so that every call to the class returns one cached instance:

```python
# singleton_class.py
from typing import Any

class singleton:
    def __init__(self, wrapped: type) -> None:
        self.wrapped = wrapped
        self.instance: Any = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"singleton.__call__({args}, {kwargs})")
        name = self.wrapped.__name__
        if self.instance is None:
            print(f"constructing {name}")
            self.instance = self.wrapped(*args, **kwargs)
        else:
            print(f"cached {name}: arguments discarded")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *,
                 limit: int = 10) -> None:
        print(f"Registry.__init__({name}, {limit})")
        self.name = name
        self.limit = limit
        self.items: list[str] = []
```

`@singleton` on `Registry` runs `Registry = singleton(Registry)`.
The name `Registry` now refers to a `singleton` object that holds the class,
not to the class.

Why does `__call__()` intercept the constructor for a `Registry`?
To evaluate `obj(...)`,
Python [looks up `__call__()` on the type of `obj`](25_Patterns--Surrogate.md#special-methods-bypass-getattr).
For an ordinary class `C`, `type(C)` is `type`,
so the parentheses run `type.__call__()`,
the machinery that invokes `__new__()` and then `__init__()`.
After decoration, `type(Registry)` is `singleton`,
so the same parentheses run `singleton.__call__()` instead.
The wrapped class's constructor runs only when that method calls it.

```python
# singleton_class_demo.py
from singleton_class import Registry

first = Registry("primary", limit=3)
#: singleton.__call__(('primary',), {'limit': 3})
#: constructing Registry
#: Registry.__init__(primary, 3)
first.items.append("spam")
first.items.append("eggs")
second = Registry("secondary", limit=99)
#: singleton.__call__(('secondary',), {'limit': 99})
#: cached Registry: arguments discarded
print(first is second, second.name,
      second.limit, second.items)
#: True primary 3 ['spam', 'eggs']
```

A caller who believes the arguments to `Registry("secondary", limit=99)` took effect holds an object configured by someone else.

`isinstance()` requires a class, a tuple of classes,
or a union as its second argument,
and `Registry` now names a `singleton` object.
So `isinstance(first, Registry)` raises a `TypeError`,
and so does `class Sub(Registry)`:

```python
# test_singleton_class.py
import pytest
from singleton_class import Registry

def test_isinstance_on_the_decorated_name_raises() -> None:
    with pytest.raises(TypeError,
                       match="arg 2 must be a type"):
        isinstance(Registry("primary"), Registry)  # type: ignore

def test_subclassing_the_decorated_name_raises() -> None:
    with pytest.raises(TypeError,
                       match="takes 2 positional"):
        class Sub(Registry):  # type: ignore
            pass
```

`ty` and Pyright reject `Sub` statically.
Its base has type `singleton`, not a class.
Under mypy, which ignores a class decorator's return type,
`Registry` is still a class, so `Sub` passes.

At runtime the `class` statement raises a `TypeError`.
A class statement hands the name, bases,
and namespace to its [metaclass](17_Techniques--Metaprogramming.md#writing-a-metaclass),
and Python takes that metaclass from the type of the base, which is `singleton`.
Calling `singleton` with those three passes four positional arguments to `singleton.__init__()`,
which takes two.
The line `class Sub(Registry)` names `Sub` and `Registry`,
so the error names a class that does not appear in the failing line.
The class decorator causes that confusion.

The decorator weakens static checking as well.
Under `ty` and Pyright,
`Registry("primary", limit=3)` is a call to `singleton.__call__(self, *args: Any, **kwargs: Any) -> Any`.
A wrong argument type passes the check,
and so does a misspelled attribute on the result.
Under mypy the name is still the class, so mypy catches both.
`singleton_class_variable.py` keeps the name pointing at a real class,
and that is the reason to prefer it.

A metaclass can also intercept construction.
[Metaprogramming](17_Techniques--Metaprogramming.md#intercepting-instance-creation)
shows that singleton.
Its metaclass overrides `__call__()`.
That override skips `__new__()` and `__init__()` on every later construction,
so only the first call's arguments reach the constructor.
In a class that overrides `__new__()` instead,
as `singleton_class_variable.py` does, `__new__()` still runs on every call.
That listing's `__new__()` sets `val = []` on the first call and runs `val.append(arg)` on every call,
so each later argument joins the shared list,
where the metaclass form discards it.

[Metaprogramming](17_Techniques--Metaprogramming.md)
also covers `__init_subclass__()` and `__set_name__()`,
the simpler methods that replace most metaclasses.
A singleton needs none of this machinery,
since a module or a cached factory gives you one instance and leaves construction alone.

## Which Should You Use?

Use the lightest tool that fits:

- For almost everything, use a module with module-level state.
  It is the default Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`),
  or override `__new__()` as `singleton_class_variable.py` does.
  Both create the instance on the first call,
  so under threads build it once at import time or use the module form.
- If you want many objects sharing one set of state, use *Borg*,
  but only when something needs those objects to be class instances:
  an existing class-based interface, an `isinstance()` check, or subclassing.
  A module shares that state with every importer and needs no class,
  so shared data alone is no reason to use *Borg*.
- The decorator and metaclass forms work,
  but they are more machinery than the problem usually justifies.

The elaborate *GoF Design Patterns* singleton is largely a workaround for languages where a module is not a first-class,
single-instance namespace.
In Python, a module is that single instance,
so most of that ceremony is unnecessary.

## Exercises

Try each exercise before opening its [solution](../Solutions/23_Patterns--Singleton/).

1.  `singleton_pattern.py` waits for the first construction to build its inner object.
    Modify it to use eager creation,
    creating the inner instance in the class body,
    and remove the sentinel and the guard.
    What does the change give up,
    and which failure from [Tests, Threads, and Locks](#tests-threads-and-locks)
    can no longer occur?
2.  Using `singleton_cached_factory.py` as a starting point,
    create a factory that manages a pool holding a set number of objects
    (say, database connections) and hands them out,
    rather than a single instance.
3.  Rewrite one of this chapter's class-based singletons as a module,
    and argue which you would use in real code.
4.  In `shared_config.py`, replace the mutation with a rebinding,
    `settings = {"theme": "dark"}`.
    Predict both printed values before running it,
    and explain the difference using the [mutate-versus-rebind distinction](#a-module-is-already-a-singleton).
5.  Add a `threading.Lock` inside `settings()` in `singleton_cached_race.py`,
    wrapping only the body of the constructor function, and run it.
    Explain why the object count does not drop to one,
    then fix it without a lock.
6.  Give `singleton_borg.py` a second `Borg` subclass and construct one of each.
    Explain the value you get back,
    and change the code so the two subclasses keep separate shared state.
7.  In `singleton_class_variable.py`,
    remove the two lines of `__new__()` that use `val`.
    Add an `__init__(self, arg: str)` that prints `arg` and sets `self.val = [arg]`.
    Predict what `x.val` holds after the three constructions, then run it.
    Explain the result using what `__new__()` returns.
