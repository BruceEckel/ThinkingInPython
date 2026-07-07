# Cleanup: Solutions

## 1. A `dict` registry instead of a `list`

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

counters = {}
for name in ["First", "Second", "Third"]:
    counters[name] = Counter(name)

print(Counter.live_count())
#: 3
del counters["Third"]
print(Counter.live_count())
#: 2
del counters["Second"]
print(Counter.live_count())
#: 1
counters.clear()
print(Counter.live_count())
#: 0
```

A `dict` works exactly like the `list` did: `_instances` only holds
weak references, so it never keeps an object alive on its own. Once
`counters` drops its last strong reference to a particular `Counter`
(via `del counters[name]` or `clear()`), that instance becomes
collectible and its entry disappears from `_instances` on its own,
with no explicit cleanup call. One easy way to break this by accident:
if you keep any other strong reference around (a loop variable left
over after a `for` loop, for instance), that single reference is
enough to keep `live_count()` from dropping, even after you remove the
object from `counters`. Watch for stray references before concluding a
weak-referenced registry has a bug.

## 2. Rebinding `counters` instead of clearing it

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
something different but reaches the same result: it points the name
`counters` at a brand-new, empty list, abandoning the old list
entirely. Since nothing else refers to that old list, it (and every
reference it held) becomes collectible immediately. Either way, the
three `Counter` instances lose their last strong reference at the same
moment, so `live_count()` falls to `0` right after.

## 3. Listing the names of every live instance

```python
# exercise_3.py
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

## 4. Building the `list` with a comprehension instead of a loop

```python
# exercise_4.py
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
