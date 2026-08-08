# Cleanup: Solutions

## 1. Rebinding `counters` instead of clearing it

```python
# exercise_1.py
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
counters = []  # Rebind the name instead of calling .clear()
print(Counter.live_count())
#: 0
```

`counters.clear()` empties the existing list in place, dropping its
references to all three `Counter` objects. `counters = []` does
something different: it points the name `counters` at a brand-new,
empty list and abandons the old one. Here nothing else refers to that
old list, so it (and every reference it held) becomes collectible
immediately, and both spellings reach `live_count() == 0`.

They stop agreeing the moment a second name enters the picture:

```python
# exercise_1_alias.py
counters = [1, 2, 3]
other = counters  # A second name for the same list
counters = []  # Rebinding: 'other' still sees the old list
print(other)
#: [1, 2, 3]
counters = [1, 2, 3]
other = counters
counters.clear()  # Clearing: 'other' sees the emptied list
print(other)
#: []
```

`clear()` changes the object every name can see. Rebinding changes
only which object this one name points at. The two coincide in
`weak_value.py` because that list has exactly one reference; with two,
rebinding would leave the `Counter` objects alive and `live_count()`
stuck at `3`.

## 2. Listing the names of every live instance

```python
# exercise_2.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[WeakValueDictionary[int, Counter]] = (
        WeakValueDictionary())

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_names(cls) -> list[str]:
        return sorted(c.name for c in cls._instances.values())

counters = [Counter(name) for name in ("Charlie", "Alpha", "Bravo")]
print(Counter.live_names())
#: ['Alpha', 'Bravo', 'Charlie']
```

`cls._instances.values()` iterates the live `Counter` objects
currently tracked (a `WeakValueDictionary` behaves like a normal
`dict` for reading), and the generator expression pulls out each
one's `.name`. Sorting gives a deterministic order, since a
dictionary's iteration order here follows insertion, not name order.

## 3. Building the `list` with a comprehension instead of a loop

```python
# exercise_3.py
from typing import ClassVar

class Counter:
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
            print(Counter.count, "Counter objects remaining")

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = [Counter(name) for name in ["First", "Second", "Third"]]

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

The output is identical to the original `for`-loop-with-`append()`
version. A comprehension still calls `Counter(name)` once per name,
in order, and still keeps the resulting list as the only thing holding
references to those three objects. `del c` inside the loop still only
unbinds the name `c`; it does not touch the list. Nothing about how
the list gets built changes when its contents get destroyed, so the
`deleted` messages still only appear at interpreter shutdown, after
`End of delete loop` has already printed.

## 4. A strong registry that never lets go

```python
# exercise_4.py
from typing import ClassVar

class Counter:
    _instances: ClassVar[dict[int, Counter]] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = [Counter(name) for name in ("First", "Second", "Third")]
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.clear()
print(Counter.live_count())
#: 3
```

The count never falls. A `dict` holds a strong reference to each
value, so `_instances` alone keeps every `Counter` alive no matter
what `counters` does. `pop()` removes one reference and the registry
still holds another, so the object's reference count never reaches
zero and nothing is ever collected.

The registry has become the leak it was meant to observe:
`live_count()` now reports how many `Counter` objects were ever
created, which is exactly the number it can never report correctly. A
`WeakValueDictionary` holds its values weakly, so it can answer the
question without changing the answer.

## 5. `finalize(self, self.close)` and what it keeps alive

```python
# exercise_5.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.closer = finalize(self, self.close)

    def close(self) -> None:
        print(self.name, "closed")

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.closer()
#: A closed
a.closer()
print(a.closer.alive, b.closer.alive)
#: False True
del b
print("End of program")
#: End of program
```

Run directly, the whole output is:

```text
A opened
B opened
A closed
False True
End of program
B closed
```

`B closed` now prints *after* `End of program`, where the chapter's
version printed it at the `del b`. It is missing from the markers
above because it arrives during interpreter shutdown, later than the
book's output checker captures, which is a demonstration of the point
in its own right. Nothing else about the output
changes, which is what makes the mistake hard to see: the callback
still runs, just at a different time and for a different reason.

What keeps the `Connection` alive is the callback itself. `self.close`
is a bound method, and a bound method holds a strong reference to the
object it is bound to. `finalize()` stores the callback, so the
finalizer registry now holds a reference to the very object whose
death it is waiting for. `del b` drops the last reference the program
has, but not the last reference that exists, so the object survives.

`B closed` prints at all only because of `finalize()`'s `atexit`
backstop, which runs every still-alive finalizer as the interpreter
shuts down. That is the fallback the chapter describes, doing exactly
its job, on an object that should have been collected at `del b`.

The chapter's `finalize(self, print, name, "closed")` avoids this by
passing the pieces the callback needs rather than the object that has
them. `name` is a `str` the `Connection` also happens to hold; the
finalizer's reference to it keeps a string alive, not a connection.
The rule generalizes: a finalizer may capture anything except a path
back to its own object.

## 6. A two-object cycle, with and without the collector

```python
# exercise_6.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def pair_link() -> None:
    a, b = Node("a"), Node("b")
    a.peer = b
    b.peer = a

gc.disable()
pair_link()
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
#: b finalized
gc.enable()
print("after collect")
#: after collect
```

Both finalizers run at `gc.collect()`, in creation order. Nothing
changed in principle: reference counting cannot reclaim either object,
because each holds the other, and the cycle collector reclaims both
together when it runs. A cycle through two objects behaves exactly
like a cycle through one; the self-reference in `cycle.py` is only the
smallest case.

Removing the `gc.disable()`/`gc.enable()` pair is what makes the output
unpredictable. The collector then runs on its own schedule, triggered
by allocation counts rather than by your call, so the two `finalized`
lines can appear anywhere after `pair_link()` returns: between the two
`print()` calls, after both, or not until the interpreter shuts down.
Whether they land before `after collect` depends on how many objects
the program happens to have allocated by then, which is not a fact
about this program.

`gc.disable()` is in the chapter's listing for that reason alone. It
is not advice. It buys a deterministic transcript for a demonstration
whose entire subject is the absence of determinism, which is why the
listing turns the collector back on immediately afterward.
