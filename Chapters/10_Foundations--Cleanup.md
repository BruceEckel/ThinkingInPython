# Cleanup

> Python frees memory on its own,
> and a file, a socket, or a lock is not memory.

## Why `__del__()` Is Not Cleanup {#why-del-is-not-cleanup}

Python calls an object's `__del__()` method when it destroys that object.
That looks like the place to release resources:

```python
# cleanup.py
from typing import ClassVar

class Counter:
    # Number of objects of this class
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "created")
        Counter.count += 1

    def __del__(self) -> None:
        Counter.count -= 1
        print(self.name, "deleted,", Counter.count, "left")

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))
#: First created
#: Second created
#: Third created

for c in counters:
    del c
print(Counter.count)
#: 3
print("End of delete loop")
#: End of delete loop
```

`del c` inside the loop does not delete the object.
It unbinds the name `c` and drops the one reference that name held.
The `counters` list still references each `Counter`,
so every `Counter`'s reference count stays above zero during the loop.

Python destroys the objects later, at interpreter shutdown,
when it tears down the global `counters` list.
That list holds the only remaining references,
so destroying the list drops each `Counter`'s reference count to zero,
and Python destroys each `Counter` in turn.
The listing's markers end at `End of delete loop`,
which the program's last statement prints.
Each `__del__()` prints afterward.
If you run `cleanup.py` as a standalone program,
three more lines follow `End of delete loop`:

    Third deleted, 2 left
    Second deleted, 1 left
    First deleted, 0 left

That was one run on one machine.
This book's output checker executes all of a chapter's listings in one process.
There, Python finalizes the same three objects in the opposite order.

The order in which the three `__del__()` methods run is an implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown,
and it can differ from one CPython build to the next.
Another implementation can destroy the objects in a different order,
or skip the `__del__()` methods at exit.
PyPy, with a tracing garbage collector, is one such implementation.

So `__del__()` is fragile.
The language specifies neither when it runs nor whether it runs.
At interpreter shutdown,
Python may have deleted the globals a `__del__()` method uses,
or set them to `None`.
The Python documentation warns:

> Warning: Due to the precarious circumstances under which `__del__()`
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to `sys.stderr` instead. In particular:
>
> - `__del__()` can be invoked when arbitrary code is being executed,
>   including from any arbitrary thread. If `__del__()` needs to take a
>   lock or invoke any other blocking resource, it may deadlock as the
>   resource may already be taken by the code that gets interrupted to
>   execute `__del__()`.
> - `__del__()` can be executed during interpreter shutdown. As a
>   consequence, the global variables it needs to access (including other
>   modules) may already have been deleted or set to `None`. Python
>   guarantees that globals whose name begins with a single underscore
>   are deleted from their module before other globals are deleted; if
>   no other references to such globals exist, this may help in assuring
>   that imported modules are still available at the time when the
>   `__del__()` method is called.

<!-- The indented transcript above is the chapter's only output that no
     gate checks: it is prose, not a `#:` marker, because it arrives after
     the program's last statement. If CPython changes the order
     list_dealloc drops its items, this block goes stale silently. Verified
     against 3.15.0 (final, 2026-10-11). -->

In the direct run, shutdown destroys the objects,
and shutdown is the precarious moment the warning describes.
`Counter` and `print()` were still available,
so each `__del__()` printed its line.
The teardown order that kept them available is an implementation detail.
Make `__del__()` do as little as possible, and do not depend on it.

The ignored exception the warning describes is the failure most likely to go unnoticed in production:

```python
# del_swallows.py

class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        raise RuntimeError(f"{self.name} not released")

resource = Resource("db")
del resource
print("still running")
#: still running
```

The `RuntimeError` stays out of stdout.
Python prints a traceback to `sys.stderr`, labeled `Exception ignored`,
and discards the exception.
No caller can catch the `RuntimeError`, the exit status is still `0`,
and a test asserting on stdout passes.
In a `with` block, an exception from `close()` propagates to the caller.

## Reference Cycles Delay Destruction

A reference cycle postpones `__del__()` too.
An object that refers to itself stays alive after it becomes unreachable,
whether the reference is direct or runs through another object:

```python
# cycle.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def self_link() -> None:
    node = Node("a")
    node.peer = node
    print(gc.get_referrers(node) == [node])

gc.disable()
self_link()
#: True
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
gc.enable()
print("after collect")
#: after collect
```

