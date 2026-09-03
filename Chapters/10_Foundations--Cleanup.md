# Cleanup

Python manages memory, so most objects need no explicit cleanup.
However, when an object owns an external resource (a file, a socket, a lock),
you must release it.

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
        print(self.name, "deleted")
        Counter.count -= 1
        if Counter.count == 0:
            print("Last Counter object deleted")
        else:
            print(Counter.count,
                  "Counter objects remaining")

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))
#: First created
#: Second created
#: Third created

for c in counters:
    print(c)
    del c
#: Counter('First' 3)
#: Counter('Second' 3)
#: Counter('Third' 3)
print("End of delete loop")
#: End of delete loop
```

`del c` inside the loop does not delete the object.
It unbinds the name `c` and drops the one reference that name held.
The `counters` list still references each `Counter`,
so no `Counter`'s reference count reaches zero during the loop.
That is why no `deleted` lines appear while the loop runs,
why every `__repr__()` reports a count of `3`,
and why `End of delete loop` prints before any deletion.

Python destroys the objects later, at interpreter shutdown,
when it tears down the global `counters` list.
That list holds the only remaining references, so when it goes,
the objects it holds go with it.
The listing ends at `End of delete loop`, the program's last statement,
and each `__del__()` prints only afterward.
If you run `cleanup.py` directly,
three more pairs of lines follow the last one above:

    Third deleted
    2 Counter objects remaining
    Second deleted
    1 Counter objects remaining
    First deleted
    Last Counter object deleted

That was one run on one machine.
This book's output checker, which executes every chapter in a single process,
finalizes the same three objects in the opposite order.

The order in which the three `__del__()` methods run is an implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown,
and it can differ from one CPython build to the next.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order, or skip the finalizers at exit.

So `__del__()` is fragile:
the language specifies neither when it runs nor whether it runs.
At interpreter shutdown,
the globals a `__del__()` method refers to may have vanished.
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
     against 3.15.0rc1. -->

In the direct run, shutdown destroys the objects,
and shutdown is the precarious moment the warning describes.
`Counter` and `print()` were still available, so the output came out cleanly,
but nothing guarantees the teardown order that allowed it.
`__del__()` should do as little as possible, and you should not depend on it.

The swallowed exception is the failure that costs most in production:

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

The release fails, and stdout says nothing about it.
A traceback goes to `sys.stderr` labeled `Exception ignored`,
but nothing propagates: no caller can catch it, no `finally` runs,
the exit status is still `0`, and a test asserting on stdout passes.
A `close()` call in a `with` block fails loudly instead.

## Reference Cycles Delay Destruction

Unpredictable timing is one of two problems with `__del__()`.
An object that refers to itself, directly or through another object,
outlives the moment it becomes unreachable:

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
    print(gc.get_referrers(node)[0] is node)

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

CPython frees most objects by counting references:
when the last reference to an object goes away, the object goes with it.
A reference cycle defeats that count.
`self_link()` returns and its local `node` disappears,
but the object still refers to itself, so its count never reaches zero.
Before disabling the collector,
`self_link()` calls `gc.get_referrers(node)`,
which lists every object that directly refers to `node`
without collecting or destroying anything.
The only referrer is `node` itself, which confirms the self-reference.
When a real object won't disappear and you don't know why,
`gc.get_referrers()` is how you find what still holds it,
the same way this listing uses it to show its own cycle.
Freeing it takes the cyclic garbage collector,
a separate mechanism that runs on allocation counts rather than when the object becomes unreachable.
`gc.disable()` above keeps that collector from running on its own,
and `gc.collect()` then forces a run,
so the `a finalized` line marks the moment of destruction.
In a real program nothing tells you when the collector runs.
Before Python 3.4 the collector refused to finalize a cycle containing a `__del__()`,
leaving the objects in `gc.garbage`.
[PEP 442](https://peps.python.org/pep-0442/) removed that restriction,
so a cycle now costs only the delay.

Cycles are a second reason not to put cleanup in `__del__()`:
one back-reference between two objects is enough to postpone it,
and the code that creates the cycle often lives far from the code that owns the resource.

## Reliable Alternatives

Two approaches are more reliable:

1. An explicit cleanup method such as the `close()` that file objects provide,
   which a `with` block calls.
   The method runs whether or not an error interrupts the code:

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
sock.close()
#: A opened
#: using A
#: A closed
try:
    with Socket("B"):
        raise RuntimeError("boom")
except RuntimeError as e:
    print("caught", e)
#: B opened
#: B closed
#: caught boom
```

