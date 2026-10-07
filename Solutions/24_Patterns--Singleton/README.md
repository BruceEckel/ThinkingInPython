# Singleton: Solutions

## 1. `singleton_pattern.py` rewritten to eager initialization

> `singleton_pattern.py` waits for the first construction to build its inner object.
> Modify it to use *eager initialization*,
> creating the inner instance in the class body,
> and remove the sentinel and the guard.
> What did the change cost,
> and which failure from [Tests, Threads, and Locks](../../Chapters/24_Patterns--Singleton.md#tests-threads-and-locks)
> can no longer occur?

<details>
<summary>Where to look</summary>

[Lazy Creation](../../Chapters/24_Patterns--Singleton.md#lazy-creation) builds the inner object on the first construction, behind a sentinel and a guard.
Move that construction into the class body so it runs once, when Python defines the class.
Then read [Tests, Threads, and Locks](../../Chapters/24_Patterns--Singleton.md#tests-threads-and-locks) for the failure that depends on a first call, and ask whether a first call still exists.

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
<summary>Solution</summary>

If you remove the guard but keep the annotation `ClassVar[__OnlyOne | None]`,
the script still runs and prints the same line,
but `ty` reports an `unresolved-attribute` error on `OnlyOne.instance.val.append(arg)`,
because `val` is not defined on `None`.
In the chapter's version, the guard is the type checker's evidence that `instance` holds an object.
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

**Build the instance with the class.** The sentinel and the guard exist to defer creation, so removing
the deferral removes both. `instance` now carries the type
`ClassVar[__OnlyOne]` rather than `ClassVar[__OnlyOne | None]`, and
the class body binds it to the inner instance. The bare
`__OnlyOne()` works there. The qualified `OnlyOne.__OnlyOne()`
fails, since Python binds the name `OnlyOne` after the class
body finishes.

**Record each caller's argument.** `__init__()` shrinks to the one `append`. Externally the behavior
stays the same: `x.val` accumulates the same way, `x is y` is still
`False`, and `x.instance is y.instance` is still `True`.

The cost
is that Python builds the inner object at class definition, during
module import, whether or not anything constructs an
`OnlyOne`. Removing the deferral also removes the first-call race from
[Tests, Threads, and Locks](../../Chapters/24_Patterns--Singleton.md#tests-threads-and-locks):
two threads racing the first construction could each see the `None`
sentinel and each build an inner object. The single-threaded
import builds the object, leaving no first call to race.

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

[When You Want a Class, Cache the Instance](../../Chapters/24_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance) uses `functools.cache` on a zero-argument function to return one object.
Keep that technique for the pool, and give the pool a list of available connections and a set of leased ones.
`acquire()` moves a connection from one to the other, and `release()` moves it back.

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
<summary>Solution</summary>

If you give `pool()` a `size` parameter with a default of 2,
`@cache` builds one pool for each way a caller writes the call.
In that version `pool()`, `pool(2)`, and `pool(size=2)` return three different pools,
and after two `acquire()` calls exhaust the first, `pool(2).acquire()` lends a third connection.
[When You Want a Class, Cache the Instance](../../Chapters/24_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance) shows the same failure with `settings(env)`,
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

**Hold a closed set of connections.** The change from
`singleton_cached_factory.py` is in what the one shared object holds.
Instead of holding a single value, it holds a set number of
`Connection`s and tracks which ones it has handed out.

**Lend a connection and take it back.** `acquire()` and `release()`
replace the "get the instance" idea with "borrow one member of a
pool and give it back,"
similar in spirit to [Context Managers](../../Chapters/15_Techniques--Context_Managers.md#an-object-pool)'s
`Pool.lease()`, but without the automatic return a context manager
guarantees. Here a caller must remember to call `release()`, and
to call it once.

**Refuse a second release.** `release()` removes the connection from `_leased`
with `remove()`, which raises a `KeyError` for a connection that is
not on lease. With `discard()` there, a second `release()` would
put the same connection into `_available` twice, and the pool would
hand one connection to two callers.

**Share one pool.** `@cache` on the zero-argument `pool()` constructor function still
yields one `ConnectionPool` object (`p1 is p2`), the same technique
`singleton_cached_factory.py` uses for `Settings`.

</details>
</details>
</details>

## 3. A class-based singleton rewritten as a module

> Rewrite one of the class-based singletons above as a module,
> and argue which you would use in real code.

<details>
<summary>Where to look</summary>

[A Module Is Already a *Singleton*](../../Chapters/24_Patterns--Singleton.md#a-module-is-already-a-singleton) explains that Python caches a module in `sys.modules` and runs its body once.
Put the shared list at module level, add a function that appends to it, and use it from a second file.
For the argument, weigh the code each form needs against what only a class can offer.

<details>
<summary>The shape</summary>

```python
# The shape of only_one.py
def add(arg: str) -> None:
    ...
```

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

The module behaves like `OnlyOne` from
`singleton_pattern.py`: a shared, one-and-only-one `val` list to
which any part of the program can append. The module is the single
shared object Python caches in `sys.modules`, so the solution drops
the chapter's machinery: the wrapper class, the nested private
class, the `ClassVar` sentinel, and the `__getattr__()` delegation.

For real code, prefer the module. It is less code, has no
indirection to follow, and gets the same guarantee.
[A Module Is Already a *Singleton*](../../Chapters/24_Patterns--Singleton.md#a-module-is-already-a-singleton)
makes that argument at the top of the chapter. The class-based
versions are worth their complexity when something needs the shape
of a class, such as participating in an interface other code
expects, or needing `__new__()`-level control over construction.
Absent that requirement, a module is the simpler tool.

</details>
</details>
</details>

## 4. Rebinding instead of mutating

> In `shared_config.py`, replace the mutation with a rebinding,
> `settings = {"theme": "dark"}`,
> and add `import config` plus `print(config.settings)` at the end.
> Predict both printed values before running it,
> and explain the difference using the [binding-versus-mutation distinction](../../Chapters/24_Patterns--Singleton.md#a-module-is-already-a-singleton).

<details>
<summary>Where to look</summary>

[A Module Is Already a *Singleton*](../../Chapters/24_Patterns--Singleton.md#a-module-is-already-a-singleton) distinguishes mutating a shared object from rebinding a name.
`from config import settings` creates a second name for the same dict in your module's namespace.
Ask which name an assignment changes, and which names a mutation reaches.

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
print(settings)
#: {'theme': 'dark'}
print(config.settings)
#: {}
```

The two prints disagree, and the exercise turns on why.

**Give one dict two names.** `from config import settings` copies a binding: two names, this
module's `settings` and `config.settings`, initially pointing at
one dict. Mutating through either name, as the original
`settings["theme"] = "dark"` does, changes the object both names
reference, so both see the change.

**Rebind only the local name.** Assigning to `settings` points
this module's name at a new dict. The name in `config` still
points at the original empty dict, so the second print shows `{}`.

Nothing warns you at runtime. The module still imports, the
assignment succeeds, and the local `settings` holds what you put in
it. The sharing is simply gone. Each module now reads a different
dict, with no error to mark the split. Importing the module and
assigning `config.settings = {...}` replaces the value every reader
of `config.settings` sees, because that assignment rebinds the
attribute on the one module object rather than a name in your own
namespace.

**Silence the deliberate rebinding.** A linter does object, which is why the listing carries
`# noqa: F811`. Ruff reads the assignment as redefining a name the
module just imported, and flags it as an unused import followed by a
shadowing binding. That rule exists because rebinding an imported
name is far more often a mistake than an intention. Here the
rebinding is deliberate, so the solution silences the warning, but
in ordinary code the warning is the one automatic signal you get
that code has rebound a shared name.

A name and the object it refers to are different things, and every
singleton built on module state depends on that difference. Mutate
through any name, rebind only through the module.

</details>
</details>

## 5. A lock in the wrong place

> Add a `threading.Lock` *inside* `settings()` in `singleton_cached_race.py`,
> wrapping only the body of the cached function, and run it.
> Explain why the object count does not drop to one,
> then fix it without a lock.

<details>
<summary>Where to look</summary>

[The First-Call Race](../../Chapters/24_Patterns--Singleton.md#the-first-call-race) shows several threads missing the cache before any of them stores a result.
Compare the order of the two steps in a cached call, the lookup and the body, with where the lock sits.
For the fix without a lock, see [Double-Checked Locking and Eager Creation](../../Chapters/24_Patterns--Singleton.md#double-checked-locking-and-eager-creation): call the cached function once before any thread starts.

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

**Order only the body.** The count does not drop, because the lock guards the wrong step. A
call to `settings()` takes two steps: `@cache` looks for a stored
result, and, on a miss, the body runs. The lock sits inside the
body, so it orders only the second step. All eight threads reach
the lookup before any of them has stored anything, so all eight
miss. Each is already committed to running the body before the
first one takes the lock.

**Race eight first calls.** The lock changes the timing, not the outcome. Without it the eight
constructors overlap and the whole run takes about 50 milliseconds.
With it they queue, and the run takes about 400. Each thread still
builds its own `Settings` and still returns the one it built.
`@cache` keeps whichever finished last, so seven callers hold
objects the cache no longer holds. The lock makes the program
slower and fixes nothing.

You cannot put the lock inside `functools.cache`,
where the check and the store live and where a per-key lock would sit,
because you do not own that code.
You can put it around the cached call.
An uncached wrapper function takes the lock and calls the cached `settings()` inside it,
so the lookup and the body both run under one lock,
and eight racing first calls build one object.

The cost is that every call takes the lock, not just the first,
because the wrapper cannot see a hit until it has asked the cache.
The chapter's `singleton_locked_settings.py` pays the same cost.
It drops `@cache` and hand-writes the check inside one lock.

**Build the object before the threads start.** Without a lock, the fix is to remove the race rather than to order
it. A race needs two threads arriving before the object exists, so
build the object first. The module body calls `primed()` once,
before any worker thread starts, and by the time the pool exists
every call is a cache hit. The count is `1`.

Priming the cache before any worker thread starts is
`singleton_eager_factory.py` from the chapter, and it works for the
same reason the module form does. The import system runs a module
body once, and a thread that imports the module while the body is
running waits for the body to finish.

The trade is that the module body builds the object whether or not
anything uses it. For settings that cost is negligible. For a database
connection it may be real, and then the hand-written lock is the
answer.

</details>
</details>
</details>

## 6. Two Borg subclasses share one namespace

> Give `singleton_borg.py` a second `Borg` subclass and construct one of each.
> Explain the value you get back,
> and change the code so the two subclasses keep separate shared state.

<details>
<summary>Where to look</summary>

[*Borg*: *Singleton* by Inheritance](../../Chapters/24_Patterns--Singleton.md#borg-singleton-by-inheritance) points every instance's `__dict__` at a dict held in a class variable.
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

`x.val` is `"eggs"`, the value `Other` set. Constructing an
unrelated subclass overwrites a value belonging to `Singleton`, and
nothing reports the overwrite.

**Inherit the base's one dict.** `_shared_state` is one dict, and it lives on `Borg`. `Singleton` and
`Other` do not declare their own, so `self._shared_state` resolves
to `Borg`'s dict from both, and `Borg.__init__()` points both
instances' `__dict__` at that one dict. The sharing is per-`Borg`,
not per-subclass. The class hierarchy hides that sharing.
`Singleton` and `Other` have no visible connection to each other.

**Give a subclass its own storage.** The fix is one line per subclass. `Separate` declares its own
`_shared_state`, so the lookup stops there instead of reaching `Borg`,
and its instances share with each other and with nobody else. Martelli
makes the same point in the article the chapter links: a subclass that
needs state of its own says so.

The trap is the general shape of a mutable `ClassVar` on a base
class, not a quirk of *Borg*. The base declares one object, and
every subclass inherits that same one. A subclass that binds its own
`_shared_state` in its class body, instead of mutating the inherited one,
gets storage of its own, while the others keep sharing. *Borg*
sharpens the trap. Mutation is its design, so every version of the
pattern carries the trap.

</details>
</details>
</details>

## 7. `__init__()` runs on every construction

> In `singleton_class_variable.py`,
> remove the two lines of `__new__()` that use `val`.
> Add an `__init__()` that takes `arg`, prints it,
> and sets `self.val = [arg]`.
> Predict what `x.val` holds after the three constructions, then run it.
> Explain the result using what `__new__()` returns.

<details>
<summary>Where to look</summary>

[One Instance in a Class Variable](../../Chapters/24_Patterns--Singleton.md#one-instance-in-a-class-variable) returns the stored instance from `__new__()`.
When `__new__()` returns an instance of the class under construction, Python then calls `__init__()` on it.
Count how many times Python calls `__init__()` across the three constructions, and what each call does to `val`.

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

`x.val` is `['spam']`. The three names refer to one object, and
that object holds the value from the last construction.

**Return the one instance.** `__new__()` returns the shared instance every time. That instance
is a `SingletonClassVar`, the class under construction, so Python
runs `__init__()` on it after every call to `__new__()`.

**Reset the state on every construction.** The trace
shows three runs. Each one rebinds `val` to a new one-item list,
and the lists from the first two constructions are gone. The
object is single, and every caller who constructs it resets its
state.

The chapter's listing avoids the reset by defining no `__init__()`.
Its `__new__()` does the work, and the `None` test there separates
the first construction, which creates `val`, from the later ones,
which append to it. A singleton that keeps an `__init__()` must
make it safe to run repeatedly, for example by returning at once
when `hasattr(self, "val")` is true.

The metaclass form in
[Metaprogramming](../../Chapters/17_Techniques--Metaprogramming.md#intercepting-instance-creation)
runs `__init__()` once. Its `__call__()` runs before `__new__()` and
`__init__()`, and after the first construction it calls neither.

</details>
</details>
</details>
