# Cleanup

Python manages memory, so most objects do not need explicit cleanup.
However, when an object owns an external resource (a file, a socket, a lock),
you must release it.

## Why `__del__()` Is Not Cleanup {#why-del-is-not-cleanup}

Python calls an object's `__del__()` method when it destroys that object.
This seems like a candidate for releasing resources:

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
It only unbinds the name `c`.
The `counters` list still references each `Counter`,
so no `Counter`'s reference count reaches zero during the loop.
That is why no `deleted` lines appear while the loop runs,
why every `__repr__()` prints `3`,
and why `End of delete loop` prints before any deletion happens.

Python destroys the objects later, at interpreter shutdown,
when it tears down the global `counters` list.
That list holds the only remaining references, so when it goes,
the objects it holds go with it.
The listing ends at `End of delete loop`, the program's last statement,
and each `__del__()` prints only afterward.
Run `cleanup.py` directly and three more groups of lines follow the last one above:

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
the language specifies neither when it runs nor whether it runs at all.
At interpreter shutdown,
the globals a `__del__()` method refers to may already be gone.
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

In this run the objects are destroyed during shutdown,
which is the precarious moment the warning describes.
`Counter` and `print()` were still available, so the output came out cleanly,
but nothing guarantees the teardown order that allowed it.
`__del__()` should do as little as possible, and you should not depend on it.

## Reference Cycles Delay Destruction

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
a separate mechanism that runs periodically rather than at the moment the object becomes unreachable.
`gc.collect()` above forces a run so the timing is visible;
in a real program nothing tells you when it happens.
This is a second reason not to put cleanup in `__del__()`:
one back-reference between two objects is enough to postpone it,
and the code that creates the cycle is often not the code that owns the resource.

## Reliable Alternatives

Three approaches are more reliable:

1. An explicit finalizer such as the `close()` that file objects provide,
   called from a `with` block.
   This runs even when an error interrupts the code.
   [Context Managers](15_Context_Managers.md) covers `with` in full.

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

`finalize()` registers `print(name, "closed")` to run when `a` is destroyed.
The callback receives `name`, not the `Connection`,
so registering the cleanup does not keep the object alive.
`close()` runs the callback immediately.
The second `close()` does nothing: a finalizer runs at most once,
and `alive` reports whether it still can.
When `b` goes away without anyone calling `close()`, the callback still runs,
and it runs before interpreter shutdown rather than during it.

3. A weak reference, which tracks an object without keeping it alive.
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

The key is `id(self)` because the registry needs a key per object, not per name:
two counters could share a name, and one would then displace the other.
Reused `id()` values are not a hazard here,
since the dictionary only ever holds live objects and no two live objects share an id.
When the values need no key at all, `weakref.WeakSet` is the simpler container.
`live_count()` is the size of that registry,
so it reports how many `Counter` objects currently exist.
When an instance loses its last ordinary reference,
in this case when `pop()` removes it from the `counters` list,
the interpreter collects it at once,
and the dictionary drops its entry on its own.
The count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no explicit cleanup call.

A `dict` or `list` as the registry keeps every instance alive forever,
so the count can never fall.
The weak reference allows the registry to prune itself.
The immediate drop in the count is CPython's reference counting at work.
On an implementation with a tracing collector, such as PyPy,
the entries disappear only when its collector runs,
so the counts do not fall promptly.
Unlike the `__del__()` version, this reads the count during normal execution,
so it never depends on the unreliable bookkeeping at interpreter shutdown.

## The Rule

Never put resource release in `__del__()`.
Give a class that owns a resource a `close()` method and a `with` block that calls it,
so the release happens at a point in the program you can see.
Where a callback must still run if the caller forgets,
add `weakref.finalize()` as the backstop, not as the plan.

## Exercises

1.  In `weak_value.py`, change `counters` from a `list` to a `dict` keyed by name,
    then pop entries from that `dict` one at a time and confirm `live_count()` still falls correctly.
2.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    The two do different things to the list object.
    Say what each one does,
    then say what a second name bound to the same list would see after each.
3.  Add a classmethod `live_names()` to `Counter` in `weak_value.py` that returns a sorted list of the `.name` of every live instance,
    by reading `cls._instances.values()`.
4.  In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
    and confirm the output is unchanged:
    nothing is deleted before `End of delete loop` prints.
5.  In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
    Report what `live_count()` prints after each `pop()`,
    and explain the difference in terms of what each container holds.