`close()` runs at the end of the `with` block, at a line you can point at,
and the second half shows it running when the body raises an exception.
Compare `cleanup.py`,
where the cleanup runs at an unknowable moment after the program's last statement.
[Context Managers](15_Techniques--Context_Managers.md) covers the protocol,
the `@contextmanager` shorthand, and what `__exit__`'s arguments mean.
This chapter shows the shape.
That one explains it.

`close()` also guards against a second call:
the explicit `sock.close()` after the `with` block prints nothing,
because `self.closed` blocks the repeat.
The `with` protocol calls `close()` for you once;
nothing stops your own code from calling it again,
so a real `close()` must guard itself against being called more than once,
the way a file object's `close()` does.

`Socket.__init__()` also prints "opened" before `__enter__()` ever runs,
which hides a trap: if `__init__()` raises after acquiring the resource,
the `with` statement's target is never bound,
so `__enter__()` and `__exit__()` never run and the resource leaks silently:

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

`C opened` has no matching `closed`:
`__init__()` raised before the `with` statement could bind its target,
so `__exit__()` never ran to release what `__init__()` had already acquired.
Acquire the resource in `__enter__()` instead of `__init__()`
when construction itself can fail,
or wrap the acquisition in its own `try`/`except`
and release what you already opened before re-raising.

2. `weakref.finalize()`,
   which registers a cleanup callback for an object without giving that callback a reference to the object:

```python
# finalizer.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.closer = finalize(self, print, name, "closed")

    def close(self) -> None:
        self.closer()

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.close()
#: A closed
a.close()
print(a.closer.alive, b.closer.alive)
#: False True
del b
#: B closed
print("End of program")
#: End of program
```

`finalize()` registers `print(name, "closed")` to run at `a`'s destruction.
The callback receives `name`, not the `Connection`,
so registering the cleanup does not keep the object alive.
`finalize(self, self.close)` looks tidier and defeats that separation:
the bound method holds a strong reference to the object,
so the object survives until the program ends.
`close()` runs the callback immediately.
The second `close()` does nothing: a finalizer runs at most once,
and `alive` reports whether it still can.
`b` holds the only reference to its `Connection`,
so `del b` destroys the object here, where the `del c` in `cleanup.py` did not.
Nobody calls `close()`, but the callback still runs,
and it runs before interpreter shutdown rather than during it.
For an object still alive when the program ends,
`finalize()` runs the callback from the `atexit` module's exit handlers,
ahead of the teardown that makes `__del__()` unreliable.

The `self.close` mistake produces no error, only an object that never goes away:

```python
# finalize_trap.py
import gc
from weakref import finalize, ref

class Leaky:
    def __init__(self, name: str) -> None:
        self.name = name
        # ty: missing-slot: typeshed's finalize lists no
        # slot for its writable atexit property:
        finalize(self, self.close).atexit = False  # type: ignore

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
#: S closed
gc.collect()
print(leaky() is None, safe() is None)
#: False True
```

A `ref()` is a weak reference: it watches its object without keeping it alive,
and it reports `None` once the object disappears.
So `False True` says the interpreter reclaimed `Safe` and kept `Leaky`.
`Safe` printed `S closed` at the `ref()` line:
reference counting reclaimed it there, before `gc.collect()` ran.
`Leaky` printed nothing, because its callback never ran and nothing failed.
The listing turns `atexit` off on `Leaky`'s finalizer,
so the question it answers is whether the collector reclaimed the object,
rather than whether the callback eventually ran at exit.

