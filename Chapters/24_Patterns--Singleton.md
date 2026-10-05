# Singleton

> A program has one configuration, one log, one registry of plugins,
> and every part of the program must see the same one.
> A *Singleton* creates that one instance and shares it.

The classic form is a class that refuses a second instance.
Before writing one, ask whether the language solves the problem for you,
the question [When a Pattern Dissolves](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
poses for every pattern.
For *Singleton*, the language already has an answer.

## A Module Is Already a Singleton

Python [imports each module once](06_Foundations--Modules_and_Packages.md)
and caches it in `sys.modules`.
Every `import` after the first produces the same module object.
A module is a singleton.
Whatever it defines at module level exists once per interpreter,
and every importer shares it.
One interpreter, not one machine.
A process pool or an [`InterpreterPoolExecutor`](19_Techniques--Concurrency.md#subinterpreters)
gives each worker its own `sys.modules`,
so each builds its own copy and a write in one is invisible to the rest.
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
import config
import config as again

#: config body runs
print(config is again, config.settings is again.settings)
#: True True
```

Two `import` statements, but `config body runs` prints once.
The first `import` runs `config.py` top to bottom and files the resulting module object in `sys.modules` under the name `config`.
The second finds it there and skips the work,
so the body runs once and builds one `settings` dict.
That is the singleton: not a rule a class enforces,
but a lookup the import system performs.

Every import of `settings`, from anywhere, hands back that same `dict`.
Mutating it through one import is visible through every other:

```python
# shared_config.py
from config import settings

#: config body runs
settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
```

No class, no ceremony.
For most singleton needs, a module solves the problem.

The three listings come down to three steps through `sys.modules`,
and a fourth step shows the mistake that undoes the sharing:

![](_images/singleton_story)

Steps 3 and 4 look alike in code but differ in where the arrow points.
A mutation follows the name's arrow into the dict that `config` holds,
so every importer sees the change.
A rebinding moves the arrow to a new dict and leaves the module's dict as it was.

Mutation makes the sharing work.
Rebinding is the mistake that quietly ends it.
`from config import settings` gives your module its own name for the same `dict` object named by `config.settings`.
Mutating through your name, `settings["theme"] = "dark"`,
changes that shared object, so every module sees it.
But `settings = {}` in your module rebinds only your module's name,
and the two modules silently diverge.
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

A module's state is a set of loose names.
When the shared thing has fields and methods that belong together,
or other code needs a type to name in an annotation, it is a class.
Every construction should then return the same object.
The simplest approach hides construction behind a cached factory:
`functools.cache` applied to a *constructor function*,
an ordinary function that builds and returns an instance of a class.
The constructor function stands in for a direct call to the class constructor.

[`functools.cache`](18_Techniques--Performance.md#caching)
*memoizes* a function.
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

Giving the constructor function a parameter breaks the guarantee.
`functools.cache` keys its cache on the arguments,
so each distinct argument value gets its own entry and its own instance:

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

print(settings("prod") is settings("dev"))
#: False
```

One parameter turns "one singleton" into one singleton per argument value.
A default does not help.
The cache keys on the arguments as the call writes them and does not fill in a default,
so `settings()`, `settings("prod")`,
and `settings(env="prod")` build three objects for one environment.
Keep the constructor function's signature empty,
or accept that you built a cache, not a singleton.

### Nothing Keeps the Class Private

Nothing stops a caller from writing `Settings()` and getting a second instance.
Naming the class `_Settings` marks it internal and keeps it out of `from module import *`,
and that marking is as far as Python goes.
A second underscore adds no strength.
The compiler [mangles](11_Techniques--Testing.md#white-box-and-black-box-tests)
names only inside a class body,
so at module level `__Settings` keeps its name unmangled,
as reachable as any other.
The second underscore's one effect is a trap.
In code inside a class body,
the compiler rewrites a reference to `m.__Settings` into a lookup for `m._TheClass__Settings`,
and that lookup fails.

The cached-factory listings name the class `Settings`, with no underscore,
because the name is public.
`settings()` returns a `Settings`,
so the class appears in the module's public signature.
A caller who annotates the result must write that name,
and a type outsiders must name is not private, whatever its first character.
`_Settings` fits a type that stays inside the module.

Two stronger-looking moves fail the same way.
Deleting the name after building the instance leaves the class reachable.
`type(settings())` hands the class back.
Defining the class inside `settings()` leaves the module no name for it,
since `@cache` runs that body once and the class lives in the function's locals.
`type(settings())` still recovers the class.

Nesting costs the return annotation as well.
`def settings() -> Settings` still parses and runs,
because an annotation evaluates only when something reads it,
so a clean run proves nothing about the name.
Whatever reads the annotation searches the scope containing the function,
while the class lives in the function's own locals.
A type checker reports an unresolved reference,
and `inspect.get_annotations()` raises a `NameError`.
The signature must name something reachable,
so a nested class forces a choice between dropping the annotation and defining a separate `Protocol` to name in its place.

Privacy in Python is advice, not enforcement.
An underscore asks callers to stay out, and nothing makes them.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#encapsulation-leaks)
makes the same case about hidden data.
The reachable class is also useful when a test needs a fresh,
uncached `Settings`.

### Tests, Threads, and Locks

1. A singleton holds shared state, and shared state leaks between tests.
   The cached factory offers a reset the classic forms lack.
   `settings.cache_clear()` discards the instance, so each test can start fresh.

2. Every lazy singleton has a first-call race under threads.
   Concurrent first calls can each run the constructor,
   and each caller can end up holding a different object,
   and the cache keeps one of those objects.
   With a constructor slow enough to widen that race,
   eight threads calling `settings()` at once usually run the constructor eight times and hand back eight different objects.
   When threads can arrive before the singleton exists,
   create it eagerly instead.
   Call `settings()` once at import time, or use the module form,
   which the import system builds exactly once.

3. A [lock](19_Techniques--Concurrency.md#the-gil-does-not-prevent-races)
   is the other fix for that race, but not in the obvious place.
   A `threading.Lock` around the cached function's body changes nothing,
   because every thread misses the cache before reaching the lock.
   They serialize, each still builds an object,
   and the cache keeps whichever finished last.
   The check must run inside the lock, as `singleton_locked_settings.py` shows.

### The First-Call Race

The first-call race is easy to see with a wide enough window:

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
Every thread checks the cache before any of them has filled it,
so each runs the constructor and hands its caller a different object.
Only the object from the last thread to finish stays in the cache.
The other seven are already in the hands of their callers.
The listing prints a comparison instead of the count because the count depends on timing.
The count is eight when every thread misses the cache,
and the sleep makes that the usual result without guaranteeing it.

The fix puts the check inside a lock.
`@cache` keeps its check out of reach,
so the version below drops `@cache` and writes the check by hand:

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

One thread finds `_instance` empty and builds it.
The rest wait on the lock, and each finds `_instance` filled.
Under the same eight-thread race,
the cached version produces more than one object, usually eight.
The locked version produces one, as the printed count confirms.
The sleep stands in for a constructor that does real work,
such as opening a file or a connection.
Without the sleep, the cached version showed no duplicates across twenty trials,
and that silence is the more dangerous case.
A window too narrow to reproduce is still a window.

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
Python decides at compile time that a name a function assigns anywhere is local everywhere in that function,
so without the `global` declaration,
`if _instance is None` reads an unassigned local and raises an `UnboundLocalError`.
Mutate through any name.
Declare only what you rebind.

### Double-Checked Locking and Eager Creation

Every call to the locked `settings()` acquires the lock,
including the thousands that arrive long after the object exists.

The classic escape is *double-checked locking*:
test `_instance` before taking the lock,
take it when the test finds the object missing, then test again inside:

```python
# singleton_double_checked.py
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
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = Settings()
    return _instance

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}))
#: 1
```

The inner test is the one note 3 requires.
The outer test exists to skip the lock once the object is there.
Double-checked locking works, but it depends on two details.
If you drop the inner test,
every thread that passed the outer test before the first assignment builds its own object,
one after another.
And the assignment to `_instance` must be the last step of construction.
The outer test runs without the lock,
so a thread can read `_instance` while another thread is still inside the `with` block.
A version that assigns `_instance = Settings()` and then fills in `data` hands that reader a half-built object.
Depending on two such details is a bad trade for saving one lock acquisition.
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

The priming call is safe for the same reason the module form is.
The import system runs a module body once,
so the object exists before any thread can ask for it.
The race needs laziness, and this listing gives it up on purpose.

If you need the class to hand back one instance from its own constructor,
override `__new__()`, as `singleton_class_variable.py` does.

Modules and cached factories, primed at import time if threads are in play,
should cover your singleton needs.

## The Classic Implementations

*GoF Design Patterns* writes its examples in C++ and Smalltalk,
and it builds the singleton with more apparatus.
Its class blocks direct construction and hands out the sole instance through a class operation,
`Instance()`, which builds the object on the first call.
The cached factory's `settings()` is that operation written as a function.
Python [cannot block construction](#nothing-keeps-the-class-private),
so the class-based forms here keep the constructor public and route every construction to the same shared state.
Each does more work than the module or the cached factory above.

The first form wraps a single instance of a private nested class.
The second form keeps the instance in a class variable.
*Borg* trades one object for one shared set of state,
and the last form is a class decorator.

### Lazy Creation

The classic approach is *lazy*: it builds the inner object on the first call,
and that is why it needs the `None` sentinel and the `if` guard.

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
the compiler mangles it to `_OnlyOne__OnlyOne` wherever it appears inside `OnlyOne`'s body.
`OnlyOne.__OnlyOne`, written from outside the class,
asks for an attribute that does not exist under that name,
so it fails at runtime with `AttributeError`, not at type-checking time.
The outer class controls creation through its constructor.
The first construction of an `OnlyOne` initializes `instance`.
Every later one reuses that inner object,
and each construction appends its argument to that object's shared list.
`__getattr__()` delegates access.
Python calls it only when ordinary attribute lookup fails,
so a name the wrapper does not have, such as `val`,
falls through to the inner object.
The distinct `OnlyOne` instances all proxy to the same `__OnlyOne` object.

`__getattr__()` returns `Any`, and that `Any` stays.
`instance` is one declared field and can say `__OnlyOne | None`,
while `__getattr__()` answers for every name Python fails to find on the wrapper,
so its return type is whatever the inner object holds under that name,
an open set no annotation can list.
Delegation gives up static knowledge to forward every name,
the cost [*Surrogate*](26_Patterns--Surrogate.md#forwarding-with-getattr)
pays throughout.

The laziness is a choice.
When the inner object needs nothing from that first call,
you can create it *eagerly* in the class body instead,
`instance: ClassVar[__OnlyOne] = __OnlyOne()`.
Eager creation removes the sentinel, the guard,
and the first-call race the cached factory meets under threads,
and builds the object whether or not anything uses it (see exercise 1).
(The bare `__OnlyOne()` works because the nested class exists at that point in the body.
The qualified `OnlyOne.__OnlyOne()` fails,
since the name `OnlyOne` stays unbound until its own class body finishes running.)

Either way, `OnlyOne` is a lot of code for what a module does on its own.

### One Instance in a Class Variable

The nested private class is optional.
Here the class keeps the single instance in a class variable.
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

`object.__new__(cls)` builds a `SingletonClassVar`,
so every construction hands back that same instance and `isinstance()` reports `True`.
Python honors whatever object `__new__()` returns,
and that return value decides whether `__init__()` runs.
When `__new__()` returns an instance of the class under construction,
Python runs `__init__()` on it,
so a singleton `__new__()` triggers `__init__()` on the shared instance after *every* construction
(see exercise 7).
`SingletonClassVar` defines no `__init__()`, so `__new__()` does all the work.
A `__new__()` that returns some other object skips `__init__()` and fails `isinstance()` as well.

### Borg: Singleton by Inheritance

[Alex Martelli observes](http://www.aleax.it/Python/5ep.html)
that what you usually want is not one object but one shared set of state.
People can create as many objects as they like,
as long as they all share the same data.
He called that design the *Borg*.^[From the television show *Star Trek: The Next Generation*. The Borg are a hive-mind collective: "we are all one."]
A *Borg* points every instance's `__dict__` at the same storage:

![Three distinct instances share one `__dict__`](_images/borg_shared_state)

The previous singleton designs stand alone,
but you reuse *Borg* through inheritance:

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
# Last write wins: distinct objects, one shared __dict__:
print(x.val, x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: spam False True
```

`Singleton` writes its `__init__()` by hand, and it cannot be a `@dataclass`.
The sharing depends on `super().__init__()` rebinding `self.__dict__` to `_shared_state`,
and a dataclass generates its own `__init__()` that assigns the fields and [skips the base `__init__()`](12_Techniques--Data_Classes_as_Types.md#dataclass-inheritance),
so each instance keeps its own `__dict__`.
The dataclass version still runs,
but the class has quietly stopped being a `Borg`.
A `__post_init__()` that does the rebinding fails differently.
It runs after `__init__()` has assigned the fields,
so the rebinding discards them, and reading `val` raises an `AttributeError`.
The hand-written `__init__()` makes the sharing work,
and silently losing the sharing is worse than failing outright.

The sharing also reaches further than it looks.
`_shared_state` is one dict on `Borg`, so every subclass shares it,
not merely every instance of a single subclass.
A second subclass alongside `Singleton` writes into the same dict,
so constructing one of each leaves both objects reading the value set last.
A subclass that needs storage of its own declares it:
`class Singleton(Borg): _shared_state: ClassVar[dict[str, Any]] = {}`.
The lookup through `self` finds the subclass's dict first,
and Martelli wrote `self._shared_state` instead of `Borg._shared_state` to allow that override.

`test_borg_shares_state_but_not_identity` confirms that the objects differ but share one set of state.
*Borg* has no `cache_clear()`,
so whatever one test leaves in `_shared_state` is still there for the next.
A pytest fixture closes that gap by clearing the dict before each test.
`test_leaves_an_attribute_behind` writes an attribute into the shared dict,
and `test_fixture_clears_shared_state` confirms that the next test finds it gone:

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

### Singleton by Class Decorator

A [class decorator](14_Techniques--Decorators.md#decorating-classes)
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
            print(
                f"constructing {self.constructor.__name__}")
            self.instance = self.constructor(
                *args, **kwargs)
        else:
            print(
                f"using cached {self.constructor.__name__}")
            print(f"discarding {args}, {kwargs}")
        return self.instance

@singleton
class Registry:
    def __init__(self, name: str, *,
                 limit: int = 10) -> None:
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
print(first is second, second.name,
      second.limit, second.items)
#: True primary 3 ['spam', 'eggs']
```

`@singleton` on `Registry` runs `Registry = singleton(Registry)`.
The name `Registry` now refers to a `singleton` object that holds the class,
not to the class.
Why does `__call__()` intercept the constructor for a `Registry`?
To evaluate `obj(...)`,
Python [looks up `__call__()` on the *type* of `obj`](26_Patterns--Surrogate.md#special-methods-bypass-getattr).
For an ordinary class `C`, `type(C)` is `type`,
and the parentheses run `type.__call__()`,
the machinery that invokes `__new__()` and then `__init__()`.
After decoration, `type(Registry)` is `singleton`,
so the same parentheses run `singleton.__call__()` instead,
and the wrapped class's constructor runs only when that method decides to call it.
`__call__()` forwards `*args` and `**kwargs` to the constructor of the wrapped class,
so `Registry("primary", limit=3)` reaches the real constructor unchanged.

Only the first call constructs a `Registry`.
Every later constructor call returns the cached instance and discards the constructor arguments,
so `Registry("secondary", limit=99)` creates no new object.
A caller who believes those arguments took effect holds an object configured by someone else.

`isinstance(first, Registry)` and `class Sub(Registry)` both raise a `TypeError`:

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
Under mypy, which does not apply a class decorator's return type,
`Registry` is still a class and `Sub` passes.
At runtime the `class` statement raises a `TypeError`.
`singleton.__init__()` takes two positional arguments and receives four,
because a class statement hands the name, bases, and namespace to its metaclass,
and Python takes that metaclass from the type of the base, which is `singleton`.
Nothing in `class Sub(Registry)` mentions `singleton`,
so the error names a class that does not appear in the failing line.
That is the confusion a class decorator costs you.

The decorator costs static checking as well.
Under `ty` and Pyright,
`Registry("primary", limit=3)` is a call to `singleton.__call__()`,
which accepts any arguments and returns `Any`.
A wrong argument type passes the check,
and so does a misspelled attribute on the result.
Under mypy the name is still the class, so mypy catches both.
`singleton_class_variable.py` keeps the name pointing at a real class,
and that is the reason to prefer it.

A metaclass can also intercept construction.
[Metaprogramming](17_Techniques--Metaprogramming.md#intercepting-instance-creation)
shows that singleton.
Its metaclass overrides `__call__()`,
and that override skips `__init__()` on every later construction,
so the first call's arguments win.
In a class that overrides `__new__()` instead,
as `singleton_class_variable.py` does, `__new__()` still runs on every call,
unlike the metaclass form.
That listing puts its work inside `__new__()`,
so later calls append to the shared instance instead of overwriting it.
[Metaprogramming](17_Techniques--Metaprogramming.md)
also covers `__init_subclass__()` and `__set_name__()`,
the simpler methods that replace most metaclasses.
A singleton needs none of this machinery,
since a module or a cached factory gives you one instance without intercepting construction.

## Which Should You Use?

Use the lightest tool that fits:

- For almost everything, use a module with module-level state.
  It is the default Python singleton and needs no class.
- If you want a class, hide construction behind a cached factory (`@cache`),
  or override `__new__()` as `singleton_class_variable.py` does.
  Under threads, prime the factory at import time or use the module form.
- If you really want many handles sharing one set of state, use *Borg*,
  but only when something needs those handles to be objects:
  an existing class-based interface, an `isinstance()` check, or subclassing.
  A module shares that state with every importer and needs no class,
  so shared data alone is no reason to use *Borg*.
- The decorator and metaclass forms work,
  but they are more machinery than the problem usually justifies.

The elaborate *GoF Design Patterns* singleton is largely a workaround for languages where a module is not a first-class,
single-instance namespace.
In Python, a module is that single instance, so most of the ceremony falls away.

## Exercises

This chapter's [solutions](../Solutions/24_Patterns--Singleton/) give a hint,
usually the shape of the code, and a full answer for each exercise.

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
    and explain the difference using the [binding-versus-mutation distinction](#a-module-is-already-a-singleton).
5.  Add a `threading.Lock` *inside* `settings()` in `singleton_cached_race.py`,
    wrapping only the body of the cached function, and run it.
    Explain why the object count does not drop to one,
    then fix it without a lock.
6.  Give `singleton_borg.py` a second `Borg` subclass and construct one of each.
    Explain the value you get back,
    and change the code so the two subclasses keep separate shared state.
7.  In `singleton_class_variable.py`,
    remove the two lines of `__new__()` that use `val`.
    Add an `__init__()` that takes `arg`, prints it,
    and sets `self.val = [arg]`.
    Predict what `x.val` holds after the three constructions, then run it.
    Explain the result using what `__new__()` returns.
