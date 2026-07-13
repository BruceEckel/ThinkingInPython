# Cleanup

Python manages memory for you, so most objects need no explicit cleanup.
However, when an object owns an outside resource (a file, a socket, a lock),
you must release it.
The Python garbage collector calls an object's `__del__()` method when it collects that object.
This seems like a candidate for releasing resources:

```python
# cleanup.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0   # Number of objects of this class

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

for c in counters:
    print(c)
    del c
print("End of delete loop")
#: First created
#: Second created
#: Third created
#: Counter('First' 3)
#: Counter('Second' 3)
#: Counter('Third' 3)
#: End of delete loop
```

`del c` inside the loop does not delete the object.
It only unbinds the name `c`.
The `counters` list still references each `Counter`,
so its reference count never reaches zero during the loop.
That is why no `deleted` lines appear while the loop runs,
and why every `__repr__()` prints `3`.
Python has destroyed nothing yet,
so the class attribute `count` is still `3` for all three.
The `End of delete loop` line, printed before any deletion,
confirms that the loop destroys nothing.

Python destroys the objects later, at interpreter shutdown,
when it tears down the global `counters` list.
That list holds the only remaining references, so when it goes,
the objects it holds go with it.
That is why the `deleted` lines are missing from the output above.
The listing ends at `End of delete loop`, the program's last statement,
and each `__del__()` prints only afterward.
Run `python cleanup.py` directly to see those lines appear.

The order in which the three finalizers run is an unstable implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown,
and it can differ from one CPython build to the next.
Whether `__del__()` runs before the program exits is a reference-counting detail,
not a guarantee.
The language does not promise when, or in what order, `__del__()` runs.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order,
or not run the finalizers before exit.

Thus, leaning on `__del__()` is fragile because Python does not guarantee the timing.
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

In this run the deletions happen during shutdown,
which is the precarious moment the warning describes.
`Counter` and `print()` were still available, so the output came out cleanly,
but nothing guarantees the teardown order that allowed it.
`__del__()` should do as little as possible, and you should not depend on it.

Two approaches are more reliable:

1. An explicit finalizer such as the `close()` that file objects provide,
   called from a `with` block.
   This runs even when an error interrupts the code.
   [Context Managers](15_Context_Managers.md) covers `with` in full.

2. A weak reference, which tracks an object without keeping it alive.
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
counters.pop()               # Release "Third"
print(Counter.live_count())
#: 2
counters.pop()               # Release "Second"
print(Counter.live_count())
#: 1
counters.clear()             # Release "First"
print(Counter.live_count())
#: 0
```

Storing each instance in a `WeakValueDictionary` tracks it without keeping it alive.
`live_count()` is the size of that registry,
so it reports how many `Counter` objects currently exist.
When an instance loses its last ordinary reference,
in this case when `pop()` removes it from the `counters` list,
the interpreter collects it at once,
and the dictionary drops its entry on its own.
The count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no explicit cleanup call.

A plain `dict` or `list` as the registry would keep every instance alive forever,
so the count could never fall.
The weak reference allows the registry to prune itself.
The immediate drop in the count is CPython's reference counting at work.
On an implementation with a tracing collector, such as PyPy,
the entries disappear only when its collector runs,
so the counts would not fall promptly.
Unlike the `__del__()` version, this reads the count during normal execution,
so it never depends on the unreliable bookkeeping at interpreter shutdown.

## Exercises

1.  In `weak_value.py`, change `counters` from a `list` to a plain `dict` keyed by name,
    then pop entries from that `dict` one at a time and confirm `live_count()` still falls correctly.
2.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    Explain, in terms of what `counters` refers to,
    why rebinding has the same effect as clearing.
3.  Add a classmethod `live_names()` to `Counter` in `weak_value.py` that returns a sorted list of the `.name` of every live instance,
    by reading `cls._instances.values()`.
4.  In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
    and confirm the output is unchanged:
    nothing is deleted before `End of delete loop` prints.