CPython frees most objects by counting references.
When an object's reference count drops to zero, CPython destroys the object.
A reference cycle keeps that count above zero.
When `self_link()` returns, Python deletes its local name `node`,
but the object still refers to itself through `peer`,
so its count stays above zero.

Inside `self_link()`,
`gc.get_referrers(node)` searches the objects the collector tracks and returns those that refer directly to `node`.
The only referrer is `node`, so `node` refers to itself.
When an object in a real program stays alive and you don't know why,
`gc.get_referrers()` shows what still holds the object,
as it shows the cycle in this listing.

The cyclic garbage collector frees the node.
The collector is a separate mechanism, triggered by allocation counts.
An unreachable cycle stays in memory until the collector's next run,
so in a real program the allocation counts, rather than your code,
decide when the cycle goes away.
`gc.disable()` above turns off that collector's automatic runs,
and `gc.collect()` then forces a run,
so the `a finalized` line marks the moment of destruction.

Before Python 3.4 the collector put a cycle containing a `__del__()` in `gc.garbage` instead of finalizing it.
Older documentation calls such cycles *uncollectable* garbage.
[PEP 442](https://peps.python.org/pep-0442/) removed that restriction,
so a cycle now delays finalization until the collector runs.

Cycles are one more reason to keep cleanup out of `__del__()`.
One back-reference between two objects is enough to postpone `__del__()`.
The code that creates the cycle often belongs to a different class or module than the code that owns the resource,
so a change in unrelated code can delay the resource's cleanup.

## Reliable Alternatives

Two approaches are more reliable than `__del__()`.

### An Explicit `close()` and a `with` Block

The first is a cleanup method the caller invokes,
such as the `close()` that file objects provide,
which a [`with` block](04_Foundations--Control_Flow.md#context-managers)
runs as the block ends.
Here a class supplies the two methods that `with` calls.
`close()` runs whether or not an error interrupts the block:

```python
# closable.py

class Socket:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False
        print(name, "opened")

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        print(self.name, "closed")

    def __enter__(self) -> Socket:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

with Socket("A") as sock:
    print("using", sock.name)
#: A opened
#: using A
#: A closed
sock.close()
try:
    with Socket("B"):
        raise RuntimeError("boom")
except RuntimeError as e:
    print("caught", e)
#: B opened
#: B closed
#: caught boom
```

`with` calls `__enter__()` at the top of the block and `__exit__()` as control leaves the block.
`__exit__()` calls `close()`, so `close()` runs at the end of the `with` block,
at a line you can identify.
Compare `cleanup.py`,
where the cleanup runs at an unknowable moment after the program's last statement.
[Context Managers](15_Techniques--Context_Managers.md) covers the protocol,
the `@contextmanager` shorthand, and what `__exit__()`'s arguments mean.

`close()` also guards against a second call.
`__exit__()` calls `close()` for you once.
Your own code can call `close()` a second time,
so a real `close()` must accept a repeat call and return at once,
as a file object's `close()` does.

### An `__init__()` That Fails Leaks the Resource {#raising-init-leaks}

`Socket.__init__()` prints "opened" before `__enter__()` runs.
That ordering matters when `__init__()` fails.
If `__init__()` raises an exception after acquiring the resource,
the exception propagates out of the constructor call,
before the `with` statement has an object to enter.
Neither `__enter__()` nor `__exit__()` runs.
The resource leaks silently:

```python
# faulty_init.py

class Faulty:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        raise RuntimeError("boom")

    def __enter__(self) -> Faulty:
        return self

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

try:
    with Faulty("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: caught boom
```

The output goes from `C opened` straight to `caught boom`.
The resource that `__init__()` opened before it failed stays open.

One fix keeps `__init__()` free of resources and acquires them in `__enter__()`,
so a failed construction ends before the first acquisition.
A failure in `__enter__()` leaks the same way, though,
because `__exit__()` runs only after `__enter__()` returns (see exercise 7).
Whichever method acquires the resource,
a step that can fail after the acquisition needs its own `try`/`except`,
which releases the resource before re-raising the exception.

### `weakref.finalize()` as a Backstop

The second reliable approach is `weakref.finalize()`,
which registers a cleanup callback for an object without giving that callback a reference to the object:

```python
# finalizer.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.finalizer = finalize(
            self, print, name, "closed"
        )

    def close(self) -> None:
        self.finalizer()

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.close()  # [1]
#: A closed
a.close()  # [2]
print(a.finalizer.alive, b.finalizer.alive)
#: False True
del b
#: B closed
print("End of program")
#: End of program
```

`finalize()` registers `print(name, "closed")` to run when Python destroys the `Connection`.
A variable, a list slot, or an attribute holds a *strong reference*,
which keeps its object alive.
`finalize()` refers to the `Connection` through a *weak reference*,
which lets Python destroy the object.

The callback receives `name`, not the `Connection`,
so the finalizer refers to the `Connection` through its weak reference alone.
`finalize(self, self.close)` looks tidier, but it gives the callback the object.
The bound method holds a strong reference to the object,
so the object survives until the program ends.

The `close()` at `[1]` runs the callback immediately.
The second `close()`, at `[2]`, finds the finalizer dead and returns `None`.
A finalizer runs at most once.
Its `alive` attribute reports whether it can still run.

`b` holds the only strong reference to its `Connection`,
so `del b` destroys the object here, where the `del c` in `cleanup.py` does not.
Nobody calls `close()`, but the callback still runs,
and it runs before interpreter shutdown rather than during it.
For an object still alive when the program ends,
`finalize()` runs the callback from the `atexit` module's exit handlers,
ahead of the teardown that makes `__del__()` unreliable.

### The `self.close` Trap {#the-self-close-trap}

`finalize()` accepts `self.close` as readily as any other callback,
but the object stays alive until the program exits:

```python
# finalize_trap.py
import gc
from weakref import finalize, ref

class Leaky:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, self.close).atexit = False

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
#: S closed
gc.collect()
print("Leaky alive:", leaky() is not None)
#: Leaky alive: True
print("Safe alive:", safe() is not None)
#: Safe alive: False
```

`ref()` creates a weak reference of your own.
Calling the weak reference returns the object while it lives,
and `None` once Python destroys it.
Reference counting reclaims `Safe` at the `ref()` line,
before `gc.collect()` runs.

`gc.collect()` cannot reclaim `Leaky`, because `Leaky` is still reachable.
`finalize()` keeps every callback in a registry, `self.close` among them.
A bound method is a small object that stores its instance in its `__self__` attribute,
so whatever holds `self.close` holds `Leaky` through it.
A lambda that uses `self`, such as `lambda: print(self.name, "closed")`,
holds the object through its closure.

`Leaky` stays silent, since its callback is waiting in the registry.
No error reports the leak.
With `atexit` left on, the callback runs as the program exits.
A late `L closed` is then the one sign of the leak.
The listing turns `atexit` off on `Leaky`'s finalizer,
so its output ends at `Safe alive: False`.

### A Slotted Class Needs `__weakref__` {#slotted-class-needs-weakref}

`finalize()` needs a target that supports weak references,
and so does the `WeakValueDictionary` in the next section.
A class that declares [`__slots__`](18_Techniques--Performance.md#slots)
lists its instance attributes ahead of time.
Its instances store those attributes in slots instead of a per-instance `__dict__`.
`finalize()` rejects an instance of a class whose `__slots__` omits `__weakref__`:

```python
# slotted_no_weakref.py
from weakref import finalize
from exceptions import expect

class Slot:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

expect(TypeError, finalize, Slot("x"), print, "closed")
#: [TypeError] cannot create weak reference to 'Slot' object

class WeakSlot:
    __slots__ = ("name", "__weakref__")

    def __init__(self, name: str) -> None:
        self.name = name

finalize(WeakSlot("y"), print, "y", "closed")
#: y closed
```

`__slots__` removes the instance `__dict__` and, by default,
the `__weakref__` slot along with it,
so a `Slot` instance has no slot in which to list its weak references.
`ref()`, `weakref.proxy()`,
and `WeakValueDictionary` raise the same `TypeError` on a `Slot`,
since CPython lists every weak reference to an object in that object's `__weakref__` slot.

`WeakSlot` lists `__weakref__` among its slots,
so its instances accept weak references.
The `WeakSlot` instance is a temporary that Python destroys as soon as the statement ends,
so the callback prints `y closed` at that moment.

## Watching Objects Without Holding Them

The weak-reference machinery behind `finalize()` also solves a different problem:
tracking which objects are alive without keeping them alive.
Here, a `WeakValueDictionary` counts live instances,
using `id(self)` as each object's key:

```python
# weak_value.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[
        WeakValueDictionary[int, Counter]
    ] = WeakValueDictionary()

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

print(Counter.live_count())
#: 3
counters.pop()  # Release "Third"
print(Counter.live_count())
#: 2
counters.pop()  # Release "Second"
print(Counter.live_count())
#: 1
counters.clear()  # Release "First"
print(Counter.live_count())
#: 0
```

A `WeakSet` is enough for counting alone.
You need the dictionary as soon as you look instances up rather than count them,
as [*Flyweight*](35_Patterns--Flyweight.md) does.

`id(self)` is the key here because the registry needs one entry per object,
not per name.
Keyed by name, two `Counter` objects that share a name collide,
and the second replaces the first.
Python can give a new object the `id()` of a destroyed one.
That reuse is harmless here,
since the dictionary holds only live objects and each live object has a distinct id.

Here `pop()` or `clear()` removes an instance from the `counters` list,
which drops the instance's last strong reference.
The interpreter collects the instance at once,
and the weak reference's callback removes the instance's entry from the dictionary.
The count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no cleanup call.

A `dict` or `list` as the registry keeps every instance alive forever,
so the count stays at its peak.
Because the `WeakValueDictionary` holds weak references,
it removes each entry when Python destroys the entry's object.

CPython's reference counting makes the count fall immediately.
On an implementation with a tracing collector, such as PyPy,
the dictionary removes the entries when that collector runs,
so the counts fall later.

`cleanup.py` keeps its count inside `__del__()`,
so that count is correct only if `__del__()` runs and succeeds.
[Why `__del__()` Is Not Cleanup](#why-del-is-not-cleanup)
lists the ways `__del__()` can fail.
The weak registry hands that bookkeeping to `WeakValueDictionary`,
whose callback removes each entry when Python destroys the object.

## The Rule

Never release a resource in `__del__()`.
The standard library's file and socket types do release a resource in `__del__()`,
as a diagnostic backstop.
`io.IOBase` gives every file object a `__del__()` that closes it.
A file from `open()` or a `socket.socket` also reports a `ResourceWarning` when Python reclaims it still open:

```python
# resource_warning.py
import gc
import os
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    f = open(os.devnull)
    del f
    gc.collect()
    print(caught[0].category.__name__)
#: ResourceWarning
```

When an open file loses its last reference, Python finalizes the file.
The file's `__del__()` closes it and reports the leak,
at the same unpredictable moment as any other `__del__()`.
On CPython `del f` is that moment.
On an implementation that reclaims the file only when its collector runs,
the `gc.collect()` call runs that collector before the `print()`.

The diagnostic backstop exists to report a file left open,
not to replace `close()`.
It depends on Python reclaiming the object.
A reference cycle defers that collection until the cyclic collector runs,
or until interpreter shutdown if `gc.disable()` has stopped the collector.

Give a class that owns a resource a `close()` method and an `__exit__()` that calls it,
so the cleanup runs as a `with` block ends,
at a point in the program you can see.
Where a callback must still run if the caller forgets,
add `weakref.finalize()` as the backstop, not as the plan.
To track objects without owning them, hold them weakly,
so the registry leaves each object's lifetime as it was.

## Exercises

Try each exercise before opening its [solution](../Solutions/10_Foundations--Cleanup/).

1.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    The two do different things to the list object.
    Say what each one does,
    then say what a second name bound to the same list sees after each.
2.  In `weak_value.py`, add a classmethod `live_names()` to `Counter` that returns a sorted list of the `.name` of every live instance,
    by reading `cls._instances.values()`.
3.  In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
    and confirm the output stays the same:
    no object goes away before `End of delete loop` prints.
4.  In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
    Report what `live_count()` prints after each `pop()`,
    and explain the difference in terms of what each container holds.
5.  In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)`,
    make `close()` print `self.name, "closed"` instead of invoking the finalizer,
    and call `a.finalizer()` where the file now calls `a.close()`.
    Run it again.
    Report when `B closed` now prints relative to `End of program`,
    and say what keeps the `Connection` alive.
6.  In `cycle.py`, change `self_link()` to build a two-object cycle
    (`a.peer = b` and `b.peer = a`) instead of a self-reference.
    Confirm both `__del__()` methods run at `gc.collect()`,
    then remove the `gc.disable()`/`gc.enable()` pair and explain why the language no longer guarantees when the two `finalized` lines appear,
    although this small program still prints them in the same place every run.
7.  In `faulty_init.py`,
    move the `print()` and the `raise` from `__init__()` into `__enter__()`,
    in place of its `return self`.
    Run it and report whether `C closed` prints.
    Then wrap the `raise` in a `try`/`except` that prints the `closed` line before re-raising the exception,
    and confirm `C opened` now has its matching `closed`.
