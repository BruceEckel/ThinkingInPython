# Singleton: Solutions

## 1. `singleton_pattern.py` rewritten to eager creation

> `singleton_pattern.py` waits for the first construction to build its inner object.
> Modify it to use eager creation,
> creating the inner instance in the class body,
> and remove the sentinel and the guard.
> What does the change give up,
> and which failure from [Tests, Threads, and Locks](../../Chapters/23_Patterns--Singleton.md#tests-threads-and-locks)
> can no longer occur?

<details>
<summary>Where to look</summary>

[Lazy Creation](../../Chapters/23_Patterns--Singleton.md#lazy-creation)
builds the inner object on the first construction,
behind a sentinel and a guard.
Move that construction into the class body so it runs once,
when Python defines the class.
Then read [Tests, Threads, and Locks](../../Chapters/23_Patterns--Singleton.md#tests-threads-and-locks)
for the failure that depends on a first call,
and ask whether a first call still exists.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    # Created once, when the class is defined:
    instance: ClassVar[__OnlyOne] = __OnlyOne()

    def __init__(self, arg: str) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
```

<details>
<summary>Done when</summary>

your file prints the same accumulated `val` list and `False True` that the chapter's `singleton_pattern.py` prints,
and `uv run ty check` passes on it with the sentinel and the guard gone.
You can also name what the change gives up and the failure that no longer occurs.

<details>
<summary>Solution</summary>

If you remove the guard but keep the annotation `ClassVar[__OnlyOne | None]`,
the script still runs and prints the same line.
`ty`, though, reports an `unresolved-attribute` error on `OnlyOne.instance.val.append(arg)`,
because `None` has no `val` attribute.
In the chapter's version, the guard narrows `instance` to the inner class,
so the type checker accepts the `append()` call after it.
Once the class body binds the inner instance, `instance` always holds an object,
so the solution drops `None` from the annotation.

```python
# exercise_1.py
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
print(x.val, x is y, x.instance is y.instance)
#: ['sausage', 'eggs'] False True
```

**Build the instance with the class.**
The sentinel and the guard exist to defer creation,
so removing the deferral removes both.
In the class body, the bare `__OnlyOne()` works.
The qualified `OnlyOne.__OnlyOne()` fails,
since Python binds the name `OnlyOne` after the class body finishes.

**Record each caller's argument.**
`__init__()` shrinks to the one `append`.
Externally the behavior stays the same.

The change gives up the deferral.
Python now builds the inner object at class definition, during module import,
whether or not anything constructs an `OnlyOne`.

Removing the deferral also removes the first-call race from [Tests, Threads, and Locks](../../Chapters/23_Patterns--Singleton.md#tests-threads-and-locks).
In the chapter's version,
two threads racing the first construction can each see the `None` sentinel and each build an inner object.
The class body runs once, during the import,
so the inner object exists before any thread calls `OnlyOne()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A pool of connections instead of one instance

> Using `singleton_cached_factory.py` as a starting point,
> create a factory that manages a pool holding a set number of objects
> (say, database connections) and hands them out,
> rather than a single instance.

<details>
<summary>Where to look</summary>

[When You Want a Class, Cache the Instance](../../Chapters/23_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance)
uses `functools.cache` on a zero-argument function to return one object.
Keep that technique for the pool,
and give the pool a list of available connections and a set of leased ones.
`acquire()` moves a connection from the available list to the leased set,
and `release()` moves it back.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from functools import cache
from exceptions import expect
from record import record

@record
class Connection:
    number: int

class ConnectionPool:
    def __init__(self, size: int) -> None:
        ...

    def acquire(self) -> Connection:
        ...

    def release(self, conn: Connection) -> None:
        ...

@cache
def pool() -> ConnectionPool:
    "Always returns the same ConnectionPool instance."
    ...
```

<details>
<summary>Done when</summary>

two calls to your factory return the same pool,
and with a pool of two a third request raises an exception while both connections are out.
Releasing one makes the next request return that same connection,
and releasing a connection twice raises an exception rather than adding it back.

<details>
<summary>Solution</summary>

If you give `pool()` a `size` parameter with a default of 2,
`@cache` builds one pool for each way a caller writes the call.
In that version, `pool()`, `pool(2)`,
and `pool(size=2)` return three different pools.
After two `acquire()` calls exhaust the pool from `pool()`,
`pool(2).acquire()` still lends a third connection.
[When You Want a Class, Cache the Instance](../../Chapters/23_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance)
shows the same failure with `settings(env)`,
so the solution keeps `pool()`'s signature empty and sets the size in its body.

```python
# exercise_2.py
from functools import cache
from exceptions import expect
from record import record

@record
class Connection:
    number: int

class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._available = [
            Connection(i) for i in range(size)]
        self._leased: set[Connection] = set()

    def acquire(self) -> Connection:
        if not self._available:
            raise RuntimeError("pool exhausted")
        conn = self._available.pop()
        self._leased.add(conn)
        return conn

    def release(self, conn: Connection) -> None:
        self._leased.remove(conn)
        self._available.append(conn)

@cache
def pool() -> ConnectionPool:
    "Always returns the same ConnectionPool instance."
    return ConnectionPool(size=2)

p1 = pool()
p2 = pool()
print(p1 is p2)
#: True
c1 = p1.acquire()
c2 = p1.acquire()
print(c1 != c2)
#: True
expect(RuntimeError, p1.acquire)
#: [RuntimeError] pool exhausted
p1.release(c1)
expect(KeyError, p1.release, c1)
#: [KeyError] Connection(number=1)
c3 = p1.acquire()
print(c3 == c1)
#: True
```

**Hold a limited number of connections.**
The pool keeps the shape of `singleton_cached_factory.py` and changes the contents of the one shared object.
That object holds a set number of `Connection`s instead of a single value,
and tracks which ones it has handed out.

**Lend a connection and take it back.**
`acquire()` and `release()` replace the "get the instance" idea with "borrow one member of a pool and give it back."
[Context Managers](../../Chapters/15_Techniques--Context_Managers.md#an-object-pool)'s `Pool.lease()` does the same,
but puts the member back automatically when the `with` block ends.
Here a caller must remember to call `release()`, and to call it once.

**Refuse a second release.**
With `discard()` in place of `remove()` in `release()`,
a second `release()` puts the same connection into `_available` twice,
so the pool hands one connection to two callers.

**Share one pool.**
The zero-argument `pool()` constructor function still returns one `ConnectionPool` object
(`p1 is p2`), because `@cache` stores its first result.
`singleton_cached_factory.py` uses the same technique for `Settings`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A class-based singleton rewritten as a module

> Rewrite one of this chapter's class-based singletons as a module,
> and argue which you would use in real code.

<details>
<summary>Where to look</summary>

[A Module Is Already a *Singleton*](../../Chapters/23_Patterns--Singleton.md#a-module-is-already-a-singleton)
explains that Python caches a module in `sys.modules` and runs its body once.
Put the shared list at module level, add a function that appends to it,
and use the module from a second file.
For the argument, weigh the code each form needs against what only a class can offer.

<details>
<summary>The shape</summary>

```python
# The shape of only_one.py
def add(arg: str) -> None:
    ...
```

<details>
<summary>Done when</summary>

a second file imports your module, adds `"sausage"` and `"eggs"` through it,
and prints `['sausage', 'eggs']`, and your module defines no class.
You can also name one situation in which the class form is the better choice.

<details>
<summary>Solution</summary>

```python
# only_one.py
val: list[str] = []

def add(arg: str) -> None:
    val.append(arg)
```

```python
# use_only_one.py
import only_one

only_one.add("sausage")
only_one.add("eggs")
print(only_one.val)
#: ['sausage', 'eggs']
```

The module behaves like `OnlyOne` from `singleton_pattern.py`: a shared,
one-and-only-one `val` list to which any part of the program can append.
Python caches the module in `sys.modules`,
so the module is the single shared object.
The solution therefore drops the chapter's machinery: the wrapper class,
the nested private class, the `ClassVar` sentinel,
and the `__getattr__()` delegation.

For real code, prefer the module,
as [A Module Is Already a *Singleton*](../../Chapters/23_Patterns--Singleton.md#a-module-is-already-a-singleton)
argues at the top of the chapter.
The module is less code, lets the caller read the list as a module attribute,
and still holds one list that every importer shares.
The class-based versions are a better choice when the singleton must be a class:
when it must satisfy an interface other code expects,
or when it needs `__new__()`-level control over construction.
Everywhere else, the module is the simpler tool.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Rebinding instead of mutating

> In `shared_config.py`, replace the mutation with a rebinding,
> `settings = {"theme": "dark"}`.
> Predict both printed values before running it,
> and explain the difference using the [mutate-versus-rebind distinction](../../Chapters/23_Patterns--Singleton.md#a-module-is-already-a-singleton).

<details>
<summary>Where to look</summary>

[A Module Is Already a *Singleton*](../../Chapters/23_Patterns--Singleton.md#a-module-is-already-a-singleton)
distinguishes mutating a shared object from rebinding a name.
`from config import settings` creates a second name for the same dict in your module's namespace.
Ask which name an assignment changes, and which names a mutation reaches.

<details>
<summary>Done when</summary>

you write both predictions down first,
and the run prints `{'theme': 'dark'}` for `settings` and `{}` for `config.settings`.
You can say which name the assignment changes,
and why the original mutation reached both names.

<details>
<summary>Solution</summary>

```python
# config.py
print("config body runs")
settings: dict[str, str] = {}
```

```python
# exercise_4.py
import config
from config import settings

#: config body runs
settings = {"theme": "dark"}  # noqa: F811
print(settings)  # [1]
#: {'theme': 'dark'}
print(config.settings)  # [2]
#: {}
```

The prints at `[1]` and `[2]` disagree.

**Give one dict two names.**
`from config import settings` copies a binding.
This module's `settings` and `config.settings` start out as two names for one dict.
The original `settings["theme"] = "dark"` mutates that dict through one of them.
A mutation through either name changes the object both names reference,
so a read through either name returns the changed dict.

**Rebind only the local name.**
Assigning to `settings` points this module's name at a new dict.
The name in `config` still points at the original empty dict,
so the print at `[2]` shows `{}`.

The runtime accepts the rebinding.
The module still imports, the assignment succeeds,
and the local `settings` holds what you put in it.
But the sharing has ended.
Each module now reads a different dict.

**Silence the deliberate rebinding.**
A linter does report the rebinding,
which is why the listing carries `# noqa: F811`.
Ruff reads the assignment as redefining a name the module just imported,
and flags it as an unused import followed by a shadowing binding.
That rule exists because rebinding an imported name is far more often a mistake than an intention.
Here the rebinding is deliberate, so the solution silences the warning.
In ordinary code that warning is an automatic signal that code has rebound a shared name.

To replace the shared dict, assign through the module.
`config.settings = {...}` rebinds the attribute on the one module object rather than a name in your own namespace,
so every later read of `config.settings` returns the new dict.

A name and the object it refers to are different things,
and every singleton built on module state depends on that difference.
Mutate through any name, rebind only through the module.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. A lock in the wrong place

> Add a `threading.Lock` inside `settings()` in `singleton_cached_race.py`,
> wrapping only the body of the constructor function, and run it.
> Explain why the object count does not drop to one,
> then fix it without a lock.

<details>
<summary>Where to look</summary>

[The First-Call Race](../../Chapters/23_Patterns--Singleton.md#the-first-call-race)
shows several threads missing the cache before any of them stores a result.
Compare the order of the three steps in a cached call, the lookup, the body,
and the store, with where the lock sits.
For the fix without a lock,
see [Double-Checked Locking and Eager Creation](../../Chapters/23_Patterns--Singleton.md#double-checked-locking-and-eager-creation):
call the cached function once before any thread starts.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache
from typing import Final

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ...

@cache
def settings() -> Settings:
    ...

@cache
def primed() -> Settings:
    ...
```

<details>
<summary>Done when</summary>

with your lock inside `settings()`,
`singleton_cached_race.py` still prints `True` for `distinct_objects(settings) > 1`,
and your lock-free version builds one object across eight threads,
a count of `1`.
You can name the step of a cached call that runs before your lock.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache
from typing import Final

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

_lock: Final[threading.Lock] = threading.Lock()

@cache
def settings() -> Settings:
    with _lock:  # Too late: the cache miss already happened
        return Settings()

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}) > 1)
#: True

@cache
def primed() -> Settings:
    return Settings()

primed()  # Built once, before any thread asks

with ThreadPoolExecutor(max_workers=8) as pool:
    shared = list(pool.map(lambda _: primed(), range(8)))
print(len({id(s) for s in shared}))
#: 1
```

**Order only the body.**
The count stays above one because the lock guards the wrong step.
A call to `settings()` takes three steps: `@cache` looks for a stored result,
on a miss the body runs, and `@cache` stores what the body returns.
The lock sits inside the body, so it orders only the second step.
All eight threads reach the lookup before any of them has stored anything,
so all eight miss.
Each thread that missed then waits for the lock and runs the body in turn.

**Race eight first calls.**
The lock changes the timing, not the outcome.
Without it the eight constructors overlap,
so the whole run takes about 50 milliseconds.
With it they queue, so the run takes about 400.
Each thread still builds its own `Settings` and still returns the one it built.
`@cache` keeps whichever finished last,
so seven callers hold objects the cache has overwritten.
The lock makes the program slower and leaves the race in place.

The check and the store run inside `functools.cache`,
which is where a per-key lock would go.
`functools.cache` belongs to the standard library,
so you cannot add a lock there.
You can put one around the cached call.
An uncached wrapper function takes the lock,
then calls the cached `settings()` while holding it.
The lookup and the body then both run under one lock,
so eight racing first calls build one object.

The wrapper takes the lock on every call, cache hits included,
because the cache lookup runs inside `settings()`,
which the wrapper calls with the lock held.
The chapter's `singleton_locked_settings.py` takes the lock on every call too.
It drops `@cache` and hand-writes the check inside one lock.

**Build the object before the threads start.**
Without a lock, the fix is to remove the race rather than to order it.
A race needs two threads arriving before the object exists,
so build the object first.
The module body calls `primed()` once,
before the second pool starts any worker thread,
so every call a worker makes to `primed()` is a cache hit.

The chapter's `singleton_eager_factory.py` uses the same technique.
It primes the cache at import, before any thread can ask.
Priming works for the same reason the module form does.
The import system runs a module body once,
and a thread that imports the module while the body is running waits for the body to finish.

The module body builds the object whether or not anything uses it.
For `Settings`, an object that sits idle is fine.
A database connection, though, opens at import, before any caller asks for it.
For a connection, the hand-written lock is the answer.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Two Borg subclasses share one namespace

> Give `singleton_borg.py` a second `Borg` subclass and construct one of each.
> Explain the value you get back,
> and change the code so the two subclasses keep separate shared state.

<details>
<summary>Where to look</summary>

[*Borg*: *Singleton* by Inheritance](../../Chapters/23_Patterns--Singleton.md#borg-singleton-by-inheritance)
points every instance's `__dict__` at a dict held in a class variable.
Check which class owns that dict when a second subclass looks up `_shared_state`.
A subclass that binds its own `_shared_state` in its class body gets separate storage.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import Any, ClassVar

class Borg:
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        ...

class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        ...

class Other(Borg):
    def __init__(self, arg: str) -> None:
        ...

class Separate(Borg):
    # Its own storage
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self, arg: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

one instance of each subclass shows the second construction's `val` from both,
and their `__dict__` attributes are the same object.
After your change, each subclass's instance shows its own `val`,
and the `__dict__` identity test prints `False`.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from typing import Any, ClassVar

class Borg:
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        super().__init__()
        self.val = arg

# A second subclass, sharing Borg's one dict
class Other(Borg):
    def __init__(self, arg: str) -> None:
        super().__init__()
        self.val = arg

x = Singleton("sausage")
y = Other("eggs")
print(x.val, y.val, x.__dict__ is y.__dict__)
#: eggs eggs True

class Separate(Borg):
    # Its own storage
    _shared_state: ClassVar[dict[str, Any]] = {}

    def __init__(self, arg: str) -> None:
        super().__init__()
        self.val = arg

a = Singleton("spam")
b = Separate("beans")
print(a.val, b.val, a.__dict__ is b.__dict__)
#: spam beans False
```

Constructing an unrelated subclass overwrites a value belonging to `Singleton`.
The overwrite passes silently.

**Inherit the base's one dict.**
`_shared_state` is one dict, and it lives on `Borg`.
`Singleton` and `Other` inherit it,
so `self._shared_state` resolves to `Borg`'s dict from both.
The sharing is per-`Borg`, not per-subclass.
The class hierarchy hides that sharing.
Read separately, `Singleton` and `Other` look like independent siblings.

**Give a subclass its own storage.**
The fix is one line per subclass.
`Separate` declares its own `_shared_state`,
so the lookup finds `Separate`'s dict before `Borg`'s dict.
`Separate` is `Other` with that one line added.
The instances of `Separate` share its dict among themselves.
Martelli makes the same point in the article the chapter links:
a subclass that needs state of its own declares it.

The trap is the general shape of a mutable `ClassVar` on a base class,
not a quirk of *Borg*.
The base declares one object, and every subclass inherits that same one.
A subclass gets separate storage when its class body binds a new `_shared_state` instead of mutating the inherited one.

*Borg* makes the trap worse,
because every *Borg* instance writes its attributes into the shared dict by design.
Any subclass that leaves `_shared_state` alone writes into `Borg`'s dict,
beside every other such subclass.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. `__init__()` runs on every construction

> In `singleton_class_variable.py`,
> remove the two lines of `__new__()` that use `val`.
> Add an `__init__(self, arg: str)` that prints `arg` and sets `self.val = [arg]`.
> Predict what `x.val` holds after the three constructions, then run it.
> Explain the result using what `__new__()` returns.

<details>
<summary>Where to look</summary>

[One Instance in a Class Variable](../../Chapters/23_Patterns--Singleton.md#one-instance-in-a-class-variable)
returns the stored instance from `__new__()`.
When `__new__()` returns an instance of the class under construction,
Python then calls `__init__()` on it.
Count how many times Python calls `__init__()` across the three constructions,
and note what each call does to `val`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        ...

    def __init__(self, arg: str) -> None:
        ...
```

<details>
<summary>Done when</summary>

your file prints `sausage`, `eggs`, and `spam` from `__init__()`,
then `['spam'] True` for `x.val` and `x is y is z`.
You can say what `__new__()` returns and why that makes Python call `__init__()` on every construction.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from typing import ClassVar

class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
        if SingletonClassVar.__instance is None:
            SingletonClassVar.__instance = (
                object.__new__(cls))
        return SingletonClassVar.__instance

    def __init__(self, arg: str) -> None:
        print(f"__init__({arg})")
        self.val = [arg]

x = SingletonClassVar("sausage")
#: __init__(sausage)
y = SingletonClassVar("eggs")
#: __init__(eggs)
z = SingletonClassVar("spam")
#: __init__(spam)
print(x.val, x is y is z)
#: ['spam'] True
```

The three names refer to one object,
and that object holds the value from the last construction.

**Return the one instance.**
`__new__()` returns the shared instance every time.
That instance is a `SingletonClassVar`, the class under construction,
so Python runs `__init__()` on it after every call to `__new__()`.

**Reset the state on every construction.**
Each run of `__init__()` rebinds `val` to a new one-item list,
discarding the list before it.
The object is single.
Every caller who constructs it resets its state.

The chapter's listing inherits `object.__init__()` and does all its work in `__new__()`.
There the first construction passes the `None` test and creates `val`.
Every construction, the first included, appends its argument to `val`.

A singleton that keeps an `__init__()` must make it safe to run repeatedly,
for example by returning at once when `hasattr(self, "val")` is true.

The metaclass form in [Metaprogramming](../../Chapters/17_Techniques--Metaprogramming.md#intercepting-instance-creation)
runs `__init__()` once.
Its `__call__()` runs before `__new__()` and `__init__()` and decides whether they run.
On the first construction it builds the instance through `type.__call__()`,
which runs both.
After that it returns the stored instance from `_instances`,
and neither method runs.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
