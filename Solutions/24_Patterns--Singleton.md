# Singleton: Solutions

## 1. `singleton_pattern.py` rewritten to eager initialization

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

The sentinel and the guard existed to defer creation, so removing
the deferral removes both. `instance` now carries the type
`ClassVar[__OnlyOne]` rather than `ClassVar[__OnlyOne | None]`, and
the class body binds it to the inner instance. The bare
`__OnlyOne()` works there. The qualified `OnlyOne.__OnlyOne()`
would fail, since `OnlyOne` is unbound until its own body finishes.
`__init__()` shrinks to the one `append`. Externally nothing
changes: `x.val` accumulates the same way, `x is y` is still
`False`, and `x.instance is y.instance` is still `True`. The cost
is that Python builds the inner object at class definition, during
module import, whether or not anything ever constructs an
`OnlyOne`. Removing the deferral also removes the first-call race from
[Tests, Threads, and Locks](../Chapters/24_Patterns--Singleton.md#tests-threads-and-locks):
two threads racing the first construction could each see the `None`
sentinel and each build an inner object. The single-threaded
import builds the object, leaving no first call to race.

## 2. A pool of connections instead of one instance

```python
# exercise_2.py
from dataclasses import dataclass
from functools import cache

@dataclass(frozen=True)
class Connection:
    number: int

class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._all = [Connection(i) for i in range(size)]
        self._available = list(self._all)
        self._leased: set[Connection] = set()

    def acquire(self) -> Connection:
        if not self._available:
            raise RuntimeError("pool exhausted")
        conn = self._available.pop()
        self._leased.add(conn)
        return conn

    def release(self, conn: Connection) -> None:
        self._leased.discard(conn)
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
try:
    p1.acquire()
except RuntimeError as e:
    print("caught:", e)
#: caught: pool exhausted
p1.release(c1)
c3 = p1.acquire()
print(c3 == c1)
#: True
```

`@cache` on the zero-argument `pool()` constructor function still
guarantees exactly one `ConnectionPool` object exists (`p1 is p2`),
the same trick `singleton_cached_factory.py` uses for `Settings`.
The change is what that one object *is*: instead of holding a
single value, it holds a fixed collection of `Connection`s and
tracks which ones it has handed out. `acquire()` and `release()`
replace the "get the instance" idea with "borrow one member of a
pool and give it back,"
similar in spirit to [Context Managers](../Chapters/15_Techniques--Context_Managers.md#an-object-pool)'s
`Pool.lease()`, but without the automatic return a context manager
guarantees. Here a caller must remember to call `release()`.

## 3. A class-based singleton rewritten as a module

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

The module behaves exactly like `OnlyOne` from
`singleton_pattern.py`: a shared, one-and-only-one `val` list that
any part of the program can append to. The design needs no wrapper
class, no nested private class, no `ClassVar` sentinel, and no
`__getattr__()` delegation, because the module itself is already
the single shared object Python caches in `sys.modules`.

For real code, prefer the module. It is less code, has no
indirection to read through, and gets the same guarantee.
[A Module Is Already a Singleton](../Chapters/24_Patterns--Singleton.md#a-module-is-already-a-singleton)
makes that argument at the top of the chapter. The class-based
versions only earn their complexity when something genuinely needs
the shape of a class, such as participating in an interface other
code expects, or needing `__new__()`-level control over
construction. Absent that requirement, a module is the simpler tool
that already does the job.

## 4. Rebinding instead of mutating

```python
# config.py
settings: dict[str, str] = {}
```

```python
# exercise_4.py
import config
from config import settings

settings = {"theme": "dark"}  # noqa: F811
print(settings)
#: {'theme': 'dark'}
print(config.settings)
#: {}
```

The two prints disagree, and that is the whole lesson.
`from config import settings` copies a binding: two names, this
module's `settings` and `config.settings`, initially pointing at
one dict. Mutating through either name, as the original
`settings["theme"] = "dark"` did, changes the object both names
refer to, so both see the change. Assigning to `settings` changes
only which object this module's name refers to. The name in
`config` still points at the original empty dict, which is why the
second print shows `{}`.

Nothing warns you at runtime. The module still imports, the
assignment succeeds, and the local `settings` holds what you put in
it. The sharing is simply gone: each module now reads a different
dict, with no error to mark the split. Importing the module and
assigning `config.settings = {...}` replaces the value everyone
sees, because that assignment rebinds the attribute on the one
module object rather than a name in your own namespace.

A linter does object, which is why the listing carries
`# noqa: F811`. Ruff reads the assignment as redefining a name the
module just imported, and flags it as an unused import followed by
a shadowing binding. That rule exists because rebinding an imported
name is far more often a mistake than an intention. Here the
rebinding is deliberate, so the solution silences the warning, but
in ordinary code the warning is the one automatic signal you get
that a shared name has stopped being shared.

A name and the object it refers to are different things, and every
singleton built on module state depends on that difference. Mutate
through any name, rebind only through the module.

## 5. A lock in the wrong place

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

The count does not drop, because the lock guards the wrong step. A
call to `settings()` takes two steps: `@cache` looks for a stored
result, and, on a miss, the body runs. The lock sits inside the
body, so it can only order the second step. All eight threads reach
the lookup before any of them has stored anything, so all eight
miss. Each is already committed to running the body before the
first one takes the lock.

The lock changes the timing, not the outcome. Without it the eight
constructors overlap and the whole run takes about 50 milliseconds.
With it they queue, and the run takes about 400. Each thread still
builds its own `Settings` and still returns the one it built.
`@cache` keeps whichever finished last, so seven callers walk away
holding objects the cache has never heard of. The lock made the
program slower and fixed nothing, the worst outcome a lock can
produce.

You cannot move the lock to the right place either. The right place
is inside `functools.cache`, where the check and the store live,
and you do not own that code. That is why the chapter's
`singleton_locked_settings.py` drops `@cache` and hand-writes the
check: once you need the test and the construction inside one lock,
you need to own both.

Without a lock, the fix is to remove the race rather than to order
it. A race needs two threads arriving before the object exists, so
build the object first. The module body calls `primed()` once,
before any worker thread starts, and by the time the pool exists
every call is a cache hit. The count is `1`. Priming the cache this
way is `singleton_eager_factory.py` from the chapter, and it works
for the same reason the module form does: the import system runs a
module body exactly once, so import time is single-threaded by
guarantee rather than by hope.

The trade is that the module body builds the object whether or not
anything uses it. For settings that cost is nothing. For a database
connection it may be real, and then the hand-written lock is the
honest answer.

## 6. Two Borg subclasses share one namespace

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
unrelated subclass overwrote a value belonging to `Singleton`, and
nothing reported it.

`_shared_state` is one dict, and it lives on `Borg`. `Singleton` and
`Other` do not declare their own, so `self._shared_state` resolves
to `Borg`'s dict from both, and `Borg.__init__()` points both
instances' `__dict__` at that one dict. The sharing the pattern
promises is per-`Borg`, not per-subclass. The class hierarchy hides
that sharing: `Singleton` and `Other` have no visible connection to
each other.

The fix is one line per subclass. `Separate` declares its own
`_shared_state`, so the lookup stops there instead of reaching `Borg`,
and its instances share with each other and with nobody else. Martelli
makes the same point in the article the chapter links: a subclass that
needs state of its own says so.

The trap is the general shape of a mutable `ClassVar` on a base
class, not a quirk of *Borg*. The base declares one object, and
every subclass inherits that same one. A subclass that assigns to
it instead of mutating it gets a private copy, while the others
keep sharing. *Borg* sharpens the trap: mutation is the whole
design, so every version of the pattern carries it.
