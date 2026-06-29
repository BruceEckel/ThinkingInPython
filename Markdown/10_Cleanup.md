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
        print(name, 'created')
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, 'deleted')
        Counter.count -= 1
        if Counter.count == 0:
            print('Last Counter object deleted')
        else:
            print(Counter.count, 'Counter objects remaining')

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
Each `Counter` is still referenced by the `counters` list,
so its reference count never reaches zero during the loop.
That is why no `deleted` lines appear while the loop runs,
and why every `__repr__()` prints `3`.
Nothing has been destroyed yet, so the class attribute `count` is still `3` for all three.
The `End of delete loop` line, printed before any deletion, confirms that the loop destroys nothing.

The objects are destroyed later, at interpreter shutdown,
when the global `counters` list is torn down.
That list holds the only remaining references,
so when it goes, the objects it holds go with it.

This is why the `deleted` lines are missing from the output above.
The listing ends at `End of delete loop` because that is the program's last statement.
Each `__del__()` runs only afterward, at interpreter shutdown, so the lines it prints come after the captured output rather than inside it.
Run `python cleanup.py` directly to see them appear after `End of delete loop`.

The order in which the three finalizers run is an unstable implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown, and it can differ from one CPython build to the next.
Even the fact that `__del__()` runs before the program exits is a reference-counting detail, not a guarantee.
The language does not promise when, or in what order, `__del__()` runs.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order, or not run the finalizers before exit at all.

Thus, leaning on `__del__()` is fragile because the timing is not guaranteed.
At interpreter shutdown the globals it refers to may already be gone.
The Python documentation warns:

> Warning: Due to the precarious circumstances under which `__del__()`
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to `sys.stderr` instead. Also, when
> `__del__()` is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the `__del__()` method may already have been deleted*. For this
> reason, `__del__()` methods should do the absolute minimum needed to
> maintain external invariants.

In this run the deletions happen during shutdown,
exactly the precarious moment the warning describes.
`Counter` and `print()` were still available, so the output came out cleanly,
but the teardown order that allowed that is not guaranteed.
So `__del__()` should do as little as possible, and you should not depend on it.

Two approaches are more reliable:

1. An explicit finalizer such as the `close()` that file objects provide,
   called from a `with` block. This runs even when an error interrupts the
   code. [Context Managers](16_Context_Managers.md) covers `with` in full.

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
#: First deleted
#: 2 Counter objects remaining
#: Second deleted
#: 1 Counter objects remaining
#: Third deleted
#: Last Counter object deleted
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
When an instance loses its last ordinary reference, here by being popped off the `counters` list,
it is collected at once, and the dictionary drops its entry on its own.
So the count falls `3, 2, 1, 0` as the list releases the objects,
with no `__del__()` and no explicit cleanup call.

A plain `dict` or `list` as the registry would keep every instance alive forever,
so the count could never fall.
The weak reference allows the registry to prune itself.
Unlike the `__del__()` version, this reads the count during normal execution,
so it never depends on the unreliable bookkeeping at interpreter shutdown.
