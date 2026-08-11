# Cleanup

Python manages memory, so most objects do not need explicit cleanup.
However, when an object owns an external resource (a file, a socket, a lock),
you must release it.

## Why `__del__()` Is Not Cleanup {#why-del-is-not-cleanup}

Python calls an object's `__del__()` method when it destroys that object.
That looks like the place to release resources:

```python
# cleanup.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0  # Number of objects of this class

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
            print(Counter.count, "Counter objects remaining")

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
Running the same file under this book's output checker,
which executes every chapter in a single process,
finalizes the three objects in the opposite order.

The order in which the three finalizers run is an implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown,
and it can differ from one CPython build to the next.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order,
or not run the finalizers before exiting.

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
which is the precarious moment the warning describes.
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

The release failed, and stdout says nothing about it.
A traceback goes to `sys.stderr` labeled "Exception ignored",
but nothing propagates: no caller can catch it, no `finally` runs,
the exit status is still `0`, and a test asserting on stdout passes.
A `close()` call in a `with` block fails loudly instead.

## Reference Cycles Delay Destruction

Unpredictable timing is not the only problem with `__del__()`.
An object that refers to itself, directly or through another object,
is not destroyed at the moment it becomes unreachable:

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

gc.disable()
self_link()
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
Freeing it takes the cyclic garbage collector,
a separate mechanism triggered by allocation counts rather than by the object becoming unreachable.
`gc.disable()` above keeps that collector from running on its own,
and `gc.collect()` then forces a run, so the moment of destruction is visible;
in a real program nothing tells you when the collector runs.
Before Python 3.4 the collector refused to finalize a cycle containing a `__del__()`,
leaving the objects in `gc.garbage`;
[PEP 442](https://peps.python.org/pep-0442/) removed that restriction,
so the only thing a cycle costs now is the delay.

This is a second reason not to put cleanup in `__del__()`:
one back-reference between two objects is enough to postpone it,
and the code that creates the cycle is often not the code that owns the resource.

## Reliable Alternatives

Two approaches are more reliable:

1. An explicit finalizer such as the `close()` that file objects provide,
   called from a `with` block.
   This runs whether or not an error interrupts the code:

```python
# closable.py

class Socket:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")

    def close(self) -> None:
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
where the release happened at an unknowable moment after the program's last statement.
[Context Managers](15_Context_Managers.md) covers the protocol,
the `@contextmanager` shorthand, and what `__exit__`'s arguments mean.
This chapter shows the shape; that one explains it.

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
`finalize(self, self.close)` looks tidier but defeats this:
the bound method holds a strong reference to the object,
which then survives until the program ends.
`close()` runs the callback immediately.
The second `close()` does nothing: a finalizer runs at most once,
and `alive` reports whether it still can.
`del b` destroys the object here, where the `del c` in `cleanup.py` did not,
because `b` held the only reference to it.
Nobody called `close()`, but the callback still runs,
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
        finalize(self, self.close).atexit = False

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
gc.collect()
#: S closed
print(leaky() is None, safe() is None)
#: False True
```

A `ref()` is a weak reference: it watches its object without keeping it alive,
and it reports `None` once the object disappears.
So `False True` says the collector reclaimed `Safe` but not `Leaky`.
`Safe` printed as it was reclaimed; `Leaky` printed nothing,
because its callback never ran and nothing failed.
Turning `atexit` off on `Leaky`'s finalizer narrows the listing to the question at hand,
whether the collector reclaimed the object,
rather than whether the callback eventually ran at exit.

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
    _instances: ClassVar[WeakValueDictionary[int, Counter]] = (
        WeakValueDictionary())

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
The dictionary is what you want as soon as you look instances up rather than count them,
which [Flyweight](35_Flyweight.md) does with a pool keyed by name.
`id(self)` is the key here because the registry needs one entry per object,
not per name: two counters could share a name,
and one would then displace the other.
Reused `id()` values are not a hazard,
since the dictionary holds only live objects and no two live objects share an id.
`live_count()` is the size of that registry,
so it reports how many `Counter` objects currently exist.
When an instance loses its last ordinary reference,
in this case when `pop()` removes it from the `counters` list,
the interpreter collects it at once,
and the dictionary drops its entry on its own.
The count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no explicit cleanup call.

A `dict` or `list` as the registry keeps every instance alive forever,
so the count cannot fall.
The weak reference allows the registry to prune itself.
The immediate drop in the count is CPython's reference counting at work.
On an implementation with a tracing collector, such as PyPy,
the entries disappear only when its collector runs,
so the counts do not fall promptly.
Unlike the `__del__()` version, this reads the count during normal execution,
so it does not depend on the unreliable bookkeeping at interpreter shutdown.

## The Rule

Never put resource release in `__del__()`.
Give a class that owns a resource a `close()` method and a `with` block that calls it,
so the release happens at a point in the program you can see.
Where a callback must still run if the caller forgets,
add `weakref.finalize()` as the backstop, not as the plan.
To track objects without owning them, hold them weakly,
so the registry cannot become the leak it is meant to catch.

## Exercises

1.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    The two do different things to the list object.
    Say what each one does,
    then say what a second name bound to the same list would see after each.
2.  Add a classmethod `live_names()` to `Counter` in `weak_value.py` that returns a sorted list of the `.name` of every live instance,
    by reading `cls._instances.values()`.
3.  In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
    and confirm the output stays the same:
    no object goes away before `End of delete loop` prints.
4.  In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
    Report what `live_count()` prints after each `pop()`,
    and explain the difference in terms of what each container holds.
5.  In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)` and run the file again.
    Report when `B closed` now prints relative to `End of program`,
    and say what keeps the `Connection` alive.
6.  In `cycle.py`, change `self_link()` to build a two-object cycle
    (`a.peer = b` and `b.peer = a`) instead of a self-reference.
    Confirm both finalizers run at `gc.collect()`,
    then remove the `gc.disable()`/`gc.enable()` pair and explain why the output is no longer predictable.