Both `finalize()` and, as the next section shows,
`WeakValueDictionary` need the target to support weak references at all.
A class with `__slots__` that omits `__weakref__` cannot be weakly referenced:

```python
# slotted_no_weakref.py
from weakref import finalize

class Slotted:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

try:
    finalize(Slotted("x"), print, "closed")
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

`__slots__` removes the instance `__dict__` and,
by default, the `__weakref__` slot along with it,
so `finalize()` has nothing to attach a reference to.
Listing `__weakref__` among the slots opts back in.

## Watching Objects Without Holding Them

The weak-reference machinery behind `finalize()` also solves a different problem:
observing which objects are alive without being the reason they are.
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

A `WeakSet` would do for counting alone.
You need the dictionary as soon as you look instances up rather than count them,
and [Flyweight](35_Patterns--Flyweight.md) does that with a pool keyed by name.
`id(self)` is the key here because the registry needs one entry per object,
not per name: two counters could share a name,
and one would then displace the other.
Reused `id()` values are harmless,
since the dictionary holds only live objects and no two live objects share an id.
`live_count()` returns the size of that registry,
so it reports how many `Counter` objects currently exist.
When an instance loses its last ordinary reference,
in this case when `pop()` removes it from the `counters` list,
the interpreter collects it at once,
and the dictionary drops its entry on its own.
The count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no explicit cleanup call.

A `dict` or `list` as the registry keeps every instance alive forever,
so the count never falls.
The weak reference lets the registry prune itself.
CPython's reference counting makes the count fall immediately.
On an implementation with a tracing collector, such as PyPy,
the entries disappear when its collector runs, so the counts fall late.
This listing reads the count during normal execution,
where the `__del__()` version waited for interpreter shutdown and its unreliable bookkeeping.

## The Rule

Never put resource release in `__del__()`.
The standard library bends that rule only as a diagnostic backstop:
`io.IOBase` (so every file object) and `socket.socket` each define
a `__del__()` that closes the resource and raises a `ResourceWarning`,
catching a forgotten `close()` rather than replacing it:

```python
# resource_warning.py
import gc
import tempfile
import warnings
from pathlib import Path

path = Path(tempfile.gettempdir()) / "leaky.txt"
path.write_text("data")

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    f = open(path)
    f.read(1)
    del f
    gc.collect()
    print(caught[0].category.__name__)
#: ResourceWarning
path.unlink()
```

Losing the last reference to an open file finalizes it,
and its `__del__()` closes the file and reports the leak,
at the same unpredictable moment as any other `__del__()`.
That backstop exists to catch the mistake, not to be the plan:
it still depends on the object getting collected at all,
which a reference cycle or `gc.disable()` can defer indefinitely.

Give a class that owns a resource a `close()` method and a `with` block that calls it,
so the cleanup runs at a point in the program you can see.
Where a callback must still run if the caller forgets,
add `weakref.finalize()` as the backstop, not as the plan.
To track objects without owning them, hold them weakly,
so the registry cannot become the leak it exists to catch.

## Exercises

1.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    The two do different things to the list object.
    Say what each one does,
    then say what a second name bound to the same list would see after each.
2.  In `weak_value.py`, add a classmethod `live_names()` to `Counter` that returns a sorted list of the `.name` of every live instance,
    by reading `cls._instances.values()`.
3.  In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
    and confirm the output stays the same:
    no object goes away before `End of delete loop` prints.
4.  In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
    Report what `live_count()` prints after each `pop()`,
    and explain the difference in terms of what each container holds.
5.  In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)`,
    make `close()` print `name, "closed"` instead of invoking the finalizer,
    and call `a.closer()` where the file now calls `a.close()`.
    Run it again.
    Report when `B closed` now prints relative to `End of program`,
    and say what keeps the `Connection` alive.
6.  In `cycle.py`, change `self_link()` to build a two-object cycle
    (`a.peer = b` and `b.peer = a`) instead of a self-reference.
    Confirm both finalizers run at `gc.collect()`,
    then remove the `gc.disable()`/`gc.enable()` pair and explain why the output is no longer predictable.
